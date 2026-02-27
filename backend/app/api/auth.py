
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from pydantic import BaseModel
from app.models.user import User, UserRegister, UserLogin, CompleteRegistration, ForgotPasswordRequest, ResetPasswordRequest
from app.core.security import hash_password, verify_password, create_token, encrypt_data, decrypt_data
from app.services.paystack import assign_dedicated_account, create_customer, resolve_bvn

# ... (omitted code) ...


from app.api.deps import get_db, get_current_user
from datetime import datetime, timedelta
import jwt
from app.core.config import settings
from typing import Optional
from app.core.rate_limit import limiter

router = APIRouter()

@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserRegister):
    db = get_db()
    # Check if user exists
    if db.users.find_one({"$or": [{"email": user_data.email}, {"username": user_data.username}]}):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        role=user_data.role
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

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, login_data: UserLogin):
    db = get_db()
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
        
    if user.get('is_blocked'):
        raise HTTPException(status_code=403, detail="You are blocked on the pyramyd marketplace due to violation of policy")
    
    token = create_token(user['id'])
    
    # Determine default platform based on role
    platform = "home"  # Default to home page
    if user.get('role') in ['farmer', 'agent', 'driver', 'storage_owner']:
        platform = "buy_from_farm"
    elif user.get('role') == 'admin':
        platform = "admin"
    
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

@router.post("/complete-registration")
async def complete_registration(registration_data: CompleteRegistration):
    db = get_db()
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
            user_role = 'personal'
        else:
            user_role = registration_data.buyer_type
    elif registration_data.user_path == 'partner':
        if registration_data.partner_type == 'business':
            user_role = "business"
        else:
            user_role = registration_data.partner_type
    

    print(f"DEBUG: Path={registration_data.user_path}, Type={registration_data.partner_type}, Category={registration_data.business_category}")
    print(f"DEBUG: Assigned UserRole={user_role}")

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
    if registration_data.business_category:
        user_dict['business_category'] = registration_data.business_category
    user_dict['verification_info'] = registration_data.verification_info or {}
    
    # Save document metadata (secure - only keys, not URLs)
    if registration_data.documents_submitted:
        user_dict['documents_submitted'] = registration_data.documents_submitted
        user_dict['documents_verified'] = False
        user_dict['documents_verified_at'] = None
    
    user_dict['is_verified'] = False  # Will be updated after verification process

    # Handle BVN for Partners (Store only, Verify later)
    if registration_data.user_path == 'partner' and registration_data.bvn:
        # Encrypt BVN (never store plain)
        user_dict['bvn'] = encrypt_data(registration_data.bvn)
        user_dict['wallet_balance'] = 0.0
    
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

