from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingCreate, BookingResponse, BookingDetailResponse
from app.auth.dependencies import get_current_user
from app.services.booking_service import (
    create_movie_booking,
    create_event_booking,
    cancel_booking
)

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

@router.post("", status_code=status.HTTP_201_CREATED)
def make_booking(
    payload: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new booking reservation.
    Performs server-side validation, pricing calculation, and atomic seat conflict check.
    """
    if payload.show_id:
        booking = create_movie_booking(
            db=db,
            user_id=current_user.id,
            show_id=payload.show_id,
            requested_seat_ids=payload.seat_ids
        )
    elif payload.event_id:
        booking = create_event_booking(
            db=db,
            user_id=current_user.id,
            event_id=payload.event_id,
            num_tickets=payload.num_event_tickets or 1
        )
    else:
        raise HTTPException(status_code=400, detail="Must provide either show_id or event_id.")

    return {
        "booking_id": booking.id,
        "booking_reference": booking.booking_reference,
        "total_amount": booking.total_amount,
        "status": booking.status,
        "num_tickets": booking.num_tickets,
        "message": "Booking initiated. Proceed to payment simulation."
    }

@router.get("", response_model=List[BookingResponse])
def get_user_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves bookings belonging to the authenticated user."""
    # If admin, can see all bookings if desired, but user sees their own
    return db.query(Booking).filter(Booking.user_id == current_user.id).order_by(Booking.id.desc()).all()

@router.get("/{booking_id}")
def get_booking_details(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves detailed information for a specific booking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    is_admin = current_user.role == "ADMIN"
    if not is_admin and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this booking.")

    movie_info = None
    theatre_info = None
    show_info = None
    event_info = None

    if booking.show:
        show_info = {
            "id": booking.show.id,
            "date": str(booking.show.show_date),
            "time": booking.show.show_time,
            "base_price": booking.show.base_price
        }
        if booking.show.movie:
            movie_info = {
                "id": booking.show.movie.id,
                "title": booking.show.movie.title,
                "poster_url": booking.show.movie.poster_url,
                "language": booking.show.movie.language,
                "genre": booking.show.movie.genre
            }
        if booking.show.theatre:
            theatre_info = {
                "id": booking.show.theatre.id,
                "name": booking.show.theatre.name,
                "city": booking.show.theatre.city,
                "address": booking.show.theatre.address,
                "screen_name": booking.show.screen.name if booking.show.screen else "Screen 1"
            }

    if booking.event:
        event_info = {
            "id": booking.event.id,
            "title": booking.event.title,
            "category": booking.event.category,
            "location": booking.event.location,
            "date": str(booking.event.event_date),
            "time": booking.event.event_time,
            "poster_url": booking.event.poster_url
        }

    seats_data = [
        {
            "id": s.id,
            "seat_id": s.seat_id,
            "seat_code": s.seat_code,
            "price": s.price,
            "is_active": s.is_active
        }
        for s in booking.seats
    ]

    payment_info = None
    if booking.payment:
        payment_info = {
            "id": booking.payment.id,
            "payment_reference": booking.payment.payment_reference,
            "method": booking.payment.payment_method,
            "status": booking.payment.status,
            "amount": booking.payment.amount,
            "transaction_time": str(booking.payment.transaction_time)
        }

    return {
        "id": booking.id,
        "booking_reference": booking.booking_reference,
        "status": booking.status,
        "total_amount": booking.total_amount,
        "num_tickets": booking.num_tickets,
        "booking_time": str(booking.booking_time),
        "cancelled_at": str(booking.cancelled_at) if booking.cancelled_at else None,
        "movie": movie_info,
        "theatre": theatre_info,
        "show": show_info,
        "event": event_info,
        "seats": seats_data,
        "payment": payment_info
    }

@router.delete("/{booking_id}")
def cancel_existing_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancels an existing booking and releases its seats."""
    is_admin = current_user.role == "ADMIN"
    booking = cancel_booking(db, booking_id=booking_id, user_id=current_user.id, is_admin=is_admin)
    return {
        "message": "Booking cancelled successfully. Seats have been released.",
        "booking_reference": booking.booking_reference,
        "status": booking.status
    }
