import asyncio
import httpx
import os
import uuid
from dotenv import load_dotenv

# Optional: will not fail if .env is absent
load_dotenv()

BASE_URL = os.getenv("API_URL", "https://ticket-backend-jdpp.onrender.com").rstrip("/")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "strongpassword")



async def login(email: str, password: str) -> str:
    global token_cache
    if token_cache:
        return token_cache
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BASE_URL}/admin/login",
            data={"username": email, "password": password},
        )
        res.raise_for_status()
        data = res.json()
        token_cache = data["access_token"]
        return token_cache


async def create_ticket() -> str:
    # Generate unique values to avoid duplicate constraint
    unique_suffix = uuid.uuid4().hex[:6]
    payload = {
        "name": "Test User",
        "id_card_number": f"T{unique_suffix}",
        "date_of_birth": "1990-01-01",
        "phone_number": "1234567890",
        "event": f"Test Event {unique_suffix}",
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/tickets", json=payload)
        res.raise_for_status()
        data = res.json()
        return data["ticket_id"]


async def validate_ticket(ticket_id: str):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BASE_URL}/validate_ticket",
            json={"payload": ticket_id},
            headers={"Authorization": f"Bearer {await login(ADMIN_EMAIL, ADMIN_PASSWORD)}"},
        )
        res.raise_for_status()
        return res.json()


async def export_tickets():
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{BASE_URL}/admin/export",
            headers={"Authorization": f"Bearer {await login(ADMIN_EMAIL, ADMIN_PASSWORD)}"},
        )
        res.raise_for_status()
        return res.json()


async def run_tests():
    print("🔐 Logging in as admin...")
    token = await login(ADMIN_EMAIL, ADMIN_PASSWORD)
    print("✅ Login successful")

    print("🎟️ Creating ticket...")
    ticket_id = await create_ticket()
    print(f"✅ Ticket created: {ticket_id}")

    print("🧪 Validating ticket...")
    validation_result = await validate_ticket(ticket_id)
    print(f"✅ Ticket validated: {validation_result}")

    print("📦 Exporting tickets...")
    tickets = await export_tickets()
    print(f"✅ Export successful: {len(tickets)} tickets found")

    print("🎉 All tests passed!")


if __name__ == "__main__":
    asyncio.run(run_tests())