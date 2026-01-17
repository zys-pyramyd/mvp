import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def print_step(msg):
    print(f"\n{'='*50}\n{msg}\n{'='*50}")

def signup_user(username, email, role, password="password123"):
    print(f"Signing up {role}: {username} (BVN: 12345678901)...")
    payload = {
        "username": username,
        "email": email,
        "password": password,
        "role": role,
        "phone": "08012345678",
        "bvn": "12345678901" # Mock BVN
    }
    try:
        # Use register endpoint (handling the new flow)
        # Note: If BVN logic is strict, this might fail unless mocked in backend or using Partner flow.
        # Assuming MVP register covers it.
        # Wait, if role is 'partner' (agent), it asks for BVN.
        res = requests.post(f"{BASE_URL}/auth/register", json=payload)
        
        # If user already exists, try login
        if res.status_code == 400 and "exists" in res.text:
            print("User exists, logging in...")
            return login_user(username, password)
            
        if res.status_code != 200:
            print(f"Register failed: {res.text}")
            return None
            
        data = res.json()
        return data["access_token"]
    except Exception as e:
        print(f"Error: {e}")
        return None

def login_user(username, password="password123"):
    payload = {
        "username": username,
        "password": password
    }
    res = requests.post(f"{BASE_URL}/auth/login", data=payload) # OAuth2 form data
    if res.status_code == 200:
        return res.json()["access_token"]
    print(f"Login failed: {res.text}")
    return None

def main():
    print_step("1. SETUP USERS")
    # Buyer
    buyer_token = signup_user("simulator_buyer", "buyer@sim.com", "personal")
    if not buyer_token: return
    
    # Agent
    agent_token = signup_user("simulator_agent", "agent@sim.com", "partner")
    if not agent_token: return
    
    print_step("2. CREATE RFQ (BUYER)")
    rfq_payload = {
        "title": "Simulation Rice Supply",
        "items": [
            {"name": "Rice", "quantity": 10, "unit": "bags", "specifications": "Long grain"},
            {"name": "Oil", "quantity": 5, "unit": "liters", "specifications": "Vegetable"}
        ],
        "delivery_days": 2, # PyExpress
        "location": "Lagos, Ikeja (Simulated)",
        "budget": 50000,
        "quantity_required": 15,
        "unit_of_measure": "mixed",
        "persona": "personal",
        "business_category": "General"
    }
    
    headers_buyer = {"Authorization": f"Bearer {buyer_token}"}
    res = requests.post(f"{BASE_URL}/requests", json=rfq_payload, headers=headers_buyer)
    print(f"Create RFQ: {res.status_code} - {res.text}")
    if res.status_code != 200: return
    request_id = res.json()["request_id"]
    print(f"Request ID: {request_id} | Platform: {res.json()['platform_assigned']}")

    print_step("3. LIST REQUESTS & MAKE OFFER (AGENT)")
    headers_agent = {"Authorization": f"Bearer {agent_token}"}
    
    # Agent checks Market
    res = requests.get(f"{BASE_URL}/requests?platform=PyExpress", headers=headers_agent)
    requests_list = res.json()
    print(f"Found {len(requests_list)} PyExpress requests.")
    
    # Verify our request is there
    target_req = next((r for r in requests_list if r["id"] == request_id), None)
    if not target_req:
        print("Error: Request not found in list.")
        return

    # Make Offer
    offer_payload = {
        "price": 48000,
        "quantity_offered": 15,
        "delivery_date": "2026-02-01T10:00:00",
        "notes": "I can deliver fast."
    }
    res = requests.post(f"{BASE_URL}/requests/{request_id}/offers", json=offer_payload, headers=headers_agent)
    print(f"Make Offer: {res.status_code} - {res.text}")
    offer_id = res.json().get("offer_id")
    
    print_step("4. ACCEPT OFFER (BUYER)")
    # Buyer fetches request (implied MyRequests)
    # Accept
    res = requests.post(f"{BASE_URL}/offers/{offer_id}/accept", headers=headers_buyer)
    print(f"Accept Offer: {res.status_code} - {res.text}")
    if res.status_code != 200: return
    data = res.json()
    tracking_id = data["tracking_id"]
    otp_code = data["otp_code"] # Last 8 chars
    print(f"Tracking ID: {tracking_id}")
    print(f"Expected Confirmation Code (Last 8): {otp_code}")
    
    print_step("5. AGENT MARKS DELIVERED")
    res = requests.post(f"{BASE_URL}/offers/{offer_id}/delivered", headers=headers_agent)
    print(f"Mark Delivered: {res.status_code} - {res.text}")
    
    print_step("6. BUYER CONFIRMS RECEIPT (MANUAL)")
    confirm_payload = {"otp_code": otp_code}
    res = requests.post(f"{BASE_URL}/offers/{offer_id}/confirm-delivery", json=confirm_payload, headers=headers_buyer)
    print(f"Confirm Delivery: {res.status_code} - {res.text}")
    
    if res.status_code == 200:
        print("\nSUCCESS: Full Cycle Verified!")
    else:
        print("\nFAILED: Confirmation failed.")

if __name__ == "__main__":
    main()
