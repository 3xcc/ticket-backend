from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field
try:
    # Pydantic v2
    from pydantic import ConfigDict
    V2 = True
except Exception:
    V2 = False


class TicketBase(SQLModel):
    name: str
    id_card_number: str
    date_of_birth: str
    phone_number: str
    event: str


class TicketCreate(TicketBase):
    # All fields required on creation
    pass


class Ticket(TicketBase, table=True):
    ticket_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True, index=True)
    ticket_number: Optional[str] = Field(default=None, index=True, unique=True)  # Human-friendly number
    used: bool = Field(default=False)
    scanned_at: Optional[str] = None


class TicketResponse(SQLModel):
    ticket_number: Optional[str] = None
    name: str
    id_card_number: str
    date_of_birth: str
    phone_number: str
    ticket_id: str
    qr: str
    status: str
    event: Optional[str] = None
    timestamp: Optional[str] = None

    class Config:
        orm_mode = True


class TicketValidationRequest(SQLModel):
    payload: str
