import os
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load .env in local dev; on Render this will simply pick up the existing env vars
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from app.db.engine import engine

# Core routers (must exist)
from app.api.tickets import router as tickets_router
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router

# Optional Phase 4D+ routers
def safe_import_router(path, name):
    try:
        module = __import__(path, fromlist=["router"])
        logging.info(f"{name} router loaded")
        return getattr(module, "router", None)
    except ImportError:
        logging.warning(f"{name} router not loaded")
        return None
    except Exception as e:
        logging.error(f"Error loading {name} router: {e}")
        return None

templates_router = safe_import_router("app.routes.templates", "Templates")
uploads_router = safe_import_router("app.routes.uploads", "Uploads")
render_router = safe_import_router("app.routes.render", "Render")
files_router = safe_import_router("app.routes.files", "Files")  # NEW for DB-stored uploads

# Lifespan handler — replaces deprecated @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        SQLModel.metadata.create_all(engine)
        logging.info("Database tables ensured")
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
    yield  # No shutdown logic needed yet

# Instantiate the FastAPI app with lifespan
app = FastAPI(
    title="Ticket Manager API",
    description="Handles ticket creation, QR generation, scanning, and admin workflows",
    version="0.3.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers with consistent /api prefix
app.include_router(tickets_router, prefix="/api", tags=["Tickets"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

if templates_router:
    app.include_router(templates_router, prefix="/api", tags=["Templates"])
if uploads_router:
    app.include_router(uploads_router, prefix="/api", tags=["Uploads"])
if render_router:
    app.include_router(render_router, prefix="/api", tags=["Render"])
if files_router:
    app.include_router(files_router, prefix="/api", tags=["Files"])

# Static mount for template backgrounds
try:
    os.makedirs("uploads/templates", exist_ok=True)
    app.mount(
        "/static/template-backgrounds",
        StaticFiles(directory="uploads/templates"),
        name="template_backgrounds"
    )
    logging.info("Static mount for template backgrounds ready")
except Exception as e:
    logging.error(f"Error setting up static mount: {e}")

# Simple health check
@app.get("/")
def root():
    return {"message": "Ticket Manager API is running"}
