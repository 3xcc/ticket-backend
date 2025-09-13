import requests
import uuid

BASE_URL = "https://ticket-backend-jdpp.onrender.com"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin1234"

def login_admin():
    res = requests.post(f"{BASE_URL}/admin/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    res.raise_for_status()
    token = res.json()["access_token"]
    print("✅ Logged in as admin")
    return token

def create_scanner(token):
    res = requests.post(f"{BASE_URL}/admin/create_user",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "email": "scanner@example.com",
            "password": "scanner1234",
            "role": "scanner"
        }
    )
    if res.status_code == 409:
        print("⚠️ Scanner already exists")
    else:
        res.raise_for_status()
        print("✅ Scanner created")

def export_tickets(token):
    res = requests.get(f"{BASE_URL}/admin/export",
        headers={"Authorization": f"Bearer {token}"}
    )
    res.raise_for_status()
    tickets = res.json()
    print(f"📦 Exported {len(tickets)} ticket(s)")
    return tickets

def bulk_delete(token):
    res = requests.delete(f"{BASE_URL}/admin/tickets?confirm=true",
        headers={"Authorization": f"Bearer {token}"}
    )
    res.raise_for_status()
    print("🗑️ All tickets deleted")

if __name__ == "__main__":
    token = login_admin()
    create_scanner(token)
    export_tickets(token)
    bulk_delete(token)
