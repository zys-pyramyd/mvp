
import os
from pymongo import MongoClient, TEXT, ASCENDING, DESCENDING

# Connect to DB (Make sure to set MONGO_URL env var before running)
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
print(f"Connecting to MongoDB at {mongo_url.split('@')[-1] if '@' in mongo_url else 'localhost'}...")

client = MongoClient(mongo_url)
db = client.pyramyd_db

def create_indexes():
    print("Creating indexes...")
    
    # 1. Users
    # Unique constraint on email and username
    # This prevents duplicate registrations
    print("- Users Collection")
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.users.create_index([("role", ASCENDING)])
    db.users.create_index([("bvn", ASCENDING)]) # For Partner lookup

    # 2. Products
    # Search efficiency
    print("- Products Collection")
    db.products.create_index([("id", ASCENDING)], unique=True)
    db.products.create_index([("seller_id", ASCENDING)])
    db.products.create_index([("category", ASCENDING)])
    db.products.create_index([("platform", ASCENDING)]) # Retail vs Farm
    # Text Index for Search
    db.products.create_index([
        ("title", TEXT), 
        ("description", TEXT),
        ("seller_name", TEXT),
        ("agent_name", TEXT)
    ], weights={
        "title": 10,
        "seller_name": 5,
        "description": 1
    })

    # 3. Orders
    print("- Orders Collection")
    db.orders.create_index([("order_id", ASCENDING)], unique=True)
    db.orders.create_index([("buyer_id", ASCENDING)])
    db.orders.create_index([("seller_id", ASCENDING)])
    db.orders.create_index([("status", ASCENDING)])
    db.orders.create_index([("created_at", DESCENDING)]) # For sorting by newest

    # 4. Wallet Transactions
    print("- Wallet Transactions Collection")
    db.wallet_transactions.create_index([("user_id", ASCENDING)])
    db.wallet_transactions.create_index([("reference", ASCENDING)], unique=True) # Critical for idempotency

    # 5. Community / Group Buy
    print("- Community Collections")
    db.group_buy_participants.create_index([("product_id", ASCENDING)])
    db.group_buy_participants.create_index([("user_id", ASCENDING)])

    print("✅ Indexes created successfully!")

if __name__ == "__main__":
    try:
        create_indexes()
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
