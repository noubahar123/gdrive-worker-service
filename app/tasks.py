# worker-service/app/tasks.py
from typing import Optional
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import Image
from .google_drive_client import list_image_files_in_folder, download_drive_file
from .storage import upload_bytes_to_s3
from datetime import datetime
import mimetypes
import os

# Ensure tables exist (safe on import)
Base.metadata.create_all(bind=engine)


def _safe_filename(name: str) -> str:
    # Minimal safe filename conversion; you can replace with slugify if desired.
    return name.replace(" ", "_")


def process_google_drive_folder(folder_id: str) -> None:
    """
    RQ job: import images from a public Google Drive folder into Postgres.
    Downloads via API key (alt=media), uploads to S3, stores S3 URL in storage_path.
    """
    db: Session = SessionLocal()
    try:
        files = list_image_files_in_folder(folder_id)
        print(f"[WORKER] Found {len(files)} images in folder {folder_id}")

        inserted_count = 0

        for f in files:
            file_id = f.get("id")
            name = f.get("name", f"unknown_{file_id}")
            mime_type = f.get("mimeType") or mimetypes.guess_type(name)[0] or "application/octet-stream"

            # 1) Download bytes using API-key alt=media method (raises on failure)
            try:
                data = download_drive_file(file_id)
                if not data:
                    print(f"[WORKER] No data returned for {file_id} ({name}), skipping.")
                    continue
            except Exception as e:
                print(f"[WORKER] Failed to download {file_id} ({name}): {e}")
                continue

            # 2) Upload bytes to S3
            try:
                ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
                safe_name = _safe_filename(name)
                key = f"imports/{folder_id}/{ts}_{safe_name}"
                s3_url = upload_bytes_to_s3(key, data, content_type=mime_type)
            except Exception as e:
                print(f"[WORKER] Failed to upload {name} to S3: {e}")
                continue

            # 3) Determine size
            size_value: Optional[int] = None
            if "size" in f:
                try:
                    size_value = int(f["size"])
                except Exception:
                    size_value = len(data) if data else None
            else:
                size_value = len(data) if data else None

            # 4) Persist to DB
            img = Image(
                name=name,
                google_drive_id=file_id,
                size=size_value,
                mime_type=mime_type,
                storage_path=s3_url,
            )
            db.add(img)
            inserted_count += 1

        db.commit()
        print(f"[WORKER] Inserted {inserted_count} images from folder {folder_id}")

    except Exception as e:
        db.rollback()
        print(f"[WORKER] Error while processing folder {folder_id}: {e}")
        raise
    finally:
        db.close()
