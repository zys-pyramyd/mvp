import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Attempting to import server...")
    import server
    print("Successfully imported server.py")
    
    print("Checking Paystack imports...")
    print(f"PaystackSubaccount: {server.PaystackSubaccount}")
    print(f"PAYSTACK_API_URL: {server.PAYSTACK_API_URL}")
    print("Imports verified.")
    
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
