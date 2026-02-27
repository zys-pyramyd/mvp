import requests
import time
import sys

BASE_URL = "http://localhost:8001"  # Docker maps 8001:8001 in dev usually, or we can try 8000
# Update: Server code says 8001 by default via env, but uvicorn command often uses 8000/8001. 
# Let's try to detect or use 8000 if 8001 fails.
# Dockerfile exposes 8001.

def test_rate_limit():
    print("Testing Rate Limiting on /api/auth/login...")
    print(f"Target: {BASE_URL}")
    
    # We don't need valid credentials, just hitting the endpoint is enough to trigger rate limit
    # because rate limit is by IP usually (or key_func).
    # However, invalid credentials might return 401. Rate limit should kick in before that? 
    # Actually slowapi runs before the route handler.
    
    payload = {"email_or_phone": "test@example.com", "password": "password"}
    
    success_count = 0
    blocked = False
    
    for i in range(1, 10):
        try:
            res = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
            print(f"Request {i}: Status {res.status_code}")
            
            if res.status_code == 429:
                print("Rate Limit Triggered! (429 Too Many Requests)")
                blocked = True
                break
            elif res.status_code in [200, 401]:
                success_count += 1
            else:
                print(f"Unexpected status: {res.status_code}")
                print(f"Response: {res.text}")
                
        except requests.exceptions.ConnectionError:
            print("Connection Error: Is the server running?")
            return
            
        time.sleep(0.1)
        
    if blocked:
        print("\nPASSED: Rate limiting is active.")
    else:
        print("\nFAILED: Rate limiting did not trigger within 10 requests (Limit should be 5/minute).")

if __name__ == "__main__":
    test_rate_limit()
