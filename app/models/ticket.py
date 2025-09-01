from sqlmodel import SQLModel, Field
from typing import Optional

class Ticket(SQLModel, table=True):
    ticket_id: str = Field(primary_key=True)
    name: str
    id_card_number: str
    date_of_birth: str
    phone_number: str

class TicketCreate(SQLModel):
    name: str
    id_card_number: str
    date_of_birth: str
    phone_number: str

class TicketResponse(TicketCreate):
    ticket_id: str
    qr: str
