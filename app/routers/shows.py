from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.theatre import Show, Screen, Theatre
from app.models.movie import Movie
from app.schemas.theatre import ShowCreate, ShowUpdate, ShowResponse
from app.auth.dependencies import get_current_admin
from app.services.booking_service import get_show_seating_matrix

router = APIRouter(prefix="/api/shows", tags=["Shows"])

@router.get("", response_model=List[ShowResponse])
def get_shows(
    movie_id: Optional[int] = Query(None),
    theatre_id: Optional[int] = Query(None),
    show_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieves all scheduled shows matching criteria."""
    query = db.query(Show).filter(Show.is_active == True)
    if movie_id:
        query = query.filter(Show.movie_id == movie_id)
    if theatre_id:
        query = query.filter(Show.theatre_id == theatre_id)
    if show_date:
        query = query.filter(Show.show_date == show_date)
    return query.all()

@router.get("/{show_id}")
def get_show_detail(show_id: int, db: Session = Depends(get_db)):
    """Retrieves single show details with movie, theatre, and screen metadata."""
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found.")

    return {
        "id": show.id,
        "show_date": str(show.show_date),
        "show_time": show.show_time,
        "base_price": show.base_price,
        "is_active": show.is_active,
        "movie": {
            "id": show.movie.id,
            "title": show.movie.title,
            "genre": show.movie.genre,
            "language": show.movie.language,
            "rating": show.movie.rating,
            "poster_url": show.movie.poster_url
        },
        "theatre": {
            "id": show.theatre.id,
            "name": show.theatre.name,
            "city": show.theatre.city,
            "address": show.theatre.address
        },
        "screen": {
            "id": show.screen.id,
            "name": show.screen.name,
            "total_rows": show.screen.total_rows,
            "total_cols": show.screen.total_cols
        }
    }

@router.get("/{show_id}/seats")
def get_show_seats(
    show_id: int,
    recommend_count: Optional[int] = Query(None, description="Request contiguous seats recommendation (DSA)"),
    db: Session = Depends(get_db)
):
    """
    Returns 2D Seating Matrix and seat states for the interactive visual seat map.
    Includes contiguous seat recommendation via DSA Sliding Window algorithm.
    """
    show, matrix = get_show_seating_matrix(db, show_id)

    recommendations = []
    if recommend_count and recommend_count > 0:
        recommended_nodes = matrix.find_contiguous_seats(recommend_count)
        recommendations = [n.to_dict() for n in recommended_nodes]

    return {
        "show_id": show.id,
        "movie_title": show.movie.title,
        "theatre_name": show.theatre.name,
        "theatre_city": show.theatre.city,
        "screen_name": show.screen.name,
        "show_date": str(show.show_date),
        "show_time": show.show_time,
        "base_price": show.base_price,
        "grid": matrix.to_matrix_json(),
        "recommended_seats": recommendations
    }

@router.post("", response_model=ShowResponse, status_code=status.HTTP_201_CREATED)
def create_show(
    payload: ShowCreate,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to create a new showtime."""
    # Validate movie, theatre, screen exist
    movie = db.query(Movie).filter(Movie.id == payload.movie_id).first()
    theatre = db.query(Theatre).filter(Theatre.id == payload.theatre_id).first()
    screen = db.query(Screen).filter(Screen.id == payload.screen_id, Screen.theatre_id == payload.theatre_id).first()

    if not movie or not theatre or not screen:
        raise HTTPException(status_code=400, detail="Invalid movie, theatre, or screen association.")

    show = Show(**payload.model_dump())
    db.add(show)
    db.commit()
    db.refresh(show)
    return show

@router.put("/{show_id}", response_model=ShowResponse)
def update_show(
    show_id: int,
    payload: ShowUpdate,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to update show details or base price."""
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found.")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(show, k, v)

    db.commit()
    db.refresh(show)
    return show

@router.delete("/{show_id}", status_code=status.HTTP_200_OK)
def delete_show(
    show_id: int,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to delete a show."""
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found.")
    db.delete(show)
    db.commit()
    return {"message": "Show deleted successfully."}
