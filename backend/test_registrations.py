import requests
import json
import uuid
import sys

BASE_URL = "http://localhost:8000"

def print_result(flow_name, success, message):
    mark = "PASS" if success else "FAIL"
    print(f"\n[{mark}] {flow_name}: {message}")

def test_personal_registration():
    uid = uuid.uuid4().hex[:8]
    payload = {
        "email_or_phone": f"personal_{uid}@example.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "Personal",
        "username": f"personal_user_{uid}",
        "gender": "male",
        "date_of_birth": "1990-01-01"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        if res.status_code == 200:
            print_result("Personal Registration", True, "Successfully registered personal user.")
        else:
            print_result("Personal Registration", False, f"Failed: {res.text}")
    except Exception as e:
        print_result("Personal Registration", False, f"Error: {e}")

def test_partner_registration(role):
    uid = uuid.uuid4().hex[:8]
    endpoints = {
        "business": "/api/auth/register-business",
        "farmer": "/api/auth/register-partner",
        "agent": "/api/auth/register-partner"
    }
    
    endpoint = endpoints.get(role, "/api/auth/register-partner")
    
    payload = {
        "company_name": f"Test {role.capitalize()} {uid}",
        "email_or_phone": f"{role}_{uid}@example.com",
        "password": "Password123!",
        "contact_person": f"Contact {uid}",
        "phone": f"0801234{uid[:4]}",
        "address": "123 Test St",
        "cac_number": f"RC{uid}",
        "bvn": f"2222{uid[:6]}",
        "partner_type": role
    }
    
    try:
        res = requests.post(f"{BASE_URL}{endpoint}", json=payload)
        if res.status_code == 200:
            print_result(f"{role.capitalize()} Registration", True, f"Successfully registered {role} user.")
        else:
            print_result(f"{role.capitalize()} Registration", False, f"Failed: {res.text} (payload: {payload})")
    except Exception as e:
        print_result(f"{role.capitalize()} Registration", False, f"Error: {e}")

if __name__ == "__main__":
    print("Testing Registration Flows...")
    try:
        # Check if backend is alive
        requests.get(f"{BASE_URL}/api/health")
    except Exception:
        print("[ERROR] Cannot connect to backend. Is the FastAPI server running on port 8000?")
        sys.exit(1)
        
    test_personal_registration()
    test_partner_registration("business")
    test_partner_registration("farmer")
    test_partner_registration("agent")
