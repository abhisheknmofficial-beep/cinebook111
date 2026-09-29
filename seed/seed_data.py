"""
=============================================================================
CineBook Database Seeding Script
=============================================================================
Populates the SQLite database with rich, realistic entertainment catalog data:
- Admin and Normal User accounts
- Theatres across major cities (Mumbai, Bengaluru, Delhi, Hyderabad)
- Screens with 2D Seat Matrix (VIP, Premium, Regular)
- Blockbuster Movies across genres and languages
- Scheduled Shows with varied timings and pricing
- Live Events (Concerts, Standup Comedy, Workshops, Sports)
- Demo Bookings & Payments for realistic dashboard statistics
=============================================================================
"""

import sys
import os
from datetime import date, datetime, timedelta, timezone

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.movie import Movie
from app.models.event import Event
from app.models.theatre import Theatre, Screen, Seat, Show
from app.models.booking import Booking, BookingSeat, BookingStatus
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.auth.security import hash_password


def seed_database():
    print("🚀 Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).first():
            print("⚠️ Database already contains data. Skipping seeding.")
            return

        print("🌱 Seeding Users...")
        admin_user = User(
            name="CineBook Administrator",
            email="admin@cinebook.com",
            hashed_password=hash_password("admin123"),
            phone="+91 99999 88888",
            role=UserRole.ADMIN.value
        )
        normal_user = User(
            name="Gayatri Sharma",
            email="user@cinebook.com",
            hashed_password=hash_password("user123"),
            phone="+91 98765 43210",
            role=UserRole.USER.value
        )
        student_user = User(
            name="Aarav Patel",
            email="aarav@college.edu",
            hashed_password=hash_password("college123"),
            phone="+91 91234 56789",
            role=UserRole.USER.value
        )
        db.add_all([admin_user, normal_user, student_user])
        db.flush()

        print("🌱 Seeding Theatres and Screens...")
        theatres_data = [
            {
                "name": "PVR Icon Infinity Mall",
                "city": "Mumbai",
                "address": "Link Road, Andheri West, Mumbai",
                "screens": [
                    {"name": "Audi 1 (Dolby Atmos)", "rows": 5, "cols": 8},
                    {"name": "Audi 2 (IMAX Laser)", "rows": 5, "cols": 8}
                ]
            },
            {
                "name": "INOX Megaplex Forum",
                "city": "Bengaluru",
                "address": "Koramangala, Hosur Road, Bengaluru",
                "screens": [
                    {"name": "Screen 1 (4K Christie)", "rows": 5, "cols": 8},
                    {"name": "Screen 2 (Insignia)", "rows": 5, "cols": 8}
                ]
            },
            {
                "name": "Cinépolis DLF Avenue",
                "city": "Delhi",
                "address": "Saket District Centre, New Delhi",
                "screens": [
                    {"name": "Screen 1 (Macro XE)", "rows": 5, "cols": 8}
                ]
            },
            {
                "name": "AMB Cinemas Superplex",
                "city": "Hyderabad",
                "address": "Gachibowli - Miyapur Rd, Kondapur, Hyderabad",
                "screens": [
                    {"name": "Screen 1 (VIP Lounge)", "rows": 5, "cols": 8}
                ]
            }
        ]

        created_screens = []
        for t_info in theatres_data:
            theatre = Theatre(name=t_info["name"], city=t_info["city"], address=t_info["address"])
            db.add(theatre)
            db.flush()

            for s_info in t_info["screens"]:
                screen = Screen(
                    theatre_id=theatre.id,
                    name=s_info["name"],
                    total_rows=s_info["rows"],
                    total_cols=s_info["cols"]
                )
                db.add(screen)
                db.flush()
                created_screens.append((theatre, screen))

                # Generate seats for screen
                row_labels = ["A", "B", "C", "D", "E"][:s_info["rows"]]
                for r in row_labels:
                    stype = "VIP" if r == "A" else ("PREMIUM" if r in ["B", "C"] else "REGULAR")
                    for c in range(1, s_info["cols"] + 1):
                        seat = Seat(
                            screen_id=screen.id,
                            row_label=r,
                            seat_number=c,
                            seat_code=f"{r}{c}",
                            seat_type=stype
                        )
                        db.add(seat)

        db.flush()

        print("🌱 Seeding Movies...")
        movies_data = [
            {
                "title": "Interstellar: Beyond Time",
                "genre": "Sci-Fi, Adventure, Drama",
                "language": "English",
                "duration_mins": 169,
                "rating": 8.9,
                "release_date": date(2026, 8, 15),
                "description": "When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot is tasked to pilot a spacecraft, along with a team of researchers, to find a new planet for humans.",
                "poster_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1200&auto=format&fit=crop&q=80"
            },
            {
                "title": "Cyber City: 2099",
                "genre": "Action, Cyberpunk, Sci-Fi",
                "language": "English",
                "duration_mins": 138,
                "rating": 8.4,
                "release_date": date(2026, 9, 1),
                "description": "In a neon-drenched futuristic metropolis ruled by megacorporations, an AI rogue agent uncovers a conspiracy that threatens to rewrite human consciousness.",
                "poster_url": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1200&auto=format&fit=crop&q=80"
            },
            {
                "title": "Kalki's Ascent",
                "genre": "Mythology, Action, Fantasy",
                "language": "Telugu",
                "duration_mins": 165,
                "rating": 8.7,
                "release_date": date(2026, 9, 10),
                "description": "An epic cinematic saga blending ancient Indian mythology with post-apocalyptic technology where divine warriors battle for the fate of humanity.",
                "poster_url": "https://images.unsplash.com/photo-1514533450685-4493e01d1fdc?w=500&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&auto=format&fit=crop&q=80"
            },
            {
                "title": "The Mumbai Chronicles",
                "genre": "Crime, Drama, Thriller",
                "language": "Hindi",
                "duration_mins": 142,
                "rating": 8.2,
                "release_date": date(2026, 8, 28),
                "description": "A high-stakes crime investigation through the bustling streets of Mumbai where an undercover detective races against time to dismantle an underground syndicate.",
                "poster_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=1200&auto=format&fit=crop&q=80"
            },
            {
                "title": "Quantum Odyssey",
                "genre": "Adventure, Sci-Fi",
                "language": "English",
                "duration_mins": 125,
                "rating": 7.9,
                "release_date": date(2026, 9, 18),
                "description": "A team of young quantum physicists accidentally collapses the fabric of spacetime, journeying through parallel dimensions to prevent universal annihilation.",
                "poster_url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=500&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&auto=format&fit=crop&q=80"
            },
            {
                "title": "Whispers in the Mist",
                "genre": "Mystery, Horror, Thriller",
                "language": "Tamil",
                "duration_mins": 118,
                "rating": 8.1,
                "release_date": date(2026, 9, 22),
                "description": "Set in a fog-shrouded hill station in Southern India, an archaeological team stumbles upon an ancient forbidden temple harboring supernatural secrets.",
                "poster_url": "https://images.unsplash.com/photo-1509281373149-e957c6296406?w=500&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1200&auto=format&fit=crop&q=80"
            }
        ]

        created_movies = []
        for m in movies_data:
            movie = Movie(**m)
            db.add(movie)
            created_movies.append(movie)

        db.flush()

        print("🌱 Seeding Scheduled Shows...")
        today = date.today()
        show_times = ["10:00 AM", "01:30 PM", "04:45 PM", "07:30 PM", "10:15 PM"]
        prices = [180.0, 200.0, 250.0, 280.0, 300.0]

        created_shows = []
        # Create shows pairing movies and screens
        for m_idx, movie in enumerate(created_movies):
            for t_idx, (theatre, screen) in enumerate(created_screens):
                time_choice = show_times[(m_idx + t_idx) % len(show_times)]
                price_choice = prices[(m_idx + t_idx) % len(prices)]
                show = Show(
                    movie_id=movie.id,
                    theatre_id=theatre.id,
                    screen_id=screen.id,
                    show_date=today,
                    show_time=time_choice,
                    base_price=price_choice,
                    is_active=True
                )
                db.add(show)
                created_shows.append(show)

        db.flush()

        print("🌱 Seeding Live Events...")
        events_data = [
            {
                "title": "Acoustic Sunset: Indie Music Night",
                "category": "Concert",
                "location": "Bandra Amphitheatre, Mumbai",
                "event_date": today + timedelta(days=7),
                "event_time": "06:30 PM",
                "description": "An intimate evening of soulful indie acoustic melodies featuring top independent singer-songwriters from across India.",
                "price": 499.0,
                "total_seats": 200,
                "available_seats": 185,
                "poster_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80"
            },
            {
                "title": "Laugh Out Loud: Standup Marathon",
                "category": "Comedy Show",
                "location": "The Comedy Factory, Bengaluru",
                "event_date": today + timedelta(days=10),
                "event_time": "08:00 PM",
                "description": "Non-stop laughter with 4 top national comedians performing their fresh hour specials on college life, tech jobs, and dating quirks.",
                "price": 350.0,
                "total_seats": 120,
                "available_seats": 95,
                "poster_url": "https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=500&auto=format&fit=crop&q=80"
            },
            {
                "title": "Hands-on AI & Agentic Systems Workshop",
                "category": "Workshop",
                "location": "Tech Hub Convention Centre, Hyderabad",
                "event_date": today + timedelta(days=14),
                "event_time": "10:00 AM",
                "description": "Deep dive into building Autonomous AI Agents, LLM fine-tuning, and modern DSA applications in artificial intelligence.",
                "price": 899.0,
                "total_seats": 80,
                "available_seats": 60,
                "poster_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&auto=format&fit=crop&q=80"
            },
            {
                "title": "Pro Basketball Championship Finals",
                "category": "Sports Event",
                "location": "Indira Gandhi Indoor Stadium, Delhi",
                "event_date": today + timedelta(days=12),
                "event_time": "05:00 PM",
                "description": "High-octane national basketball championship match between Northern Warriors and Southern Blitz.",
                "price": 299.0,
                "total_seats": 300,
                "available_seats": 240,
                "poster_url": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=500&auto=format&fit=crop&q=80"
            }
        ]

        for ed in events_data:
            ev = Event(**ed)
            db.add(ev)

        db.flush()

        print("🌱 Seeding Demo Completed Bookings & Payments...")
        # Book a couple seats in the first show for normal_user
        first_show = created_shows[0]
        # Retrieve seats for this screen
        show_seats = db.query(Seat).filter(Seat.screen_id == first_show.screen_id).all()
        booked_seats_demo = show_seats[:2]  # A1, A2

        booking = Booking(
            booking_reference="CB-2026-DEMO01",
            user_id=normal_user.id,
            show_id=first_show.id,
            event_id=None,
            total_amount=round(first_show.base_price * 1.5 * 2, 2),  # VIP multiplier 1.5
            status=BookingStatus.CONFIRMED,
            num_tickets=2,
            booking_time=datetime.now(timezone.utc) - timedelta(hours=3)
        )
        db.add(booking)
        db.flush()

        for s in booked_seats_demo:
            bs = BookingSeat(
                booking_id=booking.id,
                show_id=first_show.id,
                seat_id=s.id,
                seat_code=s.seat_code,
                price=round(first_show.base_price * 1.5, 2),
                is_active=True
            )
            db.add(bs)

        payment = Payment(
            booking_id=booking.id,
            payment_reference="PAY-DEMO998877",
            payment_method=PaymentMethod.UPI,
            amount=booking.total_amount,
            status=PaymentStatus.SUCCESS,
            transaction_time=datetime.now(timezone.utc) - timedelta(hours=3)
        )
        db.add(payment)

        db.commit()
        print("✅ Database successfully seeded with demo movies, theatres, shows, events, and users!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
