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
            qr_string=payment_data.get("QrString"),
            transaction_id=payment_data.get("TransactionId"),
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )
        db.add(payment)
        await db.commit()

        return {
            "QrString": payment_data.get("QrString"),
            "TransactionId": payment_data.get("TransactionId"),
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
    trx_id: str = "TEST_TRX_123", status: str = "berhasil"
):
    """
    Endpoint GET khusus untuk testing lokal via browser.
    Contoh: http://localhost:8000/api/payment/notify?trx_id=12345&status=berhasil
    """
    return {
        "message": "Local test successful. Webhook endpoint is active.",
        "simulated_data": {"trx_id": trx_id, "status": status},
    }


@router.post("/notify")
async def payment_notify(request: Request, db: AsyncSession = Depends(get_db)):
    """Webhook for payment notification from iPaymu."""
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
            elif status == "expired" or status == "-2" or status == "2":
                payment.status = "failed"
                await db.commit()

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

    # Create payment record with success status
    demo_transaction_id = f"DEMO-{uuid.uuid4().hex[:12].upper()}"
    payment = Payment(
        session_id=session.id,
        booth_id=booth_id,
        amount=float(request.amount),
        status="success",
        provider="demo",
        qr_string="demo-qr-string",
        transaction_id=demo_transaction_id,
        paid_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=15),
    )
    db.add(payment)
    await db.commit()

    return {
        "QrString": "demo-qr-string",
        "TransactionId": demo_transaction_id,
        "ReferenceId": f"DEMO-{datetime.today().strftime('%Y%m%d%H%M%S')}",
        "SessionId": str(session.id),
        "Status": "success",
    }
