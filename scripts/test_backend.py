import asyncio
import httpx
import os
from dotenv import load_dotenv

# Optional: will not fail if .env is absent
load_dotenv()

BASE_URL = os.getenv("API_URL", "https://ticket-backend-jdpp.onrender.com").rstrip("/")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "strongpassword")


async def login(email, password):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BASE_URL}/admin/login",
            data={"username": email, "password": password},
        )
        res.raise_for_status()
        data = res.json()
        assert "access_token" in data, f"Login missing access_token: {data}"
        return data["access_token"]


async def create_ticket():
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BASE_URL}/tickets",
            json={
                "name": "Test User",
                "id_card_number": "T123456",
                "date_of_birth": "1990-01-01",
                "phone_number": "1234567890",
                "event": "Test Event",
            },
        )
        res.raise_for_status()
        data = res.json()
        assert "ticket_id" in data, f"Create ticket missing ticket_id: {data}"
        return data["ticket_id"]


async def validate_ticket(token, ticket_id):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BASE_URL}/validate_ticket",
            headers={"Authorization": f"Bearer {token}"},
            json={"payload": ticket_id},
        )
        res.raise_for_status()
        data = res.json()
        assert "status" in data, f"Validate ticket missing status: {data}"
        return data["status"]


async def export_tickets(token):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{BASE_URL}/admin/export",
            headers={"Authorization": f"Bearer {token}"},
        )
        res.raise_for_status()
        data = res.json()
        assert isinstance(data, list), f"Export should return a list: {type(data)} {data}"
        return data


async def run_tests():
    print("🔐 Logging in as admin...")
    token = await login(ADMIN_EMAIL, ADMIN_PASSWORD)
    print("✅ Login successful")

    print("🎟️ Creating ticket...")
    ticket_id = await create_ticket()
    print(f"✅ Ticket created: {ticket_id}")

    print("🧪 Validating ticket...")
    status = await validate_ticket(token, ticket_id)
    assert status == "valid", f"❌ Unexpected status: {status}"
    print("✅ Ticket validated")

    print("📦 Exporting tickets...")
    tickets = await export_tickets(token)
    assert any(t.get("ticket_id") == ticket_id for t in tickets), "❌ Ticket not found in export"
    print("✅ Export successful")

    print("🎉 All tests passed!")


if __name__ == "__main__":
    asyncio.run(run_tests())
