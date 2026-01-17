from fastapi import APIRouter, Request, Header, HTTPException, status
from app.services.paystack import verify_signature
from app.api.deps import get_db
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def paystack_webhook(request: Request, x_paystack_signature: str = Header(None)):
    """
    Comprehensive Paystack Webhook Handler
    
    Handles ALL Paystack events:
    - charge.success: Payment successful (wallet funding, RFQ payments, orders)
    - transfer.success: Payout completed
    - transfer.failed: Payout failed
    - transfer.reversed: Payout reversed
    - customeridentification.success: BVN verification
    - dedicatedaccount.assign.success: DVA created
    
    Register this URL in Paystack Dashboard:
    https://yourdomain.com/api/paystack/webhook
    """
    if not x_paystack_signature:
        logger.warning("Webhook received without signature")
        raise HTTPException(status_code=400, detail="Missing signature")
    
    payload = await request.body()
    try:
        # Verify signature for security
        if not verify_signature(payload, x_paystack_signature):
            logger.warning("Invalid Paystack Webhook Signature")
            raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Signature Verification Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Signature verification failed")
    
    event = await request.json()
    event_type = event.get("event")
    data = event.get("data", {})
    
    logger.info(f"Paystack Webhook: {event_type}")
    
    db = get_db()
    
    # ========================================
    # 1. CHARGE SUCCESS - Payment Received
    # ========================================
    if event_type == "charge.success":
        customer = data.get("customer", {})
        customer_code = customer.get("customer_code")
        email = customer.get("email")
        amount_kobo = data.get("amount", 0)
        amount_naira = amount_kobo / 100.0
        reference = data.get("reference")
        
        # Check if transaction exists (e.g. pending RFQ payment, order payment)
        existing_txn = db.wallet_transactions.find_one({"reference": reference})
        
        if existing_txn:
            if existing_txn["status"] == "success":
                logger.info(f"Transaction already processed: {reference}")
                return {"status": "success", "message": "Transaction already processed"}
            
            # Handle Pending Transactions
            if existing_txn["status"] == "pending":
                # Update transaction to success
                db.wallet_transactions.update_one(
                    {"_id": existing_txn["_id"]},
                    {"$set": {
                        "status": "success", 
                        "metadata.paystack_data": data, 
                        "updated_at": datetime.utcnow()
                    }}
                )
                
                # Handle different transaction categories
                category = existing_txn.get("category")
                
                if category == "rfq_service_charge":
                    # Activate RFQ/Buyer Request
                    db.buyer_requests.update_one(
                        {"payment_reference": reference},
                        {"$set": {"status": "open", "payment_status": "paid"}}
                    )
                    logger.info(f"✅ RFQ Service Charge verified. Request Activated. Ref: {reference}")
                    
                elif category == "order_payment":
                    # Mark order as paid
                    db.orders.update_one(
                        {"payment_reference": reference},
                        {"$set": {"payment_status": "paid", "status": "processing"}}
                    )
                    logger.info(f"✅ Order payment verified. Ref: {reference}")
                    
                elif category == "wallet_funding":
                    # Credit user wallet
                    user_id = existing_txn.get("user_id")
                    db.users.update_one(
                        {"id": user_id},
                        {"$inc": {"wallet_balance": amount_naira}}
                    )
                    logger.info(f"✅ Wallet funded for user {user_id}: +₦{amount_naira}")
                
                return {"status": "success", "message": f"{category} processed"}
        
        # If NO existing transaction, assume Direct Wallet Funding
        else:
            user = db.users.find_one({
                "$or": [
                    {"paystack_customer_code": customer_code},
                    {"email": email}
                ]
            })
            
            if user:
                # Create transaction record
                transaction = {
                    "user_id": user["id"],
                    "type": "credit",
                    "category": "wallet_funding",
                    "amount": amount_naira,
                    "reference": reference,
                    "description": "Wallet funding (Direct Payment)",
                    "status": "success",
                    "metadata": data,
                    "created_at": datetime.utcnow()
                }
                db.wallet_transactions.insert_one(transaction)
                
                # Update user balance
                db.users.update_one(
                    {"id": user["id"]},
                    {"$inc": {"wallet_balance": amount_naira}}
                )
                
                logger.info(f"✅ Wallet funded for user {user['id']}: +₦{amount_naira} (Ref: {reference})")
            else:
                logger.warning(f"⚠️ User not found for {email}/{customer_code}")
    
    # ========================================
    # 2. TRANSFER SUCCESS - Payout Completed
    # ========================================
    elif event_type == "transfer.success":
        reference = data.get("reference")
        amount_kobo = data.get("amount", 0)
        amount_naira = amount_kobo / 100.0
        recipient = data.get("recipient", {})
        
        # Find order by transfer reference
        order = db.orders.find_one({"transfer_ref": reference})
        if order:
            db.orders.update_one(
                {"order_id": order["order_id"]},
                {"$set": {
                    "transfer_status": "success",
                    "payout_completed_at": datetime.utcnow()
                }}
            )
            logger.info(f"✅ Transfer successful for order {order['order_id']}: ₦{amount_naira}")
        else:
            logger.warning(f"⚠️ Transfer success but no order found: {reference}")
    
    # ========================================
    # 3. TRANSFER FAILED - Payout Failed
    # ========================================
    elif event_type == "transfer.failed":
        reference = data.get("reference")
        
        order = db.orders.find_one({"transfer_ref": reference})
        if order:
            # Refund to seller's wallet
            seller_id = order.get("seller_id")
            amount = order.get("seller_amount", 0)
            
            db.users.update_one(
                {"id": seller_id},
                {"$inc": {"wallet_balance": amount}}
            )
            
            db.orders.update_one(
                {"order_id": order["order_id"]},
                {"$set": {"transfer_status": "failed"}}
            )
            
            logger.error(f"❌ Transfer failed for order {order['order_id']}. Refunded to wallet.")
    
    # ========================================
    # 4. TRANSFER REVERSED - Payout Reversed
    # ========================================
    elif event_type == "transfer.reversed":
        reference = data.get("reference")
        
        order = db.orders.find_one({"transfer_ref": reference})
        if order:
            db.orders.update_one(
                {"order_id": order["order_id"]},
                {"$set": {"transfer_status": "reversed"}}
            )
            logger.warning(f"⚠️ Transfer reversed for order {order['order_id']}")
    
    # ========================================
    # 5. DEDICATED ACCOUNT ASSIGNED - DVA Created
    # ========================================
    elif event_type == "dedicatedaccount.assign.success":
        customer = data.get("customer", {})
        customer_code = customer.get("customer_code")
        account_number = data.get("account_number")
        bank = data.get("bank", {})
        bank_name = bank.get("name") if isinstance(bank, dict) else bank
        
        # Update user with DVA details
        result = db.users.update_one(
            {"paystack_customer_code": customer_code},
            {"$set": {
                "dva_account_number": account_number,
                "dva_bank_name": bank_name,
                "dva_assigned_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            logger.info(f"✅ DVA assigned: {account_number} ({bank_name})")
        else:
            logger.warning(f"⚠️ DVA assigned but user not found: {customer_code}")
    
    # ========================================
    # 6. CUSTOMER IDENTIFICATION SUCCESS - BVN Verified
    # ========================================
    elif event_type == "customeridentification.success":
        customer_code = data.get("customer_code")
        
        db.users.update_one(
            {"paystack_customer_code": customer_code},
            {"$set": {"bvn_verified": True, "bvn_verified_at": datetime.utcnow()}}
        )
        logger.info(f"✅ BVN verified for customer: {customer_code}")
    
    # ========================================
    # 7. REFUND PROCESSED
    # ========================================
    elif event_type == "refund.processed":
        reference = data.get("transaction_reference")
        amount_kobo = data.get("amount", 0)
        amount_naira = amount_kobo / 100.0
        
        # Find original transaction
        txn = db.wallet_transactions.find_one({"reference": reference})
        if txn:
            user_id = txn.get("user_id")
            
            # Create refund transaction
            refund_txn = {
                "user_id": user_id,
                "type": "credit",
                "category": "refund",
                "amount": amount_naira,
                "reference": f"refund_{reference}",
                "description": f"Refund for {reference}",
                "status": "success",
                "metadata": data,
                "created_at": datetime.utcnow()
            }
            db.wallet_transactions.insert_one(refund_txn)
            
            # Credit user wallet
            db.users.update_one(
                {"id": user_id},
                {"$inc": {"wallet_balance": amount_naira}}
            )
            
            logger.info(f"✅ Refund processed for user {user_id}: +₦{amount_naira}")
    
    # ========================================
    # 8. SUBSCRIPTION EVENTS (Future Use)
    # ========================================
    elif event_type in ["subscription.create", "subscription.disable"]:
        logger.info(f"Subscription event: {event_type}")
        # Handle subscription logic here if needed
    
    # ========================================
    # 9. DISPUTE EVENTS
    # ========================================
    elif event_type in ["dispute.create", "dispute.resolve"]:
        logger.warning(f"Dispute event: {event_type}")
        # Handle dispute logic here
    
    # Always return 200 to acknowledge receipt
    return {"status": "success", "event": event_type}
