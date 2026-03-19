
from pymongo import MongoClient
import os

class MongoDB:
    client: MongoClient = None
    db = None

db = MongoDB()

def get_database():
    return db.db

get_db = get_database

def connect_to_mongo():
    from app.core.config import settings
    db.client = MongoClient(settings.MONGO_URL)
    try:
        # Explicitly select the database
        db.db = db.client.get_database("pyramyd")
        # Ping the server to ensure connectivity
        db.client.admin.command('ping')
        print("Connected to MongoDB and ping successful")
    except Exception as e:
        print(f"Could not connect to MongoDB or ping failed: {e}")
        raise e

def close_mongo_connection():
    if db.client:
        db.client.close()
        print("MongoDB connection closed")
