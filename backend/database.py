import os
import pymongo
from pymongo import MongoClient
import sys
import certifi

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', os.environ.get('MONGO_URI'))

# Initialize MongoDB
db = None
client = None

def get_db():
    return db

def connect_db():
    global db, client
    try:
        if not MONGO_URL:
             print("CRITICAL SECURITY ERROR: Missing MONGO_URL environment variable")
             return None
             
        # Add tlsCAFile=certifi.where() to fix SSL errors on Render/Linux
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
        db = client['pyramyd']
        print("OK Connected to MongoDB (Module)")
        return db
    except Exception as e:
        print(f"X Error connecting to MongoDB: {e}")
        return None

# Initialize on import (optional, or call explicitly in server.py)
if not db:
    connect_db()

# Collections (Lazy access or defined here)
def get_collection(name):
    if db is not None:
        return db[name]
    return None
