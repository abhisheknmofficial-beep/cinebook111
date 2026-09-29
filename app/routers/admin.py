import time
import random
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.booking import Booking
from app.schemas.auth import UserResponse
from app.schemas.booking import BookingResponse
from app.auth.dependencies import get_current_admin
from app.services.admin_service import get_admin_dashboard_stats
from app.services.search_service import build_ecosystem_graph
from app.dsa.search import linear_search, binary_search
from app.dsa.sorting import merge_sort, quick_sort

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])

@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Retrieves executive summary analytics for the admin dashboard."""
    stats = get_admin_dashboard_stats(db)
    # Convert recent bookings to JSON-safe structure
    recent_list = []
    for b in stats["recent_bookings"]:
        recent_list.append({
            "id": b.id,
            "reference": b.booking_reference,
            "user_email": b.user.email if b.user else "N/A",
            "amount": b.total_amount,
            "status": b.status,
            "date": str(b.booking_time)[:16]
        })
    stats["recent_bookings"] = recent_list
    return stats

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Retrieves all registered user accounts."""
    return db.query(User).order_by(User.id.desc()).all()

@router.get("/bookings")
def get_all_bookings(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Retrieves all bookings across the platform."""
    bookings = db.query(Booking).order_by(Booking.id.desc()).all()
    out = []
    for b in bookings:
        item_title = "Unknown"
        if b.show and b.show.movie:
            item_title = f"Movie: {b.show.movie.title}"
        elif b.event:
            item_title = f"Event: {b.event.title}"

        out.append({
            "id": b.id,
            "reference": b.booking_reference,
            "user_name": b.user.name if b.user else "Deleted User",
            "user_email": b.user.email if b.user else "N/A",
            "item": item_title,
            "tickets": b.num_tickets,
            "amount": b.total_amount,
            "status": b.status,
            "booking_time": str(b.booking_time)
        })
    return out

@router.get("/dsa-graph")
def get_graph_data(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Returns the Adjacency List Representation of the hierarchical booking graph
    (Movie -> Theatre -> Screen -> Show) for DSA verification.
    """
    graph = build_ecosystem_graph(db)
    nodes_list = [
        {"id": n.node_id, "type": n.node_type, "data": n.data}
        for n in graph.nodes.values()
    ]
    edges_list = []
    for src, targets in graph.adjacency.items():
        for dst in targets:
            edges_list.append({"from": src, "to": dst})

    return {
        "nodes": nodes_list,
        "edges": edges_list,
        "total_nodes": len(nodes_list),
        "total_edges": len(edges_list)
    }

@router.get("/dsa-benchmark")
def run_dsa_benchmark(
    size: int = 5000,
    admin: User = Depends(get_current_admin)
):
    """
    Executes live micro-benchmarks comparing Merge Sort vs Quick Sort
    and Linear Search vs Binary Search for viva presentation.
    """
    data = [random.randint(1, 100000) for _ in range(size)]

    # 1. Sort Benchmarks
    t0 = time.perf_counter()
    merge_sorted = merge_sort(list(data))
    merge_time = (time.perf_counter() - t0) * 1000  # ms

    t0 = time.perf_counter()
    quick_sorted = quick_sort(list(data))
    quick_time = (time.perf_counter() - t0) * 1000  # ms

    # 2. Search Benchmarks on sorted list
    target = data[size // 2]

    t0 = time.perf_counter()
    linear_search(data, lambda x: x == target)
    linear_time_us = (time.perf_counter() - t0) * 1_000_000  # microseconds

    t0 = time.perf_counter()
    binary_search(quick_sorted, target, lambda x: x)
    binary_time_us = (time.perf_counter() - t0) * 1_000_000  # microseconds

    return {
        "sample_size": size,
        "sorting": {
            "merge_sort_ms": round(merge_time, 3),
            "quick_sort_ms": round(quick_time, 3),
            "merge_sort_complexity": "O(n log n) stable",
            "quick_sort_complexity": "O(n log n) in-place"
        },
        "searching": {
            "linear_search_microseconds": round(linear_time_us, 3),
            "binary_search_microseconds": round(binary_time_us, 3),
            "linear_search_complexity": "O(n)",
            "binary_search_complexity": "O(log n)"
        }
    }
