from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models.user import User, UserRole
from app.models.movie import Movie
from app.models.event import Event
from app.models.theatre import Theatre, Show, Screen
from app.models.booking import Booking, BookingStatus
from app.auth.dependencies import get_optional_current_user, get_current_user, get_current_admin
from app.services.search_service import search_and_filter_movies, search_and_filter_events
from app.services.booking_service import get_show_seating_matrix
from app.services.admin_service import get_admin_dashboard_stats

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter(include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
def page_home(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_optional_current_user)):
    featured_movies = db.query(Movie).filter(Movie.is_active == True).order_by(Movie.rating.desc()).limit(6).all()
    upcoming_events = db.query(Event).filter(Event.is_active == True).limit(4).all()
    theatres = db.query(Theatre).all()
    cities = sorted(list({t.city for t in theatres if t.city}))
    return templates.TemplateResponse(request, "index.html", {
        "user": user,
        "featured_movies": featured_movies,
        "upcoming_events": upcoming_events,
        "cities": cities
    })

@router.get("/login", response_class=HTMLResponse)
def page_login(request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"user": None})

@router.get("/register", response_class=HTMLResponse)
def page_register(request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request, "register.html", {"user": None})

@router.get("/logout")
def page_logout():
    response = RedirectResponse(url="/login?logged_out=1", status_code=303)
    response.delete_cookie(key="access_token")
    return response

