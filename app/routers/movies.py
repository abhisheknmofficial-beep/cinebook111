from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.movie import Movie
from app.models.theatre import Show, Theatre
from app.schemas.movie import MovieCreate, MovieUpdate, MovieResponse
from app.auth.dependencies import get_current_admin
from app.services.search_service import search_and_filter_movies, get_cached_movie, movie_cache

router = APIRouter(prefix="/api/movies", tags=["Movies"])

@router.get("", response_model=List[MovieResponse])
def get_movies(
    q: Optional[str] = Query(None, description="Search term for title/genre/language"),
    city: Optional[str] = Query(None, description="Filter by theatre city"),
    language: Optional[str] = Query(None, description="Filter by language"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    min_rating: Optional[float] = Query(None, description="Minimum rating filter"),
    sort_by: str = Query("rating_desc", description="Sorting option"),
    db: Session = Depends(get_db)
):
    """
    Retrieves movies applying DSA-backed search, filtering, and sorting (Merge/Quick Sort).
    """
    return search_and_filter_movies(
        db=db,
        query=q,
        city=city,
        language=language,
        genre=genre,
        min_rating=min_rating,
        sort_by=sort_by
    )

@router.get("/{movie_id}")
def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    """Retrieves full movie details along with scheduled shows and theatres."""
    movie = get_cached_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")

    # Fetch shows grouped by theatre
    shows = (
        db.query(Show)
        .join(Theatre, Show.theatre_id == Theatre.id)
        .filter(Show.movie_id == movie_id, Show.is_active == True)
        .all()
    )

    shows_data = []
    for s in shows:
        shows_data.append({
            "id": s.id,
            "show_date": str(s.show_date),
            "show_time": s.show_time,
            "base_price": s.base_price,
            "theatre_id": s.theatre.id,
            "theatre_name": s.theatre.name,
            "theatre_city": s.theatre.city,
            "screen_name": s.screen.name
        })

    return {
        "id": movie.id,
        "title": movie.title,
        "genre": movie.genre,
        "language": movie.language,
        "duration_mins": movie.duration_mins,
        "rating": movie.rating,
        "release_date": str(movie.release_date),
        "description": movie.description,
        "poster_url": movie.poster_url,
        "backdrop_url": movie.backdrop_url,
        "shows": shows_data
    }

@router.post("", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(
    payload: MovieCreate,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to create a new movie entry."""
    movie = Movie(**payload.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie

@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    payload: MovieUpdate,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to update movie details."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(movie, field, val)

    db.commit()
    db.refresh(movie)
    movie_cache.clear()
    return movie

@router.delete("/{movie_id}", status_code=status.HTTP_200_OK)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to delete a movie."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")

    db.delete(movie)
    db.commit()
    movie_cache.clear()
    return {"message": f"Movie '{movie.title}' deleted successfully."}
