
import os
from pymongo import MongoClient, TEXT, ASCENDING, DESCENDING
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connect to DB (Make sure to set MONGO_URL env var before running)
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
logger.info(f"Connecting to MongoDB at {mongo_url.split('@')[-1] if '@' in mongo_url else 'localhost'}...")

try:
    client = MongoClient(mongo_url)
    db = client.pyramyd_db
    logger.info("Connected successfully.")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    exit(1)

def create_indexes():
    logger.info("Starting index creation...")

    # --- 1. Users Collection ---
    logger.info("Indexing: Users")
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.users.create_index([("role", ASCENDING)])
    db.users.create_index([("bvn", ASCENDING)]) # For Partner lookup
    db.users.create_index([("kyc_status", ASCENDING)])
    
    # --- 2. Products Collection ---
    logger.info("Indexing: Products")
    db.products.create_index([("id", ASCENDING)], unique=True)
    db.products.create_index([("seller_id", ASCENDING)])
    db.products.create_index([("category", ASCENDING)])
    db.products.create_index([("platform", ASCENDING)]) # Retail vs Farm
    db.products.create_index([("community_id", ASCENDING)]) # Products in communities
    
    # Text Index for Search
    try:
        db.products.create_index([
            ("title", TEXT), 
            ("description", TEXT),
            ("seller_name", TEXT),
            ("agent_name", TEXT)
        ], weights={
            "title": 10,
            "seller_name": 5,
            "description": 1
        }, name="ProductTextIndex")
    except Exception as e:
        logger.warning(f"Text index creation warning (might already exist with different options): {e}")

    # --- 3. Orders Collection ---
    logger.info("Indexing: Orders")
    db.orders.create_index([("order_id", ASCENDING)], unique=True)
    db.orders.create_index([("buyer_id", ASCENDING)])
    db.orders.create_index([("seller_id", ASCENDING)])
    db.orders.create_index([("status", ASCENDING)])
    db.orders.create_index([("created_at", DESCENDING)]) # For sorting by newest
    db.orders.create_index([("origin_offer_id", ASCENDING)]) # Linking to RFQ offers
    db.orders.create_index([("payment_reference", ASCENDING)]) # For Paystack lookups

    # --- 4. Wallet Transactions ---
    logger.info("Indexing: Wallet Transactions")
    db.wallet_transactions.create_index([("user_id", ASCENDING)])
    db.wallet_transactions.create_index([("reference", ASCENDING)], unique=True)
    db.wallet_transactions.create_index([("created_at", DESCENDING)])

    # --- 5. Communities ---
    logger.info("Indexing: Communities")
    db.communities.create_index([("id", ASCENDING)], unique=True)
    db.communities.create_index([("category", ASCENDING)])
    db.communities.create_index([("members_count", DESCENDING)]) # for popularity sorting
    
    # Community Members
    logger.info("Indexing: Community Members")
    db.community_members.create_index([("user_id", ASCENDING)]) # "My Communities"
    db.community_members.create_index([("community_id", ASCENDING)]) # "Community Members"
    db.community_members.create_index([("community_id", ASCENDING), ("user_id", ASCENDING)], unique=True) # Uniqueness

    # Community Posts
    logger.info("Indexing: Community Posts")
    db.community_posts.create_index([("community_id", ASCENDING)])
    db.community_posts.create_index([("created_at", DESCENDING)]) # Feed sorting
    db.community_posts.create_index([("user_id", ASCENDING)]) 

    # --- 6. RFQ System (Requests & Offers) ---
    logger.info("Indexing: RFQ System")
    # Requests
    db.requests.create_index([("id", ASCENDING)], unique=True)
    db.requests.create_index([("status", ASCENDING)])
    db.requests.create_index([("type", ASCENDING)])
    db.requests.create_index([("platform", ASCENDING)])
    db.requests.create_index([("buyer_id", ASCENDING)])
    db.requests.create_index([("created_at", DESCENDING)])
    
    # Offers
    db.offers.create_index([("id", ASCENDING)], unique=True)
    db.offers.create_index([("request_id", ASCENDING)])
    db.offers.create_index([("seller_id", ASCENDING)])
    db.offers.create_index([("status", ASCENDING)])
    db.offers.create_index([("created_at", DESCENDING)])

    # --- 7. Messaging & Notifications ---
    logger.info("Indexing: Messaging & Notifications")
    db.notifications.create_index([("recipient_id", ASCENDING)])
    db.notifications.create_index([("is_read", ASCENDING)])
    db.notifications.create_index([("created_at", DESCENDING)])

    db.messages.create_index([("conversation_id", ASCENDING)])
    db.messages.create_index([("recipient_id", ASCENDING)])
    db.messages.create_index([("sender_id", ASCENDING)])
    db.messages.create_index([("created_at", ASCENDING)]) # Chat history order

    # --- 8. Tracking & Logs ---
    logger.info("Indexing: Tracking & Logs")
    db.tracking_logs.create_index([("tracking_id", ASCENDING)], unique=True)
    db.tracking_logs.create_index([("order_id", ASCENDING)])
    
    db.audit_logs.create_index([("user_id", ASCENDING)])
    db.audit_logs.create_index([("action", ASCENDING)])
    db.audit_logs.create_index([("timestamp", DESCENDING)])
    
    db.settlement_logs.create_index([("request_id", ASCENDING)])
    db.settlement_logs.create_index([("payout_reference", ASCENDING)])

    logger.info("[OK] All indexes created successfully!")

if __name__ == "__main__":
    try:
        create_indexes()
    except Exception as e:
        logger.error(f"[Error] Error creating indexes: {e}")
