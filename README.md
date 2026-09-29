# 🎬 CineBook — Movie & Event Ticket Booking App

> A full-stack BookMyShow-inspired web application built with **FastAPI**, **SQLite**, **Jinja2**, and **DSA implementations** — created as a BSc AI & Data Science college project.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🌐 Live Demo

> Deployed on Render: **[https://cinebook.onrender.com](https://cinebook.onrender.com)** *(update link after deployment)*

**Demo Credentials:**
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@cinebook.com | admin123 |
| User | user@cinebook.com | user1234 |

---

## ✨ Features

### 👤 User Features
- Register / Login with JWT authentication
- Browse movies and events with search & filters
- View movie details with show timings by city
- Interactive seat map with visual seat selection
- Booking with payment simulation (UPI / Card / NetBanking)
- Booking history and cancellation
- User profile

### 🛠️ Admin Features
- Admin dashboard with stats
- Manage Movies, Events, Theatres, Shows
- View all bookings and users

### 🧮 DSA Features (College Project Highlight)
- **Binary Search** — fast movie/event search
- **Merge Sort & Quick Sort** — sorting movies by rating/date
- **Hash Table with Chaining** — fast seat lookup
- **FIFO Queue** — booking queue processing
- **BFS & DFS Graph** — theatre-screen relationship traversal
- **Sliding Window** — available seat range detection
- **2D Matrix** — seat grid representation

### 🔗 Interactive DSA Explorer
Visit `/dsa-explorer` for a live, visual demo of all DSA algorithms used in the app.

---

## 🗂️ Project Structure

```
cinebook/
├── app/
│   ├── auth/           # JWT authentication & dependencies
│   ├── dsa/            # All DSA algorithm implementations
│   ├── models/         # SQLAlchemy database models
│   ├── routers/        # API endpoints & page routes
│   ├── schemas/        # Pydantic request/response schemas
│   ├── services/       # Business logic (booking, search, admin)
│   ├── static/         # CSS, JS, images
│   ├── templates/      # Jinja2 HTML templates
│   ├── database.py     # Database engine & session
│   └── main.py         # FastAPI app entry point
├── seed/
│   └── seed_data.py    # Sample data seeder
├── tests/              # Pytest test suite (32 tests)
├── requirements.txt
├── run.py              # App entry point
└── README.md
```

---

## 🚀 Getting Started (Local)

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/cinebook.git
cd cinebook
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed the database
```bash
python seed/seed_data.py
```

### 4. Run the app
```bash
python run.py
```

### 5. Open in browser
- **App:** http://127.0.0.1:8000
- **API Docs:** http://127.0.0.1:8000/docs
- **DSA Explorer:** http://127.0.0.1:8000/dsa-explorer

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

All **32 tests** cover authentication, booking flow, payment, admin, movies, and DSA algorithms.

---

## 🧮 DSA Algorithms Used

| Algorithm | Where Used |
|-----------|------------|
| Binary Search | Movie/event search by title |
| Merge Sort | Sort movies by rating |
| Quick Sort | Sort movies by release date |
| Hash Table (Chaining) | Seat code → seat ID lookup |
| FIFO Queue | Booking request queue |
| BFS & DFS | Theatre → Screen → Seat graph |
| Sliding Window | Find consecutive available seats |
| 2D Matrix | Seat grid visualization |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python |
| Server | Uvicorn |
| Database | SQLite (via SQLAlchemy ORM) |
| Auth | JWT (python-jose), bcrypt |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Testing | Pytest |

---

## 📡 Deployment

This app is deployed on **Render** (free tier). See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step deployment instructions.

---

## 👩‍💻 Author

**Gayatri** — BSc AI & Data Science  
Built as a DSA College Project

---

## 📄 License

MIT License — free to use for educational purposes.
