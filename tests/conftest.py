import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.movie import Movie
from app.models.theatre import Theatre, Screen, Seat, Show
from app.models.booking import Booking, BookingSeat, BookingStatus
from app.auth.security import hash_password, create_access_token
from datetime import date, datetime

# In-memory SQLite database specifically for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def normal_user(db):
    user = User(
        name="Test User",
        email="testuser@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.USER.value
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    admin = User(
        name="Test Admin",
        email="testadmin@example.com",
        hashed_password=hash_password("adminpass123"),
        role=UserRole.ADMIN.value
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def user_token(normal_user):
    return create_access_token(data={"sub": normal_user.email, "role": normal_user.role, "id": normal_user.id})


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(data={"sub": admin_user.email, "role": admin_user.role, "id": admin_user.id})


@pytest.fixture
def test_theatre_and_show(db):
    theatre = Theatre(name="Test Cinema", city="Mumbai", address="123 Film Street")
    db.add(theatre)
    db.flush()

    screen = Screen(theatre_id=theatre.id, name="Screen 1", total_rows=5, total_cols=8)
    db.add(screen)
    db.flush()

    # Create 40 seats (A1 to E8)
    seats = []
    for r in ["A", "B", "C", "D", "E"]:
        stype = "VIP" if r == "A" else ("PREMIUM" if r in ["B", "C"] else "REGULAR")
        for c in range(1, 9):
            s = Seat(
                screen_id=screen.id,
                row_label=r,
                seat_number=c,
                seat_code=f"{r}{c}",
                seat_type=stype
            )
            db.add(s)
            seats.append(s)
    db.flush()

    movie = Movie(
        title="Test Inception",
        genre="Sci-Fi",
        language="English",
        duration_mins=148,
        rating=8.8,
        release_date=date.today(),
        description="A thief who steals corporate secrets through dream-sharing technology.",
        is_active=True
    )
    db.add(movie)
    db.flush()

    show = Show(
        movie_id=movie.id,
        theatre_id=theatre.id,
        screen_id=screen.id,
        show_date=date.today(),
        show_time="07:00 PM",
        base_price=200.0,
        is_active=True
    )
    db.add(show)
    db.commit()

    return {
        "theatre": theatre,
        "screen": screen,
        "seats": seats,
        "movie": movie,
        "show": show
    }
