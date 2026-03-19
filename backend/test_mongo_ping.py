"""
Quick MongoDB Atlas connection test.
Run: python test_mongo_ping.py
"""
import os
import sys
from pathlib import Path

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
    print("✓ Loaded .env file")
except ImportError:
    print("⚠ python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

# Build connection URI from env vars (same logic as database.py)
import urllib.parse

username = os.environ.get("MONGO_USERNAME", "")
password = os.environ.get("MONGO_PASSWORD", "")
cluster = os.environ.get("MONGO_CLUSTER", "")
db_name = os.environ.get("MONGO_DB_NAME", "pyramyd")
auth_source = os.environ.get("MONGO_AUTH_SOURCE", "admin")

print(f"\n--- Connection Details ---")
print(f"  Username:    {username}")
print(f"  Cluster:     {cluster}")
print(f"  DB Name:     {db_name}")
print(f"  Auth Source: {auth_source}")
print(f"  Password:    {'*' * len(password) if password else '⚠ MISSING!'}")

if not all([username, password, cluster]):
    print("\n✗ Missing required env vars (MONGO_USERNAME, MONGO_PASSWORD, MONGO_CLUSTER)")
    print("  Fill them in backend/.env first.")
    sys.exit(1)

encoded_password = urllib.parse.quote_plus(password)

if "mongodb.net" in cluster:
    uri = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?authSource={auth_source}&retryWrites=true&w=majority&appName=Pyramyd"
else:
    uri = f"mongodb://{username}:{encoded_password}@{cluster}/?authSource={auth_source}"

print(f"\n--- Connecting... ---")

try:
    import pymongo
    import certifi
    print(f"  pymongo version: {pymongo.version}")
except ImportError as e:
    print(f"✗ Missing package: {e}")
    print("  Run: pip install pymongo certifi")
    sys.exit(1)

try:
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=10000, tlsCAFile=certifi.where())
    
    # Ping the server
    result = client.admin.command('ping')
    print(f"\n✅ PING SUCCESS: {result}")
    
    # List databases
    dbs = client.list_database_names()
    print(f"\n--- Available Databases ---")
    for d in dbs:
        print(f"  • {d}")
    
    # Check target database
    db = client[db_name]
    collections = db.list_collection_names()
    print(f"\n--- Collections in '{db_name}' ---")
    if collections:
        for c in collections:
            count = db[c].estimated_document_count()
            print(f"  • {c} ({count} docs)")
    else:
        print(f"  (empty — no collections yet)")
    
    print(f"\n✅ MongoDB Atlas connection is HEALTHY. You're good to go live!")
    
    client.close()

except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f"\n✗ CONNECTION TIMEOUT: Could not reach the cluster.")
    print(f"  Check: IP whitelist in Atlas (allow 0.0.0.0/0 for dev)")
    print(f"  Error: {e}")
except pymongo.errors.OperationFailure as e:
    print(f"\n✗ AUTH FAILED: Bad username/password.")
    print(f"  Check MONGO_USERNAME and MONGO_PASSWORD in .env")
    print(f"  Error: {e}")
except Exception as e:
    print(f"\n✗ UNEXPECTED ERROR: {type(e).__name__}: {e}")
