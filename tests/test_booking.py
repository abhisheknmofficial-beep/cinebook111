import pytest


def test_get_show_seats(client, test_theatre_and_show):
    show_id = test_theatre_and_show["show"].id
    response = client.get(f"/api/shows/{show_id}/seats")
    assert response.status_code == 200
    data = response.json()
    assert "grid" in data
    assert len(data["grid"]) == 5  # 5 rows (A-E)
    assert len(data["grid"][0]) == 8  # 8 columns (1-8)
    assert data["base_price"] == 200.0


def test_create_booking_success(client, user_token, test_theatre_and_show):
    show = test_theatre_and_show["show"]
    seats = test_theatre_and_show["seats"]
    seat_a1 = seats[0]  # VIP seat
    seat_a2 = seats[1]  # VIP seat

    payload = {
        "show_id": show.id,
        "seat_ids": [seat_a1.id, seat_a2.id]
    }
    response = client.post(
        "/api/bookings",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "booking_id" in data
    assert data["status"] == "PENDING"
    assert data["num_tickets"] == 2
    # VIP multiplier is 1.5 -> base 200 * 1.5 * 2 = 600.0
    assert data["total_amount"] == 600.0


def test_double_booking_prevention(client, user_token, admin_token, test_theatre_and_show):
    """
    CRITICAL TEST: Ensures that two users cannot book the same seat.
    User 1 books seat B1.
    User 2 attempts to book seat B1 and B2 -> Server MUST reject with 409 Conflict.
    """
    show = test_theatre_and_show["show"]
    seats = test_theatre_and_show["seats"]
    seat_b1 = seats[8]  # Row B Col 1
    seat_b2 = seats[9]  # Row B Col 2

    # User 1 books B1
    res1 = client.post(
        "/api/bookings",
        json={"show_id": show.id, "seat_ids": [seat_b1.id]},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res1.status_code == 201

    # User 2 attempts to book [B1, B2]
    res2 = client.post(
        "/api/bookings",
        json={"show_id": show.id, "seat_ids": [seat_b1.id, seat_b2.id]},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res2.status_code == 409
    assert "already booked" in res2.json()["detail"].lower()


def test_payment_simulation_success(client, user_token, test_theatre_and_show):
    show = test_theatre_and_show["show"]
    seats = test_theatre_and_show["seats"]
    seat_c1 = seats[16]

    # Create pending booking
    book_res = client.post(
        "/api/bookings",
        json={"show_id": show.id, "seat_ids": [seat_c1.id]},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    booking_id = book_res.json()["booking_id"]

    # Process payment
    pay_res = client.post(
        "/api/payments",
        json={"booking_id": booking_id, "payment_method": "UPI", "simulate_failure": False},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert pay_res.status_code == 201
    pay_data = pay_res.json()
    assert pay_data["status"] == "SUCCESS"

    # Verify booking status transitioned to CONFIRMED
    details_res = client.get(
        f"/api/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert details_res.status_code == 200
    assert details_res.json()["status"] == "CONFIRMED"


def test_payment_simulation_failure_releases_seats(client, user_token, admin_token, test_theatre_and_show):
    show = test_theatre_and_show["show"]
    seats = test_theatre_and_show["seats"]
    seat_d1 = seats[24]

    # User creates booking
    book_res = client.post(
        "/api/bookings",
        json={"show_id": show.id, "seat_ids": [seat_d1.id]},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    booking_id = book_res.json()["booking_id"]

    # Simulate payment failure
    pay_res = client.post(
        "/api/payments",
        json={"booking_id": booking_id, "payment_method": "CARD", "simulate_failure": True},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert pay_res.status_code == 201
    assert pay_res.json()["status"] == "FAILED"

    # Now verify seat D1 is released and another user CAN book it!
    book_again = client.post(
        "/api/bookings",
        json={"show_id": show.id, "seat_ids": [seat_d1.id]},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert book_again.status_code == 201


def test_booking_cancellation_releases_seats(client, user_token, admin_token, test_theatre_and_show):
    show = test_theatre_and_show["show"]
    seats = test_theatre_and_show["seats"]
    seat_e1 = seats[32]

    # Create and confirm booking
    book_res = client.post(
        "/api/bookings",
        json={"show_id": show.id, "seat_ids": [seat_e1.id]},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    booking_id = book_res.json()["booking_id"]
    client.post(
        "/api/payments",
        json={"booking_id": booking_id, "payment_method": "UPI", "simulate_failure": False},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    # Cancel booking
    cancel_res = client.delete(
        f"/api/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # Verify that seat E1 can now be re-booked!
    rebook_res = client.post(
        "/api/bookings",
        json={"show_id": show.id, "seat_ids": [seat_e1.id]},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert rebook_res.status_code == 201
