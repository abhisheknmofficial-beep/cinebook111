from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class PaymentStatus:
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class PaymentMethod:
    UPI = "UPI"
    CARD = "CARD"
    NETBANKING = "NETBANKING"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, unique=True)
    payment_reference = Column(String(60), unique=True, index=True, nullable=False)
    payment_method = Column(String(30), default=PaymentMethod.UPI)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default=PaymentStatus.PENDING, index=True)
    transaction_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    booking = relationship("Booking", back_populates="payment")

    def __repr__(self):
        return f"<Payment {self.payment_reference} ({self.status}) ₹{self.amount}>"
