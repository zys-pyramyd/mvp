import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator, EmailStr
from database import db, get_client, get_db, get_collection
from auth import get_current_user, create_access_token, get_password_hash, verify_password, JWT_SECRET, ALGORITHM
from messaging.routes import router as messaging_router

# --- R2 Cloudflare Integration ---
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

# R2 Configuration
R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
R2_PRIVATE_BUCKET = os.environ.get('R2_PRIVATE_BUCKET', 'pyramyd-private')
R2_PUBLIC_BUCKET = os.environ.get('R2_PUBLIC_BUCKET', 'pyramyd-public')
SIGNED_URL_EXPIRATION = int(os.environ.get('SIGNED_URL_EXPIRATION', 3600))

# Initialize R2 Client
s3_client = None
if R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY:
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4')
        )
        print("R2 Client Initialized")
    except Exception as e:
        print(f"Failed to initialize R2 client: {e}")

# Folder validaton and Bucket mapping
ALLOWED_FOLDERS = {
    'user-registration': {'bucket': R2_PRIVATE_BUCKET, 'privacy': 'private'},
    'messages': {'bucket': R2_PRIVATE_BUCKET, 'privacy': 'private'},
    'notifications': {'bucket': R2_PRIVATE_BUCKET, 'privacy': 'private'},
    'admin': {'bucket': R2_PRIVATE_BUCKET, 'privacy': 'private'},
    'temp': {'bucket': R2_PRIVATE_BUCKET, 'privacy': 'private'}, 
    'social': {'bucket': R2_PUBLIC_BUCKET, 'privacy': 'public'},
    'products': {'bucket': R2_PUBLIC_BUCKET, 'privacy': 'public'}
}

class UploadSignRequest(BaseModel):
    folder: str
    filename: str
    contentType: str

class DocumentMetadata(BaseModel):
    type: str 
    key: str
    bucket: str
    filename: str

# Helper functions (Auth helpers moved to auth.py)

import jwt
from enum import Enum
from cryptography.fernet import Fernet
import base64
import hashlib
import hmac
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from geo_helper import GeopyHelper
from payment.paystack import (
    PaystackSubaccount, 
    PaystackTransaction, 
    PaystackTransferRecipient, 
    CommissionPayout,
    PAYSTACK_API_URL,
    paystack_request,
    naira_to_kobo,
    kobo_to_naira,
    verify_paystack_signature
)
from payment.farm_deals_payment import initialize_farmhub_payment
from payment.pyexpress_payment import initialize_pyexpress_payment
from payment.community_payment import initialize_community_payment
from order.models import (
    Order, 
    CartItem, 
    GroupOrder, 
    OutsourcedOrder, 
    AgentPurchaseOption, 
    GroupBuyingRequest
)

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', os.environ.get('MONGO_URI'))
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

# Third Party APIs
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
TWILIO_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
GEOAPIFY_API_KEY = os.environ.get('GEOAPIFY_API_KEY')

# Kwik Delivery API
KWIK_ACCESS_TOKEN = os.environ.get('KWIK_ACCESS_TOKEN')
KWIK_DOMAIN_NAME = os.environ.get('KWIK_DOMAIN_NAME', 'pyramyd.com')
KWIK_VENDOR_ID = os.environ.get('KWIK_VENDOR_ID')
KWIK_API_URL = "https://api.kwik.delivery"

def check_critical_env_vars():
    """Ensure critical environment variables are set."""
    missing = []
    if not MONGO_URL: missing.append("MONGO_URL")
    if not JWT_SECRET: missing.append("JWT_SECRET")
    
    if missing:
        error_msg = f"CRITICAL SECURITY ERROR: Missing required environment variables: {', '.join(missing)}"
        print(error_msg)

    if not PAYSTACK_SECRET_KEY: print("WARNING: PAYSTACK_SECRET_KEY missing. Payments will fail.")
    if not GEOAPIFY_API_KEY: print("WARNING: GEOAPIFY_API_KEY missing. Location services will fail.")

check_critical_env_vars()
KWIK_API_URL = "https://api.kwik.delivery"
KWIK_ENABLED_STATES = ["Lagos", "Oyo", "FCT Abuja"]

# Email Configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
SUPPORT_EMAIL = os.environ.get('SUPPORT_MAIL','')
FROM_EMAIL = os.environ.get('FROM_EMAIL', SUPPORT_EMAIL)

# Admin credentials
ADMIN_EMAIL = os.environ.get('ADMIN_MAIL')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# Collections (from imported db)
# Note: db is initialized in database.py
if db is not None:
    users_collection = db['users']
    agent_farmers_collection = db['agent_farmers']
    ratings_collection = db['ratings']
    community_posts_collection = db['community_posts']
    post_likes_collection = db['post_likes']
    post_comments_collection = db['post_comments']
    group_orders_collection = db['group_orders']
else:
    print("Warning: Database not initialized")

from database import db, client, get_db, get_collection
from auth import get_current_user, create_access_token, get_password_hash, verify_password, JWT_SECRET, ALGORITHM
from messaging.routes import router as messaging_router

# ... (Previous imports remain same)

# Initialize FastAPI
app = FastAPI(
    title="Pyramyd API",
    description="Backend for Pyramyd Market",
    version="1.0.0"
)

import threading
import time

# Startup check that does NOT crash the app
@app.on_event("startup")
def startup():
    def warm_db():
        print("Starting background DB warmup...")
        for i in range(5):
            try:
                # Use get_db() to access the lazy client
                db_instance = get_db()
                # Run a cheap command
                db_instance.command("ping")
                print("MongoDB warmed and connected")
                break
            except Exception as e:
                print(f"MongoDB warming attempt {i+1} failed: {e}")
                time.sleep(5)
    
    # Start warmup in background thread
    threading.Thread(target=warm_db, daemon=True).start()

@app.get("/api/health")
async def health_check():
    """Health check endpoint to wake up server"""
    try:
         # Optional: Check DB status here too, or just return online
         get_db().command("ping")
         db_status = "connected"
    except Exception:
         db_status = "disconnected"
         
    return {"status": "online", "db_status": db_status}

# Include Routers
app.include_router(messaging_router)

from community.routes import router as community_router
app.include_router(community_router)

# CORS Middleware
allowed_origins = [
    "*"
]

vercel_url = os.environ.get('VERCEL_URL')
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "Pyramyd API is running"}

@app.post("/api/upload/sign-public")
async def sign_upload_public(request: UploadSignRequest):
    """Generate a presigned URL for public/registration uploads (Restricted folders)"""
    print(f"DEBUG: Internal sign-public called for folder={request.folder}, filename={request.filename}")
    
    if not s3_client:
        print("DEBUG: S3 Client is None")
        raise HTTPException(status_code=503, detail="Storage service unavailable")
        
    # Strictly allow only registration folder for unauthenticated uploads
    if request.folder != 'user-registration':
        print(f"DEBUG: Unauthorized folder access: {request.folder}")
        raise HTTPException(status_code=403, detail="Unauthorized folder access")
    
    config = ALLOWED_FOLDERS.get(request.folder)
    if not config:
        print(f"DEBUG: Invalid folder config for {request.folder}")
        raise HTTPException(status_code=400, detail="Invalid folder configuration")

    bucket = config['bucket']
    
    file_ext = request.filename.split('.')[-1] if '.' in request.filename else 'bin'
    safe_filename = f"{uuid.uuid4().hex}.{file_ext}" # No user ID available yet, use random UUID
    key = f"{request.folder}/temp/{safe_filename}"
    
    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket,
                'Key': key,
                'ContentType': request.contentType
            },
            ExpiresIn=SIGNED_URL_EXPIRATION 
        )
        print(f"DEBUG: Successfully generated URL for {key}")
        
        return {
            "uploadUrl": presigned_url,
            "key": key,
            "bucket": bucket,
            "publicUrl": None
        }
    except ClientError as e:
        print(f"R2 Signing Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate upload URL: {str(e)}")
    except Exception as e:
        print(f"Unexpected Error in sign-public: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/api/upload/sign")
async def sign_upload(request: UploadSignRequest, current_user: dict = Depends(get_current_user)):
    """Generate a presigned URL for direct R2 upload"""
    if not s3_client:
        raise HTTPException(status_code=503, detail="Storage service unavailable")
        
    if request.folder not in ALLOWED_FOLDERS:
        raise HTTPException(status_code=400, detail="Invalid folder")
    
    config = ALLOWED_FOLDERS[request.folder]
    bucket = config['bucket']
    
    file_ext = request.filename.split('.')[-1] if '.' in request.filename else 'bin'
    safe_filename = f"{uuid.uuid4().hex}.{file_ext}"
    key = f"{request.folder}/{current_user['id']}/{safe_filename}"
    
    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket,
                'Key': key,
                'ContentType': request.contentType
            },
            ExpiresIn=SIGNED_URL_EXPIRATION 
        )
        
        return {
            "uploadUrl": presigned_url,
            "key": key,
            "bucket": bucket,
            "publicUrl": f"https://pub-cdn.pyramydhub.com/{key}" if config['privacy'] == 'public' else None
        }
    except ClientError as e:
        print(f"R2 Signing Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")

@app.post("/api/user/documents")
async def save_document_metadata(doc: DocumentMetadata, current_user: dict = Depends(get_current_user)):
    """Save metadata for an uploaded document"""
    users_collection.update_one(
        {"id": current_user["id"]},
        {"$push": {"documents": {
            "type": doc.type,
            "key": doc.key,
            "bucket": doc.bucket,
            "filename": doc.filename,
            "uploaded_at": datetime.now(),
            "status": "pending_verification"
        }}}
    )
    return {"status": "success", "message": "Document saved"}

# Pydantic Models for Registration
class CompleteRegistration(BaseModel):
    first_name: str
    last_name: str
    username: str
    email_or_phone: str
    password: str
    phone: str
    user_path: str
    # Address Fields
    address_street: Optional[str] = None # Number and Street Name
    city: Optional[str] = None # Town/City
    landmark: Optional[str] = None # Nearest Landmark (Optional)
    state: Optional[str] = None # State (Dropdown)
    country: str = "Nigeria" # Default Nigeria
    
    buyer_type: Optional[str] = None
    partner_type: Optional[str] = None
    business_category: Optional[str] = None
    business_info: Optional[dict] = None
    verification_info: Optional[dict] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    # Enhanced fields
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    documents: Optional[Dict[str, str]] = None  # URLs or base64 of uploaded docs
    directors: Optional[List[dict]] = None
    farm_details: Optional[List[dict]] = None
    registration_status: Optional[str] = None # 'registered' or 'unregistered' for business
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    verification_documents: Optional[Dict[str, str]] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    username: str
    email: str
    phone: str
    role: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Address
    address_street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


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

    # Admin Override for scalable access
    if registration_data.email_or_phone in ADMIN_EMAILS:
        user_role = 'admin'
    
    # --- ENFORCEMENT LOGIC ---
    
    # 1. Agent & Farmer Enforcement
    if user_role in ['agent', 'farmer']:
        # Require ID, Headshot, Address Proof
        if not registration_data.id_type or not registration_data.id_number:
             raise HTTPException(status_code=400, detail="Identity verification (ID Type & Number) is required.")
        
        docs = registration_data.documents or {}
        if not docs.get('headshot'):
             raise HTTPException(status_code=400, detail="Profile Picture (Headshot) is required.")
        if not docs.get('id_document'): # Slip/Card upload
             raise HTTPException(status_code=400, detail="ID Document upload is required.")
        if not docs.get('proof_of_address'):
             raise HTTPException(status_code=400, detail="Proof of Address is required.")
             
        if user_role == 'farmer':
            if not registration_data.farm_details:
                raise HTTPException(status_code=400, detail="Farm details are required for Farmers.")

    # 2. Business Enforcement
    # Business roles can be: food_servicing, food_processor, farm_input, fintech, agriculture, supplier, others
    is_business_role = registration_data.partner_type == 'business'
    
    if is_business_role:
        if not registration_data.business_info:
             raise HTTPException(status_code=400, detail="Business Information is required.")
        
        reg_status = registration_data.registration_status
        if not reg_status:
             raise HTTPException(status_code=400, detail="Business Registration Status (registered/unregistered) is required.")

        docs = registration_data.documents or {}
        
        if reg_status == 'registered':
            # Registered Business: CAC, TIN, Proof of Address (Director check removed per request)
            if not docs.get('cac_document'):
                 raise HTTPException(status_code=400, detail="CAC Document is required for registered businesses.")
            if not docs.get('proof_of_address'):
                 raise HTTPException(status_code=400, detail="Proof of Business Address is required.")
            if not registration_data.business_info.get('tin'):
                 raise HTTPException(status_code=400, detail="TIN is required for registered businesses.")
                 
        elif reg_status == 'unregistered':
            # Unregistered Business: Treat like Agent (ID, Headshot, Bio)
            if not registration_data.id_type or not registration_data.id_number:
                 raise HTTPException(status_code=400, detail="Identity verification is required for unregistered businesses.")
            if not docs.get('headshot'):
                 raise HTTPException(status_code=400, detail="Headshot (Camera) is required.")
            if not docs.get('id_document'):
                 raise HTTPException(status_code=400, detail="ID Document/NIN upload is required.")
            if not docs.get('proof_of_address'):
                 raise HTTPException(status_code=400, detail="Proof of Address is required.")
            # Bio is optional/implied by business info

    # --- END ENFORCEMENT ---

    # Create user with complete information
    user = User(
        first_name=registration_data.first_name,
        last_name=registration_data.last_name,
        username=registration_data.username,
        email=registration_data.email_or_phone,  # Store as email for compatibility
        phone=registration_data.phone,
        role=user_role,
        profile_picture=registration_data.profile_picture,
        verification_documents=registration_data.verification_documents,
        # Address Mapping
        address_street=registration_data.address_street,
        city=registration_data.city,
        state=registration_data.state,
        country=registration_data.country
    )
    
    # Create user document with additional fields
    user_dict = user.dict()
    user_dict['password'] = hash_password(registration_data.password)
    user_dict['gender'] = registration_data.gender
    user_dict['date_of_birth'] = registration_data.date_of_birth
    user_dict['user_path'] = registration_data.user_path
    user_dict['business_info'] = registration_data.business_info or {}
    user_dict['verification_info'] = registration_data.verification_info or {}
    
    # Store enhanced fields
    user_dict['id_type'] = registration_data.id_type
    user_dict['id_number'] = registration_data.id_number
    user_dict['documents'] = registration_data.documents or {}
    user_dict['landmark'] = registration_data.landmark
    user_dict['directors'] = registration_data.directors or []
    user_dict['farm_details'] = registration_data.farm_details or []
    user_dict['registration_status'] = registration_data.registration_status
    user_dict['bio'] = registration_data.bio
    
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





