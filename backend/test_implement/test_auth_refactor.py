import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:8000/api/auth"

def test_auth_flow():
    print("Testing Auth Refactor...")

    # 1. Register with Email
    email_user = {
        "first_name": "Test",
        "last_name": "Email",
        "username": f"test_email_{uuid.uuid4().hex[:8]}",
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "password": "password123",
        "phone": ""
    }
    print(f"\n1. Registering with Email: {email_user['email']}")
    try:
        response = requests.post(f"{BASE_URL}/register", json=email_user)
        if response.status_code == 200:
            print("   SUCCESS")
            print(f"   Response: {response.json()}")
        else:
            print(f"   FAILED: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # 2. Register with Phone
    phone_user = {
        "first_name": "Test",
        "last_name": "Phone",
        "username": f"test_phone_{uuid.uuid4().hex[:8]}",
        "email": "",
        "password": "password123",
        "phone": "+2348012345678" 
    }
    print(f"\n2. Registering with Phone: {phone_user['phone']}")
    try:
        response = requests.post(f"{BASE_URL}/register", json=phone_user)
        if response.status_code == 200:
            print("   SUCCESS")
            print(f"   Response: {response.json()}")
        else:
            print(f"   FAILED: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # 3. Login with Email
    print(f"\n3. Login with Email: {email_user['email']}")
    login_email = {
        "email_or_phone": email_user['email'],
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_email)
        if response.status_code == 200:
            print("   SUCCESS")
            token_email = response.json()['token']
        else:
            print(f"   FAILED: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # 4. Login with Phone
    print(f"\n4. Login with Phone: {phone_user['phone']}")
    login_phone = {
        "email_or_phone": phone_user['phone'],
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_phone)
        if response.status_code == 200:
            print("   SUCCESS")
            token_phone = response.json()['token']
        else:
            print(f"   FAILED: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # 5. Complete Registration (Email User)
    print(f"\n5. Complete Registration (Email User)")
    complete_email_user = {
        "first_name": "Test",
        "last_name": "Email Complete",
        "username": f"complete_email_{uuid.uuid4().hex[:8]}",
        "email": f"complete_{uuid.uuid4().hex[:8]}@example.com",
        "password": "password123",
        "phone": "",
        "gender": "male",
        "date_of_birth": "1990-01-01",
        "user_path": "buyer",
        "buyer_type": "skip",
        "email_or_phone": "" # Should be ignored or optional now
    }
    try:
        response = requests.post(f"{BASE_URL}/complete-registration", json=complete_email_user)
        if response.status_code == 200:
            print("   SUCCESS")
            print(f"   Response: {response.json()}")
        else:
            print(f"   FAILED: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # 6. Complete Registration (Phone User)
    print(f"\n6. Complete Registration (Phone User)")
    complete_phone_user = {
        "first_name": "Test",
        "last_name": "Phone Complete",
        "username": f"complete_phone_{uuid.uuid4().hex[:8]}",
        "email": "",
        "password": "password123",
        "phone": "+2348087654321",
        "gender": "female",
        "date_of_birth": "1995-05-05",
        "user_path": "partner",
        "partner_type": "agent",
        "email_or_phone": "" # Should be ignored or optional now
    }
    try:
        response = requests.post(f"{BASE_URL}/complete-registration", json=complete_phone_user)
        if response.status_code == 200:
            print("   SUCCESS")
            print(f"   Response: {response.json()}")
        else:
            print(f"   FAILED: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")

if __name__ == "__main__":
    test_auth_flow()
