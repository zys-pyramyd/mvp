import os
import uuid
import hmac
import hashlib
import requests
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import HTTPException

# Paystack API Base URL
PAYSTACK_API_URL = "https://api.paystack.co"

# Environment Variables
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY', 'sk_test_dummy_paystack_key')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY', 'pk_test_dummy_paystack_key')

# Farm Deals Fixed Split Group (Sophie Farms Investment Ltd)
FARMHUB_SPLIT_GROUP = os.environ.get('FARMHUB_SPLIT_GROUP', '')
FARMHUB_SUBACCOUNT = os.environ.get('FARMHUB_SUBACCOUNT', '')

# Paystack Models
class PaystackSubaccount(BaseModel):
    """Paystack subaccount for vendors/farmers/communities"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subaccount_code: str  # From Paystack (ACCT_xxxxxxxxxx)
    business_name: str
    account_number: str
    bank_code: str
    bank_name: str
    percentage_charge: float = 0.0  # Always 0.0 for fixed split
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PaystackTransaction(BaseModel):
    """Transaction record with split details"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reference: str  # Paystack reference
    buyer_id: str
    buyer_email: str
    product_id: Optional[str] = None
    order_id: Optional[str] = None
    product_total: int  # In kobo
    delivery_fee: int  # In kobo
    platform_cut: int  # In kobo (transaction_charge)
    total_amount: int  # In kobo (what customer pays)
    subaccount_code: str  # Recipient subaccount
    vendor_share: int  # In kobo
    buyer_is_agent: bool = False
    agent_commission: int = 0  # In kobo (4% if agent)
    payment_status: str = "pending"  # pending, success, failed
    authorization_url: Optional[str] = None
    access_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None

class PaystackTransferRecipient(BaseModel):
    """Transfer recipient for commission payouts"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    recipient_code: str  # From Paystack
    name: str
    account_number: str
    bank_code: str
    bank_name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommissionPayout(BaseModel):
    """Agent/Buyer commission payout tracker"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str
    recipient_id: str
    recipient_user_id: str
    amount: int  # In kobo
    transfer_code: Optional[str] = None  # From Paystack transfer
    status: str = "pending"  # pending, processing, success, failed
    reason: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None

# Paystack Helper Functions
def paystack_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make authenticated request to Paystack API"""
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{PAYSTACK_API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Paystack API error: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Paystack API error: {str(e)}")

def verify_paystack_signature(payload: bytes, signature: str) -> bool:
    """Verify Paystack webhook signature"""
    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)

def naira_to_kobo(amount: float) -> int:
    """Convert Naira to Kobo (sub-unit)"""
    return int(amount * 100)

def kobo_to_naira(amount: int) -> float:
    """Convert Kobo to Naira"""
    return amount / 100
