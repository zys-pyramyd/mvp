import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from pymongo import MongoClient
import bcrypt
import jwt
from enum import Enum

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-here')
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY', 'sk_test_dummy_paystack_key')
TWILIO_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'dummy_twilio_sid')
TWILIO_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', 'dummy_twilio_token')

# Commission structure for agents (updated rates)
AGENT_COMMISSION_RATES = {
    'purchase': 0.05,  # 5% commission for agent purchases
    'sale': 0.05,      # 5% commission for agent sales (updated from 4% to 5%)
    'onboarding': 0.075, # 7.5% farmer onboarding incentive (first sale only)
    'verification': 0.02  # 2% farmer verification fee
}

app = FastAPI(title="Pyramyd API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient(MONGO_URL)
db = client.pyramyd_db
users_collection = db.users
messages_collection = db.messages
dropoff_locations_collection = db.dropoff_locations
ratings_collection = db.ratings
driver_slots_collection = db.driver_slots
wallet_transactions_collection = db.wallet_transactions
bank_accounts_collection = db.bank_accounts
gift_cards_collection = db.gift_cards
wallet_security_collection = db.wallet_security

# Security
security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    FARMER = "farmer"
    AGENT = "agent"
    BUSINESS = "business"
    PERSONAL = "personal"

class BusinessCategory(str, Enum):
    FOOD_SERVICING = "food_servicing"  # hotels, restaurants, cafe
    FOOD_PROCESSOR = "food_processor" 
    FARM_INPUT = "farm_input"  # fertilizers, herbicides, seeds etc
    FINTECH = "fintech"
    AGRICULTURE = "agriculture"
    SUPPLIER = "supplier"  # wholesaler & retailer
    OTHERS = "others"  # with specification

class BusinessRegistrationStatus(str, Enum):
    REGISTERED = "registered"
    UNREGISTERED = "unregistered"

class KYCStatus(str, Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ProductCategory(str, Enum):
    FARM_INPUT = "farm_input"
    RAW_FOOD = "raw_food" 
    PACKAGED_FOOD = "packaged_food"
    FISH_MEAT = "fish_meat"
    PEPPER_VEGETABLES = "pepper_vegetables"

class FarmInputSubcategory(str, Enum):
    SEEDS = "seeds"
    SEEDLINGS = "seedlings"
    FERTILIZER = "fertilizer"
    HERBICIDES = "herbicides"
    PESTICIDES = "pesticides"
    FARMING_TOOLS = "farming_tools"

class RawFoodSubcategory(str, Enum):
    RICE = "rice"
    GRAINS = "grains"
    TUBERS = "tubers"
    FRUITS = "fruits"
    NUTS = "nuts"
    LEGUMES = "legumes"

class PackagedFoodSubcategory(str, Enum):
    PACKAGED_RICE = "packaged_rice"
    BEANS = "beans"
    PASTA = "pasta"  # spaghetti, noodles
    CANNED_FOOD = "canned_food"
    SNACKS = "snacks"
    BEVERAGES = "beverages"
    FLOUR = "flour"

class FishMeatSubcategory(str, Enum):
    FRESH_FISH = "fresh_fish"
    DRIED_FISH = "dried_fish"
    FROZEN_FISH = "frozen_fish"
    FRESH_MEAT = "fresh_meat"
    PROCESSED_MEAT = "processed_meat"
    POULTRY = "poultry"

class PepperVegetablesSubcategory(str, Enum):
    PEPPERS = "peppers"
    LEAFY_VEGETABLES = "leafy_vegetables"
    ROOT_VEGETABLES = "root_vegetables"
    ONIONS_GARLIC = "onions_garlic"
    TOMATOES = "tomatoes"
    HERBS_SPICES = "herbs_spices"

class ProcessingLevel(str, Enum):
    NOT_PROCESSED = "not_processed"  # Raw, natural state
    SEMI_PROCESSED = "semi_processed"  # Partially processed 
    PROCESSED = "processed"  # Fully processed/packaged

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(BaseModel):
    id: Optional[str] = None
    order_id: str
    buyer_username: str
    seller_username: str
    product_details: dict
    quantity: float
    unit: str
    unit_specification: Optional[str] = None  # e.g., "100kg" for bags, "5 litres" for gallons
    unit_price: float
    total_amount: float
    delivery_method: str = "dropoff"  # "platform", "offline", or "dropoff"
    delivery_status: str = "pending"  # For offline deliveries
    shipping_address: Optional[str] = None  # Traditional shipping address (optional when using dropoff)
    dropoff_location_id: Optional[str] = None  # ID of selected drop-off location
    dropoff_location_details: Optional[dict] = None  # Snapshot of drop-off location info
    agent_fee_percentage: float = 0.05  # Updated agent fee (5%)
    payment_timing: str = "after_delivery"  # "after_delivery" for offline, "during_transit" for platform
    status: OrderStatus = OrderStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class QuantityUnit(BaseModel):
    unit: str
    specification: Optional[str] = None
    
    @validator('unit')
    def validate_unit(cls, v):
        allowed_units = ['kg', 'g', 'ton', 'pieces', 'liters', 'bags', 'crates', 'gallons']
        if v not in allowed_units:
            raise ValueError(f'Unit must be one of: {", ".join(allowed_units)}')
        return v

class OrderCreate(BaseModel):
    product_id: str
    quantity: float
    unit: str
    unit_specification: Optional[str] = None
    shipping_address: Optional[str] = None  # Optional when using drop-off
    delivery_method: str = "dropoff"  # "platform", "offline", or "dropoff"
    dropoff_location_id: Optional[str] = None  # Required when delivery_method is "dropoff"
    
    @validator('dropoff_location_id')
    def validate_dropoff_location(cls, v, values):
        delivery_method = values.get('delivery_method')
        if delivery_method == 'dropoff' and not v:
            raise ValueError('Drop-off location is required when using drop-off delivery method')
        return v
    
class OrderStatusUpdate(BaseModel):
    order_id: str
    status: OrderStatus
    delivery_status: Optional[str] = None  # For offline deliveries

class DriverStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"
    ON_DELIVERY = "on_delivery"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted" 
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class VehicleType(str, Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    VAN = "van"
    TRUCK = "truck"
    BICYCLE = "bicycle"

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

class DeliveryRequest(BaseModel):
    id: Optional[str] = None
    order_id: str  # References order or pre-order
    order_type: str  # "regular" or "preorder"
    requester_username: str  # Agent, farmer, or supplier requesting delivery
    pickup_location: dict  # {"lat": float, "lng": float, "address": str}
    delivery_locations: List[dict] = []  # Multiple destinations support
    total_quantity: float
    quantity_unit: str  # "kg", "pieces", etc.
    distance_km: float
    estimated_price: float
    negotiated_price: Optional[float] = None
    product_details: str
    weight_kg: Optional[float] = None
    special_instructions: Optional[str] = None
    assigned_driver_id: Optional[str] = None
    preferred_driver_id: Optional[str] = None  # For driver search and selection
    status: DeliveryStatus = DeliveryStatus.PENDING
    delivery_otp: Optional[str] = None
    chat_messages: List[dict] = []  # Messaging between requester and driver
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class DeliveryMessage(BaseModel):
    id: Optional[str] = None
    delivery_request_id: str
    sender_username: str
    sender_type: str  # "requester" or "driver"
    message_type: str  # "text", "location", "image"
    content: str
    location_data: Optional[dict] = None  # For location sharing
    timestamp: Optional[datetime] = None

class DeliveryRequestCreate(BaseModel):
    order_id: str
    order_type: str
    pickup_address: str
    pickup_coordinates: Optional[dict] = None  # {"lat": float, "lng": float}
    delivery_addresses: List[str]  # Multiple delivery addresses
    delivery_coordinates: Optional[List[dict]] = []  # Coordinates for each delivery address
    total_quantity: float
    quantity_unit: str
    product_details: str
    weight_kg: Optional[float] = None
    special_instructions: Optional[str] = None
    estimated_price: float
    preferred_driver_username: Optional[str] = None  # For driver selection

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

class DeliveryRequestCreate(BaseModel):
    order_id: str
    order_type: str
    pickup_address: str
    delivery_address: str
    product_details: str
    weight_kg: Optional[float] = None
    special_instructions: Optional[str] = None
    estimated_price: float

class PreOrderStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published" 
    PARTIAL_PAID = "partial_paid"
    AWAITING_DELIVERY = "awaiting_delivery"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Old ProductCategory enum removed - using new structure above
    FISH = "fish"
    MEAT = "meat"
    PACKAGED_GOODS = "packaged_goods"
    FEEDS = "feeds"
    FRUITS = "fruits"

class PreOrder(BaseModel):
    id: Optional[str] = None
    seller_username: str
    seller_type: str  # farmer, supplier, processor
    business_name: str
    farm_name: Optional[str] = None
    agent_username: Optional[str] = None  # If published by agent
    product_name: str
    product_category: ProductCategory
    description: str
    total_stock: int
    available_stock: int
    unit: str  # kg, pieces, tons, etc.
    price_per_unit: float
    partial_payment_percentage: float  # 0.1 to 0.9 (10% to 90%)
    location: str
    delivery_date: datetime  # When product will be available
    images: List[str] = []
    status: PreOrderStatus = PreOrderStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    orders_count: int = 0  # Number of pre-orders placed
    total_ordered_quantity: int = 0

class PreOrderCreate(BaseModel):
    product_name: str
    product_category: ProductCategory
    description: str
    total_stock: int
    unit: str
    price_per_unit: float
    partial_payment_percentage: float
    location: str
    delivery_date: datetime
    business_name: str
    farm_name: Optional[str] = None
    images: List[str] = []
    
    @validator('partial_payment_percentage')
    def validate_percentage(cls, v):
        if not 0.1 <= v <= 0.9:
            raise ValueError('Partial payment percentage must be between 10% and 90%')
        return v
    
    @validator('total_stock')
    def validate_stock(cls, v):
        if v <= 0:
            raise ValueError('Total stock must be greater than 0')
        return v
    
    @validator('price_per_unit')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price per unit must be greater than 0')
        return v

class PreOrderFilter(BaseModel):
    category: Optional[ProductCategory] = None
    location: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    delivery_date_from: Optional[datetime] = None
    delivery_date_to: Optional[datetime] = None
    only_preorders: Optional[bool] = None
    search_term: Optional[str] = None
    seller_type: Optional[str] = None  # farmer, supplier, processor

# Drop-off Location Models
class DropoffLocation(BaseModel):
    id: Optional[str] = None
    name: str
    address: str
    city: str
    state: str
    country: str = "Nigeria"
    coordinates: Optional[dict] = None  # {"lat": float, "lng": float}
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    operating_hours: Optional[str] = None
    description: Optional[str] = None
    agent_username: str  # Agent who added this location
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DropoffLocationCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str
    country: str = "Nigeria"
    coordinates: Optional[dict] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    operating_hours: Optional[str] = None
    description: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Location name must be at least 3 characters long')
        return v.strip()
    
    @validator('address')
    def validate_address(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Address must be at least 5 characters long')
        return v.strip()

class DropoffLocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    coordinates: Optional[dict] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    operating_hours: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

# Pydantic models
class UserRegister(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email_or_phone: str
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    username: str
    email: str
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_verified: bool = False
    wallet_balance: float = 0.0
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

class CompleteRegistration(BaseModel):
    first_name: str
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

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    seller_name: str
    title: str
    description: str
    category: ProductCategory
    price_per_unit: float
    unit_of_measure: str  # kg, basket, crate, bag, gallon, etc.
    unit_specification: Optional[str] = None  # "100kg", "big", "5 litres", etc.
    quantity_available: int
    minimum_order_quantity: int = 1
    location: str
    farm_name: Optional[str] = None
    listed_by_agent: bool = False
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    images: List[str] = []
    platform: str  # "pyhub" or "pyexpress"
    # Enhanced delivery options for suppliers
    supports_dropoff_delivery: bool = True  # Whether supplier accepts drop-off locations
    supports_shipping_delivery: bool = True  # Whether supplier accepts shipping addresses
    delivery_cost_dropoff: float = 0.0  # Cost for drop-off delivery (0.0 = free)
    delivery_cost_shipping: float = 0.0  # Cost for shipping delivery (0.0 = free)
    delivery_notes: Optional[str] = None  # Special delivery instructions/notes
    # Rating information
    average_rating: float = 5.0  # Product rating
    total_ratings: int = 0  # Number of product ratings
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    title: str
    description: str
    category: ProductCategory
    price_per_unit: float
    unit_of_measure: str
    unit_specification: Optional[str] = None  # "100kg", "big", "5 litres", etc.
    quantity_available: int
    minimum_order_quantity: int = 1
    location: str
    farm_name: Optional[str] = None
    images: List[str] = []
    platform: str = "pyhub"
    # Enhanced delivery options for suppliers
    supports_dropoff_delivery: bool = True  # Whether supplier accepts drop-off locations  
    supports_shipping_delivery: bool = True  # Whether supplier accepts shipping addresses
    delivery_cost_dropoff: float = 0.0  # Cost for drop-off delivery (0.0 = free)
    delivery_cost_shipping: float = 0.0  # Cost for shipping delivery (0.0 = free)
    delivery_notes: Optional[str] = None  # Special delivery instructions/notes

class CartItem(BaseModel):
    product_id: str
    quantity: int

# Rating System Models
class RatingType(str, Enum):
    USER_RATING = "user_rating"  # Rating for farmers, agents, suppliers, processors
    PRODUCT_RATING = "product_rating"  # Rating for products
    DRIVER_RATING = "driver_rating"  # Rating for drivers
    ORDER_RATING = "order_rating"  # Overall order experience rating

class Rating(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rating_type: RatingType
    rating_value: int = Field(..., ge=1, le=5)  # 1-5 star rating
    rater_username: str  # Who gave the rating
    rater_id: str
    rated_entity_id: str  # ID of user, product, driver being rated
    rated_entity_username: Optional[str] = None  # Username if rating a user/driver
    order_id: Optional[str] = None  # Associated order if applicable
    comment: Optional[str] = None  # Optional review comment
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class RatingCreate(BaseModel):
    rating_type: RatingType
    rating_value: int = Field(..., ge=1, le=5)
    rated_entity_id: str
    rated_entity_username: Optional[str] = None
    order_id: Optional[str] = None
    comment: Optional[str] = None

class RatingResponse(BaseModel):
    id: str
    rating_type: RatingType
    rating_value: int
    rater_username: str
    rated_entity_id: str
    rated_entity_username: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime

# Driver Management Models
class DriverSubscriptionStatus(str, Enum):
    TRIAL = "trial"  # 14-day free trial
    ACTIVE = "active"  # Paid subscription
    EXPIRED = "expired"  # Subscription expired
    SUSPENDED = "suspended"  # Suspended by admin

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

# Enhanced Driver Profile for Uber-like Interface
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

# Digital Wallet System Models
class TransactionType(str, Enum):
    WALLET_FUNDING = "wallet_funding"
    WALLET_WITHDRAWAL = "wallet_withdrawal" 
    ORDER_PAYMENT = "order_payment"
    ORDER_REFUND = "order_refund"
    GIFT_CARD_PURCHASE = "gift_card_purchase"
    GIFT_CARD_REDEMPTION = "gift_card_redemption"
    COMMISSION_PAYMENT = "commission_payment"
    DRIVER_PAYMENT = "driver_payment"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FundingMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    DEBIT_CARD = "debit_card"
    USSD = "ussd"
    BANK_DEPOSIT = "bank_deposit"
    GIFT_CARD = "gift_card"

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

# Gift Card System Models
class GiftCardStatus(str, Enum):
    ACTIVE = "active"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

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

# Wallet Settings and Security
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

# Enhanced User Wallet Summary
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

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload.get('user_id')
        user = db.users.find_one({'id': user_id})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Pyramyd API"}

@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    # Check if user exists
    if db.users.find_one({"$or": [{"email": user_data.email}, {"username": user_data.username}]}):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone
    )
    
    # Hash password and store
    user_dict = user.dict()
    user_dict['password'] = hash_password(user_data.password)
    
    db.users.insert_one(user_dict)
    
    # Generate token
    token = create_token(user.id)
    
    return {
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }

@app.post("/api/auth/login")
async def login(login_data: UserLogin):
    # Find user by email or phone
    user = db.users.find_one({
        "$or": [
            {"email": login_data.email_or_phone},
            {"phone": login_data.email_or_phone},
            {"email_or_phone": login_data.email_or_phone}  # For backward compatibility
        ]
    })
    
    if not user or not verify_password(login_data.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user['id'])
    
    # Determine default platform based on role
    platform = "home"  # Default to home page
    if user.get('role') in ['farmer', 'agent', 'driver', 'storage_owner']:
        platform = "buy_from_farm"
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user['id'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "username": user['username'],
            "email": user.get('email', user.get('email_or_phone')),
            "role": user.get('role'),
            "platform": platform
        }
    }

@app.post("/api/auth/complete-registration")
async def complete_registration(registration_data: CompleteRegistration):
    # Check if user exists
    if db.users.find_one({"$or": [
        {"email_or_phone": registration_data.email_or_phone}, 
        {"username": registration_data.username}
    ]}):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Determine user role based on registration path
    user_role = None
    if registration_data.user_path == 'buyer':
        if registration_data.buyer_type == 'skip':
            user_role = 'general_buyer'
        else:
            user_role = registration_data.buyer_type
    elif registration_data.user_path == 'partner':
        if registration_data.partner_type == 'business':
            user_role = registration_data.business_category
        else:
            user_role = registration_data.partner_type
    
    # Create user with complete information
    user = User(
        first_name=registration_data.first_name,
        last_name=registration_data.last_name,
        username=registration_data.username,
        email=registration_data.email_or_phone,  # Store as email for compatibility
        phone=registration_data.phone,
        role=user_role
    )
    
    # Create user document with additional fields
    user_dict = user.dict()
    user_dict['password'] = hash_password(registration_data.password)
    user_dict['gender'] = registration_data.gender
    user_dict['date_of_birth'] = registration_data.date_of_birth
    user_dict['user_path'] = registration_data.user_path
    user_dict['business_info'] = registration_data.business_info or {}
    user_dict['verification_info'] = registration_data.verification_info or {}
    user_dict['is_verified'] = False  # Will be updated after verification process
    
    db.users.insert_one(user_dict)
    
    # Generate token
    token = create_token(user.id)
    
    return {
        "message": "Registration completed successfully",
        "token": token,
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "role": user_role,
            "user_path": registration_data.user_path
        }
    }

@app.get("/api/user/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_data = {
        "id": current_user['id'],
        "first_name": current_user['first_name'],
        "last_name": current_user['last_name'],
        "username": current_user['username'],
        "email": current_user['email'],
        "phone": current_user.get('phone'),
        "role": current_user.get('role'),
        "is_verified": current_user.get('is_verified', False),
        "wallet_balance": current_user.get('wallet_balance', 0.0)
    }
    return user_data

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    only_preorders: Optional[bool] = None,
    search_term: Optional[str] = None,
    seller_type: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get products with advanced filtering"""
    try:
        results = {"products": [], "preorders": [], "total_count": 0, "page": page, "limit": limit}
        
        # Regular products query
        if not only_preorders:
            products_query = {}
            
            if category:
                products_query["category"] = category
                
            if location:
                products_query["location"] = {"$regex": location, "$options": "i"}
                
            if min_price is not None or max_price is not None:
                price_filter = {}
                if min_price is not None:
                    price_filter["$gte"] = min_price
                if max_price is not None:
                    price_filter["$lte"] = max_price
                products_query["price_per_unit"] = price_filter
                
            if search_term:
                products_query["$or"] = [
                    {"crop_type": {"$regex": search_term, "$options": "i"}},
                    {"location": {"$regex": search_term, "$options": "i"}},
                    {"farm_name": {"$regex": search_term, "$options": "i"}}
                ]
            
            # Get products
            skip = (page - 1) * limit
            products = list(db.products.find(products_query).sort("created_at", -1).skip(skip).limit(limit))
            
            # Clean up products
            for product in products:
                product["_id"] = str(product["_id"])
                if "created_at" in product and isinstance(product["created_at"], datetime):
                    product["created_at"] = product["created_at"].isoformat()
                product["type"] = "regular"
            
            results["products"] = products
            results["total_count"] += db.products.count_documents(products_query)
        
        # Pre-orders query (if not filtering out pre-orders)
        if only_preorders or only_preorders is None:
            preorders_query = {"status": PreOrderStatus.PUBLISHED}
            
            if category:
                preorders_query["product_category"] = category
                
            if location:
                preorders_query["location"] = {"$regex": location, "$options": "i"}
                
            if min_price is not None or max_price is not None:
                price_filter = {}
                if min_price is not None:
                    price_filter["$gte"] = min_price
                if max_price is not None:
                    price_filter["$lte"] = max_price
                preorders_query["price_per_unit"] = price_filter
                
            if search_term:
                preorders_query["$or"] = [
                    {"product_name": {"$regex": search_term, "$options": "i"}},
                    {"description": {"$regex": search_term, "$options": "i"}},
                    {"business_name": {"$regex": search_term, "$options": "i"}},
                    {"farm_name": {"$regex": search_term, "$options": "i"}}
                ]
                
            if seller_type:
                preorders_query["seller_type"] = seller_type
            
            # Get pre-orders with improved pagination logic
            skip = (page - 1) * limit if only_preorders else 0
            
            # Fix: Ensure pre-orders get a fair share of the response, not just leftovers
            if only_preorders:
                limit_preorders = limit
            else:
                # Allow pre-orders alongside products - increase effective limit or reserve space
                # Option 1: Reserve space for pre-orders (e.g., show up to 15 products + 5 pre-orders)
                max_products_for_mixed = max(1, int(limit * 0.75))  # Reserve 75% for products, 25% for pre-orders  
                if len(results["products"]) > max_products_for_mixed:
                    # Trim products to make space for pre-orders
                    results["products"] = results["products"][:max_products_for_mixed]
                
                limit_preorders = limit - len(results["products"])
                limit_preorders = max(limit_preorders, int(limit * 0.25))  # Always allow at least 25% for pre-orders
            
            if limit_preorders > 0:
                preorders = list(db.preorders.find(preorders_query).sort("created_at", -1).skip(skip).limit(limit_preorders))
                
                # Clean up pre-orders
                for preorder in preorders:
                    preorder.pop('_id', None)
                    preorder["created_at"] = preorder["created_at"].isoformat()
                    preorder["updated_at"] = preorder["updated_at"].isoformat()
                    preorder["delivery_date"] = preorder["delivery_date"].isoformat()
                    preorder["type"] = "preorder"
                
                results["preorders"] = preorders
                results["total_count"] += db.preorders.count_documents(preorders_query)
        
        results["total_pages"] = (results["total_count"] + limit - 1) // limit
        
        return results
        
    except Exception as e:
        print(f"Error getting products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get products")

@app.get("/api/categories")
async def get_categories():
    return [{"value": cat.value, "label": cat.value.replace("_", " ").title()} for cat in ProductCategory]

@app.post("/api/products")
async def create_product(product_data: ProductCreate, current_user: dict = Depends(get_current_user)):
    if not current_user.get('role'):
        raise HTTPException(status_code=400, detail="Please select a role first")
    
    # Check if user can create products
    allowed_roles = ['farmer', 'agent', 'supplier_farm_inputs', 'supplier_food_produce', 'processor']
    if current_user.get('role') not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized to create products")
    
    # Determine platform based on user role and product category
    user_role = current_user.get('role')
    product_platform = product_data.platform
    
    # Enforce platform restrictions
    if user_role == 'farmer':
        product_platform = 'pyhub'
    elif user_role == 'supplier_farm_inputs':
        product_platform = 'pyhub'
        # Validate that the product category is appropriate for farm inputs
        farm_input_categories = ['fertilizer', 'herbicides', 'pesticides', 'seeds']
        if product_data.category.value not in farm_input_categories:
            raise HTTPException(status_code=400, detail="Farm input suppliers can only list farm input products")
    elif user_role == 'supplier_food_produce':
        product_platform = 'pyexpress'
        # Validate that the product category is appropriate for food produce
        food_categories = ['sea_food', 'grain', 'legumes', 'vegetables', 'spices', 'fruits', 'fish', 'meat', 'packaged_goods']
        if product_data.category.value not in food_categories:
            raise HTTPException(status_code=400, detail="Food produce suppliers can only list food products")
    elif user_role == 'processor':
        product_platform = 'pyexpress'
    
    # Create product
    product = Product(
        seller_id=current_user['id'],
        seller_name=current_user['username'],
        platform=product_platform,
        **{k: v for k, v in product_data.dict().items() if k != 'platform'}
    )
    
    # Apply service charges based on role
    if current_user.get('role') == 'farmer':
        # 30% markup for farmers on PyHub
        product.price_per_unit = product_data.price_per_unit * 1.30
    elif current_user.get('role') in ['supplier_food_produce', 'processor']:
        # 10% service charge deduction for PyExpress suppliers
        product.price_per_unit = product_data.price_per_unit * 0.90
    
    product_dict = product.dict()
    db.products.insert_one(product_dict)
    
    return {"message": "Product created successfully", "product_id": product.id}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    product = db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.pop('_id', None)
    return product

@app.post("/api/orders")
async def create_order(items: List[CartItem], delivery_address: str, current_user: dict = Depends(get_current_user)):
    if not items:
        raise HTTPException(status_code=400, detail="No items in order")
    
    order_items = []
    total_amount = 0.0
    seller_id = None
    seller_name = None
    
    for item in items:
        product = db.products.find_one({"id": item.product_id})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if item.quantity > product['quantity_available']:
            raise HTTPException(status_code=400, detail=f"Insufficient quantity for {product['title']}")
        
        if item.quantity < product['minimum_order_quantity']:
            raise HTTPException(status_code=400, detail=f"Minimum order quantity for {product['title']} is {product['minimum_order_quantity']}")
        
        item_total = product['price_per_unit'] * item.quantity
        total_amount += item_total
        
        order_items.append({
            "product_id": product['id'],
            "title": product['title'],
            "price_per_unit": product['price_per_unit'],
            "quantity": item.quantity,
            "total": item_total
        })
        
        # All items should be from same seller for this MVP
        if seller_id is None:
            seller_id = product['seller_id']
            seller_name = product['seller_name']
        elif seller_id != product['seller_id']:
            raise HTTPException(status_code=400, detail="All items must be from the same seller")
    
    # Create order
    order = Order(
        buyer_id=current_user['id'],
        buyer_name=current_user['username'],
        seller_id=seller_id,
        seller_name=seller_name,
        items=order_items,
        total_amount=total_amount,
        delivery_address=delivery_address
    )
    
    order_dict = order.dict()
    db.orders.insert_one(order_dict)
    
    # Update product quantities
    for item in items:
        db.products.update_one(
            {"id": item.product_id},
            {"$inc": {"quantity_available": -item.quantity}}
        )
    
    return {"message": "Order created successfully", "order_id": order.id, "total_amount": total_amount}

@app.get("/api/orders")
async def get_orders(current_user: dict = Depends(get_current_user)):
    # Get orders where user is buyer or seller
    orders = list(db.orders.find({
        "$or": [
            {"buyer_id": current_user['id']},
            {"seller_id": current_user['id']}
        ]
    }).sort("created_at", -1))
    
    # Clean up response
    for order in orders:
        order.pop('_id', None)
    
    return orders

class AgentPurchaseOption(BaseModel):
    commission_type: str  # "percentage" or "collect_after_delivery"
    customer_id: str
    delivery_address: str

class GroupBuyingRequest(BaseModel):
    produce: str
    category: str
    quantity: int
    location: str

class GroupOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    produce: str
    category: str
    location: str
    total_quantity: int
    buyers: List[dict]
    selected_farm: dict
    commission_type: str  # "pyramyd" or "after_delivery"
    total_amount: float
    agent_commission: float
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OutsourcedOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requester_id: str  # Agent or Processor who outsourced
    produce: str
    category: str
    quantity: int
    expected_price: float
    location: str
    status: str = "open"  # "open", "accepted", "completed", "cancelled"
    accepting_agent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

@app.post("/api/agent/purchase")
async def agent_purchase(
    items: List[CartItem], 
    purchase_option: AgentPurchaseOption,
    current_user: dict = Depends(get_current_user)
):
    """Agent purchasing on behalf of customers with commission options"""
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can use this endpoint")
    
    if not items:
        raise HTTPException(status_code=400, detail="No items in order")
    
    order_items = []
    total_amount = 0.0
    seller_id = None
    seller_name = None
    
    for item in items:
        product = db.products.find_one({"id": item.product_id})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if item.quantity > product['quantity_available']:
            raise HTTPException(status_code=400, detail=f"Insufficient quantity for {product['title']}")
        
        item_total = product['price_per_unit'] * item.quantity
        total_amount += item_total
        
        order_items.append({
            "product_id": product['id'],
            "title": product['title'],
            "price_per_unit": product['price_per_unit'],
            "quantity": item.quantity,
            "total": item_total
        })
        
        if seller_id is None:
            seller_id = product['seller_id']
            seller_name = product['seller_name']
        elif seller_id != product['seller_id']:
            raise HTTPException(status_code=400, detail="All items must be from the same seller")
    
    # Calculate agent commission
    commission_rate = AGENT_COMMISSION_RATES['purchase']  # 5%
    commission_amount = total_amount * commission_rate
    
    # Create order with agent commission details
    order = Order(
        buyer_id=purchase_option.customer_id,
        buyer_name="Customer (via Agent)",
        seller_id=seller_id,
        seller_name=seller_name,
        items=order_items,
        total_amount=total_amount,
        delivery_address=purchase_option.delivery_address,
        agent_id=current_user['id'],
        agent_commission_type=purchase_option.commission_type,
        agent_commission_amount=commission_amount
    )
    
    order_dict = order.dict()
    db.orders.insert_one(order_dict)
    
    # Update product quantities
    for item in items:
        db.products.update_one(
            {"id": item.product_id},
            {"$inc": {"quantity_available": -item.quantity}}
        )
    
    return {
        "message": "Agent purchase successful",
        "order_id": order.id,
        "total_amount": total_amount,
        "commission_amount": commission_amount,
        "commission_type": purchase_option.commission_type
    }

@app.get("/api/users/search")
async def search_users(username: str, current_user: dict = Depends(get_current_user)):
    """Search users by username for group buying"""
    if not username:
        return []
    
    users = list(db.users.find({
        "username": {"$regex": username, "$options": "i"},
        "role": {"$in": ["general_buyer", "retailer", "hotel", "restaurant", "cafe"]}
    }).limit(10))
    
    # Clean up response and add NIN verification status
    for user in users:
        user.pop('_id', None)
        user.pop('password', None)
        # Check if user has NIN for group buying eligibility
        user['is_nin_verified'] = bool(user.get('verification_info', {}).get('nin'))
    
    return users

@app.post("/api/group-buying/recommendations")
async def get_price_recommendations(
    request: GroupBuyingRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Get price recommendations for group buying based on matching farms"""
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can access group buying")
    
    # Find matching products/farms
    query = {
        "$or": [
            {"title": {"$regex": request.produce, "$options": "i"}},
            {"description": {"$regex": request.produce, "$options": "i"}}
        ],
        "category": request.category,
        "quantity_available": {"$gte": 1}  # At least some stock
    }
    
    if request.location:
        query["location"] = {"$regex": request.location, "$options": "i"}
    
    matching_products = list(db.products.find(query))
    
    recommendations = []
    for product in matching_products:
        # Calculate match percentage based on available quantity
        match_percentage = min(100, (product['quantity_available'] / request.quantity) * 100)
        
        # Calculate distance (mock calculation - in real app, use geolocation)
        distance = 5 + (hash(product['location']) % 50)  # Mock 5-55km distance
        
        rec = {
            "farm_id": product['seller_id'],
            "farm_name": product.get('farm_name', product['seller_name']),
            "location": product['location'],
            "price_per_unit": product['price_per_unit'],
            "available_quantity": product['quantity_available'],
            "match_percentage": int(match_percentage),
            "distance": distance,
            "product_id": product['id']
        }
        recommendations.append(rec)
    
    # Sort by match percentage and distance
    recommendations.sort(key=lambda x: (-x['match_percentage'], x['distance']))
    
    return {"recommendations": recommendations[:5]}  # Return top 5 matches

@app.post("/api/group-buying/create-order")
async def create_group_order(
    order_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a group buying order"""
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can create group orders")
    
    # Calculate commission
    total_amount = order_data['selectedPrice']['price_per_unit'] * order_data['quantity']
    
    if order_data['commissionType'] == 'pyramyd':
        agent_commission = total_amount * 0.05  # 5% commission
    else:
        agent_commission = 0  # Will be collected after delivery
    
    # Create group order
    group_order = GroupOrder(
        agent_id=current_user['id'],
        produce=order_data['produce'],
        category=order_data['category'],
        location=order_data['location'],
        total_quantity=order_data['quantity'],
        buyers=order_data['buyers'],
        selected_farm=order_data['selectedPrice'],
        commission_type=order_data['commissionType'],
        total_amount=total_amount,
        agent_commission=agent_commission
    )
    
    # Save to database
    order_dict = group_order.dict()
    db.group_orders.insert_one(order_dict)
    
    # Update product quantity (real-time stock management)
    db.products.update_one(
        {"id": order_data['selectedPrice']['product_id']},
        {"$inc": {"quantity_available": -order_data['quantity']}}
    )
    
    return {
        "message": "Group order created successfully",
        "order_id": group_order.id,
        "total_amount": total_amount,
        "agent_commission": agent_commission
    }

@app.post("/api/outsource-order")
async def create_outsourced_order(
    produce: str,
    category: str,
    quantity: int,
    expected_price: float,
    location: str,
    current_user: dict = Depends(get_current_user)
):
    """Create an outsourced order for agents to bid on"""
    allowed_roles = ['agent', 'processor', 'supplier']
    if current_user.get('role') not in allowed_roles:
        raise HTTPException(status_code=403, detail="Only agents, processors, and suppliers can outsource orders")
    
    outsourced_order = OutsourcedOrder(
        requester_id=current_user['id'],
        produce=produce,
        category=category,
        quantity=quantity,
        expected_price=expected_price,
        location=location
    )
    
    order_dict = outsourced_order.dict()
    db.outsourced_orders.insert_one(order_dict)
    
    return {
        "message": "Order outsourced successfully",
        "order_id": outsourced_order.id,
        "status": "open"
    }

@app.get("/api/outsourced-orders")
async def get_outsourced_orders(current_user: dict = Depends(get_current_user)):
    """Get available outsourced orders for agents to accept"""
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can view outsourced orders")
    
    orders = list(db.outsourced_orders.find({"status": "open"}).sort("created_at", -1))
    
    # Clean up response
    for order in orders:
        order.pop('_id', None)
    
    return orders

@app.post("/api/outsourced-orders/{order_id}/accept")
async def accept_outsourced_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Accept an outsourced order"""
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can accept outsourced orders")
    
    # Update order status
    result = db.outsourced_orders.update_one(
        {"id": order_id, "status": "open"},
        {
            "$set": {
                "status": "accepted",
                "accepting_agent_id": current_user['id']
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found or already accepted")
    
    return {"message": "Order accepted successfully"}

@app.get("/api/users/search-messaging")
async def search_users_messaging(username: str, current_user: dict = Depends(get_current_user)):
    """Search users by username for messaging"""
    if len(username) < 2:
        raise HTTPException(status_code=400, detail="Search term must be at least 2 characters")
    
    # Search for users with username containing the search term, excluding current user
    users = list(users_collection.find({
        "$and": [
            {"username": {"$regex": username, "$options": "i"}},
            {"username": {"$ne": current_user["username"]}}
        ]
    }, {"password": 0}))  # Exclude password field
    
    # Clean up response
    for user in users:
        user.pop('_id', None)
    
    return users[:10]  # Limit to 10 results

@app.post("/api/messages/send")
async def send_message(
    message_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send a message to another user"""
    try:
        # Validate message data
        if not message_data.get("recipient_username"):
            raise HTTPException(status_code=400, detail="Recipient username is required")
        
        if not message_data.get("content") and not message_data.get("audio_data"):
            raise HTTPException(status_code=400, detail="Message content or audio data is required")
        
        # Check if recipient exists
        recipient = users_collection.find_one({"username": message_data["recipient_username"]})
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")
        
        # Create message document
        message = {
            "id": str(uuid.uuid4()),
            "sender_username": current_user["username"],
            "recipient_username": message_data["recipient_username"],
            "conversation_id": message_data.get("conversation_id"),
            "type": message_data.get("type", "text"),
            "content": message_data.get("content"),
            "audio_data": message_data.get("audio_data"),
            "timestamp": datetime.utcnow(),
            "read": False
        }
        
        # Store message in database
        messages_collection.insert_one(message)
        
        return {"message": "Message sent successfully", "message_id": message["id"]}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@app.get("/api/messages/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    """Get user's conversations"""
    try:
        # Get all messages where user is sender or recipient
        messages = list(messages_collection.find({
            "$or": [
                {"sender_username": current_user["username"]},
                {"recipient_username": current_user["username"]}
            ]
        }).sort("timestamp", -1))
        
        # Group by conversation_id and get latest message for each
        conversations = {}
        for message in messages:
            conv_id = message.get("conversation_id")
            if conv_id and conv_id not in conversations:
                # Get the other participant
                other_user = message["recipient_username"] if message["sender_username"] == current_user["username"] else message["sender_username"]
                other_user_data = users_collection.find_one({"username": other_user}, {"password": 0})
                
                if other_user_data:
                    # Clean up other_user_data
                    other_user_data.pop('_id', None)
                    
                    # Clean up message for response
                    message_copy = message.copy()
                    message_copy.pop('_id', None)
                    message_copy["timestamp"] = message_copy["timestamp"].isoformat()
                    
                    conversations[conv_id] = {
                        "id": conv_id,
                        "participants": [current_user["username"], other_user],
                        "other_user": {
                            "username": other_user_data["username"],
                            "first_name": other_user_data.get("first_name", ""),
                            "last_name": other_user_data.get("last_name", "")
                        },
                        "last_message": message_copy,
                        "timestamp": message["timestamp"].isoformat()
                    }
        
        return list(conversations.values())
        
    except Exception as e:
        print(f"Error getting conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")

@app.get("/api/messages/{conversation_id}")
async def get_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get messages for a specific conversation"""
    try:
        # Get all messages for this conversation
        messages = list(messages_collection.find({
            "conversation_id": conversation_id,
            "$or": [
                {"sender_username": current_user["username"]},
                {"recipient_username": current_user["username"]}
            ]
        }).sort("timestamp", 1))
        
        # Clean up messages for response
        for message in messages:
            message.pop('_id', None)
            message["timestamp"] = message["timestamp"].isoformat()
        
        # Mark messages as read
        messages_collection.update_many(
            {
                "conversation_id": conversation_id,
                "recipient_username": current_user["username"],
                "read": False
            },
            {"$set": {"read": True}}
        )
        
        return messages
        
    except Exception as e:
        print(f"Error getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@app.post("/api/preorders/create")
async def create_preorder(preorder_data: PreOrderCreate, current_user: dict = Depends(get_current_user)):
    """Create a new pre-order"""
    try:
        # Validate user can create pre-orders (farmers, suppliers, processors, agents)
        allowed_roles = ['farmer', 'supplier', 'processor', 'agent']
        if current_user.get('role') not in allowed_roles:
            raise HTTPException(status_code=403, detail="Only farmers, suppliers, processors, and agents can create pre-orders")
        
        # Create pre-order document
        pre_order = {
            "id": str(uuid.uuid4()),
            "seller_username": current_user["username"],
            "seller_type": current_user.get("role", "farmer"),
            "business_name": preorder_data.business_name,
            "farm_name": preorder_data.farm_name,
            "agent_username": current_user["username"] if current_user.get("role") == "agent" else None,
            "product_name": preorder_data.product_name,
            "product_category": preorder_data.product_category,
            "description": preorder_data.description,
            "total_stock": preorder_data.total_stock,
            "available_stock": preorder_data.total_stock,
            "unit": preorder_data.unit,
            "price_per_unit": preorder_data.price_per_unit,
            "partial_payment_percentage": preorder_data.partial_payment_percentage,
            "location": preorder_data.location,
            "delivery_date": preorder_data.delivery_date,
            "images": preorder_data.images,
            "status": PreOrderStatus.DRAFT,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "orders_count": 0,
            "total_ordered_quantity": 0
        }
        
        # Store in database
        db.preorders.insert_one(pre_order)
        
        return {"message": "Pre-order created successfully", "preorder_id": pre_order["id"]}
        
    except Exception as e:
        print(f"Error creating pre-order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create pre-order")

@app.post("/api/preorders/{preorder_id}/publish")
async def publish_preorder(preorder_id: str, current_user: dict = Depends(get_current_user)):
    """Publish a pre-order to make it available for buyers"""
    try:
        # Find the pre-order
        preorder = db.preorders.find_one({"id": preorder_id})
        if not preorder:
            raise HTTPException(status_code=404, detail="Pre-order not found")
        
        # Check ownership
        if preorder["seller_username"] != current_user["username"]:
            raise HTTPException(status_code=403, detail="You can only publish your own pre-orders")
        
        # Check if already published
        if preorder["status"] != PreOrderStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Pre-order is already published or has orders")
        
        # Update status to published
        db.preorders.update_one(
            {"id": preorder_id},
            {
                "$set": {
                    "status": PreOrderStatus.PUBLISHED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Pre-order published successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error publishing pre-order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish pre-order")

@app.get("/api/preorders")
async def get_preorders(
    category: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    delivery_date_from: Optional[str] = None,
    delivery_date_to: Optional[str] = None,
    only_preorders: Optional[bool] = None,
    search_term: Optional[str] = None,
    seller_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get pre-orders with advanced filtering"""
    try:
        # Build filter query
        query = {}
        
        # Only show published pre-orders by default
        if status:
            query["status"] = status
        else:
            query["status"] = PreOrderStatus.PUBLISHED
        
        if category:
            query["product_category"] = category
            
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
            
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            query["price_per_unit"] = price_filter
            
        if delivery_date_from or delivery_date_to:
            date_filter = {}
            if delivery_date_from:
                date_filter["$gte"] = datetime.fromisoformat(delivery_date_from.replace('Z', '+00:00'))
            if delivery_date_to:
                date_filter["$lte"] = datetime.fromisoformat(delivery_date_to.replace('Z', '+00:00'))
            query["delivery_date"] = date_filter
            
        if search_term:
            query["$or"] = [
                {"product_name": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}},
                {"business_name": {"$regex": search_term, "$options": "i"}},
                {"farm_name": {"$regex": search_term, "$options": "i"}}
            ]
            
        if seller_type:
            query["seller_type"] = seller_type
        
        # Calculate skip for pagination
        skip = (page - 1) * limit
        
        # Get pre-orders with pagination
        preorders = list(db.preorders.find(query).sort("created_at", -1).skip(skip).limit(limit))
        
        # Get total count for pagination
        total_count = db.preorders.count_documents(query)
        
        # Clean up response
        for preorder in preorders:
            preorder.pop('_id', None)
            preorder["created_at"] = preorder["created_at"].isoformat()
            preorder["updated_at"] = preorder["updated_at"].isoformat()
            preorder["delivery_date"] = preorder["delivery_date"].isoformat()
        
        return {
            "preorders": preorders,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        print(f"Error getting pre-orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get pre-orders")

@app.get("/api/preorders/{preorder_id}")
async def get_preorder_details(preorder_id: str):
    """Get detailed information about a specific pre-order"""
    try:
        preorder = db.preorders.find_one({"id": preorder_id})
        if not preorder:
            raise HTTPException(status_code=404, detail="Pre-order not found")
        
        # Clean up response
        preorder.pop('_id', None)
        preorder["created_at"] = preorder["created_at"].isoformat()
        preorder["updated_at"] = preorder["updated_at"].isoformat()
        preorder["delivery_date"] = preorder["delivery_date"].isoformat()
        
        return preorder
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting pre-order details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get pre-order details")

@app.post("/api/preorders/{preorder_id}/order")
async def place_preorder(
    preorder_id: str,
    order_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Place an order on a pre-order"""
    try:
        # Validate order data
        if not order_data.get("quantity") or order_data["quantity"] <= 0:
            raise HTTPException(status_code=400, detail="Valid quantity is required")
        
        quantity = order_data["quantity"]
        
        # Find the pre-order
        preorder = db.preorders.find_one({"id": preorder_id})
        if not preorder:
            raise HTTPException(status_code=404, detail="Pre-order not found")
        
        # Check if pre-order is published
        if preorder["status"] != PreOrderStatus.PUBLISHED:
            raise HTTPException(status_code=400, detail="Pre-order is not available for ordering")
        
        # Check stock availability
        if quantity > preorder["available_stock"]:
            raise HTTPException(status_code=400, detail=f"Only {preorder['available_stock']} units available")
        
        # Calculate amounts
        total_amount = quantity * preorder["price_per_unit"]
        partial_amount = int(total_amount * preorder["partial_payment_percentage"])
        remaining_amount = total_amount - partial_amount
        
        # Create order document
        order = {
            "id": str(uuid.uuid4()),
            "preorder_id": preorder_id,
            "buyer_username": current_user["username"],
            "seller_username": preorder["seller_username"],
            "product_name": preorder["product_name"],
            "quantity": quantity,
            "unit_price": preorder["price_per_unit"],
            "total_amount": total_amount,
            "partial_amount": partial_amount,
            "remaining_amount": remaining_amount,
            "partial_payment_percentage": preorder["partial_payment_percentage"],
            "status": "pending_partial_payment",
            "delivery_date": preorder["delivery_date"],
            "location": preorder["location"],
            "business_name": preorder["business_name"],
            "farm_name": preorder.get("farm_name"),
            "agent_username": preorder.get("agent_username"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Store order
        db.preorder_orders.insert_one(order)
        
        # Update pre-order stock and counts
        db.preorders.update_one(
            {"id": preorder_id},
            {
                "$inc": {
                    "available_stock": -quantity,
                    "orders_count": 1,
                    "total_ordered_quantity": quantity
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {
            "message": "Pre-order placed successfully",
            "order_id": order["id"],
            "total_amount": total_amount,
            "partial_amount": partial_amount,
            "remaining_amount": remaining_amount
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error placing pre-order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to place pre-order")

@app.get("/api/my-preorders")
async def get_my_preorders(current_user: dict = Depends(get_current_user)):
    """Get current user's pre-orders"""
    try:
        preorders = list(db.preorders.find({"seller_username": current_user["username"]}).sort("created_at", -1))
        
        # Clean up response
        for preorder in preorders:
            preorder.pop('_id', None)
            preorder["created_at"] = preorder["created_at"].isoformat()
            preorder["updated_at"] = preorder["updated_at"].isoformat()
            preorder["delivery_date"] = preorder["delivery_date"].isoformat()
        
        return preorders
        
    except Exception as e:
        print(f"Error getting user pre-orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user pre-orders")

@app.post("/api/drivers/register-independent")
async def register_independent_driver(driver_data: DriverCreate, current_user: dict = Depends(get_current_user)):
    """Register as an independent driver"""
    try:
        # Validate user can register as driver
        if current_user.get('role') != 'driver':
            raise HTTPException(status_code=403, detail="Only users with driver role can register as independent drivers")
        
        # Check if user already has a driver profile
        existing_driver = db.drivers.find_one({"driver_username": current_user["username"]})
        if existing_driver:
            raise HTTPException(status_code=400, detail="Driver profile already exists")
        
        # Create driver document
        driver = {
            "id": str(uuid.uuid4()),
            "driver_username": current_user["username"],
            "driver_name": driver_data.driver_name,
            "phone_number": driver_data.phone_number,
            "email": driver_data.email,
            "profile_picture": driver_data.profile_picture,
            "driver_license": driver_data.driver_license,
            "status": DriverStatus.OFFLINE,
            "current_location": None,
            "rating": 5.0,
            "total_deliveries": 0,
            "is_independent": True,
            "logistics_business_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Create vehicle document
        vehicle = {
            "id": str(uuid.uuid4()),
            "driver_id": driver["id"],
            "vehicle_type": driver_data.vehicle_type,
            "plate_number": driver_data.plate_number,
            "make_model": driver_data.make_model,
            "color": driver_data.color,
            "year": driver_data.year,
            "created_at": datetime.utcnow()
        }
        
        # Store in database
        db.drivers.insert_one(driver)
        db.vehicles.insert_one(vehicle)
        
        return {"message": "Driver registered successfully", "driver_id": driver["id"]}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error registering independent driver: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register driver")

@app.post("/api/logistics/add-driver")
async def add_driver_to_logistics(driver_data: DriverCreate, current_user: dict = Depends(get_current_user)):
    """Add a driver to logistics business dashboard"""
    try:
        # Validate user is logistics business
        if current_user.get('partner_type') != 'business' or current_user.get('business_category') != 'logistics_business':
            raise HTTPException(status_code=403, detail="Only logistics businesses can add managed drivers")
        
        # Get or create logistics business profile
        logistics_business = db.logistics_businesses.find_one({"business_username": current_user["username"]})
        if not logistics_business:
            # Create logistics business profile
            logistics_business = {
                "id": str(uuid.uuid4()),
                "business_username": current_user["username"],
                "business_name": current_user.get("business_info", {}).get("business_name", "Unknown Business"),
                "business_address": current_user.get("business_info", {}).get("business_address", ""),
                "phone_number": current_user.get("phone", ""),
                "email": current_user.get("email", ""),
                "cac_number": current_user.get("verification_info", {}).get("cac_number", ""),
                "drivers": [],
                "vehicles": [],
                "created_at": datetime.utcnow()
            }
            db.logistics_businesses.insert_one(logistics_business)
        
        # Create unique driver username
        driver_username = f"{current_user['username']}_driver_{len(logistics_business.get('drivers', [])) + 1}"
        
        # Create driver document
        driver = {
            "id": str(uuid.uuid4()),
            "driver_username": driver_username,
            "driver_name": driver_data.driver_name,
            "phone_number": driver_data.phone_number,
            "email": driver_data.email,
            "profile_picture": driver_data.profile_picture,
            "driver_license": driver_data.driver_license,
            "status": DriverStatus.OFFLINE,
            "current_location": None,
            "rating": 5.0,
            "total_deliveries": 0,
            "is_independent": False,
            "logistics_business_id": logistics_business["id"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Create vehicle document
        vehicle = {
            "id": str(uuid.uuid4()),
            "driver_id": driver["id"],
            "vehicle_type": driver_data.vehicle_type,
            "plate_number": driver_data.plate_number,
            "make_model": driver_data.make_model,
            "color": driver_data.color,
            "year": driver_data.year,
            "created_at": datetime.utcnow()
        }
        
        # Store in database
        db.drivers.insert_one(driver)
        db.vehicles.insert_one(vehicle)
        
        # Update logistics business
        db.logistics_businesses.update_one(
            {"id": logistics_business["id"]},
            {
                "$push": {
                    "drivers": driver["id"],
                    "vehicles": vehicle["id"]
                }
            }
        )
        
        return {
            "message": "Driver added successfully",
            "driver_id": driver["id"],
            "driver_username": driver_username,
            "driver_access_link": f"/driver-portal?token={driver['id']}"  # Link for driver to access portal
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding driver to logistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add driver")

@app.get("/api/logistics/my-drivers")
async def get_my_drivers(current_user: dict = Depends(get_current_user)):
    """Get all drivers managed by current logistics business"""
    try:
        # Get logistics business
        logistics_business = db.logistics_businesses.find_one({"business_username": current_user["username"]})
        if not logistics_business:
            return {"drivers": [], "vehicles": []}
        
        # Get drivers
        drivers = list(db.drivers.find({
            "logistics_business_id": logistics_business["id"]
        }))
        
        # Get vehicles
        vehicles = list(db.vehicles.find({
            "driver_id": {"$in": [driver["id"] for driver in drivers]}
        }))
        
        # Clean up response
        for driver in drivers:
            driver.pop('_id', None)
            if driver.get("created_at"):
                driver["created_at"] = driver["created_at"].isoformat()
            if driver.get("updated_at"):
                driver["updated_at"] = driver["updated_at"].isoformat()
        
        for vehicle in vehicles:
            vehicle.pop('_id', None)
            if vehicle.get("created_at"):
                vehicle["created_at"] = vehicle["created_at"].isoformat()
        
        return {"drivers": drivers, "vehicles": vehicles}
        
    except Exception as e:
        print(f"Error getting logistics drivers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get drivers")

@app.post("/api/delivery/request")
async def create_delivery_request(request_data: DeliveryRequestCreate, current_user: dict = Depends(get_current_user)):
    """Create a delivery request"""
    try:
        # Validate user can request delivery
        allowed_roles = ['agent', 'farmer', 'supplier', 'processor']
        if current_user.get('role') not in allowed_roles:
            raise HTTPException(status_code=403, detail="Only sellers can request delivery")
        
        # Calculate distance (simplified - in real app would use maps API)
        import random
        distance_km = random.uniform(5.0, 50.0)  # Mock distance
        
        # Generate OTP
        import random
        otp = str(random.randint(100000, 999999))
        
        # Create delivery request
        delivery_request = {
            "id": str(uuid.uuid4()),
            "order_id": request_data.order_id,
            "order_type": request_data.order_type,
            "requester_username": current_user["username"],
            "pickup_location": {
                "address": request_data.pickup_address,
                "lat": 0.0,  # Would be geocoded in real app
                "lng": 0.0
            },
            "delivery_location": {
                "address": request_data.delivery_address,
                "lat": 0.0,
                "lng": 0.0
            },
            "distance_km": distance_km,
            "estimated_price": request_data.estimated_price,
            "product_details": request_data.product_details,
            "weight_kg": request_data.weight_kg,
            "special_instructions": request_data.special_instructions,
            "status": DeliveryStatus.PENDING,
            "delivery_otp": otp,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Store in database
        db.delivery_requests.insert_one(delivery_request)
        
        return {
            "message": "Delivery request created successfully",
            "request_id": delivery_request["id"],
            "estimated_price": request_data.estimated_price,
            "distance_km": distance_km,
            "delivery_otp": otp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating delivery request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create delivery request")

@app.get("/api/delivery/available")
async def get_available_deliveries(current_user: dict = Depends(get_current_user)):
    """Get available delivery requests for drivers"""
    try:
        # Check if user is a driver
        driver = db.drivers.find_one({"driver_username": current_user["username"]})
        if not driver:
            raise HTTPException(status_code=403, detail="Only registered drivers can view delivery requests")
        
        # Get pending delivery requests
        delivery_requests = list(db.delivery_requests.find({
            "status": DeliveryStatus.PENDING
        }).sort("created_at", -1))
        
        # Clean up response
        for request in delivery_requests:
            request.pop('_id', None)
            request["created_at"] = request["created_at"].isoformat()
            request["updated_at"] = request["updated_at"].isoformat()
            # Don't expose OTP to drivers until they accept
            request.pop('delivery_otp', None)
        
        return {"delivery_requests": delivery_requests}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting available deliveries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get available deliveries")

@app.post("/api/delivery/{request_id}/accept")
async def accept_delivery_request(request_id: str, current_user: dict = Depends(get_current_user)):
    """Accept a delivery request"""
    try:
        # Check if user is a driver
        driver = db.drivers.find_one({"driver_username": current_user["username"]})
        if not driver:
            raise HTTPException(status_code=403, detail="Only registered drivers can accept deliveries")
        
        # Check if driver is available
        if driver["status"] in [DriverStatus.BUSY, DriverStatus.ON_DELIVERY]:
            raise HTTPException(status_code=400, detail="Driver is not available")
        
        # Find and update delivery request
        delivery_request = db.delivery_requests.find_one({"id": request_id})
        if not delivery_request:
            raise HTTPException(status_code=404, detail="Delivery request not found")
        
        if delivery_request["status"] != DeliveryStatus.PENDING:
            raise HTTPException(status_code=400, detail="Delivery request is no longer available")
        
        # Update delivery request
        db.delivery_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "assigned_driver_id": driver["id"],
                    "status": DeliveryStatus.ACCEPTED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update driver status
        db.drivers.update_one(
            {"id": driver["id"]},
            {
                "$set": {
                    "status": DriverStatus.ON_DELIVERY,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Delivery request accepted",
            "request_id": request_id,
            "pickup_address": delivery_request["pickup_location"]["address"],
            "delivery_address": delivery_request["delivery_location"]["address"],
            "estimated_price": delivery_request["estimated_price"],
            "delivery_otp": delivery_request["delivery_otp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error accepting delivery: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to accept delivery")

@app.post("/api/delivery/{request_id}/complete")
async def complete_delivery(request_id: str, otp: str, current_user: dict = Depends(get_current_user)):
    """Complete delivery with OTP verification"""
    try:
        # Find delivery request
        delivery_request = db.delivery_requests.find_one({"id": request_id})
        if not delivery_request:
            raise HTTPException(status_code=404, detail="Delivery request not found")
        
        # Verify OTP
        if delivery_request["delivery_otp"] != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        # Check if user is authorized (buyer or the assigned driver)
        driver = db.drivers.find_one({"id": delivery_request.get("assigned_driver_id")})
        if current_user["username"] != driver.get("driver_username"):
            # Could be buyer/agent confirming - add additional validation here
            pass
        
        # Update delivery request
        db.delivery_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "status": DeliveryStatus.DELIVERED,
                    "completed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update driver status and stats
        if driver:
            db.drivers.update_one(
                {"id": driver["id"]},
                {
                    "$set": {
                        "status": DriverStatus.ONLINE,
                        "updated_at": datetime.utcnow()
                    },
                    "$inc": {"total_deliveries": 1}
                }
            )
        
        # TODO: Process payment to agents and sellers here
        # This would integrate with payment processing system
        
        return {
            "message": "Delivery completed successfully",
            "request_id": request_id,
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing delivery: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete delivery")

@app.post("/api/delivery/{request_id}/negotiate")
async def negotiate_delivery_price(request_id: str, proposed_price: float, current_user: dict = Depends(get_current_user)):
    """Negotiate delivery price"""
    try:
        # Check if user is a driver
        driver = db.drivers.find_one({"driver_username": current_user["username"]})
        if not driver:
            raise HTTPException(status_code=403, detail="Only registered drivers can negotiate prices")
        
        # Find delivery request
        delivery_request = db.delivery_requests.find_one({"id": request_id})
        if not delivery_request:
            raise HTTPException(status_code=404, detail="Delivery request not found")
        
        if delivery_request["status"] != DeliveryStatus.PENDING:
            raise HTTPException(status_code=400, detail="Cannot negotiate on this delivery request")
        
        # Update with negotiated price
        db.delivery_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "negotiated_price": proposed_price,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Price negotiation submitted",
            "request_id": request_id,
            "proposed_price": proposed_price,
            "original_price": delivery_request["estimated_price"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error negotiating price: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to negotiate price")

@app.get("/api/drivers/search")
async def search_drivers(
    pickup_lat: Optional[float] = None,
    pickup_lng: Optional[float] = None,
    radius_km: float = 50.0,
    vehicle_type: Optional[str] = None,
    min_rating: float = 3.0,
    current_user: dict = Depends(get_current_user)
):
    """Search for available drivers near pickup location"""
    try:
        # Build search query
        query = {
            "status": {"$in": [DriverStatus.ONLINE, DriverStatus.OFFLINE]},
            "rating": {"$gte": min_rating}
        }
        
        if vehicle_type:
            # Get vehicle IDs with matching type
            vehicle_query = {"vehicle_type": vehicle_type}
            vehicles = list(db.vehicles.find(vehicle_query))
            driver_ids = [v["driver_id"] for v in vehicles]
            query["id"] = {"$in": driver_ids}
        
        # Get drivers
        drivers = list(db.drivers.find(query))
        
        # Get vehicle info for each driver
        driver_results = []
        for driver in drivers:
            vehicle = db.vehicles.find_one({"driver_id": driver["id"]})
            
            # Calculate distance if pickup coordinates provided
            distance_km = None
            if pickup_lat and pickup_lng and driver.get("current_location"):
                # Simple distance calculation (in real app would use proper geo calculation)
                import math
                lat1, lng1 = pickup_lat, pickup_lng
                lat2, lng2 = driver["current_location"].get("lat", 0), driver["current_location"].get("lng", 0)
                
                # Haversine formula approximation
                dlat = math.radians(lat2 - lat1)
                dlng = math.radians(lng2 - lng1)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
                c = 2 * math.asin(math.sqrt(a))
                distance_km = 6371 * c  # Earth's radius in km
                
                # Filter by radius
                if distance_km > radius_km:
                    continue
            
            driver_result = {
                "driver_id": driver["id"],
                "driver_name": driver["driver_name"],
                "driver_username": driver["driver_username"],
                "rating": driver["rating"],
                "total_deliveries": driver["total_deliveries"],
                "current_location": driver.get("current_location"),
                "vehicle_info": {
                    "type": vehicle.get("vehicle_type") if vehicle else "unknown",
                    "plate_number": vehicle.get("plate_number") if vehicle else "",
                    "make_model": vehicle.get("make_model") if vehicle else "",
                    "color": vehicle.get("color") if vehicle else ""
                },
                "status": driver["status"],
                "distance_km": round(distance_km, 2) if distance_km else None
            }
            driver_results.append(driver_result)
        
        # Sort by distance if available, then by rating
        driver_results.sort(key=lambda x: (x["distance_km"] or 999, -x["rating"]))
        
        return {"drivers": driver_results[:20]}  # Limit to 20 results
        
    except Exception as e:
        print(f"Error searching drivers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search drivers")

@app.post("/api/delivery/request-enhanced")
async def create_enhanced_delivery_request(request_data: DeliveryRequestCreate, current_user: dict = Depends(get_current_user)):
    """Create enhanced delivery request with multiple destinations and driver selection"""
    try:
        # Validate user can request delivery
        allowed_roles = ['agent', 'farmer', 'supplier', 'processor']
        if current_user.get('role') not in allowed_roles:
            raise HTTPException(status_code=403, detail="Only sellers can request delivery")
        
        # Calculate total distance for multiple destinations
        total_distance = 0.0
        for i in range(len(request_data.delivery_addresses)):
            total_distance += 10.0  # Mock distance calculation
        
        # Generate OTP
        import random
        otp = str(random.randint(100000, 999999))
        
        # Process delivery locations
        delivery_locations = []
        for i, address in enumerate(request_data.delivery_addresses):
            coords = request_data.delivery_coordinates[i] if i < len(request_data.delivery_coordinates) else {"lat": 0.0, "lng": 0.0}
            delivery_locations.append({
                "address": address,
                "lat": coords.get("lat", 0.0),
                "lng": coords.get("lng", 0.0),
                "order": i + 1
            })
        
        # Create delivery request
        delivery_request = {
            "id": str(uuid.uuid4()),
            "order_id": request_data.order_id,
            "order_type": request_data.order_type,
            "requester_username": current_user["username"],
            "pickup_location": {
                "address": request_data.pickup_address,
                "lat": request_data.pickup_coordinates.get("lat", 0.0) if request_data.pickup_coordinates else 0.0,
                "lng": request_data.pickup_coordinates.get("lng", 0.0) if request_data.pickup_coordinates else 0.0
            },
            "delivery_locations": delivery_locations,
            "total_quantity": request_data.total_quantity,
            "quantity_unit": request_data.quantity_unit,
            "distance_km": total_distance,
            "estimated_price": request_data.estimated_price,
            "product_details": request_data.product_details,
            "weight_kg": request_data.weight_kg,
            "special_instructions": request_data.special_instructions,
            "status": DeliveryStatus.PENDING,
            "delivery_otp": otp,
            "chat_messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # If preferred driver specified, assign directly
        if request_data.preferred_driver_username:
            preferred_driver = db.drivers.find_one({"driver_username": request_data.preferred_driver_username})
            if preferred_driver:
                delivery_request["preferred_driver_id"] = preferred_driver["id"]
        
        # Store in database
        db.delivery_requests.insert_one(delivery_request)
        
        return {
            "message": "Enhanced delivery request created successfully",
            "request_id": delivery_request["id"],
            "total_destinations": len(delivery_locations),
            "total_quantity": request_data.total_quantity,
            "quantity_unit": request_data.quantity_unit,
            "estimated_price": request_data.estimated_price,
            "total_distance_km": total_distance,
            "delivery_otp": otp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating enhanced delivery request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create delivery request")

@app.post("/api/delivery/{request_id}/message")
async def send_delivery_message(request_id: str, message_data: dict, current_user: dict = Depends(get_current_user)):
    """Send message in delivery chat"""
    try:
        # Find delivery request
        delivery_request = db.delivery_requests.find_one({"id": request_id})
        if not delivery_request:
            raise HTTPException(status_code=404, detail="Delivery request not found")
        
        # Determine sender type
        sender_type = "requester"
        if delivery_request.get("assigned_driver_id"):
            driver = db.drivers.find_one({"id": delivery_request["assigned_driver_id"]})
            if driver and driver["driver_username"] == current_user["username"]:
                sender_type = "driver"
        
        # Validate authorization
        if (sender_type == "requester" and current_user["username"] != delivery_request["requester_username"]) or \
           (sender_type == "driver" and current_user["username"] != driver.get("driver_username")):
            raise HTTPException(status_code=403, detail="Not authorized to send messages in this delivery")
        
        # Create message
        message = {
            "id": str(uuid.uuid4()),
            "delivery_request_id": request_id,
            "sender_username": current_user["username"],
            "sender_type": sender_type,
            "message_type": message_data.get("type", "text"),
            "content": message_data.get("content", ""),
            "location_data": message_data.get("location_data"),
            "timestamp": datetime.utcnow()
        }
        
        # Add message to delivery request
        db.delivery_requests.update_one(
            {"id": request_id},
            {
                "$push": {"chat_messages": message},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {"message": "Message sent successfully", "message_id": message["id"]}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending delivery message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@app.get("/api/delivery/{request_id}/messages")
async def get_delivery_messages(request_id: str, current_user: dict = Depends(get_current_user)):
    """Get all messages for a delivery request"""
    try:
        # Find delivery request
        delivery_request = db.delivery_requests.find_one({"id": request_id})
        if not delivery_request:
            raise HTTPException(status_code=404, detail="Delivery request not found")
        
        # Validate authorization
        is_requester = current_user["username"] == delivery_request["requester_username"]
        is_driver = False
        if delivery_request.get("assigned_driver_id"):
            driver = db.drivers.find_one({"id": delivery_request["assigned_driver_id"]})
            is_driver = driver and driver["driver_username"] == current_user["username"]
        
        if not is_requester and not is_driver:
            raise HTTPException(status_code=403, detail="Not authorized to view messages")
        
        # Get messages
        messages = delivery_request.get("chat_messages", [])
        
        # Format timestamps
        for message in messages:
            if isinstance(message.get("timestamp"), datetime):
                message["timestamp"] = message["timestamp"].isoformat()
        
        return {
            "messages": messages,
            "delivery_request": {
                "id": delivery_request["id"],
                "status": delivery_request["status"],
                "pickup_location": delivery_request["pickup_location"],
                "delivery_locations": delivery_request["delivery_locations"],
                "product_details": delivery_request["product_details"],
                "total_quantity": delivery_request["total_quantity"],
                "quantity_unit": delivery_request["quantity_unit"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting delivery messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@app.post("/api/drivers/location")
async def update_driver_location(location_data: dict, current_user: dict = Depends(get_current_user)):
    """Update driver's current location"""
    try:
        # Find driver
        driver = db.drivers.find_one({"driver_username": current_user["username"]})
        if not driver:
            raise HTTPException(status_code=404, detail="Driver profile not found")
        
        # Update location
        location = {
            "lat": location_data.get("lat"),
            "lng": location_data.get("lng"),
            "address": location_data.get("address", ""),
            "updated_at": datetime.utcnow()
        }
        
        db.drivers.update_one(
            {"driver_username": current_user["username"]},
            {
                "$set": {
                    "current_location": location,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Location updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating driver location: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update location")

@app.post("/api/orders/create")
async def create_order(order_data: OrderCreate, current_user: dict = Depends(get_current_user)):
    """Create a new order with enhanced quantity system and delivery options"""
    try:
        # Find the product
        product = db.products.find_one({"id": order_data.product_id}) or db.preorders.find_one({"id": order_data.product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Validate delivery method against supplier preferences
        if order_data.delivery_method == "dropoff":
            if not product.get("supports_dropoff_delivery", True):
                raise HTTPException(status_code=400, detail="This supplier does not support drop-off delivery. Please choose shipping address.")
        elif order_data.delivery_method in ["platform", "offline"] and order_data.shipping_address:
            if not product.get("supports_shipping_delivery", True):
                raise HTTPException(status_code=400, detail="This supplier does not support shipping delivery. Please choose a drop-off location.")
        
        # Handle drop-off location validation and details
        dropoff_location_details = None
        if order_data.delivery_method == "dropoff":
            if not order_data.dropoff_location_id:
                raise HTTPException(status_code=400, detail="Drop-off location is required for drop-off delivery")
            
            # Get drop-off location details
            dropoff_location = dropoff_locations_collection.find_one({"id": order_data.dropoff_location_id, "is_active": True})
            if not dropoff_location:
                raise HTTPException(status_code=404, detail="Drop-off location not found or inactive")
            
            # Create snapshot of location details for order
            dropoff_location_details = {
                "id": dropoff_location["id"],
                "name": dropoff_location["name"],
                "address": dropoff_location["address"],
                "city": dropoff_location["city"],
                "state": dropoff_location["state"],
                "contact_person": dropoff_location.get("contact_person"),
                "contact_phone": dropoff_location.get("contact_phone"),
                "operating_hours": dropoff_location.get("operating_hours")
            }
        
        # Calculate total amount including delivery costs
        unit_price = product.get("price_per_unit", 0)
        product_total = order_data.quantity * unit_price
        
        # Add delivery cost based on delivery method and supplier preferences
        delivery_cost = 0.0
        if order_data.delivery_method == "dropoff":
            delivery_cost = product.get("delivery_cost_dropoff", 0.0)
        elif order_data.delivery_method in ["platform", "offline"] and order_data.shipping_address:
            delivery_cost = product.get("delivery_cost_shipping", 0.0)
        
        total_amount = product_total + delivery_cost
        
        # Determine payment timing based on delivery method
        payment_timing = "after_delivery" if order_data.delivery_method == "offline" else "during_transit"
        
        # Create order
        order = {
            "id": str(uuid.uuid4()),
            "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
            "buyer_username": current_user["username"],
            "seller_username": product.get("seller_username", ""),
            "product_details": {
                "product_id": order_data.product_id,
                "name": product.get("product_name") or product.get("crop_type", ""),
                "category": product.get("product_category") or product.get("category", ""),
                "description": product.get("description", "")
            },
            "quantity": order_data.quantity,
            "unit": order_data.unit,
            "unit_specification": order_data.unit_specification,
            "unit_price": unit_price,
            "product_total": product_total,  # Product cost without delivery
            "delivery_cost": delivery_cost,  # Separate delivery cost
            "total_amount": total_amount,  # Total including delivery
            "delivery_method": order_data.delivery_method,
            "delivery_status": "pending" if order_data.delivery_method == "offline" else "",
            "shipping_address": order_data.shipping_address,
            "dropoff_location_id": order_data.dropoff_location_id,
            "dropoff_location_details": dropoff_location_details,
            "agent_fee_percentage": 0.05,
            "payment_timing": payment_timing,
            "status": OrderStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Store order
        db.orders.insert_one(order)
        
        # Prepare response with delivery info and cost breakdown
        delivery_info = {
            "method": order_data.delivery_method,
            "cost": delivery_cost,
            "is_free": delivery_cost == 0.0,
            "payment_timing": payment_timing
        }
        
        if dropoff_location_details:
            delivery_info["dropoff_location"] = {
                "name": dropoff_location_details["name"],
                "address": dropoff_location_details["address"],
                "city": dropoff_location_details["city"],
                "state": dropoff_location_details["state"]
            }
        
        return {
            "message": "Order created successfully",
            "order_id": order["order_id"],
            "cost_breakdown": {
                "product_total": product_total,
                "delivery_cost": delivery_cost,
                "total_amount": total_amount
            },
            "total_amount": total_amount,  # Keep for backward compatibility
            "delivery_info": delivery_info,
            "quantity_display": f"{order_data.quantity} {order_data.unit}" + (f" ({order_data.unit_specification})" if order_data.unit_specification else ""),
            "agent_fee_info": {
                "percentage": "5%",
                "amount": total_amount * 0.05,
                "payment_timing": payment_timing
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create order")

@app.get("/api/products/{product_id}/delivery-options")
async def get_product_delivery_options(product_id: str):
    """Get delivery options for a specific product"""
    try:
        product = db.products.find_one({"id": product_id}) or db.preorders.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        delivery_options = {
            "product_id": product_id,
            "supports_dropoff_delivery": product.get("supports_dropoff_delivery", True),
            "supports_shipping_delivery": product.get("supports_shipping_delivery", True),
            "delivery_costs": {
                "dropoff": {
                    "cost": product.get("delivery_cost_dropoff", 0.0),
                    "is_free": product.get("delivery_cost_dropoff", 0.0) == 0.0
                },
                "shipping": {
                    "cost": product.get("delivery_cost_shipping", 0.0),
                    "is_free": product.get("delivery_cost_shipping", 0.0) == 0.0
                }
            },
            "delivery_notes": product.get("delivery_notes")
        }
        
        return delivery_options
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting delivery options: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get delivery options")

@app.put("/api/products/{product_id}/delivery-options")
async def update_product_delivery_options(
    product_id: str,
    delivery_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update delivery options for a product (suppliers only)"""
    try:
        # Check if product exists and user owns it
        product = db.products.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.get("seller_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="You can only update delivery options for your own products")
        
        # Validate at least one delivery method is supported
        supports_dropoff = delivery_data.get("supports_dropoff_delivery", True)
        supports_shipping = delivery_data.get("supports_shipping_delivery", True)
        
        if not supports_dropoff and not supports_shipping:
            raise HTTPException(status_code=400, detail="At least one delivery method must be supported")
        
        # Update product delivery options
        update_data = {
            "supports_dropoff_delivery": supports_dropoff,
            "supports_shipping_delivery": supports_shipping,
            "delivery_cost_dropoff": max(0.0, delivery_data.get("delivery_cost_dropoff", 0.0)),
            "delivery_cost_shipping": max(0.0, delivery_data.get("delivery_cost_shipping", 0.0)),
            "delivery_notes": delivery_data.get("delivery_notes", "").strip() or None,
            "updated_at": datetime.utcnow()
        }
        
        db.products.update_one({"id": product_id}, {"$set": update_data})
        
        return {"message": "Delivery options updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating delivery options: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update delivery options")

@app.put("/api/orders/{order_id}/status")
async def update_order_status(order_id: str, status_update: OrderStatusUpdate, current_user: dict = Depends(get_current_user)):
    """Update order status - for sellers managing offline deliveries"""
    try:
        # Find the order
        order = db.orders.find_one({"order_id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if user is the seller
        if order["seller_username"] != current_user["username"]:
            raise HTTPException(status_code=403, detail="Only the seller can update order status")
        
        # Update order
        update_data = {
            "status": status_update.status,
            "updated_at": datetime.utcnow()
        }
        
        if status_update.delivery_status:
            update_data["delivery_status"] = status_update.delivery_status
        
        if status_update.status == OrderStatus.DELIVERED:
            update_data["delivered_at"] = datetime.utcnow()
        
        db.orders.update_one(
            {"order_id": order_id},
            {"$set": update_data}
        )
        
        return {
            "message": f"Order status updated to {status_update.status}",
            "order_id": order_id,
            "status": status_update.status,
            "delivery_status": status_update.delivery_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating order status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update order status")

@app.get("/api/orders/my-orders")
async def get_my_orders(order_type: str = "buyer", current_user: dict = Depends(get_current_user)):
    """Get user's orders (as buyer or seller)"""
    try:
        if order_type == "buyer":
            query = {"buyer_username": current_user["username"]}
        elif order_type == "seller":
            query = {"seller_username": current_user["username"]}
        else:
            raise HTTPException(status_code=400, detail="order_type must be 'buyer' or 'seller'")
        
        orders = list(db.orders.find(query).sort("created_at", -1))
        
        # Clean up response
        for order in orders:
            order.pop('_id', None)
            if order.get("created_at"):
                order["created_at"] = order["created_at"].isoformat()
            if order.get("updated_at"):
                order["updated_at"] = order["updated_at"].isoformat()
            if order.get("delivered_at"):
                order["delivered_at"] = order["delivered_at"].isoformat()
        
        return {"orders": orders}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get orders")

@app.get("/api/orders/units")
async def get_available_units():
    """Get all available units with examples"""
    return {
        "units": [
            {"value": "kg", "label": "Kilograms", "examples": ["50kg", "100kg"]},
            {"value": "g", "label": "Grams", "examples": ["500g", "1000g"]},
            {"value": "ton", "label": "Tons", "examples": ["1 ton", "5 tons"]},
            {"value": "pieces", "label": "Pieces", "examples": ["10 pieces", "50 pieces"]},
            {"value": "liters", "label": "Liters", "examples": ["5 liters", "20 liters"]},
            {"value": "bags", "label": "Bags", "examples": ["100kg per bag", "50kg per bag"]},
            {"value": "crates", "label": "Crates", "examples": ["24 bottles per crate", "50 pieces per crate"]},
            {"value": "gallons", "label": "Gallons", "examples": ["5 litres per gallon", "4 litres per gallon"]}
        ]
    }

# Drop-off Location Management Endpoints
@app.post("/api/dropoff-locations")
async def create_dropoff_location(
    location_data: DropoffLocationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new drop-off location (agents and sellers only)"""
    try:
        # Validate user can create drop-off locations
        allowed_roles = ['agent', 'farmer', 'supplier_farm_inputs', 'supplier_food_produce', 'processor']
        if current_user.get('role') not in allowed_roles:
            raise HTTPException(status_code=403, detail="Only agents and sellers can create drop-off locations")
        
        # Create drop-off location document
        location = {
            "id": str(uuid.uuid4()),
            "name": location_data.name,
            "address": location_data.address,
            "city": location_data.city,
            "state": location_data.state,
            "country": location_data.country,
            "coordinates": location_data.coordinates,
            "contact_person": location_data.contact_person,
            "contact_phone": location_data.contact_phone,
            "operating_hours": location_data.operating_hours,
            "description": location_data.description,
            "agent_username": current_user["username"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Store in database
        dropoff_locations_collection.insert_one(location)
        
        return {
            "message": "Drop-off location created successfully",
            "location_id": location["id"],
            "location": {
                "id": location["id"],
                "name": location["name"],
                "address": location["address"],
                "city": location["city"],
                "state": location["state"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating drop-off location: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create drop-off location")

@app.get("/api/dropoff-locations")
async def get_dropoff_locations(
    state: Optional[str] = None,
    city: Optional[str] = None,
    active_only: bool = True,
    page: int = 1,
    limit: int = 50
):
    """Get available drop-off locations with optional filtering"""
    try:
        # Build filter query
        query = {}
        
        if active_only:
            query["is_active"] = True
            
        if state:
            query["state"] = {"$regex": state, "$options": "i"}
            
        if city:
            query["city"] = {"$regex": city, "$options": "i"}
        
        # Calculate skip for pagination
        skip = (page - 1) * limit
        
        # Get locations with pagination
        locations = list(dropoff_locations_collection.find(query).sort("state", 1).sort("city", 1).sort("name", 1).skip(skip).limit(limit))
        
        # Get total count for pagination
        total_count = dropoff_locations_collection.count_documents(query)
        
        # Clean up response
        for location in locations:
            location.pop('_id', None)
            if isinstance(location.get("created_at"), datetime):
                location["created_at"] = location["created_at"].isoformat()
            if isinstance(location.get("updated_at"), datetime):
                location["updated_at"] = location["updated_at"].isoformat()
        
        return {
            "locations": locations,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        print(f"Error getting drop-off locations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get drop-off locations")

@app.get("/api/dropoff-locations/my-locations")
async def get_my_dropoff_locations(current_user: dict = Depends(get_current_user)):
    """Get current agent's created drop-off locations"""
    try:
        # Validate user can manage drop-off locations
        allowed_roles = ['agent', 'farmer', 'supplier_farm_inputs', 'supplier_food_produce', 'processor']
        if current_user.get('role') not in allowed_roles:
            raise HTTPException(status_code=403, detail="Only agents and sellers can view their drop-off locations")
        
        locations = list(dropoff_locations_collection.find({"agent_username": current_user["username"]}).sort("created_at", -1))
        
        # Clean up response
        for location in locations:
            location.pop('_id', None)
            if isinstance(location.get("created_at"), datetime):
                location["created_at"] = location["created_at"].isoformat()
            if isinstance(location.get("updated_at"), datetime):
                location["updated_at"] = location["updated_at"].isoformat()
        
        return {
            "locations": locations,
            "total_count": len(locations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting user drop-off locations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user drop-off locations")

@app.get("/api/dropoff-locations/{location_id}")
async def get_dropoff_location(location_id: str):
    """Get detailed information about a specific drop-off location"""
    try:
        location = dropoff_locations_collection.find_one({"id": location_id})
        if not location:
            raise HTTPException(status_code=404, detail="Drop-off location not found")
        
        if not location.get("is_active", False):
            raise HTTPException(status_code=404, detail="Drop-off location is not active")
        
        # Clean up response
        location.pop('_id', None)
        if isinstance(location.get("created_at"), datetime):
            location["created_at"] = location["created_at"].isoformat()
        if isinstance(location.get("updated_at"), datetime):
            location["updated_at"] = location["updated_at"].isoformat()
        
        return location
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting drop-off location details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get drop-off location details")

@app.put("/api/dropoff-locations/{location_id}")
async def update_dropoff_location(
    location_id: str,
    location_data: DropoffLocationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a drop-off location (only by creator)"""
    try:
        # Find the location
        location = dropoff_locations_collection.find_one({"id": location_id})
        if not location:
            raise HTTPException(status_code=404, detail="Drop-off location not found")
        
        # Check ownership
        if location["agent_username"] != current_user["username"]:
            raise HTTPException(status_code=403, detail="You can only update your own drop-off locations")
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        
        for field, value in location_data.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        # Update location
        dropoff_locations_collection.update_one(
            {"id": location_id},
            {"$set": update_data}
        )
        
        return {"message": "Drop-off location updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating drop-off location: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update drop-off location")

@app.delete("/api/dropoff-locations/{location_id}")
async def delete_dropoff_location(
    location_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Deactivate a drop-off location (only by creator)"""
    try:
        # Find the location
        location = dropoff_locations_collection.find_one({"id": location_id})
        if not location:
            raise HTTPException(status_code=404, detail="Drop-off location not found")
        
        # Check ownership
        if location["agent_username"] != current_user["username"]:
            raise HTTPException(status_code=403, detail="You can only delete your own drop-off locations")
        
        # Soft delete by marking as inactive
        dropoff_locations_collection.update_one(
            {"id": location_id},
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Drop-off location deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting drop-off location: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete drop-off location")

@app.get("/api/dropoff-locations/states-cities")
async def get_dropoff_states_cities():
    """Get available states and cities for drop-off locations"""
    try:
        # Get distinct states and cities
        states = list(dropoff_locations_collection.distinct("state", {"is_active": True}))
        cities_by_state = {}
        
        for state in states:
            cities = list(dropoff_locations_collection.distinct("city", {"state": state, "is_active": True}))
            cities_by_state[state] = sorted(cities)
        
        return {
            "states": sorted(states),
            "cities_by_state": cities_by_state
        }
        
    except Exception as e:
        print(f"Error getting states and cities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get states and cities")

# ==================== DIGITAL WALLET SYSTEM ENDPOINTS ====================

@app.get("/api/wallet/summary")
async def get_wallet_summary(current_user: dict = Depends(get_current_user)):
    """Get comprehensive wallet summary for the current user"""
    try:
        user_id = current_user["id"]
        
        # Get current balance from user record
        user = users_collection.find_one({"id": user_id})
        current_balance = user.get("wallet_balance", 0.0) if user else 0.0
        
        # Calculate transaction statistics
        all_transactions = list(wallet_transactions_collection.find({
            "user_id": user_id,
            "status": TransactionStatus.COMPLETED
        }))
        
        total_funded = sum(t["amount"] for t in all_transactions if t["transaction_type"] in [TransactionType.WALLET_FUNDING, TransactionType.GIFT_CARD_REDEMPTION])
        total_spent = sum(t["amount"] for t in all_transactions if t["transaction_type"] in [TransactionType.ORDER_PAYMENT, TransactionType.GIFT_CARD_PURCHASE])
        total_withdrawn = sum(t["amount"] for t in all_transactions if t["transaction_type"] == TransactionType.WALLET_WITHDRAWAL)
        
        # Pending transactions
        pending_count = wallet_transactions_collection.count_documents({
            "user_id": user_id,
            "status": TransactionStatus.PENDING
        })
        
        # Last transaction
        last_transaction = wallet_transactions_collection.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        # Linked accounts
        linked_accounts_count = bank_accounts_collection.count_documents({"user_id": user_id})
        
        # Gift cards statistics
        gift_cards_purchased = gift_cards_collection.count_documents({"purchaser_id": user_id})
        gift_cards_redeemed = gift_cards_collection.count_documents({"redeemed_by_id": user_id})
        
        # Security status
        wallet_security = wallet_security_collection.find_one({"user_id": user_id})
        security_status = {
            "pin_set": bool(wallet_security and wallet_security.get("transaction_pin")),
            "pin_locked": bool(wallet_security and wallet_security.get("pin_locked_until") and wallet_security["pin_locked_until"] > datetime.utcnow()),
            "two_factor_enabled": bool(wallet_security and wallet_security.get("two_factor_enabled")),
            "daily_limit": wallet_security.get("daily_limit", 50000.0) if wallet_security else 50000.0,
            "monthly_limit": wallet_security.get("monthly_limit", 1000000.0) if wallet_security else 1000000.0
        }
        
        return {
            "user_id": user_id,
            "username": current_user["username"],
            "balance": current_balance,
            "total_funded": total_funded,
            "total_spent": total_spent,
            "total_withdrawn": total_withdrawn,
            "pending_transactions": pending_count,
            "last_transaction_date": last_transaction["created_at"].isoformat() if last_transaction else None,
            "security_status": security_status,
            "linked_accounts": linked_accounts_count,
            "gift_cards_purchased": gift_cards_purchased,
            "gift_cards_redeemed": gift_cards_redeemed
        }
        
    except Exception as e:
        print(f"Error getting wallet summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get wallet summary")

@app.post("/api/wallet/fund")
async def fund_wallet(
    transaction_data: WalletTransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Fund user wallet (mock implementation)"""
    try:
        if transaction_data.transaction_type != TransactionType.WALLET_FUNDING:
            raise HTTPException(status_code=400, detail="Invalid transaction type for funding")
        
        user_id = current_user["id"]
        amount = transaction_data.amount
        
        # Get current balance
        user = users_collection.find_one({"id": user_id})
        current_balance = user.get("wallet_balance", 0.0) if user else 0.0
        
        # Create transaction record
        transaction = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "username": current_user["username"],
            "transaction_type": TransactionType.WALLET_FUNDING,
            "amount": amount,
            "balance_before": current_balance,
            "balance_after": current_balance + amount,
            "status": TransactionStatus.COMPLETED,  # Mock: instantly successful
            "reference": f"FUND-{uuid.uuid4().hex[:12].upper()}",
            "description": transaction_data.description,
            "funding_method": transaction_data.funding_method,
            "metadata": transaction_data.metadata or {},
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow()
        }
        
        # Insert transaction
        wallet_transactions_collection.insert_one(transaction)
        
        # Update user balance
        users_collection.update_one(
            {"id": user_id},
            {"$set": {"wallet_balance": current_balance + amount}}
        )
        
        return {
            "message": "Wallet funded successfully",
            "transaction_id": transaction["id"],
            "reference": transaction["reference"],
            "amount": amount,
            "new_balance": current_balance + amount,
            "funding_method": transaction_data.funding_method
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error funding wallet: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fund wallet")

@app.post("/api/wallet/withdraw")
async def withdraw_from_wallet(
    withdrawal_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Withdraw from wallet to bank account (mock implementation)"""
    try:
        amount = withdrawal_data.get("amount")
        bank_account_id = withdrawal_data.get("bank_account_id")
        description = withdrawal_data.get("description", "Wallet withdrawal")
        
        if not amount or amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid withdrawal amount")
        
        if not bank_account_id:
            raise HTTPException(status_code=400, detail="Bank account is required for withdrawal")
        
        user_id = current_user["id"]
        
        # Verify bank account ownership
        bank_account = bank_accounts_collection.find_one({
            "id": bank_account_id,
            "user_id": user_id
        })
        
        if not bank_account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        # Get current balance
        user = users_collection.find_one({"id": user_id})
        current_balance = user.get("wallet_balance", 0.0) if user else 0.0
        
        if current_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        
        # Create transaction record
        transaction = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "username": current_user["username"],
            "transaction_type": TransactionType.WALLET_WITHDRAWAL,
            "amount": amount,
            "balance_before": current_balance,
            "balance_after": current_balance - amount,
            "status": TransactionStatus.COMPLETED,  # Mock: instantly successful
            "reference": f"WTHD-{uuid.uuid4().hex[:12].upper()}",
            "description": description,
            "metadata": {
                "bank_account": {
                    "account_name": bank_account["account_name"],
                    "account_number": bank_account["account_number"],
                    "bank_name": bank_account["bank_name"]
                }
            },
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow()
        }
        
        # Insert transaction
        wallet_transactions_collection.insert_one(transaction)
        
        # Update user balance
        users_collection.update_one(
            {"id": user_id},
            {"$set": {"wallet_balance": current_balance - amount}}
        )
        
        return {
            "message": "Withdrawal successful",
            "transaction_id": transaction["id"],
            "reference": transaction["reference"],
            "amount": amount,
            "new_balance": current_balance - amount,
            "bank_account": f"{bank_account['account_name']} - {bank_account['bank_name']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process withdrawal")

@app.get("/api/wallet/transactions")
async def get_wallet_transactions(
    transaction_type: Optional[TransactionType] = None,
    status: Optional[TransactionStatus] = None,
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user wallet transactions with filtering and pagination"""
    try:
        user_id = current_user["id"]
        
        # Build query
        query = {"user_id": user_id}
        if transaction_type:
            query["transaction_type"] = transaction_type
        if status:
            query["status"] = status
        
        # Get total count
        total_count = wallet_transactions_collection.count_documents(query)
        
        # Get transactions
        skip = (page - 1) * limit
        transactions = list(wallet_transactions_collection.find(query)
                          .sort("created_at", -1)
                          .skip(skip)
                          .limit(limit))
        
        # Clean up response
        for transaction in transactions:
            transaction.pop('_id', None)
            if isinstance(transaction.get("created_at"), datetime):
                transaction["created_at"] = transaction["created_at"].isoformat()
            if isinstance(transaction.get("completed_at"), datetime):
                transaction["completed_at"] = transaction["completed_at"].isoformat()
        
        return {
            "transactions": transactions,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit if total_count > 0 else 0
        }
        
    except Exception as e:
        print(f"Error getting wallet transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get wallet transactions")

# ==================== BANK ACCOUNT MANAGEMENT ====================

@app.post("/api/wallet/bank-accounts")
async def add_bank_account(
    account_data: BankAccountCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a bank account for wallet withdrawals (mock implementation)"""
    try:
        user_id = current_user["id"]
        
        # Check if account already exists
        existing_account = bank_accounts_collection.find_one({
            "user_id": user_id,
            "account_number": account_data.account_number
        })
        
        if existing_account:
            raise HTTPException(status_code=400, detail="Bank account already exists")
        
        # If this is set as primary, remove primary status from other accounts
        if account_data.is_primary:
            bank_accounts_collection.update_many(
                {"user_id": user_id},
                {"$set": {"is_primary": False}}
            )
        
        # Create bank account record
        bank_account = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "account_name": account_data.account_name,
            "account_number": account_data.account_number,
            "bank_name": account_data.bank_name,
            "bank_code": account_data.bank_code,
            "is_primary": account_data.is_primary,
            "is_verified": True,  # Mock: auto-verify for demo
            "created_at": datetime.utcnow()
        }
        
        bank_accounts_collection.insert_one(bank_account)
        
        return {
            "message": "Bank account added successfully",
            "account_id": bank_account["id"],
            "account_name": account_data.account_name,
            "account_number": account_data.account_number,
            "bank_name": account_data.bank_name,
            "is_verified": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding bank account: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add bank account")

@app.get("/api/wallet/bank-accounts")
async def get_user_bank_accounts(current_user: dict = Depends(get_current_user)):
    """Get user's linked bank accounts"""
    try:
        user_id = current_user["id"]
        
        accounts = list(bank_accounts_collection.find({"user_id": user_id}))
        
        # Clean up response
        for account in accounts:
            account.pop('_id', None)
            if isinstance(account.get("created_at"), datetime):
                account["created_at"] = account["created_at"].isoformat()
            
            # Mask account number for security (show only last 4 digits)
            if len(account["account_number"]) >= 4:
                account["masked_account_number"] = "*" * (len(account["account_number"]) - 4) + account["account_number"][-4:]
            else:
                account["masked_account_number"] = account["account_number"]
        
        return {
            "accounts": accounts,
            "total_accounts": len(accounts)
        }
        
    except Exception as e:
        print(f"Error getting bank accounts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get bank accounts")

@app.delete("/api/wallet/bank-accounts/{account_id}")
async def remove_bank_account(
    account_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a bank account"""
    try:
        user_id = current_user["id"]
        
        # Find and verify ownership
        account = bank_accounts_collection.find_one({
            "id": account_id,
            "user_id": user_id
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        # Delete the account
        bank_accounts_collection.delete_one({"id": account_id})
        
        return {
            "message": "Bank account removed successfully",
            "account_id": account_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error removing bank account: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove bank account")

# ==================== GIFT CARD SYSTEM ====================

@app.post("/api/wallet/gift-cards")
async def create_gift_card(
    gift_card_data: GiftCardCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create/purchase a gift card"""
    try:
        user_id = current_user["id"]
        amount = gift_card_data.amount
        
        # Check wallet balance
        user = users_collection.find_one({"id": user_id})
        current_balance = user.get("wallet_balance", 0.0) if user else 0.0
        
        if current_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance to purchase gift card")
        
        # Create gift card
        gift_card = {
            "id": str(uuid.uuid4()),
            "card_code": f"GIFT-{uuid.uuid4().hex[:8].upper()}",
            "amount": amount,
            "balance": amount,
            "status": GiftCardStatus.ACTIVE,
            "purchaser_id": user_id,
            "purchaser_username": current_user["username"],
            "recipient_email": gift_card_data.recipient_email,
            "recipient_name": gift_card_data.recipient_name,
            "message": gift_card_data.message,
            "expiry_date": datetime.utcnow() + timedelta(days=365),
            "created_at": datetime.utcnow(),
            "redeemed_at": None,
            "redeemed_by_id": None,
            "redeemed_by_username": None
        }
        
        gift_cards_collection.insert_one(gift_card)
        
        # Create transaction record for purchase
        transaction = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "username": current_user["username"],
            "transaction_type": TransactionType.GIFT_CARD_PURCHASE,
            "amount": amount,
            "balance_before": current_balance,
            "balance_after": current_balance - amount,
            "status": TransactionStatus.COMPLETED,
            "reference": f"GIFT-{uuid.uuid4().hex[:12].upper()}",
            "description": f"Gift card purchase - {gift_card['card_code']}",
            "gift_card_id": gift_card["id"],
            "metadata": {
                "gift_card_code": gift_card["card_code"],
                "recipient_email": gift_card_data.recipient_email,
                "recipient_name": gift_card_data.recipient_name
            },
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow()
        }
        
        wallet_transactions_collection.insert_one(transaction)
        
        # Update user balance
        users_collection.update_one(
            {"id": user_id},
            {"$set": {"wallet_balance": current_balance - amount}}
        )
        
        return {
            "message": "Gift card created successfully",
            "gift_card": {
                "id": gift_card["id"],
                "card_code": gift_card["card_code"],
                "amount": amount,
                "expiry_date": gift_card["expiry_date"].isoformat(),
                "recipient_email": gift_card_data.recipient_email,
                "recipient_name": gift_card_data.recipient_name,
                "message": gift_card_data.message
            },
            "transaction_id": transaction["id"],
            "new_balance": current_balance - amount
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating gift card: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create gift card")

@app.post("/api/wallet/gift-cards/redeem")
async def redeem_gift_card(
    redeem_data: GiftCardRedeem,
    current_user: dict = Depends(get_current_user)
):
    """Redeem a gift card to wallet balance"""
    try:
        user_id = current_user["id"]
        card_code = redeem_data.card_code.upper()
        
        # Find gift card
        gift_card = gift_cards_collection.find_one({"card_code": card_code})
        
        if not gift_card:
            raise HTTPException(status_code=404, detail="Gift card not found")
        
        if gift_card["status"] != GiftCardStatus.ACTIVE:
            raise HTTPException(status_code=400, detail=f"Gift card is {gift_card['status']} and cannot be redeemed")
        
        if gift_card["expiry_date"] < datetime.utcnow():
            # Mark as expired
            gift_cards_collection.update_one(
                {"id": gift_card["id"]},
                {"$set": {"status": GiftCardStatus.EXPIRED}}
            )
            raise HTTPException(status_code=400, detail="Gift card has expired")
        
        # Check if user is trying to redeem their own gift card
        if gift_card["purchaser_id"] == user_id and not gift_card.get("recipient_email"):
            raise HTTPException(status_code=400, detail="Cannot redeem your own gift card unless it was sent to an email")
        
        # Determine redemption amount
        available_balance = gift_card["balance"]
        redemption_amount = redeem_data.amount if redeem_data.amount else available_balance
        
        if redemption_amount > available_balance:
            raise HTTPException(status_code=400, detail=f"Insufficient gift card balance. Available: ₦{available_balance}")
        
        if redemption_amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid redemption amount")
        
        # Get current user balance
        user = users_collection.find_one({"id": user_id})
        current_balance = user.get("wallet_balance", 0.0) if user else 0.0
        
        # Update gift card
        new_gift_card_balance = available_balance - redemption_amount
        gift_card_updates = {
            "balance": new_gift_card_balance,
            "redeemed_by_id": user_id,
            "redeemed_by_username": current_user["username"]
        }
        
        # If fully redeemed, mark as redeemed
        if new_gift_card_balance == 0:
            gift_card_updates["status"] = GiftCardStatus.REDEEMED
            gift_card_updates["redeemed_at"] = datetime.utcnow()
        
        gift_cards_collection.update_one(
            {"id": gift_card["id"]},
            {"$set": gift_card_updates}
        )
        
        # Create transaction record for redemption
        transaction = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "username": current_user["username"],
            "transaction_type": TransactionType.GIFT_CARD_REDEMPTION,
            "amount": redemption_amount,
            "balance_before": current_balance,
            "balance_after": current_balance + redemption_amount,
            "status": TransactionStatus.COMPLETED,
            "reference": f"REDEEM-{uuid.uuid4().hex[:12].upper()}",
            "description": f"Gift card redemption - {card_code}",
            "gift_card_id": gift_card["id"],
            "metadata": {
                "gift_card_code": card_code,
                "original_purchaser": gift_card["purchaser_username"],
                "redemption_amount": redemption_amount,
                "remaining_balance": new_gift_card_balance
            },
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow()
        }
        
        wallet_transactions_collection.insert_one(transaction)
        
        # Update user balance
        users_collection.update_one(
            {"id": user_id},
            {"$set": {"wallet_balance": current_balance + redemption_amount}}
        )
        
        return {
            "message": "Gift card redeemed successfully",
            "redeemed_amount": redemption_amount,
            "gift_card_remaining_balance": new_gift_card_balance,
            "new_wallet_balance": current_balance + redemption_amount,
            "transaction_id": transaction["id"],
            "fully_redeemed": new_gift_card_balance == 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error redeeming gift card: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to redeem gift card")

@app.get("/api/wallet/gift-cards/my-cards")
async def get_my_gift_cards(
    status: Optional[GiftCardStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get gift cards purchased by the current user"""
    try:
        user_id = current_user["id"]
        
        # Build query
        query = {"purchaser_id": user_id}
        if status:
            query["status"] = status
        
        gift_cards = list(gift_cards_collection.find(query).sort("created_at", -1))
        
        # Clean up response
        for card in gift_cards:
            card.pop('_id', None)
            if isinstance(card.get("created_at"), datetime):
                card["created_at"] = card["created_at"].isoformat()
            if isinstance(card.get("expiry_date"), datetime):
                card["expiry_date"] = card["expiry_date"].isoformat()
            if isinstance(card.get("redeemed_at"), datetime):
                card["redeemed_at"] = card["redeemed_at"].isoformat()
        
        return {
            "gift_cards": gift_cards,
            "total_cards": len(gift_cards)
        }
        
    except Exception as e:
        print(f"Error getting gift cards: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get gift cards")

@app.get("/api/wallet/gift-cards/{card_code}")
async def get_gift_card_details(card_code: str):
    """Get gift card details (for checking validity before redemption)"""
    try:
        card_code = card_code.upper()
        gift_card = gift_cards_collection.find_one({"card_code": card_code})
        
        if not gift_card:
            raise HTTPException(status_code=404, detail="Gift card not found")
        
        # Public information only
        card_info = {
            "card_code": gift_card["card_code"],
            "amount": gift_card["amount"],
            "balance": gift_card["balance"],
            "status": gift_card["status"],
            "expiry_date": gift_card["expiry_date"].isoformat() if isinstance(gift_card.get("expiry_date"), datetime) else None,
            "is_expired": gift_card["expiry_date"] < datetime.utcnow() if gift_card.get("expiry_date") else False,
            "recipient_name": gift_card.get("recipient_name"),
            "message": gift_card.get("message")
        }
        
        return card_info
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting gift card details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get gift card details")

# ==================== WALLET SECURITY ====================

@app.post("/api/wallet/security/set-pin")
async def set_transaction_pin(
    pin_data: WalletPinCreate,
    current_user: dict = Depends(get_current_user)
):
    """Set transaction PIN for wallet security"""
    try:
        user_id = current_user["id"]
        hashed_pin = hash_password(pin_data.pin)
        
        # Check if security record exists
        existing_security = wallet_security_collection.find_one({"user_id": user_id})
        
        if existing_security:
            # Update existing record
            wallet_security_collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "transaction_pin": hashed_pin,
                    "pin_attempts": 0,
                    "pin_locked_until": None,
                    "updated_at": datetime.utcnow()
                }}
            )
        else:
            # Create new security record
            security_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "transaction_pin": hashed_pin,
                "pin_attempts": 0,
                "pin_locked_until": None,
                "two_factor_enabled": False,
                "daily_limit": 50000.0,
                "monthly_limit": 1000000.0,
                "created_at": datetime.utcnow(),
                "updated_at": None
            }
            
            wallet_security_collection.insert_one(security_record)
        
        return {
            "message": "Transaction PIN set successfully",
            "pin_set": True
        }
        
    except Exception as e:
        print(f"Error setting transaction PIN: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to set transaction PIN")

@app.post("/api/wallet/security/verify-pin")
async def verify_transaction_pin(
    pin_data: WalletPinVerify,
    current_user: dict = Depends(get_current_user)
):
    """Verify transaction PIN"""
    try:
        user_id = current_user["id"]
        
        security_record = wallet_security_collection.find_one({"user_id": user_id})
        
        if not security_record or not security_record.get("transaction_pin"):
            raise HTTPException(status_code=400, detail="Transaction PIN not set")
        
        # Check if PIN is locked
        if security_record.get("pin_locked_until") and security_record["pin_locked_until"] > datetime.utcnow():
            raise HTTPException(status_code=423, detail="PIN is temporarily locked due to multiple failed attempts")
        
        # Verify PIN
        if verify_password(pin_data.pin, security_record["transaction_pin"]):
            # Reset failed attempts on successful verification
            wallet_security_collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "pin_attempts": 0,
                    "pin_locked_until": None,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {
                "message": "PIN verified successfully",
                "verified": True
            }
        else:
            # Increment failed attempts
            attempts = security_record.get("pin_attempts", 0) + 1
            updates = {
                "pin_attempts": attempts,
                "updated_at": datetime.utcnow()
            }
            
            # Lock PIN after 5 failed attempts for 30 minutes
            if attempts >= 5:
                updates["pin_locked_until"] = datetime.utcnow() + timedelta(minutes=30)
            
            wallet_security_collection.update_one(
                {"user_id": user_id},
                {"$set": updates}
            )
            
            if attempts >= 5:
                raise HTTPException(status_code=423, detail="PIN locked for 30 minutes due to multiple failed attempts")
            else:
                raise HTTPException(status_code=400, detail=f"Invalid PIN. {5 - attempts} attempts remaining")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error verifying PIN: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify PIN")

# ==================== ENHANCED SELLER DASHBOARD ENDPOINTS ====================

@app.get("/api/seller/dashboard/analytics")
async def get_seller_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive seller analytics and metrics"""
    try:
        seller_id = current_user["id"]
        seller_username = current_user["username"]
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get seller's products (both regular and pre-orders)
        products = list(db.products.find({"seller_id": seller_id}))
        preorders = list(db.preorders.find({"seller_id": seller_id}))
        all_products = products + preorders
        product_ids = [p["id"] for p in all_products]
        
        # Get orders for this seller's products
        orders_query = {
            "product_details.product_id": {"$in": product_ids},
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        orders = list(db.orders.find(orders_query))
        
        # Revenue calculations
        total_revenue = sum(order.get("total_amount", 0) for order in orders if order.get("status") in ["completed", "delivered"])
        pending_revenue = sum(order.get("total_amount", 0) for order in orders if order.get("status") in ["pending", "confirmed", "in_transit"])
        
        # Order statistics
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.get("status") in ["completed", "delivered"]])
        pending_orders = len([o for o in orders if o.get("status") in ["pending", "confirmed"]])
        cancelled_orders = len([o for o in orders if o.get("status") == "cancelled"])
        
        # Product performance
        product_performance = {}
        for product in all_products:
            product_orders = [o for o in orders if o.get("product_details", {}).get("product_id") == product["id"]]
            product_performance[product["id"]] = {
                "product_name": product.get("product_name") or product.get("crop_type", "Unknown"),
                "total_orders": len(product_orders),
                "total_revenue": sum(o.get("total_amount", 0) for o in product_orders if o.get("status") in ["completed", "delivered"]),
                "average_rating": product.get("average_rating", 5.0),
                "total_ratings": product.get("total_ratings", 0),
                "stock_level": product.get("quantity_available", 0),
                "low_stock": product.get("quantity_available", 0) < product.get("minimum_order_quantity", 1) * 5
            }
        
        # Customer insights
        unique_customers = len(set(order.get("buyer_username") for order in orders))
        repeat_customers = {}
        for order in orders:
            buyer = order.get("buyer_username")
            if buyer:
                repeat_customers[buyer] = repeat_customers.get(buyer, 0) + 1
        
        repeat_customer_count = len([count for count in repeat_customers.values() if count > 1])
        
        # Daily sales trend (last 7 days)
        daily_sales = {}
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_sales[date] = 0
        
        for order in orders:
            if order.get("status") in ["completed", "delivered"]:
                order_date = order.get("created_at")
                if isinstance(order_date, datetime):
                    date_str = order_date.strftime("%Y-%m-%d")
                    if date_str in daily_sales:
                        daily_sales[date_str] += order.get("total_amount", 0)
        
        # Top customers
        top_customers = sorted(
            [{"username": k, "total_spent": sum(o.get("total_amount", 0) for o in orders if o.get("buyer_username") == k and o.get("status") in ["completed", "delivered"]), "order_count": v} 
             for k, v in repeat_customers.items()],
            key=lambda x: x["total_spent"],
            reverse=True
        )[:5]
        
        # Inventory alerts
        low_stock_products = [p for p in all_products if p.get("quantity_available", 0) < p.get("minimum_order_quantity", 1) * 5]
        out_of_stock_products = [p for p in all_products if p.get("quantity_available", 0) == 0]
        
        return {
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "revenue": {
                "total_revenue": total_revenue,
                "pending_revenue": pending_revenue,
                "daily_average": total_revenue / days if days > 0 else 0,
                "daily_sales": daily_sales
            },
            "orders": {
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "pending_orders": pending_orders,
                "cancelled_orders": cancelled_orders,
                "completion_rate": (completed_orders / total_orders * 100) if total_orders > 0 else 0
            },
            "customers": {
                "unique_customers": unique_customers,
                "repeat_customers": repeat_customer_count,
                "repeat_rate": (repeat_customer_count / unique_customers * 100) if unique_customers > 0 else 0,
                "top_customers": top_customers
            },
            "products": {
                "total_products": len(all_products),
                "active_products": len([p for p in all_products if p.get("quantity_available", 0) > 0]),
                "low_stock_alerts": len(low_stock_products),
                "out_of_stock": len(out_of_stock_products),
                "performance": product_performance
            },
            "inventory_alerts": {
                "low_stock_products": [{"id": p["id"], "name": p.get("product_name") or p.get("crop_type"), "stock": p.get("quantity_available", 0)} for p in low_stock_products[:5]],
                "out_of_stock_products": [{"id": p["id"], "name": p.get("product_name") or p.get("crop_type")} for p in out_of_stock_products[:5]]
            }
        }
        
    except Exception as e:
        print(f"Error getting seller analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get seller analytics")

@app.get("/api/seller/dashboard/orders")
async def get_seller_orders(
    status: Optional[str] = None,
    days: Optional[int] = None,
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get seller's orders with advanced filtering"""
    try:
        seller_id = current_user["id"]
        
        # Get seller's products
        products = list(db.products.find({"seller_id": seller_id}))
        preorders = list(db.preorders.find({"seller_id": seller_id}))
        product_ids = [p["id"] for p in products + preorders]
        
        # Build query
        query = {"product_details.product_id": {"$in": product_ids}}
        
        if status:
            query["status"] = status
        
        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query["created_at"] = {"$gte": start_date}
        
        # Get total count
        total_count = db.orders.count_documents(query)
        
        # Get orders with pagination
        skip = (page - 1) * limit
        orders = list(db.orders.find(query)
                     .sort("created_at", -1)
                     .skip(skip)
                     .limit(limit))
        
        # Clean up response
        for order in orders:
            order.pop('_id', None)
            if isinstance(order.get("created_at"), datetime):
                order["created_at"] = order["created_at"].isoformat()
            if isinstance(order.get("updated_at"), datetime):
                order["updated_at"] = order["updated_at"].isoformat()
        
        # Order statistics
        status_counts = {}
        for status_type in ["pending", "confirmed", "in_transit", "delivered", "completed", "cancelled"]:
            count = db.orders.count_documents({
                "product_details.product_id": {"$in": product_ids},
                "status": status_type
            })
            status_counts[status_type] = count
        
        return {
            "orders": orders,
            "pagination": {
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit if total_count > 0 else 0
            },
            "status_summary": status_counts,
            "filters_applied": {
                "status": status,
                "days": days
            }
        }
        
    except Exception as e:
        print(f"Error getting seller orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get seller orders")

@app.put("/api/seller/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update order status (for sellers only)"""
    try:
        new_status = status_data.get("status")
        notes = status_data.get("notes", "")
        
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        # Validate status
        valid_statuses = ["pending", "confirmed", "preparing", "ready", "in_transit", "delivered", "completed", "cancelled"]
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Find order
        order = db.orders.find_one({"order_id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Verify seller ownership
        product_id = order.get("product_details", {}).get("product_id")
        if not product_id:
            raise HTTPException(status_code=400, detail="Invalid order structure")
        
        # Check if seller owns this product
        product = db.products.find_one({"id": product_id, "seller_id": current_user["id"]})
        if not product:
            product = db.preorders.find_one({"id": product_id, "seller_id": current_user["id"]})
        
        if not product:
            raise HTTPException(status_code=403, detail="You can only update orders for your own products")
        
        # Update order status
        update_data = {
            "status": new_status,
            "updated_at": datetime.utcnow()
        }
        
        if notes:
            update_data["seller_notes"] = notes
        
        db.orders.update_one(
            {"order_id": order_id},
            {"$set": update_data}
        )
        
        return {
            "message": "Order status updated successfully",
            "order_id": order_id,
            "new_status": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating order status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update order status")

@app.get("/api/seller/products/performance")
async def get_product_performance(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed product performance metrics"""
    try:
        seller_id = current_user["id"]
        
        # Get seller's products
        products = list(db.products.find({"seller_id": seller_id}))
        preorders = list(db.preorders.find({"seller_id": seller_id}))
        all_products = products + preorders
        
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        product_metrics = []
        
        for product in all_products:
            product_id = product["id"]
            
            # Get orders for this product
            orders = list(db.orders.find({
                "product_details.product_id": product_id,
                "created_at": {"$gte": start_date}
            }))
            
            # Calculate metrics
            total_orders = len(orders)
            completed_orders = len([o for o in orders if o.get("status") in ["completed", "delivered"]])
            revenue = sum(o.get("total_amount", 0) for o in orders if o.get("status") in ["completed", "delivered"])
            
            # Get product ratings
            product_ratings = list(ratings_collection.find({
                "rated_entity_id": product_id,
                "rating_type": RatingType.PRODUCT_RATING
            }))
            
            # View count (simulated - would be real in production)
            view_count = total_orders * 5  # Approximation
            
            product_metrics.append({
                "product_id": product_id,
                "product_name": product.get("product_name") or product.get("crop_type", "Unknown"),
                "category": product.get("category", ""),
                "price_per_unit": product.get("price_per_unit", 0),
                "stock_level": product.get("quantity_available", 0),
                "metrics": {
                    "total_orders": total_orders,
                    "completed_orders": completed_orders,
                    "conversion_rate": (completed_orders / total_orders * 100) if total_orders > 0 else 0,
                    "revenue": revenue,
                    "view_count": view_count,
                    "average_rating": product.get("average_rating", 5.0),
                    "total_ratings": len(product_ratings),
                    "rating_distribution": {
                        "5_star": len([r for r in product_ratings if r["rating_value"] == 5]),
                        "4_star": len([r for r in product_ratings if r["rating_value"] == 4]),
                        "3_star": len([r for r in product_ratings if r["rating_value"] == 3]),
                        "2_star": len([r for r in product_ratings if r["rating_value"] == 2]),
                        "1_star": len([r for r in product_ratings if r["rating_value"] == 1])
                    }
                },
                "alerts": {
                    "low_stock": product.get("quantity_available", 0) < product.get("minimum_order_quantity", 1) * 5,
                    "out_of_stock": product.get("quantity_available", 0) == 0,
                    "low_rating": product.get("average_rating", 5.0) < 3.5,
                    "no_recent_orders": total_orders == 0
                }
            })
        
        # Sort by revenue
        product_metrics.sort(key=lambda x: x["metrics"]["revenue"], reverse=True)
        
        return {
            "products": product_metrics,
            "summary": {
                "total_products": len(product_metrics),
                "low_stock_count": len([p for p in product_metrics if p["alerts"]["low_stock"]]),
                "out_of_stock_count": len([p for p in product_metrics if p["alerts"]["out_of_stock"]]),
                "low_rating_count": len([p for p in product_metrics if p["alerts"]["low_rating"]]),
                "top_performer": product_metrics[0] if product_metrics else None
            }
        }
        
    except Exception as e:
        print(f"Error getting product performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get product performance")

@app.get("/api/seller/customers/insights")
async def get_customer_insights(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get customer insights and analytics"""
    try:
        seller_id = current_user["id"]
        
        # Get seller's products
        products = list(db.products.find({"seller_id": seller_id}))
        preorders = list(db.preorders.find({"seller_id": seller_id}))
        product_ids = [p["id"] for p in products + preorders]
        
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get orders
        orders = list(db.orders.find({
            "product_details.product_id": {"$in": product_ids},
            "created_at": {"$gte": start_date}
        }))
        
        # Customer analysis
        customer_data = {}
        for order in orders:
            buyer = order.get("buyer_username")
            if not buyer:
                continue
            
            if buyer not in customer_data:
                customer_data[buyer] = {
                    "username": buyer,
                    "total_orders": 0,
                    "total_spent": 0,
                    "completed_orders": 0,
                    "first_order": order.get("created_at"),
                    "last_order": order.get("created_at"),
                    "favorite_products": {},
                    "average_order_value": 0
                }
            
            customer = customer_data[buyer]
            customer["total_orders"] += 1
            customer["total_spent"] += order.get("total_amount", 0)
            
            if order.get("status") in ["completed", "delivered"]:
                customer["completed_orders"] += 1
            
            # Track order dates
            order_date = order.get("created_at")
            if order_date:
                if customer["first_order"] is None or order_date < customer["first_order"]:
                    customer["first_order"] = order_date
                if customer["last_order"] is None or order_date > customer["last_order"]:
                    customer["last_order"] = order_date
            
            # Track favorite products
            product_name = order.get("product_details", {}).get("name", "Unknown")
            customer["favorite_products"][product_name] = customer["favorite_products"].get(product_name, 0) + 1
        
        # Calculate averages and insights
        for customer in customer_data.values():
            customer["average_order_value"] = customer["total_spent"] / customer["total_orders"] if customer["total_orders"] > 0 else 0
            customer["completion_rate"] = customer["completed_orders"] / customer["total_orders"] * 100 if customer["total_orders"] > 0 else 0
            
            # Get favorite product
            if customer["favorite_products"]:
                customer["top_product"] = max(customer["favorite_products"].items(), key=lambda x: x[1])[0]
            else:
                customer["top_product"] = "None"
            
            # Clean up dates for JSON serialization
            if isinstance(customer["first_order"], datetime):
                customer["first_order"] = customer["first_order"].isoformat()
            if isinstance(customer["last_order"], datetime):
                customer["last_order"] = customer["last_order"].isoformat()
        
        # Sort customers by total spent
        top_customers = sorted(customer_data.values(), key=lambda x: x["total_spent"], reverse=True)
        
        # Customer segments
        high_value_customers = [c for c in customer_data.values() if c["total_spent"] > 10000]  # Above ₦10,000
        repeat_customers = [c for c in customer_data.values() if c["total_orders"] > 1]
        new_customers = [c for c in customer_data.values() if c["total_orders"] == 1]
        
        return {
            "summary": {
                "total_customers": len(customer_data),
                "high_value_customers": len(high_value_customers),
                "repeat_customers": len(repeat_customers),
                "new_customers": len(new_customers),
                "average_customer_value": sum(c["total_spent"] for c in customer_data.values()) / len(customer_data) if customer_data else 0,
                "customer_retention_rate": len(repeat_customers) / len(customer_data) * 100 if customer_data else 0
            },
            "top_customers": top_customers[:10],
            "segments": {
                "high_value": len(high_value_customers),
                "repeat": len(repeat_customers),
                "new": len(new_customers),
                "at_risk": len([c for c in customer_data.values() if c["total_orders"] > 1 and c["completion_rate"] < 50])
            }
        }
        
    except Exception as e:
        print(f"Error getting customer insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get customer insights")

@app.put("/api/seller/products/{product_id}/inventory")
async def update_product_inventory(
    product_id: str,
    inventory_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update product inventory (stock levels)"""
    try:
        new_quantity = inventory_data.get("quantity_available")
        min_quantity = inventory_data.get("minimum_order_quantity")
        
        if new_quantity is None:
            raise HTTPException(status_code=400, detail="quantity_available is required")
        
        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Quantity cannot be negative")
        
        # Find product and verify ownership
        product = db.products.find_one({"id": product_id, "seller_id": current_user["id"]})
        if not product:
            product = db.preorders.find_one({"id": product_id, "seller_id": current_user["id"]})
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or you don't have permission to update it")
        
        # Update inventory
        update_data = {
            "quantity_available": new_quantity,
            "updated_at": datetime.utcnow()
        }
        
        if min_quantity is not None:
            update_data["minimum_order_quantity"] = max(1, min_quantity)
        
        # Update in appropriate collection
        if product.get("type") == "preorder":
            db.preorders.update_one({"id": product_id}, {"$set": update_data})
        else:
            db.products.update_one({"id": product_id}, {"$set": update_data})
        
        return {
            "message": "Inventory updated successfully",
            "product_id": product_id,
            "new_quantity": new_quantity,
            "minimum_order_quantity": update_data.get("minimum_order_quantity", product.get("minimum_order_quantity", 1))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating product inventory: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update product inventory")

# ==================== RATING SYSTEM ENDPOINTS ====================

@app.post("/api/ratings")
async def create_rating(
    rating_data: RatingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new rating (1-5 stars) for users, products, or drivers"""
    try:
        # Validate rating value
        if rating_data.rating_value < 1 or rating_data.rating_value > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5 stars")
        
        # Check if rating already exists for this entity by this user
        existing_rating = ratings_collection.find_one({
            "rater_id": current_user["id"],
            "rated_entity_id": rating_data.rated_entity_id,
            "rating_type": rating_data.rating_type,
            "order_id": rating_data.order_id  # Allow multiple ratings for different orders
        })
        
        # If updating existing rating
        if existing_rating:
            # Update existing rating
            update_data = {
                "rating_value": rating_data.rating_value,
                "comment": rating_data.comment,
                "updated_at": datetime.utcnow()
            }
            
            ratings_collection.update_one(
                {"id": existing_rating["id"]},
                {"$set": update_data}
            )
            
            rating_id = existing_rating["id"]
        else:
            # Create new rating
            rating = {
                "id": str(uuid.uuid4()),
                "rating_type": rating_data.rating_type,
                "rating_value": rating_data.rating_value,
                "rater_username": current_user["username"],
                "rater_id": current_user["id"],
                "rated_entity_id": rating_data.rated_entity_id,
                "rated_entity_username": rating_data.rated_entity_username,
                "order_id": rating_data.order_id,
                "comment": rating_data.comment,
                "created_at": datetime.utcnow(),
                "updated_at": None
            }
            
            ratings_collection.insert_one(rating)
            rating_id = rating["id"]
        
        # Update average rating for the rated entity
        await update_entity_average_rating(rating_data.rated_entity_id, rating_data.rating_type)
        
        return {
            "message": "Rating submitted successfully",
            "rating_id": rating_id,
            "rating_value": rating_data.rating_value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating rating: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create rating")

async def update_entity_average_rating(entity_id: str, rating_type: RatingType):
    """Helper function to update average rating for users, products, or drivers"""
    try:
        # Get all ratings for this entity
        all_ratings = list(ratings_collection.find({
            "rated_entity_id": entity_id,
            "rating_type": rating_type
        }))
        
        if not all_ratings:
            return
        
        # Calculate new average
        total_rating = sum(rating["rating_value"] for rating in all_ratings)
        average_rating = round(total_rating / len(all_ratings), 1)
        total_ratings = len(all_ratings)
        
        # Update appropriate collection based on rating type
        if rating_type == RatingType.USER_RATING:
            users_collection.update_one(
                {"id": entity_id},
                {"$set": {
                    "average_rating": average_rating,
                    "total_ratings": total_ratings
                }}
            )
        elif rating_type == RatingType.PRODUCT_RATING:
            db.products.update_one(
                {"id": entity_id},
                {"$set": {
                    "average_rating": average_rating,
                    "total_ratings": total_ratings
                }}
            )
            db.preorders.update_one(
                {"id": entity_id},
                {"$set": {
                    "average_rating": average_rating,
                    "total_ratings": total_ratings
                }}
            )
        elif rating_type == RatingType.DRIVER_RATING:
            # Update driver slot rating
            driver_slots_collection.update_one(
                {"driver_id": entity_id},
                {"$set": {
                    "average_rating": average_rating,
                    "total_ratings": total_ratings
                }}
            )
            # Also update user rating if driver is also a user
            users_collection.update_one(
                {"id": entity_id},
                {"$set": {
                    "average_rating": average_rating,
                    "total_ratings": total_ratings
                }}
            )
    except Exception as e:
        print(f"Error updating average rating: {str(e)}")

@app.get("/api/ratings/{entity_id}")
async def get_entity_ratings(
    entity_id: str,
    rating_type: RatingType,
    page: int = 1,
    limit: int = 20
):
    """Get ratings for a specific entity (user, product, or driver)"""
    try:
        skip = (page - 1) * limit
        
        # Get ratings for the entity
        ratings = list(ratings_collection.find({
            "rated_entity_id": entity_id,
            "rating_type": rating_type
        }).sort("created_at", -1).skip(skip).limit(limit))
        
        # Get total count
        total_count = ratings_collection.count_documents({
            "rated_entity_id": entity_id,
            "rating_type": rating_type
        })
        
        # Clean up response
        for rating in ratings:
            rating.pop('_id', None)
            if isinstance(rating.get("created_at"), datetime):
                rating["created_at"] = rating["created_at"].isoformat()
        
        # Calculate rating summary
        rating_distribution = {}
        for i in range(1, 6):
            count = ratings_collection.count_documents({
                "rated_entity_id": entity_id,
                "rating_type": rating_type,
                "rating_value": i
            })
            rating_distribution[f"{i}_star"] = count
        
        return {
            "ratings": ratings,
            "total_count": total_count,
            "rating_distribution": rating_distribution,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit if total_count > 0 else 0
        }
        
    except Exception as e:
        print(f"Error getting entity ratings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get ratings")

@app.get("/api/ratings/my-ratings")
async def get_my_ratings(
    rating_type: Optional[RatingType] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get ratings given by the current user"""
    try:
        query = {"rater_id": current_user["id"]}
        if rating_type:
            query["rating_type"] = rating_type
        
        ratings = list(ratings_collection.find(query).sort("created_at", -1))
        
        # Clean up response
        for rating in ratings:
            rating.pop('_id', None)
            if isinstance(rating.get("created_at"), datetime):
                rating["created_at"] = rating["created_at"].isoformat()
        
        return {
            "ratings": ratings,
            "total_count": len(ratings)
        }
        
    except Exception as e:
        print(f"Error getting user ratings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user ratings")

# ==================== DRIVER MANAGEMENT SYSTEM ====================

@app.post("/api/driver-slots/purchase")
async def purchase_driver_slots(
    slots_count: int,
    current_user: dict = Depends(get_current_user)
):
    """Purchase driver slots for logistics business (₦500 per slot, 14-day free trial)"""
    try:
        # Validate user is logistics business
        if current_user.get('role') != 'logistics':
            raise HTTPException(status_code=403, detail="Only logistics businesses can purchase driver slots")
        
        if slots_count < 1 or slots_count > 50:
            raise HTTPException(status_code=400, detail="Slot count must be between 1 and 50")
        
        # Get existing slots count for this business
        existing_slots = driver_slots_collection.count_documents({
            "logistics_business_id": current_user["id"],
            "is_active": True
        })
        
        # Create new slots
        slots_created = []
        for i in range(slots_count):
            slot_number = existing_slots + i + 1
            
            slot = {
                "id": str(uuid.uuid4()),
                "logistics_business_id": current_user["id"],
                "logistics_username": current_user["username"],
                "slot_number": slot_number,
                "driver_id": None,
                "driver_username": None,
                "driver_name": None,
                "vehicle_type": None,
                "plate_number": None,
                "vehicle_make_model": None,
                "vehicle_color": None,
                "vehicle_year": None,
                "vehicle_photo": None,
                "date_of_birth": None,
                "address": None,
                "driver_license": None,
                "registration_link": None,
                "subscription_status": DriverSubscriptionStatus.TRIAL,
                "trial_start_date": datetime.utcnow(),
                "subscription_start_date": None,
                "subscription_end_date": None,
                "monthly_fee": 500.0,
                "is_active": True,
                "total_trips": 0,
                "average_rating": 5.0,
                "created_at": datetime.utcnow(),
                "updated_at": None
            }
            
            driver_slots_collection.insert_one(slot)
            slots_created.append(slot["id"])
        
        total_cost = slots_count * 500.0
        trial_end_date = datetime.utcnow() + timedelta(days=14)
        
        return {
            "message": f"Successfully purchased {slots_count} driver slots",
            "slots_created": len(slots_created),
            "total_slots": existing_slots + slots_count,
            "trial_period": "14 days",
            "trial_end_date": trial_end_date.isoformat(),
            "monthly_cost_per_slot": "₦500",
            "total_monthly_cost": f"₦{total_cost:,.0f}",
            "slot_ids": slots_created
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error purchasing driver slots: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to purchase driver slots")

@app.get("/api/driver-slots/my-slots")
async def get_my_driver_slots(
    include_inactive: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get driver slots owned by logistics business"""
    try:
        # Validate user is logistics business
        if current_user.get('role') != 'logistics':
            raise HTTPException(status_code=403, detail="Only logistics businesses can view driver slots")
        
        query = {"logistics_business_id": current_user["id"]}
        if not include_inactive:
            query["is_active"] = True
        
        slots = list(driver_slots_collection.find(query).sort("slot_number", 1))
        
        # Clean up response
        for slot in slots:
            slot.pop('_id', None)
            if isinstance(slot.get("created_at"), datetime):
                slot["created_at"] = slot["created_at"].isoformat()
            if isinstance(slot.get("trial_start_date"), datetime):
                slot["trial_start_date"] = slot["trial_start_date"].isoformat()
        
        # Calculate summary statistics
        active_slots = len([s for s in slots if s.get("is_active")])
        occupied_slots = len([s for s in slots if s.get("driver_id")])
        trial_slots = len([s for s in slots if s.get("subscription_status") == "trial"])
        
        return {
            "slots": slots,
            "summary": {
                "total_slots": len(slots),
                "active_slots": active_slots,
                "occupied_slots": occupied_slots,
                "available_slots": active_slots - occupied_slots,
                "trial_slots": trial_slots,
                "monthly_cost": f"₦{active_slots * 500:,.0f}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting driver slots: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get driver slots")

@app.post("/api/driver-slots/{slot_id}/assign-driver")
async def assign_driver_to_slot(
    slot_id: str,
    driver_data: DriverSlotCreate,
    current_user: dict = Depends(get_current_user)
):
    """Assign driver information to a purchased slot and generate registration link"""
    try:
        # Find the slot
        slot = driver_slots_collection.find_one({"id": slot_id})
        if not slot:
            raise HTTPException(status_code=404, detail="Driver slot not found")
        
        # Validate ownership
        if slot["logistics_business_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="You can only assign drivers to your own slots")
        
        # Check if slot is already occupied
        if slot.get("driver_id"):
            raise HTTPException(status_code=400, detail="This slot is already assigned to a driver")
        
        # Generate unique registration link
        registration_token = str(uuid.uuid4())
        registration_link = f"/api/drivers/register/{registration_token}"
        
        # Update slot with driver information
        update_data = {
            "driver_name": driver_data.driver_name,
            "vehicle_type": driver_data.vehicle_type,
            "plate_number": driver_data.plate_number.upper(),
            "vehicle_make_model": driver_data.vehicle_make_model,
            "vehicle_color": driver_data.vehicle_color,
            "vehicle_year": driver_data.vehicle_year,
            "vehicle_photo": driver_data.vehicle_photo,
            "date_of_birth": driver_data.date_of_birth,
            "address": driver_data.address,
            "driver_license": driver_data.driver_license,
            "registration_link": registration_link,
            "registration_token": registration_token,
            "updated_at": datetime.utcnow()
        }
        
        driver_slots_collection.update_one(
            {"id": slot_id},
            {"$set": update_data}
        )
        
        return {
            "message": "Driver assigned to slot successfully",
            "slot_id": slot_id,
            "driver_name": driver_data.driver_name,
            "vehicle_info": f"{driver_data.vehicle_make_model} ({driver_data.plate_number})",
            "registration_link": registration_link,
            "instructions": "Share this registration link with the driver to complete their account setup"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error assigning driver to slot: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to assign driver to slot")

@app.post("/api/drivers/register/{registration_token}")
async def complete_driver_registration(
    registration_token: str,
    registration_data: DriverRegistrationComplete
):
    """Complete driver registration using the provided registration link"""
    try:
        # Find slot with this registration token
        slot = driver_slots_collection.find_one({"registration_token": registration_token})
        if not slot:
            raise HTTPException(status_code=404, detail="Invalid registration link")
        
        # Check if slot is already activated
        if slot.get("driver_id"):
            raise HTTPException(status_code=400, detail="This registration link has already been used")
        
        # Check if username is available
        existing_user = users_collection.find_one({"username": registration_data.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create driver user account
        driver_user = {
            "id": str(uuid.uuid4()),
            "first_name": slot["driver_name"].split()[0] if slot.get("driver_name") else "Driver",
            "last_name": " ".join(slot["driver_name"].split()[1:]) if slot.get("driver_name") and len(slot["driver_name"].split()) > 1 else "",
            "username": registration_data.username,
            "email": f"{registration_data.username}@pyramyddriver.com",  # Generated email
            "password": hash_password(registration_data.password),
            "phone": None,  # Will be updated when driver provides it
            "role": UserRole.DRIVER,
            "is_verified": True,  # Auto-verify logistics business managed drivers
            "wallet_balance": 0.0,
            "average_rating": 5.0,
            "total_ratings": 0,
            "created_at": datetime.utcnow()
        }
        
        users_collection.insert_one(driver_user)
        
        # Update slot with driver account information
        driver_slots_collection.update_one(
            {"id": slot["id"]},
            {"$set": {
                "driver_id": driver_user["id"],
                "driver_username": registration_data.username,
                "registration_token": None,  # Clear token after use
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "message": "Driver registration completed successfully",
            "driver_username": registration_data.username,
            "vehicle_info": {
                "type": slot.get("vehicle_type"),
                "make_model": slot.get("vehicle_make_model"),
                "plate_number": slot.get("plate_number"),
                "color": slot.get("vehicle_color")
            },
            "logistics_business": slot["logistics_username"],
            "instructions": "You can now access the driver platform using your username and password"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing driver registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete driver registration")

@app.get("/api/drivers/profile/{driver_username}")
async def get_driver_profile(driver_username: str):
    """Get enhanced driver profile for uber-like interface"""
    try:
        # Get driver user information
        driver_user = users_collection.find_one({"username": driver_username, "role": "driver"})
        if not driver_user:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Get driver slot information
        driver_slot = driver_slots_collection.find_one({"driver_username": driver_username})
        
        # Get driver ratings
        driver_ratings = list(ratings_collection.find({
            "rated_entity_id": driver_user["id"],
            "rating_type": RatingType.DRIVER_RATING
        }).sort("created_at", -1).limit(10))
        
        # Clean up ratings
        for rating in driver_ratings:
            rating.pop('_id', None)
            if isinstance(rating.get("created_at"), datetime):
                rating["created_at"] = rating["created_at"].isoformat()
        
        # Build enhanced profile
        profile = {
            "id": driver_user["id"],
            "driver_username": driver_username,
            "driver_name": f"{driver_user['first_name']} {driver_user['last_name']}".strip(),
            "phone_number": driver_user.get("phone"),
            "average_rating": driver_user.get("average_rating", 5.0),
            "total_ratings": driver_user.get("total_ratings", 0),
            "total_trips": driver_slot.get("total_trips", 0) if driver_slot else 0,
            "is_independent": driver_slot is None,  # Independent if no slot found
            "status": "offline",  # Default status, would be updated with real-time data
            "vehicle_info": {},
            "logistics_business_info": None,
            "recent_ratings": driver_ratings,
            "created_at": driver_user["created_at"].isoformat() if isinstance(driver_user.get("created_at"), datetime) else None
        }
        
        # Add vehicle and logistics information if slot exists
        if driver_slot:
            profile["vehicle_info"] = {
                "type": driver_slot.get("vehicle_type"),
                "make_model": driver_slot.get("vehicle_make_model"),
                "plate_number": driver_slot.get("plate_number"),
                "color": driver_slot.get("vehicle_color"),
                "year": driver_slot.get("vehicle_year"),
                "photo": driver_slot.get("vehicle_photo")
            }
            profile["logistics_business_info"] = {
                "business_username": driver_slot.get("logistics_username"),
                "slot_number": driver_slot.get("slot_number")
            }
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting driver profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get driver profile")

@app.get("/api/drivers/find-drivers")
async def find_available_drivers(
    location: Optional[str] = None,
    vehicle_type: Optional[VehicleType] = None,
    min_rating: Optional[float] = None,
    limit: int = 20
):
    """Find available drivers for uber-like interface"""
    try:
        # Build query for active driver slots
        query = {"is_active": True, "driver_id": {"$ne": None}}
        
        if vehicle_type:
            query["vehicle_type"] = vehicle_type
        
        if min_rating:
            query["average_rating"] = {"$gte": min_rating}
        
        # Get driver slots
        driver_slots = list(driver_slots_collection.find(query).limit(limit))
        
        # Build driver profiles
        drivers = []
        for slot in driver_slots:
            # Get user information
            driver_user = users_collection.find_one({"id": slot["driver_id"]})
            if not driver_user:
                continue
            
            driver_profile = {
                "id": slot["driver_id"],
                "username": slot["driver_username"],
                "name": slot["driver_name"],
                "average_rating": slot.get("average_rating", 5.0),
                "total_trips": slot.get("total_trips", 0),
                "vehicle_info": {
                    "type": slot.get("vehicle_type"),
                    "make_model": slot.get("vehicle_make_model"),
                    "plate_number": slot.get("plate_number"),
                    "color": slot.get("vehicle_color"),
                    "photo": slot.get("vehicle_photo")
                },
                "logistics_business": slot.get("logistics_username"),
                "status": "available"  # Would be dynamic in real implementation
            }
            
            drivers.append(driver_profile)
        
        return {
            "drivers": drivers,
            "total_found": len(drivers),
            "filters_applied": {
                "location": location,
                "vehicle_type": vehicle_type,
                "min_rating": min_rating
            }
        }
        
    except Exception as e:
        print(f"Error finding drivers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to find drivers")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)