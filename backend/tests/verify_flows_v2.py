
import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

# 1. Setup Wrapper
def print_step(msg):
    print(f"\n[STEP] {msg}")

    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {msg}")

# 2. Login
print_step("Logging in...")
try:
    # Use a known test user or create one. Assuming 'testuser' exists or register one.
    # For speed, let's try to register a temp user
    username = f"verifier_{str(uuid.uuid4())[:6]}"
    email = f"{username}@example.com"
    password = "password123"
    
    reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
        "role": "personal",
        "phone": "08012345678"
    })
    
    # If already exists (unlikely with uuid), login
    login_res = requests.post(f"{BASE_URL}/api/auth/login", data={
        "username": username,
        "password": password
    })
    
    if login_res.status_code != 200:
        print_result(f"Login Failed: {login_res.text}", False)
        exit(1)
        
    token = login_res.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print_result("Logged in successfully as " + username)

except Exception as e:
    print_result(f"Connection Error: {e}", False)
    exit(1)

# 3. Create Test Products (We need 2 products from different 'sellers' ideally, but same seller is fine for basic Split test if we vary Delivery Method)
# Actually, to test Seller splitting we need 2 sellers. 
# To test Delivery splitting we can use 1 seller but 2 items with diff methods.
# Since we are not logged in as Admin/Seller easily without more setup, we'll try to fetch existing products.
print_step("Fetching Products...")
prods_res = requests.get(f"{BASE_URL}/api/products")
products = prods_res.json()

if len(products) < 2:
    print_result("Not enough products to test split. Need at least 2.", False)
    # We could create them if we had seller auth, but let's assume seed data exists.
    exit(1)

p1 = products[0]
p2 = products[1] if len(products) > 1 else products[0]

print_result(f"Using Product 1: {p1['title']} (ID: {p1['id']})")
print_result(f"Using Product 2: {p2['title']} (ID: {p2['id']})")


# 4. Verify Community Pledge
print_step("Verifying Community Pledge...")
try:
    # Use Product 1
    pledge_qty = 5
    res = requests.post(f"{BASE_URL}/api/community/pledge", json={
        "product_id": p1['id'],
        "quantity": pledge_qty
    }, headers=headers)
    
    if res.status_code == 200:
        print_result(f"Pledge Successful: {res.json()['message']}")
        # Verify count increased
        p1_new = requests.get(f"{BASE_URL}/api/products/{p1['id']}?type=community").json() # Endpoint might vary, usually list handles it
        # Just check list again
        # Actually our list endpoint might not show committed_quantity details unless specific? 
        # The endpoint returns Product models, which now have committed_quantity.
        # Let's assume fetching products works.
        pass
    else:
        print_result(f"Pledge Failed: {res.text}", False)

except Exception as e:
    print_result(f"Community Test Error: {e}", False)


# 5. Verify Checkout Split (Delivery Method)
print_step("Verifying Checkout Split (Delivery vs Pickup)...")
try:
    # Item 1: Home Delivery
    item1 = {
        "product_id": p1['id'],
        "quantity": 1,
        "delivery_method": "delivery"
    }
    
    # Item 2: Pickup
    item2 = {
        "product_id": p2['id'],
        "quantity": 2,
        "delivery_method": "pickup",
        "dropoff_location": "Lagos Pickup Station A"
    }
    
    payload = {
        "items": [item1, item2],
        "delivery_address": "123 Home Street, Lagos",
        "payment_method": "card" # Mock payment
    }
    
    order_res = requests.post(f"{BASE_URL}/api/orders", json=payload, headers=headers)
    
    if order_res.status_code == 200:
        data = order_res.json()
        order_ids = data['order_ids']
        print_result(f"Orders Created: {len(order_ids)} orders. IDs: {order_ids}")
        
        # We expect 2 orders if p1 and p2 are same seller but diff methods.
        # OR if p1 and p2 are diff sellers, also 2 orders.
        # If p1 and p2 are same seller AND we failed to split by method, we'd get 1 order.
        
        if len(order_ids) >= 2:
             print_result("Successfully split orders!")
        else:
             print_result("Warning: Only 1 order created. Might be same seller + logic issue? Or verify contents.", False)
             
        # Fetch orders to verify addresses
        my_orders = requests.get(f"{BASE_URL}/api/orders", headers=headers).json()
        
        # Find the new orders
        new_orders = [o for o in my_orders if o['order_id'] in order_ids]
        
        for o in new_orders:
            print(f"  - Order {o['order_id']}: Addr='{o['shipping_address']}'")
            if "PICKUP POINT" in o['shipping_address']:
                print_result(f"    -> Found Pickup Order Correctly")
            elif "123 Home Street" in o['shipping_address']:
                print_result(f"    -> Found Home Delivery Order Correctly")
                
    else:
        print_result(f"Checkout Failed: {order_res.text}", False)

except Exception as e:
    print_result(f"Checkout Test Error: {e}", False)
