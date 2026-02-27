import sys
import os
import pytest
from fastapi.testclient import TestClient
import uuid

# Add parent directory to path so we can import server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Environment BEFORE importing server/database so database.py picks up the correct DB name
os.environ["DB_NAME"] = "test_pyramyd_integration"
os.environ["JWT_SECRET"] = "test-secret-key"

# Now import app
from server import app
from database import get_db, get_client

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    # Setup: Ensure clean DB
    client_mongo = get_client()
    # Drop test database to start fresh
    client_mongo.drop_database("test_pyramyd_integration")
    
    yield
    
    # Teardown: Drop database again locally if needed
    client_mongo.drop_database("test_pyramyd_integration")

def test_full_order_flow():
    # 1. Register Buyer
    buyer_email = f"buyer_{uuid.uuid4()}@example.com"
    buyer_username = f"buyer_{uuid.uuid4()}"
    buyer_data = {
        "email": buyer_email,
        "username": buyer_username,
        "password": "password123",
        "role": "personal",
        "first_name": "Integration",
        "last_name": "Buyer"
    }
    res = client.post("/api/auth/register", json=buyer_data)
    assert res.status_code == 200, res.text
    buyer_token = res.json()["token"]
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    
    # 2. Register Seller (Farmer)
    seller_email = f"seller_{uuid.uuid4()}@example.com"
    seller_username = f"seller_{uuid.uuid4()}"
    seller_data = {
        "email": seller_email,
        "username": seller_username,
        "password": "password123",
        "role": "farmer",
        "first_name": "Integration",
        "last_name": "Farmer",
        "business_name": "Int Farm"
    }
    res = client.post("/api/auth/register", json=seller_data)
    assert res.status_code == 200, res.text
    seller_token = res.json()["token"]
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    
    # Bypass KYC: Update seller directly in DB to approved
    db = get_db()
    db.users.update_one({"email": seller_email}, {"$set": {"kyc_status": "approved", "is_verified": True}})
    
    # 3. Create Product (Seller)
    product_data = {
        "title": "Integration Test Corn",
        "category": "grains_legumes",
        "price_per_unit": 1000,
        "quantity_available": 100,
        "description": "Test corn for integration",
        "location": "Lagos",
        "images": ["http://example.com/corn.jpg"],
        "unit_of_measure": "kg",
        "platform": "pyhub",
        "minimum_order_quantity": 1
    }
    # Note: Check correct endpoint for product creation
    res = client.post("/api/products/", json=product_data, headers=seller_headers)
    if res.status_code == 404:
        # Fallback to create route if needed
        res = client.post("/api/products/create", json=product_data, headers=seller_headers)
    
    assert res.status_code == 200, res.text
    # Check if response creates product or returns dict
    if "data" in res.json():
        product_id = res.json()["data"]["id"]
    else:
        product_id = res.json().get("id") or res.json().get("_id") or res.json().get("product_id")
    
    # 4. Create Order (Buyer)
    order_data = {
        "product_id": product_id,
        "quantity": 2,
        "delivery_method": "pickup", 
        "unit": "kg"
    }
    res = client.post("/api/orders/create", json=order_data, headers=buyer_headers)
    assert res.status_code == 200, res.text
    order_id = res.json()["order_id"]
    
    # 5. Simulate Payment Success (Update Order Status Directly)
    # In real world, Paystack webhook updates this.
    db.orders.update_one({"order_id": order_id}, {"$set": {"status": "held_in_escrow"}})
    
    # 6. Seller Marks Delivered
    # Endpoint: POST /api/orders/{order_id}/mark-delivered
    res = client.post(f"/api/orders/{order_id}/mark-delivered", headers=seller_headers)
    assert res.status_code == 200, f"Mark delivered failed: {res.text}"
    status_res = res.json()
    # Check status response structure
    assert status_res.get("status") == "delivered", f"Expected delivered, got {status_res}"
    
    # 7. Buyer Confirms Delivery
    # Endpoint: POST /api/orders/{order_id}/confirm-delivery
    res = client.post(f"/api/orders/{order_id}/confirm-delivery", headers=buyer_headers)
    assert res.status_code == 200, f"Confirm delivery failed: {res.text}"
    final_status = res.json()
    assert final_status.get("status") == "completed", f"Expected completed, got {final_status}"
    
    # 8. Verify Wallet Balance (Seller should get paid)
    # 2 items * 1000 = 2000. Platform takes cut.
    # Check seller wallet
    res = client.get("/api/wallet/summary", headers=seller_headers)
    assert res.status_code == 200
    wallet_data = res.json()
    balance = wallet_data.get("balance", 0)
    assert balance > 0, "Seller wallet should have funds"
    print(f"Test Pass: Seller wallet balance is {balance}")
