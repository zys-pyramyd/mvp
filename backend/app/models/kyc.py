
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.common import DocumentType, BusinessType, IdentificationType

class KYCDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    document_type: DocumentType
    file_name: str
    file_data: str  # base64 encoded file
    file_size: int
    mime_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False
    verification_notes: Optional[str] = None

class RegisteredBusinessKYC(BaseModel):
    business_registration_number: str
    tax_identification_number: str
    business_type: BusinessType
    business_address: str
    contact_person_name: str
    contact_person_phone: str
    contact_person_email: str
    # Documents will be uploaded separately
    certificate_of_incorporation_id: Optional[str] = None
    tin_certificate_id: Optional[str] = None
    utility_bill_id: Optional[str] = None

class UnregisteredEntityKYC(BaseModel):
    identification_type: IdentificationType  # NIN or BVN
    identification_number: str
    headshot_photo_id: Optional[str] = None  # Camera captured photo
    national_id_document_id: Optional[str] = None
    utility_bill_id: Optional[str] = None

class AgentKYC(BaseModel):
    """KYC requirements specific to agents"""
    # Business Information
    agent_business_name: str
    business_registration_number: Optional[str] = None  # Optional for unregistered agents
    tax_identification_number: Optional[str] = None
    business_address: str
    business_type: str = "Agricultural Agent/Aggregator"
    
    # Personal Information
    full_name: str
    phone_number: str
    email_address: str
    identification_type: IdentificationType  # NIN or BVN
    identification_number: str
    
    # Agent-specific requirements
    agricultural_experience_years: Optional[int] = None
    target_locations: List[str] = []  # Areas they plan to operate
    expected_farmer_network_size: Optional[int] = None
    
    # Document IDs (uploaded separately)
    headshot_photo_id: Optional[str] = None
    national_id_document_id: Optional[str] = None
    utility_bill_id: Optional[str] = None
    certificate_of_incorporation_id: Optional[str] = None  # If registered business
    tin_certificate_id: Optional[str] = None  # If registered business
    bank_statement_id: Optional[str] = None  # For financial verification

class FarmerKYC(BaseModel):
    """KYC requirements for farmers (self-registering or agent-registered)"""
    # Personal Information
    full_name: str
    phone_number: str
    identification_type: IdentificationType  # NIN or BVN
    identification_number: str
    
    # Farm Information
    farm_location: str
    farm_size_hectares: float
    primary_crops: List[str]
    farming_experience_years: Optional[int] = None
    farm_ownership_type: str  # "owned", "leased", "family_land"
    
    # Verification Method
    verification_method: str  # "agent_verified" or "self_verified"
    verifying_agent_id: Optional[str] = None  # If verified by agent
    
    # Document IDs (uploaded separately)  
    headshot_photo_id: Optional[str] = None
    national_id_document_id: Optional[str] = None
    farm_photo_id: Optional[str] = None  # Photo of the farm
    land_ownership_document_id: Optional[str] = None  # Land certificate/lease agreement
