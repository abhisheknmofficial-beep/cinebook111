import pytest
from datetime import date


def test_admin_stats(client, admin_token):
    res = client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "total_revenue" in data
    assert "total_bookings" in data


def test_admin_get_users(client, admin_token, normal_user):
    res = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    users = res.json()
    assert len(users) >= 2
    assert any(u["email"] == normal_user.email for u in users)


def test_admin_schedule_and_delete_show(client, admin_token, test_theatre_and_show):
    movie = test_theatre_and_show["movie"]
    theatre = test_theatre_and_show["theatre"]
    screen = test_theatre_and_show["screen"]

    # 1. Schedule Show
    payload = {
        "movie_id": movie.id,
        "theatre_id": theatre.id,
        "screen_id": screen.id,
        "show_date": str(date.today()),
        "show_time": "11:30 PM",
        "base_price": 250.0,
        "is_active": True
    }
    create_res = client.post(
        "/api/shows",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_res.status_code == 201
    show_id = create_res.json()["id"]

    # 2. Delete Show
    del_res = client.delete(
        f"/api/shows/{show_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert del_res.status_code == 200


def test_admin_dsa_benchmark(client, admin_token):
    res = client.get(
        "/api/admin/dsa-benchmark?size=500",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "sorting" in data
    assert "searching" in data
    assert "merge_sort_ms" in data["sorting"]
    assert "binary_search_microseconds" in data["searching"]
