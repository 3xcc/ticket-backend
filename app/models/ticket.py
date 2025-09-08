from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict

# ---------------------------
# Shared Base Fields
# ---------------------------
class TicketBase(SQLModel):
    name: Optional[str] = Field(default=None, nullable=True)
    id_card_number: Optional[str] = Field(default=None, nullable=True)
    date_of_birth: Optional[str] = Field(default=None, nullable=True)
    phone_number: Optional[str] = Field(default=None, nullable=True)
    event: Optional[str] = Field(default=None, nullable=True)

# ---------------------------
# Ticket Creation Payload
# ---------------------------
class TicketCreate(TicketBase):
    # All fields optional on creation (for flexibility)
    pass

# ---------------------------
# Ticket DB Model
# ---------------------------
class Ticket(TicketBase, table=True):
    ticket_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True, index=True)
    ticket_number: Optional[str] = Field(default=None, index=True, unique=True)
    used: bool = Field(default=False)
    scanned_at: Optional[str] = Field(default=None, nullable=True)
    scanned_by: Optional[int] = Field(default=None, foreign_key="adminuser.id", nullable=True)  # NEW

# ---------------------------
# Ticket Response Payload
# ---------------------------
class TicketResponse(SQLModel):
    ticket_number: Optional[str] = None
    name: Optional[str] = None
    id_card_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None
    ticket_id: str
    qr: str
    status: str
    event: Optional[str] = None
    timestamp: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# ---------------------------
# Ticket Validation Payload
# ---------------------------
class TicketValidationRequest(SQLModel):
    payload: str
