from fastapi import APIRouter
from app.models.ticket import Ticket
from app.services.qr import generate_qr

router = APIRouter()

@router.post("/tickets")
def create_ticket(t: Ticket):
    try:
        data = f"{t.name}|{t.email}"
        qr = generate_qr(data)
        return {"qr": qr}
    except Exception as e:
        print(f"Error in /tickets: {e}")
        return {"error": str(e)}


@router.get("/health")
def health():
    return {"status": "ok"}



