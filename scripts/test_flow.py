import requests
from uuid import uuid4

BASE_URL = "https://ticket-backend-jdpp.onrender.com"

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin1234"

SCANNER_EMAIL = "scanner@example.com"
SCANNER_PASSWORD = "scanner1234"

# --- Helpers ---
def login(email, password):
    res = requests.post(f"{BASE_URL}/admin/login", json={
        "email": email,
        "password": password
    })
    res.raise_for_status()
    token = res.json()["access_token"]
    print(f"✅ Logged in as {email}")
    return token

def create_scanner(token):
    res = requests.post(f"{BASE_URL}/admin/create_user",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": SCANNER_EMAIL,
            "password": SCANNER_PASSWORD,
            "role": "scanner"
        }
    )
    if res.status_code == 409:
        print("⚠️ Scanner already exists")
    else:
        res.raise_for_status()
        print("✅ Scanner created")

def create_ticket(token):
    ticket_payload = {
        "name": "Test User",
        "id_card_number": str(uuid4())[:8],  # 👈 unique ID
        "date_of_birth": "1990-01-01",
        "phone_number": "+9601234567",
        "event": "Test Event"
    }
    res = requests.post(f"{BASE_URL}/tickets",
        headers={"Authorization": f"Bearer {token}"},
        json=ticket_payload
    )
    res.raise_for_status()
    ticket = res.json()
    print(f"✅ Ticket created: {ticket['ticket_id']}")
    return ticket["ticket_id"]

def scan_ticket_path(token, ticket_id):
    """Scan using /scan/{ticket_id} route"""
    res = requests.post(f"{BASE_URL}/scan/{ticket_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    res.raise_for_status()
    print(f"✅ [Path] Scan result: {res.json()['status']}")

def scan_ticket_payload(token, ticket_id):
    """Scan using /validate_ticket route"""
    res = requests.post(f"{BASE_URL}/validate_ticket",
        headers={"Authorization": f"Bearer {token}"},
        json={"payload": ticket_id}
    )
    res.raise_for_status()
    print(f"✅ [Payload] Scan result: {res.json()['status']}")

def export_tickets(token, **filters):
    res = requests.get(f"{BASE_URL}/admin/export",
        headers={"Authorization": f"Bearer {token}"},
        params=filters
    )
    res.raise_for_status()
    tickets = res.json()
    print(f"📦 Exported {len(tickets)} ticket(s) with filters {filters}")
    return tickets

def bulk_delete_tickets(token):
    res = requests.delete(f"{BASE_URL}/admin/tickets",
        headers={"Authorization": f"Bearer {token}"},
        params={"confirm": True}
    )
    res.raise_for_status()
    print("🗑️ All tickets deleted")

def delete_scanner_user(token):
    """Optional cleanup: delete scanner user by email"""
    res = requests.delete(f"{BASE_URL}/admin/delete_user",
        headers={"Authorization": f"Bearer {token}"},
        params={"email": SCANNER_EMAIL}
    )
    if res.status_code == 404:
        print("ℹ️ Scanner user not found for cleanup")
    elif res.status_code == 200:
        print("🧹 Scanner user deleted")
    else:
        print(f"⚠️ Cleanup returned {res.status_code}: {res.text}")

# --- Full Flow ---
if __name__ == "__main__":
    # 1. Admin login
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)

    # 2. Create scanner user
    create_scanner(admin_token)

    # 3. Create ticket as admin
    ticket_id = create_ticket(admin_token)

    # 4. Scanner login
    scanner_token = login(SCANNER_EMAIL, SCANNER_PASSWORD)

    # 5. Scan ticket via /scan/{ticket_id}
    scan_ticket_path(scanner_token, ticket_id)

    # 6. Scan ticket again via /validate_ticket
    scan_ticket_payload(scanner_token, ticket_id)

    # 7. Export used tickets
    export_tickets(admin_token, used=True)

    # 8. Bulk delete tickets
    bulk_delete_tickets(admin_token)

    # 9. Cleanup scanner user
    delete_scanner_user(admin_token)

    print("\n🎯 Full flow test completed successfully")
