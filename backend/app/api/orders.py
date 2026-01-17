
from fastapi import APIRouter, HTTPException, Depends, status
from app.api.deps import get_db, get_current_user
from app.models.product import CartItem
from app.models.order import Order
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from app.api.deps import validate_kyc_compliance

router = APIRouter()

@router.post("/")
async def create_order(items: List[CartItem], delivery_address: str, current_user: dict = Depends(get_current_user)):
    if not items:
        raise HTTPException(status_code=400, detail="No items in order")
    
    validate_kyc_compliance(current_user, "collect_payments")
    
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
        
        if seller_id is None:
            seller_id = product['seller_id']
            seller_name = product['seller_name']
        elif seller_id != product['seller_id']:
            raise HTTPException(status_code=400, detail="All items must be from the same seller")
    
    
    from app.utils.id_generator import generate_tracking_id
    
    # Store explicit items list in order dict
    order_dict = {
        "order_id": generate_tracking_id(),
        "buyer_id": current_user['id'],
        "buyer_username": current_user['username'],
        "seller_id": seller_id,
        "seller_username": seller_name,
        "items": order_items,
        "total_amount": total_amount,
        "delivery_address": delivery_address,
        "status":"pending",
        "created_at": datetime.utcnow()
    }
    
    db.orders.insert_one(order_dict)
    
    # Update product quantities
    for item in items:
        db.products.update_one(
            {"id": item.product_id},
            {"$inc": {"quantity_available": -item.quantity}}
        )
    
    return {"message": "Order created successfully", "order_id": order_dict["order_id"], "total_amount": total_amount}

@router.get("/")
async def get_orders(current_user: dict = Depends(get_current_user)):
    db = get_db()
    # Get orders where user is buyer or seller
    orders = list(db.orders.find({
        "$or": [
            {"buyer_id": current_user['id']},
            {"seller_id": current_user['id']}
        ]
    }).sort("created_at", -1))
    
    for order in orders:
        order.pop('_id', None)
        if "created_at" in order and isinstance(order["created_at"], datetime):
            order["created_at"] = order["created_at"].isoformat()
    
    return orders

@router.post("/{order_id}/confirm-delivery")
async def confirm_delivery(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    Confirm delivery of an order.
    Releases funds from escrow to seller.
    """
    db = get_db()
    order = db.orders.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Check permissions: Only Buyer or Admin can confirm delivery?
    # Or maybe Seller can if proof provided? 
    # Usually Buyer confirms receipt.
    if order['buyer_id'] != current_user['id'] and current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only buyer can confirm delivery")
        
    if order['status'] != 'held_in_escrow':
         raise HTTPException(status_code=400, detail="Order is not in escrow")
         
    # Process Payout
    from app.services.payout_service import process_order_payout
    success, message = await process_order_payout(order_id, db)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
        
    return {"message": "Delivery confirmed and funds released", "order_id": order_id}
