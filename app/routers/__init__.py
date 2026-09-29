from app.routers.auth import router as auth_router
from app.routers.movies import router as movies_router
from app.routers.events import router as events_router
from app.routers.theatres import router as theatres_router
from app.routers.shows import router as shows_router
from app.routers.bookings import router as bookings_router
from app.routers.payments import router as payments_router
from app.routers.admin import router as admin_router
from app.routers.pages import router as pages_router

__all__ = [
    "auth_router",
    "movies_router",
    "events_router",
    "theatres_router",
    "shows_router",
    "bookings_router",
    "payments_router",
    "admin_router",
    "pages_router"
]