@router.get("/movies", response_class=HTMLResponse)
def page_movies(
    request: Request,
    q: Optional[str] = None,
    city: Optional[str] = None,
    language: Optional[str] = None,
    genre: Optional[str] = None,
    sort_by: str = "rating_desc",
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    movies = search_and_filter_movies(
        db=db, query=q, city=city, language=language, genre=genre, sort_by=sort_by
    )
    theatres = db.query(Theatre).all()
    cities = sorted(list({t.city for t in theatres if t.city}))
    all_genres = ["Action", "Sci-Fi", "Drama", "Thriller", "Adventure", "Animation", "Comedy"]
    all_languages = ["English", "Hindi", "Telugu", "Tamil"]

    return templates.TemplateResponse(request, "movies.html", {
        "user": user,
        "movies": movies,
        "cities": cities,
        "genres": all_genres,
        "languages": all_languages,
        "selected_city": city or "",
        "selected_genre": genre or "",
        "selected_lang": language or "",
        "selected_sort": sort_by,
        "query": q or ""
    })

@router.get("/movies/{movie_id}", response_class=HTMLResponse)
def page_movie_detail(
    movie_id: int,
    request: Request,
    city: Optional[str] = None,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    shows_query = (
        db.query(Show)
        .join(Theatre, Show.theatre_id == Theatre.id)
        .filter(Show.movie_id == movie_id, Show.is_active == True)
    )
    if city:
        shows_query = shows_query.filter(Theatre.city.ilike(f"%{city}%"))
    shows = shows_query.all()

    # Group shows by Theatre
    theatre_shows = {}
    for s in shows:
        t_id = s.theatre.id
        if t_id not in theatre_shows:
            theatre_shows[t_id] = {
                "theatre": s.theatre,
                "shows": []
            }
        theatre_shows[t_id]["shows"].append(s)

    theatres = db.query(Theatre).all()
    cities = sorted(list({t.city for t in theatres if t.city}))

    return templates.TemplateResponse(request, "movie_detail.html", {
        "user": user,
        "movie": movie,
        "theatre_shows": list(theatre_shows.values()),
        "cities": cities,
        "selected_city": city or ""
    })

@router.get("/events", response_class=HTMLResponse)
def page_events(
    request: Request,
    q: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    sort_by: str = "price_asc",
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    events = search_and_filter_events(
        db=db, query=q, category=category, location=location, sort_by=sort_by
    )
    categories = ["Concert", "Comedy Show", "Workshop", "Sports Event", "Theatre & Play"]
    return templates.TemplateResponse(request, "events.html", {
        "user": user,
        "events": events,
        "categories": categories,
        "selected_cat": category or "",
        "query": q or "",
        "selected_sort": sort_by
    })

@router.get("/events/{event_id}", response_class=HTMLResponse)
def page_event_detail(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return templates.TemplateResponse(request, "event_detail.html", {
        "user": user,
        "event": event
    })

@router.get("/theatres", response_class=HTMLResponse)
def page_theatres(
    request: Request,
    city: Optional[str] = None,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    theatres_query = db.query(Theatre)
    if city:
        theatres_query = theatres_query.filter(Theatre.city.ilike(f"%{city}%"))
    theatres = theatres_query.all()
    all_theatres = db.query(Theatre).all()
    cities = sorted(list({t.city for t in all_theatres if t.city}))
    return templates.TemplateResponse(request, "theatres.html", {
        "user": user,
        "theatres": theatres,
        "cities": cities,
        "selected_city": city or ""
    })

@router.get("/shows/{show_id}")
def page_show_redirect(show_id: int):
    return RedirectResponse(url=f"/seats/{show_id}", status_code=303)

@router.get("/seats/{show_id}", response_class=HTMLResponse)
def page_seats(
    show_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user:
        return RedirectResponse(url=f"/login?next=/seats/{show_id}", status_code=303)

    show, matrix = get_show_seating_matrix(db, show_id)
    return templates.TemplateResponse(request, "seats.html", {
        "user": user,
        "show": show,
        "grid": matrix.to_matrix_json()
    })

@router.get("/booking/{booking_id}", response_class=HTMLResponse)
def page_booking_summary(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user:
        return RedirectResponse(url=f"/login?next=/booking/{booking_id}", status_code=303)

    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user.role != "ADMIN" and booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return templates.TemplateResponse(request, "booking_summary.html", {
        "user": user,
        "booking": booking
    })

@router.get("/payment/{booking_id}", response_class=HTMLResponse)
def page_payment(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user:
        return RedirectResponse(url=f"/login?next=/payment/{booking_id}", status_code=303)

    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user.role != "ADMIN" and booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if booking.status == BookingStatus.CONFIRMED:
        return RedirectResponse(url=f"/booking-confirmation/{booking.id}", status_code=303)

    return templates.TemplateResponse(request, "payment.html", {
        "user": user,
        "booking": booking
    })

@router.get("/booking-confirmation/{booking_id}", response_class=HTMLResponse)
def page_booking_confirmation(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user.role != "ADMIN" and booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return templates.TemplateResponse(request, "booking_confirmation.html", {
        "user": user,
        "booking": booking
    })

@router.get("/my-bookings", response_class=HTMLResponse)
def page_my_bookings(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user:
        return RedirectResponse(url="/login?next=/my-bookings", status_code=303)

    bookings = db.query(Booking).filter(Booking.user_id == user.id).order_by(Booking.id.desc()).all()
    return templates.TemplateResponse(request, "my_bookings.html", {
        "user": user,
        "bookings": bookings
    })

@router.get("/profile", response_class=HTMLResponse)
def page_profile(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user:
        return RedirectResponse(url="/login?next=/profile", status_code=303)

    bookings_count = db.query(Booking).filter(Booking.user_id == user.id).count()
    return templates.TemplateResponse(request, "profile.html", {
        "user": user,
        "bookings_count": bookings_count
    })

@router.get("/dsa-explorer", response_class=HTMLResponse)
def page_dsa_explorer(
    request: Request,
    user: Optional[User] = Depends(get_optional_current_user)
):
    """Interactive DSA demonstration console for college viva."""
    return templates.TemplateResponse(request, "dsa_explorer.html", {
        "user": user
    })

# ----------------- ADMIN PAGES -----------------

@router.get("/admin", response_class=HTMLResponse)
def page_admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user:
        return RedirectResponse(url="/login?next=/admin", status_code=303)
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin privileges required")

    stats = get_admin_dashboard_stats(db)
    return templates.TemplateResponse(request, "admin/dashboard.html", {
        "user": user,
        "stats": stats
    })

@router.get("/admin/movies", response_class=HTMLResponse)
def page_admin_movies(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user or user.role != "ADMIN":
        return RedirectResponse(url="/login?next=/admin/movies", status_code=303)

    movies = db.query(Movie).order_by(Movie.id.desc()).all()
    return templates.TemplateResponse(request, "admin/movies.html", {
        "user": user,
        "movies": movies
    })

@router.get("/admin/events", response_class=HTMLResponse)
def page_admin_events(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user or user.role != "ADMIN":
        return RedirectResponse(url="/login?next=/admin/events", status_code=303)

    events = db.query(Event).order_by(Event.id.desc()).all()
    return templates.TemplateResponse(request, "admin/events.html", {
        "user": user,
        "events": events
    })

@router.get("/admin/theatres", response_class=HTMLResponse)
def page_admin_theatres(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user or user.role != "ADMIN":
        return RedirectResponse(url="/login?next=/admin/theatres", status_code=303)

    theatres = db.query(Theatre).order_by(Theatre.id.desc()).all()
    return templates.TemplateResponse(request, "admin/theatres.html", {
        "user": user,
        "theatres": theatres
    })

@router.get("/admin/shows", response_class=HTMLResponse)
def page_admin_shows(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user or user.role != "ADMIN":
        return RedirectResponse(url="/login?next=/admin/shows", status_code=303)

    shows = db.query(Show).order_by(Show.id.desc()).all()
    movies = db.query(Movie).filter(Movie.is_active == True).all()
    theatres = db.query(Theatre).all()
    return templates.TemplateResponse(request, "admin/shows.html", {
        "user": user,
        "shows": shows,
        "movies": movies,
        "theatres": theatres
    })

@router.get("/admin/bookings", response_class=HTMLResponse)
def page_admin_bookings(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user or user.role != "ADMIN":
        return RedirectResponse(url="/login?next=/admin/bookings", status_code=303)

    bookings = db.query(Booking).order_by(Booking.id.desc()).all()
    return templates.TemplateResponse(request, "admin/bookings.html", {
        "user": user,
        "bookings": bookings
    })

@router.get("/admin/users", response_class=HTMLResponse)
def page_admin_users(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    if not user or user.role != "ADMIN":
        return RedirectResponse(url="/login?next=/admin/users", status_code=303)

    users = db.query(User).order_by(User.id.desc()).all()
    return templates.TemplateResponse(request, "admin/users.html", {
        "user": user,
        "users": users
    })
