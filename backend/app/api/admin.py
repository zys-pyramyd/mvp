
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from app.models.user import User, CreateAdminRequest, UserRole
from app.core.security import hash_password, decrypt_data
from app.api.deps import get_db, get_current_user
from app.services.paystack import assign_dedicated_account
from app.core.config import settings
import os

router = APIRouter()

@router.post("/users/create")
async def create_admin(request: CreateAdminRequest, current_user: dict = Depends(get_current_user)):
    """Create a new admin user (requires admin privileges)"""
    
    # Check if current user is admin
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")

    # Verify secret key (extra layer of security)
    admin_secret = os.environ.get("ADMIN_CREATION_SECRET")
    if not admin_secret or request.secret_key != admin_secret:
         raise HTTPException(status_code=403, detail="Invalid admin creation secret key")
         
    db = get_db()
    if db.users.find_one({"email": request.email}):
        raise HTTPException(status_code=400, detail="User already exists")
        
    admin_user = User(
        first_name=request.first_name,
        last_name=request.last_name,
        username=request.email.split('@')[0], # Generate username from email
        email=request.email,
        role=UserRole.ADMIN,
        is_verified=True
    )
    
    user_dict = admin_user.dict()
    user_dict['password'] = hash_password(request.password)
    
    db.users.insert_one(user_dict)
    
    return {"message": "Admin user created successfully", "user_id": admin_user.id}


# --- User Management ---
@router.get("/users")
async def list_all_users(current_user: dict = Depends(get_current_user)):
    """List all users with basic analysis data"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    users = list(db.users.find({}, {"password": 0, "_id": 0})) # Exclude sensitive data
    return {"users": users}

@router.put("/users/{user_id}/block")
async def block_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    result = db.users.update_one({"id": user_id}, {"$set": {"is_blocked": True}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"message": f"User {user_id} has been blocked"}

@router.put("/users/{user_id}/unblock")
async def unblock_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    result = db.users.update_one({"id": user_id}, {"$set": {"is_blocked": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"message": f"User {user_id} has been unblocked"}

@router.put("/users/{user_id}/verify")
async def verify_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Manually verify a user (Admin only)"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    
    # Fetch user first to get details for DVA
    user = db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    dva_message = ""
    dva_created = False
    
    # Try creating DVA if Partner (has BVN) and doesn't have one
    if user.get("bvn") and not user.get("dva_account_number"):
        try:
            bvn = decrypt_data(user["bvn"])
            dva_data_req = {
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "phone": user.get("phone")
            }
            dva_result = assign_dedicated_account(dva_data_req, bvn)
            
            if dva_result and dva_result.get("status") and dva_result.get("data"):
                data = dva_result["data"]
                # Update with DVA details
                db.users.update_one(
                    {"id": user_id},
                    {"$set": {
                        "dva_account_number": data.get("account_number"),
                        "dva_bank_name": data.get("bank", {}).get("name") if isinstance(data.get("bank"), dict) else data.get("bank", "Unknown"),
                        "paystack_customer_code": data.get("customer", {}).get("customer_code")
                    }}
                )
                dva_created = True
                dva_message = ". DVA created successfully."
            else:
                 dva_message = f". DVA creation failed: {dva_result.get('message')}. User can retry in profile."
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Verify User DVA Error: {e}")
            dva_message = ". DVA creation error (check logs). User can retry."

    # Update user verification status (Always verify if admin clicked it, regardless of DVA)
    result = db.users.update_one(
        {"id": user_id},
        {"$set": {
            "is_verified": True,
            "kyc_status": "approved", # Sync with KYC status
            "verification_info.manual_verification": True,
            "verification_info.verified_by": current_user.get('username', 'admin'),
            "verification_info.verified_at": datetime.utcnow()
        }}
    )
        
    return {"message": f"User {user_id} has been manually verified{dva_message}"}

# --- Global Order Tracking ---
@router.get("/orders")
async def list_all_orders(current_user: dict = Depends(get_current_user)):
    """View all orders on the platform"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    orders = list(db.orders.find().sort("created_at", -1))
    for order in orders:
        order['_id'] = str(order['_id'])
    

    return {"orders": orders}

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str, 
    status_update: dict, 
    current_user: dict = Depends(get_current_user)
):
    """
    Update order status. 
    If status is 'delivered', triggers payout.
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    new_status = status_update.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")

    db = get_db()
    order = db.orders.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # If marking as delivered, trigger payout logic
    if new_status == 'delivered' and order.get('status') != 'delivered':
        from app.services.payout_service import process_order_payout
        success, message = await process_order_payout(order_id, db)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Payout failed: {message}")
            
        return {"message": "Order marked as delivered and payout processed"}

    # Standard status update
    db.orders.update_one(
        {"order_id": order_id},
        {"$set": {
            "status": new_status,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": f"Order status updated to {new_status}"}

# --- Analytics & Overview ---
@router.get("/analytics")
async def get_admin_analytics(current_user: dict = Depends(get_current_user)):
    """Get high-level platform metrics for the admin dashboard"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    db = get_db()
    
    # 1. User Stats
    total_users = db.users.count_documents({})
    user_distribution = {
        "farmers": db.users.count_documents({"role": "farmer"}),
        "agents": db.users.count_documents({"role": "agent"}),
        "buyers": db.users.count_documents({"role": {"$in": ["buyer", "personal"]}}),
        "logistics": db.users.count_documents({"role": "logistics_business"}),
        "business": db.users.count_documents({"role": "business"})
    }
    
    # 2. Order Stats
    total_orders = db.orders.count_documents({})
    active_orders = db.orders.count_documents({"status": {"$in": ["pending", "processing", "shipped"]}})
    
    # 3. Financials (Rough approx - assuming total_amount field exists in orders)
    pipeline = [
        {"$group": {"_id": None, "total_gmv": {"$sum": "$total_amount"}}}
    ]
    gmv_result = list(db.orders.aggregate(pipeline))
    gmv = gmv_result[0]['total_gmv'] if gmv_result else 0
    
    # Estimated revenue (e.g. 5% commission on GMV)
    revenue = gmv * 0.05 

    return {
        "metrics": {
            "gmv": gmv,
            "revenue": revenue,
            "active_users": total_users,
            "total_orders": total_orders
        },
        "user_distribution": user_distribution
    }

