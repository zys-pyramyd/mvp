
import requests
import uuid
import sys
import datetime

BASE_URL = "http://localhost:8000"

def generate_random_user(role="buyer"):
    uid = str(uuid.uuid4())[:8]
    return {
        "first_name": f"Test{uid}",
        "last_name": "User",
        "username": f"user{uid}",
        "email": f"user{uid}@example.com",
        "email_or_phone": f"user{uid}@example.com", # Required field
        "password": "password123",
        "phone": f"080{uid}",
        "gender": "male",
        "date_of_birth": "1990-01-01",
        "role": role,
        "is_verified": True # Simulate verified
    }

def test_standard_request_flow():
    print("Starting Standard Request Integration Test...")
    
    # 1. Register/Login User
    user_data = generate_random_user()
    # Note: Using backend register endpoint directly or simulating via direct DB insertion if possible?
    # Let's try the public register endpoints.
    # Assuming /api/auth/register or similar exists. 
    # Based on server.py, auth_router is at /api/auth. 
    # Let's try to register.
    
    # Actually, simpler to just login as admin or create a user if we can.
    # verify_upgrades.py used /api/auth/complete-registration.
    
    print(f"Registering user {user_data['username']}...")
    reg_data = {
        "first_name": user_data['first_name'],
        "last_name": user_data['last_name'],
        "username": user_data['username'],
        "email": user_data['email'],
        "email_or_phone": user_data['email_or_phone'],
        "password": user_data['password'],
        "phone": user_data['phone'],
        "gender": user_data['gender'],
        "date_of_birth": user_data['date_of_birth'],
        "user_path": "buyer", 
        "partner_type": "skip" # If partner flow
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/auth/complete-registration", json=reg_data)
        if res.status_code != 200:
            print(f"Registration failed: {res.text}")
            return
            
        token = res.json()['token']
        print("User registered and logged in.")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Upload/Create Request
        print("Creating Standard Request...")
        
        payload = {
            "type": "standard",
            "items": [
                {
                    "name": "Test Rice",
                    "quantity": 100,
                    "unit": "kg",
                    "target_price": 5000
                }
            ],
            "location": "Lagos, Nigeria",
            "delivery_date": (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat(),
            "budget": 500000,
            "notes": "Integration Test Request",
            "payment_reference": f"TEST_REF_{uuid.uuid4().hex[:8]}", # Simulated Paystack Ref
            "amount_paid": 5000.0,
            "estimated_budget": 500000.0
        }
        
        req_res = requests.post(f"{BASE_URL}/api/requests/", json=payload, headers=headers)
        
        if req_res.status_code == 200:
            data = req_res.json()
            print(f"[SUCCESS] Request Created! ID: {data['request_id']}")
            print(f"Response: {data}")
            
            # Verify it shows up in list
            print("Verifying request in list...")
            list_res = requests.get(f"{BASE_URL}/api/requests/?type=standard", headers=headers)
            if list_res.status_code == 200:
                requests_list = list_res.json()
                found = any(r['id'] == data['request_id'] for r in requests_list)
                if found:
                    print("[SUCCESS] Request found in listing.")
                else:
                    print("[FAILURE] Request not found in listing.")
            else:
                print(f"[FAILURE] Failed to list requests: {list_res.text}")
                
        else:
            print(f"[FAILURE] Request creation failed: {req_res.text}")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to server. Is it running?")

if __name__ == "__main__":
    test_standard_request_flow()
