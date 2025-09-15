from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel

# Allowed field types for the template designer
FieldType = Literal["qr", "text", "image", "barcode"]

class TemplateField(BaseModel):
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


class TemplateBase(BaseModel):
    name: str
    background_file_id: Optional[str] = None  # NEW: FK to StoredFile
    fields: List[TemplateField]


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    background_file_id: Optional[str] = None
    fields: Optional[List[TemplateField]] = None


class TemplateOut(TemplateBase):
    id: str
    created_at: datetime
    updated_at: datetime
    download_url: Optional[str] = None  # NEW: convenience for frontend

    class Config:
        orm_mode = True
