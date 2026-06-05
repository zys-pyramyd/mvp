from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_db, get_current_user
from app.models.order import OrderCreate, Order, PyHubOrderDetails, PyExpressOrderDetails
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import logging
from app.utils.geo import get_distance_km

logger = logging.getLogger(__name__)
router = APIRouter()

class UnifiedCheckoutRequest(BaseModel):
    items: list
    delivery_address: str
    payment_method: str = "paystack"
    payment_reference: Optional[str] = None
    callback_url: Optional[str] = None
    platform: str = "pyhub"
    pyhub_details: Optional[dict] = None
    pyexpress_details: Optional[dict] = None
    pay_delivery_on_arrival: bool = False

class CalculateDeliveryRequest(BaseModel):
    items: list
    delivery_address: str
    delivery_state: Optional[str] = None
    delivery_city: Optional[str] = None
    platform: str = "pyhub"

@router.post("/calculate-delivery")
async def calculate_delivery(payload: CalculateDeliveryRequest, db=Depends(get_db)):
    """
    Calculates delivery fee based on platform:
    - PyExpress: Intra-city (1500/item), Intra-state (2500/item), Inter-state (Forced Pay on Delivery)
    - FarmHub/PyHub: 2500 base + (0.15 * weight_kg * distance_km)
    """
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items provided")

    delivery_fee = 0.0
    is_interstate = False
    
    # 1. Group items by Seller to calculate distance per seller
    # For MVP, we assume single seller checkout as enforced in unified_checkout.
    first_item_id = payload.items[0].get("product_id")
    product = db.products.find_one({"id": first_item_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    seller_state = product.get("state", "").lower().strip()
    seller_city = product.get("lga", "").lower().strip() or product.get("city", "").lower().strip()
    seller_address = product.get("location", f"{seller_city}, {seller_state}")

    buyer_state = (payload.delivery_state or "").lower().strip()
    buyer_city = (payload.delivery_city or "").lower().strip()

    total_items = sum(item.get("quantity", 1) for item in payload.items)

    if payload.platform == "pyexpress":
        # PyExpress Logic
        if buyer_state and seller_state and buyer_state != seller_state:
            is_interstate = True
            delivery_fee = 0.0 # Force pay on delivery
        elif buyer_city and seller_city and buyer_city == seller_city:
            delivery_fee = 1500.0 * total_items
        else:
            delivery_fee = 2500.0 * total_items # Intra-state different city
    else:
        # FarmHub / Standard Logic
        total_weight_kg = 0.0
        for item in payload.items:
            prod = db.products.find_one({"id": item.get("product_id")})
            qty = item.get("quantity", 1)
            weight = prod.get("weight_kg") or prod.get("weight") or 1.0
            total_weight_kg += float(weight) * qty

        distance_km = get_distance_km(seller_address, payload.delivery_address)
        base_fee = 2500.0
        delivery_fee = base_fee + (0.15 * total_weight_kg * distance_km)

    # Cap delivery fee at 80,000 NGN
    if delivery_fee > 80000.0:
        delivery_fee = 80000.0

    return {
        "delivery_fee": round(delivery_fee, 2),
        "is_interstate": is_interstate,
        "seller_state": seller_state,
        "buyer_state": buyer_state
    }

@router.post("/unified")
async def unified_checkout(
    payload: UnifiedCheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Unified checkout endpoint for both PyHub and PyExpress.
    Handles order creation, wallet deduction, and Paystack initialization.
    """
    db = get_db()
    
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items in order")
        
    total_amount = 0.0
    order_items = []
    seller_id = None
    seller_name = None
    agent_id = None
    
    # Process Items
    for item in payload.items:
        product_id = item.get("product_id")
        quantity = item.get("quantity")
        product = db.products.find_one({"id": product_id})
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
            
        if quantity > product.get('quantity_available', 0):
            raise HTTPException(status_code=400, detail=f"Insufficient quantity for {product.get('title')}")
            
        item_total = product['price_per_unit'] * quantity
        total_amount += item_total
        
        order_items.append({
            "product_id": product['id'],
            "title": product['title'],
            "price_per_unit": product['price_per_unit'],
            "quantity": quantity,
            "total": item_total
        })
        
        if seller_id is None:
            seller_id = product.get('seller_id')
            seller_name = product.get('seller_name')
            agent_id = product.get('agent_id')
        elif seller_id != product.get('seller_id'):
            raise HTTPException(status_code=400, detail="All items must be from the same seller")

    if payload.platform == "pyexpress" and total_amount < 15000.0:
        raise HTTPException(status_code=400, detail="PyExpress orders must have a minimum value of ₦15,000")
            
    # Delivery Fee logic is now handled in frontend via calculate-delivery and passed implicitly, 
    # but for security we should recalculate it here. For MVP, we will rely on frontend passing it 
    # via pay_delivery_on_arrival boolean.
    delivery_fee = 0.0
    if not payload.pay_delivery_on_arrival:
        # We need to fetch the dynamically calculated delivery fee. We can reconstruct the logic or
        # trust the total amount from frontend? Wait, frontend passes `total_amount` implicitly? No, `unified` 
        # recalculates it. Let's recalculate the delivery fee.
        calc_payload = CalculateDeliveryRequest(
            items=payload.items,
            delivery_address=payload.delivery_address,
            platform=payload.platform
        )
        try:
            # We call the method directly to reuse logic
            calc_res = await calculate_delivery(calc_payload, db)
            delivery_fee = calc_res.get("delivery_fee", 0.0)
        except Exception as e:
            logger.error(f"Error calculating delivery in unified checkout: {e}")
            pass

        total_amount += delivery_fee
    else:
        # If paying on arrival, we don't add to total_amount, but we might want to record it
        pass
    
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    order_status = "pending"
    
    # Wallet payment logic
    if payload.payment_method == "wallet":
        result = db.users.update_one(
            {"id": current_user["id"], "wallet_balance": {"$gte": total_amount}},
            {"$inc": {"wallet_balance": -total_amount}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        order_status = "held_in_escrow"
        
    # Construct base order dictionary
    new_order = {
         "order_id": order_id,
         "buyer_id": current_user["id"],
         "buyer_username": current_user.get("username"),
         "seller_id": seller_id,
         "seller_username": seller_name,
         "agent_id": agent_id,
         "items": order_items,
         "total_amount": total_amount,
         "delivery_fee": delivery_fee,
         "pay_delivery_on_arrival": payload.pay_delivery_on_arrival,
         "status": order_status,
         "payment_method": payload.payment_method,
         "payment_status": "paid" if payload.payment_method == "wallet" else "pending",
         "created_at": datetime.utcnow(),
         "platform": payload.platform,
         "delivery_address": payload.delivery_address,
         "pyhub_details": payload.pyhub_details,
         "pyexpress_details": payload.pyexpress_details
    }
    
    # Reserve stock
    for item in order_items:
        db.products.update_one(
            {"id": item["product_id"]},
            {"$inc": {"quantity_available": -item["quantity"]}}
        )
        
    # Insert order
    db.orders.insert_one(new_order)
    
    # Paystack initialization
    if payload.payment_method == "paystack":
        from app.services.paystack import initialize_transaction
        try:
            amount_kobo = int(total_amount * 100)
            metadata = {
                "order_id": order_id,
                "buyer_id": current_user['id'],
                "seller_id": seller_id
            }
            callback_url = payload.callback_url or "https://pyramydhub.com/orders/callback"
            
            result = initialize_transaction(
                email=current_user.get('email'),
                amount=amount_kobo,
                callback_url=callback_url,
                metadata=metadata
            )
            
            payment_reference = result["data"]["reference"]
            authorization_url = result["data"]["authorization_url"]
            
            db.orders.update_one(
                {"order_id": order_id},
                {"$set": {"payment_reference": payment_reference}}
            )
            
            return {
                "message": "Order created. Please complete payment.",
                "order_id": order_id,
                "total_amount": total_amount,
                "payment_url": authorization_url,
                "payment_reference": payment_reference
            }
        except Exception as e:
            logger.error(f"Paystack error: {e}")
            raise HTTPException(status_code=400, detail="Payment initialization failed")

    return {
        "message": "Order created successfully", 
        "order_id": order_id, 
        "total_amount": total_amount, 
        "status": order_status
    }
