from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field as PydField

FieldType = Literal["qr", "text", "image", "barcode"]

class TemplateFieldIn(BaseModel):
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

class TemplateCreate(BaseModel):
    name: str
    background_url: str = ""
    fields: List[TemplateFieldIn] = PydField(default_factory=list)

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    background_url: Optional[str] = None
    fields: Optional[List[TemplateFieldIn]] = None

class TemplateOut(BaseModel):
    id: str
    name: str
    background_url: str
    fields: List[TemplateFieldIn]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # allows ORM objects to be returned directly
