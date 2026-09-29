import pytest
from app.dsa.search import linear_search, binary_search, binary_search_range
from app.dsa.sorting import merge_sort, quick_sort, sort_catalog
from app.dsa.hashing import ChainingHashTable, SeatStatusMap, MovieLookupCache
from app.dsa.queue import FIFOQueue, BookingRequest
from app.dsa.seat_allocation import SeatGridMatrix, SeatNode
from app.dsa.graph import BookingGraph


def test_linear_search():
    items = [{"id": 1, "title": "Avatar"}, {"id": 2, "title": "Avengers"}, {"id": 3, "title": "Batman"}]
    found = linear_search(items, lambda x: "ven" in x["title"].lower())
    assert len(found) == 1
    assert found[0]["title"] == "Avengers"

    not_found = linear_search(items, lambda x: "Titanic" in x["title"])
    assert len(not_found) == 0


def test_binary_search():
    sorted_numbers = [10, 25, 33, 47, 52, 68, 79, 91, 105]
    match = binary_search(sorted_numbers, 52, lambda x: x)
    assert match == 52

    absent = binary_search(sorted_numbers, 100, lambda x: x)
    assert absent is None


def test_binary_search_range():
    sorted_ratings = [7.1, 7.5, 8.0, 8.2, 8.4, 8.8, 9.1]
    in_range = binary_search_range(sorted_ratings, 8.0, 8.5, lambda x: x)
    assert in_range == [8.0, 8.2, 8.4]


def test_merge_sort():
    movies = [
        {"title": "Movie C", "rating": 7.5},
        {"title": "Movie A", "rating": 8.9},
        {"title": "Movie B", "rating": 8.2}
    ]
    # Descending by rating
    sorted_desc = merge_sort(movies, key_func=lambda x: x["rating"], reverse=True)
    assert sorted_desc[0]["title"] == "Movie A"
    assert sorted_desc[1]["title"] == "Movie B"
    assert sorted_desc[2]["title"] == "Movie C"

    # Ascending
    sorted_asc = merge_sort(movies, key_func=lambda x: x["rating"], reverse=False)
    assert sorted_asc[0]["title"] == "Movie C"


def test_quick_sort():
    prices = [350.0, 180.0, 420.0, 200.0, 150.0]
    sorted_prices = quick_sort(prices)
    assert sorted_prices == [150.0, 180.0, 200.0, 350.0, 420.0]

    sorted_prices_desc = quick_sort(prices, reverse=True)
    assert sorted_prices_desc == [420.0, 350.0, 200.0, 180.0, 150.0]


def test_chaining_hash_table():
    ht = ChainingHashTable(initial_capacity=4)
    ht.put("movie:1", "Interstellar")
    ht.put("movie:2", "Inception")
    ht.put("movie:3", "Oppenheimer")
    ht.put("movie:4", "Tenet")
    ht.put("movie:5", "Dunkirk")  # Triggers dynamic resizing

    assert ht.get("movie:1") == "Interstellar"
    assert ht.get("movie:3") == "Oppenheimer"
    assert ht.get("movie:99") is None

    # Test update
    ht.put("movie:1", "Interstellar Extended")
    assert ht.get("movie:1") == "Interstellar Extended"

    # Test deletion
    deleted = ht.delete("movie:2")
    assert deleted is True
    assert ht.get("movie:2") is None


def test_fifo_queue():
    q = FIFOQueue(max_size=5)
    assert q.is_empty() is True
    assert q.size() == 0

    q.enqueue("REQ_001")
    q.enqueue("REQ_002")
    q.enqueue("REQ_003")

    assert q.size() == 3
    assert q.peek() == "REQ_001"

    popped = q.dequeue()
    assert popped == "REQ_001"
    assert q.peek() == "REQ_002"
    assert q.size() == 2


def test_seat_grid_matrix_and_sliding_window():
    class MockSeat:
        def __init__(self, id, row, col, code, stype="REGULAR"):
            self.id = id
            self.row_label = row
            self.seat_number = col
            self.seat_code = code
            self.seat_type = stype

    seats_data = []
    seat_id = 1
    for r in ["A", "B", "C"]:
        for c in range(1, 6):
            seats_data.append(MockSeat(seat_id, r, c, f"{r}{c}"))
            seat_id += 1

    matrix = SeatGridMatrix(rows=3, cols=5, base_price=200.0)
    # Seat B3 is booked
    booked_ids = {8}  # Seat B3 has id 8
    matrix.populate_seats(seats_data, booked_ids)

    # Validate availability check
    valid, msg, nodes = matrix.validate_seats_available([1, 2])
    assert valid is True
    assert len(nodes) == 2

    # Colliding seat check (B3 is booked)
    valid_coll, msg_coll, _ = matrix.validate_seats_available([7, 8])
    assert valid_coll is False
    assert "already booked" in msg_coll

    # Contiguous Seat Sliding Window recommendation (request 2 seats)
    rec = matrix.find_contiguous_seats(2)
    assert len(rec) == 2
    # Expects contiguous in row B (e.g. B1, B2 or B4, B5) or row A
    assert rec[0].row_label == rec[1].row_label
    assert abs(rec[0].col_number - rec[1].col_number) == 1


def test_booking_graph_bfs_and_dfs():
    g = BookingGraph()
    g.add_node("movie:1", "MOVIE", {"title": "Avengers"})
    g.add_node("theatre:10", "THEATRE", {"name": "PVR Mumbai", "city": "Mumbai"})
    g.add_node("theatre:20", "THEATRE", {"name": "INOX Delhi", "city": "Delhi"})
    g.add_node("screen:101", "SCREEN", {"name": "Audi 1"})
    g.add_node("show:1001", "SHOW", {"time": "07:00 PM"})

    g.add_edge("movie:1", "theatre:10")
    g.add_edge("movie:1", "theatre:20")
    g.add_edge("theatre:10", "screen:101")
    g.add_edge("screen:101", "show:1001")

    # BFS from movie in Mumbai should find show:1001
    shows_mumbai = g.bfs_find_shows_for_movie(1, city_filter="mumbai")
    assert len(shows_mumbai) == 1
    assert shows_mumbai[0]["time"] == "07:00 PM"

    # BFS from movie in Delhi should find 0 shows (no screen added under theatre:20 yet)
    shows_delhi = g.bfs_find_shows_for_movie(1, city_filter="delhi")
    assert len(shows_delhi) == 0

    # DFS Lineage path tracing
    paths = g.dfs_trace_lineage("movie:1")
    assert len(paths) == 2
    # One path leads to show:1001
    assert "show:1001" in paths[0] or "show:1001" in paths[1]
