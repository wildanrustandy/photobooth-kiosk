from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List, Optional
from models.payment import Payment
from models.session import Session


class TransactionService:
    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        booth_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[dict]:
        """Get all transactions with optional filters."""
        # Build query with joins
        query = (
            select(Payment)
            .options(selectinload(Payment.session).selectinload(Session.booth))
            .order_by(Payment.created_at.desc())
        )

        # Apply filters
        filters = []

        if booth_id:
            filters.append(Payment.booth_id == booth_id)

        if status:
            filters.append(Payment.status == status)

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                filters.append(Payment.created_at >= start_dt)
            except ValueError:
                pass

        if end_date:
            try:
                # Add 1 day to include the end date fully
                end_dt = datetime.fromisoformat(end_date) + timedelta(days=1)
                filters.append(Payment.created_at < end_dt)
            except ValueError:
                pass

        if filters:
            query = query.where(and_(*filters))

        result = await db.execute(query)
        payments = result.scalars().all()

        # Format response
        transactions = []
        for payment in payments:
            session = payment.session
            booth = session.booth if session else None

            transactions.append(
                {
                    "id": str(payment.id),
                    "session_id": str(payment.session_id),
                    "reference_id": payment.reference_id,
                    "transaction_id": payment.transaction_id,
                    "booth_id": str(payment.booth_id),
                    "booth_name": booth.name if booth else "Unknown",
                    "amount": float(payment.amount),
                    "print_count": session.print_count if session else 1,
                    "status": payment.status,
                    "payment_method": payment.provider or "qris",
                    "created_at": payment.created_at,
                    "updated_at": payment.paid_at,
                }
            )

        return transactions

    @staticmethod
    async def get_transaction_by_id(
        db: AsyncSession, transaction_id: str
    ) -> Optional[dict]:
        """Get a single transaction by ID."""
        query = (
            select(Payment)
            .options(selectinload(Payment.session).selectinload(Session.booth))
            .where(Payment.id == transaction_id)
        )

        result = await db.execute(query)
        payment = result.scalar_one_or_none()

        if not payment:
            return None

        session = payment.session
        booth = session.booth if session else None

        return {
            "id": str(payment.id),
            "session_id": str(payment.session_id),
            "reference_id": payment.reference_id,
            "transaction_id": payment.transaction_id,
            "booth_id": str(payment.booth_id),
            "booth_name": booth.name if booth else "Unknown",
            "amount": float(payment.amount),
            "print_count": session.print_count if session else 1,
            "status": payment.status,
            "payment_method": payment.provider or "qris",
            "created_at": payment.created_at,
            "updated_at": payment.paid_at,
        }
