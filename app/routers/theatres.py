from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.theatre import Theatre, Screen, Seat
from app.schemas.theatre import TheatreCreate, TheatreResponse, ScreenCreate, ScreenResponse
from app.auth.dependencies import get_current_admin

router = APIRouter(prefix="/api/theatres", tags=["Theatres"])

@router.get("", response_model=List[TheatreResponse])
def get_theatres(
    city: Optional[str] = Query(None, description="Filter theatres by city"),
    db: Session = Depends(get_db)
):
    """Retrieves all registered theatres."""
    query = db.query(Theatre)
    if city:
        query = query.filter(Theatre.city.ilike(f"%{city}%"))
    return query.all()

@router.get("/{theatre_id}", response_model=TheatreResponse)
def get_theatre_detail(theatre_id: int, db: Session = Depends(get_db)):
    """Retrieves theatre details with its screens."""
    theatre = db.query(Theatre).filter(Theatre.id == theatre_id).first()
    if not theatre:
        raise HTTPException(status_code=404, detail="Theatre not found.")
    return theatre

@router.post("", response_model=TheatreResponse, status_code=status.HTTP_201_CREATED)
def create_theatre(
    payload: TheatreCreate,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to create a new theatre with an initial default screen and seats."""
    theatre = Theatre(
        name=payload.name.strip(),
        city=payload.city.strip(),
        address=payload.address.strip()
    )
    db.add(theatre)
    db.flush()

    # Automatically create default Screen 1 with seats grid
    screen = Screen(theatre_id=theatre.id, name="Screen 1 (4K Dolby)", total_rows=5, total_cols=8)
    db.add(screen)
    db.flush()

    # Generate seats: Rows A-E, Cols 1-8
    row_labels = ["A", "B", "C", "D", "E"]
    for r_idx, r_label in enumerate(row_labels):
        s_type = "VIP" if r_label == "A" else ("PREMIUM" if r_label in ["B", "C"] else "REGULAR")
        for c in range(1, 9):
            seat = Seat(
                screen_id=screen.id,
                row_label=r_label,
                seat_number=c,
                seat_code=f"{r_label}{c}",
                seat_type=s_type
            )
            db.add(seat)

    db.commit()
    db.refresh(theatre)
    return theatre

@router.delete("/{theatre_id}", status_code=status.HTTP_200_OK)
def delete_theatre(
    theatre_id: int,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to delete a theatre."""
    theatre = db.query(Theatre).filter(Theatre.id == theatre_id).first()
    if not theatre:
        raise HTTPException(status_code=404, detail="Theatre not found.")
    db.delete(theatre)
    db.commit()
    return {"message": f"Theatre '{theatre.name}' deleted successfully."}
