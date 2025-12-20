import os
import sys

# Add current directory to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from geo_helper import GeopyHelper

# Use the key from env
API_KEY = os.environ.get("GEOAPIFY_API_KEY")

def test_lagos_distance():
    print("Testing Distance Calculation for Lagos Addresses...")
    helper = GeopyHelper(api_key=API_KEY)
    
    addr1 = "5 marina road, lagos island, Lagos, Nigeria"
    addr2 = "5 shitta street, dopemu, agege, lagos, Nigeria"
    
    print(f"\n1. Geocoding: {addr1}")
    coords1 = helper.geocode_address(addr1)
    print(f"   Result: {coords1}")
    
    print(f"\n2. Geocoding: {addr2}")
    coords2 = helper.geocode_address(addr2)
    print(f"   Result: {coords2}")
    
    if coords1 and coords2:
        print("\n3. Calculating Distance...")
        dist = helper.distance_km(coords1, coords2)
        print(f"   Distance: {dist} km")
    else:
        print("\nError: Could not geocode one or both addresses.")

if __name__ == "__main__":
    test_lagos_distance()
