from datetime import datetime
from app.services.paystack import initiate_transfer, create_transfer_recipient, resolve_account_number
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Constants (Mirrored from server.py to avoid circular imports)
FARMHUB_SERVICE_CHARGE = 0.10  # 10%
AGENT_SALE_COMMISSION = 0.05   # 5%

async def process_order_payout(order_id: str, db):
    """
    Process payout for a confirmed/delivered order.
    Splits funds between Platform, Agent (if any), and Seller.
    Initiates actual bank transfer if seller has bank details.
    """
    logger.info(f"Processing payout for order: {order_id}")
    
    # 1. Fetch Order and Check Payout Status Atomically
    # This prevents duplicate payouts if confirm_delivery is called multiple times
    order = db.orders.find_one_and_update(
        {
            "order_id": order_id,
            "status": {"$in": ["held_in_escrow", "delivered"]},
            "payout_status": {"$ne": "completed"}  # Ensure not already paid
        },
        {
            "$set": {
                "payout_status": "processing",
                "payout_started_at": datetime.utcnow()
            }
        },
        return_document=True
    )
    
    if not order:
        # Either order not found, wrong status, or already paid out
        existing_order = db.orders.find_one({"order_id": order_id})
        if not existing_order:
            logger.error(f"Order {order_id} not found")
            return False, "Order not found"
        elif existing_order.get("payout_status") == "completed":
            logger.warning(f"Order {order_id} already paid out")
            return False, "Order already paid out"
        else:
            logger.error(f"Order {order_id} has invalid status: {existing_order.get('status')}")
            return False, f"Order must be in escrow or delivered status. Current: {existing_order.get('status')}"
    
    # 2. Identify Parties
    seller_id = order.get("seller_id")
    seller = db.users.find_one({"id": seller_id})
    if not seller:
        # Rollback payout status
        db.orders.update_one(
            {"order_id": order_id},
            {"$set": {"payout_status": "failed", "payout_error": "Seller not found"}}
        )
        return False, "Seller not found"
        
    # Check for Agent (if seller has an agent)
    # Logic: usually strictly based on 'selling_agent_id' in order, but MVP might not have it.
    # We'll assume direct sale unless 'agent_id' is in order.
    agent_id = order.get("agent_id") # populated if agent facilitated
    
    # 3. Calculate Splits
    total_amount = order.get("total_amount", 0.0)
    
    # Base Rates
    platform_fee_rate = FARMHUB_SERVICE_CHARGE
    
    # Dynamic Logic
    platform = order.get("platform", "farm_deals") # Default to standard if missing
    seller_role = order.get("seller_role", "farmer")
    
    agent_commission = 0.0
    
    if platform == "pyexpress" and seller_role == "business":
        # PyExpress Business Sales: No Agent Commission
        pass
    elif agent_id:
        # Standard Agent Commission if agent involved
        agent_commission = total_amount * AGENT_SALE_COMMISSION
        
    platform_fee = total_amount * platform_fee_rate
        
    seller_amount = total_amount - platform_fee - agent_commission
    
    logger.info(f"Processing payout for order {order_id}. Total: ₦{total_amount}, Seller: ₦{seller_amount}, Platform: ₦{platform_fee}, Agent: ₦{agent_commission}")
    
    # 4. Update Wallets (Ledger)
    # Credit Seller
    db.users.update_one(
        {"id": seller_id},
        {
            "$inc": {"wallet_balance": seller_amount},
            "$push": {
                "wallet_history": {
                    "type": "credit",
                    "amount": seller_amount,
                    "description": f"Payout for Order #{order_id}",
                    "date": datetime.utcnow()
                }
            }
        }
    )
    
    # Credit Agent
    if agent_id:
        db.users.update_one(
            {"id": agent_id},
            {
                "$inc": {"wallet_balance": agent_commission},
                "$push": {
                    "wallet_history": {
                        "type": "credit",
                        "amount": agent_commission,
                        "description": f"Commission for Order #{order_id}",
                        "date": datetime.utcnow()
                    }
                }
            }
        )
        
    # Credit Platform (Admin User or dedicated collection?)
    # For MVP, we just track it in order or separate ledger. 
    # db.platform_revenue.insert(...)
    
    # 5. Real Money Transfer (Paystack)
    # Check if seller has bank details
    transfer_status = "skipped"
    transfer_ref = None
    
    bank_details = seller.get("bank_details")
    if bank_details and bank_details.get("account_number") and bank_details.get("bank_code"):
        try:
            # Create Recipient
            # Note: In prod, cache recipient code.
            recipient_resp = create_transfer_recipient(
                name=bank_details.get("account_name", "Seller"),
                account_number=bank_details["account_number"],
                bank_code=bank_details["bank_code"]
            )
            
            if recipient_resp.get("status"):
                recipient_code = recipient_resp["data"]["recipient_code"]
                
                # Initiate Transfer (Amount in kobo)
                amount_kobo = int(seller_amount * 100)
                transfer_resp = initiate_transfer(
                    amount=amount_kobo,
                    recipient_code=recipient_code,
                    reason=f"Payout for Order {order_id}"
                )
                
                if transfer_resp.get("status"):
                    transfer_status = "initiated"
                    transfer_ref = transfer_resp["data"]["reference"]
                    logger.info(f"Transfer initiated for order {order_id}: {transfer_ref}")
                    
                    # Deduct from wallet immediately? 
                    # Usually we keep it in wallet history as "Auto-Withdrawal"
                    db.users.update_one(
                        {"id": seller_id},
                        {
                            "$inc": {"wallet_balance": -seller_amount},
                            "$push": {
                                "wallet_history": {
                                    "type": "debit",
                                    "amount": seller_amount,
                                    "description": f"Auto-Withdrawal to Bank ({bank_details.get('bank_name', 'Unknown Bank')})",
                                    "date": datetime.utcnow()
                                }
                            }
                        }
                    )
                else:
                    transfer_status = "failed_initiation"
            else:
                 transfer_status = "failed_recipient"
                 
        except Exception as e:
            logger.error(f"Transfer failed for order {order_id}: {e}")
            transfer_status = f"error: {str(e)}"
    
    # 6. Update Order Status
    db.orders.update_one(
        {"order_id": order_id},
        {
            "$set": {
                "status": "completed",  # Order fully completed after payout
                "payout_status": "completed",
                "transfer_status": transfer_status,
                "transfer_ref": transfer_ref,
                "buyer_confirmed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow() 
            }
        }
    )
    
    return True, "Payout processed successfully"
