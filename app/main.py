import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load .env in local dev; on Render this will simply pick up the existing env vars
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.db.engine import engine

# Routers
from app.api.tickets import router as tickets_router
from app.routes.admin import router as admin_router  # NEW
from app.routes.auth import router as auth_router

# Lifespan handler — replaces deprecated @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield  # No shutdown logic needed yet

# Instantiate the FastAPI app with lifespan
app = FastAPI(
    title="Ticket Manager API",
    description="Handles ticket creation, QR generation, scanning, and admin workflows",
    version="0.3.0",  # Bumped version for admin system
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

# Mount routers
app.include_router(tickets_router, tags=["Tickets"])
app.include_router(admin_router, tags=["Admin"]) 
app.include_router(auth_router, prefix="/auth") # NEW

# Simple health check
@app.get("/")
def root():
    return {"message": "Ticket Manager API is running"}
