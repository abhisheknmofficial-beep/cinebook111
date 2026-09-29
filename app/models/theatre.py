from datetime import date
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Theatre(Base):
    __tablename__ = "theatres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    address = Column(String(255), nullable=False)

    screens = relationship("Screen", back_populates="theatre", cascade="all, delete-orphan")
    shows = relationship("Show", back_populates="theatre", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Theatre {self.name}, {self.city}>"

class Screen(Base):
    __tablename__ = "screens"

    id = Column(Integer, primary_key=True, index=True)
    theatre_id = Column(Integer, ForeignKey("theatres.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)  # e.g., "Screen 1 - Audi 4K", "IMAX"
    total_rows = Column(Integer, default=5)   # A to E
    total_cols = Column(Integer, default=8)   # 1 to 8

    theatre = relationship("Theatre", back_populates="screens")
    seats = relationship("Seat", back_populates="screen", cascade="all, delete-orphan")
    shows = relationship("Show", back_populates="screen", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Screen {self.name} at {self.theatre_id}>"

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    screen_id = Column(Integer, ForeignKey("screens.id", ondelete="CASCADE"), nullable=False)
    row_label = Column(String(5), nullable=False)  # 'A', 'B', 'C', etc.
    seat_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    seat_code = Column(String(10), nullable=False, index=True)  # 'A1', 'A2', 'B5'
    seat_type = Column(String(20), default="REGULAR")  # 'REGULAR', 'PREMIUM', 'VIP'

    screen = relationship("Screen", back_populates="seats")
    booking_seats = relationship("BookingSeat", back_populates="seat")

    __table_args__ = (
        UniqueConstraint("screen_id", "seat_code", name="uq_screen_seat_code"),
    )

    def __repr__(self):
        return f"<Seat {self.seat_code} ({self.seat_type})>"

class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    theatre_id = Column(Integer, ForeignKey("theatres.id", ondelete="CASCADE"), nullable=False)
    screen_id = Column(Integer, ForeignKey("screens.id", ondelete="CASCADE"), nullable=False)
    show_date = Column(Date, default=date.today, index=True)
    show_time = Column(String(20), nullable=False)  # "10:00 AM", "01:30 PM", "07:00 PM"
    base_price = Column(Float, nullable=False, default=200.0)
    is_active = Column(Boolean, default=True)

    movie = relationship("Movie", back_populates="shows")
    theatre = relationship("Theatre", back_populates="shows")
    screen = relationship("Screen", back_populates="shows")
    bookings = relationship("Booking", back_populates="show", cascade="all, delete-orphan")
    booking_seats = relationship("BookingSeat", back_populates="show", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Show {self.movie_id} at {self.theatre_id} ({self.show_date} {self.show_time})>"
