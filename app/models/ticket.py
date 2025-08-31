from pydantic import BaseModel

class Ticket(BaseModel):
    name: str
    email: str