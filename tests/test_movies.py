import pytest


def test_get_movies(client, test_theatre_and_show):
    response = client.get("/api/movies")
    assert response.status_code == 200
    movies = response.json()
    assert len(movies) >= 1
    assert any(m["title"] == "Test Inception" for m in movies)


def test_movie_search_by_query(client, test_theatre_and_show):
    response = client.get("/api/movies?q=inception")
    assert response.status_code == 200
    movies = response.json()
    assert len(movies) == 1
    assert "Inception" in movies[0]["title"]

    # Search for nonexistent
    empty_res = client.get("/api/movies?q=NonExistentMovie999")
    assert empty_res.status_code == 200
    assert len(empty_res.json()) == 0


def test_movie_sorting(client, test_theatre_and_show, db):
    from app.models.movie import Movie
    from datetime import date

    m2 = Movie(
        title="Alpha Movie",
        genre="Drama",
        language="Hindi",
        duration_mins=120,
        rating=9.5,
        release_date=date.today(),
        description="High rated movie for sorting check"
    )
    db.add(m2)
    db.commit()

    # Sort rating high to low (DSA Merge Sort)
    res = client.get("/api/movies?sort_by=rating_desc")
    assert res.status_code == 200
    sorted_movies = res.json()
    assert sorted_movies[0]["title"] == "Alpha Movie"
    assert sorted_movies[0]["rating"] == 9.5


def test_get_movie_details(client, test_theatre_and_show):
    movie_id = test_theatre_and_show["movie"].id
    response = client.get(f"/api/movies/{movie_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Inception"
    assert "shows" in data
    assert len(data["shows"]) >= 1
    assert data["shows"][0]["theatre_name"] == "Test Cinema"


def test_admin_create_update_delete_movie(client, admin_token):
    # 1. Create
    payload = {
        "title": "Interstellar Odyssey",
        "genre": "Sci-Fi",
        "language": "English",
        "duration_mins": 169,
        "rating": 8.9,
        "description": "Explorers travel through a wormhole in space in an attempt to ensure humanity's survival."
    }
    create_res = client.post(
        "/api/movies",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_res.status_code == 201
    movie_id = create_res.json()["id"]

    # 2. Update
    update_res = client.put(
        f"/api/movies/{movie_id}",
        json={"rating": 9.0},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["rating"] == 9.0

    # 3. Delete
    del_res = client.delete(
        f"/api/movies/{movie_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert del_res.status_code == 200

    # Verify gone
    get_res = client.get(f"/api/movies/{movie_id}")
    assert get_res.status_code == 404
