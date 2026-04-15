
from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_db, get_current_user
from app.models.product import CartItem
from app.models.order import Order
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

# Local Request Models
class AgentPurchaseOption(BaseModel):
    commission_type: str  # "percentage" or "collect_after_delivery"
    customer_id: str
    delivery_address: str

AGENT_COMMISSION_RATES = {'purchase': 0.05, 'sales': 0.05}

router = APIRouter()

@router.post("/purchase")
async def agent_purchase(
    items: List[CartItem], 
    purchase_option: AgentPurchaseOption,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can use this endpoint")
    
    if not items:
        raise HTTPException(status_code=400, detail="No items in order")
    
    db = get_db()
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
    
    commission_rate = AGENT_COMMISSION_RATES['purchase']
    commission_amount = total_amount * commission_rate
    
    # Store order
    order_data = {
        "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
        "buyer_id": purchase_option.customer_id,
        "buyer_name": "Customer (via Agent)",
        "seller_id": seller_id,
        "seller_name": seller_name,
        "items": order_items,
        "total_amount": total_amount,
        "delivery_address": purchase_option.delivery_address,
        "agent_id": current_user['id'],
        "agent_commission_type": purchase_option.commission_type,
        "agent_commission_amount": commission_amount,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    db.orders.insert_one(order_data)
    
    for item in items:
        db.products.update_one(
            {"id": item.product_id},
            {"$inc": {"quantity_available": -item.quantity}}
        )
        
    return {
        "message": "Agent purchase successful",
        "order_id": order_data["order_id"],
        "total_amount": total_amount,
        "commission_amount": commission_amount
    }

# --- Agent Farmer & Delivery Endpoints ---

@router.get("/farmers")
async def get_managed_farmers(current_user: dict = Depends(get_current_user)):
    """Get farmers registered by this agent"""
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents access this")
        
    db = get_db()
    # Find users with role='farmer' and agent_id=current_user['id']
    farmers = list(db.users.find({"role": "farmer", "agent_id": current_user['id']}))
    
    # Enrich with stats if needed (product count, sales)
    for farmer in farmers:
        farmer['id'] = farmer.get('id') or str(farmer['_id'])
        farmer.pop('_id', None)
        farmer.pop('password', None) # Security
        
        # Stats
        farmer['product_count'] = db.products.count_documents({"seller_id": farmer['id']})
        # Calculate sales (this is expensive aggregation, simplify for MVP)
        farmer['total_sales'] = 0 
        
    return {"farmers": farmers}

@router.get("/farmers/lookup")
async def lookup_farmer(identifier: str, current_user: dict = Depends(get_current_user)):
    """Lookup farmer by phone, email, or username for product listing validation."""
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can lookup farmers")
        
    db = get_db()
    # Find farmer under this agent by identifier
    query = {
        "role": "farmer",
        "agent_id": current_user['id'],
        "$or": [
            {"phone": identifier},
            {"email": identifier},
            {"username": identifier}
        ]
    }
    
    farmer = db.users.find_one(query)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found or not managed by you")
        
    return {
        "first_name": farmer.get("first_name"),
        "last_name": farmer.get("last_name"),
        "farmer_id": farmer.get("id") or str(farmer.get("_id"))
    }


# ---------------------------------------------------------------------------
# Agent-side verification for self-registered farmers
# ---------------------------------------------------------------------------
# When a farmer self-registers and provides an agent's username/ID as their
# sponsor, they land in a "pending_agent_review" state. The agent (not admin)
# can then approve or reject them from their own dashboard.

@router.get("/farmers/pending-review")
async def get_farmers_pending_agent_review(current_user: dict = Depends(get_current_user)):
    """
    Farmers who self-registered, linked this agent as sponsor, and are
    awaiting the agent's identity confirmation (not yet admin-verified).
    """
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents access this")

    db = get_db()
    farmers = list(db.users.find({
        "role": "farmer",
        "agent_id": current_user['id'],
        "agent_review_status": "pending"
    }))

    for f in farmers:
        f.pop('_id', None)
        f.pop('password', None)
        f.pop('bvn', None)

    return {"farmers": farmers}


class AgentFarmerDecision(BaseModel):
    reason: str = ""  # Optional — required for reject


@router.post("/farmers/{farmer_id}/agent-verify")
async def agent_verify_farmer(
    farmer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Agent confirms they have met this self-registered farmer in person and
    vouches for their identity. Marks them as agent-verified.
    Admin still makes the final is_verified decision via /pyadmin.
    """
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can verify farmers")

    db = get_db()
    farmer = db.users.find_one({"id": farmer_id, "agent_id": current_user['id']})
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found or not managed by you")

    db.users.update_one(
        {"id": farmer_id},
        {"$set": {
            "agent_review_status": "approved",
            "agent_verified_by": current_user['id'],
            "agent_verified_at": datetime.utcnow(),
            "kyc_status": "pending_review",   # Escalate to admin queue
            "verification_note": f"Field-confirmed by Agent @{current_user['username']}"
        }}
    )

    # In-app notification to the farmer
    from app.api.notifications import create_notification
    create_notification(
        user_id=farmer_id,
        title="Agent Verification Approved",
        message=f"Your agent @{current_user['username']} has confirmed your registration. Your documents are now under admin review.",
        type="kyc",
        action_link="/profile"
    )

    return {"message": f"Farmer {farmer_id} confirmed by agent. Sent to admin for final verification."}


@router.post("/farmers/{farmer_id}/agent-reject")
async def agent_reject_farmer(
    farmer_id: str,
    body: AgentFarmerDecision,
    current_user: dict = Depends(get_current_user)
):
    """
    Agent indicates they cannot confirm this farmer's identity.
    Account remains inactive until resubmission.
    """
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can reject farmers")

    db = get_db()
    farmer = db.users.find_one({"id": farmer_id, "agent_id": current_user['id']})
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found or not managed by you")

    db.users.update_one(
        {"id": farmer_id},
        {"$set": {
            "agent_review_status": "rejected",
            "agent_verified_by": current_user['id'],
            "agent_verified_at": datetime.utcnow(),
            "kyc_status": "rejected",
            "is_verified": False,
            "verification_note": f"Rejected by Agent @{current_user['username']}. Reason: {body.reason}"
        }}
    )

    from app.api.notifications import create_notification
    create_notification(
        user_id=farmer_id,
        title="Agent Verification Declined",
        message=f"Your agent could not confirm your identity. Reason: {body.reason or 'Not specified'}. Please contact your agent or re-register.",
        type="kyc",
        action_link="/profile"
    )

    return {"message": f"Farmer {farmer_id} rejected by agent."}


class RegisterFarmerRequest(BaseModel):
    first_name: str
    last_name: str
    phone: str
    gender: str
    date_of_birth: str
    address_street: Optional[str] = None
    city: str
    state: str
    farm_location: str
    farm_size: str
    crops: str
    bank_account_number: str
    bank_code: str

@router.post("/farmers/register")
async def register_farmer(
    data: RegisterFarmerRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Agent registers a farmer.
    Farmer is auto-verified because Agent verified them.
    """
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can register farmers")
        
    db = get_db()
    from app.core.security import hash_password
    from app.utils.id_generator import generate_tracking_id # Reuse or UUID
    
    # Check if phone/username exists
    if db.users.find_one({"phone": data.phone}):
         raise HTTPException(status_code=400, detail="Farmer with this phone already exists")
         
    # Verify Bank Details
    from app.services.paystack import resolve_account_number
    bank_resolution = resolve_account_number(data.bank_account_number, data.bank_code)
    
    if not bank_resolution.get("status"):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid bank details. Paystack error: {bank_resolution.get('message', 'Unknown error')}"
        )
        
    resolved_name = bank_resolution["data"]["account_name"]
    
    # Simple name match validation
    first_name_lower = data.first_name.strip().lower()
    last_name_lower = data.last_name.strip().lower()
    resolved_name_lower = resolved_name.strip().lower()
    
    # We require either the first name or last name to be present in the bank account name
    if first_name_lower not in resolved_name_lower and last_name_lower not in resolved_name_lower:
        raise HTTPException(
            status_code=400,
            detail=f"Bank name mismatch. The resolved account name '{resolved_name}' does not match the farmer's name '{data.first_name} {data.last_name}'."
        )
        
    # Create Farmer User
    farmer_id = str(uuid.uuid4())
    username = f"{data.first_name.lower()}{data.last_name.lower()}{data.phone[-4:]}"
    
    farmer_dict = {
        "id": farmer_id,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "username": username,
        "email": f"{username}@placeholder.com", # Placeholder if no email
        "phone": data.phone,
        "role": "farmer",
        "agent_id": current_user['id'], # Link to Agent
        "is_verified": True, # AUTO-VERIFY
        "verification_status": "verified",
        "verification_note": f"Verified by Agent {current_user['username']}",
        "gender": data.gender,
        "date_of_birth": data.date_of_birth,
        "address": f"{data.address_street}, {data.city}, {data.state}",
        "city": data.city,
        "state": data.state,
        "farm_details": {
            "location": data.farm_location,
            "size": data.farm_size,
            "crops": data.crops
        },
        "bank_details": {
            "account_number": data.bank_account_number,
            "bank_code": data.bank_code,
            "account_name": resolved_name
        },
        "password": hash_password("123456"), # Default password, should change
        "created_at": datetime.utcnow()
    }
    
    db.users.insert_one(farmer_dict)
    
    return {"message": "Farmer registered successfully", "farmer_id": farmer_id}

@router.get("/deliveries")
async def get_agent_deliveries(current_user: dict = Depends(get_current_user)):
    """Get deliveries assigned to agent or their sales"""
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents access this")
    
    db = get_db()
    # Deliveries where agent is involved?
    # Or orders where agent's farmers are sellers?
    # Or agent purchase orders?
    # 'SellerDashboard.js' tabs imply 'Deliveries' might be logistics? 
    # Or just orders managed.
    # Let's return orders where agent_id is user OR seller's agent is user.
    
    # 1. Orders from Agent's Farmers
    farmers = list(db.users.find({"agent_id": current_user['id']}, {"id": 1}))
    farmer_ids = [f['id'] for f in farmers]
    
    query = {
        "$or": [
            {"agent_id": current_user['id']}, # Direct agent orders
            {"seller_id": {"$in": farmer_ids}} # Orders from managed farmers
        ]
    }
    
    orders = list(db.orders.find(query).sort("created_at", -1))
    for order in orders:
        order['_id'] = str(order['_id'])
        
    return {"orders": orders}
