from pydantic import BaseModel

class TicketCreate(BaseModel):
    name: str
    id_card_number: str
    date_of_birth: str
    phone_number: str

class TicketResponse(TicketCreate):
    ticket_id: str
    qr: str