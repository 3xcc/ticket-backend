from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field

class TicketBase(SQLModel):
    name: str
    id_card_number: str
    date_of_birth: str
    phone_number: str
    event: str

class TicketCreate(TicketBase):
    """
    Input schema for creating a ticket.
    Inherits all required fields from TicketBase.
    """
    pass

class Ticket(TicketBase, table=True):
    """
    The actual database model.
    Inherits metadata fields + adds primary key and scan flags.
    """
    ticket_id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        index=True
    )
    used: bool = Field(default=False, description="Has this ticket been scanned?")
    scanned_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp of when the ticket was first scanned"
    )

class TicketResponse(SQLModel):
    """
    Response schema for all outbound ticket data.
    Mirrors TicketBase plus generated fields.
    """
    ticket_id: str
    qr: str
    status: str
    timestamp: Optional[str]

    class Config:
        orm_mode = True

class TicketValidationRequest(SQLModel):
    """
    Payload schema for validating a ticket.
    """
    payload: str
