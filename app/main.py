# Try 2
from .database import Base, engine, SessionLocal
from .models import Image
from sqlalchemy.orm import Session
from .google_drive_client import list_image_files_in_folder

# Ensure table exists
Base.metadata.create_all(bind=engine)


def process_google_drive_folder(folder_id: str) -> None:
    db: Session = SessionLocal()

    try:
        print(f"[WORKER] Checking folder: {folder_id}")

        files = list_image_files_in_folder(folder_id)
        print(f"[WORKER] Found {len(files)} public images")

        for f in files:
            size_value = None
            if "size" in f:
                try:
                    size_value = int(f["size"])
                except:
                    size_value = None

            img = Image(
                name=f["name"],
                google_drive_id=f["id"],
                mime_type=f["mimeType"],
                size=size_value,
                storage_path=f"google-drive://{f['id']}"
            )

            db.add(img)

        db.commit()
        print("[WORKER] Import completed.")

    except Exception as e:
        db.rollback()
        print(f"[WORKER] ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # TEST FOLDER ID — temp
    test_folder_id = "1989-UKrKWfy62OIzz1TJiP8W4_UfUmP7"
    process_google_drive_folder(test_folder_id)
    






















# # worker-service/app/main.py
# from sqlalchemy.orm import Session

# from .database import Base, engine, SessionLocal
# from .models import Image


# # Create tables if they don't exist yet
# Base.metadata.create_all(bind=engine)


# def process_google_drive_folder(folder_id: str) -> None:
#     """
#     TEMP IMPLEMENTATION:
#     Simulate importing images from a Google Drive folder.

#     For now, it just inserts ONE dummy image row into the DB
#     so we can see it from the API's /images endpoint.
#     Later this will call the real Google Drive API.
#     """
#     db: Session = SessionLocal()

#     try:
#         dummy_image = Image(
#             name=f"dummy_from_folder_{folder_id}.jpg",
#             google_drive_id=f"{folder_id}_file_1",
#             size=123456,
#             mime_type="image/jpeg",
#             storage_path=f"https://dummy-storage.local/{folder_id}/file1.jpg",
#         )

#         db.add(dummy_image)
#         db.commit()
#         db.refresh(dummy_image)

#         print(f"[WORKER] Inserted dummy image with id={dummy_image.id} for folder={folder_id}")

#     except Exception as e:
#         db.rollback()
#         print(f"[WORKER] Error while inserting dummy image: {e}")
#         raise
#     finally:
#         db.close()


# # Allow running this file directly:
# if __name__ == "__main__":
#     # Example manual test:
#     test_folder_id = "12345ABCDE"
#     print(f"[WORKER] Running test import for folder_id={test_folder_id}")
#     process_google_drive_folder(test_folder_id)
