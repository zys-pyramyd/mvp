
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import settings
# from app.db.mongodb import get_database
from database import get_db as get_database

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
    
    # Business KYC requirements
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
