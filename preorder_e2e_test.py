#!/usr/bin/env python3
"""
End-to-End Pre-order System Testing for Pyramyd Agritech Platform
Comprehensive testing of the complete pre-order lifecycle as requested
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class PreOrderE2ETester:
    def __init__(self, base_url: str = "https://f85d82b5-c3d9-4b5c-ac39-13c8f9f753c8.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_preorder_id = None

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    expected_status: int = 200, use_auth: bool = False) -> tuple[bool, Dict]:
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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
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

    def test_login_existing_user(self):
        """Test login with existing testagent@pyramyd.com user"""
        print("🔐 Testing Login with Existing Test Agent User...")
        
        login_data = {
            "email_or_phone": "testagent@pyramyd.com",
            "password": "password123"
        }

        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            user_role = response['user'].get('role', 'unknown')
            self.log_test("Login with Test Agent User", True, f"Logged in as {user_role}")
            return True, response['user']
        else:
            self.log_test("Login with Test Agent User", False, f"Login failed: {response}")
            return False, None

    def test_create_preorder(self):
        """Test creating a new pre-order"""
        print("📦 Testing Pre-order Creation...")
        
        # Create a unique pre-order with current timestamp
        timestamp = datetime.now().strftime("%H%M%S")
        delivery_date = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
        
        preorder_data = {
            "product_name": f"Premium Organic Tomatoes - Test {timestamp}",
            "product_category": "vegetables",
            "description": "Fresh organic tomatoes from our certified farm - End-to-End Test",
            "total_stock": 500,
            "unit": "kg",
            "price_per_unit": 850.0,
            "partial_payment_percentage": 0.4,  # 40%
            "location": "Kano, Nigeria",
            "delivery_date": delivery_date,
            "business_name": "Green Valley Test Farms",
            "farm_name": "Green Valley Test Farm",
            "images": ["https://example.com/tomato-test.jpg"]
        }

        success, response = self.make_request('POST', '/api/preorders/create', preorder_data, 200, use_auth=True)
        
        if success and 'preorder_id' in response:
            self.created_preorder_id = response['preorder_id']
            self.log_test("Pre-order Creation", True, f"Created pre-order ID: {self.created_preorder_id}")
            return True, self.created_preorder_id
        else:
            self.log_test("Pre-order Creation", False, f"Creation failed: {response}")
            return False, None

    def test_publish_preorder(self):
        """Test publishing the created pre-order"""
        print("📢 Testing Pre-order Publishing...")
        
        if not self.created_preorder_id:
            self.log_test("Pre-order Publishing", False, "No pre-order ID available")
            return False

        success, response = self.make_request('POST', f'/api/preorders/{self.created_preorder_id}/publish', {}, 200, use_auth=True)
        
        if success and response.get('message'):
            self.log_test("Pre-order Publishing", True, "Pre-order published successfully")
            return True
        else:
            self.log_test("Pre-order Publishing", False, f"Publishing failed: {response}")
            return False

    def test_advanced_filtering_api(self):
        """Test advanced product filtering API with various parameters"""
        print("🔍 Testing Advanced Product Filtering API...")
        
        test_cases = [
            {
                "name": "Basic Products + Pre-orders",
                "params": "",
                "expected_keys": ["products", "preorders", "total_count", "page", "limit"]
            },
            {
                "name": "Category Filtering (vegetables)",
                "params": "?category=vegetables",
                "expected_keys": ["products", "preorders"]
            },
            {
                "name": "Location Filtering (Kano)",
                "params": "?location=Kano",
                "expected_keys": ["products", "preorders"]
            },
            {
                "name": "Price Range Filtering",
                "params": "?min_price=500&max_price=1000",
                "expected_keys": ["products", "preorders"]
            },
            {
                "name": "Search Term (tomato)",
                "params": "?search_term=tomato",
                "expected_keys": ["products", "preorders"]
            },
            {
                "name": "Only Pre-orders",
                "params": "?only_preorders=true",
                "expected_keys": ["products", "preorders"]
            },
            {
                "name": "Pagination",
                "params": "?page=1&limit=5",
                "expected_keys": ["products", "preorders", "page", "limit", "total_pages"]
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            success, response = self.make_request('GET', f'/api/products{test_case["params"]}')
            
            if success and isinstance(response, dict):
                # Check if expected keys are present
                has_required_keys = all(key in response for key in test_case["expected_keys"])
                if has_required_keys:
                    self.log_test(f"Advanced Filtering - {test_case['name']}", True)
                else:
                    self.log_test(f"Advanced Filtering - {test_case['name']}", False, f"Missing keys: {test_case['expected_keys']}")
                    all_passed = False
            else:
                self.log_test(f"Advanced Filtering - {test_case['name']}", False, f"Invalid response: {response}")
                all_passed = False
        
        return all_passed

    def test_products_api_returns_both(self):
        """Verify products API returns both regular products and pre-orders"""
        print("🛍️ Testing Products API Returns Both Regular Products and Pre-orders...")
        
        success, response = self.make_request('GET', '/api/products')
        
        if success and isinstance(response, dict):
            has_products = 'products' in response and isinstance(response['products'], list)
            has_preorders = 'preorders' in response and isinstance(response['preorders'], list)
            has_metadata = all(key in response for key in ['total_count', 'page', 'limit'])
            
            if has_products and has_preorders and has_metadata:
                products_count = len(response['products'])
                preorders_count = len(response['preorders'])
                total_count = response['total_count']
                
                self.log_test("Products API Returns Both Types", True, 
                            f"Found {products_count} products, {preorders_count} pre-orders, total: {total_count}")
                return True
            else:
                self.log_test("Products API Returns Both Types", False, 
                            f"Missing required structure: products={has_products}, preorders={has_preorders}, metadata={has_metadata}")
                return False
        else:
            self.log_test("Products API Returns Both Types", False, f"Invalid response: {response}")
            return False

    def test_preorder_details(self):
        """Test getting specific pre-order details"""
        print("📄 Testing Pre-order Details API...")
        
        if not self.created_preorder_id:
            self.log_test("Pre-order Details", False, "No pre-order ID available")
            return False, None

        success, response = self.make_request('GET', f'/api/preorders/{self.created_preorder_id}')
        
        if success and response.get('id') == self.created_preorder_id:
            required_fields = ['id', 'seller_username', 'product_name', 'price_per_unit', 
                             'total_stock', 'available_stock', 'status', 'delivery_date']
            
            if all(field in response for field in required_fields):
                self.log_test("Pre-order Details", True, f"Status: {response.get('status')}, Stock: {response.get('available_stock')}")
                return True, response
            else:
                self.log_test("Pre-order Details", False, f"Missing required fields: {required_fields}")
                return False, response
        else:
            self.log_test("Pre-order Details", False, f"Details retrieval failed: {response}")
            return False, None

    def test_place_order_on_preorder(self):
        """Test placing an order on the pre-order"""
        print("🛒 Testing Place Order on Pre-order...")
        
        if not self.created_preorder_id:
            self.log_test("Place Order on Pre-order", False, "No pre-order ID available")
            return False

        # Get pre-order details first to check available stock
        details_success, preorder_details = self.test_preorder_details()
        if not details_success:
            self.log_test("Place Order on Pre-order", False, "Could not get pre-order details")
            return False

        available_stock = preorder_details.get('available_stock', 0)
        order_quantity = min(25, available_stock)  # Order 25 kg or available stock, whichever is less
        
        if order_quantity <= 0:
            self.log_test("Place Order on Pre-order", False, f"No stock available: {available_stock}")
            return False

        order_data = {
            "quantity": order_quantity
        }

        success, response = self.make_request('POST', f'/api/preorders/{self.created_preorder_id}/order', order_data, 200, use_auth=True)
        
        if success and 'order_id' in response:
            order_id = response['order_id']
            total_amount = response.get('total_amount', 0)
            partial_amount = response.get('partial_amount', 0)
            remaining_amount = response.get('remaining_amount', 0)
            
            self.log_test("Place Order on Pre-order", True, 
                        f"Order ID: {order_id}, Quantity: {order_quantity}, Total: ₦{total_amount}, Partial: ₦{partial_amount}")
            return True, response
        else:
            self.log_test("Place Order on Pre-order", False, f"Order placement failed: {response}")
            return False

    def test_stock_management(self):
        """Test stock management after placing order"""
        print("📊 Testing Stock Management After Order...")
        
        if not self.created_preorder_id:
            self.log_test("Stock Management", False, "No pre-order ID available")
            return False

        # Get pre-order details to check updated stock
        success, response = self.make_request('GET', f'/api/preorders/{self.created_preorder_id}')
        
        if success and response.get('id') == self.created_preorder_id:
            available_stock = response.get('available_stock', 0)
            total_stock = response.get('total_stock', 0)
            orders_count = response.get('orders_count', 0)
            total_ordered_quantity = response.get('total_ordered_quantity', 0)
            
            # Check if stock was properly reduced
            stock_reduced = available_stock < total_stock
            has_orders = orders_count > 0
            has_ordered_quantity = total_ordered_quantity > 0
            
            if stock_reduced and has_orders and has_ordered_quantity:
                self.log_test("Stock Management", True, 
                            f"Stock: {available_stock}/{total_stock}, Orders: {orders_count}, Ordered: {total_ordered_quantity}")
                return True
            else:
                self.log_test("Stock Management", False, 
                            f"Stock not properly managed: available={available_stock}, total={total_stock}, orders={orders_count}")
                return False
        else:
            self.log_test("Stock Management", False, f"Could not retrieve pre-order details: {response}")
            return False

    def test_user_preorders_api(self):
        """Test user's created pre-orders API"""
        print("👤 Testing User Pre-orders API...")
        
        success, response = self.make_request('GET', '/api/my-preorders', use_auth=True)
        
        if success and isinstance(response, list):
            # Look for our created pre-order
            found_our_preorder = False
            if self.created_preorder_id:
                found_our_preorder = any(preorder.get('id') == self.created_preorder_id for preorder in response)
            
            preorders_count = len(response)
            self.log_test("User Pre-orders API", True, 
                        f"Found {preorders_count} pre-orders, includes our test: {found_our_preorder}")
            return True
        else:
            self.log_test("User Pre-orders API", False, f"Invalid response: {response}")
            return False

    def test_user_preorder_orders_api(self):
        """Test user's pre-order purchases API"""
        print("🛍️ Testing User Pre-order Orders API...")
        
        success, response = self.make_request('GET', '/api/my-preorder-orders', use_auth=True)
        
        if success and isinstance(response, list):
            orders_count = len(response)
            
            # Check if we have any orders with proper structure
            if orders_count > 0:
                order = response[0]
                required_fields = ['id', 'preorder_id', 'buyer_username', 'quantity', 'total_amount', 'status']
                has_required_fields = all(field in order for field in required_fields)
                
                if has_required_fields:
                    self.log_test("User Pre-order Orders API", True, f"Found {orders_count} orders with proper structure")
                else:
                    self.log_test("User Pre-order Orders API", False, f"Orders missing required fields: {required_fields}")
            else:
                self.log_test("User Pre-order Orders API", True, f"Found {orders_count} orders (expected for some users)")
            
            return True
        else:
            self.log_test("User Pre-order Orders API", False, f"Invalid response: {response}")
            return False

    def test_complete_preorder_flow(self):
        """Test the complete pre-order flow from creation to ordering"""
        print("\n🔄 Testing Complete Pre-order System End-to-End Flow...")
        print("=" * 80)
        
        # Step 1: Login with existing test agent user
        login_success, user_info = self.test_login_existing_user()
        if not login_success:
            print("❌ Cannot proceed without successful login")
            return False
        
        print(f"✅ Logged in as: {user_info.get('username')} ({user_info.get('role')})")
        
        # Step 2: Create a test pre-order
        create_success, preorder_id = self.test_create_preorder()
        if not create_success:
            print("❌ Cannot proceed without successful pre-order creation")
            return False
        
        # Step 3: Publish the pre-order
        publish_success = self.test_publish_preorder()
        if not publish_success:
            print("❌ Cannot proceed without successful pre-order publishing")
            return False
        
        # Step 4: Test advanced filtering API
        filtering_success = self.test_advanced_filtering_api()
        
        # Step 5: Verify products API returns both types
        products_api_success = self.test_products_api_returns_both()
        
        # Step 6: Test pre-order details
        details_success, preorder_details = self.test_preorder_details()
        
        # Step 7: Place an order on the pre-order
        order_success = self.test_place_order_on_preorder()
        
        # Step 8: Test stock management
        stock_success = self.test_stock_management()
        
        # Step 9: Test user pre-orders API
        user_preorders_success = self.test_user_preorders_api()
        
        # Step 10: Test user pre-order orders API
        user_orders_success = self.test_user_preorder_orders_api()
        
        # Overall success evaluation
        critical_steps = [login_success, create_success, publish_success, order_success, stock_success]
        additional_steps = [filtering_success, products_api_success, details_success, user_preorders_success, user_orders_success]
        
        critical_passed = all(critical_steps)
        additional_passed = sum(additional_steps)
        
        overall_success = critical_passed and additional_passed >= 4  # At least 4 out of 5 additional steps
        
        if overall_success:
            self.log_test("Complete Pre-order System E2E Flow", True, 
                        f"All critical steps passed, {additional_passed}/5 additional steps passed")
        else:
            self.log_test("Complete Pre-order System E2E Flow", False, 
                        f"Critical steps: {sum(critical_steps)}/5, Additional: {additional_passed}/5")
        
        return overall_success

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 END-TO-END PRE-ORDER SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_run - self.tests_passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['name']}: {result['details']}")
        
        print("\n✅ Passed Tests:")
        for result in self.test_results:
            if result['success']:
                print(f"   - {result['name']}")
                if result['details']:
                    print(f"     Details: {result['details']}")
        
        print("\n🎯 Key Findings:")
        if self.tests_passed >= self.tests_run * 0.9:
            print("   ✅ Pre-order system is fully functional")
        elif self.tests_passed >= self.tests_run * 0.8:
            print("   ✅ Pre-order system is mostly functional with minor issues")
        else:
            print("   ⚠️  Pre-order system has significant issues")
        
        if self.created_preorder_id:
            print(f"\n📦 Test Pre-order Created: {self.created_preorder_id}")
            print("   This pre-order can be used for further testing or verification")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    print("🚀 Starting End-to-End Pre-order System Testing...")
    print("📡 Testing against: https://f85d82b5-c3d9-4b5c-ac39-13c8f9f753c8.preview.emergentagent.com")
    print("👤 Using existing test agent user: testagent@pyramyd.com")
    print("=" * 80)
    
    tester = PreOrderE2ETester()
    
    try:
        success = tester.test_complete_preorder_flow()
        tester.print_summary()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())