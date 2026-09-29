from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class PaymentProcessRequest(BaseModel):
    booking_id: int
    payment_method: str = Field("UPI", description="UPI, CARD, or NETBANKING")
    simulate_failure: bool = False

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    payment_reference: str
    payment_method: str
    amount: float
    status: str
    transaction_time: datetime

    model_config = ConfigDict(from_attributes=True)
