import asyncio
import sys
import uuid
from datetime import datetime, timedelta
import os

# Add backend to path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

# Mock Environment variables if needed
os.environ["MONGO_URL"] = "mongodb://localhost:27017/" 
os.environ["JWT_SECRET"] = "verification_test_secret"

from database import db
from server import check_rfq_auto_release

async def verify_auto_release():
    print("--- Starting Auto-Release Verification ---")
    
    # Clean up previous test data
    test_prefix = "TEST_AUTO_"
    db.requests.delete_many({"id": {"$regex": f"^{test_prefix}"}})
    db.offers.delete_many({"id": {"$regex": f"^{test_prefix}"}})
    db.orders.delete_many({"order_id": {"$regex": f"^{test_prefix}"}})
    
    
    seller_id = "test_seller_001"
    
    # Ensure seller exists for payout
    db.users.update_one(
        {"id": seller_id},
        {"$set": {
            "id": seller_id,
            "username": "test_seller",
            "email": "seller@test.com",
            "wallet_balance": 0.0,
            "role": "farmer"
        }},
        upsert=True
    )
    
    
    # --- Scenario 1: PyExpress (Instant) - Delivered 4 days ago (Should Release) ---
    req_id_1 = f"{test_prefix}REQ_PYEXPRESS"
    offer_id_1 = f"{test_prefix}OFF_PYEXPRESS"
    order_id_1 = f"{test_prefix}ORD_PYEXPRESS"
    
    print(f"Creating PyExpress Test Case: {order_id_1} (4 Days Old)")
    
    db.requests.insert_one({
        "id": req_id_1,
        "platform": "pyexpress", # Lowercase to test fix
        "type": "instant",
        "status": "completed"
    })
    
    db.offers.insert_one({
        "id": offer_id_1,
        "request_id": req_id_1,
        "seller_id": seller_id,
        "status": "delivered",
        "delivered_at": datetime.utcnow() - timedelta(days=4), # > 3 days
        "price": 5000
    })
    
    # We need an order for the payout service to process
    db.orders.insert_one({
        "order_id": order_id_1,
        "origin_offer_id": offer_id_1,
        "seller_id": seller_id,
        "total_amount": 5000,
        "status": "delivered", 
        "platform": "pyexpress",
        "delivery_method": "platform"
    })
    
    # --- Scenario 2: FarmDeals (Standard) - Delivered 10 days ago (Should NOT Release) ---
    req_id_2 = f"{test_prefix}REQ_FARM_YOUNG"
    offer_id_2 = f"{test_prefix}OFF_FARM_YOUNG"
    
    print(f"Creating FarmDeals Test Case (Young): {offer_id_2} (10 Days Old)")
    
    db.requests.insert_one({
        "id": req_id_2,
        "platform": "farm_deals",
        "type": "standard",
        "status": "completed"
    })
    
    db.offers.insert_one({
        "id": offer_id_2,
        "request_id": req_id_2,
        "seller_id": seller_id,
        "status": "delivered",
        "delivered_at": datetime.utcnow() - timedelta(days=10), # < 14 days
        "price": 10000
    })
    
    # --- Scenario 3: FarmDeals (Standard) - Delivered 15 days ago (Should Release) ---
    req_id_3 = f"{test_prefix}REQ_FARM_OLD"
    offer_id_3 = f"{test_prefix}OFF_FARM_OLD"
    order_id_3 = f"{test_prefix}ORD_FARM_OLD"

    print(f"Creating FarmDeals Test Case (Old): {order_id_3} (15 Days Old)")
    
    db.requests.insert_one({
        "id": req_id_3,
        "platform": "farm_deals",
        "type": "standard",
        "status": "completed"
    })
    
    db.offers.insert_one({
        "id": offer_id_3,
        "request_id": req_id_3,
        "seller_id": seller_id,
        "status": "delivered",
        "delivered_at": datetime.utcnow() - timedelta(days=15), # > 14 days
        "price": 10000
    })
    
    db.orders.insert_one({
        "order_id": order_id_3,
        "origin_offer_id": offer_id_3,
        "seller_id": seller_id,
        "total_amount": 10000,
        "status": "delivered", 
        "platform": "farm_deals",
        "delivery_method": "platform"
    })

    # --- Run Auto Release Job ---
    print("\nRunning check_rfq_auto_release()...\n")
    try:
        await check_rfq_auto_release()
    except Exception as e:
        print(f"ERROR executing job: {e}")

    # --- Verify Results ---
    print("\n--- Verification Results ---")
    
    # Check PyExpress (Should be Completed)
    offer_1 = db.offers.find_one({"id": offer_id_1})
    status_1 = offer_1.get("status")
    print(f"1. PyExpress (4 Days): Status = {status_1} [{'PASSED' if status_1 == 'completed' else 'FAILED'}]")
    
    # Check FarmDeals Young (Should be Delivered/Unchanged)
    offer_2 = db.offers.find_one({"id": offer_id_2})
    status_2 = offer_2.get("status")
    print(f"2. FarmDeals (10 Days): Status = {status_2} [{'PASSED' if status_2 == 'delivered' else 'FAILED'}]")
    
    # Check FarmDeals Old (Should be Completed)
    offer_3 = db.offers.find_one({"id": offer_id_3})
    status_3 = offer_3.get("status")
    print(f"3. FarmDeals (15 Days): Status = {status_3} [{'PASSED' if status_3 == 'completed' else 'FAILED'}]")

    print("\nDone.")

if __name__ == "__main__":
    asyncio.run(verify_auto_release())
