import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import (
    pages_router,
    auth_router,
    movies_router,
    events_router,
    theatres_router,
    shows_router,
    bookings_router,
    payments_router,
    admin_router
)
from seed.seed_data import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event: ensures database tables exist and seeds demo data on initial run."""
    Base.metadata.create_all(bind=engine)
    try:
        seed_database()
    except Exception as e:
        print(f"Warning during seed check: {e}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-Stack Movie and Event Ticket Booking Web Application with Embedded DSA Core Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(movies_router)
app.include_router(events_router)
app.include_router(theatres_router)
app.include_router(shows_router)
app.include_router(bookings_router)
app.include_router(payments_router)
app.include_router(admin_router)


# Global Exception Handlers
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"detail": "Resource not found."})
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>404 - Not Found | CineBook</title><link rel="stylesheet" href="/static/css/style.css"></head>
        <body style="display: flex; align-items: center; justify-content: center; min-height: 100vh; text-align: center;">
            <div style="background: #1e293b; padding: 3rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); max-width: 500px;">
                <span style="font-size: 3rem;">🔍</span>
                <h1 style="font-size: 2rem; margin: 1rem 0 0.5rem; color: #f43f5e;">404 - Page Not Found</h1>
                <p style="color: #94a3b8; margin-bottom: 1.5rem;">The page you are looking for does not exist or was moved.</p>
                <a href="/" class="btn btn-primary">Return to Homepage</a>
            </div>
        </body>
        </html>
        """,
        status_code=404
    )


@app.exception_handler(403)
async def custom_403_handler(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=403, content={"detail": "Access forbidden: administrative privileges required."})
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>403 - Forbidden | CineBook</title><link rel="stylesheet" href="/static/css/style.css"></head>
        <body style="display: flex; align-items: center; justify-content: center; min-height: 100vh; text-align: center;">
            <div style="background: #1e293b; padding: 3rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); max-width: 500px;">
                <span style="font-size: 3rem;">🔒</span>
                <h1 style="font-size: 2rem; margin: 1rem 0 0.5rem; color: #ef4444;">403 - Access Forbidden</h1>
                <p style="color: #94a3b8; margin-bottom: 1.5rem;">You do not have administrative privileges to access this area.</p>
                <a href="/" class="btn btn-primary">Return to Homepage</a>
            </div>
        </body>
        </html>
        """,
        status_code=403
    )
