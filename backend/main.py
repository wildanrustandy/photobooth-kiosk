import requests
import json
import urllib.parse
from datetime import datetime
import hashlib
import hmac
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ipaymuVa = "0000005155258811"  # using the VA from ipaymu.py (direct payment example)
ipaymuKey = "SANDBOX4DDE84C3-7D3A-4572-8178-33DF5B494131"
ipaymuUrl = "https://sandbox.ipaymu.com"


class PaymentRequest(BaseModel):
    amount: str
    product_name: str
    qty: str


@app.post("/api/payment/create")
def create_payment(req: PaymentRequest):
    body = {
        "name": "Kiosk User",
        "phone": "08123456789",
        "email": "user@kiosk.com",
        "amount": req.amount,
        # "notifyUrl": "http://localhost:8000/api/payment/notify",
        "notifyUrl": "https://fd85-2404-8000-100c-385-99a8-78ad-1c67-f998.ngrok-free.app/api/payment/notify",
        "comments": "Photobooth Payment",
        "referenceId": "PB" + datetime.today().strftime("%Y%m%d%H%M%S"),
        "paymentMethod": "qris",
        "paymentChannel": "qris",
    }

    data_body = json.dumps(body, separators=(",", ":"))
    encrypt_body = hashlib.sha256(data_body.encode()).hexdigest()
    stringtosign = f"POST:{ipaymuVa}:{encrypt_body}:{ipaymuKey}"
    signature = (
        hmac.new(ipaymuKey.encode(), stringtosign.encode(), hashlib.sha256)
        .hexdigest()
        .lower()
    )
    timestamp = datetime.today().strftime("%Y%m%d%H%M%S")

    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "signature": signature,
        "va": ipaymuVa,
        "timestamp": timestamp,
    }

    url = f"{ipaymuUrl}/api/v2/payment/direct"
    resp = requests.post(url, headers=headers, data=data_body)
    data = resp.json()

    if data.get("Status") == 200:
        return data.get("Data")
    raise HTTPException(status_code=400, detail=data)


@app.get("/api/payment/status/{transaction_id}")
def check_status(transaction_id: str):
    body = {"transactionId": transaction_id}
    data_body = json.dumps(body, separators=(",", ":"))
    encrypt_body = hashlib.sha256(data_body.encode()).hexdigest()
    stringtosign = f"POST:{ipaymuVa}:{encrypt_body}:{ipaymuKey}"
    signature = (
        hmac.new(ipaymuKey.encode(), stringtosign.encode(), hashlib.sha256)
        .hexdigest()
        .lower()
    )
    timestamp = datetime.today().strftime("%Y%m%d%H%M%S")

    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "signature": signature,
        "va": ipaymuVa,
        "timestamp": timestamp,
    }

    url = f"{ipaymuUrl}/api/v2/transaction"
    resp = requests.post(url, headers=headers, data=data_body)
    data = resp.json()

    if data.get("Status") == 200:
        return data.get("Data")
    raise HTTPException(status_code=400, detail=data)


@app.get("/api/payment/notify")
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


@app.post("/api/payment/notify")
async def payment_notify(request: Request):
    # Baca raw body
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
