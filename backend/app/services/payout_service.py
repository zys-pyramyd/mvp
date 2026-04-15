from datetime import datetime
from app.services.paystack import initiate_transfer, create_transfer_recipient, resolve_account_number
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Constants (Mirrored from server.py to avoid circular imports)
FARMHUB_SERVICE_CHARGE = 0.05  # 5% (Reduced from 10%)
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
        
    # Ensure seller has payout destination (DVA or Bank)
    seller_dva = seller.get("dva_account_number")
    
    # --- Check for assigned Product Payout Account first ---
    bank_details = order.get("product_payout_account") or seller.get("bank_details")
    

    if not seller_dva and not (bank_details and bank_details.get("account_number") and bank_details.get("bank_code")):
        # Route to manual_reconciliations
        db.manual_reconciliations.insert_one({
            "order_id": order_id,
            "user_id": seller_id,
            "role": "seller",
            "amount_expected": order.get("total_amount"),
            "status": "pending",
            "created_at": datetime.utcnow()
        })
        
        # Mark order as pending reconciliation
        db.orders.update_one(
            {"order_id": order_id},
            {"$set": {
                "payout_status": "pending_reconciliation", 
                "payout_error": "Missing DVA or Bank Details"
            }}
        )
        
        # Emit notification
        db.notifications.insert_one({
            "user_id": seller_id,
            "title": "Payout Held for Reconciliation",
            "message": f"Your payout for order #{order_id} is held by Pyramyd because you don't have a linked DVA or Bank Account. Please add one. Reconciliation happens 24 hours after adding details.",
            "type": "payout_held",
            "is_read": False,
            "created_at": datetime.utcnow()
        })
        logger.warning(f"Order {order_id} payout held. Missing DVA/Bank for seller {seller_id}")
        return False, "Missing DVA or Bank Details. Routed to manual reconciliation."

    # Check for Agent (if seller has an agent)
    selling_agent_id = order.get("agent_id") # populated if agent facilitated sale
    buying_agent_id = order.get("buyer_agent_id")
    
    # 3. Calculate Splits
    total_amount = order.get("total_amount", 0.0)
    product_cost_total = order.get("product_cost_total", total_amount)
    total_delivery_fee = order.get("total_delivery_fee", 0.0)
    buyer_agent_service_charge = order.get("agent_service_charge", 0.0)
    logistics_managed_by = order.get("logistics_managed_by", "pyramyd")
    
    # Base Rates
    platform_fee_rate = FARMHUB_SERVICE_CHARGE
    
    # Dynamic Logic
    platform = order.get("platform", "farm_deals") # Default to standard if missing
    seller_role = order.get("seller_role", "farmer")
    
    selling_agent_commission = 0.0
    
    if platform == "pyexpress" and seller_role == "business":
        # PyExpress Business Sales: No Selling Agent Commission
        pass
    elif selling_agent_id:
        # Standard Agent Commission if selling agent involved
        selling_agent_commission = round(product_cost_total * AGENT_SALE_COMMISSION, 2)
        # Note: Platform still takes its 5%, Agent takes an additional 5% totaling 10% deduction from seller.
        
    platform_fee = round(product_cost_total * platform_fee_rate, 2)
        
    seller_amount = round(product_cost_total - platform_fee - selling_agent_commission, 2)
    
    # Apply Delivery Fee logic
    if logistics_managed_by == "seller":
        seller_amount += total_delivery_fee
    elif logistics_managed_by == "pyramyd":
        # Platform holds delivery fee to pay logistics
        platform_fee += total_delivery_fee
        
    logger.info(f"Processing payout for order {order_id}. Total: ₦{total_amount}, Seller: ₦{seller_amount}, Platform: ₦{platform_fee}, Selling Agent: ₦{selling_agent_commission}, Buying Agent: ₦{buyer_agent_service_charge}")
    
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
    
    # Credit Selling Agent
    if selling_agent_id:
        db.users.update_one(
            {"id": selling_agent_id},
            {
                "$inc": {"wallet_balance": selling_agent_commission},
                "$push": {
                    "wallet_history": {
                        "type": "credit",
                        "amount": selling_agent_commission,
                        "description": f"Selling Commission for Order #{order_id}",
                        "date": datetime.utcnow()
                    }
                }
            }
        )
        
    # Credit Buying Agent
    if buying_agent_id and buyer_agent_service_charge > 0:
        db.users.update_one(
            {"id": buying_agent_id},
            {
                "$inc": {"wallet_balance": buyer_agent_service_charge},
                "$push": {
                    "wallet_history": {
                        "type": "credit",
                        "amount": buyer_agent_service_charge,
                        "description": f"Buying Agent Service Charge for Order #{order_id}",
                        "date": datetime.utcnow()
                    }
                }
            }
        )
        
    # Credit Platform (Admin User or dedicated collection?)
    # For MVP, we just track it in order or separate ledger. 
    # db.platform_revenue.insert(...)
    
    # 5. Real Money Transfer (Paystack)
    # Check if seller/product has explicit bank details
    transfer_status = "skipped"
    transfer_ref = None
    
    bank_details = order.get("product_payout_account") or seller.get("bank_details")
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
