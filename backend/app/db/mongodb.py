
from pymongo import MongoClient
import os

class MongoDB:
    client: MongoClient = None
    db = None

db = MongoDB()

def get_database():
    return db.db

def connect_to_mongo():
    from app.core.config import settings
    db.client = MongoClient(settings.MONGO_URL)
    try:
        # Default to 'pyramyd' if not in connection string, or rely on client.get_default_database
        # server.py used "client['pyramyd']" mostly implicitly via connection or similar.
        # We will be explicit.
        db.db = db.client.get_database("pyramyd")
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")
        raise e

def close_mongo_connection():
    if db.client:
        db.client.close()
        print("MongoDB connection closed")
