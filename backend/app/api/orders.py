
from fastapi import APIRouter, HTTPException, Depends, status
from app.api.deps import get_db, get_current_user
from app.models.product import CartItem
from app.models.order import Order, OrderStatusUpdate
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()

@router.get("/my-orders")
async def get_my_orders(order_type: str = "buyer", current_user: dict = Depends(get_current_user)):
    """
    Get user's orders, filtered by role (buyer or seller).
    """
    db = get_db()
    query = {}
    
    if order_type == "seller":
        query["seller_id"] = current_user['id']
    else:
        query["buyer_id"] = current_user['id']
        
    orders = list(db.orders.find(query).sort("created_at", -1))
    
    for order in orders:
        order.pop('_id', None)
        if "created_at" in order and isinstance(order["created_at"], datetime):
            order["created_at"] = order["created_at"].isoformat()
            
    return {"orders": orders}

@router.put("/{order_id}/status")
async def update_order_status(order_id: str, status_update: OrderStatusUpdate, current_user: dict = Depends(get_current_user)):
    """
    Update order status (Seller/Admin only).
    """
    db = get_db()
    order = db.orders.find_one({"order_id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Check permissions
    if order['seller_id'] != current_user['id'] and current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only the seller can update order status")
        
    update_data = {"status": status_update.status}
    if status_update.delivery_status:
        update_data["delivery_status"] = status_update.delivery_status
        
    db.orders.update_one(
        {"order_id": order_id},
        {"$set": update_data}
    )
    
    return {"message": "Order status updated successfully", "order_id": order_id, "status": status_update.status}

class CreateOrderRequest(BaseModel):
    items: List[CartItem]
    delivery_address: str
    payment_method: Optional[str] = "paystack" # wallet, paystack
    payment_reference: Optional[str] = None

@router.post("/")
async def create_order(
    order_req: CreateOrderRequest, 
    current_user: dict = Depends(get_current_user)
):
    import logging
    logging.getLogger(__name__).debug("ENTERING CREATE_ORDER")
    items = order_req.items
    delivery_address = order_req.delivery_address
    
    if not items:
        raise HTTPException(status_code=400, detail="No items in order")
    
    # Exclude personal buyers from KYC, but enforce it for business buyers
    if current_user.get('role') == 'business' and current_user.get('kyc_status') != 'approved':
        raise HTTPException(status_code=403, detail="Business buyers must have approved KYC to place orders.")
    
    db = get_db()
    order_items = []
    total_amount = 0.0
    seller_id = None
    seller_name = None
    
    # Bulk fetch products to avoid N+1 DB roundtrips
    product_ids = [item.product_id for item in items]
    products = list(db.products.find({"id": {"$in": product_ids}}))
    product_map = {p["id"]: p for p in products}

    product_payout_account = None

    for item in items:
        product = product_map.get(item.product_id)
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
            
            # Phase 4: Capture specific product payout details if available
            if product.get("payout_account_number"):
                product_payout_account = {
                    "account_number": product.get("payout_account_number"),
                    "bank_code": product.get("payout_bank_code"),
                    "account_name": product.get("payout_account_name")
                }
        elif seller_id != product['seller_id']:
            raise HTTPException(status_code=400, detail="All items must be from the same seller")
            
    # Calculate Delivery Fee & Agent Buying Service Charge
    product_cost_total = total_amount
    total_delivery_fee = 0.0
    logistics_managed_by = "pyramyd" # Default
    
    # Check if Seller manages logistics for the first product
    first_product = product_map.get(items[0].product_id)
    if first_product and first_product.get('logistics_managed_by') == 'seller':
        logistics_managed_by = 'seller'
        for item in items:
            p = product_map.get(item.product_id)
            total_delivery_fee += float(p.get('seller_delivery_fee', 0.0) or 0.0)
    else:
        # Pyramyd manages logistics: Dynamic Geoapify Distance
        from app.utils.geo import get_distance_km
        seller = db.users.find_one({"id": seller_id})
        seller_address = seller.get("address", "") if seller else ""
        
        distance = get_distance_km(seller_address, delivery_address)
        platform_type = first_product.get('platform', 'pyhub') if first_product else 'pyhub'
        
        delivery_base_fee = 0.0
        delivery_per_km = 100.0 if platform_type == 'pyexpress' else 2.0
        total_delivery_fee = delivery_base_fee + (delivery_per_km * distance)

    # Calculate 4% Agent Buying Service Charge
    agent_service_charge = 0.0
    # Apply if the user is linked to an agent, or explicitly buying via agent
    if current_user.get('agent_id'):
        agent_service_charge = product_cost_total * 0.04

    # Build final cart total
    total_amount = product_cost_total + total_delivery_fee + agent_service_charge
    
    # --- GHOST STOCK PREVENTION: Reserve Stock First ---
    reserved_items = []
    try:
        for item in items:
            result = db.products.update_one(
                {
                    "id": item.product_id,
                    "quantity_available": {"$gte": item.quantity}  # Atomic stock check
                },
                {"$inc": {"quantity_available": -item.quantity}}
            )
            if result.modified_count == 0:
                raise Exception(f"Insufficient stock for product {item.product_id}")
            reserved_items.append(item)
    except Exception as e:
        # Rollback stock for previously reserved items in this order
        for r_item in reserved_items:
            db.products.update_one(
                {"id": r_item.product_id},
                {"$inc": {"quantity_available": r_item.quantity}}
            )
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Order creation failed prior to payment due to stock: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock for product. {str(e)}"
        )
        
    # Payment Handling
    order_status = "pending"
    
    # Generate order ID early for transaction tracking
    from app.utils.id_generator import generate_tracking_id
    order_id = generate_tracking_id()
    
    if order_req.payment_method == "wallet":
        # Atomic wallet deduction with balance check
        # This prevents race conditions where multiple requests could overdraw
        result = db.users.update_one(
            {
                "id": current_user["id"],
                "wallet_balance": {"$gte": total_amount}  # Atomic check
            },
            {"$inc": {"wallet_balance": -total_amount}}
        )
        
        if result.modified_count == 0:
            # Rollback stock because wallet failed
            for r_item in reserved_items:
                db.products.update_one(
                    {"id": r_item.product_id},
                    {"$inc": {"quantity_available": r_item.quantity}}
                )
                
            current_balance = db.users.find_one({"id": current_user["id"]}, {"wallet_balance": 1})
            if current_balance:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient wallet balance. Available: ₦{current_balance.get('wallet_balance', 0):.2f}, Required: ₦{total_amount:.2f}"
                )
            raise HTTPException(status_code=404, detail="User not found")
        
        # Log Transaction with order reference
        transaction = {
            "user_id": current_user["id"],
            "email": current_user.get("email"),
            "type": "debit",
            "category": "order_payment",
            "amount": total_amount,
            "reference": f"order_{order_id}",  # Link to order
            "description": f"Payment for Order {order_id}",
            "status": "success",
            "metadata": {
                "order_id": order_id,
                "seller_id": seller_id,
                "item_count": len(order_items)
            },
            "created_at": datetime.utcnow()
        }
        db.wallet_transactions.insert_one(transaction)
        order_status = "held_in_escrow"  # Funds held in escrow until delivery confirmation
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Wallet payment successful for order {order_id}. Amount: ₦{total_amount}, User: {current_user['id']}")
        
    elif order_req.payment_method == "paystack":
        # Paystack Payment Flow
        order_status = "pending"

    # Store explicit items list in order dict
    order_dict = {
        "order_id": order_id,
        "buyer_id": current_user['id'],
        "buyer_username": current_user['username'],
        "buyer_email": current_user.get('email'),
        "buyer_agent_id": current_user.get('agent_id'),
        "seller_id": seller_id,
        "seller_username": seller_name,
        "items": order_items,
        "total_amount": total_amount,
        "product_cost_total": product_cost_total,
        "total_delivery_fee": total_delivery_fee,
        "agent_service_charge": agent_service_charge,
        "logistics_managed_by": logistics_managed_by,
        "delivery_address": delivery_address,
        "payment_method": order_req.payment_method,
        "payment_reference": order_req.payment_reference,
        "payment_status": "pending" if order_req.payment_method == "paystack" else "paid",
        "status_history": [{"status": order_status, "date": datetime.utcnow()}],
        "status": order_status,
        "product_payout_account": product_payout_account, # Safe isolation of payout 
        "created_at": datetime.utcnow()
    }
    
    import logging
    logging.getLogger(__name__).debug(f"Inserting Order: {order_dict.get('order_id')}")
    try:
        db.orders.insert_one(order_dict)
    except Exception as e:
        # If order creation fails, refund wallet AND stock
        if order_req.payment_method == "wallet":
            db.users.update_one(
                {"id": current_user["id"]},
                {"$inc": {"wallet_balance": total_amount}}
            )
            
        for r_item in reserved_items:
            db.products.update_one(
                {"id": r_item.product_id},
                {"$inc": {"quantity_available": r_item.quantity}}
            )
            
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Order creation failed, wallet refunded and stock restored. Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")
    
    # If Paystack payment, initialize transaction and return payment URL
    if order_req.payment_method == "paystack":
        from app.services.paystack import initialize_transaction
        
        try:
            # Initialize Paystack transaction
            amount_kobo = int(total_amount * 100)
            
            # Prepare metadata
            metadata = {
                "order_id": order_id,
                "buyer_id": current_user['id'],
                "seller_id": seller_id,
                "item_count": len(order_items)
            }
            
            # Get callback URL from environment or use default
            import os
            frontend_url = os.getenv("FRONTEND_URL", "https://pyramydhub.com")
            callback_url = f"{frontend_url}/orders/{order_id}/payment-callback"
            
            result = initialize_transaction(
                email=current_user.get('email'),
                amount=amount_kobo,
                callback_url=callback_url,
                metadata=metadata
            )
            
            payment_reference = result["data"]["reference"]
            authorization_url = result["data"]["authorization_url"]
            
            # Update order with payment reference
            db.orders.update_one(
                {"order_id": order_id},
                {"$set": {"payment_reference": payment_reference}}
            )
            
            # Create pending transaction record
            transaction = {
                "user_id": current_user["id"],
                "email": current_user.get("email"),
                "type": "debit",
                "category": "order_payment",
                "amount": total_amount,
                "reference": payment_reference,
                "description": f"Payment for Order {order_id}",
                "status": "pending",
                "metadata": metadata,
                "created_at": datetime.utcnow()
            }
            db.wallet_transactions.insert_one(transaction)
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Paystack payment initialized for order {order_id}. Amount: ₦{total_amount}, Reference: {payment_reference}, User: {current_user['id']}")
            
            return {
                "message": "Order created. Please complete payment.",
                "order_id": order_id,
                "total_amount": total_amount,
                "status": order_status,
                "payment_url": authorization_url,
                "payment_reference": payment_reference
            }
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Paystack payment initialization failed for order {order_id}. Error: {str(e)}")
            
            # Mark order as failed
            db.orders.update_one(
                {"order_id": order_id},
                {"$set": {"status": "payment_failed", "payment_error": str(e)}}
            )
            
            # Rollback product quantities
            for item in items:
                db.products.update_one(
                    {"id": item.product_id},
                    {"$inc": {"quantity_available": item.quantity}}  # Add back
                )
            
            raise HTTPException(
                status_code=400,
                detail=f"Payment initialization failed: {str(e)}"
            )
    
    return {"message": "Order created successfully", "order_id": order_dict["order_id"], "total_amount": total_amount, "status": order_status}

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
        
    # Check permissions: Only Buyer or Admin can confirm delivery
    if order['buyer_id'] != current_user['id'] and current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only buyer can confirm delivery")
        
    # Order must be in escrow or delivered status
    if order['status'] not in ['held_in_escrow', 'delivered']:
        raise HTTPException(
            status_code=400, 
            detail=f"Order must be in escrow or delivered status. Current status: {order['status']}"
        )
         
    # Process Payout
    from app.services.payout_service import process_order_payout
    success, message = await process_order_payout(order_id, db)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
        
    return {"message": "Delivery confirmed and funds released", "order_id": order_id}

