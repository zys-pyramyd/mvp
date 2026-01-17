import requests
import time

BASE_URL = "http://localhost:8000"

def register_user(email, password, role="member"):
    data = {"email": email, "password": password, "full_name": "Test User", "role": role, "username": email.split('@')[0]}
    res = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    if res.status_code == 200:
        return res.json()["token"]
    # If already exists, login
    res = requests.post(f"{BASE_URL}/api/auth/login", json={"email_or_phone": email, "password": password})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return None
    return res.json()["access_token"]

def verify_group_buying():
    print("Verifying Group Buying...")
    try:
        # 1. Register/Login User (Agent)
        agent_token = register_user("agent1@test.com", "password", "agent")
        if not agent_token:
            print("Failed to get agent token. Exiting.")
            return

        headers = {"Authorization": f"Bearer {agent_token}"}
        print("Agent logged in.")

        # 2. Create Community
        comm_data = {"name": "Test Community", "description": "For testing", "category": "general", "privacy": "public"}
        res = requests.post(f"{BASE_URL}/api/communities", json=comm_data, headers=headers)
        if res.status_code == 200:
            comm_id = res.json()["community_id"]
            print(f"Community created: {comm_id}")
        else:
            # Maybe created before, fetch it?
            # Assuming it created a new one or we can lists
             print("Failed to create community or already exists")
             # For test simplicity, create a unique one or list
             comm_id = "test_comm_id_placeholder" # This might fail if strict

        # 3. Get My Communities
        res = requests.get(f"{BASE_URL}/api/my-communities", headers=headers)
        print(f"My Communities: {res.status_code}")
        if res.status_code == 200:
             comms = res.json()["communities"]
             print(f"Found {len(comms)} communities")
             if len(comms) > 0:
                 comm_id = comms[0]['id']

        # 4. Create Group Order
        order_data = {
            "community_id": comm_id,
            "product_name": "Test Rice",
            "description": "Bulk rice",
            "price_per_unit": 1000,
            "target_quantity": 100,
            "unit": "bag",
            "deadline": "2025-01-01"
        }
        res = requests.post(f"{BASE_URL}/api/group-orders", json=order_data, headers=headers)
        print(f"Create Group Order: {res.status_code}")
        if res.status_code == 200:
            order_id = res.json()["order_id"]
            
            # 5. List Group Orders
            res = requests.get(f"{BASE_URL}/api/communities/{comm_id}/group-orders", headers=headers)
            print(f"List Orders: {res.status_code}")
            
            # 6. Join Order (Pledge)
            res = requests.post(f"{BASE_URL}/api/group-orders/{order_id}/join", json={"quantity": 5}, headers=headers)
            print(f"Join Order: {res.status_code}")

    except Exception as e:
        print(f"Verification Failed: {e}")

if __name__ == "__main__":
    verify_group_buying()
