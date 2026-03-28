import requests
import json
import hashlib
import hmac
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from database import get_db
from config import settings

router = APIRouter(prefix="/api/payment", tags=["Payment"])
security = HTTPBearer()


class PaymentRequest(BaseModel):
    amount: str
    product_name: str
    qty: str = "1"
    booth_id: str = None


@router.post("/create")
async def create_payment(
    request: PaymentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Create a payment request via iPaymu."""
    # Get booth info from device token
    from utils.security import verify_device_token

    payload = verify_device_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid device token")

    booth_id = payload.get("booth_id") or request.booth_id
    if not booth_id:
        raise HTTPException(status_code=400, detail="Booth ID is required")

    # Create payment request to iPaymu
    body = {
        "name": "Kiosk User",
        "phone": "08123456789",
        "email": "user@kiosk.com",
        "amount": request.amount,
        "notifyUrl": settings.ipaymu_notify_url,
        "comments": f"Photobooth Payment - {request.product_name}",
        "referenceId": "PB" + datetime.today().strftime("%Y%m%d%H%M%S"),
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
        return data.get("Data")

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

    if status == "berhasil":
        # TODO: Update database status transaksi menjadi PAID
        pass
    elif status == "expired" or status == "-2":
        # TODO: Update database status transaksi menjadi EXPIRED/FAILED
        pass

    return {"status": "success", "trx_id": trx_id, "received_data": data}
