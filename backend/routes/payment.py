import requests
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from database import get_db
from config import settings
from models.session import Session
from models.payment import Payment
from models.booth import Booth
from sqlalchemy import select

router = APIRouter(prefix="/api/payment", tags=["Payment"])
security = HTTPBearer()


class PaymentRequest(BaseModel):
    amount: str
    product_name: str
    qty: str = "1"
    booth_id: str = None
    print_count: int = 1


@router.post("/create")
async def create_payment(
    request: PaymentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Create a payment request via iPaymu and save to database."""
    from utils.security import verify_device_token

    payload = verify_device_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid device token")

    device_id = payload.get("device_id")
    booth_id = payload.get("booth_id") or request.booth_id

    if not booth_id:
        raise HTTPException(status_code=400, detail="Booth ID is required")

    # Verify booth exists
    booth_result = await db.execute(select(Booth).where(Booth.id == booth_id))
    booth = booth_result.scalar_one_or_none()
    if not booth:
        raise HTTPException(status_code=404, detail="Booth not found")

    # Create session record
    session = Session(
        booth_id=booth_id,
        device_id=device_id,
        status="pending",
        print_count=request.print_count,
        total_price=float(request.amount),
    )
    db.add(session)
    await db.flush()  # Get session ID without committing

    # Create payment request to iPaymu
    reference_id = "PB" + datetime.today().strftime("%Y%m%d%H%M%S")
    body = {
        "name": "Kiosk User",
        "phone": "08123456789",
        "email": "user@kiosk.com",
        "amount": request.amount,
        "notifyUrl": settings.ipaymu_notify_url,
        "comments": f"Photobooth Payment - {request.product_name}",
        "referenceId": reference_id,
        "paymentMethod": "qris",
        "paymentChannel": "qris",
    }

    data_body = json.dumps(body, separators=(",", ":"))
    encrypt_body = hashlib.sha256(data_body.encode()).hexdigest()
    stringtosign = f"POST:{settings.ipaymu_va}:{encrypt_body}:{settings.ipaymu_key}"
    signature = (
        hmac.new(settings.ipaymu_key.encode(), stringtosign.encode(), hashlib.sha256)
        .hexdigest()
        .lower()
    )
    timestamp = datetime.today().strftime("%Y%m%d%H%M%S")

    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "signature": signature,
        "va": settings.ipaymu_va,
        "timestamp": timestamp,
    }

    url = f"{settings.ipaymu_url}/api/v2/payment/direct"
    resp = requests.post(url, headers=headers, data=data_body)
    data = resp.json()

    if data.get("Status") == 200:
        payment_data = data.get("Data", {})

        # Create payment record
        payment = Payment(
            session_id=session.id,
            booth_id=booth_id,
            amount=float(request.amount),
            status="pending",
            provider="qris",
            reference_id=reference_id,  # Our own reference
            qr_string=payment_data.get("QrString"),
            transaction_id=str(
                payment_data.get("TransactionId")
            ),  # iPaymu Transaction ID
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )
        db.add(payment)
        await db.commit()

        # Broadcast transaction creation to admin clients
        from routes.websocket import broadcast_transaction_update

        booth_result = await db.execute(select(Booth).where(Booth.id == booth_id))
        booth = booth_result.scalar_one_or_none()
        booth_name = booth.name if booth else "Unknown"

        await broadcast_transaction_update(
            {
                "id": str(payment.id),
                "session_id": str(session.id),
                "reference_id": reference_id,
                "transaction_id": str(payment_data.get("TransactionId")),
                "booth_id": str(booth_id),
                "booth_name": booth_name,
                "amount": float(request.amount),
                "status": "pending",
                "provider": payment.provider,
                "created_at": payment.created_at.isoformat()
                if payment.created_at
                else None,
                "paid_at": None,
            }
        )

        return {
            "QrString": payment_data.get("QrString"),
            "TransactionId": str(
                payment_data.get("TransactionId")
            ),  # Convert to string
            "ReferenceId": reference_id,
            "SessionId": str(session.id),
        }

    await db.rollback()
    raise HTTPException(status_code=400, detail=data)


@router.get("/status/{transaction_id}")
async def check_status(
    transaction_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Check payment status via iPaymu."""
    body = {"transactionId": transaction_id}
    data_body = json.dumps(body, separators=(",", ":"))
    encrypt_body = hashlib.sha256(data_body.encode()).hexdigest()
    stringtosign = f"POST:{settings.ipaymu_va}:{encrypt_body}:{settings.ipaymu_key}"
    signature = (
        hmac.new(settings.ipaymu_key.encode(), stringtosign.encode(), hashlib.sha256)
        .hexdigest()
        .lower()
    )
    timestamp = datetime.today().strftime("%Y%m%d%H%M%S")

    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "signature": signature,
        "va": settings.ipaymu_va,
        "timestamp": timestamp,
    }

    url = f"{settings.ipaymu_url}/api/v2/transaction"
    resp = requests.post(url, headers=headers, data=data_body)
    data = resp.json()

    if data.get("Status") == 200:
        return data.get("Data")

    raise HTTPException(status_code=400, detail=data)


