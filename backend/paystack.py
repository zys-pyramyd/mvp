import os
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Paystack API Base URL
PAYSTACK_API_URL = "https://api.paystack.co"

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
