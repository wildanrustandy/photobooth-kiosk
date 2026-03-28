import requests
import json
from datetime import datetime
import hashlib
import hmac
from fastapi import FastAPI, HTTPException
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
        "notifyUrl": "http://localhost:8000/api/payment/notify",
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
