from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    genre: str = Field(..., min_length=2, max_length=100)
    language: str = Field(..., min_length=2, max_length=50)
    duration_mins: int = Field(..., gt=0, le=400)
    rating: float = Field(0.0, ge=0.0, le=10.0)
    release_date: Optional[date] = None
    description: str = Field(..., min_length=10)
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    is_active: bool = True

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    duration_mins: Optional[int] = None
    rating: Optional[float] = None
    release_date: Optional[date] = None
    description: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    is_active: Optional[bool] = None

class MovieResponse(MovieBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
