
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.common import DriverStatus, VehicleType, DriverSubscriptionStatus

class Driver(BaseModel):
    id: Optional[str] = None
    driver_username: str
    driver_name: str
    phone_number: str
    email: Optional[str] = None
    profile_picture: Optional[str] = None  # base64 image
    driver_license: Optional[str] = None
    status: DriverStatus = DriverStatus.OFFLINE
    current_location: Optional[dict] = None  # {"lat": float, "lng": float, "address": str}
    rating: float = 5.0
    total_deliveries: int = 0
    is_independent: bool = True  # True for self-registered, False for logistics business managed
    logistics_business_id: Optional[str] = None  # If managed by logistics business
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Vehicle(BaseModel):
    id: Optional[str] = None
    driver_id: str
    vehicle_type: VehicleType
    plate_number: str
    make_model: str  # e.g., "Honda CBR 150", "Toyota Camry"
    color: str
    year: Optional[int] = None
    insurance_info: Optional[str] = None
    created_at: Optional[datetime] = None

class LogisticsBusiness(BaseModel):
    id: Optional[str] = None
    business_username: str
    business_name: str
    business_address: str
    phone_number: str
    email: str
    cac_number: Optional[str] = None
    drivers: List[str] = []  # List of driver IDs
    vehicles: List[str] = []  # List of vehicle IDs
    created_at: Optional[datetime] = None

class DriverSearchResult(BaseModel):
    driver_id: str
    driver_name: str
    driver_username: str
    rating: float
    total_deliveries: int
    current_location: Optional[dict] = None
    vehicle_info: dict
    status: DriverStatus
    distance_km: Optional[float] = None  # Distance from pickup location

class DriverCreate(BaseModel):
    driver_name: str
    phone_number: str
    email: Optional[str] = None
    profile_picture: Optional[str] = None
    driver_license: Optional[str] = None
    vehicle_type: VehicleType
    plate_number: str
    make_model: str
    color: str
    year: Optional[int] = None

class LogisticsDriverSlot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    logistics_business_id: str
    logistics_username: str
    slot_number: int
    driver_id: Optional[str] = None  # Assigned driver ID
    driver_username: Optional[str] = None
    driver_name: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    plate_number: Optional[str] = None
    vehicle_make_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    vehicle_year: Optional[int] = None
    vehicle_photo: Optional[str] = None  # base64 vehicle image
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    driver_license: Optional[str] = None
    registration_link: Optional[str] = None  # Unique registration link for driver
    subscription_status: DriverSubscriptionStatus = DriverSubscriptionStatus.TRIAL
    trial_start_date: datetime = Field(default_factory=datetime.utcnow)
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    monthly_fee: float = 500.0  # ₦500 per driver per month
    is_active: bool = True
    total_trips: int = 0
    average_rating: float = 5.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class DriverSlotCreate(BaseModel):
    driver_name: str
    vehicle_type: VehicleType
    plate_number: str
    vehicle_make_model: str
    vehicle_color: str
    vehicle_year: Optional[int] = None
    vehicle_photo: Optional[str] = None
    date_of_birth: str  # Format: YYYY-MM-DD
    address: str
    driver_license: Optional[str] = None

class DriverSlotUpdate(BaseModel):
    driver_name: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    plate_number: Optional[str] = None
    vehicle_make_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    vehicle_year: Optional[int] = None
    vehicle_photo: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    driver_license: Optional[str] = None
    is_active: Optional[bool] = None

class DriverRegistrationComplete(BaseModel):
    username: str
    password: str
    registration_token: str

class EnhancedDriverProfile(BaseModel):
    id: str
    driver_username: str
    driver_name: str
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None
    vehicle_info: dict  # Complete vehicle information
    current_location: Optional[dict] = None
    status: DriverStatus = DriverStatus.OFFLINE
    average_rating: float = 5.0
    total_trips: int = 0
    total_earnings: float = 0.0
    is_independent: bool = False  # False for logistics business managed drivers
    logistics_business_name: Optional[str] = None
    created_at: datetime
    last_active: Optional[datetime] = None
