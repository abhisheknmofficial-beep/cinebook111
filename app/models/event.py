from datetime import date
from sqlalchemy import Column, Integer, String, Float, Text, Date, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # Concert, Comedy Show, Workshop, Sports Event
    location = Column(String(200), nullable=False, index=True)
    event_date = Column(Date, default=date.today)
    event_time = Column(String(20), nullable=False)  # e.g., "07:00 PM"
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    total_seats = Column(Integer, default=100)
    available_seats = Column(Integer, default=100)
    poster_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    bookings = relationship("Booking", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event {self.title} ({self.category})>"
