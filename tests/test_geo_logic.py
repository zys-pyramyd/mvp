import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.utils.geo import get_distance_km

def test_geo():
    print("Testing Geo Logic...")
    
    # Test 1: Fallback (Lagos -> Ibadan)
    d1 = get_distance_km("Lagos, Nigeria", "Ibadan, Oyo")
    print(f"Lagos -> Ibadan: {d1} km (Expected 130.0)")
    
    # Test 2: Default
    d2 = get_distance_km("Unknown City", "Another City")
    print(f"Unknown -> Unknown: {d2} km (Expected 50.0)")
    
    if d1 == 130.0 and d2 == 50.0:
        print("SUCCESS: Geo logic fallbacks working.")
    else:
        print("FAILURE: Geo logic mismatch.")

if __name__ == "__main__":
    test_geo()