# --- Payment Controls ---
@router.post("/orders/{order_id}/halt-payout")
async def halt_payout(order_id: str, current_user: dict = Depends(get_current_user)):
    """Halt payout for an order (Investigation/Dispute)"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    db = get_db()
    result = db.orders.update_one(
        {"order_id": order_id},
        {"$set": {"payout_halted": True, "halted_by": current_user.get('username'), "status": "halted"}}
    )
    
    if result.matched_count == 0:
         raise HTTPException(status_code=404, detail="Order not found")
         
    return {"message": "Payout halted for order."}

@router.post("/orders/{order_id}/manual-release")
async def manual_release_payout(order_id: str, current_user: dict = Depends(get_current_user)):
    """Manually release payout for an order (Admin Override)"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    db = get_db()
    order = db.orders.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Un-halt if halted
    db.orders.update_one({"order_id": order_id}, {"$set": {"payout_halted": False, "status": "completed"}})
    
    from app.services.payout_service import process_order_payout
    # Force process
    success, msg = await process_order_payout(order_id, db)
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Payout failed: {msg}")
        
    return {"message": "Payout manually released."}


from pydantic import BaseModel

class ManualWithdrawalRequest(BaseModel):
    amount: float
    reason: str

@router.post("/users/{user_id}/manual-withdrawal")
async def manual_withdrawal(
    user_id: str, 
    request: ManualWithdrawalRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Manually deduct funds from a user's wallet (e.g., cash payout off-platform)"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
        
    db = get_db()
    
    # 1. Verify user and balance
    target_user = db.users.find_one({"id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    current_balance = target_user.get("wallet_balance", 0.0)
    if current_balance < request.amount:
        raise HTTPException(status_code=400, detail=f"Insufficient funds. User balance is {current_balance}")
        
    # 2. Deduct from wallet atomically
    result = db.users.update_one(
        {"id": user_id, "wallet_balance": {"$gte": request.amount}},
        {"$inc": {"wallet_balance": -request.amount}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to deduct funds (balance may have changed)")
        
    # 3. Create Transaction Record
    import uuid
    transaction_id = str(uuid.uuid4())
    
    transaction = {
        "id": transaction_id,
        "user_id": user_id,
        "type": "debit",
        "category": "manual_withdrawal",
        "amount": request.amount,
        "reference": f"MAN_WD_{transaction_id[:8].upper()}",
        "description": f"Manual Admin Withdrawal: {request.reason}",
        "status": "success",
        "processed_by": current_user["username"],
        "created_at": datetime.utcnow()
    }
    
    
    db.wallet_transactions.insert_one(transaction)
    
    return {
        "message": f"Successfully deducted NGN {request.amount} from user wallet.",
        "new_balance": current_balance - request.amount,
        "reference": transaction["reference"]
    }

@router.post("/rfq/{order_id}/cancel")
async def admin_cancel_rfq_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    Cancel an RFQ order. Exclusively for Admins.
    Reverses the transaction and triggers Paystack refund.
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Only Pyramyd Admins can cancel RFQ orders")

    db = get_db()
    order = db.rfq_orders.find_one({"order_id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="RFQ Order not found")
        
    if order['status'] in ['cancelled', 'completed']:
        raise HTTPException(status_code=400, detail="Order cannot be cancelled at this stage")
    
    refund_details = "Cancelled by Admin. Standard Refund Rules applied."
    from datetime import datetime
    
    if order.get('payment_reference'):
        try:
            from app.services.paystack import refund_transaction
            # Trigger full refund via Paystack directly to card
            refund_transaction(order['payment_reference'], customer_note=f"Cancelled RFQ Deal {order_id} by Platform Admin")
            
            refund_txn = {
                "user_id": order.get('buyer_id'),
                "type": "credit",
                "category": "refund",
                "amount": order.get('total_amount'),
                "reference": f"refund_api_rfq_{order['payment_reference']}",
                "description": f"Admin Cancellation Card Reversal for RFQ {order_id}",
                "status": "success",
                "created_at": datetime.utcnow()
            }
            db.wallet_transactions.insert_one(refund_txn)
            refund_details = "Paystack Reversal Initiated."
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Paystack Refund Failed for RFQ {order_id}: {str(e)}")
            order['refund_failed_reason'] = str(e)
            refund_details = f"Reversal Failed: {str(e)}"
            
    # Update Status
    update_data = {
        "status": "cancelled",
        "cancelled_by_admin": current_user['username'],
        "cancelled_at": datetime.utcnow()
    }
    
    # Also update the base offer so it shows as cancelled
    if order.get("origin_offer_id"):
        db.offers.update_one(
            {"id": order["origin_offer_id"]},
            {"$set": {"status": "cancelled", "cancelled_at": datetime.utcnow()}}
        )
        
    if 'refund_failed_reason' in order:
        update_data["refund_status"] = "failed"
        update_data["refund_failed_reason"] = order["refund_failed_reason"]
        
    db.rfq_orders.update_one({"order_id": order_id}, {"$set": update_data})
    
    return {
        "message": f"RFQ Order cancelled successfully. {refund_details}",
        "status": "cancelled"
    }
