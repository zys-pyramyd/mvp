import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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

# Security
security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    FARMER = "farmer"
    AGENT = "agent"
    SUPER_AGENT = "super_agent"
    STORAGE_OWNER = "storage_owner"
    LOGISTICS_BUSINESS = "logistics_business"
    SUPPLIER = "supplier"
    PROCESSOR = "processor"
    GENERAL_BUYER = "general_buyer"
    RETAILER = "retailer"
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    CAFE = "cafe"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
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

# Pydantic models
class UserRegister(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
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

class RoleSelection(BaseModel):
    role: UserRole
    is_buyer: bool = False

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    seller_name: str
    title: str
    description: str
    category: ProductCategory
    price_per_unit: float
    unit_of_measure: str  # kg, basket, crate, etc.
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
    quantity_available: int
    minimum_order_quantity: int = 1
    location: str
    farm_name: Optional[str] = None
    images: List[str] = []
    platform: str = "pyhub"

class CartItem(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    buyer_id: str
    buyer_name: str
    seller_id: str
    seller_name: str
    items: List[dict]  # product details with quantities
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    delivery_address: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    user = db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user['id'])
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user['id'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "username": user['username'],
            "email": user['email'],
            "role": user.get('role'),
            "platform": "pyhub" if user.get('role') in ['farmer', 'agent', 'storage_owner', 'logistics_business', 'super_agent'] else "pyexpress"
        }
    }

@app.post("/api/auth/select-role")
async def select_role(role_data: RoleSelection, current_user: dict = Depends(get_current_user)):
    # Update user role
    db.users.update_one(
        {'id': current_user['id']},
        {'$set': {'role': role_data.role.value}}
    )
    
    # Determine default platform
    platform = "pyhub" if role_data.role in [UserRole.FARMER, UserRole.AGENT, UserRole.STORAGE_OWNER, UserRole.LOGISTICS_BUSINESS, UserRole.SUPER_AGENT] else "pyexpress"
    
    return {
        "message": "Role selected successfully",
        "role": role_data.role.value,
        "platform": platform
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
async def get_products(platform: str = "pyhub", category: Optional[str] = None, search: Optional[str] = None):
    query = {"platform": platform}
    
    if category:
        query["category"] = category
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    products = list(db.products.find(query).sort("created_at", -1))
    
    # Convert ObjectId to string and clean up
    for product in products:
        product.pop('_id', None)
    
    return products

@app.post("/api/products")
async def create_product(product_data: ProductCreate, current_user: dict = Depends(get_current_user)):
    if not current_user.get('role'):
        raise HTTPException(status_code=400, detail="Please select a role first")
    
    # Check if user can create products
    allowed_roles = ['farmer', 'agent', 'supplier', 'processor']
    if current_user.get('role') not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized to create products")
    
    # Create product
    product = Product(
        seller_id=current_user['id'],
        seller_name=current_user['username'],
        **product_data.dict()
    )
    
    # Apply service charges based on role
    if current_user.get('role') == 'farmer':
        # 30% markup for farmers on PyHub
        product.price_per_unit = product_data.price_per_unit * 1.30
    
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

@app.get("/api/categories")
async def get_categories():
    return [{"value": cat.value, "label": cat.value.replace("_", " ").title()} for cat in ProductCategory]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)