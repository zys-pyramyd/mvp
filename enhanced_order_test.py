#!/usr/bin/env python3
"""
Enhanced Order Creation Testing with Drop-off Location Support
Tests order creation, agent fee calculation, and payment timing logic
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class EnhancedOrderTester:
    def __init__(self, base_url: str = "https://db16cee4-7596-40bf-9ed9-efba806794f6.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

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

    def test_complete_registration_agent(self):
        """Test complete registration flow for agent"""
        timestamp = datetime.now().strftime("%H%M%S")
        registration_data = {
            "first_name": "Agent",
            "last_name": "Test",
            "username": f"agent_order_{timestamp}",
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
            self.log_test("Complete Registration (Agent)", True)
            return True, registration_data
        else:
            self.log_test("Complete Registration (Agent)", False, f"Complete registration failed: {response}")
            return False, registration_data

    def create_test_product(self):
        """Create a test product for order testing"""
        product_data = {
            "title": "Test Product for Orders",
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
            return response['product_id']
        else:
            return None

    def create_test_dropoff_location(self):
        """Create a test drop-off location"""
        location_data = {
            "name": "Test Drop-off Location",
            "address": "123 Test Street, Lagos",
            "city": "Lagos",
            "state": "Lagos State",
            "country": "Nigeria",
            "contact_person": "Test Contact",
            "contact_phone": "+234-801-234-5678",
            "operating_hours": "8:00 AM - 6:00 PM",
            "description": "Test drop-off location for order testing"
        }

        success, response = self.make_request('POST', '/api/dropoff-locations', location_data, 200, use_auth=True)
        
        if success and 'location_id' in response:
            return response['location_id']
        else:
            return None

    def test_order_creation_with_dropoff(self):
        """Test enhanced order creation with drop-off location support"""
        print("\n🛒 Testing Order Creation with Drop-off Location...")
        
        # Create test product and location
        product_id = self.create_test_product()
        location_id = self.create_test_dropoff_location()
        
        if not product_id or not location_id:
            self.log_test("Order Creation with Drop-off", False, "Cannot test without valid product and location")
            return False

        # Test 1: Valid order with drop-off location
        order_data = {
            "product_id": product_id,
            "quantity": 10,
            "unit": "kg",
            "unit_specification": "fresh",
            "delivery_method": "dropoff",
            "dropoff_location_id": location_id
        }

        success, response = self.make_request('POST', '/api/orders/create', order_data, 200, use_auth=True)
        
        if success and 'order_id' in response:
            self.log_test("Order Creation with Drop-off (Valid)", True)
            valid_order_success = True
            order_id = response['order_id']
        else:
            self.log_test("Order Creation with Drop-off (Valid)", False, f"Order creation failed: {response}")
            valid_order_success = False
            order_id = None

        # Test 2: Drop-off delivery without location ID (should fail)
        invalid_order_data = {
            "product_id": product_id,
            "quantity": 5,
            "unit": "kg",
            "delivery_method": "dropoff"
            # Missing dropoff_location_id
        }

        success, response = self.make_request('POST', '/api/orders/create', invalid_order_data, 422, use_auth=True)
        
        if success:  # Should return 422 validation error
            self.log_test("Order Creation with Drop-off (Missing Location)", True)
            validation_success = True
        else:
            self.log_test("Order Creation with Drop-off (Missing Location)", False, f"Should return 422 error: {response}")
            validation_success = False

        # Test 3: Invalid drop-off location ID
        invalid_location_order_data = {
            "product_id": product_id,
            "quantity": 5,
            "unit": "kg",
            "delivery_method": "dropoff",
            "dropoff_location_id": "non-existent-location-id"
        }

        success, response = self.make_request('POST', '/api/orders/create', invalid_location_order_data, 404, use_auth=True)
        
        if success:  # Should return 404 error
            self.log_test("Order Creation with Drop-off (Invalid Location)", True)
            invalid_location_success = True
        else:
            self.log_test("Order Creation with Drop-off (Invalid Location)", False, f"Should return 404 error: {response}")
            invalid_location_success = False

        # Test 4: Platform delivery (should work without drop-off location)
        platform_order_data = {
            "product_id": product_id,
            "quantity": 3,
            "unit": "kg",
            "delivery_method": "platform",
            "shipping_address": "123 Test Street, Lagos, Nigeria"
        }

        success, response = self.make_request('POST', '/api/orders/create', platform_order_data, 200, use_auth=True)
        
        if success and 'order_id' in response:
            self.log_test("Order Creation with Platform Delivery", True)
            platform_success = True
        else:
            self.log_test("Order Creation with Platform Delivery", False, f"Platform order creation failed: {response}")
            platform_success = False

        # Test 5: Offline delivery (should work without drop-off location)
        offline_order_data = {
            "product_id": product_id,
            "quantity": 2,
            "unit": "kg",
            "delivery_method": "offline",
            "shipping_address": "456 Test Avenue, Abuja, Nigeria"
        }

        success, response = self.make_request('POST', '/api/orders/create', offline_order_data, 200, use_auth=True)
        
        if success and 'order_id' in response:
            self.log_test("Order Creation with Offline Delivery", True)
            offline_success = True
        else:
            self.log_test("Order Creation with Offline Delivery", False, f"Offline order creation failed: {response}")
            offline_success = False

        overall_success = (valid_order_success and validation_success and invalid_location_success and 
                          platform_success and offline_success)
        
        return overall_success, order_id

    def test_agent_fee_calculation(self):
        """Test updated agent fee calculation (5%)"""
        print("\n💰 Testing Agent Fee Calculation (5%)...")
        
        # Create a test product
        product_id = self.create_test_product()
        
        if not product_id:
            self.log_test("Agent Fee Calculation", False, "Cannot test without valid product")
            return False

        # Test agent purchase with commission
        request_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 100  # Large quantity to see clear commission
                }
            ],
            "purchase_option": {
                "commission_type": "percentage",
                "customer_id": "test_customer_fee_calc",
                "delivery_address": "Test Address for Fee Calculation"
            }
        }

        success, response = self.make_request('POST', '/api/agent/purchase', request_data, 200, use_auth=True)
        
        if success and 'commission_amount' in response and 'total_amount' in response:
            total_amount = response['total_amount']
            commission_amount = response['commission_amount']
            expected_commission = total_amount * 0.05  # 5%
            
            # Allow small floating point differences
            if abs(commission_amount - expected_commission) < 0.01:
                self.log_test("Agent Fee Calculation (5%)", True, 
                             f"Total: ₦{total_amount}, Commission: ₦{commission_amount} (5%)")
                return True
            else:
                self.log_test("Agent Fee Calculation (5%)", False, 
                             f"Expected ₦{expected_commission}, got ₦{commission_amount}")
                return False
        else:
            self.log_test("Agent Fee Calculation (5%)", False, f"Agent purchase failed: {response}")
            return False

    def test_payment_timing_logic(self, order_id: str):
        """Test payment timing logic based on delivery method"""
        print("\n⏰ Testing Payment Timing Logic...")
        
        if not order_id:
            self.log_test("Payment Timing Logic", False, "Cannot test without valid order")
            return False

        # Get order details to check payment timing
        success, response = self.make_request('GET', f'/api/orders/{order_id}', use_auth=True)
        
        if success and 'payment_timing' in response:
            payment_timing = response['payment_timing']
            delivery_method = response.get('delivery_method', 'unknown')
            
            # Check if payment timing matches delivery method
            if delivery_method == 'platform' and payment_timing == 'during_transit':
                self.log_test("Payment Timing Logic (Platform)", True, 
                             f"Platform delivery correctly set to 'during_transit'")
                return True
            elif delivery_method in ['offline', 'dropoff'] and payment_timing == 'after_delivery':
                self.log_test("Payment Timing Logic (Offline/Dropoff)", True, 
                             f"{delivery_method} delivery correctly set to 'after_delivery'")
                return True
            else:
                self.log_test("Payment Timing Logic", False, 
                             f"Unexpected timing: {delivery_method} -> {payment_timing}")
                return False
        else:
            self.log_test("Payment Timing Logic", False, f"Order details retrieval failed: {response}")
            return False

    def run_enhanced_order_tests(self):
        """Run all enhanced order tests"""
        print("🚀 Starting Enhanced Order Creation Testing...")
        print("=" * 60)
        
        # Create agent user
        agent_reg_success, agent_data = self.test_complete_registration_agent()
        if not agent_reg_success:
            print("❌ Agent registration failed - stopping tests")
            return False
        
        # Step 1: Test order creation with drop-off
        order_creation_success, order_id = self.test_order_creation_with_dropoff()
        
        # Step 2: Test agent fee calculation
        agent_fee_success = self.test_agent_fee_calculation()
        
        # Step 3: Test payment timing logic
        if order_id:
            payment_timing_success = self.test_payment_timing_logic(order_id)
        else:
            payment_timing_success = False
        
        overall_success = order_creation_success and agent_fee_success and payment_timing_success
        
        if overall_success:
            self.log_test("Complete Enhanced Order System", True, 
                         "All enhanced order functionality working correctly")
        else:
            self.log_test("Complete Enhanced Order System", False, 
                         "One or more enhanced order components failed")
        
        return overall_success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED ORDER CREATION TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_run - self.tests_passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['name']}: {result['details']}")

        print("\n🎯 Key Findings:")
        if self.tests_passed >= self.tests_run * 0.8:
            print("   ✅ Enhanced Order Creation API is mostly functional")
        else:
            print("   ⚠️  Enhanced Order Creation API has significant issues")

        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = EnhancedOrderTester()
    
    try:
        success = tester.run_enhanced_order_tests()
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