import sys
import os
from datetime import datetime, timedelta

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_user

# --- Test Data ---
buyer_user = {
    "id": "buyer_123",
    "username": "buyer_test",
    "email": "buyer@test.com",
    "role": "buyer",
    "is_verified": True
}

seller_user = {
    "id": "seller_456",
    "username": "seller_test",
    "email": "seller@test.com",
    "role": "agent",
    "is_verified": True
}

# --- Client ---
client = TestClient(app)

def run_verification():
    print("🚀 Starting RFQ Flow Verification...")

    # 1. Create Request (Mocking Payment Verification or using direct create)
    # Since verify-payment calls external Paystack, we'll cheat and use the old /requests endpoint 
    # BUT we need to provide payment_reference to pass the check.
    # The check is: if not request_data.payment_reference: raise 402
    
    # We'll use dependency override to switch to Buyer
    app.dependency_overrides[get_current_user] = lambda: buyer_user
    
    req_payload = {
        "type": "standard",
        "items": [{"name": "Test Onion", "quantity": 100, "unit": "Bags"}],
        "region_country": "Nigeria",
        "region_state": "Lagos",
        "location": "Lagos",
        "delivery_date": (datetime.now() + timedelta(days=5)).isoformat(),
        "budget": 500000,
        "payment_reference": "TEST-REF-123", # Fake ref
        "amount_paid": 5000
    }
    
    # Note: connect_to_mongo runs on startup, so DB should be active.
    # If using real DB, this will insert data. 
    # For a specialized test, we'd mock DB, but here we want to test broadly.
    
    print("\n1. Creating Request (as Buyer)...")
    res = client.post("/api/requests/", json=req_payload)
    if res.status_code != 200:
        print(f"❌ Failed to create request: {res.text}")
        return
    
    request_id = res.json()["request_id"]
    print(f"✅ Request Created: {request_id}")

    # 2. Make Offer (as Seller)
    app.dependency_overrides[get_current_user] = lambda: seller_user
    
    offer_payload = {
        "price": 480000,
        "items": [
            {"name": "Test Onion", "quantity": 100, "unit": "Bags", "target_price": 4800}
        ],
        "delivery_date": (datetime.now() + timedelta(days=3)).isoformat(),
        "notes": "I can deliver early."
    }
    
    print(f"\n2. Making Offer (as Seller) on {request_id}...")
    res = client.post(f"/api/requests/{request_id}/offers", json=offer_payload)
    if res.status_code != 200:
        print(f"❌ Failed to make offer: {res.text}")
        return
        
    offer_id = res.json()["offer_id"]
    print(f"✅ Offer Created: {offer_id}")
    
    # 3. Accept Offer & Set Terms (as Buyer)
    app.dependency_overrides[get_current_user] = lambda: buyer_user
    
    accept_payload = {
        "acknowledgment_note": "Please ensure good quality.",
        "confirmed_delivery_date": (datetime.now() + timedelta(days=4)).isoformat(),
        "payment_terms": {"upfront_percent": 70, "on_delivery_percent": 30}
    }
    
    print(f"\n3. Accepting Offer with Terms (as Buyer) on {offer_id}...")
    res = client.post(f"/api/offers/{offer_id}/accept", json=accept_payload)
    if res.status_code != 200:
        print(f"❌ Failed to accept offer: {res.text}")
        return
        
    print(f"✅ Offer Accepted (Terms Sent). Status: {res.json()['status']}")
    
    # 4. Confirm Terms (as Seller)
    app.dependency_overrides[get_current_user] = lambda: seller_user
    
    print(f"\n4. Confirming Terms (as Seller)...")
    res = client.post(f"/api/offers/{offer_id}/confirm-terms")
    if res.status_code != 200:
        print(f"❌ Failed to confirm terms: {res.text}")
        return
        
    order_id = res.json()["order_id"]
    print(f"✅ Terms Confirmed! Order Created: {order_id}")
    
    print("\n🎉 Verification SUCCESS! The Negotiation Flow works correctly.")

if __name__ == "__main__":
    run_verification()
