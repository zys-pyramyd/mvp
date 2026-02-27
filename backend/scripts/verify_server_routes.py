import sys
import os
from fastapi.routing import APIRoute

# Add backend directory to path so we can import server
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from server import app
    print("[OK] Server module imported successfully.")
except Exception as e:
    print(f"[Error] Failed to import server: {e}")
    sys.exit(1)

def list_routes():
    print("\n--- Verifying Routes ---")
    
    expected_tags = ['kyc', 'rfq', 'communities']
    found_tags = {tag: False for tag in expected_tags}
    
    routes_found = []
    
    for route in app.routes:
        if isinstance(route, APIRoute):
            tags = route.tags or []
            path = route.path
            name = route.name
            
            # Check for expected tags
            for tag in expected_tags:
                if tag in tags:
                    found_tags[tag] = True
            
            if any(t in tags for t in expected_tags):
                routes_found.append(f"[{','.join(tags)}] {path}")

    if routes_found:
        print(f"Found {len(routes_found)} modular routes:")
        for r in routes_found[:5]: # Show first 5
            print(f"  {r}")
        if len(routes_found) > 5:
            print(f"  ... and {len(routes_found)-5} more.")
    else:
        print("[WARN] No modular routes found!")

    print("\n--- Summary ---")
    all_good = True
    for tag, found in found_tags.items():
        status = "[OK] Found" if found else "[FAIL] MISSING"
        if not found: all_good = False
        print(f"Tag '{tag}': {status}")
        
    if all_good:
        print("\nSUCCESS: All expected modular routes are registered.")
    else:
        print("\nFAILURE: Some routes are missing.")

if __name__ == "__main__":
    list_routes()
