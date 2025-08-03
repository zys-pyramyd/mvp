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

# Security
security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    FARMER = "farmer"
    AGENT = "agent"
    SUPER_AGENT = "super_agent"
    STORAGE_OWNER = "storage_owner"
    LOGISTICS_BUSINESS = "logistics_business"
    SUPPLIER_FARM_INPUTS = "supplier_farm_inputs"  # New: Farm input suppliers (PyHub only)
    SUPPLIER_FOOD_PRODUCE = "supplier_food_produce"  # New: Food produce suppliers (PyExpress only)
    PROCESSOR = "processor"
    GENERAL_BUYER = "general_buyer"
    RETAILER = "retailer"
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    CAFE = "cafe"

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
    shipping_address: str
    delivery_method: str = "platform"  # "platform" or "offline"
    
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

class ProductCategory(str, Enum):
    SEA_FOOD = "sea_food"
    GRAIN = "grain"
    LEGUMES = "legumes"
    VEGETABLES = "vegetables"
    SPICES = "spices"
    CASH_CROP = "cash_crop"
    FERTILIZER = "fertilizer"
    HERBICIDES = "herbicides"
    PESTICIDES = "pesticides"
    SEEDS = "seeds"
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

class CartItem(BaseModel):
    product_id: str
    quantity: int

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
        product = db.products.find_one({"_id": order_data.product_id}) or db.preorders.find_one({"id": order_data.product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Calculate total amount
        unit_price = product.get("price_per_unit", 0)
        total_amount = order_data.quantity * unit_price
        
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
            "total_amount": total_amount,
            "delivery_method": order_data.delivery_method,
            "delivery_status": "pending" if order_data.delivery_method == "offline" else "",
            "shipping_address": order_data.shipping_address,
            "status": OrderStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Store order
        db.orders.insert_one(order)
        
        return {
            "message": "Order created successfully",
            "order_id": order["order_id"],
            "total_amount": total_amount,
            "delivery_method": order_data.delivery_method,
            "quantity_display": f"{order_data.quantity} {order_data.unit}" + (f" ({order_data.unit_specification})" if order_data.unit_specification else "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create order")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)