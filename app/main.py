import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load .env in local dev; on Render this will simply pick up the existing env vars
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.db.engine import engine
from app.api.tickets import router as tickets_router

# Lifespan handler — replaces deprecated @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield  # No shutdown logic needed yet

# Instantiate the FastAPI app with lifespan
app = FastAPI(
    title="Ticket Manager API",
    description="Handles ticket creation, QR generation, and scanning workflows",
    version="0.2.0",
    lifespan=lifespan
)

# CORS setup — tighten allow_origins once your frontend URL is known
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the tickets router under /ticket
app.include_router(tickets_router, tags=["Tickets"])

# Simple health check
@app.get("/")
def root():
    return {"message": "Ticket Manager API is running"}
