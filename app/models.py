# worker-service/app/models.py
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func
from .database import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    google_drive_id = Column(String, nullable=False, index=True)
    size = Column(BigInteger, nullable=True)
    mime_type = Column(String, nullable=True)
    storage_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
