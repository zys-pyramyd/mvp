# Auto-extracted Router
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api.deps import get_db, get_current_user
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import random
import string

router = APIRouter()

@router.post("/api/offers/{offer_id}/accept", tags=["RFQ"])
async def accept_offer(
    offer_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    offer = db.request_offers.find_one({"id": offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    request = db.buyer_requests.find_one({"id": offer["request_id"]})
    
    # Validation: Only Buyer can accept
    if request["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if offer["status"] != "pending":
        raise HTTPException(status_code=400, detail="Offer is not pending")
        
    # Fractional Logic: Deduct quantity
    qty_needed = request["quantity_remaining"]
    qty_offered = offer["quantity_offered"]
    
    if qty_offered > qty_needed:
        # Edge case: two people accepted same time?
        raise HTTPException(status_code=400, detail="Offer exceeds remaining quantity needed")
        
    # Generate Handshake
    tracking_id = f"RFQ-TRK-{uuid.uuid4().hex[:16].upper()}"
    otp_code = tracking_id[-8:] # Last 8 chars
    
    # Update Offer
    db.request_offers.update_one(
        {"id": offer_id},
        {
            "$set": {
                "status": "accepted", 
                "tracking_id": tracking_id,
                "delivery_otp": otp_code,
                "date_accepted": datetime.utcnow()
            }
        }
    )
    
    # Update Request Pool
    new_remaining = qty_needed - qty_offered
    req_status = "partially_filled" if new_remaining > 0 else "filled"
    # If filled, maybe close it? Or keep open for backup? Spec says "closed" if 0.
    if new_remaining == 0:
        req_status = "filled" # Logic: filled means done for now.
        
    db.buyer_requests.update_one(
        {"id": request["id"]},
        {"$set": {"quantity_remaining": new_remaining, "status": req_status}}
    )
    
    # PAYMENT NOTE: Here we should trigger payment deduction from Wallet (Escrow).
    # For MVP, we assume User has funds and we lock it.
    # In production, this would call `process_payment(user_id, offer.price)`
    
    return {
        "status": "success", 
        "message": "Offer accepted", 
        "tracking_id": tracking_id,
        "otp_code": otp_code 
    }

@router.post("/api/offers/{offer_id}/delivered", tags=["RFQ"])
async def mark_delivered(
    offer_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    offer = db.request_offers.find_one({"id": offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    # Only Seller can mark delivered
    if offer["seller_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if offer["status"] != "accepted":
        raise HTTPException(status_code=400, detail="Offer must be in 'accepted' state")
        
    db.request_offers.update_one(
        {"id": offer_id},
        {"$set": {"status": "delivered", "date_delivered": datetime.utcnow()}}
    )
    
    return {"status": "success", "message": "Order marked as delivered. Waiting for buyer confirmation or auto-release."}

@router.post("/api/offers/{offer_id}/confirm-delivery", tags=["RFQ"])
async def confirm_delivery_otp(
    offer_id: str,
    data: DeliveryConfirm,
    current_user: dict = Depends(get_current_user), 
    db = Depends(get_database)
):
    offer = db.request_offers.find_one({"id": offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    request = db.buyer_requests.find_one({"id": offer["request_id"]})
    
    # Buyer Confirmation: Only Buyer can confirm receipt
    if request["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized (Only Buyer can confirm receipt)")
        
    if offer["delivery_otp"] != data.otp_code:
        raise HTTPException(status_code=400, detail="Invalid Confirmation Code (Check Tracking ID)")
        
    # Verify Success! Release Funds.
    # 1. Payout
    # 2. Log Settlement
    
    # Idempotency check: If already completed
    if offer["status"] == "completed":
        return {"status": "success", "message": "Already completed"}
    
    amount = offer["price"]
    
    amount = offer["price"]
    fee = amount * 0.03 # 3% Platform Fee (Assumption)
    payout = amount - fee
    
    # Credit Seller Wallet
    db.users.update_one(
        {"id": current_user["id"]},
        {
            "$inc": {"wallet_balance": payout},
            "$push": {
                "wallet_history": {
                    "id": str(uuid.uuid4()),
                    "type": "payout",
                    "amount": payout,
                    "description": f"RFQ Payout: {offer_id}",
                    "status": "success",
                    "created_at": datetime.utcnow()
                }
            }
        }
    )
    
    # Log Settlement
    settlement = {
        "id": str(uuid.uuid4()),
        "request_id": offer["request_id"],
        "offer_id": offer_id,
        "amount": amount,
        "fee": fee,
        "payout_reference": f"PAY-{uuid.uuid4().hex[:8]}",
        "method_of_fulfillment": "OTP Verified",
        "created_at": datetime.utcnow()
    }
    db.settlement_logs.insert_one(settlement)
    
    # Update Offer Status
    db.request_offers.update_one(
        {"id": offer_id},
        {"$set": {"status": "completed", "date_delivered": datetime.utcnow(), "payout_status": "success"}}
    )
    
    return {"status": "success", "message": "Delivery confirmed. Funds released."}

