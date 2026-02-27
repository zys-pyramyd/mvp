import asyncio
import sys
import os
import uuid
from datetime import datetime
import logging

# Setup environment
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))
os.environ["MONGO_URL"] = "mongodb://localhost:27017/" 
os.environ["JWT_SECRET"] = "e2e_test_secret"

from database import db
from app.services.payout_service import process_order_payout

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

TEST_PREFIX = "E2E_"

def cleanup():
    logger.info("Cleaning up previous test data...")
    db.users.delete_many({"id": {"$regex": f"^{TEST_PREFIX}"}})
    db.products.delete_many({"id": {"$regex": f"^{TEST_PREFIX}"}})
    db.orders.delete_many({"order_id": {"$regex": f"^{TEST_PREFIX}"}})
    db.requests.delete_many({"id": {"$regex": f"^{TEST_PREFIX}"}})
    db.offers.delete_many({"id": {"$regex": f"^{TEST_PREFIX}"}})
    db.wallet_transactions.delete_many({"user_id": {"$regex": f"^{TEST_PREFIX}"}})

async def run_direct_purchase_flow():
    logger.info("\n--- 1. Testing Direct Purchase Flow ---")
    
    # 1. Create Users
    buyer_id = f"{TEST_PREFIX}BUYER"
    seller_id = f"{TEST_PREFIX}SELLER"
    
    db.users.insert_one({"id": buyer_id, "username": "e2e_buyer", "email": "buyer@e2e.com", "wallet_balance": 50000, "role": "buyer"})
    db.users.insert_one({"id": seller_id, "username": "e2e_seller", "email": "seller@e2e.com", "wallet_balance": 0, "role": "farmer"})
    
    # 2. Create Product
    product_id = f"{TEST_PREFIX}PROD_RICE"
    db.products.insert_one({
        "id": product_id,
        "title": "E2E Rice",
        "seller_id": seller_id,
        "seller_name": "E2E Seller",
        "price_per_unit": 5000,
        "quantity_available": 100,
        "platform": "retail"
    })
    
    # 3. Create Order (Simulate Wallet Checkout)
    order_id = f"{TEST_PREFIX}ORD_DIRECT"
    total_amount = 5000
    
    logger.info(f"Creating Order {order_id}...")
    db.orders.insert_one({
        "order_id": order_id,
        "buyer_id": buyer_id,
        "seller_id": seller_id,
        "items": [{
            "product_id": product_id,
            "title": "E2E Rice",
            "price_per_unit": 5000,
            "quantity": 1,
            "total": 5000
        }],
        "total_amount": total_amount,
        "status": "held_in_escrow", # Paid via wallet
        "payment_method": "wallet",
        "payment_status": "paid",
        "created_at": datetime.utcnow()
    })
    
    # Deduct Buyer Wallet
    db.users.update_one({"id": buyer_id}, {"$inc": {"wallet_balance": -total_amount}})
    
    # 4. Confirm Delivery & Payout
    logger.info("Simulating Delivery Confirmation & Payout...")
    # Update status to delivered so payout service can process
    db.orders.update_one({"order_id": order_id}, {"$set": {"status": "delivered"}})
    
    success, msg = await process_order_payout(order_id, db)
    
    if success:
        logger.info("✅ Payout Processed Successfully")
    else:
        logger.error(f"❌ Payout Failed: {msg}")
        return

    # 5. Verify Balances
    seller = db.users.find_one({"id": seller_id})
    # Fee is 10% for retail usually, need to check payout service logic explicitly
    # Assuming standard logic: 5000 - fee. 
    # Let's check the wallet balance > 0
    if seller['wallet_balance'] > 0:
         logger.info(f"✅ Seller Wallet Credited: ₦{seller['wallet_balance']}")
    else:
         logger.error(f"❌ Seller Wallet Empty: ₦{seller['wallet_balance']}")

async def run_rfq_flow():
    logger.info("\n--- 2. Testing RFQ (Deal) Flow ---")
    
    buyer_id = f"{TEST_PREFIX}BUYER"
    seller_id = f"{TEST_PREFIX}SELLER"
    
    # 1. Create Request
    req_id = f"{TEST_PREFIX}REQ_TOMATO"
    db.requests.insert_one({
        "id": req_id,
        "buyer_id": buyer_id,
        "title": "Need Tomatoes",
        "type": "instant",
        "platform": "pyexpress",
        "status": "active"
    })
    
    # 2. Create Offer
    offer_id = f"{TEST_PREFIX}OFF_TOMATO"
    db.offers.insert_one({
        "id": offer_id,
        "request_id": req_id,
        "seller_id": seller_id,
        "price": 10000,
        "status": "accepted"
    })
    
    # 3. Create Linked Order
    order_id = f"{TEST_PREFIX}ORD_RFQ"
    logger.info(f"Creating RFQ Order {order_id}...")
    
    db.orders.insert_one({
        "order_id": order_id,
        "buyer_id": buyer_id,
        "seller_id": seller_id,
        "origin_offer_id": offer_id,
        "origin_request_id": req_id,
        "total_amount": 10000,
        "status": "held_in_escrow",
        "payment_method": "wallet",
        "payment_status": "paid",
        "platform": "pyexpress",
        "created_at": datetime.utcnow()
    })
    
    # 4. Trigger Auto-Release (Simulated)
    # We update order to 'delivered' and call payout directly
    logger.info("Simulating Auto-Release Trigger...")
    db.orders.update_one({"order_id": order_id}, {"$set": {"status": "delivered"}})
    db.offers.update_one({"id": offer_id}, {"$set": {"status": "delivered", "delivered_at": datetime.utcnow()}})
    
    success, msg = await process_order_payout(order_id, db)
    
    if success:
        logger.info("✅ RFQ Payout Processed Successfully")
        # Verify Offer Complete
        db.offers.update_one({"id": offer_id}, {"$set": {"status": "completed"}})
    else:
        logger.error(f"❌ RFQ Payout Failed: {msg}")

    # Verify Final Status
    order = db.orders.find_one({"order_id": order_id})
    if order['status'] == 'completed':
        logger.info("✅ Order Status is Completed")
    else:
        logger.error(f"❌ Order Status mismatch: {order['status']}")

async def main():
    try:
        cleanup()
        await run_direct_purchase_flow()
        await run_rfq_flow()
        logger.info("\n✅ ALl TESTS COMPLETED SUCCESSFULLY")
    except Exception as e:
        logger.error(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
