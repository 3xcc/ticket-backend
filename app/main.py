import os
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Load .env in local dev; on Render this will simply pick up the existing env vars
try:
    load_dotenv()
    logging.info(".env loaded successfully (if present)")
except Exception as e:
    logging.warning(f"Could not load .env file: {e}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from app.db.engine import engine

# Core routers (must exist)
tickets_router = None
admin_router = None
auth_router = None
try:
    from app.api.tickets import router as tickets_router
    from app.routes.admin import router as admin_router
    from app.routes.auth import router as auth_router
    logging.info("Core routers loaded successfully")
except ImportError as e:
    logging.critical(f"Failed to import core routers: {e}")
except Exception as e:
    logging.critical(f"Unexpected error importing core routers: {e}")

# Optional routers loader
def safe_import_router(path: str, name: str):
    try:
        module = __import__(path, fromlist=["router"])
        router = getattr(module, "router", None)
        if router:
            logging.info(f"{name} router loaded")
        else:
            logging.warning(f"{name} router found but has no 'router' attribute")
        return router
    except ImportError:
        logging.warning(f"{name} router not found — skipping")
        return None
    except Exception as e:
        logging.error(f"Error loading {name} router: {e}")
        return None

templates_router = safe_import_router("app.routes.templates", "Templates")
uploads_router = safe_import_router("app.routes.uploads", "Uploads")
render_router = safe_import_router("app.routes.render", "Render")
files_router = safe_import_router("app.routes.files", "Files")
events_router = safe_import_router("app.routes.events", "Events")  # NEW

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
try:
    app = FastAPI(
        title="Ticket Manager API",
        description="Handles ticket creation, QR generation, scanning, and admin workflows",
        version="0.3.0",
        lifespan=lifespan
    )
    logging.info("FastAPI app instantiated")
except Exception as e:
    logging.critical(f"Error creating FastAPI app: {e}")
    raise

# CORS setup
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[os.getenv("FRONTEND_URL", "*")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logging.info("CORS middleware configured")
except Exception as e:
    logging.error(f"Error configuring CORS: {e}")

# Mount routers with consistent /api prefix
try:
    if tickets_router:
        app.include_router(tickets_router, prefix="/api", tags=["Tickets"])
    if admin_router:
        app.include_router(admin_router, prefix="/api", tags=["Admin"])
    if auth_router:
        app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
    if templates_router:
        app.include_router(templates_router, prefix="/api", tags=["Templates"])
    if uploads_router:
        app.include_router(uploads_router, prefix="/api", tags=["Uploads"])
    if render_router:
        app.include_router(render_router, prefix="/api", tags=["Render"])
    if files_router:
        app.include_router(files_router, prefix="/api", tags=["Files"])
    if events_router:
        app.include_router(events_router, prefix="/api", tags=["Events"])
    logging.info("Routers mounted successfully")
except Exception as e:
    logging.error(f"Error mounting routers: {e}")

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
    try:
        return {"message": "Ticket Manager API is running"}
    except Exception as e:
        logging.error(f"Error in health check endpoint: {e}")
        return {"message": "Error retrieving API status", "error": str(e)}
