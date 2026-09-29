from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# Seat Schemas
class SeatResponse(BaseModel):
    id: int
    screen_id: int
    row_label: str
    seat_number: int
    seat_code: str
    seat_type: str

    model_config = ConfigDict(from_attributes=True)

# Screen Schemas
class ScreenBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    total_rows: int = Field(5, ge=1, le=26)
    total_cols: int = Field(8, ge=1, le=30)

class ScreenCreate(ScreenBase):
    theatre_id: int

class ScreenResponse(ScreenBase):
    id: int
    theatre_id: int

    model_config = ConfigDict(from_attributes=True)

# Theatre Schemas
class TheatreBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    city: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=5, max_length=255)

class TheatreCreate(TheatreBase):
    pass

class TheatreResponse(TheatreBase):
    id: int
    screens: List[ScreenResponse] = []

    model_config = ConfigDict(from_attributes=True)

# Show Schemas
class ShowBase(BaseModel):
    movie_id: int
    theatre_id: int
    screen_id: int
    show_date: date
    show_time: str
    base_price: float = Field(200.0, gt=0)
    is_active: bool = True

class ShowCreate(ShowBase):
    pass

class ShowUpdate(BaseModel):
    movie_id: Optional[int] = None
    theatre_id: Optional[int] = None
    screen_id: Optional[int] = None
    show_date: Optional[date] = None
    show_time: Optional[str] = None
    base_price: Optional[float] = None
    is_active: Optional[bool] = None

class ShowResponse(ShowBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
