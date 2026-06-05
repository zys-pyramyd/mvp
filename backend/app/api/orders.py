
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



@router.get("/units")
async def get_available_units():
    """Get all available units with examples"""
    return {
        "units": [
            {"value": "kg", "label": "Kilograms", "examples": ["50kg", "100kg"]},
            {"value": "g", "label": "Grams", "examples": ["500g", "1000g"]},
            {"value": "ton", "label": "Tons", "examples": ["1 ton", "5 tons"]},
            {"value": "pieces", "label": "Pieces", "examples": ["10 pieces", "50 pieces"]},
            {"value": "liters", "label": "Liters", "examples": ["5 liters", "20 liters"]},
            {"value": "bags", "label": "Bags", "examples": ["100kg per bag", "50kg per bag"]},
            {"value": "crates", "label": "Crates", "examples": ["24 bottles per crate", "50 pieces per crate"]},
            {"value": "gallons", "label": "Gallons", "examples": ["5 litres per gallon", "4 litres per gallon"]}
        ]
    }

class DisputeCreate(BaseModel):
    reason: str
    description: str

@router.post("/{order_id}/dispute", tags=["Orders"])
async def report_dispute(
    order_id: str,
    dispute_data: DisputeCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    # Retrieve Order
    order = db.orders.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify Participant
    user_id = current_user["id"]
    if user_id != order.get("buyer_id") and user_id != order.get("seller_id"):
        raise HTTPException(status_code=403, detail="Not a participant in this order")

    # Verify Status
    if order.get("status") in ["cancelled", "pending"]:
         raise HTTPException(status_code=400, detail="Cannot dispute an order in this state.")

    # Create Dispute
    import uuid
    from datetime import datetime
    dispute = {
        "id": str(uuid.uuid4()),
        "order_id": order_id,
        "reporter_id": user_id,
        "reporter_role": "buyer" if user_id == order.get("buyer_id") else "seller",
        "reason": dispute_data.reason,
        "description": dispute_data.description,
        "status": "open",
        "created_at": datetime.utcnow()
    }
    db.disputes.insert_one(dispute)

    # Update Order Status
    db.orders.update_one(
        {"order_id": order_id},
        {"$set": {"status": "disputed", "updated_at": datetime.utcnow()}}
    )

    return {"status": "success", "message": "Dispute opened successfully", "dispute_id": dispute["id"]}
