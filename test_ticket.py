import requests

payload = {
    "name": "3xc",
    "email": "test@example.com"
}

res = requests.post("http://localhost:8000/tickets", json=payload)

print("Status Code:", res.status_code)
print("Response:", res.json())
