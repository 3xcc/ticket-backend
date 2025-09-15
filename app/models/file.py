# app/models/file.py
from datetime import datetime
from uuid import uuid4
from sqlmodel import SQLModel, Field

class StoredFile(SQLModel, table=True):
    __tablename__ = "stored_files"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True, index=True)
    filename: str
    content_type: str
    data: bytes  # Stored as BYTEA in Postgres
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
