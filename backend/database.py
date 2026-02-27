import os
import pymongo
from pymongo import MongoClient
import sys
import certifi

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', os.environ.get('MONGO_URI', 'mongodb://localhost:27017/'))

# Global client variable (Lazy Loading)
_client = None

def get_db():
    global _client
    if _client is None:
        if not MONGO_URL:
            print("CRITICAL SECURITY ERROR: Missing MONGO_URL environment variable")
            return None
            
        try:
            # Only add tlsCAFile for remote connections (Render/Atlas)
            kwargs = {}
            if "localhost" not in MONGO_URL and "127.0.0.1" not in MONGO_URL:
                kwargs['tlsCAFile'] = certifi.where()

            _client = MongoClient(
                MONGO_URL, 
                serverSelectionTimeoutMS=10000, 
                **kwargs
            )
            print("Client initialized (Lazy)")
        except Exception as e:
            print(f"X Error initializing MongoDB client: {e}")
            return None
            
    db_name = os.environ.get('DB_NAME', 'pyramyd')
    return _client[db_name]

# Proxy object to maintain backward compatibility with 'from database import db'
# This allows db['collection'] to work by creating the client on demand if accessed.
# However, to be safe and simple, we will expose a db object that is initialized via get_db() if possible,
# or we update server.py. Given the constraints, let's make db call get_db() if accessed.
# But 'db' is a module level variable. 
# We'll just define db as the result of get_db() effectively, but wait, if get_db() connects, we defeat the purpose?
# No, MongoClient() is lazy. It doesn't connect until used.
# So we can just do:
# db = get_db()
# But get_db() logic above creates the client.
# So:

try:
    if MONGO_URL:
        # We initialize the client definition but do not force a command
        # This is safe. The actual connection (network) happens later.
        db = get_db()
    else:
        db = None
except Exception:
    db = None

def get_collection(name):
    """Safely get a collection from the database"""
    database = get_db()
    if database is not None:
        return database[name]
    return None

def get_client():
    global _client
    if _client is None:
        get_db() # This initializes _client
    return _client
