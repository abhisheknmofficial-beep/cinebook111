from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User, UserRole
from app.models.movie import Movie
from app.models.event import Event
from app.models.theatre import Theatre, Show, Screen
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus

def get_admin_dashboard_stats(db: Session) -> Dict[str, Any]:
    """Computes comprehensive executive statistics for the admin dashboard."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_movies = db.query(func.count(Movie.id)).scalar() or 0
    total_theatres = db.query(func.count(Theatre.id)).scalar() or 0
    total_shows = db.query(func.count(Show.id)).scalar() or 0
    total_events = db.query(func.count(Event.id)).scalar() or 0
    total_bookings = db.query(func.count(Booking.id)).scalar() or 0

    confirmed_bookings = db.query(func.count(Booking.id)).filter(
        Booking.status == BookingStatus.CONFIRMED
    ).scalar() or 0

    total_revenue = db.query(func.sum(Booking.total_amount)).filter(
        Booking.status == BookingStatus.CONFIRMED
    ).scalar() or 0.0

    recent_bookings = db.query(Booking).order_by(Booking.id.desc()).limit(10).all()

    return {
        "total_users": total_users,
        "total_movies": total_movies,
        "total_theatres": total_theatres,
        "total_shows": total_shows,
        "total_events": total_events,
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "total_revenue": round(float(total_revenue), 2),
        "recent_bookings": recent_bookings
    }
