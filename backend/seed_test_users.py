import requests
import uuid

BASE_URL = "http://localhost:8000"

def register_user(role, email_prefix):
    uid = uuid.uuid4().hex[:4]
    email = f"{email_prefix}_{uid}@example.com"
    payload = {
        "first_name": "Test",
        "last_name": role.capitalize(),
        "username": f"{email_prefix}_{uid}",
        "email": email,
        "phone": f"0800000{uid}",
        "password": "Password123!",
        "role": role
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        if res.status_code == 200:
            print(f"SUCCESS: {role.capitalize()} registered!")
            print(f"Email: {email}")
            print(f"Password: Password123!")
            print("-" * 30)
        else:
            print(f"FAIL: {role.capitalize()} Registration Failed: {res.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("Seeding Test Users for PyExpress Flow...\n")
    register_user("personal", "buyer")
    register_user("farmer", "seller")
