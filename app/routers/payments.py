from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.payment import PaymentProcessRequest, PaymentResponse
from app.auth.dependencies import get_current_user
from app.services.booking_service import process_payment

router = APIRouter(prefix="/api/payments", tags=["Payments"])

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def execute_payment_simulation(
    payload: PaymentProcessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simulates a payment transaction.
    - Statuses: PENDING, SUCCESS, FAILED
    - Supported methods: UPI, CARD, NETBANKING
    - Updates booking status to CONFIRMED on SUCCESS.
    - Releases seats on simulated failure.
    """
    booking, payment = process_payment(
        db=db,
        booking_id=payload.booking_id,
        payment_method=payload.payment_method,
        simulate_failure=payload.simulate_failure
    )
    return payment
