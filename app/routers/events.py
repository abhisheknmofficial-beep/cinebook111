from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.auth.dependencies import get_current_admin
from app.services.search_service import search_and_filter_events

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("", response_model=List[EventResponse])
def get_events(
    q: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Event category"),
    location: Optional[str] = Query(None, description="Location"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    sort_by: str = Query("price_asc", description="Sort option"),
    db: Session = Depends(get_db)
):
    """Retrieves live events/concerts with DSA search and sorting."""
    return search_and_filter_events(
        db=db,
        query=q,
        category=category,
        location=location,
        max_price=max_price,
        sort_by=sort_by
    )

@router.get("/{event_id}", response_model=EventResponse)
def get_event_detail(event_id: int, db: Session = Depends(get_db)):
    """Retrieves event details by ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return event

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to create a new event."""
    data = payload.model_dump()
    if not data.get("available_seats"):
        data["available_seats"] = data.get("total_seats", 100)
    event = Event(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to update event details."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(event, field, val)

    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    admin: Any = Depends(get_current_admin)
):
    """Admin endpoint to delete an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    db.delete(event)
    db.commit()
    return {"message": f"Event '{event.title}' deleted successfully."}
