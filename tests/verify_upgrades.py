
import requests
import uuid
import sys
import random

BASE_URL = "http://localhost:8000"

def generate_random_user(role="buyer"):
    uid = str(uuid.uuid4())[:8]
    return {
        "first_name": f"Test{uid}",
        "last_name": "User",
        "username": f"user{uid}",
        "email_or_phone": f"user{uid}@example.com",
        "password": "password123",
        "phone": f"080{uid}",
        "gender": "male",
        "date_of_birth": "1990-01-01",
        "user_path": role,
        "verification_info": {}
    }

def test_personal_registration():
    print("Testing Personal Registration...")
    user_data = generate_random_user("buyer")
    user_data["buyer_type"] = "skip"
    
    # First step: Register
    # For this test simplify by calling complete-registration directly if possible
    # But API requires a process. Let's try direct call to complete-registration
    
    response = requests.post(f"{BASE_URL}/api/auth/complete-registration", json=user_data)
    if response.status_code == 200:
        print("[OK] Personal Registration Successful")
        return response.json()['token']
    else:
        print(f"[FAILED] Personal Registration Failed: {response.text}")
        return None

def test_partner_registration_with_bvn():
    print("\nTesting Partner Registration with BVN...")
    user_data = generate_random_user("partner")
    user_data["first_name"] = "TestPartner" # Fixed name for mock matching
    user_data["last_name"] = "User"
    user_data["partner_type"] = "farmer"
    user_data["bvn"] = "12345678901"
    
    response = requests.post(f"{BASE_URL}/api/auth/complete-registration", json=user_data)
    
    if response.status_code == 200:
        print("[OK] Partner Registration Successful")
        user = response.json()['user']
        return response.json()['token'], user['id']
    else:
        print(f"[FAILED] Partner Registration Failed: {response.text}")
        return None, None

def login_admin():
    print("\nLogging in as Admin...")
    payload = {"email_or_phone": "admin@pyramydhub.com", "password": "admin123"}
    try:
        res = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        if res.status_code == 200:
            print("[OK] Admin Login Successful")
            return res.json()['token']
        else:
            print(f"[FAILED] Admin Login Failed: {res.text}")
            # Try creating admin if missing/failed? for now just fail.
            return None
    except Exception as e:
        print(f"[FAILED] Admin Login Error: {e}")
        return None

def test_admin_verification(admin_token, user_id):
    print(f"\nTesting Admin Verification for User {user_id}...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Verify User
    res = requests.put(f"{BASE_URL}/api/admin/users/{user_id}/verify", headers=headers)
    
    if res.status_code == 200:
        print(f"[OK] Verification Result: {res.json()['message']}")
        
        # Check if DVA was created (by checking user profile/admin get)
        # We can't easily check DB directly here without pymongo, 
        # but we can try login as user or check admin user list?
        # Let's trust the message for now or add a 'get user' check if admin has endpoint.
        pass
    else:
        print(f"[FAILED] Verification Failed: {res.text}")

if __name__ == "__main__":
    print("Starting Verification...")
    try:
        requests.get(BASE_URL)
    except requests.exceptions.ConnectionError:
        print("[FAILED] Server is not running. Please start the backend server first.")
        sys.exit(1)
        
    token = test_personal_registration()
    partner_token, partner_id = test_partner_registration_with_bvn()
    
    if partner_id:
        admin_token = login_admin()
        if admin_token:
            test_admin_verification(admin_token, partner_id)
    
    # End
