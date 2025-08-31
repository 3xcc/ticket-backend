from fastapi import APIRouter
from app.models.ticket import Ticket
from app.services.qr import generate_qr

router = APIRouter()

@router.post("/tickets")
def create_ticket(t: Ticket):
    data = f"{t.name}|{t.email}"
    qr = generate_qr(data)
    return {"qr": qr}

@router.get("/health")
def health():
    return {"status": "ok"}
