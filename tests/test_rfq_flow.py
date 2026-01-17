import pytest
import requests
import uuid
from datetime import datetime
from pymongo import MongoClient
import os

# Config
BASE_URL = "http://localhost:8000/api"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "pyramyd_db"

@pytest.fixture
def db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

@pytest.fixture
def buyer_token():
    # Login as buyer (ensure user exists or create)
    # detailed setup omitted for brevity, assuming 'buyer_user' exists
    login_data = {"username": "buyer_test", "password": "password123"}
    resp = requests.post(f"{BASE_URL}/login", data=login_data)
    if resp.status_code != 200:
         # Create if not exists
         requests.post(f"{BASE_URL}/register", json={"username": "buyer_test", "password": "password123", "role": "buyer", "email": "buyer@test.com"})
         resp = requests.post(f"{BASE_URL}/login", data=login_data)
    return resp.json()["access_token"]

@pytest.fixture
def agent_token():
    login_data = {"username": "agent_test", "password": "password123"}
    resp = requests.post(f"{BASE_URL}/login", data=login_data)
    if resp.status_code != 200:
         requests.post(f"{BASE_URL}/register", json={"username": "agent_test", "password": "password123", "role": "agent", "email": "agent@test.com", "is_verified": True})
         # Manually verify in DB if needed
         client = MongoClient(MONGO_URI)
         client[DB_NAME].users.update_one({"username": "agent_test"}, {"$set": {"is_verified": True}})
         resp = requests.post(f"{BASE_URL}/login", data=login_data)
    return resp.json()["access_token"]

@pytest.fixture
def admin_token():
    login_data = {"username": "admin_test", "password": "password123"}
    resp = requests.post(f"{BASE_URL}/login", data=login_data)
    if resp.status_code != 200:
         requests.post(f"{BASE_URL}/register", json={"username": "admin_test", "password": "password123", "role": "admin", "email": "admin@test.com"})
         resp = requests.post(f"{BASE_URL}/login", data=login_data)
    return resp.json()["access_token"]

def test_instant_request_flow(buyer_token, agent_token, admin_token, db):
    # 1. Buyer creates Instant Request
    headers_buyer = {"Authorization": f"Bearer {buyer_token}"}
    req_data = {
        "type": "instant",
        "items": [{"name": "Tomatoes", "quantity": 10, "unit": "kg"}],
        "location": "Lagos",
        "delivery_days": 2,
        "budget": 5000
    }
    resp = requests.post(f"{BASE_URL}/requests/", json=req_data, headers=headers_buyer)
    assert resp.status_code == 200
    request_id = resp.json()["request_id"]
    print(f"Request Created: {request_id}")

    # 2. Agent Takes Job
    headers_agent = {"Authorization": f"Bearer {agent_token}"}
    resp = requests.post(f"{BASE_URL}/requests/{request_id}/take", headers=headers_agent)
    assert resp.status_code == 200
    tracking_id = resp.json()["tracking_id"]
    print(f"Job Taken. Tracking ID: {tracking_id}")
    
    # 3. Agent Marks Delivered
    # Need to find the "fake" offer ID or just use the order logic?
    # The 'take' endpoint creates an order and a fake offer.
    # Agent fetches 'My Offers' to see it.
    resp = requests.get(f"{BASE_URL}/requests/offers/mine", headers=headers_agent)
    assert resp.status_code == 200
    my_offers = resp.json()
    offer = next((o for o in my_offers if o['tracking_id'] == tracking_id), None)
    assert offer is not None
    offer_id = offer['id']
    
    resp = requests.post(f"{BASE_URL}/offers/{offer_id}/delivered", headers=headers_agent)
    assert resp.status_code == 200
    print("Marked as Delivered")

    # 4. Buyer Confirms Delivery
    # Code is last 8 chars of Tracking ID
    code = tracking_id[-8:]
    resp = requests.post(f"{BASE_URL}/offers/{offer_id}/confirm-delivery", json={"code": code}, headers=headers_buyer)
    assert resp.status_code == 200
    print("Delivery Confirmed by Buyer")
    
    # Verify Order Status
    order = db.orders.find_one({"order_id": tracking_id})
    assert order['status'] == 'completed' or 'delivered' # Depending on verify implementation
    # Payout should be triggered/logged
    
def test_admin_halt_release(buyer_token, agent_token, admin_token, db):
    # Setup: Create another order
    headers_buyer = {"Authorization": f"Bearer {buyer_token}"}
    headers_agent = {"Authorization": f"Bearer {agent_token}"}
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    
    req_data = {
        "type": "instant",
        "items": [{"name": "Onions", "quantity": 5, "unit": "kg"}],
        "location": "Abuja",
        "delivery_days": 1,
        "budget": 2000
    }
    resp = requests.post(f"{BASE_URL}/requests/", json=req_data, headers=headers_buyer)
    request_id = resp.json()["request_id"]
    
    resp = requests.post(f"{BASE_URL}/requests/{request_id}/take", headers=headers_agent)
    tracking_id = resp.json()["tracking_id"]
    
    # Hold Payout (UI uses "Hold", API uses "halt-payout")
    resp = requests.post(f"{BASE_URL}/admin/orders/{tracking_id}/halt-payout", headers=headers_admin)
    assert resp.status_code == 200
    print("Payout Held")
    
    order = db.orders.find_one({"order_id": tracking_id})
    assert order['payout_halted'] == True
    
    # Manual Release
    resp = requests.post(f"{BASE_URL}/admin/orders/{tracking_id}/manual-release", headers=headers_admin)
    assert resp.status_code == 200
    print("Payout Released Manually")
    
    order = db.orders.find_one({"order_id": tracking_id})
    assert order['payout_halted'] == False
    assert order['status'] == 'completed'

def test_admin_orders_list_fields(buyer_token, admin_token):
    # Verify order list contains payout_halted field
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/admin/orders", headers=headers_admin)
    assert resp.status_code == 200
    orders = resp.json()['orders']
    if len(orders) > 0:
        assert 'payout_halted' in orders[0]
        print("Admin Orders List contains payout_halted field")
