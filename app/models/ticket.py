from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import BaseModel

class Ticket(SQLModel, table=True):
    ticket_id: str = Field(primary_key=True)
    name: str
    id_card_number: str
    date_of_birth: str
    phone_number: str
    used: Optional[bool] = False
    scanned_at: Optional[str] = None

class TicketCreate(SQLModel):
    name: str
    id_card_number: str
    date_of_birth: str
    phone_number: str
    event: Optional[str] = None

class TicketResponse(TicketCreate):
    ticket_id: str
    qr: Optional[str] = None
    status: Optional[str] = None
    event: Optional[str] = None
    timestamp: Optional[str] = None

class TicketValidationRequest(BaseModel):
    payload: str
