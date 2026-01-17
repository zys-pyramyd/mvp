
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
from app.models.common import TransactionType, TransactionStatus, FundingMethod, GiftCardStatus

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

class WalletTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username: str
    transaction_type: TransactionType
    amount: float
    balance_before: float
    balance_after: float
    status: TransactionStatus = TransactionStatus.PENDING
    reference: str = Field(default_factory=lambda: f"TXN-{uuid.uuid4().hex[:12].upper()}")
    description: str
    funding_method: Optional[FundingMethod] = None
    order_id: Optional[str] = None  # If related to an order
    gift_card_id: Optional[str] = None  # If related to gift card
    metadata: Optional[dict] = None  # Additional transaction data
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class WalletTransactionCreate(BaseModel):
    transaction_type: TransactionType
    amount: float = Field(..., gt=0)
    description: str
    funding_method: Optional[FundingMethod] = None
    order_id: Optional[str] = None
    metadata: Optional[dict] = None

class MockBankAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    account_name: str
    account_number: str = Field(..., pattern=r'^\d{10}$')  # 10-digit account number
    bank_name: str
    bank_code: str = Field(..., pattern=r'^\d{3}$')  # 3-digit bank code
    is_primary: bool = False
    is_verified: bool = False  # Mock verification status
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BankAccountCreate(BaseModel):
    account_name: str
    account_number: str = Field(..., pattern=r'^\d{10}$')
    bank_name: str
    bank_code: str = Field(..., pattern=r'^\d{3}$')
    is_primary: bool = False

class GiftCard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    card_code: str = Field(default_factory=lambda: f"GIFT-{uuid.uuid4().hex[:8].upper()}")
    amount: float
    balance: float  # Remaining balance (can be partially used)
    status: GiftCardStatus = GiftCardStatus.ACTIVE
    purchaser_id: str  # User who bought the gift card
    purchaser_username: str
    recipient_email: Optional[str] = None  # If gifted to someone
    recipient_name: Optional[str] = None
    message: Optional[str] = None  # Gift message
    expiry_date: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=365))  # 1 year validity
    created_at: datetime = Field(default_factory=datetime.utcnow)
    redeemed_at: Optional[datetime] = None
    redeemed_by_id: Optional[str] = None
    redeemed_by_username: Optional[str] = None

class GiftCardCreate(BaseModel):
    amount: float = Field(..., ge=100, le=100000)  # ₦100 to ₦100,000
    recipient_email: Optional[str] = None
    recipient_name: Optional[str] = None
    message: Optional[str] = None

class GiftCardRedeem(BaseModel):
    card_code: str
    amount: Optional[float] = None  # Amount to redeem (for partial redemption)

class WalletSecurity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    transaction_pin: Optional[str] = None  # Hashed 4-6 digit PIN
    pin_attempts: int = 0
    pin_locked_until: Optional[datetime] = None
    two_factor_enabled: bool = False
    daily_limit: float = 50000.0  # ₦50,000 default daily limit
    monthly_limit: float = 1000000.0  # ₦1,000,000 default monthly limit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class WalletPinCreate(BaseModel):
    pin: str = Field(..., pattern=r'^\d{4,6}$')  # 4-6 digit PIN

class WalletPinVerify(BaseModel):
    pin: str = Field(..., pattern=r'^\d{4,6}$')

class UserWalletSummary(BaseModel):
    user_id: str
    username: str
    balance: float
    total_funded: float
    total_spent: float
    total_withdrawn: float
    pending_transactions: int
    last_transaction_date: Optional[datetime] = None
    security_status: dict
    linked_accounts: int
    gift_cards_purchased: int
    gift_cards_redeemed: int
