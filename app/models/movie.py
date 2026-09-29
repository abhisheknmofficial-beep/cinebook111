from datetime import date
from sqlalchemy import Column, Integer, String, Float, Text, Date, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    genre = Column(String(100), nullable=False, index=True)  # Action, Drama, Sci-Fi, etc.
    language = Column(String(50), nullable=False, index=True)  # English, Hindi, Telugu, etc.
    duration_mins = Column(Integer, nullable=False)
    rating = Column(Float, default=0.0, index=True)  # e.g., 8.8
    release_date = Column(Date, default=date.today)
    description = Column(Text, nullable=False)
    poster_url = Column(String(500), nullable=True)
    backdrop_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    shows = relationship("Show", back_populates="movie", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Movie {self.title} ({self.rating}/10)>"
