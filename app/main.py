from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import tickets

app = FastAPI(
    title="Ticket Manager API",
    description="Handles ticket creation, QR generation, and scanning workflows",
    version="0.2.0"
)

# CORS setup for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with Vercel domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include ticket router
app.include_router(tickets.router, prefix="/ticket", tags=["Tickets"])

# Health check
@app.get("/")
def root():
    return {"message": "Ticket Manager API is running"}