@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, password_request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    db = get_db()
    user = db.users.find_one({"email": request.email})
    if not user:
        # Don't reveal if user exists
        return {"message": "If an account exists with this email, a reset link will be sent."}
    
    # Generate reset token (short lived - 1 hour)
    reset_token = jwt.encode(
        {'user_id': user['id'], 'type': 'password_reset', 'exp': datetime.utcnow() + timedelta(hours=1)},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    # Construct reset link
    # Assuming frontend is on port 3000 or served by nginx
    reset_link = f"{settings.PAYSTACK_API_URL.replace('https://api.paystack.co', 'http://localhost:3000')}/reset-password?token={reset_token}" # Hacky replacement or use env var
    # Better to use a FRONTEND_URL env var, defaulting to localhost:3000?
    frontend_url = "http://localhost:3000" # Hardcoded for now or use os.environ
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"

    # In a real app, send email here. For MVP, log it.
    print(f"PASSWORD RESET LINK for {request.email}: {reset_link}")
    
    return {"message": "If an account exists with this email, a reset link will be sent."}

@router.post("/reset-password")
@limiter.limit("3/minute")
async def reset_password(request: Request, reset_request: ResetPasswordRequest):
    try:
        payload = jwt.decode(request.token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get('type') != 'password_reset':
            raise HTTPException(status_code=400, detail="Invalid token type")
            
        user_id = payload.get('user_id')
        db = get_db()
        user = db.users.find_one({'id': user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Update password
        new_password_hash = hash_password(request.new_password)
        db.users.update_one({'id': user_id}, {'$set': {'password': new_password_hash}})
        
        return {"message": "Password updated successfully"}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None

@router.patch("/profile", response_model=dict)
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user profile details (First, Middle, Last Name).
    Essential for correcting names to match BVN/NIN for DVA creation.
    """
    db = get_db()
    updates = {k: v for k, v in profile_data.dict().items() if v is not None}
    
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
        
    # Update in DB
    result = db.users.update_one(
        {"id": current_user["id"]},
        {"$set": updates}
    )
    
    if result.modified_count == 0:
        # Check if fields were already same
        pass
        
    return {"message": "Profile updated successfully"}

class CreateDVARequest(BaseModel):
    bvn: Optional[str] = None

@router.post("/create-dva", response_model=dict)
async def create_dva(
    request: CreateDVARequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Manually trigger DVA creation for a partner.
    Allows updating BVN if one was not provided or needs correction.
    """
    db = get_db()
    
    # 0. Check if DVA already exists
    if current_user.get("dva_account_number"):
        raise HTTPException(status_code=400, detail="Dedicated Virtual Account already exists. You cannot create another one.")
    
    bvn_to_use = None
    
    # If BVN provided in request, update it
    if request.bvn:
        # Encrypt and store new BVN
        encrypted_new_bvn = encrypt_data(request.bvn)
        db.users.update_one({"id": current_user["id"]}, {"$set": {"bvn": encrypted_new_bvn}})
        bvn_to_use = request.bvn
    else:
        # Use stored BVN
        encrypted_bvn = current_user.get("bvn")
        if not encrypted_bvn:
            raise HTTPException(status_code=400, detail="No BVN provided or found on account. Please provide your BVN.")
        try:
            bvn_to_use = decrypt_data(encrypted_bvn)
        except Exception:
            raise HTTPException(status_code=500, detail="Error decrypting stored BVN")

    # 1. Verify Name Match (Optional but recommended before creating DVA)
    try:
        bvn_data = resolve_bvn(bvn_to_use)
        if not bvn_data or not bvn_data.get('status'):
            raise HTTPException(status_code=400, detail="BVN verification failed")

        resolved_data = bvn_data.get('data', {})
        bvn_first_name = resolved_data.get('first_name', '').lower()
        bvn_last_name = resolved_data.get('last_name', '').lower()
        
        user_first = current_user.get("first_name", "").lower()
        user_last = current_user.get("last_name", "").lower()
        
        fn_match = user_first in bvn_first_name or bvn_first_name in user_first
        ln_match = user_last in bvn_last_name or bvn_last_name in user_last
        
        if not fn_match or not ln_match:
            raise HTTPException(status_code=400, detail=f"Name mismatch! BVN Name: {resolved_data.get('first_name')} {resolved_data.get('last_name')}. Your Profile: {current_user.get('first_name')} {current_user.get('last_name')}. Please update your profile to match.")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during DVA manual creation verification: {e}")
        # Proceed or Fail? User explicitly asked for this feature to fix failures.
        # Let's fail if verification fails here, so they know why.
        raise HTTPException(status_code=400, detail="BVN Verification failed. Please ensure details match.")

    # 2. Create DVA
    dva_user_data = {
        "email": current_user['email'],
        "first_name": current_user['first_name'],
        "last_name": current_user['last_name'],
        "phone": current_user.get('phone')
    }
    
    dva_result = assign_dedicated_account(dva_user_data, bvn_to_use)
    
    if dva_result and dva_result.get('status') and dva_result.get('data'):
        dva_data = dva_result['data']
        account_number = dva_data.get('account_number')
        bank_info = dva_data.get('bank')
        bank_name = bank_info.get('name') if isinstance(bank_info, dict) else bank_info
        
        # Update user
        db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {
                "dva_account_number": account_number,
                "dva_bank_name": bank_name,
                "paystack_customer_code": dva_data.get('customer', {}).get('customer_code')
            }}
        )
        return {
            "message": "DVA created successfully",
            "account_number": account_number,
            "bank_name": bank_name
        }
    else:
        raise HTTPException(status_code=400, detail=f"DVA creation failed: {dva_result.get('message') if dva_result else 'Unknown error'}")
