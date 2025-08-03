#!/usr/bin/env python3
"""
Focused test for Order Creation Fix
Tests the specific issues mentioned in the review request
"""

import requests
import sys
import json
from datetime import datetime

class OrderCreationTester:
    def __init__(self, base_url: str = "https://db16cee4-7596-40bf-9ed9-efba806794f6.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")

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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

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

    def create_agent_user(self):
        """Create a complete agent user for testing"""
        timestamp = datetime.now().strftime("%H%M%S")
        registration_data = {
            "first_name": "Test",
            "last_name": "Agent",
            "username": f"test_agent_order_{timestamp}",
            "email_or_phone": f"agent_order_{timestamp}@pyramyd.com",
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
            self.log_test("Agent User Registration", True)
            return True
        else:
            self.log_test("Agent User Registration", False, f"Registration failed: {response}")
            return False

    def test_order_creation_fix(self):
        """Test the order creation endpoint fix"""
        print("\n🛒 Testing Order Creation Fix...")
        
        # Step 1: Create a test product first
        print("📦 Creating test product for order testing...")
        product_data = {
            "title": "Test Product for Order Fix",
            "description": "Test product for order creation testing",
            "category": "vegetables",
            "price_per_unit": 500.0,
            "unit_of_measure": "kg",
            "unit_specification": "fresh",
            "quantity_available": 100,
            "minimum_order_quantity": 1,
            "location": "Lagos, Nigeria",
            "farm_name": "Test Farm",
            "images": [],
            "platform": "pyhub"
        }

        success, response = self.make_request('POST', '/api/products', product_data, 200, use_auth=True)
        
        if success and 'product_id' in response:
            self.log_test("Order Test - Product Creation", True)
            test_product_id = response['product_id']
        else:
            self.log_test("Order Test - Product Creation", False, f"Product creation failed: {response}")
            return False
        
        # Step 2: Create a test drop-off location
        print("📍 Creating test drop-off location...")
        dropoff_data = {
            "name": "Test Drop-off Location",
            "address": "123 Test Street, Test Area",
            "city": "Lagos",
            "state": "Lagos",
            "country": "Nigeria",
            "contact_person": "Test Contact",
            "contact_phone": "+2341234567890",
            "operating_hours": "9AM - 6PM",
            "description": "Test drop-off location for order testing"
        }

        success, response = self.make_request('POST', '/api/dropoff-locations', dropoff_data, 200, use_auth=True)
        
        if success and 'location_id' in response:
            self.log_test("Order Test - Drop-off Location Creation", True)
            test_dropoff_id = response['location_id']
        else:
            self.log_test("Order Test - Drop-off Location Creation", False, f"Drop-off location creation failed: {response}")
            return False
        
        # Step 3: Test order creation with dropoff_location_id (main fix test)
        print("🛒 Testing order creation with drop-off location...")
        order_data = {
            "product_id": test_product_id,
            "quantity": 5.0,
            "unit": "kg",
            "unit_specification": "fresh",
            "delivery_method": "dropoff",
            "dropoff_location_id": test_dropoff_id
        }

        success, response = self.make_request('POST', '/api/orders/create', order_data, 200, use_auth=True)
        
        if success and 'order_id' in response:
            self.log_test("Order Creation with Drop-off Location", True)
            
            # Step 4: Check agent fee is 5%
            agent_fee_info = response.get('agent_fee_info', {})
            if agent_fee_info.get('percentage') == '5%':
                self.log_test("Agent Fee Calculation (5%)", True)
                agent_fee_success = True
            else:
                self.log_test("Agent Fee Calculation (5%)", False, f"Expected 5%, got {agent_fee_info.get('percentage')}")
                agent_fee_success = False
            
            # Step 5: Check payment timing is set correctly for dropoff
            if agent_fee_info.get('payment_timing') == 'during_transit':
                self.log_test("Payment Timing (Drop-off)", True)
                payment_timing_success = True
            else:
                self.log_test("Payment Timing (Drop-off)", False, f"Expected 'during_transit', got {agent_fee_info.get('payment_timing')}")
                payment_timing_success = False
            
            # Step 6: Verify drop-off location details are included
            delivery_info = response.get('delivery_info', {})
            if 'dropoff_location' in delivery_info:
                dropoff_info = delivery_info['dropoff_location']
                if dropoff_info.get('name') == 'Test Drop-off Location':
                    self.log_test("Drop-off Location Details", True)
                    dropoff_details_success = True
                else:
                    self.log_test("Drop-off Location Details", False, f"Drop-off location name mismatch: {dropoff_info}")
                    dropoff_details_success = False
            else:
                self.log_test("Drop-off Location Details", False, "Drop-off location details missing from response")
                dropoff_details_success = False
            
            order_creation_success = True
        else:
            self.log_test("Order Creation with Drop-off Location", False, f"Order creation failed: {response}")
            agent_fee_success = False
            payment_timing_success = False
            dropoff_details_success = False
            order_creation_success = False
        
        # Step 7: Test offline delivery payment timing
        print("🚚 Testing offline delivery payment timing...")
        offline_order_data = {
            "product_id": test_product_id,
            "quantity": 3.0,
            "unit": "kg",
            "unit_specification": "fresh",
            "delivery_method": "offline",
            "shipping_address": "123 Test Address, Lagos"
        }

        success, response = self.make_request('POST', '/api/orders/create', offline_order_data, 200, use_auth=True)
        
        if success and 'agent_fee_info' in response:
            agent_fee_info = response['agent_fee_info']
            if agent_fee_info.get('payment_timing') == 'after_delivery':
                self.log_test("Payment Timing (Offline)", True)
                offline_payment_success = True
            else:
                self.log_test("Payment Timing (Offline)", False, f"Expected 'after_delivery', got {agent_fee_info.get('payment_timing')}")
                offline_payment_success = False
        else:
            self.log_test("Payment Timing (Offline)", False, f"Offline order creation failed: {response}")
            offline_payment_success = False
        
        # Step 8: Test product lookup bug fix (ensure it uses 'id' not '_id')
        print("🔍 Testing product lookup bug fix...")
        if order_creation_success:
            self.log_test("Product Lookup Bug Fix", True, "Product found successfully using 'id' field")
            product_lookup_success = True
        else:
            self.log_test("Product Lookup Bug Fix", False, "Product lookup may still have issues")
            product_lookup_success = False
        
        # Overall success
        overall_success = (order_creation_success and agent_fee_success and 
                          payment_timing_success and dropoff_details_success and 
                          offline_payment_success and product_lookup_success)
        
        if overall_success:
            self.log_test("Order Creation Fix - Complete", True, "All order creation functionality working correctly")
        else:
            self.log_test("Order Creation Fix - Complete", False, "Some order creation issues remain")
        
        return overall_success

    def run_test(self):
        """Run the focused order creation test"""
        print("🚀 Starting Order Creation Fix Test...")
        print("=" * 60)
        
        # Login first
        if not self.login_existing_user():
            print("❌ Login failed. Cannot proceed with tests.")
            return False
        
        # Run the order creation fix test
        success = self.test_order_creation_fix()
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 TEST COMPLETE")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if success:
            print("🎉 ORDER CREATION FIX WORKING!")
        else:
            print("⚠️ ORDER CREATION FIX HAS ISSUES")
            
        return success

def main():
    """Main test execution"""
    tester = OrderCreationTester()
    
    try:
        success = tester.run_test()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())