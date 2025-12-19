# worker-service/app/__init__.py
# Make `app.tasks.process_google_drive_folder` importable for RQ
from . import tasks

__all__ = ["tasks"]