@router.get("/notify")
async def test_payment_notify_get(
    trx_id: str = "TEST_TRX_123",
    status: str = "berhasil",
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint GET khusus untuk testing lokal via browser.
    Contoh: http://localhost:8000/api/payment/notify?trx_id=201383&status=berhasil
    """
    from routes.websocket import broadcast_transaction_update

    # Update payment status in database
    if trx_id and trx_id != "TEST_TRX_123":
        payment_result = await db.execute(
            select(Payment).where(Payment.transaction_id == trx_id)
        )
        payment = payment_result.scalar_one_or_none()

        if payment:
            if status == "berhasil" or status == "1":
                payment.status = "success"
                payment.paid_at = datetime.utcnow()

                # Update session status
                session_result = await db.execute(
                    select(Session).where(Session.id == payment.session_id)
                )
                session = session_result.scalar_one_or_none()
                if session:
                    session.status = "paid"

                await db.commit()

                # Get booth name for broadcast
                booth_result = await db.execute(
                    select(Booth).where(Booth.id == payment.booth_id)
                )
                booth = booth_result.scalar_one_or_none()
                booth_name = booth.name if booth else "Unknown"

                # Broadcast transaction update to admin clients
                await broadcast_transaction_update(
                    {
                        "id": str(payment.id),
                        "session_id": str(payment.session_id),
                        "reference_id": payment.reference_id,
                        "transaction_id": payment.transaction_id,
                        "booth_id": str(payment.booth_id),
                        "booth_name": booth_name,
                        "amount": float(payment.amount),
                        "status": "success",
                        "provider": payment.provider,
                        "created_at": payment.created_at.isoformat()
                        if payment.created_at
                        else None,
                        "paid_at": payment.paid_at.isoformat()
                        if payment.paid_at
                        else None,
                    }
                )

                return {
                    "message": "Payment updated successfully",
                    "trx_id": trx_id,
                    "status": "success",
                    "broadcast_sent": True,
                }

            elif status == "expired" or status == "-2" or status == "2":
                payment.status = "failed"
                await db.commit()

                # Get booth name for broadcast
                booth_result = await db.execute(
                    select(Booth).where(Booth.id == payment.booth_id)
                )
                booth = booth_result.scalar_one_or_none()
                booth_name = booth.name if booth else "Unknown"

                # Broadcast transaction update to admin clients
                await broadcast_transaction_update(
                    {
                        "id": str(payment.id),
                        "session_id": str(payment.session_id),
                        "reference_id": payment.reference_id,
                        "transaction_id": payment.transaction_id,
                        "booth_id": str(payment.booth_id),
                        "booth_name": booth_name,
                        "amount": float(payment.amount),
                        "status": "failed",
                        "provider": payment.provider,
                        "created_at": payment.created_at.isoformat()
                        if payment.created_at
                        else None,
                    }
                )

                return {
                    "message": "Payment updated to failed",
                    "trx_id": trx_id,
                    "status": "failed",
                    "broadcast_sent": True,
                }

    return {
        "message": "Local test endpoint. Use: /api/payment/notify?trx_id=<transaction_id>&status=berhasil",
        "simulated_data": {"trx_id": trx_id, "status": status},
    }


@router.post("/notify")
async def payment_notify(request: Request, db: AsyncSession = Depends(get_db)):
    """Webhook for payment notification from iPaymu."""
    from routes.websocket import broadcast_transaction_update

    raw_body = await request.body()
    body_str = raw_body.decode("utf-8")

    data = {}

    if body_str:
        if body_str.strip().startswith("{"):
            try:
                data = json.loads(body_str)
            except Exception:
                pass
        else:
            import urllib.parse

            parsed = urllib.parse.parse_qs(body_str)
            data = {k: v[0] for k, v in parsed.items()}

    status = data.get("status", "UNKNOWN")
    trx_id = data.get("trx_id", data.get("transaction_id", "UNKNOWN"))

    # Update payment status in database
    if trx_id and trx_id != "UNKNOWN":
        payment_result = await db.execute(
            select(Payment).where(Payment.transaction_id == trx_id)
        )
        payment = payment_result.scalar_one_or_none()

        if payment:
            if status == "berhasil" or status == "1":
                payment.status = "success"
                payment.paid_at = datetime.utcnow()

                # Update session status
                session_result = await db.execute(
                    select(Session).where(Session.id == payment.session_id)
                )
                session = session_result.scalar_one_or_none()
                if session:
                    session.status = "paid"

                await db.commit()

                # Get booth name for broadcast
                booth_result = await db.execute(
                    select(Booth).where(Booth.id == payment.booth_id)
                )
                booth = booth_result.scalar_one_or_none()
                booth_name = booth.name if booth else "Unknown"

                # Broadcast transaction update to admin clients
                await broadcast_transaction_update(
                    {
                        "id": str(payment.id),
                        "session_id": str(payment.session_id),
                        "reference_id": payment.reference_id,
                        "transaction_id": payment.transaction_id,
                        "booth_id": str(payment.booth_id),
                        "booth_name": booth_name,
                        "amount": float(payment.amount),
                        "status": "success",
                        "provider": payment.provider,
                        "created_at": payment.created_at.isoformat()
                        if payment.created_at
                        else None,
                        "paid_at": payment.paid_at.isoformat()
                        if payment.paid_at
                        else None,
                    }
                )

            elif status == "expired" or status == "-2" or status == "2":
                payment.status = "failed"
                await db.commit()

                # Get booth name for broadcast
                booth_result = await db.execute(
                    select(Booth).where(Booth.id == payment.booth_id)
                )
                booth = booth_result.scalar_one_or_none()
                booth_name = booth.name if booth else "Unknown"

                # Broadcast transaction update to admin clients
                await broadcast_transaction_update(
                    {
                        "id": str(payment.id),
                        "session_id": str(payment.session_id),
                        "reference_id": payment.reference_id,
                        "transaction_id": payment.transaction_id,
                        "booth_id": str(payment.booth_id),
                        "booth_name": booth_name,
                        "amount": float(payment.amount),
                        "status": "failed",
                        "provider": payment.provider,
                        "created_at": payment.created_at.isoformat()
                        if payment.created_at
                        else None,
                    }
                )

    return {"status": "success", "trx_id": trx_id, "received_data": data}


@router.post("/demo/create")
async def create_demo_payment(
    request: PaymentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Create a demo payment for testing (auto-success)."""
    from utils.security import verify_device_token
    import uuid

    payload = verify_device_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid device token")

    device_id = payload.get("device_id")
    booth_id = payload.get("booth_id") or request.booth_id

    if not booth_id:
        raise HTTPException(status_code=400, detail="Booth ID is required")

    # Verify booth exists
    booth_result = await db.execute(select(Booth).where(Booth.id == booth_id))
    booth = booth_result.scalar_one_or_none()
    if not booth:
        raise HTTPException(status_code=404, detail="Booth not found")

    # Create session record
    session = Session(
        booth_id=booth_id,
        device_id=device_id,
        status="paid",
        print_count=request.print_count,
        total_price=float(request.amount),
    )
    db.add(session)
    await db.flush()

    # Generate reference ID
    reference_id = "PB" + datetime.today().strftime("%Y%m%d%H%M%S")

    # Create payment record with success status
    demo_transaction_id = f"DEMO-{uuid.uuid4().hex[:12].upper()}"
    payment = Payment(
        session_id=session.id,
        booth_id=booth_id,
        amount=float(request.amount),
        status="success",
        provider="demo",
        reference_id=reference_id,
        qr_string="demo-qr-string",
        transaction_id=demo_transaction_id,
        paid_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=15),
    )
    db.add(payment)
    await db.commit()

    # Broadcast transaction update to admin clients
    from routes.websocket import broadcast_transaction_update

    await broadcast_transaction_update(
        {
            "id": str(payment.id),
            "session_id": str(payment.session_id),
            "reference_id": payment.reference_id,
            "transaction_id": payment.transaction_id,
            "booth_id": str(payment.booth_id),
            "booth_name": booth.name if booth else "Unknown",
            "amount": float(payment.amount),
            "status": "success",
            "provider": payment.provider,
            "created_at": payment.created_at.isoformat()
            if payment.created_at
            else None,
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        }
    )

    return {
        "QrString": "demo-qr-string",
        "TransactionId": demo_transaction_id,
        "ReferenceId": reference_id,
        "SessionId": str(session.id),
        "Status": "success",
    }
