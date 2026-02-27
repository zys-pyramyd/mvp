
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

class GroupBuyingRequest(BaseModel):
    produce: str
    category: str
    quantity: int
    location: str

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

@router.post("/group-buying/recommendations")
async def get_price_recommendations(
    request: GroupBuyingRequest, 
    current_user: dict = Depends(get_current_user)
):
    # ... (existing code)
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can access group buying")
    
    db = get_db()
    query = {
        "$or": [
            {"title": {"$regex": request.produce, "$options": "i"}},
            {"description": {"$regex": request.produce, "$options": "i"}}
        ],
        "category": request.category,
        "quantity_available": {"$gte": 1}
    }
    
    if request.location:
        query["location"] = {"$regex": request.location, "$options": "i"}
    
    matching_products = list(db.products.find(query))
    
    recommendations = []
    for product in matching_products:
        match_percentage = min(100, (product['quantity_available'] / request.quantity) * 100)
        recommendations.append({
            "product": product,
            "match_percentage": match_percentage
        })
        
    return recommendations

# --- Missing Endpoints Implementation ---

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
    from app.api.auth import get_password_hash
    from app.utils.id_generator import generate_tracking_id # Reuse or UUID
    
    # Check if phone/username exists
    if db.users.find_one({"phone": data.phone}):
         raise HTTPException(status_code=400, detail="Farmer with this phone already exists")
         
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
        "password": get_password_hash("123456"), # Default password, should change
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
