import os
import asyncio
import httpx

BASE_URL = os.getenv("API_URL", "http://localhost:8000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "strongpassword")


async def login(email: str, password: str) -> str:
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BASE_URL}/admin/login",
            data={"username": email, "password": password},
        )
        res.raise_for_status()
        return res.json()["access_token"]


async def clean_tickets():
    token = await login(ADMIN_EMAIL, ADMIN_PASSWORD)
    async with httpx.AsyncClient() as client:
        res = await client.delete(
            f"{BASE_URL}/admin/tickets",
            params={"confirm": "true"},
            headers={"Authorization": f"Bearer {token}"},
        )
        if res.status_code == 200:
            print("🧹 Tickets table cleaned successfully.")
        else:
            print(f"⚠️ Failed to clean tickets: {res.status_code} {res.text}")


if __name__ == "__main__":
    asyncio.run(clean_tickets())