# Commission rates
AGENT_BUYER_COMMISSION_RATE = 0.04  # 4% for agent buyers



# Base delivery fees for each state in Nigeria (in Naira)
# These fees are used as the base for geocoded distance calculations
BASE_DELIVERY_FEES = STATE_DELIVERY_FEES = {
    # Lagos and neighbors - Tier 1
    "Lagos": 1500,
    "Ogun": 2000,
    
    # South West - Tier 2
    "Oyo": 2500,
    "Osun": 2500,
    "Ondo": 3000,
    "Ekiti": 3000,
    
    # South South - Tier 2
    "Rivers": 2500,
    "Delta": 2500,
    "Edo": 2500,
    "Bayelsa": 3000,
    "Cross River": 3000,
    "Akwa Ibom": 3000,
    
    # South East - Tier 2  
    "Anambra": 2500,
    "Enugu": 2500,
    "Imo": 2500,
    "Abia": 2500,
    "Ebonyi": 3000,
    
    # FCT - Tier 1
    "FCT Abuja": 1500,
    
    # North Central - Tier 3
    "Nasarawa": 3000,
    "Niger": 3500,
    "Kogi": 3000,
    "Benue": 3500,
    "Plateau": 3500,
    "Kwara": 3000,
    
    # North West - Tier 3
    "Kaduna": 3500,
    "Kano": 3500,
    "Katsina": 4000,
    "Sokoto": 4000,
    "Zamfara": 4000,
    "Kebbi": 4000,
    "Jigawa": 4000,
    
    # North East - Tier 4
    "Borno": 4500,
    "Yobe": 4500,
    "Adamawa": 4000,
    "Gombe": 4000,
    "Bauchi": 4000,
    "Taraba": 4000,
}

# HOME platform operates only in these states (24-hour delivery)
HOME_PLATFORM_STATES = ["Lagos", "Oyo", "FCT Abuja"]

# Perishable product categories (require faster/special handling)
PERISHABLE_CATEGORIES = ["fish_meat", "spices_vegetables"]

def get_base_delivery_fee(state: str) -> float:
    """Get base delivery fee for a state"""
    return BASE_DELIVERY_FEES.get(state, 3000)  # Default 3000 if state not found

def get_delivery_fee_by_state(state: str) -> float:
    """Get delivery fee based on customer's state (backward compatibility)"""
    return get_base_delivery_fee(state)

# Generate encryption key if not provided (for development only)
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"WARNING: Using auto-generated encryption key. Set ENCRYPTION_KEY in production!")

# Initialize Fernet cipher for encryption
cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not data:
        return None
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return None
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        return None




# --- AUTHENTICATION & SECURITY ---
security = HTTPBearer()

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


class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    # Find user by email, username, or phone
    user = db.users.find_one({"$or": [
        {"email": login_data.username},
        {"username": login_data.username},
        {"phone": login_data.username},
        {"email_or_phone": login_data.username}
    ]})
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    token = create_token(user["id"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user["id"],
        "username": user["username"],
        "role": user.get("role", "buyer"),
         "user": {
            "id": user["id"],
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "username": user["username"],
            "email": user.get("email"),
            "role": user.get("role"),
            "profile_picture": user.get("profile_picture")
        }
    }

ADMIN_EMAILS = ["abdulazeezshakrullah@gmail.com", "abdulazeezshakrullah@pyramydhub.com"]

@app.on_event("startup")
async def startup_db_client():
    print("Checking for admin users...")
    try:
        initial_password = "AdminInitialPassword123!" # Default initial password
        hashed = hash_password(initial_password)
        
        for email in ADMIN_EMAILS:
            user = db.users.find_one({"email": email})
            if not user:
                print(f"Creating admin user: {email}")
                new_admin = {
                    "id": str(uuid.uuid4()),
                    "email": email,
                    "password": hashed,
                    "role": "admin",
                    "username": email.split('@')[0],
                    "first_name": "Abdulazeez",
                    "last_name": "Shakrullah",
                    "is_verified": True,
                    "created_at": datetime.utcnow()
                }
                db.users.insert_one(new_admin)
                print(f"Admin created: {email}, Default Password: {initial_password}")
            else:
                if user.get("role") != "admin":
                    db.users.update_one({"_id": user["_id"]}, {"$set": {"role": "admin"}})
                    print(f"Updated role to admin for {email}")
    except Exception as e:
        print(f"Error seeding admins: {e}")

def get_kyc_requirements(user: dict) -> dict:
    """Get specific KYC requirements based on user type"""
    role = user.get("role", "")
    business_category = user.get("business_category", "")
    is_registered_business = user.get("is_registered_business", False)
    
    # Agent-specific KYC requirements
    if role == "agent":
        return {
            "type": "agent",
            "title": "Agent KYC Requirements",
            "description": "Specialized requirements for agricultural agents",
            "review_time": "1-3 business days",
            "documents": [
                "Headshot Photo (Camera captured)",
                "National ID Document (NIN or BVN)",
                "Utility Bill (Address verification)",
                "Bank Statement (Financial verification)",
                "Certificate of Incorporation (If registered business)",
                "TIN Certificate (If registered business)"
            ],
            "information_required": [
                "Business name and address",
                "Personal identification details",
                "Agricultural experience",
                "Target operation locations",
                "Expected farmer network size"
            ],
            "endpoint": "/api/kyc/agent/submit",
            "benefits_after_approval": [
                "Register and verify farmers",
                "Earn commission on farmer sales",
                "Access agent dashboard",
                "Build farmer network"
            ]
        }
    
    # Farmer-specific KYC requirements  
    elif role == "farmer":
        return {
            "type": "farmer",
            "title": "Farmer KYC Requirements", 
            "description": "Verification requirements for farmers",
            "review_time": "24-48 hours (agent-verified) or 2-5 business days (self-verified)",
            "documents": [
                "Headshot Photo (Camera captured)",
                "National ID Document (NIN or BVN)", 
                "Farm Photo (Show your farming area)",
                "Land Ownership Document (Certificate or lease agreement)"
            ],
            "information_required": [
                "Personal identification details",
                "Farm location and size",
                "Primary crops grown",
                "Farming experience",
                "Land ownership status"
            ],
            "verification_options": [
                {
                    "method": "agent_verified",
                    "title": "Agent Verification (Recommended)",
                    "description": "Get verified by a registered agent for faster processing",
                    "processing_time": "24-48 hours",
                    "benefits": ["Faster approval", "Agent support", "Market access guidance"]
                },
                {
                    "method": "self_verified", 
                    "title": "Self Verification",
                    "description": "Submit documents directly for verification",
                    "processing_time": "2-5 business days",
                    "benefits": ["Direct submission", "Full document control"]
                }
            ],
            "endpoint": "/api/kyc/farmer/submit"
        }
    
    # Business KYC requirements (existing)
    elif role == "business":
        if is_registered_business:
            return {
                "type": "registered_business",
                "title": "Registered Business KYC",
                "description": "Requirements for registered businesses",
                "review_time": "2-5 business days",
                "documents": [
                    "Business Registration Number",
                    "TIN Certificate", 
                    "Certificate of Incorporation",
                    "Business Address Verification (Utility Bill)"
                ],
                "endpoint": "/api/kyc/registered-business/submit"
            }
        else:
            return {
                "type": "unregistered_business",
                "title": "Unregistered Business KYC", 
                "description": "Requirements for unregistered businesses",
                "review_time": "2-5 business days",
                "documents": [
                    "NIN or BVN",
                    "Headshot Photo (Camera)",
                    "National ID Document",
                    "Utility Bill (Address Verification)"
                ],
                "endpoint": "/api/kyc/unregistered-entity/submit"
            }
    
    # Default for other roles
    else:
        return {
            "type": "unregistered_entity", 
            "title": "Standard KYC Requirements",
            "documents": [
                "NIN or BVN",
                "Headshot Photo (Camera)",
                "National ID Document", 
                "Utility Bill (Address Verification)"
            ],
            "endpoint": "/api/kyc/unregistered-entity/submit"
        }

def validate_kyc_compliance(user: dict, action: str = "general"):
    """
    Validate if user is KYC compliant for specific actions.
    """
    # Personal accounts don't require KYC
    if user.get("role") == "personal":
        return True
    
    # Check if KYC is required and approved
    kyc_status = user.get("kyc_status", "not_started")
    user_role = user.get("role", "")
    
    # Enhanced restrictions for agents - they must complete KYC before ANY platform actions
    if user_role == "agent":
        if kyc_status == "not_started":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "AGENT_KYC_REQUIRED",
                    "message": "Agents must complete their KYC verification before performing any actions on the platform. Please submit your KYC documents to get started.",
                    "kyc_status": kyc_status,
                    "verification_time": "Verification takes within 24 hours to verify",
                    "access_level": "view_only",
                    "required_actions": get_kyc_requirements(user)
                }
            )
        elif kyc_status == "pending":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "AGENT_KYC_PENDING", 
                    "message": "Your KYC is under review. You can access the platform to view but cannot onboard farmers or publish farm produce until your status changes to verified.",
                    "kyc_status": kyc_status,
                    "verification_time": "Verification typically completes within 24 hours",
                    "access_level": "view_only"
                }
            )
        elif kyc_status == "rejected":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "AGENT_KYC_REJECTED",
                    "message": "Your KYC was rejected. Please resubmit with correct documents. You can only view the platform until verification is completed.",
                    "kyc_status": kyc_status,
                    "access_level": "view_only",
                    "required_actions": get_kyc_requirements(user)
                }
            )
    
    # For other roles (business, farmer, etc.) - standard KYC validation
    if kyc_status != "approved":
        status_messages = {
            "not_started": "Please complete your KYC verification to perform this action",
            "pending": "Your KYC is under review. You can perform this action once approved", 
            "rejected": "Your KYC was rejected. Please resubmit with correct documents to continue"
        }
        
        action_context = {
            "sales": "receive payments or complete sales",
            "register_farmers": "register farmers to your network",
            "post_products": "post products for sale", 
            "collect_payments": "collect payments from customers"
        }
        
        context = action_context.get(action, "perform this action")
        message = f"KYC verification required to {context}. {status_messages.get(kyc_status, 'KYC verification required')}"
        
        raise HTTPException(
            status_code=403,
            detail={
                "error": "KYC_REQUIRED",
                "message": message,
                "kyc_status": kyc_status,
                "required_actions": get_kyc_requirements(user)
            }
        )
    
    return True

