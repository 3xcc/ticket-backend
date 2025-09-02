from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.api import tickets
from app.db.engine import engine

# Optional: load .env in local dev
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Safe fallback if dotenv isn't installed

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

# DB table creation on startup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
