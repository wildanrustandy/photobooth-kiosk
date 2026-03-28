from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    booth_id = Column(
        UUID(as_uuid=True), ForeignKey("booths.id", ondelete="CASCADE"), nullable=False
    )
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending")  # pending, success, failed, expired
    provider = Column(String(50), default="qris")
    reference_id = Column(String(100), nullable=True)  # Our own reference ID
    qr_string = Column(Text, nullable=True)
    transaction_id = Column(String(255), nullable=True)  # iPaymu Transaction ID
    paid_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="payment")

    def __repr__(self):
        return f"<Payment {self.id} - {self.status}>"
