from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base

class BookingStatus:
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    show_id = Column(Integer, ForeignKey("shows.id", ondelete="SET NULL"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), default=BookingStatus.PENDING, index=True)
    num_tickets = Column(Integer, default=1)
    booking_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    cancelled_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="bookings")
    show = relationship("Show", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")
    seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Booking {self.booking_reference} - {self.status}>"

class BookingSeat(Base):
    __tablename__ = "booking_seats"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    show_id = Column(Integer, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    seat_code = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)  # True when booked, False when cancelled

    booking = relationship("Booking", back_populates="seats")
    show = relationship("Show", back_populates="booking_seats")
    seat = relationship("Seat", back_populates="booking_seats")

    __table_args__ = (
        Index("idx_show_seat_active", "show_id", "seat_id", "is_active"),
    )

    def __repr__(self):
        return f"<BookingSeat {self.seat_code} for Show {self.show_id} (Active: {self.is_active})>"
