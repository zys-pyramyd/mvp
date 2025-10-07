#!/usr/bin/env python3
"""
Pre-order Structure Investigation Test
Specifically checking why pre-orders are not showing in frontend pre-order section
"""

import requests
import sys
import json
from datetime import datetime

class PreOrderStructureTester:
    def __init__(self, base_url: str = "https://cropchain-hub-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None

    def make_request(self, method: str, endpoint: str, data=None, expected_status: int = 200, use_auth: bool = False):
        """Make HTTP request and validate response"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if use_auth and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if not success:
                print(f"   Status: {response.status_code} (expected {expected_status})")
                print(f"   Response: {response_data}")

            return success, response_data

        except requests.exceptions.RequestException as e:
            print(f"   Request failed: {str(e)}")
            return False, {"error": str(e)}

    def login_as_agent(self):
        """Login as existing agent user"""
        login_data = {
            "email_or_phone": "testagent@pyramyd.com",
            "password": "password123"
        }

        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"✅ Logged in as agent: {response['user']['username']}")
            return True
        else:
            print(f"❌ Login failed: {response}")
            return False

    def investigate_products_api_structure(self):
        """Investigate GET /api/products response structure"""
        print("\n🔍 INVESTIGATING GET /api/products STRUCTURE...")
        
        success, response = self.make_request('GET', '/api/products')
        
        if success:
            print(f"✅ GET /api/products successful")
            print(f"📊 Response structure:")
            print(f"   - Type: {type(response)}")
            
            if isinstance(response, dict):
                print(f"   - Keys: {list(response.keys())}")
                
                # Check products
                if 'products' in response:
                    products = response['products']
                    print(f"   - Products count: {len(products)}")
                    if len(products) > 0:
                        print(f"   - First product keys: {list(products[0].keys())}")
                        print(f"   - First product type field: {products[0].get('type', 'NOT FOUND')}")
                
                # Check preorders
                if 'preorders' in response:
                    preorders = response['preorders']
                    print(f"   - Pre-orders count: {len(preorders)}")
                    if len(preorders) > 0:
                        print(f"   - First pre-order keys: {list(preorders[0].keys())}")
                        print(f"   - First pre-order type field: {preorders[0].get('type', 'NOT FOUND')}")
                        
                        # Show full structure of first pre-order
                        print(f"\n📋 FIRST PRE-ORDER FULL STRUCTURE:")
                        print(json.dumps(preorders[0], indent=2, default=str))
                
                # Check total counts
                if 'total_count' in response:
                    print(f"   - Total count: {response['total_count']}")
                    
            return True, response
        else:
            print(f"❌ GET /api/products failed: {response}")
            return False, response

    def investigate_preorders_api_structure(self):
        """Investigate GET /api/preorders response structure"""
        print("\n🔍 INVESTIGATING GET /api/preorders STRUCTURE...")
        
        success, response = self.make_request('GET', '/api/preorders')
        
        if success:
            print(f"✅ GET /api/preorders successful")
            print(f"📊 Response structure:")
            print(f"   - Type: {type(response)}")
            
            if isinstance(response, dict) and 'preorders' in response:
                preorders = response['preorders']
                print(f"   - Pre-orders count: {len(preorders)}")
                
                if len(preorders) > 0:
                    print(f"   - First pre-order keys: {list(preorders[0].keys())}")
                    print(f"   - First pre-order type field: {preorders[0].get('type', 'NOT FOUND')}")
                    
                    # Show full structure of first pre-order
                    print(f"\n📋 FIRST PRE-ORDER FROM /api/preorders:")
                    print(json.dumps(preorders[0], indent=2, default=str))
                    
                    # Check if any pre-orders have type field
                    preorders_with_type = [p for p in preorders if 'type' in p]
                    print(f"\n🏷️ PRE-ORDERS WITH 'type' FIELD: {len(preorders_with_type)}")
                    
                    if len(preorders_with_type) > 0:
                        for i, preorder in enumerate(preorders_with_type[:3]):  # Show first 3
                            print(f"   Pre-order {i+1} type: {preorder.get('type')}")
                    
                    return True, preorders[0]['id'] if len(preorders) > 0 else None
            else:
                print(f"   - No preorders found or invalid structure")
                return True, None
        else:
            print(f"❌ GET /api/preorders failed: {response}")
            return False, None

    def investigate_specific_preorder(self, preorder_id):
        """Get specific pre-order details"""
        if not preorder_id:
            print("\n⚠️ No pre-order ID available for specific investigation")
            return False
            
        print(f"\n🔍 INVESTIGATING SPECIFIC PRE-ORDER: {preorder_id}")
        
        success, response = self.make_request('GET', f'/api/preorders/{preorder_id}')
        
        if success:
            print(f"✅ GET /api/preorders/{preorder_id} successful")
            print(f"📊 Pre-order structure:")
            print(f"   - Keys: {list(response.keys())}")
            print(f"   - Type field: {response.get('type', 'NOT FOUND')}")
            
            print(f"\n📋 FULL PRE-ORDER STRUCTURE:")
            print(json.dumps(response, indent=2, default=str))
            
            return True
        else:
            print(f"❌ GET /api/preorders/{preorder_id} failed: {response}")
            return False

    def check_frontend_expectation(self):
        """Check what the frontend expects vs what backend provides"""
        print("\n🎯 FRONTEND EXPECTATION ANALYSIS:")
        print("   Frontend filters for: product.type === 'preorder'")
        print("   Let's check if backend provides this...")
        
        # Check /api/products response
        success, products_response = self.make_request('GET', '/api/products')
        
        if success and isinstance(products_response, dict):
            # Check if products have type field
            products = products_response.get('products', [])
            preorders = products_response.get('preorders', [])
            
            print(f"\n📊 PRODUCTS ANALYSIS:")
            print(f"   - Regular products count: {len(products)}")
            products_with_type = [p for p in products if p.get('type') == 'preorder']
            print(f"   - Products with type='preorder': {len(products_with_type)}")
            
            print(f"\n📊 PRE-ORDERS ANALYSIS:")
            print(f"   - Pre-orders count: {len(preorders)}")
            preorders_with_type = [p for p in preorders if p.get('type') == 'preorder']
            print(f"   - Pre-orders with type='preorder': {len(preorders_with_type)}")
            
            # Check if pre-orders are in the products array with type='preorder'
            all_items = products + preorders
            preorder_type_items = [item for item in all_items if item.get('type') == 'preorder']
            
            print(f"\n🎯 FRONTEND COMPATIBILITY:")
            print(f"   - Total items that would match frontend filter (type='preorder'): {len(preorder_type_items)}")
            
            if len(preorder_type_items) == 0:
                print("   ❌ ISSUE FOUND: No items have type='preorder' field!")
                print("   💡 SOLUTION: Backend should add type='preorder' to pre-order items")
            else:
                print("   ✅ Items with type='preorder' found")
                
            return len(preorder_type_items) > 0
        
        return False

    def create_test_preorder(self):
        """Create a test pre-order to investigate structure"""
        print("\n🔧 CREATING TEST PRE-ORDER...")
        
        if not self.token:
            print("❌ Not authenticated, cannot create pre-order")
            return False, None
            
        preorder_data = {
            "product_name": "Test Investigation Tomatoes",
            "product_category": "vegetables",
            "description": "Test pre-order for structure investigation",
            "total_stock": 100,
            "unit": "kg",
            "price_per_unit": 500.0,
            "partial_payment_percentage": 0.3,
            "location": "Test Location",
            "delivery_date": "2025-03-01T10:00:00Z",
            "business_name": "Test Business",
            "farm_name": "Test Farm",
            "images": []
        }

        success, response = self.make_request('POST', '/api/preorders/create', preorder_data, 200, use_auth=True)
        
        if success and 'preorder_id' in response:
            preorder_id = response['preorder_id']
            print(f"✅ Test pre-order created: {preorder_id}")
            
            # Publish it
            publish_success, publish_response = self.make_request('POST', f'/api/preorders/{preorder_id}/publish', {}, 200, use_auth=True)
            
            if publish_success:
                print(f"✅ Test pre-order published")
                return True, preorder_id
            else:
                print(f"❌ Failed to publish test pre-order: {publish_response}")
                return False, preorder_id
        else:
            print(f"❌ Failed to create test pre-order: {response}")
            return False, None

    def run_investigation(self):
        """Run complete investigation"""
        print("🔍 PRE-ORDER STRUCTURE INVESTIGATION")
        print("=" * 50)
        
        # Step 1: Login
        if not self.login_as_agent():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Check current /api/products structure
        products_success, products_response = self.investigate_products_api_structure()
        
        # Step 3: Check /api/preorders structure
        preorders_success, first_preorder_id = self.investigate_preorders_api_structure()
        
        # Step 4: Check specific pre-order if available
        if first_preorder_id:
            self.investigate_specific_preorder(first_preorder_id)
        
        # Step 5: Create test pre-order and check its structure
        test_success, test_preorder_id = self.create_test_preorder()
        if test_success and test_preorder_id:
            self.investigate_specific_preorder(test_preorder_id)
        
        # Step 6: Analyze frontend compatibility
        frontend_compatible = self.check_frontend_expectation()
        
        # Step 7: Final analysis
        print("\n" + "=" * 50)
        print("🎯 INVESTIGATION SUMMARY:")
        print("=" * 50)
        
        if not frontend_compatible:
            print("❌ ISSUE IDENTIFIED:")
            print("   - Frontend expects: product.type === 'preorder'")
            print("   - Backend provides: Pre-orders in separate 'preorders' array without type field")
            print("   - Solution needed: Add type='preorder' field to pre-order items")
        else:
            print("✅ Pre-orders should be visible in frontend")
        
        return frontend_compatible

if __name__ == "__main__":
    tester = PreOrderStructureTester()
    success = tester.run_investigation()
    
    if not success:
        print("\n❌ Investigation revealed issues with pre-order structure")
        sys.exit(1)
    else:
        print("\n✅ Pre-order structure investigation completed")
        sys.exit(0)