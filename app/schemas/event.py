from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    category: str = Field(..., min_length=2, max_length=50)
    location: str = Field(..., min_length=2, max_length=200)
    event_date: Optional[date] = None
    event_time: str = Field(..., min_length=2, max_length=20)
    description: str = Field(..., min_length=10)
    price: float = Field(..., gt=0)
    total_seats: int = Field(100, gt=0)
    available_seats: Optional[int] = None
    poster_url: Optional[str] = None
    is_active: bool = True

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    total_seats: Optional[int] = None
    available_seats: Optional[int] = None
    poster_url: Optional[str] = None
    is_active: Optional[bool] = None

class EventResponse(EventBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
