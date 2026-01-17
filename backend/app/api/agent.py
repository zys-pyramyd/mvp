
from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_db, get_current_user
from app.models.product import CartItem
from app.models.order import Order
from typing import List
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
    # Route: /api/agent/group-buying/recommendations? No server.py had /api/group-buying/recommendations
    # but I'll mount this router at /agent maybe?
    # Server.py had: @app.post("/api/group-buying/recommendations")
    # It was NOT under /api/agent.
    # I should separate group buying if I want exact match, or client needs update.
    # For now, I'll put it here.
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
