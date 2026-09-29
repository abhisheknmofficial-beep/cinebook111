from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.movie import Movie
from app.models.event import Event
from app.models.theatre import Theatre, Show, Screen
from app.dsa.search import linear_search, binary_search
from app.dsa.sorting import sort_catalog
from app.dsa.graph import BookingGraph
from app.dsa.hashing import MovieLookupCache

movie_cache = MovieLookupCache()

def get_cached_movie(db: Session, movie_id: int) -> Optional[Movie]:
    """O(1) hash map retrieval with fallback to database."""
    cached = movie_cache.get_by_id(movie_id)
    if cached:
        return cached
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        movie_cache.insert(movie)
    return movie

def search_and_filter_movies(
    db: Session,
    query: Optional[str] = None,
    city: Optional[str] = None,
    language: Optional[str] = None,
    genre: Optional[str] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "rating_desc"
) -> List[Movie]:
    """
    Search and filter movies utilizing custom DSA algorithms:
    - Linear Search for flexible multi-term substring match.
    - Merge Sort / Quick Sort for stable or in-place ordering.
    """
    all_movies = db.query(Movie).filter(Movie.is_active == True).all()

    # If city filter is specified, find movie IDs showing in that city
    valid_movie_ids = None
    if city:
        shows_in_city = (
            db.query(Show.movie_id)
            .join(Theatre, Show.theatre_id == Theatre.id)
            .filter(Theatre.city.ilike(f"%{city}%"), Show.is_active == True)
            .distinct()
            .all()
        )
        valid_movie_ids = {s[0] for s in shows_in_city}

    # 1. DSA Linear Search with predicate for search term and filter criteria
    def match_predicate(m: Movie) -> bool:
        if valid_movie_ids is not None and m.id not in valid_movie_ids:
            return False
        if language and m.language.lower() != language.lower():
            return False
        if genre and genre.lower() not in m.genre.lower():
            return False
        if min_rating and (m.rating or 0.0) < min_rating:
            return False
        if query:
            q = query.strip().lower()
            in_title = q in m.title.lower()
            in_genre = q in m.genre.lower()
            in_lang = q in m.language.lower()
            in_desc = q in (m.description or "").lower()
            return in_title or in_genre or in_lang or in_desc
        return True

    filtered_movies = linear_search(all_movies, match_predicate)

    # 2. DSA Sorting: Merge Sort (stable) or Quick Sort
    algorithm = "quick_sort" if "price" in sort_by else "merge_sort"
    sorted_movies = sort_catalog(filtered_movies, sort_by=sort_by, algorithm=algorithm)

    return sorted_movies

def search_and_filter_events(
    db: Session,
    query: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    max_price: Optional[float] = None,
    sort_by: str = "price_asc"
) -> List[Event]:
    """Search and filter live events utilizing Linear Search and Merge Sort."""
    all_events = db.query(Event).filter(Event.is_active == True).all()

    def match_predicate(e: Event) -> bool:
        if category and e.category.lower() != category.lower():
            return False
        if location and location.lower() not in e.location.lower():
            return False
        if max_price and e.price > max_price:
            return False
        if query:
            q = query.strip().lower()
            in_title = q in e.title.lower()
            in_cat = q in e.category.lower()
            in_loc = q in e.location.lower()
            return in_title or in_cat or in_loc
        return True

    filtered_events = linear_search(all_events, match_predicate)
    sorted_events = sort_catalog(filtered_events, sort_by=sort_by, algorithm="quick_sort")
    return sorted_events

def build_ecosystem_graph(db: Session) -> BookingGraph:
    """
    Constructs a directed hierarchical graph of Movie -> Theatre -> Screen -> Show.
    Used for DSA graph traversal demonstration (BFS / DFS).
    """
    graph = BookingGraph()
    shows = db.query(Show).filter(Show.is_active == True).all()

    for s in shows:
        movie = s.movie
        theatre = s.theatre
        screen = s.screen

        if movie and theatre and screen:
            m_id = f"movie:{movie.id}"
            t_id = f"theatre:{theatre.id}"
            sc_id = f"screen:{screen.id}"
            sh_id = f"show:{s.id}"

            graph.add_node(m_id, "MOVIE", {"id": movie.id, "title": movie.title})
            graph.add_node(t_id, "THEATRE", {"id": theatre.id, "name": theatre.name, "city": theatre.city})
            graph.add_node(sc_id, "SCREEN", {"id": screen.id, "name": screen.name})
            graph.add_node(sh_id, "SHOW", {
                "id": s.id,
                "date": str(s.show_date),
                "time": s.show_time,
                "price": s.base_price,
                "theatre_name": theatre.name,
                "theatre_city": theatre.city
            })

            # Add directed edges down the hierarchy
            graph.add_edge(m_id, t_id)
            graph.add_edge(t_id, sc_id)
            graph.add_edge(sc_id, sh_id)

    return graph
