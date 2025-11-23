import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Attempting to import paystack...")
    import paystack
    print("Successfully imported paystack.py")
    print(f"PaystackSubaccount: {paystack.PaystackSubaccount}")
    print(f"PAYSTACK_API_URL: {paystack.PAYSTACK_API_URL}")
    
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
