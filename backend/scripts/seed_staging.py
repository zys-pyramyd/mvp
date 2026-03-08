import os
import sys
import uuid
import datetime
import random

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from app.auth import get_password_hash

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
print(f"Connecting to MongoDB at {mongo_url}")

client = MongoClient(mongo_url)
db = client.pyramyd_db

def clear_collections():
    print("Clearing collections for clean staging...")
    db.users.delete_many({})
    db.products.delete_many({})
    db.orders.delete_many({})
    db.requests.delete_many({})
    db.offers.delete_many({})
    db.communities.delete_many({})

def seed_users():
    print("Seeding test users...")
    password = "Password123!"
    hashed_pw = get_password_hash(password)
    
    roles = ['admin', 'buyer', 'farmer', 'agent', 'business', 'driver']
    users = []
    created_users = {}
    
    for r in roles:
        uid = str(uuid.uuid4())
        user_dict = {
            "id": uid,
            "email": f"{r}@test.com",
            "username": f"test_{r}",
            "hashed_password": hashed_pw,
            "role": r,
            "first_name": "Test",
            "last_name": r.capitalize(),
            "phone": f"+23480000000{random.randint(10, 99)}",
            "is_active": True,
            "kyc_status": "approved" if r != 'buyer' else "pending",
            "created_at": datetime.datetime.utcnow(),
            "wallet_balance": 500000 # Pre-fund wallets
        }
        if r == 'farmer':
            user_dict['farm_name'] = "Test Staging Farm"
        
        users.append(user_dict)
        created_users[r] = uid
        print(f"✅ Created {r} user: {r}@test.com / {password}")
        
    db.users.insert_many(users)
    return created_users

def seed_products(user_ids):
    print("Seeding products...")
    farmer_id = user_ids['farmer']
    agent_id = user_ids['agent']
    
    categories = {
        'fruits': ['apples', 'banana', 'orange', 'mango', 'pineapple'],
        'cash_crop': ['cocoa', 'cashewnut', 'sesame_seeds'],
        'feeds': ['chicken_feeds', 'fish_feeds', 'dog_food'],
        'farm_inputs': ['pesticides', 'fertilizers', 'seeds'],
        'spices_vegetables': ['tomatoes', 'onions', 'peppers']
    }
    
    products = []
    
    for cat, subcats in categories.items():
        for subcat in subcats:
            is_wholesale = random.choice([True, False])
            products.append({
                "id": str(uuid.uuid4()),
                "seller_id": farmer_id,
                "agent_id": agent_id if random.random() > 0.5 else None,
                "seller_name": "Test Farmer",
                "title": f"Fresh {subcat.replace('_', ' ').capitalize()}",
                "description": f"High quality {subcat.replace('_', ' ')} straight from the farm.",
                "category": cat,
                "subcategory": subcat,
                "price": float(random.randint(1000, 20000)),
                "price_per_unit": float(random.randint(1000, 20000)),
                "unit": "kg",
                "unit_of_measure": "kg",
                "quantity_available": random.randint(50, 1000),
                "minimum_order_quantity": 10 if is_wholesale else 1,
                "is_active": True,
                "is_verified": True,
                "platform": 'farm_deals' if is_wholesale else 'py_express',
                "images": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwxfHx2ZWdldGFibGVzfGVufDB8fHx8MTc1MzY0MTExMnww&ixlib=rb-4.1.0&q=85"],
                "location": "Lagos",
                "created_at": datetime.datetime.utcnow()
            })
            
    db.products.insert_many(products)
    print(f"✅ Created {len(products)} categorized products.")

def run():
    print("=== STARTING STAGING SEED ===")
    clear_collections()
    user_ids = seed_users()
    seed_products(user_ids)
    print("=== STAGING SEED COMPLETE ===")
    print("You can now log in with the generated test accounts (e.g. buyer@test.com / Password123!) to test flows.")

if __name__ == '__main__':
    run()
