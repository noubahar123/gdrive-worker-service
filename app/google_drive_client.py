# Change 2 (To add images in S3)
# app/google_drive_client.py
import os
import requests
from typing import List, Dict, Optional

API_KEY = os.getenv("GOOGLE_API_KEY")
DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"

if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not set in environment variables.")


def list_image_files_in_folder(folder_id: str) -> List[Dict]:
    """
    List image files in a Drive folder using API key (metadata).
    Returns list of dicts with keys id, name, mimeType, size (if available).
    """
    files = []
    params = {
        "q": f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false",
        "key": API_KEY,
        "fields": "files(id,name,mimeType,size),nextPageToken",
        "pageSize": 1000,
    }
    page_token = None

    while True:
        if page_token:
            params["pageToken"] = page_token
        resp = requests.get(DRIVE_FILES_URL, params=params, timeout=30)
        resp.raise_for_status()
        body = resp.json()
        files.extend(body.get("files", []))
        page_token = body.get("nextPageToken")
        if not page_token:
            break

    return files


def download_drive_file(file_id: str) -> bytes:
    """
    Download file bytes using alt=media with API key.
    Works for publicly shared files (or files accessible via API key).
    Raises RuntimeError on non-200 responses.
    """
    url = f"{DRIVE_FILES_URL}/{file_id}"
    params = {"alt": "media", "key": API_KEY}
    resp = requests.get(url, params=params, timeout=60, stream=True)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to download file {file_id}: {resp.status_code} {resp.text[:200]}")
    return resp.content






















# import os
# from typing import List, Dict
# from googleapiclient.discovery import build

# API_KEY = os.getenv("GOOGLE_API_KEY")


# def get_drive_service():
#     if not API_KEY:
#         raise RuntimeError("GOOGLE_API_KEY is not set in .env")

#     service = build("drive", "v3", developerKey=API_KEY)
#     return service


# def list_image_files_in_folder(folder_id: str) -> List[Dict]:
#     service = get_drive_service()

#     query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"

#     files: List[Dict] = []
#     page_token = None

#     while True:
#         response = (
#             service.files()
#             .list(
#                 q=query,
#                 fields="nextPageToken, files(id, name, mimeType, size)",
#                 pageToken=page_token,
#                 pageSize=1000,
#             )
#             .execute()
#         )

#         files.extend(response.get("files", []))
#         page_token = response.get("nextPageToken")

#         if not page_token:
#             break

#     return files