@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    Cancel an order and process refund.
    
    Cancellation Rules:
    - Buyer can cancel: pending, held_in_escrow orders
    - Seller can cancel: pending orders only
    - Admin can cancel: any order except completed
    
    Refund Logic:
    - Wallet payments: Immediate refund to wallet
    - Paystack payments (pending): No refund needed (not yet paid)
    - Paystack payments (paid): Refund to wallet (Paystack doesn't support auto-refunds)
    
    Stock Restoration:
    - All cancelled orders restore product quantities
    """
    import logging
    logger = logging.getLogger(__name__)
    
    db = get_db()
    order = db.orders.find_one({"order_id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    is_buyer = order['buyer_id'] == current_user['id']
    is_seller = order['seller_id'] == current_user['id']
    is_admin = current_user.get('role') == 'admin'
    
    if not (is_buyer or is_seller or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
    
    # Check if order can be cancelled
    current_status = order['status']
    
    # Cannot cancel completed or already cancelled orders
    if current_status in ['completed', 'cancelled']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel order with status '{current_status}'"
        )
    
    # Seller can only cancel pending or pending_payment orders
    if is_seller and not is_admin and current_status not in ['pending', 'pending_payment']:
        raise HTTPException(
            status_code=403,
            detail="Sellers can only cancel pending orders. Contact support for other cancellations."
        )
    
    # Buyer can cancel pending, held_in_escrow, or pending_payment orders
    if is_buyer and not is_admin and current_status not in ['pending', 'held_in_escrow', 'pending_payment']:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot cancel order in '{current_status}' status. Contact support."
        )


    
    # Process refund
    refund_amount = order['total_amount']
    payment_method = order['payment_method']
    payment_status = order.get('payment_status', 'unknown')
    refund_processed = False
    
    if payment_method == 'wallet' and payment_status == 'paid':
        # Refund to wallet
        db.users.update_one(
            {"id": order['buyer_id']},
            {"$inc": {"wallet_balance": refund_amount}}
        )
        
        # Log refund transaction
        refund_transaction = {
            "user_id": order['buyer_id'],
            "email": order.get('buyer_email'),
            "type": "credit",
            "category": "order_refund",
            "amount": refund_amount,
            "reference": f"refund_{order_id}",
            "description": f"Refund for cancelled order {order_id}",
            "status": "success",
            "metadata": {
                "order_id": order_id,
                "original_payment_method": payment_method,
                "cancelled_by": current_user['id']
            },
            "created_at": datetime.utcnow()
        }
        db.wallet_transactions.insert_one(refund_transaction)
        refund_processed = True
        logger.info(f"Wallet refund processed for order {order_id}. Amount: ₦{refund_amount}")
        
    elif payment_method == 'paystack' and payment_status == 'paid':
        # Paystack doesn't support automatic refunds via API
        # Refund to wallet instead
        db.users.update_one(
            {"id": order['buyer_id']},
            {"$inc": {"wallet_balance": refund_amount}}
        )
        
        # Log refund transaction
        refund_transaction = {
            "user_id": order['buyer_id'],
            "email": order.get('buyer_email'),
            "type": "credit",
            "category": "order_refund",
            "amount": refund_amount,
            "reference": f"refund_{order_id}",
            "description": f"Refund for cancelled order {order_id} (Paystack payment refunded to wallet)",
            "status": "success",
            "metadata": {
                "order_id": order_id,
                "original_payment_method": payment_method,
                "original_payment_reference": order.get('payment_reference'),
                "cancelled_by": current_user['id']
            },
            "created_at": datetime.utcnow()
        }
        db.wallet_transactions.insert_one(refund_transaction)
        refund_processed = True
        logger.info(f"Paystack payment refunded to wallet for order {order_id}. Amount: ₦{refund_amount}")
        
    elif payment_status == 'pending':
        # No payment made yet, no refund needed
        refund_processed = False
        logger.info(f"No refund needed for order {order_id} - payment was pending")
    
    # Restore product quantities
    for item in order['items']:
        db.products.update_one(
            {"id": item['product_id']},
            {"$inc": {"quantity_available": item['quantity']}}
        )
    
    # Update order status
    cancellation_info = {
        "status": "cancelled",
        "cancelled_at": datetime.utcnow(),
        "cancelled_by": current_user['id'],
        "cancelled_by_role": "buyer" if is_buyer else ("seller" if is_seller else "admin"),
        "cancellation_reason": f"Cancelled by {current_user.get('username', 'user')}",
        "refund_processed": refund_processed,
        "refund_amount": refund_amount if refund_processed else 0
    }
    
    db.orders.update_one(
        {"order_id": order_id},
        {"$set": cancellation_info}
    )
    
    logger.info(f"Order {order_id} cancelled by {current_user['id']}. Refund: {refund_processed}, Amount: ₦{refund_amount if refund_processed else 0}")
    
    return {
        "message": "Order cancelled successfully",
        "order_id": order_id,
        "refund_processed": refund_processed,
        "refund_amount": refund_amount if refund_processed else 0,
        "refund_method": "wallet" if refund_processed else "none"
    }

from pydantic import BaseModel
from typing import List

class RemoveItemsRequest(BaseModel):
    product_ids: List[str]  # List of product IDs to remove

@router.post("/{order_id}/remove-items")
async def remove_items_from_order(
    order_id: str, 
    request: RemoveItemsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Remove specific items from an order and process partial refund.
    
    Rules:
    - Only buyers can remove items
    - Can only remove from pending or held_in_escrow orders
    - Partial refund calculated based on removed items
    - If all items removed, order is fully cancelled
    - Stock restored for removed items
    """
    import logging
    logger = logging.getLogger(__name__)
    
    db = get_db()
    order = db.orders.find_one({"order_id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only buyer can remove items
    if order['buyer_id'] != current_user['id']:
        raise HTTPException(
            status_code=403, 
            detail="Only the buyer can remove items from their order"
        )
    
    # Can only remove items from pending, held_in_escrow, or pending_payment orders
    if order['status'] not in ['pending', 'held_in_escrow', 'pending_payment']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot modify order in '{order['status']}' status. Only pending or paid orders can be modified."
        )
    
    # Validate product_ids
    if not request.product_ids:
        raise HTTPException(status_code=400, detail="No items specified for removal")
    
    # Find items to remove
    items_to_remove = []
    items_to_keep = []
    removed_amount = 0.0
    
    for item in order['items']:
        if item['product_id'] in request.product_ids:
            items_to_remove.append(item)
            removed_amount += item['total']
        else:
            items_to_keep.append(item)
    
    if not items_to_remove:
        raise HTTPException(
            status_code=400, 
            detail="None of the specified items found in this order"
        )
    
    # If all items removed, convert to full cancellation
    if not items_to_keep:
        logger.info(f"All items removed from order {order_id}, converting to full cancellation")
        # Use the full cancellation logic
        # Just update the order to cancelled and process full refund
        return await cancel_order(order_id, current_user)
    
    # Calculate new order total
    new_total = sum(item['total'] for item in items_to_keep)
    
    # Process partial refund
    payment_method = order['payment_method']
    payment_status = order.get('payment_status', 'unknown')
    refund_processed = False
    
    if payment_status == 'paid':
        # Refund the removed amount to wallet
        db.users.update_one(
            {"id": order['buyer_id']},
            {"$inc": {"wallet_balance": removed_amount}}
        )
        
        # Log partial refund transaction
        refund_transaction = {
            "user_id": order['buyer_id'],
            "email": order.get('buyer_email'),
            "type": "credit",
            "category": "partial_order_refund",
            "amount": removed_amount,
            "reference": f"partial_refund_{order_id}_{datetime.utcnow().timestamp()}",
            "description": f"Partial refund for {len(items_to_remove)} item(s) removed from order {order_id}",
            "status": "success",
            "metadata": {
                "order_id": order_id,
                "items_removed": len(items_to_remove),
                "original_total": order['total_amount'],
                "new_total": new_total,
                "refund_amount": removed_amount
            },
            "created_at": datetime.utcnow()
        }
        db.wallet_transactions.insert_one(refund_transaction)
        refund_processed = True
        logger.info(f"Partial refund processed for order {order_id}. Amount: ₦{removed_amount}, Items removed: {len(items_to_remove)}")
    
    # Restore stock for removed items
    for item in items_to_remove:
        db.products.update_one(
            {"id": item['product_id']},
            {"$inc": {"quantity_available": item['quantity']}}
        )
    
    # Update order with remaining items and new total
    db.orders.update_one(
        {"order_id": order_id},
        {
            "$set": {
                "items": items_to_keep,
                "total_amount": new_total,
                "modified_at": datetime.utcnow()
            },
            "$push": {
                "modification_history": {
                    "action": "items_removed",
                    "removed_items": items_to_remove,
                    "refund_amount": removed_amount if refund_processed else 0,
                    "modified_by": current_user['id'],
                    "modified_at": datetime.utcnow()
                }
            }
        }
    )
    
    logger.info(f"Items removed from order {order_id}. Removed: {len(items_to_remove)}, Remaining: {len(items_to_keep)}, New total: ₦{new_total}")
    
    return {
        "message": f"{len(items_to_remove)} item(s) removed from order",
        "order_id": order_id,
        "items_removed": len(items_to_remove),
        "items_remaining": len(items_to_keep),
        "refund_processed": refund_processed,
        "refund_amount": removed_amount if refund_processed else 0,
        "new_order_total": new_total,
        "removed_items": [{"product_id": item['product_id'], "title": item['title'], "amount": item['total']} for item in items_to_remove]
    }

@router.post("/{order_id}/mark-delivered")
async def mark_order_delivered(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    Seller marks order as delivered.
    Transitions order from 'held_in_escrow' to 'delivered'.
    Buyer can then confirm delivery to release funds.
    """
    db = get_db()
    order = db.orders.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Check permissions: Only Seller or Admin can mark as delivered
    if order['seller_id'] != current_user['id'] and current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only seller can mark order as delivered")
        
    # Verify order is in escrow (payment received)
    if order['status'] != 'held_in_escrow':
        raise HTTPException(
            status_code=400, 
            detail=f"Order must be in escrow to mark as delivered. Current status: {order['status']}"
        )
        
    # Update order status to delivered
    db.orders.update_one(
        {"order_id": order_id},
        {"$set": {
            "status": "delivered",
            "delivered_at": datetime.utcnow(),
            "delivery_confirmed_by_seller": True
        }}
    )
    
    return {
        "message": "Order marked as delivered. Waiting for buyer confirmation to release funds.",
        "order_id": order_id,
        "status": "delivered"
    }

@router.get("/{order_id}/payment-status")
async def check_payment_status(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    Check payment status for an order.
    Used by frontend after payment callback to verify if webhook has confirmed payment.
    """
    db = get_db()
    order = db.orders.find_one({"order_id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Verify user is buyer or seller
    if order['buyer_id'] != current_user['id'] and order['seller_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return {
        "order_id": order_id,
        "status": order['status'],
        "payment_status": order.get('payment_status', 'unknown'),
        "payment_reference": order.get('payment_reference'),
        "total_amount": order['total_amount'],
        "paid_at": order.get('paid_at'),
        "message": get_payment_status_message(order)
    }

def get_payment_status_message(order: dict) -> str:
    """Helper function to generate user-friendly payment status message"""
    status = order['status']
    payment_status = order.get('payment_status', 'unknown')
    
    if status == 'held_in_escrow' and payment_status == 'paid':
        return "Payment confirmed. Order is being processed."
    elif status == 'pending' and payment_status == 'pending':
        return "Waiting for payment confirmation. This may take a few moments."
    elif status == 'payment_failed':
        return f"Payment failed: {order.get('payment_error', 'Unknown error')}"
    elif status == 'delivered':
        return "Order has been delivered. Waiting for buyer confirmation."
    elif status == 'completed':
        return "Order completed successfully."
    else:
        return f"Order status: {status}"

@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    Cancel an order and refund the buyer using Paystack Reversal API.
    Only orders that are 'pending' or 'held_in_escrow' can be cancelled by the buyer.
    """
    db = get_db()
    order = db.orders.find_one({"order_id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order['buyer_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Only the buyer can cancel this order")
        
    if order['status'] not in ['pending', 'held_in_escrow']:
        raise HTTPException(status_code=400, detail="Order cannot be cancelled at this stage")
        
    # 1. Reverse "Ghost Stock"
    for item in order.get("items", []):
        db.products.update_one(
            {"id": item["product_id"]},
            {"$inc": {"quantity_available": item["quantity"]}}
        )
        
    # 2. Refund Escrow via Paystack if Paid
    if order['status'] == 'held_in_escrow' and order.get('payment_reference'):
        try:
            from app.services.paystack import refund_transaction
            # Trigger full refund
            refund_transaction(order['payment_reference'], customer_note=f"Cancelled Order {order_id}")
            
            # Log refund
            refund_txn = {
                "user_id": current_user['id'],
                "type": "credit",
                "category": "refund",
                "amount": order.get('total_amount'),
                "reference": f"refund_api_{order['payment_reference']}",
                "description": f"Card Reversal for Order {order_id}",
                "status": "success",
                "created_at": datetime.utcnow()
            }
            db.wallet_transactions.insert_one(refund_txn)
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Paystack Refund Failed for {order_id}: {str(e)}")
            order['refund_failed_reason'] = str(e)
            
    # 3. Update Status
    update_data = {
        "status": "cancelled",
        "cancelled_at": datetime.utcnow()
    }
    if 'refund_failed_reason' in order:
        update_data["refund_status"] = "failed"
        update_data["refund_failed_reason"] = order["refund_failed_reason"]
    elif order['status'] == 'held_in_escrow':
        update_data["refund_status"] = "processing"
        
    db.orders.update_one({"order_id": order_id}, {"$set": update_data})
    
    return {
        "message": "Order cancelled successfully. If paid, your card refund is processing.",
        "status": "cancelled"
    }
