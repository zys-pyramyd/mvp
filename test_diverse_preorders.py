#!/usr/bin/env python3
"""
Test script specifically for creating diverse pre-order products
"""

import requests
import sys
import json
from datetime import datetime, timedelta

class DiversePreorderTester:
    def __init__(self, base_url: str = "https://7153c80b-e670-44f1-b4af-554c09ef9392.preview.emergentagent.com"):
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
        """Login with existing agent user or create one"""
        # First try existing agent
        login_data = {
            "email_or_phone": "testagent@pyramyd.com",
            "password": "password123"
        }

        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            user_role = response['user'].get('role')
            print(f"✅ Logged in successfully with role: {user_role}")
            
            # Check if user has the right role for creating pre-orders
            allowed_roles = ['farmer', 'supplier', 'processor', 'agent']
            if user_role in allowed_roles:
                print(f"✅ User role '{user_role}' is authorized to create pre-orders")
                return True
            else:
                print(f"❌ User role '{user_role}' is not authorized to create pre-orders")
                print("Trying to create a new agent user...")
                return self.create_agent_user()
        else:
            print(f"❌ Login failed: {response}")
            print("Trying to create a new agent user...")
            return self.create_agent_user()

    def create_agent_user(self):
        """Create a new agent user for testing"""
        timestamp = datetime.now().strftime("%H%M%S")
        registration_data = {
            "first_name": "Test",
            "last_name": "Agent",
            "username": f"test_agent_preorder_{timestamp}",
            "email_or_phone": f"agent_preorder_{timestamp}@pyramyd.com",
            "password": "AgentPass123!",
            "phone": "+1234567890",
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "user_path": "partner",
            "partner_type": "agent",
            "business_info": {
                "business_name": "Test Agent Business",
                "business_address": "Test Address"
            },
            "verification_info": {
                "nin": "12345678901"
            }
        }

        success, response = self.make_request('POST', '/api/auth/complete-registration', registration_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            user_role = response['user'].get('role')
            print(f"✅ Created new agent user with role: {user_role}")
            return True
        else:
            print(f"❌ Agent user creation failed: {response}")
            return False

    def create_diverse_preorder_products(self):
        """Create the 3 diverse pre-order products as requested"""
        print("\n🌾 Creating Diverse Pre-order Products...")
        
        # Calculate delivery dates
        rice_delivery = (datetime.utcnow() + timedelta(days=45)).isoformat() + "Z"
        tomato_delivery = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
        palm_oil_delivery = (datetime.utcnow() + timedelta(days=60)).isoformat() + "Z"
        
        # 1. Rice Pre-order
        rice_preorder_data = {
            "product_name": "Premium Basmati Rice - Harvest 2024",
            "product_category": "grain",
            "description": "Premium quality Basmati rice from the 2024 harvest season. Carefully selected and processed for superior taste and aroma.",
            "total_stock": 500,
            "unit": "bag",
            "price_per_unit": 850.0,
            "partial_payment_percentage": 0.4,  # 40%
            "location": "Kebbi State, Nigeria",
            "delivery_date": rice_delivery,
            "business_name": "Kebbi Rice Mills",
            "farm_name": "Golden Harvest Farm",
            "images": []
        }

        print("Creating Rice Pre-order...")
        success, response = self.make_request('POST', '/api/preorders/create', rice_preorder_data, 200, use_auth=True)
        
        if success and 'preorder_id' in response:
            rice_preorder_id = response['preorder_id']
            # Publish the rice pre-order
            publish_success, _ = self.make_request('POST', f'/api/preorders/{rice_preorder_id}/publish', {}, 200, use_auth=True)
            if publish_success:
                print("✅ Rice Pre-order created and published successfully")
                rice_success = True
            else:
                print("❌ Rice Pre-order created but failed to publish")
                rice_success = False
        else:
            print(f"❌ Rice Pre-order creation failed: {response}")
            rice_success = False

        # 2. Tomato Pre-order
        tomato_preorder_data = {
            "product_name": "Fresh Roma Tomatoes - Seasonal",
            "product_category": "vegetables",
            "description": "Fresh, juicy Roma tomatoes perfect for cooking and processing. Harvested at peak ripeness for maximum flavor and nutrition.",
            "total_stock": 200,
            "unit": "crate",
            "price_per_unit": 400.0,
            "partial_payment_percentage": 0.3,  # 30%
            "location": "Kaduna State, Nigeria",
            "delivery_date": tomato_delivery,
            "business_name": "Kaduna Fresh Produce",
            "farm_name": "Valley View Tomato Farm",
            "images": []
        }

        print("Creating Tomato Pre-order...")
        success, response = self.make_request('POST', '/api/preorders/create', tomato_preorder_data, 200, use_auth=True)
        
        if success and 'preorder_id' in response:
            tomato_preorder_id = response['preorder_id']
            # Publish the tomato pre-order
            publish_success, _ = self.make_request('POST', f'/api/preorders/{tomato_preorder_id}/publish', {}, 200, use_auth=True)
            if publish_success:
                print("✅ Tomato Pre-order created and published successfully")
                tomato_success = True
            else:
                print("❌ Tomato Pre-order created but failed to publish")
                tomato_success = False
        else:
            print(f"❌ Tomato Pre-order creation failed: {response}")
            tomato_success = False

        # 3. Palm Oil Pre-order
        palm_oil_preorder_data = {
            "product_name": "Pure Red Palm Oil - Cold Pressed",
            "product_category": "packaged_goods",
            "description": "Pure, unrefined red palm oil extracted using traditional cold-press methods. Rich in vitamins and natural antioxidants.",
            "total_stock": 100,
            "unit": "gallon",
            "price_per_unit": 1200.0,
            "partial_payment_percentage": 0.35,  # 35%
            "location": "Cross River State, Nigeria",
            "delivery_date": palm_oil_delivery,
            "business_name": "Cross River Palm Processing",
            "farm_name": "Tropical Palm Estate",
            "images": []
        }

        print("Creating Palm Oil Pre-order...")
        success, response = self.make_request('POST', '/api/preorders/create', palm_oil_preorder_data, 200, use_auth=True)
        
        if success and 'preorder_id' in response:
            palm_oil_preorder_id = response['preorder_id']
            # Publish the palm oil pre-order
            publish_success, _ = self.make_request('POST', f'/api/preorders/{palm_oil_preorder_id}/publish', {}, 200, use_auth=True)
            if publish_success:
                print("✅ Palm Oil Pre-order created and published successfully")
                palm_oil_success = True
            else:
                print("❌ Palm Oil Pre-order created but failed to publish")
                palm_oil_success = False
        else:
            print(f"❌ Palm Oil Pre-order creation failed: {response}")
            palm_oil_success = False

        overall_success = rice_success and tomato_success and palm_oil_success
        
        if overall_success:
            print("\n🎉 All 3 diverse pre-order products created and published successfully!")
        else:
            print("\n⚠️ One or more pre-order products failed to create/publish")
        
        return overall_success

    def test_preorder_retrieval(self):
        """Test that created pre-order products can be retrieved"""
        print("\n🔍 Testing Pre-order Products Retrieval...")
        
        # Test 1: Get all products including pre-orders
        success, response = self.make_request('GET', '/api/products')
        
        if success and isinstance(response, dict) and 'preorders' in response:
            preorders = response.get('preorders', [])
            
            # Look for our created pre-orders
            rice_found = any(p.get('product_name') == 'Premium Basmati Rice - Harvest 2024' for p in preorders)
            tomato_found = any(p.get('product_name') == 'Fresh Roma Tomatoes - Seasonal' for p in preorders)
            palm_oil_found = any(p.get('product_name') == 'Pure Red Palm Oil - Cold Pressed' for p in preorders)
            
            found_count = sum([rice_found, tomato_found, palm_oil_found])
            
            print(f"✅ Found {len(preorders)} total pre-orders, {found_count}/3 of our created pre-orders visible")
            
            if found_count == 3:
                print("🎉 All 3 diverse pre-order products are visible in the API!")
            elif found_count > 0:
                print(f"⚠️ Only {found_count}/3 pre-order products are visible")
            else:
                print("❌ None of our pre-order products are visible")
                
            products_success = found_count > 0
        else:
            print(f"❌ Failed to get products: {response}")
            products_success = False

        # Test 2: Try the dedicated pre-orders endpoint
        success, response = self.make_request('GET', '/api/preorders')
        
        if success and isinstance(response, dict) and 'preorders' in response:
            preorders = response.get('preorders', [])
            
            # Look for our created pre-orders
            rice_found = any(p.get('product_name') == 'Premium Basmati Rice - Harvest 2024' for p in preorders)
            tomato_found = any(p.get('product_name') == 'Fresh Roma Tomatoes - Seasonal' for p in preorders)
            palm_oil_found = any(p.get('product_name') == 'Pure Red Palm Oil - Cold Pressed' for p in preorders)
            
            found_count = sum([rice_found, tomato_found, palm_oil_found])
            
            print(f"✅ /api/preorders endpoint: Found {len(preorders)} total pre-orders, {found_count}/3 of our created pre-orders visible")
            
            if found_count == 3:
                print("🎉 All 3 diverse pre-order products are visible in the dedicated pre-orders API!")
                preorders_success = True
            elif found_count > 0:
                print(f"⚠️ Only {found_count}/3 pre-order products are visible in dedicated API")
                preorders_success = True
            else:
                print("❌ None of our pre-order products are visible in dedicated API")
                preorders_success = False
                
        else:
            print(f"❌ Failed to get pre-orders from dedicated endpoint: {response}")
            preorders_success = False

        return products_success or preorders_success

    def run_test(self):
        """Run the complete test"""
        print("🚀 Starting Diverse Pre-order Products Creation Test...")
        print("=" * 60)
        
        # Step 1: Login as agent
        if not self.login_as_agent():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Create diverse pre-order products
        creation_success = self.create_diverse_preorder_products()
        
        # Step 3: Test retrieval
        retrieval_success = self.test_preorder_retrieval()
        
        # Final result
        print("\n" + "=" * 60)
        if creation_success and retrieval_success:
            print("🎉 SUCCESS: Diverse pre-order products created and retrievable!")
            print("\nCreated Products:")
            print("1. Premium Basmati Rice - Harvest 2024 (₦850/bag, 40% partial payment)")
            print("2. Fresh Roma Tomatoes - Seasonal (₦400/crate, 30% partial payment)")
            print("3. Pure Red Palm Oil - Cold Pressed (₦1200/gallon, 35% partial payment)")
            return True
        else:
            print("❌ FAILED: One or more steps failed")
            return False

def main():
    """Main test execution"""
    tester = DiversePreorderTester()
    
    try:
        success = tester.run_test()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())