from typing import Optional, List, Literal
from datetime import datetime
from uuid import uuid4
from sqlmodel import SQLModel, Field, Column, JSON, Relationship

# NEW: Import StoredFile for FK relationship
from app.models.file import StoredFile

# Allowed field types for the template designer
FieldType = Literal["qr", "text", "image", "barcode"]

class TemplateField(SQLModel):
    """
    Represents a single field on a ticket template.
    Coordinates and sizes are in pixels relative to the background image.
    """
    name: str
    type: FieldType
    x: int
    y: int
    width: int
    height: int
    font_family: Optional[str] = None
    font_weight: Optional[str] = None
    font_size: Optional[int] = None
    color: Optional[str] = None
    align: Optional[Literal["left", "center", "right"]] = None
    data_key: Optional[str] = None
    conditions: Optional[dict] = None


class TicketTemplate(SQLModel, table=True):
    """
    Stores the template configuration for rendering tickets.
    """
    __tablename__ = "ticket_templates"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True, index=True)
    name: str

    # CHANGED: Replace background_url with background_file_id FK
    background_file_id: Optional[str] = Field(
        default=None,
        foreign_key="stored_files.id",
        index=True
    )

    # Relationship to StoredFile
    background_file: Optional[StoredFile] = Relationship()

    fields: List[TemplateField] = Field(sa_column=Column(JSON), default=[])
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
