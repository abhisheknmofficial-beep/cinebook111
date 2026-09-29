from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class SeatSelectionItem(BaseModel):
    seat_id: int
    seat_code: str

class BookingCreate(BaseModel):
    show_id: Optional[int] = None
    event_id: Optional[int] = None
    seat_ids: List[int] = []  # For movie shows
    num_event_tickets: Optional[int] = Field(1, ge=1)  # For event bookings

class BookingSeatResponse(BaseModel):
    id: int
    seat_id: int
    seat_code: str
    price: float
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class BookingResponse(BaseModel):
    id: int
    booking_reference: str
    user_id: int
    show_id: Optional[int] = None
    event_id: Optional[int] = None
    total_amount: float
    status: str
    num_tickets: int
    booking_time: datetime
    cancelled_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class BookingDetailResponse(BookingResponse):
    seats: List[BookingSeatResponse] = []
