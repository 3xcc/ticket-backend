from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime

class EventBase(SQLModel):
    name: str
    date: date
    location: str

class Event(EventBase, table=True):
    id: str = Field(primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EventCreate(EventBase):
    pass

class EventRead(EventBase):
    id: str
    created_at: datetime
