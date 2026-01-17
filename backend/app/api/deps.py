
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import settings
from app.db.mongodb import get_database

security = HTTPBearer()

def get_db():
    return get_database()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get('user_id')
        
        db = get_db()
        user = db.users.find_one({'id': user_id})
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_admin(current_user: dict = Depends(get_current_user)):
    """Validates that the current user is an admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def get_kyc_requirements(user: dict) -> dict:
    """Get specific KYC requirements based on user type"""
    role = user.get("role", "")
    business_category = user.get("business_category", "")
    is_registered_business = user.get("is_registered_business", False)
    # Basic implementation - in real app would return structure seen in server.py
    return {"message": "Please submit required documents."}

def validate_kyc_compliance(user: dict, action: str = "general"):
    """
    Validate if user is KYC compliant for specific actions.
    """
    # Personal accounts don't require KYC
    if user.get("role") == "personal":
        return True
    
    kyc_status = user.get("kyc_status", "not_started")
    user_role = user.get("role", "")
    
    if user_role == "agent":
        if kyc_status in ["not_started", "pending", "rejected"]:
             raise HTTPException(
                status_code=403,
                detail={"error": "AGENT_KYC_REQUIRED", "message": f"Agent must be KYC verified. Current status: {kyc_status}"}
            )
            
    if kyc_status != "approved":
        raise HTTPException(
            status_code=403,
            detail={"error": "KYC_REQUIRED", "message": f"KYC verification required for '{action}'. Current status: {kyc_status}"}
        )
    
    return True