def send_order_completion_email(order_data: dict):
    """Send order completion notification to support email"""
    try:
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print("⚠️ Email credentials not configured. Skipping email notification.")
            return False

        # Create email content
        subject = f"Order Completed: {order_data.get('order_id', 'N/A')}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                <h2 style="color: #2ecc71; border-bottom: 2px solid #2ecc71; padding-bottom: 10px;">Order Completed Successfully</h2>
                
                <div style="margin: 20px 0;">
                    <h3 style="color: #27ae60;">Order Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Order ID:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{order_data.get('order_id', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Buyer:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{order_data.get('buyer_username', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Seller:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{order_data.get('seller_username', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Total Amount:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">₦{order_data.get('total_amount', 0):,.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Delivery Method:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{order_data.get('delivery_method', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Delivery Address:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{order_data.get('shipping_address', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Completed At:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #eee;">{order_data.get('delivered_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S') if isinstance(order_data.get('delivered_at'), datetime) else 'N/A'}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3 style="color: #27ae60;">Product Details</h3>
                    {_format_product_details(order_data.get('product_details', {}))}
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; font-size: 12px;">
                    <p>This is an automated notification from Pyramyd Hub.</p>
                    <p>For inquiries, contact: {SUPPORT_EMAIL}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = SUPPORT_EMAIL
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Order completion email sent for order: {order_data.get('order_id')}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send order completion email: {str(e)}")
        return False

def _format_product_details(product_details: dict) -> str:
    """Format product details for email"""
    if not product_details:
        return "<p>No product details available</p>"
    
    return f"""
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Product Name:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{product_details.get('title', 'N/A')}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Quantity:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{product_details.get('quantity', 0)} {product_details.get('unit', '')}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Unit Price:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">₦{product_details.get('unit_price', 0):,.2f}</td>
        </tr>
    </table>
    """

# Commission structure for agents (updated rates)
AGENT_COMMISSION_RATES = {
    'purchase': 0.05,  # 5% commission for agent purchases
    'sale': 0.05,      # 5% commission for agent sales (updated from 4% to 5%)
    'onboarding': 0.075, # 7.5% farmer onboarding incentive (first sale only)
    'verification': 0.02  # 2% farmer verification fee
}

# Agent Tier System (Gamification)
AGENT_TIERS = {
    'starter': {'min_farmers': 0, 'max_farmers': 99, 'bonus_commission': 0.00, 'name': 'Starter'},
    'pro': {'min_farmers': 100, 'max_farmers': 999, 'bonus_commission': 0.005, 'name': 'Pro'},
    'expert': {'min_farmers': 1000, 'max_farmers': 4999, 'bonus_commission': 0.01, 'name': 'Expert'},
    'master': {'min_farmers': 5000, 'max_farmers': 9999, 'bonus_commission': 0.02, 'name': 'Master'},
    'elite': {'min_farmers': 10000, 'max_farmers': float('inf'), 'bonus_commission': 0.04, 'name': 'Elite'}
}

def get_agent_tier(farmer_count: int) -> dict:
    """Calculate agent tier based on farmer count"""
    for tier_key, tier_data in AGENT_TIERS.items():
        if tier_data['min_farmers'] <= farmer_count <= tier_data['max_farmers']:
            return {
                'tier': tier_key,
                'tier_name': tier_data['name'],
                'farmer_count': farmer_count,
                'bonus_commission': tier_data['bonus_commission'],
                'next_tier': get_next_tier(tier_key),
                'farmers_to_next_tier': get_farmers_to_next_tier(farmer_count, tier_key)
            }
    return {
        'tier': 'starter',
        'tier_name': 'Starter',
        'farmer_count': farmer_count,
        'bonus_commission': 0.00,
        'next_tier': 'pro',
        'farmers_to_next_tier': 100 - farmer_count
    }

def get_next_tier(current_tier: str) -> str:
    """Get the next tier name"""
    tier_order = ['starter', 'pro', 'expert', 'master', 'elite']
    try:
        current_index = tier_order.index(current_tier)
        if current_index < len(tier_order) - 1:
            return tier_order[current_index + 1]
        return 'elite'  # Already at max
    except ValueError:
        return 'pro'

def get_farmers_to_next_tier(farmer_count: int, current_tier: str) -> int:
    """Calculate how many more farmers needed for next tier"""
    next_tier = get_next_tier(current_tier)
    if next_tier == current_tier:  # Already at elite
        return 0
    next_tier_data = AGENT_TIERS.get(next_tier)
    if next_tier_data:
        return max(0, next_tier_data['min_farmers'] - farmer_count)
    return 0

def calculate_agent_commission(product_total: float, agent_user_id: str, db) -> dict:
    """Calculate agent commission with tier bonus"""
    # Get agent's farmer count
    farmer_count = agent_farmers_collection.count_documents({'agent_id': agent_user_id})
    
    # Get agent tier
    tier_info = get_agent_tier(farmer_count)
    
    # Base commission (4%)
    base_commission = product_total * AGENT_BUYER_COMMISSION_RATE
    
    # Tier bonus commission
    bonus_commission = product_total * tier_info['bonus_commission']
    
    # Total commission
    total_commission = base_commission + bonus_commission
    
    return {
        'base_commission': base_commission,
        'bonus_commission': bonus_commission,
        'total_commission': total_commission,
        'tier_info': tier_info
    }

# Kwik Delivery Integration
def kwik_request(method: str, endpoint: str, data: dict = None) -> dict:
    """
    Make authenticated request to Kwik Delivery API.
    Kwik API requires access_token in the request body, not headers.
    """
    headers = {
        "Content-Type": "application/json"
    }
    url = f"{KWIK_API_URL}{endpoint}"

    # Add access_token to request body (Kwik's authentication method)
    if data is None:
        data = {}
    data['access_token'] = KWIK_ACCESS_TOKEN

    try:
        if method == "GET":
            # For GET requests, send as query params
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            # For POST requests, send in body
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Kwik API error: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        # Don't raise exception, return None to fallback to state-based fees
        return None

def estimate_fare_kwik(pickup_address: dict, delivery_address: dict, vehicle_id: int = 0) -> dict:
    """
    Estimate delivery fare using Kwik API.

    Args:
        pickup_address: dict with 'address', 'name', 'phone', 'latitude', 'longitude', 'email'
        delivery_address: dict with 'address', 'name', 'phone', 'latitude', 'longitude', 'email'
        vehicle_id: 0 for Bike/Motorcycle, other IDs for different vehicle types

    Returns:
        dict with 'estimated_fare', 'distance_km', 'success' or None if failed
    """
    payload = {
        "domain_name": KWIK_DOMAIN_NAME,
        "vendor_id": KWIK_VENDOR_ID,
        "is_multiple_tasks": 1,
        "has_pickup": 1,
        "has_delivery": 1,
        "vehicle_id": vehicle_id,
        "pickups": [
            {
                "address": pickup_address.get('address', ''),
                "name": pickup_address.get('name', 'Vendor'),
                "phone": pickup_address.get('phone', '+234'),
                "latitude": str(pickup_address.get('latitude', '')),
                "longitude": str(pickup_address.get('longitude', '')),
                "email": pickup_address.get('email', 'vendor@pyramyd.com')
            }
        ],
        "deliveries": [
            {
                "address": delivery_address.get('address', ''),
                "name": delivery_address.get('name', 'Customer'),
                "phone": delivery_address.get('phone', '+234'),
                "latitude": str(delivery_address.get('latitude', '')),
                "longitude": str(delivery_address.get('longitude', '')),
                "email": delivery_address.get('email', 'customer@example.com')
            }
        ]
    }

    # Endpoint might be /task/estimate_fare or similar - verify with Kwik docs
    result = kwik_request("POST", "/task/estimate_fare", payload)

    if result and result.get('status') == 'success':
        # Parse the response - structure may vary, adjust based on actual API response
        data = result.get('data', {})
        return {
            'success': True,
            'estimated_fare': data.get('delivery_charge', 0),  # In Naira
            'distance_km': data.get('distance', 0),
            'currency': 'NGN',
            'vehicle_type': vehicle_id
        }

    return None

def calculate_delivery_fee(product_total: float, buyer_state: str, product_data: dict = None,
                          pickup_address: dict = None, delivery_address: dict = None, 
                          platform_type: str = "home", quantity: float = 1, 
                          buyer_location: str = None, seller_location: str = None,
                          buyer_city: str = None, seller_city: str = None) -> dict:
    """
    Smart delivery fee calculator with vendor priority and platform-specific logic.
    Priority: Vendor logistics > Kwik API (for HOME in enabled states) > Platform-specific geocode calculation

    Args:
        product_total: Total product value in Naira
        buyer_state: Customer's state
        product_data: Optional product info (for vendor-managed logistics and perishable check)
        pickup_address: Optional pickup location (for Kwik fare estimation)
        delivery_address: Optional delivery location (for Kwik fare estimation)
        platform_type: Platform type - "home", "farmhub", or "community"
        quantity: Quantity of product (for farmhub/community calculation)
        buyer_location: Buyer's full address/location string (for geocoding)
        seller_location: Seller's full address/location string (for geocoding)
        buyer_city: Buyer's city (used in geocoding if provided)
        seller_city: Seller's city (used in geocoding if provided)

    Returns:
        dict with delivery_fee, delivery_method, estimated_delivery_days, and other metadata
    """
    delivery_info = {
        'delivery_fee': 0.0,
        'delivery_method': 'unknown',
        'kwik_available': False,
        'vendor_managed': False,
        'estimated_delivery_days': None
    }

    # Priority 1: Check if vendor manages logistics
    if product_data and product_data.get('logistics_managed_by') == 'seller':
        vendor_fee = product_data.get('seller_delivery_fee', 0.0)
        delivery_info.update({
            'delivery_fee': vendor_fee,
            'delivery_method': 'vendor_managed',
            'vendor_managed': True,
            'is_free': vendor_fee == 0.0,
            'estimated_delivery_days': '3-14 days' if platform_type in ['farmhub', 'community'] else '24 hours'
        })
        return delivery_info

    # Priority 2: Standard Platform Delivery (Distance or Zone based)
    # We skipped Kwik as per user request. 
    
    # Continue to standard calculation below...


    # Priority 3: Platform-specific geocode-based calculation
    # Get base delivery fee for the state
    base_fee = get_base_delivery_fee(buyer_state)
    
    # Try to calculate distance using geocoding
    distance_km = None
    if buyer_location or buyer_city:
        try:
            # Build buyer address string (include city if provided)
            buyer_addr = buyer_location or ""
            if buyer_city and buyer_city not in buyer_addr:
                buyer_addr = f"{buyer_addr}, {buyer_city}" if buyer_addr else buyer_city
            if buyer_state and buyer_state not in buyer_addr:
                buyer_addr = f"{buyer_addr}, {buyer_state}, Nigeria"
            
            # Build seller address string (include city if provided)
            seller_addr = seller_location or ""
            if seller_city and seller_city not in seller_addr:
                seller_addr = f"{seller_addr}, {seller_city}" if seller_addr else seller_city
            # Add Nigeria to help with geocoding
            if "Nigeria" not in seller_addr:
                seller_addr = f"{seller_addr}, Nigeria"
            
            buyer_coords = geo_helper.geocode_address(buyer_addr.strip())
            seller_coords = geo_helper.geocode_address(seller_addr.strip())
            
            if buyer_coords and seller_coords:
                distance_km = geo_helper.distance_km(buyer_coords, seller_coords)
        except Exception as e:
            print(f"Geocoding error: {str(e)}")
            distance_km = None
    
    # Calculate platform-specific delivery fee
    if platform_type == "home":
        # HOME: base_fee + (distance * 1000), max 40,000
        if distance_km:
            calculated_fee = base_fee + (distance_km * 1000)
            delivery_fee = min(calculated_fee, 40000)  # Cap at 40,000
            delivery_info.update({
                'delivery_fee': delivery_fee,
                'delivery_method': 'geocode_distance_based',
                'distance_km': distance_km,
                'base_fee': base_fee,
                'estimated_delivery_days': '24 hours'
            })
        else:
            # Fallback to base fee if geocoding fails
            delivery_info.update({
                'delivery_fee': base_fee,
                'delivery_method': 'state_based_fallback',
                'base_fee': base_fee,
                'estimated_delivery_days': '24 hours'
            })
    
    elif platform_type in ["farmhub", "community"]:
        # FARMHUB/COMMUNITY: base_fee + (distance * quantity * multiplier)
        # Check if product is perishable (multiplier = 15, else 10)
        is_perishable = False
        if product_data:
            category = product_data.get('category', '')
            is_perishable = category in PERISHABLE_CATEGORIES
        
        multiplier = 15 if is_perishable else 10
        
        if distance_km:
            calculated_fee = base_fee + (distance_km * quantity * multiplier)
            delivery_info.update({
                'delivery_fee': calculated_fee,
                'delivery_method': 'geocode_distance_quantity_based',
                'distance_km': distance_km,
                'base_fee': base_fee,
                'quantity': quantity,
                'is_perishable': is_perishable,
                'multiplier': multiplier,
                'estimated_delivery_days': '3-14 days'
            })
        else:
            # Fallback to base fee if geocoding fails
            delivery_info.update({
                'delivery_fee': base_fee,
                'delivery_method': 'state_based_fallback',
                'base_fee': base_fee,
                'estimated_delivery_days': '3-14 days'
            })
    else:
        # Default fallback for unknown platforms
        delivery_info.update({
            'delivery_fee': base_fee,
            'delivery_method': 'state_based_default',
            'base_fee': base_fee
        })

    return delivery_info

def create_kwik_delivery(pickup_address: dict, delivery_address: dict, order_details: dict, vehicle_id: int = 0) -> dict:
    """
    Create a delivery task on Kwik API using official API structure.

    Args:
        pickup_address: dict with 'address', 'name', 'phone', 'latitude', 'longitude', 'email'
        delivery_address: dict with 'address', 'name', 'phone', 'latitude', 'longitude', 'email'
        order_details: dict with 'order_id', 'description', 'amount', 'collect_cod' (bool)
        vehicle_id: 0 for Bike/Motorcycle, other IDs for different vehicle types

    Returns:
        dict with tracking info or None if failed
    """
    # Determine payment method and COD amount
    collect_cod = order_details.get('collect_cod', False)
    total_amount_kobo = naira_to_kobo(order_details.get('amount', 0)) if collect_cod else 0

    # Payment method: 524288 for EOMB (End of Month Billing), check Kwik docs for other methods
    # If platform already collected payment, amount should be 0
    payment_method = 524288  # EOMB - adjust based on your Kwik account setup

    kwik_payload = {
        "domain_name": KWIK_DOMAIN_NAME,
        "vendor_id": KWIK_VENDOR_ID,
        "is_multiple_tasks": 1,
        "has_pickup": 1,
        "has_delivery": 1,
        "vehicle_id": vehicle_id,
        "auto_assignment": 1,  # Automatically assign to available driver
        "amount": total_amount_kobo,  # Total amount in kobo (if COD) or 0
        "payment_method": payment_method,
        "pickups": [
            {
                "address": pickup_address.get('address', ''),
                "name": pickup_address.get('name', 'Pyramyd Vendor'),
                "phone": pickup_address.get('phone', '+234'),
                "latitude": str(pickup_address.get('latitude', '')),
                "longitude": str(pickup_address.get('longitude', '')),
                "email": pickup_address.get('email', 'vendor@pyramyd.com')
            }
        ],
        "deliveries": [
            {
                "address": delivery_address.get('address', ''),
                "name": delivery_address.get('name', 'Customer'),
                "phone": delivery_address.get('phone', '+234'),
                "latitude": str(delivery_address.get('latitude', '')),
                "longitude": str(delivery_address.get('longitude', '')),
                "email": delivery_address.get('email', 'customer@example.com')
            }
        ],
        "delivery_instruction": f"Order Ref: {order_details.get('order_id', '')}. {order_details.get('description', 'Handle with care.')}"
    }

    # Official endpoint for task creation
    result = kwik_request("POST", "/task/create_pickup_and_delivery_task", kwik_payload)

    if result and result.get('status') == 'success':
        # Parse response - adjust field names based on actual Kwik API response
        data = result.get('data', {})
        return {
            'success': True,
            'kwik_task_id': data.get('task_id') or data.get('delivery_id'),
            'tracking_url': data.get('tracking_url'),
            'tracking_id': data.get('tracking_id'),
            'estimated_time': data.get('estimated_time'),
            'driver_name': data.get('driver_name'),
            'driver_phone': data.get('driver_phone'),
            'status': data.get('status', 'assigned')
        }

    return None

app = FastAPI(title="Pyramyd API", version="1.0.0")

# CORS middleware
# Get allowed origins from env, default to localhost for dev and the specified production domain
origins_str = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://pyramydhub.com,https://www.pyramydhub.com")
origins = [origin.strip() for origin in origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"], # Allow all headers for now to prevent auth issues
)

# Startup Event
@app.on_event("startup")
async def startup_event():
    print(f"Application starting up on port {os.environ.get('PORT', '8001')}...")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Pyramyd Backend Running", "service": "backend"}



# Initialize GeopyHelper with MongoDB caching
geo_helper = GeopyHelper(api_key=GEOAPIFY_API_KEY, user_agent="pyramyd_platform", db=db, cache_collection="geocode_cache")

users_collection = db.users
messages_collection = db.messages
dropoff_locations_collection = db.dropoff_locations
ratings_collection = db.ratings
driver_slots_collection = db.driver_slots
wallet_transactions_collection = db.wallet_transactions
bank_accounts_collection = db.bank_accounts
gift_cards_collection = db.gift_cards
wallet_security_collection = db.wallet_security
secure_account_details_collection = db.secure_account_details  # Encrypted account details
# Enhanced KYC collections
kyc_documents_collection = db.kyc_documents
agent_kyc_collection = db.agent_kyc
farmer_kyc_collection = db.farmer_kyc

# Communities collections
communities_collection = db.communities
community_members_collection = db.community_members
community_products_collection = db.community_products
community_product_likes_collection = db.community_product_likes
community_product_comments_collection = db.community_product_comments
group_buy_participants_collection = db.group_buy_participants
farmland_records_collection = db.farmland_records
agent_farmers_collection = db.agent_farmers
audit_logs_collection = db.audit_logs

# Paystack Payment collections
paystack_subaccounts_collection = db.paystack_subaccounts

# --- Messaging System Models & Endpoints ---

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: str
    content: Optional[str] = None
    attachments: Optional[List[str]] = [] # List of R2 keys
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MessageCreate(BaseModel):
    recipient_username: str
    content: Optional[str] = None
    attachments: Optional[List[str]] = []

@app.post("/api/messages")
async def send_message(msg_data: MessageCreate, current_user: dict = Depends(get_current_user)):
    """Send a direct message"""
    recipient = users_collection.find_one({"username": msg_data.recipient_username})
    if not recipient:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate attachements (Optional: Check if keys exist/belong to user)
    
    new_msg = {
        "id": str(uuid.uuid4()),
        "sender_id": current_user["id"],
        "recipient_id": recipient["id"],
        "content": msg_data.content,
        "attachments": msg_data.attachments,
        "is_read": False,
        "created_at": datetime.utcnow()
    }
    
    messages_collection.insert_one(new_msg)
    new_msg.pop("_id", None)
    return new_msg



@app.get("/api/users/search")
async def search_users(q: str, current_user: dict = Depends(get_current_user)):
    """Search users to start a chat"""
    users = list(users_collection.find(
        {"username": {"$regex": q, "$options": "i"}, "id": {"$ne": current_user["id"]}},
        {"first_name": 1, "last_name": 1, "username": 1, "profile_picture": 1}
    ).limit(10))
    
    results = []
    for u in users:
        results.append({
            "username": u.get("username"),
            "display_name": f"{u.get('first_name', '')} {u.get('last_name', '')}".strip(),
            "profile_picture": u.get("profile_picture") or "https://via.placeholder.com/40"
        })
    return {"users": results}


@app.put("/api/products/{product_id}/preorder-time")
async def update_preorder_time(
    product_id: str,
    time_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update pre-order availability time"""
    # Verify ownership
    product = db.products.find_one({"id": product_id})
    if not product:
         raise HTTPException(status_code=404, detail="Product not found")
         
    if product["seller_id"] != current_user["id"]:
         raise HTTPException(status_code=403, detail="Not authorized")
    
    db.products.update_one(
        {"id": product_id},
        {"$set": {
            "preorder_available_date": time_data.get("available_date"),
            "preorder_end_date": time_data.get("end_date"),
            "is_preorder": True
        }}
    )
    
    return {"message": "Pre-order time updated"}

@app.get("/api/communities/search")
async def search_communities(
    q: str,  # Search query
    type: str = "all"  # all, community, product
):
    """Search communities and products"""
    try:
        results = {
            "communities": [],
            "products": []
        }
        
        if type in ["all", "community"]:
            communities = list(communities_collection.find({
                "$or": [
                    {"name": {"$regex": q, "$options": "i"}},
                    {"description": {"$regex": q, "$options": "i"}},
                    {"category": {"$regex": q, "$options": "i"}}
                ]
            }).limit(10))
            
            for community in communities:
                community.pop('_id', None)
            results["communities"] = communities
        
        if type in ["all", "product"]:
            # Search products that belong to a community
            products = list(db.products.find({
                "community_id": {"$exists": True, "$ne": None},
                "$or": [
                    {"title": {"$regex": q, "$options": "i"}},
                    {"description": {"$regex": q, "$options": "i"}},
                    {"category": {"$regex": q, "$options": "i"}}
                ]
            }).limit(10))
            
            for product in products:
                product.pop('_id', None)
            results["products"] = products
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """Admin dashboard statistics"""
    # Verify admin - logic can be improved to check specific admin roles or email list
    # For MVP, we might just check if role is 'admin' or email matches specific env var
    # As per checklist, we should use ADMIN_EMAIL
    if current_user["email"] != ADMIN_EMAIL and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Aggregate stats
    total_transactions = paystack_transactions_collection.count_documents({"status": "success"})
    
    # Calculate revenue
    revenue_pipeline = [
        {"$match": {"status": "success"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}} # Amount is usually in kobo
    ]
    revenue_result = list(paystack_transactions_collection.aggregate(revenue_pipeline))
    total_revenue = (revenue_result[0]["total"] / 100) if revenue_result else 0
    
    return {
        "totalTransactions": total_transactions,
        "totalRevenue": total_revenue,
        "activeUsers": users_collection.count_documents({}),
        "pendingOrders": db.orders.count_documents({"status": "pending"}),
        "pendingKYC": users_collection.count_documents({"kyc_status": "pending"})
    }

@app.get("/api/agent/farmers")
async def get_agent_farmers(current_user: dict = Depends(get_current_user)):
    """Get list of farmers managed by the agent with performance stats"""
    if current_user["role"] != "agent":
        raise HTTPException(status_code=403, detail="Only agents can access this endpoint")
        
    try:
        # Get relationships
        relationships = list(agent_farmers_collection.find({"agent_id": current_user["id"]}))
        farmer_ids = [r["farmer_id"] for r in relationships]
        
        farmers = []
        for farmer_id in farmer_ids:
            # Get farmer profile
            farmer = users_collection.find_one({"id": farmer_id})
            if not farmer:
                continue
                
            # Get stats
            product_count = db.products.count_documents({"seller_id": farmer_id})
            
            # Sales stats
            sales_pipeline = [
                {"$match": {"delivery_handler_id": farmer_id, "status": {"$ne": "cancelled"}}},
                {"$group": {"_id": None, "total_sales": {"$sum": "$total_amount"}, "order_count": {"$sum": 1}}}
            ]
            sales_result = list(db.orders.aggregate(sales_pipeline))
            sales_data = sales_result[0] if sales_result else {"total_sales": 0, "order_count": 0}
            
            farmers.append({
                "id": farmer["id"],
                "username": farmer["username"],
                "first_name": farmer.get("first_name", ""),
                "last_name": farmer.get("last_name", ""),
                "profile_picture": farmer.get("profile_picture"),
                "product_count": product_count,
                "total_sales": sales_data["total_sales"],
                "total_orders": sales_data["order_count"],
                "joined_at": farmer.get("created_at")
            })
            
        return {"farmers": farmers}
        
    except Exception as e:
        print(f"Error getting agent farmers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



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
    GRAINS_CEREALS = "grains_cereals"
    GRAINS_LEGUMES = "grains_legumes" # Kept for backward compatibility
    BEANS_VARIETIES = "beans_varieties"
    FLOUR_BAKINGS = "flour_bakings"
    SPICES_VEGETABLES = "spices_vegetables" 
    FISH_MEAT = "fish_meat"
    SEA_FOODS = "sea_foods"
    TUBERS_ROOTS = "tubers_roots"
    FRUITS = "fruits"
    CASH_CROP = "cash_crop"
    FERTILIZER = "fertilizer"
    HERBICIDES = "herbicides"
    PESTICIDES = "pesticides"
    SEEDS = "seeds"
    PACKAGED_GOODS = "packaged_goods"

class GrainsLegumesSubcategory(str, Enum):
    RICE = "rice"  # e.g. local rice, ofada rice, basmati rice
    WHEAT = "wheat"  # e.g. wheat grains, wheat flour
    CORN_MAIZE = "corn_maize"  # e.g. yellow corn, white corn, dried corn
    BEANS = "beans"  # e.g. black beans, brown beans, white beans
    COWPEAS = "cowpeas"  # e.g. black-eyed peas, drum beans
    GROUNDNUTS = "groundnuts"  # e.g. peanuts, groundnut paste
    SOYBEANS = "soybeans"  # e.g. dried soybeans, soy flour
    MILLET = "millet"  # e.g. pearl millet, finger millet

class FishMeatSubcategory(str, Enum):
    FRESH_FISH = "fresh_fish"  # e.g. tilapia, catfish, mackerel
    DRIED_FISH = "dried_fish"  # e.g. stockfish, dried catfish, smoked fish
    POULTRY = "poultry"  # e.g. chicken, turkey, duck
    BEEF = "beef"  # e.g. fresh beef, processed beef
    GOAT_MUTTON = "goat_mutton"  # e.g. goat meat, mutton
    PORK = "pork"  # e.g. fresh pork, processed pork
    SNAILS = "snails"  # e.g. giant African snails

class SpicesVegetablesSubcategory(str, Enum):
    LEAFY_VEGETABLES = "leafy_vegetables"  # e.g. spinach, lettuce, cabbage, kale
    PEPPERS = "peppers"  # e.g. scotch bonnet, bell peppers, cayenne pepper
    TOMATOES = "tomatoes"  # e.g. fresh tomatoes, cherry tomatoes, Roma tomatoes
    ONIONS = "onions"  # e.g. red onions, white onions, spring onions
    GINGER_GARLIC = "ginger_garlic"  # e.g. fresh ginger, garlic, ginger powder
    HERBS_SPICES = "herbs_spices"  # e.g. basil, thyme, curry leaves, locust beans
    OKRA = "okra"  # e.g. fresh okra, dried okra
    CUCUMBER = "cucumber"  # e.g. field cucumber, greenhouse cucumber

class TubersRootsSubcategory(str, Enum):
    YAMS = "yams"  # e.g. white yam, water yam, aerial yam
    CASSAVA = "cassava"  # e.g. fresh cassava, cassava flour, garri
    SWEET_POTATOES = "sweet_potatoes"  # e.g. orange flesh, white flesh sweet potatoes
    IRISH_POTATOES = "irish_potatoes"  # e.g. red potatoes, white potatoes
    COCOYAMS = "cocoyams"  # e.g. taro, tannia
    PLANTAINS = "plantains"  # e.g. unripe plantains, ripe plantains
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

# All 36 Nigerian States + FCT Abuja
NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa",
    "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo",
    "Ekiti", "Enugu", "FCT Abuja", "Gombe", "Imo", "Jigawa",
    "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara",
    "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun",
    "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"
]


class ProductCreate(BaseModel):
    title: str
    description: str
    category: ProductCategory
    price_per_unit: float
    unit: str
    quantity: int
    images: List[str] = []
    location: str # This constitutes the State
    city: Optional[str] = None
    pickup_address: Optional[str] = None
    platform: str = "home"
    has_discount: bool = False
    discount_value: float = 0.0
    discount_type: str = "percentage"
    logistics_managed_by: str = "platform"
    seller_delivery_fee: float = 0.0
    # Additional Product Details
    about_product: Optional[str] = None
    product_benefits: Optional[List[str]] = []
    usage_instructions: Optional[str] = None
    # Pre-order specific fields
    is_preorder: bool = False
    preorder_available_date: Optional[datetime] = None
    preorder_end_date: Optional[datetime] = None
    # Agent/Community fields
    farmer_id: Optional[str] = None
    community_id: Optional[str] = None
    community_name: Optional[str] = None

class Product(ProductCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    seller_name: str
    seller_type: Optional[str] = None
    seller_profile_picture: Optional[str] = None
    seller_profile_picture: Optional[str] = None
    business_name: Optional[str] = None
    managed_by_agent_id: Optional[str] = None
    community_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    original_price: Optional[float] = None
    original_price: Optional[float] = None
    discount_amount: float = 0.0
    city: Optional[str] = None
    pickup_address: Optional[str] = None



class RatingType(str, Enum):
    USER = "user"
    PRODUCT = "product"
    DRIVER = "driver"

class RatingCreate(BaseModel):
    rating_value: float
    comment: Optional[str] = None
    rating_type: str
    rated_entity_id: str
    rated_entity_username: Optional[str] = None
    order_id: Optional[str] = None




class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(BaseModel):
    id: Optional[str] = None
    order_id: str = Field(default_factory=lambda: f"PY_ORD-{uuid.uuid4().hex[:12].upper()}")
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
    delivery_handler_id: Optional[str] = None
    delivery_notes: Optional[str] = None

class KYCDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    document_type: str  # headshot, nin, drivers_license, voters_card, cac
    document_image: str  # Base64 encoded
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BusinessKYC(BaseModel):
    cac_document: str  # Base64
    registration_id: str
    company_name: str
    director_name: str
    director_phone: str
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
    email: Optional[EmailStr] = None
    password: str
    phone: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # Basic phone validation - allow +234... or 0...
            import re
            # Remove spaces and hyphens
            clean_phone = re.sub(r'[\s-]', '', v)
            # Check for E.164 format (e.g., +234...) or local format (0...)
            if not re.match(r'^(\+\d{1,3}|0)\d{9,14}$', clean_phone):
                raise ValueError('Invalid phone number format')
        return v
    
    @validator('email', always=True)
    def validate_email_or_phone(cls, v, values):
        if not v and not values.get('phone'):
            raise ValueError('Either email or phone number must be provided')
        return v

class UserLogin(BaseModel):
    email_or_phone: str
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_verified: bool = False
    wallet_balance: float = 0.0
    profile_picture: Optional[str] = None  # Base64 encoded image or URL
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
    verification_documents: Optional[Dict[str, str]] = None # Private R2 keys for KYC docs
    created_at: datetime = Field(default_factory=datetime.utcnow)

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


class DocumentType(str, Enum):
    CERTIFICATE_OF_INCORPORATION = "certificate_of_incorporation"
    TIN_CERTIFICATE = "tin_certificate"
    UTILITY_BILL = "utility_bill"
    NATIONAL_ID_DOC = "national_id_doc"
    HEADSHOT_PHOTO = "headshot_photo"
    DRIVERS_LICENSE = "drivers_license"

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

class BusinessType(str, Enum):
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    PARTNERSHIP = "partnership"
    LIMITED_LIABILITY_COMPANY = "limited_liability_company"
    COOPERATIVE = "cooperative"
    NGO = "ngo"

class IdentificationType(str, Enum):
    NIN = "nin"
    BVN = "bvn"
    DRIVERS_LICENSE = "drivers_license"
    VOTERS_CARD = "voters_card"
    INTERNATIONAL_PASSPORT = "international_passport"

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

class NotificationType(str, Enum):
    MENTION = "mention"
    LIKE = "like"
    COMMENT = "comment"
    SYSTEM = "system"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    message: str
    type: NotificationType
    is_read: bool = False
    link: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
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

# Communities System Models
class CommunityRole(str, Enum):
    CREATOR = "creator"          # Community creator (super admin)
    ADMIN = "admin"              # Admin granted by creator
    MEMBER = "member"            # Regular member

class CommunityPrivacy(str, Enum):
    PUBLIC = "public"            # Anyone can join
    PRIVATE = "private"          # Join by invitation/approval
    RESTRICTED = "restricted"    # Invite only

class Community(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    creator_id: str
    creator_username: str
    profile_picture: Optional[str] = None  # Community profile picture
    privacy: CommunityPrivacy = CommunityPrivacy.PUBLIC
    category: str  # e.g., "farming", "business", "trading"
    location: Optional[str] = None  # Community focus location
    cover_image: Optional[str] = None
    member_count: int = 0
    product_count: int = 0
    is_active: bool = True
    community_rules: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityMember(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    community_id: str
    user_id: str
    username: str
    role: CommunityRole = CommunityRole.MEMBER
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: Optional[str] = None  # User ID who invited this member
    is_active: bool = True

class CommunityProduct(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    community_id: str
    community_name: str  # For easier display
    title: str
    description: str
    price: float
    quantity_available: int
    unit_of_measure: str
    category: str
    images: List[str] = []
    seller_id: str
    seller_username: str
    location: str
    is_active: bool = True
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    group_buy_enabled: bool = False
    group_buy_min_quantity: Optional[int] = None
    group_buy_participants: List[str] = []  # User IDs in group buy
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityProductLike(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityProductComment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    username: str
    comment: str
    reply_to: Optional[str] = None  # ID of comment being replied to
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GroupBuyParticipant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    username: str
    quantity_requested: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FarmlandRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    farmer_id: str
    location: str  # Farmland location
    size: float
    size_unit: str = "hectare"  # acre, hectare, square_meter, square_kilometer
    size_hectares: Optional[float] = None  # Deprecated/Calculated
    crop_types: List[str]  # Types of crops grown
    soil_type: Optional[str] = None
    irrigation_method: Optional[str] = None
    coordinates: Optional[dict] = None  # GPS coordinates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class AgentFarmer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    farmer_id: str
    farmer_name: str
    farmer_phone: Optional[str] = None
    farmer_location: str
    linked_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    total_listings: int = 0
    total_sales: float = 0.0

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

# KYC Compliance Validation Helper Functions
def validate_kyc_compliance(user: dict, action: str = "general"):
    """
    Validate if user is KYC compliant for specific actions.
    
    Args:
        user: User document from database
        action: Type of action being performed (e.g., 'sales', 'register_farmers', 'post_products', 'collect_payments')
    
    Returns:
        bool: True if compliant, raises HTTPException if not
    """
    # Personal accounts don't require KYC
    if user.get("role") == "personal":
        return True
    
    # Check if KYC is required and approved
    kyc_status = user.get("kyc_status", "not_started")
    user_role = user.get("role", "")
    
    # Enhanced restrictions for agents - they must complete KYC before ANY platform actions
    if user_role == "agent":
        if kyc_status == "not_started":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "AGENT_KYC_REQUIRED",
                    "message": "Agents must complete their KYC verification before performing any actions on the platform. Please submit your KYC documents to get started.",
                    "kyc_status": kyc_status,
                    "verification_time": "Verification takes within 24 hours to verify",
                    "access_level": "view_only",
                    "required_actions": get_kyc_requirements(user)
                }
            )
        elif kyc_status == "pending":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "AGENT_KYC_PENDING", 
                    "message": "Your KYC is under review. You can access the platform to view but cannot onboard farmers or publish farm produce until your status changes to verified.",
                    "kyc_status": kyc_status,
                    "verification_time": "Verification typically completes within 24 hours",
                    "access_level": "view_only"
                }
            )
        elif kyc_status == "rejected":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "AGENT_KYC_REJECTED",
                    "message": "Your KYC was rejected. Please resubmit with correct documents. You can only view the platform until verification is completed.",
                    "kyc_status": kyc_status,
                    "access_level": "view_only",
                    "required_actions": get_kyc_requirements(user)
                }
            )
    
    # For other roles (business, farmer, etc.) - standard KYC validation
    if kyc_status != "approved":
        status_messages = {
            "not_started": "Please complete your KYC verification to perform this action",
            "pending": "Your KYC is under review. You can perform this action once approved", 
            "rejected": "Your KYC was rejected. Please resubmit with correct documents to continue"
        }
        
        action_context = {
            "sales": "receive payments or complete sales",
            "register_farmers": "register farmers to your network",
            "post_products": "post products for sale", 
            "collect_payments": "collect payments from customers"
        }
        
        context = action_context.get(action, "perform this action")
        message = f"KYC verification required to {context}. {status_messages.get(kyc_status, 'KYC verification required')}"
        
        raise HTTPException(
            status_code=403,
            detail={
                "error": "KYC_REQUIRED",
                "message": message,
                "kyc_status": kyc_status,
                "required_actions": get_kyc_requirements(user)
            }
        )
    
    return True

def get_kyc_requirements(user: dict) -> dict:
    """Get specific KYC requirements based on user type"""
    role = user.get("role", "")
    business_category = user.get("business_category", "")
    is_registered_business = user.get("is_registered_business", False)
    
    # Agent-specific KYC requirements
    if role == "agent":
        return {
            "type": "agent",
            "title": "Agent KYC Requirements",
            "description": "Specialized requirements for agricultural agents",
            "review_time": "1-3 business days",
            "documents": [
                "Headshot Photo (Camera captured)",
                "National ID Document (NIN or BVN)",
                "Utility Bill (Address verification)",
                "Bank Statement (Financial verification)",
                "Certificate of Incorporation (If registered business)",
                "TIN Certificate (If registered business)"
            ],
            "information_required": [
                "Business name and address",
                "Personal identification details",
                "Agricultural experience",
                "Target operation locations",
                "Expected farmer network size"
            ],
            "endpoint": "/api/kyc/agent/submit",
            "benefits_after_approval": [
                "Register and verify farmers",
                "Earn commission on farmer sales",
                "Access agent dashboard",
                "Build farmer network"
            ]
        }
    
    # Farmer-specific KYC requirements  
    elif role == "farmer":
        return {
            "type": "farmer",
            "title": "Farmer KYC Requirements", 
            "description": "Verification requirements for farmers",
            "review_time": "24-48 hours (agent-verified) or 2-5 business days (self-verified)",
            "documents": [
                "Headshot Photo (Camera captured)",
                "National ID Document (NIN or BVN)", 
                "Farm Photo (Show your farming area)",
                "Land Ownership Document (Certificate or lease agreement)"
            ],
            "information_required": [
                "Personal identification details",
                "Farm location and size",
                "Primary crops grown",
                "Farming experience",
                "Land ownership status"
            ],
            "verification_options": [
                {
                    "method": "agent_verified",
                    "title": "Agent Verification (Recommended)",
                    "description": "Get verified by a registered agent for faster processing",
                    "processing_time": "24-48 hours",
                    "benefits": ["Faster approval", "Agent support", "Market access guidance"]
                },
                {
                    "method": "self_verified", 
                    "title": "Self Verification",
                    "description": "Submit documents directly for verification",
                    "processing_time": "2-5 business days",
                    "benefits": ["Direct submission", "Full document control"]
                }
            ],
            "endpoint": "/api/kyc/farmer/submit"
        }
    
    # Business KYC requirements (existing)
    elif role == "business":
        if is_registered_business:
            return {
                "type": "registered_business",
                "title": "Registered Business KYC",
                "description": "Requirements for registered businesses",
                "review_time": "2-5 business days",
                "documents": [
                    "Business Registration Number",
                    "TIN Certificate", 
                    "Certificate of Incorporation",
                    "Business Address Verification (Utility Bill)"
                ],
                "endpoint": "/api/kyc/registered-business/submit"
            }
        else:
            return {
                "type": "unregistered_business",
                "title": "Unregistered Business KYC", 
                "description": "Requirements for unregistered businesses",
                "review_time": "2-5 business days",
                "documents": [
                    "NIN or BVN",
                    "Headshot Photo (Camera)",
                    "National ID Document",
                    "Utility Bill (Address Verification)"
                ],
                "endpoint": "/api/kyc/unregistered-entity/submit"
            }
    
    # Default for other roles
    else:
        return {
            "type": "unregistered_entity", 
            "title": "Standard KYC Requirements",
            "documents": [
                "NIN or BVN",
                "Headshot Photo (Camera)",
                "National ID Document", 
                "Utility Bill (Address Verification)"
            ],
            "endpoint": "/api/kyc/unregistered-entity/submit"
        }

def validate_agent_farmer_registration(agent_user: dict, farmer_data: dict):
    """
    Validate that agents can register farmers and are responsible for their KYC.
    
    Args:
        agent_user: Agent user document
        farmer_data: Farmer registration data
    
    Returns:
        bool: True if valid, raises HTTPException if not
    """
    # Only agents can register farmers
    if agent_user.get("role") != "agent":
        raise HTTPException(
            status_code=403,
            detail="Only verified agents can register farmers to the platform"
        )
    
    # Agent must be KYC compliant to register farmers
    validate_kyc_compliance(agent_user, "register_farmers")
    
    # For now, we'll log that the agent is taking responsibility
    # In the future, we can add more strict validation requirements
    print(f"Agent {agent_user.get('username')} registering farmer {farmer_data.get('farmer_name')} - Agent is responsible for farmer's initial validation")
    
    return True

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Pyramyd API"}

@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    # Check if user exists
    query = {"$or": [{"username": user_data.username}]}
    if user_data.email:
        query["$or"].append({"email": user_data.email})
    if user_data.phone:
        query["$or"].append({"phone": user_data.phone})
        
    if db.users.find_one(query):
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
            "phone": user.phone,
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
            "first_name": user.get('first_name', ''),
            "last_name": user.get('last_name', ''),
            "username": user.get('username', ''),
            "email": user.get('email', user.get('email_or_phone')),
            "role": user.get('role'),
            "platform": platform
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

@app.get("/api/users/public/{username}")
async def get_public_user_profile(username: str):
    """Get public user profile information for transparency"""
    try:
        user = users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return only public information
        public_profile = {
            "username": user.get("username"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "role": user.get("role"),
            "profile_picture": user.get("profile_picture"),
            "business_name": user.get("business_name"),
            "business_category": user.get("business_category"),
            "business_description": user.get("business_description"),
            "average_rating": user.get("average_rating", 5.0),
            "total_ratings": user.get("total_ratings", 0),
            "kyc_status": user.get("kyc_status"),
            "is_verified": user.get("is_verified", False)
        }
        
        return public_profile
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting public user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    only_preorders: Optional[bool] = None,
    search_term: Optional[str] = None,
    seller_type: Optional[str] = None,
    platform: Optional[str] = None,  # 'home' or 'farm_deals'
    global_search: Optional[bool] = None,  # Search across all platforms
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
                
            if seller_type:
                products_query["seller_type"] = seller_type
            
            # Platform-based filtering (skip if global search)
            if not global_search:
                if platform == "home":
                    # Home page: Only business and supplier products
                    products_query["seller_type"] = {"$in": ["business", "supplier"]}
                elif platform == "farm_deals":
                    # Farm Deals page: Only farmer and agent products
                    products_query["seller_type"] = {"$in": ["farmer", "agent"]}
                
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
            
            # Platform-based filtering for preorders (skip if global search)
            if not global_search:
                if platform == "home":
                    # Home page: Only business and supplier preorders
                    preorders_query["seller_type"] = {"$in": ["business", "supplier"]}
                elif platform == "farm_deals":
                    # Farm Deals page: Only farmer and agent preorders
                    preorders_query["seller_type"] = {"$in": ["farmer", "agent"]}
            
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

@app.get("/api/platform/vendor-charges")
async def get_vendor_platform_charges(platform_type: str = "home"):
    """
    Get transparent breakdown of platform charges for vendors.
    This shows vendors what they will pay/receive before posting products.
    
    Query params:
    - platform_type: "home", "farmhub", or "community"
    """
    try:
        if platform_type == "farmhub":
            return {
                "platform": "FARMHUB (Farm Deals)",
                "platform_type": "farmhub",
                "vendor_commission": {
                    "rate": "10%",
                    "description": "Service charge extracted from your sales",
                    "example": "If you sell ₦10,000 worth of products, ₦1,000 goes to platform"
                },
                "buyer_service_charge": {
                    "rate": "0%",
                    "description": "No additional charge to buyers"
                },
                "vendor_receives": "90% of product price",
                "delivery_fees": "Platform manages delivery (varies by distance and quantity)",
                "example_calculation": {
                    "product_price": 10000,
                    "vendor_commission_deducted": 1000,
                    "vendor_receives": 9000,
                    "buyer_pays_product": 10000,
                    "buyer_pays_service": 0,
                    "buyer_pays_delivery": "Varies",
                    "note": "Vendor gets 90%, platform gets 10% + delivery fees"
                }
            }
        elif platform_type == "home":
            return {
                "platform": "HOME (PyExpress)",
                "platform_type": "home",
                "vendor_commission": {
                    "rate": "2.5%",
                    "description": "Commission extracted from your sales",
                    "example": "If you sell ₦10,000 worth of products, ₦250 goes to platform"
                },
                "buyer_service_charge": {
                    "rate": "3%",
                    "description": "Service charge paid by buyer (added to their total)",
                    "example": "Buyer pays ₦10,000 product + ₦300 service charge"
                },
                "vendor_receives": "97.5% of product price",
                "buyer_sees": "Product price + 3% service charge + delivery",
                "delivery_fees": "Platform manages delivery (varies by distance, capped at ₦40,000)",
                "transparency_note": "⚠️ IMPORTANT: You receive 97.5% of your product price. The 3% service charge is paid by the buyer, not deducted from your sales.",
                "example_calculation": {
                    "product_price": 10000,
                    "vendor_commission_deducted": 250,
                    "vendor_receives": 9750,
                    "buyer_pays_product": 10000,
                    "buyer_pays_service_charge": 300,
                    "buyer_pays_delivery": "Varies",
                    "total_platform_revenue": "₦250 (from vendor) + ₦300 (from buyer) + delivery = ₦550 + delivery",
                    "note": "Vendor gets 97.5%, buyer pays 3% service charge, platform gets both"
                }
            }
        else:  # community
            return {
                "platform": "COMMUNITY",
                "platform_type": "community",
                "vendor_commission": {
                    "rate": "2.5%",
                    "description": "Commission extracted from your sales",
                    "example": "If you sell ₦10,000 worth of products, ₦250 goes to platform"
                },
                "buyer_service_charge": {
                    "rate": "5%",
                    "description": "Service charge paid by buyer (added to their total)",
                    "example": "Buyer pays ₦10,000 product + ₦500 service charge"
                },
                "vendor_receives": "97.5% of product price",
                "buyer_sees": "Product price + 5% service charge + delivery",
                "delivery_fees": "Platform manages delivery (varies by distance and quantity)",
                "transparency_note": "⚠️ IMPORTANT: You receive 97.5% of your product price. The 5% service charge is paid by the buyer, not deducted from your sales.",
                "example_calculation": {
                    "product_price": 10000,
                    "vendor_commission_deducted": 250,
                    "vendor_receives": 9750,
                    "buyer_pays_product": 10000,
                    "buyer_pays_service_charge": 500,
                    "buyer_pays_delivery": "Varies",
                    "total_platform_revenue": "₦250 (from vendor) + ₦500 (from buyer) + delivery = ₦750 + delivery",
                    "note": "Vendor gets 97.5%, buyer pays 5% service charge, platform gets both"
                }
            }
    except Exception as e:
        print(f"Error getting vendor charges: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get vendor charges")






@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    product = db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.pop('_id', None)
    return product

@app.post("/api/orders")
async def create_order(items: List[CartItem], delivery_address: str, current_user: dict = Depends(get_current_user)):
    # KYC Compliance Check for Order Creation
    validate_kyc_compliance(current_user, "collect_payments")
    
    return process_create_order(items, delivery_address, current_user, db)

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
    return orders

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
    return process_create_group_order(order_data, current_user, db)

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
    return process_create_outsourced_order(produce, category, quantity, expected_price, location, current_user, db)

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
        # KYC Compliance Check for Pre-order Creation
        validate_kyc_compliance(current_user, "post_products")
        
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
        
        # KYC Compliance Check for Sellers (when order is completed, seller receives payment)
        # Note: We check the seller's KYC, not the buyer's
        seller = users_collection.find_one({"id": product["seller_id"]})
        if seller:
            validate_kyc_compliance(seller, "collect_payments")
        
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
            "delivery_status": "pending",  # Unified delivery status
            "delivery_handler_id": product.get("seller_id"), # Seller is default handler
            "delivery_notes": "",
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
        
        # Send email notification when order is completed/delivered
        if status_update.status in [OrderStatus.DELIVERED, "completed"]:
            # Get updated order with all details
            updated_order = db.orders.find_one({"order_id": order_id})
            if updated_order:
                updated_order.pop('_id', None)
                send_order_completion_email(updated_order)
        
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

@app.post("/api/delivery/status")
async def update_delivery_status(
    status_data: dict,  # {order_id: str, status: str, notes: str}
    current_user: dict = Depends(get_current_user)
):
    """Update delivery status (Agent/Farmer only)"""
    try:
        order = db.orders.find_one({"order_id": status_data.get("order_id")})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
            
        # Verify permission: User must be the seller OR an agent managing the seller
        is_authorized = False
        if current_user["id"] == order.get("delivery_handler_id"):
            is_authorized = True
        elif current_user["role"] == "agent":
             # Check if agent manages this farmer/seller
             managed_farmer = agent_farmers_collection.find_one({
                 "agent_id": current_user["id"],
                 "farmer_id": order.get("delivery_handler_id")
             })
             if managed_farmer:
                 is_authorized = True
                 
        if not is_authorized:
             raise HTTPException(status_code=403, detail="Not authorized to manage this delivery")

        update_fields = {
            "delivery_status": status_data.get("status"),
            "updated_at": datetime.utcnow()
        }
        
        # Secure Delivery Logic
        response_data = {"message": "Delivery status updated", "status": status_data.get("status")}
        
        if status_data.get("status") == "delivered":
            # Instead of marking as delivered immediately, mark as verification_pending
            # Generate 6-digit OTP
            import random
            otp = str(random.randint(100000, 999999))
            
            update_fields["delivery_status"] = "verification_pending"
            update_fields["delivery_code"] = otp
            
            response_data["status"] = "verification_pending"
            response_data["delivery_code"] = otp
            response_data["message"] = "Delivery requires buyer confirmation"

        if status_data.get("notes"):
            update_fields["delivery_notes"] = status_data.get("notes")

        db.orders.update_one(
            {"order_id": status_data.get("order_id")},
            {"$set": update_fields}
        )
        
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating delivery status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/delivery/confirm")
async def confirm_delivery(
    confirmation_data: dict, # {order_id: str, code: str}
    current_user: dict = Depends(get_current_user)
):
    """Confirm delivery with OTP (Buyer only)"""
    try:
        order_id = confirmation_data.get("order_id")
        code = confirmation_data.get("code")
        
        if not order_id or not code:
            raise HTTPException(status_code=400, detail="Order ID and Code are required")
            
        order = db.orders.find_one({"order_id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
            
        # Verify user is the buyer
        if order.get("buyer_username") != current_user["username"]:
             raise HTTPException(status_code=403, detail="Only the buyer can confirm delivery")
             
        # Verify Status
        if order.get("delivery_status") != "verification_pending":
             raise HTTPException(status_code=400, detail="Order is not pending verification")
             
        # Verify Code
        if order.get("delivery_code") != code:
             raise HTTPException(status_code=400, detail="Invalid delivery code")
             
        # Complete Delivery
        db.orders.update_one(
            {"order_id": order_id},
            {
                "$set": {
                    "delivery_status": "delivered",
                    "delivered_at": datetime.now(),
                    "updated_at": datetime.utcnow(),
                    "status": "completed" # Also update main order status
                },
                "$unset": {"delivery_code": ""} # Remove code after use
            }
        )
        
        return {"message": "Delivery confirmed successfully", "status": "delivered"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error confirming delivery: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to confirm delivery")

@app.get("/api/agent/deliveries")
async def get_agent_deliveries(current_user: dict = Depends(get_current_user)):
    """Get deliveries for farmers managed by this agent"""
    if current_user["role"] != "agent":
        raise HTTPException(status_code=403, detail="Only agents can access this endpoint")
        
    try:
        # Get list of managed farmers
        managed_farmers = list(agent_farmers_collection.find({"agent_id": current_user["id"]}))
        farmer_ids = [f["farmer_id"] for f in managed_farmers]
        
        # Also include the agent's own sales if any
        farmer_ids.append(current_user["id"])
        
        # Find pending deliveries
        orders = list(db.orders.find({
            "delivery_handler_id": {"$in": farmer_ids},
            "status": {"$ne": "cancelled"} # Show all active orders
        }).sort("created_at", -1))
        
        for order in orders:
            order.pop('_id', None)
            
        return {"orders": orders}
    except Exception as e:
        print(f"Error getting agent deliveries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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

# ==================== ENHANCED KYC SYSTEM ENDPOINTS ====================

@app.post("/api/kyc/documents/upload")
async def upload_kyc_document(
    document_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Upload KYC documents (including camera-captured headshots)"""
    try:
        user_id = current_user["id"]
        
        # Validate required fields
        required_fields = ["document_type", "file_data", "file_name", "mime_type"]
        for field in required_fields:
            if not document_data.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate document type
        if document_data["document_type"] not in [e.value for e in DocumentType]:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # Validate file size (max 10MB)
        file_data = document_data["file_data"]
        if len(file_data) > 10 * 1024 * 1024:  # 10MB in bytes
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
        
        # Create document record
        document = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "document_type": document_data["document_type"],
            "file_name": document_data["file_name"],
            "file_data": file_data,
            "file_size": len(file_data),
            "mime_type": document_data["mime_type"],
            "uploaded_at": datetime.utcnow(),
            "verified": False,
            "verification_notes": None
        }
        
        kyc_documents_collection.insert_one(document)
        
        # Log the action
        log_audit_action(user_id, "document_upload", "kyc_document", document["id"], {
            "document_type": document_data["document_type"],
            "file_name": document_data["file_name"]
        })
        
        return {
            "message": "Document uploaded successfully",
            "document_id": document["id"],
            "document_type": document_data["document_type"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading KYC document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload document")

@app.post("/api/kyc/registered-business/submit")
async def submit_registered_business_kyc(
    kyc_data: RegisteredBusinessKYC,
    current_user: dict = Depends(get_current_user)
):
    """Submit KYC for registered businesses"""
    try:
        user_id = current_user["id"]
        user_role = current_user.get("role")
        
        if user_role != "business":
            raise HTTPException(status_code=400, detail="This KYC type is only for business accounts")
        
        # Check if user has business registration status as "registered"
        user = users_collection.find_one({"id": user_id})
        if not user or user.get("business_registration_status") != "registered":
            raise HTTPException(status_code=400, detail="This KYC type requires a registered business account")
        
        # Validate required documents are uploaded
        required_docs = ["certificate_of_incorporation_id", "tin_certificate_id", "utility_bill_id"]
        for doc_field in required_docs:
            doc_id = getattr(kyc_data, doc_field, None)
            if doc_id:
                doc = kyc_documents_collection.find_one({"id": doc_id, "user_id": user_id})
                if not doc:
                    raise HTTPException(status_code=400, detail=f"Invalid or missing document: {doc_field}")
        
        # Update user KYC status and data
        kyc_update = {
            "kyc_status": KYCStatus.PENDING,
            "kyc_submitted_at": datetime.utcnow(),
            "kyc_type": "registered_business",
            "registered_business_kyc": kyc_data.dict(),
            "updated_at": datetime.utcnow()
        }
        
        users_collection.update_one(
            {"id": user_id},
            {"$set": kyc_update}
        )
        
        # Log the action
        log_audit_action(user_id, "kyc_submission", "user", user_id, {
            "kyc_type": "registered_business",
            "business_name": user.get("business_name")
        })
        
        return {
            "message": "Registered business KYC submitted successfully",
            "status": "pending",
            "estimated_review_time": "3-7 business days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting registered business KYC: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit KYC")

@app.post("/api/kyc/unregistered-entity/submit")
async def submit_unregistered_entity_kyc(
    kyc_data: UnregisteredEntityKYC,
    current_user: dict = Depends(get_current_user)
):
    """Submit KYC for unregistered businesses, agents, and farmers"""
    try:
        user_id = current_user["id"]
        user_role = current_user.get("role")
        
        if user_role not in ["business", "agent", "farmer"]:
            raise HTTPException(status_code=400, detail="This KYC type is for business, agent, or farmer accounts")
        
        # For businesses, check if unregistered
        if user_role == "business":
            user = users_collection.find_one({"id": user_id})
            if user and user.get("business_registration_status") == "registered":
                raise HTTPException(status_code=400, detail="Registered businesses should use the registered business KYC process")
        
        # Validate required documents are uploaded
        required_docs = ["headshot_photo_id", "national_id_document_id", "utility_bill_id"]
        for doc_field in required_docs:
            doc_id = getattr(kyc_data, doc_field, None)
            if doc_id:
                doc = kyc_documents_collection.find_one({"id": doc_id, "user_id": user_id})
                if not doc:
                    raise HTTPException(status_code=400, detail=f"Invalid or missing document: {doc_field}")
        
        # Validate identification number format (basic validation)
        if kyc_data.identification_type == IdentificationType.NIN:
            if len(kyc_data.identification_number) != 11 or not kyc_data.identification_number.isdigit():
                raise HTTPException(status_code=400, detail="NIN must be 11 digits")
        elif kyc_data.identification_type == IdentificationType.BVN:
            if len(kyc_data.identification_number) != 11 or not kyc_data.identification_number.isdigit():
                raise HTTPException(status_code=400, detail="BVN must be 11 digits")
        
        # Update user KYC status and data
        kyc_update = {
            "kyc_status": KYCStatus.PENDING,
            "kyc_submitted_at": datetime.utcnow(),
            "kyc_type": "unregistered_entity",
            "unregistered_entity_kyc": kyc_data.dict(),
            "updated_at": datetime.utcnow()
        }
        
        users_collection.update_one(
            {"id": user_id},
            {"$set": kyc_update}
        )
        
        # Log the action
        log_audit_action(user_id, "kyc_submission", "user", user_id, {
            "kyc_type": "unregistered_entity",
            "identification_type": kyc_data.identification_type,
            "user_role": user_role
        })
        
        return {
            "message": f"{user_role.title()} KYC submitted successfully",
            "status": "pending",
            "estimated_review_time": "2-5 business days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting unregistered entity KYC: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit KYC")

@app.post("/api/kyc/agent/submit")
async def submit_agent_kyc(kyc_data: AgentKYC, current_user: dict = Depends(get_current_user)):
    """Submit KYC for agents with specialized requirements"""
    try:
        user_id = current_user["id"]
        
        # Ensure user is an agent
        if current_user.get("role") != "agent":
            raise HTTPException(status_code=403, detail="Only agents can submit agent KYC")
        
        # Validate identification number format
        if kyc_data.identification_type == "NIN" and len(kyc_data.identification_number) != 11:
            raise HTTPException(status_code=400, detail="NIN must be exactly 11 digits")
        elif kyc_data.identification_type == "BVN" and len(kyc_data.identification_number) != 11:
            raise HTTPException(status_code=400, detail="BVN must be exactly 11 digits")
        
        # Store KYC data
        kyc_record = kyc_data.dict()
        kyc_record["user_id"] = user_id
        kyc_record["submission_date"] = datetime.utcnow().isoformat()
        kyc_record["status"] = "pending"
        kyc_record["kyc_type"] = "agent"
        
        # Determine if registered or unregistered business
        if kyc_data.business_registration_number and kyc_data.tax_identification_number:
            kyc_record["business_status"] = "registered"
        else:
            kyc_record["business_status"] = "unregistered"
        
        agent_kyc_collection.insert_one(kyc_record)
        
        # Update user KYC status
        users_collection.update_one(
            {"id": user_id},
            {
                "$set": {
                    "kyc_status": "pending",
                    "kyc_submission_date": datetime.utcnow().isoformat(),
                    "kyc_type": "agent"
                }
            }
        )
        
        # Log audit trail
        audit_logs_collection.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": "kyc_submission",
            "resource_type": "agent_kyc",
            "details": {
                "kyc_type": "agent",
                "business_status": kyc_record["business_status"],
                "target_locations": kyc_data.target_locations
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "message": "Agent KYC submitted successfully",
            "status": "pending",
            "business_status": kyc_record["business_status"],
            "estimated_review_time": "1-3 business days for agents",
            "next_steps": [
                "Upload required documents (headshot, national ID, utility bill)",
                "If registered business: Upload incorporation certificate and TIN certificate",
                "Await verification from our team",
                "Start building your farmer network once approved"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting agent KYC: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit agent KYC")


        
# --- AGENT FEATURES ---

class AgentRegisterFarmer(BaseModel):
    first_name: str
    last_name: str
    phone: str
    gender: str
    date_of_birth: str
    address: str
    farm_location: str
    farm_size: str
    crops: str
    headshot: Optional[str] = None

@app.post("/api/agent/farmers/register")
async def register_farmer_by_agent(data: AgentRegisterFarmer, current_user: dict = Depends(get_current_user)):
    """Allows an agent to register a farmer under their management"""
    if current_user.get("role") != "agent":
        raise HTTPException(status_code=403, detail="Only agents can register farmers")
        
    # Check if phone already registered
    if db.users.find_one({"phone": data.phone}):
        raise HTTPException(status_code=400, detail="Farmer phone number already registered")
        
    farmer_id = str(uuid.uuid4())
    username = f"farmer_{data.first_name.lower()}_{uuid.uuid4().hex[:4]}"
    
    # Create Farmer User
    farmer = {
        "id": farmer_id,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "username": username,
        "phone": data.phone, # No email required for managed farmer
        "role": "farmer",
        "gender": data.gender,
        "date_of_birth": data.date_of_birth,
        "address": data.address,
        "is_managed": True,
        "managed_by": current_user["id"],
        "farm_details": [{
            "address": data.farm_location,
            "size": data.farm_size,
            "products": [c.strip() for c in data.crops.split(',')]
        }],
        "profile_picture": data.headshot,
        "created_at": datetime.utcnow()
    }
    
    db.users.insert_one(farmer)
    
    # Link to Agent
    db.agent_farmers.insert_one({
        "agent_id": current_user["id"],
        "farmer_id": farmer_id,
        "created_at": datetime.utcnow()
    })
    
    return {"message": "Farmer registered successfully", "farmer_id": farmer_id}

@app.get("/api/agent/farmers")
async def get_agent_farmers(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "agent":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    links = list(db.agent_farmers.find({"agent_id": current_user["id"]}))
    farmer_ids = [l["farmer_id"] for l in links]
    
    farmers = list(db.users.find({"id": {"$in": farmer_ids}}, {"_id": 0, "password": 0}))
    
    # Enrich with stats (mocked or real)
    for f in farmers:
        # Get product count
        f["product_count"] = db.products.count_documents({"farmer_id": f["id"]})
        # Get total sales (mock for now or aggregated)
        f["total_sales"] = 0 
        f["location"] = f["farm_details"][0]["address"] if f.get("farm_details") else "Unknown"
        
    return {"farmers": farmers}
    
# Update Product Model in server.py (Find existing Product class and update it or add new fields dynamically)
# Since we are using dicts mostly in the endpoints, we'll just check the body.



@app.post("/api/products")
async def create_product(product_data: ProductCreate, current_user: dict = Depends(get_current_user)):
    if not current_user.get('role'):
        raise HTTPException(status_code=400, detail="Please select a role first")

    # KYC Compliance Check
    validate_kyc_compliance(current_user, "post_products")
    
    # Check if user can create products (Base Permission)
    allowed_roles = ['farmer', 'agent', 'supplier_farm_inputs', 'supplier_food_produce', 'processor']
    if current_user.get('role') not in allowed_roles:
         # Exception: Community creation might be open to others? 
         # For now sticking to base roles.
        raise HTTPException(status_code=403, detail="Not authorized to create products")

    # Initialize variables
    managed_by_agent_id = None
    seller_id = current_user['id']
    seller_name = current_user['username']
    seller_type = current_user.get('role')
    product_platform = product_data.platform
    
    # --- CASE 1: AGENT POSTING FOR FARMER ---
    if product_data.farmer_id:
        if current_user.get('role') != 'agent':
             raise HTTPException(status_code=403, detail="Only agents can post for others")
        
        # Verify agent manages this farmer
        link = db.agent_farmers.find_one({"agent_id": current_user['id'], "farmer_id": product_data.farmer_id})
        if not link:
            raise HTTPException(status_code=403, detail="You do not manage this farmer")
            
        # Switch seller identity to the farmer
        managed_by_agent_id = current_user['id']
        farmer_user = users_collection.find_one({"id": product_data.farmer_id})
        if not farmer_user:
             raise HTTPException(status_code=404, detail="Farmer not found")
             
        seller_id = farmer_user['id']
        seller_name = farmer_user['username']
        seller_type = 'farmer' # Effectively a farmer listing

    # --- CASE 2: COMMUNITY LISTING ---
    if product_data.community_id:
        # User must provide community name
        if not product_data.community_name:
             raise HTTPException(status_code=400, detail="Community name is required for community listings")
        
        # Validate Community Existence
        community = communities_collection.find_one({"id": product_data.community_id})
        if not community:
             raise HTTPException(status_code=404, detail="Community not found")
        
        # Verify User Membership (Affiliation)
        member = community_members_collection.find_one({
            "community_id": product_data.community_id, 
            "user_id": current_user['id'], # The one posting must be a member
            "is_active": True
        })
        if not member:
             raise HTTPException(status_code=403, detail="You must be a member of the community to list products")
             
        # Platform for community is usually PyHub or PyExpress depending on goods?
        # Typically PyHub for local community exchange, but logic remains same as per role.
        
    # --- CASE 3: STANDARD (FARMER/BUSINESS) ---
    # Implicitly handled if neither of above. 'seller_id' remains current_user.

    # --- Platform Determination Logic (Role Based) ---
    user_role = seller_type # Use effective seller type
    
    # Enforce platform restrictions based on EFFECTIVE role
    if user_role == 'farmer':
        product_platform = 'pyhub'
    elif user_role == 'supplier_farm_inputs':
        product_platform = 'pyhub'
        farm_input_categories = ['fertilizer', 'herbicides', 'pesticides', 'seeds']
        if product_data.category.value not in farm_input_categories:
            raise HTTPException(status_code=400, detail="Farm input suppliers can only list farm input products")
    elif user_role == 'supplier_food_produce':
        product_platform = 'pyexpress'
        food_categories = ['sea_food', 'grain', 'legumes', 'vegetables', 'spices', 'fruits', 'fish', 'meat', 'packaged_goods']
        if product_data.category.value not in food_categories:
            raise HTTPException(status_code=400, detail="Food produce suppliers can only list food products")
    elif user_role == 'processor':
        product_platform = 'pyexpress'
    
    # --- Product Creation ---
    product = Product(
        seller_id=seller_id,
        seller_name=seller_name,
        seller_type=seller_type,
        seller_profile_picture=current_user.get('profile_picture'), 
        business_name=current_user.get('business_name'),
        platform=product_platform,
        managed_by_agent_id=managed_by_agent_id,
        community_id=product_data.community_id, # Link product to community
        **{k: v for k, v in product_data.dict().items() if k != 'platform'}
    )
    
    # --- Pricing & Service Charges ---
    if user_role == 'farmer':
        # 30% markup for farmers on PyHub
        product.price_per_unit = product_data.price_per_unit * 1.30
    elif user_role in ['supplier_food_produce', 'processor']:
        # 10% service charge deduction for PyExpress suppliers
        product.price_per_unit = product_data.price_per_unit * 0.90
    
    # --- Discounts ---
    if product_data.has_discount and product_data.discount_value:
        product.original_price = product.price_per_unit
        
        if product_data.discount_type == "percentage":
            discount_amount = product.price_per_unit * (product_data.discount_value / 100)
            product.discount_amount = round(discount_amount, 2)
            product.price_per_unit = round(product.price_per_unit - discount_amount, 2)
        elif product_data.discount_type == "fixed":
            product.discount_amount = product_data.discount_value
            product.price_per_unit = round(product.price_per_unit - product_data.discount_value, 2)
            
        if product.price_per_unit < 0:
            raise HTTPException(status_code=400, detail="Discount cannot exceed product price")
    
    # --- Logistics ---
    if product_data.logistics_managed_by == "seller":
        if product_data.seller_delivery_fee is None:
            raise HTTPException(status_code=400, detail="Delivery fee is required when seller manages logistics")
    
    # --- Database Insertion ---
    product_dict = product.dict()
    db.products.insert_one(product_dict)
    
    # If Community Product, Increment Count
    if product_data.community_id:
         communities_collection.update_one(
             {"id": product_data.community_id},
             {"$inc": {"product_count": 1}}
         )
    
    return {"message": "Product created successfully", "product_id": product.id}

class FarmerKYCSubmission(BaseModel):
    verification_method: str = "self_verified"  # "self_verified" or "agent_verified"
    verifying_agent_id: Optional[str] = None
    farm_size_hectares: Optional[float] = None
    primary_crops: Optional[List[str]] = []
    farm_location: Optional[str] = None
    additional_notes: Optional[str] = None

@app.post("/api/kyc/farmer")
async def submit_farmer_kyc(
    kyc_data: FarmerKYCSubmission,
    current_user: dict = Depends(get_current_user)
):
    """Submit KYC for farmer (Self or Agent assisted)"""
    try:
        user_id = current_user["id"]
        
        # Determine target user (if agent is submitting for farmer)
        if kyc_data.verification_method == "agent_verified":
            if current_user["role"] != "agent":
                raise HTTPException(status_code=403, detail="Only agents can submit verified KYC")
            # Logic to find farmer would go here, but for now assuming it updates current_user or specific farmer passed
            
        estimated_time = "24-48 hours" if kyc_data.verification_method == "self_verified" else "Instant"
        
        # Create KYC record
        kyc_record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": "farmer",
            "status": "pending" if kyc_data.verification_method == "self_verified" else "verified",
            "verification_method": kyc_data.verification_method,
            "data": kyc_data.dict(),
            "submitted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        db.kyc_submissions.insert_one(kyc_record)
        
        users_collection.update_one(
            {"id": user_id},
            {
                "$set": {
                    "kyc_status": kyc_record["status"],
                    "kyc_submission_date": datetime.utcnow().isoformat(),
                    "kyc_type": "farmer",
                    "verifying_agent_id": kyc_data.verifying_agent_id if kyc_data.verification_method == "agent_verified" else None
                }
            }
        )
        
        # Log audit trail
        audit_logs_collection.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": "kyc_submission",
            "resource_type": "farmer_kyc",
            "details": {
                "kyc_type": "farmer",
                "verification_method": kyc_data.verification_method,
                "verifying_agent_id": kyc_data.verifying_agent_id,
                "farm_size_hectares": kyc_data.farm_size_hectares,
                "primary_crops": kyc_data.primary_crops
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "message": "Farmer KYC submitted successfully",
            "status": kyc_record["status"],
            "verification_method": kyc_data.verification_method,
            "estimated_review_time": estimated_time,
            "next_steps": [
                "Upload required documents (headshot, national ID, farm photo)",
                "Upload land ownership documents if applicable",
                "Await verification from our team",
                "Start listing your produce once approved"
            ] if kyc_data.verification_method == "self_verified" else [
                "Documents verified by your agent",
                "Faster processing due to agent verification", 
                "Await final approval from our team",
                "Start listing your produce once approved"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting farmer KYC: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit farmer KYC")

# Communities API Endpoints
@app.post("/api/communities")
async def create_community(community_data: dict, current_user: dict = Depends(get_current_user)):
    """Create a new community"""
    try:
        # Validate required fields
        required_fields = ["name", "description", "category"]
        for field in required_fields:
            if field not in community_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create community record
        community = {
            "id": str(uuid.uuid4()),
            "name": community_data["name"],
            "description": community_data["description"],
            "creator_id": current_user["id"],
            "creator_username": current_user["username"],
            "privacy": community_data.get("privacy", "public"),
            "category": community_data["category"],
            "location": community_data.get("location"),
            "cover_image": community_data.get("cover_image"),
            "member_count": 1,  # Creator is first member
            "product_count": 0,
            "is_active": True,
            "community_rules": community_data.get("community_rules", []),
            "tags": community_data.get("tags", []),
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = communities_collection.insert_one(community)
        
        # Add creator as first member with creator role
        creator_member = {
            "id": str(uuid.uuid4()),
            "community_id": community["id"],
            "user_id": current_user["id"],
            "username": current_user["username"],
            "role": "creator",
            "joined_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        community_members_collection.insert_one(creator_member)
        
        # Remove MongoDB _id field before returning (it's not JSON serializable)
        community.pop('_id', None)
        
        return {
            "message": "Community created successfully",
            "community": community
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating community: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create community")

@app.get("/api/communities")
async def get_communities(
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get list of communities with filtering"""
    try:
        query = {"is_active": True}
        
        if category:
            query["category"] = category
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"tags": {"$in": [search]}}
            ]
        
        skip = (page - 1) * limit
        communities = list(communities_collection.find(query).skip(skip).limit(limit))
        
        # Remove MongoDB _id field from all communities
        for community in communities:
            community.pop('_id', None)
        
        return {
            "communities": communities,
            "page": page,
            "limit": limit,
            "total": communities_collection.count_documents(query)
        }
        
    except Exception as e:
        print(f"Error getting communities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get communities")

@app.get("/api/communities/featured/products")
async def get_featured_community_products(limit: int = 6):
    """Get featured products from communities"""
    try:
        # Get products from active communities, sorted by likes and recent
        products = list(community_products_collection.find(
            {"is_active": True}
        ).sort([("likes_count", -1), ("created_at", -1)]).limit(limit))
        
        # Remove MongoDB _id field
        for product in products:
            product.pop('_id', None)
        
        return {"products": products}
        
    except Exception as e:
        print(f"Error getting featured community products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get featured products")

@app.get("/api/communities/{community_id}")
async def get_community_details(community_id: str):
    """Get detailed community information"""
    try:
        community = communities_collection.find_one({"id": community_id})
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")
        
        community.pop('_id', None)
        
        # Get recent members
        members = list(community_members_collection.find(
            {"community_id": community_id, "is_active": True}
        ).limit(10))
        
        for member in members:
            member.pop('_id', None)
        
        # Get recent products (Top 5/6)
        products = list(db.products.find(
            {"community_id": community_id, "status": "active"}
        ).sort("created_at", -1).limit(6))
        
        for product in products:
            product.pop('_id', None)
        
        community["recent_members"] = members
        community["recent_products"] = products
        
        return community
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting community details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get community details")

@app.get("/api/communities/{community_id}/products")
async def get_community_products(
    community_id: str,
    limit: int = 20,
    skip: int = 0
):
    """Get all products for a specific community"""
    try:
        products = list(db.products.find(
            {"community_id": community_id, "status": "active"}
        ).sort("created_at", -1).skip(skip).limit(limit))
        
        count = db.products.count_documents({"community_id": community_id, "status": "active"})
        
        for product in products:
            product.pop('_id', None)
            
        return {
            "products": products,
            "total": count,
            "limit": limit,
            "skip": skip
        }
    except Exception as e:
        print(f"Error getting community products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get community products")

@app.post("/api/communities/{community_id}/join")
async def join_community(community_id: str, current_user: dict = Depends(get_current_user)):
    """Join a community"""
    try:
        # Check if community exists
        community = communities_collection.find_one({"id": community_id})
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")
        
        # Check if already a member
        existing_member = community_members_collection.find_one({
            "community_id": community_id,
            "user_id": current_user["id"]
        })
        
        if existing_member:
            if existing_member["is_active"]:
                raise HTTPException(status_code=400, detail="Already a member of this community")
            else:
                # Reactivate membership
                community_members_collection.update_one(
                    {"id": existing_member["id"]},
                    {"$set": {"is_active": True, "joined_at": datetime.utcnow().isoformat()}}
                )
        else:
            # Add as new member
            member = {
                "id": str(uuid.uuid4()),
                "community_id": community_id,
                "user_id": current_user["id"],
                "username": current_user["username"],
                "role": "member",
                "joined_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            community_members_collection.insert_one(member)
        
        # Update community member count
        active_members_count = community_members_collection.count_documents({
            "community_id": community_id,
            "is_active": True
        })
        
        communities_collection.update_one(
            {"id": community_id},
            {"$set": {"member_count": active_members_count}}
        )
        
        return {"message": "Successfully joined community"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error joining community: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to join community")

@app.post("/api/communities/{community_id}/members/{user_id}/promote")
async def promote_member(
    community_id: str, 
    user_id: str, 
    promotion_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Promote a member to admin (only creators can do this)"""
    try:
        # Check if current user is creator
        current_member = community_members_collection.find_one({
            "community_id": community_id,
            "user_id": current_user["id"],
            "is_active": True
        })
        
        if not current_member or current_member["role"] != "creator":
            raise HTTPException(status_code=403, detail="Only community creators can promote members")
        
        # Check if target user is a member
        target_member = community_members_collection.find_one({
            "community_id": community_id,
            "user_id": user_id,
            "is_active": True
        })
        
        if not target_member:
            raise HTTPException(status_code=404, detail="User is not a member of this community")
        
        new_role = promotion_data.get("role", "admin")
        if new_role not in ["admin", "member"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin' or 'member'")
        
        # Update member role
        community_members_collection.update_one(
            {"id": target_member["id"]},
            {"$set": {"role": new_role}}
        )
        
        return {"message": f"Member {new_role} role updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error promoting member: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to promote member")

@app.post("/api/communities/{community_id}/posts")
async def create_community_post(
    community_id: str,
    post_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a new post in a community (Admin/Creator only)"""
    try:
        # Verify community exists
        community = communities_collection.find_one({"id": community_id})
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")

        # Verify permission (Admin/Creator)
        member = community_members_collection.find_one({
            "community_id": community_id,
            "user_id": current_user["id"],
            "is_active": True
        })

        if not member or member["role"] not in ["admin", "creator"]:
            raise HTTPException(status_code=403, detail="Only admins can post in this community")

        # Create Post
        post = {
            "id": str(uuid.uuid4()),
            "community_id": community_id,
            "user_id": current_user["id"],
            "author_name": f"{current_user['first_name']} {current_user['last_name']}",
            "author_role": member["role"],
            "content": post_data.get("content"),
            "images": post_data.get("images", []), # List of image URLs
            "product_id": post_data.get("product_id"), # Optional: Link to a product
            "likes_count": 0,
            "comments_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }

        community_posts_collection.insert_one(post)
        post.pop('_id', None)

        return {"message": "Post created successfully", "post": post}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create post")

@app.get("/api/communities/{community_id}/posts")
async def get_community_posts(
    community_id: str,
    limit: int = 20,
    skip: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get posts for a community"""
    try:
        # Check membership (Optional: Public communities might allow viewing without joining)
        # For now, let's allow anyone to view public communities, members for private
        community = communities_collection.find_one({"id": community_id})
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")

        if community.get("privacy") == "private":
             member = community_members_collection.find_one({
                "community_id": community_id,
                "user_id": current_user["id"],
                "is_active": True
            })
             if not member:
                 raise HTTPException(status_code=403, detail="Must be a member to view posts")

        posts = list(community_posts_collection.find(
            {"community_id": community_id, "is_active": True}
        ).sort("created_at", -1).skip(skip).limit(limit))

        for post in posts:
            post.pop('_id', None)
            # Check if user liked this post
            like = post_likes_collection.find_one({
                "post_id": post["id"],
                "user_id": current_user["id"]
            })
            post["has_liked"] = bool(like)

        return {"posts": posts}

    except Exception as e:
        print(f"Error getting posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch posts")

@app.post("/api/communities/{community_id}/members/add")
async def add_community_member(
    community_id: str,
    member_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Add a member to community (Admin/Creator only)"""
    try:
        # Verify permission
        current_member = community_members_collection.find_one({
            "community_id": community_id,
            "user_id": current_user["id"],
            "is_active": True
        })
        
        if not current_member or current_member["role"] not in ["admin", "creator"]:
            raise HTTPException(status_code=403, detail="Only admins can add members")

        target_identifier = member_data.get("identifier") # Email or Phone or Username
        if not target_identifier:
             raise HTTPException(status_code=400, detail="Member email, phone or username required")

        # Find User
        target_user = users_collection.find_one({
            "$or": [
                {"email": target_identifier},
                {"phone": target_identifier},
                {"username": target_identifier},
                {"email_or_phone": target_identifier}
            ]
        })

        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if already member
        existing = community_members_collection.find_one({
            "community_id": community_id,
            "user_id": target_user["id"]
        })

        if existing and existing["is_active"]:
             raise HTTPException(status_code=400, detail="User is already a member")

        if existing:
            # Reactivate
             community_members_collection.update_one(
                {"id": existing["id"]},
                {"$set": {"is_active": True, "role": "member", "joined_at": datetime.utcnow().isoformat()}}
            )
        else:
            # Add new
            new_member = {
                "id": str(uuid.uuid4()),
                "community_id": community_id,
                "user_id": target_user["id"],
                "username": target_user["username"],
                "role": "member",
                "joined_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            community_members_collection.insert_one(new_member)

        # Update count
        count = community_members_collection.count_documents({"community_id": community_id, "is_active": True})
        communities_collection.update_one({"id": community_id}, {"$set": {"member_count": count}})

        return {"message": "Member added successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding member: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add member")

@app.delete("/api/communities/{community_id}/members/{user_id}")
async def remove_community_member(
    community_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a member from community (Admin/Creator only)"""
    try:
         # Verify permission
        current_member = community_members_collection.find_one({
            "community_id": community_id,
            "user_id": current_user["id"],
            "is_active": True
        })
        
        if not current_member or current_member["role"] not in ["admin", "creator"]:
            raise HTTPException(status_code=403, detail="Only admins can remove members")
            
        # Prevent removing self (must leave instead)
        if user_id == current_user["id"]:
             raise HTTPException(status_code=400, detail="Cannot remove yourself. Use leave endpoint.")

        # Check target member
        target_member = community_members_collection.find_one({
            "community_id": community_id,
            "user_id": user_id,
            "is_active": True
        })

        if not target_member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Remove member (Soft delete)
        community_members_collection.update_one(
            {"id": target_member["id"]},
            {"$set": {"is_active": False, "left_at": datetime.utcnow().isoformat()}}
        )

        # Update count
        count = community_members_collection.count_documents({"community_id": community_id, "is_active": True})
        communities_collection.update_one({"id": community_id}, {"$set": {"member_count": count}})

        return {"message": "Member removed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error removing community member: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove member")


# --- UNIFIED CHECKOUT & CROSS-PLATFORM LOGIC ---

class UnifiedCheckoutItem(BaseModel):
    product_id: str
    quantity: float
    unit: str
    unit_specification: Optional[str] = None
    delivery_method: str = "platform"  # platform, offline, dropoff
    delivery_address: Optional[str] = None
    dropoff_location_id: Optional[str] = None

class UnifiedCheckoutRequest(BaseModel):
    items: List[UnifiedCheckoutItem]
    callback_url: str

@app.post("/api/checkout/unified")
async def unified_checkout(
    payload: UnifiedCheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Handle unified checkout for mixed cart items.
    Creates individual orders but initializes a single payment.
    """
    total_amount_kobo = 0
    created_order_ids = []
    
    # 1. Validate & Create Orders
    for item in payload.items:
        product = db.products.find_one({"id": item.product_id})
        if not product:
            continue
            
        # Calculate Costs
        item_price = product["price_per_unit"]
        total_item_cost = item_price * item.quantity
        
        # Calculate Delivery/Service Fees
        delivery_fee = 0
        if item.delivery_method == "platform":
            delivery_fee = 1000 # Placeholder fixed fee
            
        platform_type = product.get("platform", "home")
        
        # Create Order Record
        order_id = f"PY_ORD-{uuid.uuid4().hex[:8].upper()}"
        new_order = {
             "order_id": order_id,
             "buyer_id": current_user["id"],
             "buyer_username": current_user["username"],
             "seller_id": product["seller_id"],
             "product_id": product["id"],
             "product_details": product,
             "quantity": item.quantity,
             "unit": item.unit,
             "total_amount": total_item_cost + delivery_fee,
             "delivery_fee": delivery_fee,
             "status": "pending_payment",
             "payment_status": "pending",
             "created_at": datetime.utcnow(),
             "platform": platform_type,
             "delivery_method": item.delivery_method,
             "delivery_address": item.delivery_address,
             "unified_checkout_group": "PENDING_GROUP_ID", # Link orders together
             "is_unified": True
        }
        
        # Insert Order
        result = db.orders.insert_one(new_order)
        created_order_ids.append(order_id)
        
        # Add to total for payment
        total_amount_kobo += naira_to_kobo(total_item_cost + delivery_fee)

    # 2. Initialize Payment (Aggregated)
    if total_amount_kobo > 0:
        paystack_data = {
            "email": current_user["email"],
            "amount": total_amount_kobo,
            "callback_url": payload.callback_url,
            "metadata": {
                 "unified_checkout": True,
                 "order_ids": created_order_ids
            }
        }
        
        # Note: We need a valid reference
        reference = f"PY_UNI-{uuid.uuid4().hex[:12]}"
        paystack_data["reference"] = reference
        
        # Update orders with reference
        db.orders.update_many(
            {"order_id": {"$in": created_order_ids}},
            {"$set": {"payment_reference": reference}}
        )

        response = paystack_request("POST", "/transaction/initialize", paystack_data)
        
        return {
             "authorization_url": response["data"]["authorization_url"],
             "reference": reference,
             "total_amount": kobo_to_naira(total_amount_kobo)
        }
    
    return {"message": "No valid items to checkout"}

@app.post("/api/paystack/webhook")
async def paystack_webhook(request: Request):
    """
    Handle Paystack Webhooks for payment confirmation.
    """
    try:
        # Verify Signature
        payload = await request.body()
        signature = request.headers.get("x-paystack-signature")
        
        if not signature or not verify_paystack_signature(payload, signature):
            raise HTTPException(status_code=400, detail="Invalid signature")
            
        event_data = await request.json()
        event = event_data.get("event")
        data = event_data.get("data", {})
        
        if event == "charge.success":
            reference = data.get("reference")
            
            # Find all orders with this reference
            result = db.orders.update_many(
                {"payment_reference": reference},
                {"$set": {
                    "status": "confirmed",  
                    "payment_status": "paid",
                    "paid_at": datetime.utcnow()
                }}
            )
            print(f"Webhook: Updated {result.modified_count} orders for ref {reference}")
            
        elif event == "transfer.success":
             # Handle payout success
             transfer_code = data.get("transfer_code")
             
             # Find commission payout
             payout = db.commission_payouts.find_one({"transfer_code": transfer_code})
             if payout:
                 db.commission_payouts.update_one(
                     {"_id": payout["_id"]},
                     {"$set": {"status": "success", "paid_at": datetime.utcnow()}}
                 )
                 print(f"Webhook: Payout success for {transfer_code}")

        elif event == "transfer.failed":
             transfer_code = data.get("transfer_code")
             db.commission_payouts.update_one(
                 {"transfer_code": transfer_code},
                 {"$set": {"status": "failed", "reason": data.get("reason", "Unknown")}}
             )
             print(f"Webhook: Payout failed for {transfer_code}")
             
    except Exception as e:
        print(f"Webhook Error: {str(e)}")
        # Don't fail the webhook response to Paystack
        return {"status": "error", "message": str(e)}
        
    return {"status": "success"}


if __name__ == "__main__":
    # Start Server
    import uvicorn
    # Use PORT from environment or default to 5000 as requested
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}...")
    # Using string import allows reloading
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
