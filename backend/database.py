import os
import logging
import certifi
import urllib.parse
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

# Environment variables for MongoDB
MONGO_USERNAME = os.environ.get("MONGO_USERNAME", "")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "")
MONGO_CLUSTER = os.environ.get("MONGO_CLUSTER")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "pyramyd")
MONGO_AUTH_SOURCE = os.environ.get("MONGO_AUTH_SOURCE", "admin")

# Generate MONGO_URL dynamically
if MONGO_USERNAME and MONGO_PASSWORD:
    encoded_password = urllib.parse.quote_plus(MONGO_PASSWORD)
    # Use srv format if it's atlas/remote
    if MONGO_CLUSTER and "mongodb.net" in MONGO_CLUSTER:
        MONGO_URL = f"mongodb+srv://{MONGO_USERNAME}:{encoded_password}@{MONGO_CLUSTER}/?authSource={MONGO_AUTH_SOURCE}&retryWrites=true&w=majority&appName=Pyramyd"
    else:
        MONGO_URL = f"mongodb://{MONGO_USERNAME}:{encoded_password}@{MONGO_CLUSTER}/?authSource={MONGO_AUTH_SOURCE}"
else:
    # Fallback to direct URL or localhost (for local development)
    MONGO_URL = os.environ.get('MONGO_URL', os.environ.get('MONGO_URI', f'mongodb://{MONGO_CLUSTER}/'))

# Global client variable (Lazy Loading with reconnection)
_client = None
_MAX_RETRIES = 3


def _create_client():
    """Create a new MongoClient with production-ready settings."""
    if not MONGO_URL:
        logger.critical("Missing MONGO_URL environment variable")
        return None

    kwargs = {}
    if "localhost" not in MONGO_URL and "127.0.0.1" not in MONGO_URL:
        kwargs['tlsCAFile'] = certifi.where()

    client = MongoClient(
        MONGO_URL,
        serverSelectionTimeoutMS=10000,
        maxPoolSize=50,
        minPoolSize=5,
        retryWrites=True,
        retryReads=True,
        **kwargs
    )
    return client


def get_db():
    """
    Get the database connection with automatic reconnection.
    If the client is disconnected or stale, it will attempt to reconnect.
    """
    global _client

    if _client is None:
        _client = _create_client()
        if _client is None:
            return None
        logger.info("MongoDB client initialized")

    # Verify the connection is alive; reconnect if stale
    try:
        _client.admin.command('ping')
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.warning(f"MongoDB connection lost, attempting reconnect: {e}")
        _client = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                _client = _create_client()
                if _client:
                    _client.admin.command('ping')
                    logger.info(f"MongoDB reconnected on attempt {attempt}")
                    break
            except Exception as retry_err:
                logger.error(f"Reconnect attempt {attempt}/{_MAX_RETRIES} failed: {retry_err}")
                _client = None
        if _client is None:
            logger.critical("All MongoDB reconnection attempts failed")
            return None

    db_name = os.environ.get('DB_NAME', MONGO_DB_NAME)
    return _client[db_name]


# Proxy object for backward compatibility with 'from database import db'
try:
    if MONGO_URL:
        db = get_db()
    else:
        db = None
except Exception:
    db = None


def get_collection(name):
    """Safely get a collection from the database."""
    database = get_db()
    if database is not None:
        return database[name]
    return None


def get_client():
    """Get the raw MongoClient instance."""
    global _client
    if _client is None:
        get_db()
    return _client


def ping_db() -> bool:
    """Ping the MongoDB server to verify connectivity.
    Returns True if ping succeeds, False otherwise.
    """
    try:
        client = get_client()
        if client:
            client.admin.command('ping')
            return True
    except Exception as e:
        logger.warning(f"MongoDB ping failed: {e}")
    return False

def init_db_indexes(db_instance=None):
    """
    Initialize critical MongoDB indexes to ensure production performance.
    Avoids full collection scans on frequent queries.
    """
    database = db_instance if db_instance is not None else get_db()
    if database is None:
        logger.warning("Could not initialize indexes: No database connection.")
        return

    import pymongo
    
    try:
        # 1. Users Collection
        database.users.create_index("id", unique=True)
        database.users.create_index("email", unique=True)
        database.users.create_index("username", unique=True)
        database.users.create_index("role")
        
        # 2. Products Collection
        database.products.create_index("id", unique=True)
        database.products.create_index("seller_id")
        database.products.create_index("status")
        database.products.create_index("category")
        # Text index for search
        # database.products.create_index([("name", pymongo.TEXT), ("description", pymongo.TEXT)])
        
        # 3. Orders Collection
        database.orders.create_index("order_id", unique=True)
        database.orders.create_index("buyer_id")
        database.orders.create_index("seller_id")
        database.orders.create_index("status")
        database.orders.create_index("payment_reference")
        
        # 4. RFQ Requests
        if "requests" in database.list_collection_names():
            database.requests.create_index("request_id", unique=True)
            database.requests.create_index("buyer_id")
            database.requests.create_index("status")
            
        # 5. Wallet Transactions
        if "wallet_transactions" in database.list_collection_names():
            database.wallet_transactions.create_index("id")
            database.wallet_transactions.create_index("user_id")
            database.wallet_transactions.create_index("reference")
            
        # 6. Communities & Posts
        if "communities" in database.list_collection_names():
            database.communities.create_index("id", unique=True)
            database.communities.create_index("creator_id")
        if "community_posts" in database.list_collection_names():
            database.community_posts.create_index("id", unique=True)
            database.community_posts.create_index("community_id")
            database.community_posts.create_index([("created_at", pymongo.DESCENDING)])
            
        # 7. Messages
        if "messages" in database.list_collection_names():
            database.messages.create_index("conversation_id")
            database.messages.create_index("recipient_username")
            
        logger.info("Successfully initialized MongoDB indexes.")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB indexes: {e}")
