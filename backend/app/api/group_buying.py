# Auto-extracted Router
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api.deps import get_db, get_current_user
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import random
import string

from app.api.agent import GroupBuyingRequest
from order.community_order import process_create_group_order
from order.farm_deals_order import process_create_outsourced_order

router = APIRouter()

@router.post("/api/group-buying/recommendations")
async def get_price_recommendations(
    request:GroupBuyingRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Get price recommendations for group buying based on matching farms"""
    db = get_db()
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

@router.post("/api/group-buying/create-order")
async def create_group_order(
    order_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a group buying order"""
    db = get_db()
    return process_create_group_order(order_data, current_user, db)

@router.post("/api/outsource-order")
async def create_outsourced_order(
    produce: str,
    category: str,
    quantity: int,
    expected_price: float,
    location: str,
    current_user: dict = Depends(get_current_user)
):
    """Create an outsourced order for agents to bid on"""
    db = get_db()
    return process_create_outsourced_order(produce, category, quantity, expected_price, location, current_user, db)

@router.get("/api/outsourced-orders")
async def get_outsourced_orders(current_user:dict = Depends(get_current_user)):
    """Get available outsourced orders for agents to accept"""
    db = get_db()
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can view outsourced orders")
    
    orders = list(db.outsourced_orders.find({"status": "open"}).sort("created_at", -1))
    
    # Clean up response
    for order in orders:
        order.pop('_id', None)
    
    return orders

@router.post("/api/outsourced-orders/{order_id}/accept")
async def accept_outsourced_order(order_id:str, current_user: dict = Depends(get_current_user)):
    """Accept an outsourced order"""
    db = get_db()
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

