
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.common import UserRole, BusinessCategory, BusinessRegistrationStatus, KYCStatus

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    username: str
    email: str
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_verified: bool = False
    wallet_balance: float = 0.0
    profile_picture: Optional[str] = None  # Base64 encoded image or URL
    # Financial Information
    bvn: Optional[str] = None
    dva_account_number: Optional[str] = None
    dva_bank_name: Optional[str] = None
    # Business-related fields
    business_category: Optional[BusinessCategory] = None
    business_registration_status: Optional[BusinessRegistrationStatus] = None
    business_name: Optional[str] = None
    business_description: Optional[str] = None
    other_business_category: Optional[str] = None  # If business_category is "others"
    # KYC information
    kyc_status: KYCStatus = KYCStatus.NOT_STARTED
    kyc_submitted_at: Optional[datetime] = None
    kyc_approved_at: Optional[datetime] = None
    # Rating information
    average_rating: float = 5.0  # Overall rating as seller/service provider
    total_ratings: int = 0  # Number of ratings received
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserRegister(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    username: str
    email: str
    password: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email_or_phone: str
    password: str

class CompleteRegistration(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    username: str
    email_or_phone: str
    password: str
    phone: Optional[str] = None
    gender: str
    date_of_birth: str
    user_path: str  # 'buyer' or 'partner'
    buyer_type: Optional[str] = None
    business_info: Optional[dict] = None
    partner_type: Optional[str] = None
    business_category: Optional[str] = None
    verification_info: Optional[dict] = None
    bvn: Optional[str] = None

class SecureAccountDetails(BaseModel):
    """Encrypted storage for sensitive financial information"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    # Bank account details (encrypted)
    bank_name: Optional[str] = None
    account_number: Optional[str] = None  # Will be encrypted
    account_name: Optional[str] = None
    # Payment card details (encrypted) - Store only if absolutely necessary
    # Note: In production, use payment gateway tokenization instead
    # Mobile money details
    mobile_money_provider: Optional[str] = None
    mobile_money_number: Optional[str] = None  # Will be encrypted
    # Metadata
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str  # KYC update, product edit, etc.
    resource_type: str  # user, product, order, etc.
    resource_id: Optional[str] = None
    details: dict  # Action details
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class CreateAdminRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    secret_key: str # Simple protection for the endpoint

class BankAccountCreate(BaseModel):
    account_name: str
    account_number: str = Field(..., pattern=r'^\d{10}$')
    bank_name: str
    bank_code: str = Field(..., pattern=r'^\d{3}$')
    is_primary: bool = False
