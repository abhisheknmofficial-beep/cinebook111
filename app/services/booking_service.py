import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.theatre import Show, Screen, Seat, Theatre
from app.models.movie import Movie
from app.models.event import Event
from app.models.booking import Booking, BookingSeat, BookingStatus
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.dsa.seat_allocation import SeatGridMatrix, SeatNode
from app.dsa.queue import BookingRequest, BookingSimulationQueue

booking_queue = BookingSimulationQueue()

def generate_booking_reference() -> str:
    """Generates a clean, unique booking identifier like CB-2026-AB12CD."""
    code = uuid.uuid4().hex[:6].upper()
    return f"CB-2026-{code}"

def generate_payment_reference() -> str:
    code = uuid.uuid4().hex[:8].upper()
    return f"PAY-{code}"

def get_show_seating_matrix(db: Session, show_id: int) -> Tuple[Show, SeatGridMatrix]:
    """
    Constructs the 2D auditorium seating matrix for a specific show,
    identifying booked vs available seats.
    """
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found.")

    screen = db.query(Screen).filter(Screen.id == show.screen_id).first()
    if not screen:
        raise HTTPException(status_code=404, detail="Screen not found.")

    # Fetch all seats configured for this screen
    all_seats = db.query(Seat).filter(Seat.screen_id == screen.id).all()

    # Fetch all currently booked seat IDs for this show (active bookings)
    booked_records = db.query(BookingSeat).filter(
        BookingSeat.show_id == show_id,
        BookingSeat.is_active == True
    ).all()
    booked_seat_ids = {b.seat_id for b in booked_records}

    matrix = SeatGridMatrix(
        rows=screen.total_rows,
        cols=screen.total_cols,
        base_price=show.base_price
    )
    matrix.populate_seats(all_seats, booked_seat_ids)

    return show, matrix

def create_movie_booking(
    db: Session,
    user_id: int,
    show_id: int,
    requested_seat_ids: List[int]
) -> Booking:
    """
    CRITICAL DOUBLE-BOOKING PREVENTION & TRANSACTION LOGIC:
    1. Validates show existence.
    2. Validates requested seats in 2D matrix.
    3. Re-checks database under transaction for any active BookingSeat collisions.
    4. Calculates total price server-side based on seat tiers.
    5. Creates Booking (PENDING) and individual BookingSeat records.
    """
    if not requested_seat_ids:
        raise HTTPException(status_code=400, detail="You must select at least one seat.")

    show = db.query(Show).filter(Show.id == show_id, Show.is_active == True).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found or is no longer active.")

    # 1. High-concurrency DSA Queue simulation record
    req_payload = BookingRequest(
        request_id=str(uuid.uuid4()),
        user_id=user_id,
        show_id=show_id,
        seat_ids=requested_seat_ids
    )
    booking_queue.submit_request(req_payload)

    # 2. Re-query existing booked seats directly with DB lock/check to prevent race condition
    existing_conflicts = db.query(BookingSeat).filter(
        BookingSeat.show_id == show_id,
        BookingSeat.seat_id.in_(requested_seat_ids),
        BookingSeat.is_active == True
    ).all()

    if existing_conflicts:
        conflicted_codes = ", ".join([c.seat_code for c in existing_conflicts])
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Seats already booked: {conflicted_codes}. Please select different seats."
        )

    # 3. Retrieve Seat definitions for server-side pricing
    seat_records = db.query(Seat).filter(
        Seat.id.in_(requested_seat_ids),
        Seat.screen_id == show.screen_id
    ).all()

    if len(seat_records) != len(requested_seat_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more selected seats do not belong to this auditorium."
        )

    # 4. Server-side price calculation
    total_amount = 0.0
    booking_seats_to_create = []

    for seat in seat_records:
        multiplier = 1.0
        if seat.seat_type == "PREMIUM":
            multiplier = 1.25
        elif seat.seat_type == "VIP":
            multiplier = 1.50
        seat_price = round(show.base_price * multiplier, 2)
        total_amount += seat_price

        booking_seats_to_create.append({
            "seat_id": seat.id,
            "seat_code": seat.seat_code,
            "price": seat_price
        })

    # 5. Create Booking record
    booking_ref = generate_booking_reference()
    booking = Booking(
        booking_reference=booking_ref,
        user_id=user_id,
        show_id=show_id,
        event_id=None,
        total_amount=total_amount,
        status=BookingStatus.PENDING,
        num_tickets=len(seat_records),
        booking_time=datetime.now(timezone.utc)
    )
    db.add(booking)
    db.flush()  # Populates booking.id

    for item in booking_seats_to_create:
        bs = BookingSeat(
            booking_id=booking.id,
            show_id=show_id,
            seat_id=item["seat_id"],
            seat_code=item["seat_code"],
            price=item["price"],
            is_active=True
        )
        db.add(bs)

    db.commit()
    db.refresh(booking)

    # Mark queue request as processed
    processed = booking_queue.process_next()
    if processed:
        processed.processed = True
        processed.success = True

    return booking

def create_event_booking(
    db: Session,
    user_id: int,
    event_id: int,
    num_tickets: int
) -> Booking:
    """Books tickets for live events/concerts."""
    if num_tickets <= 0:
        raise HTTPException(status_code=400, detail="Must book at least 1 ticket.")

    event = db.query(Event).filter(Event.id == event_id, Event.is_active == True).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    if event.available_seats < num_tickets:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only {event.available_seats} tickets remaining for this event."
        )

    # Server-side pricing calculation
    total_amount = round(event.price * num_tickets, 2)

    # Decrement available capacity
    event.available_seats -= num_tickets

    booking_ref = generate_booking_reference()
    booking = Booking(
        booking_reference=booking_ref,
        user_id=user_id,
        show_id=None,
        event_id=event_id,
        total_amount=total_amount,
        status=BookingStatus.PENDING,
        num_tickets=num_tickets,
        booking_time=datetime.now(timezone.utc)
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def process_payment(
    db: Session,
    booking_id: int,
    payment_method: str = "UPI",
    simulate_failure: bool = False
) -> Tuple[Booking, Payment]:
    """
    Simulates payment gateway transaction.
    If success: confirms booking and marks payment as SUCCESS.
    If failed: cancels booking and releases seats.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    if booking.status == BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="This booking has already been paid and confirmed.")

    pay_ref = generate_payment_reference()
    pay_status = PaymentStatus.FAILED if simulate_failure else PaymentStatus.SUCCESS

    payment = Payment(
        booking_id=booking.id,
        payment_reference=pay_ref,
        payment_method=payment_method.upper(),
        amount=booking.total_amount,
        status=pay_status,
        transaction_time=datetime.now(timezone.utc)
    )
    db.add(payment)

    if pay_status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now(timezone.utc)
        # Release seats
        for seat in booking.seats:
            seat.is_active = False
        # If event, restore seats
        if booking.event_id and booking.event:
            booking.event.available_seats += booking.num_tickets

    db.commit()
    db.refresh(booking)
    db.refresh(payment)
    return booking, payment

def cancel_booking(db: Session, booking_id: int, user_id: int, is_admin: bool = False) -> Booking:
    """Cancels a booking and releases booked seats."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    if not is_admin and booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to cancel this booking.")

    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Booking is already cancelled.")

    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = datetime.now(timezone.utc)

    # Release movie seats
    for seat in booking.seats:
        seat.is_active = False

    # Restore event seats
    if booking.event_id and booking.event:
        booking.event.available_seats += booking.num_tickets

    db.commit()
    db.refresh(booking)
    return booking
