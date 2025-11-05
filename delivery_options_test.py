#!/usr/bin/env python3
"""
Enhanced Delivery Options System Testing for Pyramyd Agritech Platform
Tests the new supplier delivery options functionality as requested in the review
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class DeliveryOptionsAPITester:
    def __init__(self, base_url: str = "https://farm2consumer.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.test_product_ids = {}

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

    def setup_test_user(self):
        """Setup a test user with proper role for testing"""
        print("🔐 Setting up test user with agent role...")
        
        # Create new agent user with complete registration
        timestamp = datetime.now().strftime("%H%M%S")
        registration_data = {
            "first_name": "Delivery",
            "last_name": "Tester",
            "username": f"delivery_test_{timestamp}",
            "email_or_phone": f"delivery_{timestamp}@pyramyd.com",
            "password": "DeliveryTest123!",
            "phone": "+1234567890",
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "user_path": "partner",
            "partner_type": "agent",
            "business_info": {
                "business_name": "Delivery Test Business",
                "business_address": "Test Address"
            },
            "verification_info": {
                "nin": "12345678901"
            }
        }

        success, response = self.make_request('POST', '/api/auth/complete-registration', registration_data, 200)
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            self.log_test("Create Agent User for Testing", True)
            return True
        else:
            self.log_test("Create Agent User for Testing", False, f"Registration failed: {response}")
            return False

    def test_product_creation_with_delivery_options(self):
        """Test creating products with various delivery preferences"""
        print("\n📦 Testing Product Creation with Delivery Options...")
        
        # Test 1: Product that supports both dropoff and shipping delivery (both free)
        both_free_data = {
            "title": "Fresh Tomatoes - Both Free Delivery",
            "description": "Fresh tomatoes with free delivery options",
            "category": "vegetables",
            "price_per_unit": 500.0,
            "unit_of_measure": "kg",
            "quantity_available": 100,
            "minimum_order_quantity": 5,
            "location": "Lagos, Nigeria",
            "farm_name": "Green Farm",
            "images": [],
            "platform": "pyhub",
            "supports_dropoff_delivery": True,
            "supports_shipping_delivery": True,
            "delivery_cost_dropoff": 0.0,
            "delivery_cost_shipping": 0.0,
            "delivery_notes": "Free delivery for both methods"
        }

        success, response = self.make_request('POST', '/api/products', both_free_data, 200, use_auth=True)
        
        if success and 'product_id' in response:
            self.log_test("Product Creation - Both Methods Free", True)
            self.test_product_ids['both_free'] = response['product_id']
            both_free_success = True
        else:
            self.log_test("Product Creation - Both Methods Free", False, f"Creation failed: {response}")
            both_free_success = False

        # Test 2: Product that supports only dropoff delivery with ₦200 cost
        dropoff_only_data = {
            "title": "Rice - Dropoff Only ₦200",
            "description": "Premium rice with dropoff delivery only",
            "category": "grain",
            "price_per_unit": 800.0,
            "unit_of_measure": "bag",
            "unit_specification": "50kg",
            "quantity_available": 50,
            "minimum_order_quantity": 1,
            "location": "Kebbi, Nigeria",
            "farm_name": "Rice Valley",
            "images": [],
            "platform": "pyhub",
            "supports_dropoff_delivery": True,
            "supports_shipping_delivery": False,
            "delivery_cost_dropoff": 200.0,
            "delivery_cost_shipping": 0.0,
            "delivery_notes": "Dropoff delivery only - ₦200 fee"
        }

        success, response = self.make_request('POST', '/api/products', dropoff_only_data, 200, use_auth=True)
        
        if success and 'product_id' in response:
            self.log_test("Product Creation - Dropoff Only ₦200", True)
            self.test_product_ids['dropoff_only'] = response['product_id']
            dropoff_only_success = True
        else:
            self.log_test("Product Creation - Dropoff Only ₦200", False, f"Creation failed: {response}")
            dropoff_only_success = False

        # Test 3: Product that supports only shipping delivery with ₦500 cost
        shipping_only_data = {
            "title": "Palm Oil - Shipping Only ₦500",
            "description": "Pure palm oil with shipping delivery only",
            "category": "packaged_goods",
            "price_per_unit": 1200.0,
            "unit_of_measure": "gallon",
            "unit_specification": "5 litres",
            "quantity_available": 30,
            "minimum_order_quantity": 1,
            "location": "Cross River, Nigeria",
            "farm_name": "Palm Processing Center",
            "images": [],
            "platform": "pyhub",
            "supports_dropoff_delivery": False,
            "supports_shipping_delivery": True,
            "delivery_cost_dropoff": 0.0,
            "delivery_cost_shipping": 500.0,
            "delivery_notes": "Shipping delivery only - ₦500 fee"
        }

        success, response = self.make_request('POST', '/api/products', shipping_only_data, 200, use_auth=True)
        
        if success and 'product_id' in response:
            self.log_test("Product Creation - Shipping Only ₦500", True)
            self.test_product_ids['shipping_only'] = response['product_id']
            shipping_only_success = True
        else:
            self.log_test("Product Creation - Shipping Only ₦500", False, f"Creation failed: {response}")
            shipping_only_success = False

        # Test 4: Product with both methods but different costs (dropoff: free, shipping: ₦300)
        different_costs_data = {
            "title": "Maize - Different Delivery Costs",
            "description": "Fresh maize with different delivery costs",
            "category": "grain",
            "price_per_unit": 400.0,
            "unit_of_measure": "bag",
            "unit_specification": "100kg",
            "quantity_available": 80,
            "minimum_order_quantity": 2,
            "location": "Benue, Nigeria",
            "farm_name": "Maize Valley Farm",
            "images": [],
            "platform": "pyhub",
            "supports_dropoff_delivery": True,
            "supports_shipping_delivery": True,
            "delivery_cost_dropoff": 0.0,
            "delivery_cost_shipping": 300.0,
            "delivery_notes": "Free dropoff, ₦300 shipping"
        }

        success, response = self.make_request('POST', '/api/products', different_costs_data, 200, use_auth=True)
        
        if success and 'product_id' in response:
            self.log_test("Product Creation - Different Costs", True)
            self.test_product_ids['different_costs'] = response['product_id']
            different_costs_success = True
        else:
            self.log_test("Product Creation - Different Costs", False, f"Creation failed: {response}")
            different_costs_success = False

        overall_success = both_free_success and dropoff_only_success and shipping_only_success and different_costs_success
        return overall_success

    def test_delivery_options_api(self):
        """Test the delivery options API endpoints"""
        print("\n🔌 Testing Delivery Options API Endpoints...")
        
        if not self.test_product_ids.get('both_free'):
            self.log_test("Delivery Options API", False, "No test products available")
            return False

        # Test 1: GET /api/products/{product_id}/delivery-options for each test product
        
        # Test both_free product
        success, response = self.make_request('GET', f'/api/products/{self.test_product_ids["both_free"]}/delivery-options')
        
        if success and response.get('supports_dropoff_delivery') == True and response.get('supports_shipping_delivery') == True:
            delivery_costs = response.get('delivery_costs', {})
            if (delivery_costs.get('dropoff', {}).get('cost') == 0.0 and 
                delivery_costs.get('shipping', {}).get('cost') == 0.0):
                self.log_test("GET Delivery Options - Both Free", True)
                get_both_free_success = True
            else:
                self.log_test("GET Delivery Options - Both Free", False, f"Incorrect costs: {delivery_costs}")
                get_both_free_success = False
        else:
            self.log_test("GET Delivery Options - Both Free", False, f"Incorrect response: {response}")
            get_both_free_success = False

        # Test dropoff_only product
        if self.test_product_ids.get('dropoff_only'):
            success, response = self.make_request('GET', f'/api/products/{self.test_product_ids["dropoff_only"]}/delivery-options')
            
            if (success and response.get('supports_dropoff_delivery') == True and 
                response.get('supports_shipping_delivery') == False):
                delivery_costs = response.get('delivery_costs', {})
                if delivery_costs.get('dropoff', {}).get('cost') == 200.0:
                    self.log_test("GET Delivery Options - Dropoff Only ₦200", True)
                    get_dropoff_only_success = True
                else:
                    self.log_test("GET Delivery Options - Dropoff Only ₦200", False, f"Incorrect cost: {delivery_costs}")
                    get_dropoff_only_success = False
            else:
                self.log_test("GET Delivery Options - Dropoff Only ₦200", False, f"Incorrect response: {response}")
                get_dropoff_only_success = False
        else:
            get_dropoff_only_success = False

        # Test shipping_only product
        if self.test_product_ids.get('shipping_only'):
            success, response = self.make_request('GET', f'/api/products/{self.test_product_ids["shipping_only"]}/delivery-options')
            
            if (success and response.get('supports_dropoff_delivery') == False and 
                response.get('supports_shipping_delivery') == True):
                delivery_costs = response.get('delivery_costs', {})
                if delivery_costs.get('shipping', {}).get('cost') == 500.0:
                    self.log_test("GET Delivery Options - Shipping Only ₦500", True)
                    get_shipping_only_success = True
                else:
                    self.log_test("GET Delivery Options - Shipping Only ₦500", False, f"Incorrect cost: {delivery_costs}")
                    get_shipping_only_success = False
            else:
                self.log_test("GET Delivery Options - Shipping Only ₦500", False, f"Incorrect response: {response}")
                get_shipping_only_success = False
        else:
            get_shipping_only_success = False

        # Test 2: PUT /api/products/{product_id}/delivery-options to update delivery preferences
        if self.test_product_ids.get('both_free'):
            update_data = {
                "supports_dropoff_delivery": True,
                "supports_shipping_delivery": True,
                "delivery_cost_dropoff": 100.0,
                "delivery_cost_shipping": 250.0,
                "delivery_notes": "Updated delivery costs"
            }

            success, response = self.make_request('PUT', f'/api/products/{self.test_product_ids["both_free"]}/delivery-options', 
                                                update_data, 200, use_auth=True)
            
            if success and response.get('message'):
                self.log_test("PUT Delivery Options - Update", True)
                put_update_success = True
                
                # Verify the update worked
                success, response = self.make_request('GET', f'/api/products/{self.test_product_ids["both_free"]}/delivery-options')
                if (success and response.get('delivery_costs', {}).get('dropoff', {}).get('cost') == 100.0 and
                    response.get('delivery_costs', {}).get('shipping', {}).get('cost') == 250.0):
                    self.log_test("PUT Delivery Options - Verification", True)
                    put_verify_success = True
                else:
                    self.log_test("PUT Delivery Options - Verification", False, f"Update not reflected: {response}")
                    put_verify_success = False
            else:
                self.log_test("PUT Delivery Options - Update", False, f"Update failed: {response}")
                put_update_success = False
                put_verify_success = False
        else:
            put_update_success = False
            put_verify_success = False

        overall_success = (get_both_free_success and get_dropoff_only_success and 
                          get_shipping_only_success and put_update_success and put_verify_success)
        return overall_success

    def test_enhanced_order_creation(self):
        """Test order creation with the new delivery cost calculations"""
        print("\n🛒 Testing Enhanced Order Creation with Delivery Costs...")
        
        if not self.test_product_ids:
            self.log_test("Enhanced Order Creation", False, "No test products available")
            return False

        # First create a test drop-off location for dropoff orders
        dropoff_location_data = {
            "name": "Test Delivery Hub",
            "address": "123 Test Street, Test Area",
            "city": "Lagos",
            "state": "Lagos",
            "contact_person": "Test Contact",
            "contact_phone": "+2341234567890",
            "operating_hours": "8AM - 6PM",
            "description": "Test drop-off location for delivery testing"
        }

        success, response = self.make_request('POST', '/api/dropoff-locations', dropoff_location_data, 200, use_auth=True)
        
        if success and 'location_id' in response:
            dropoff_location_id = response['location_id']
            dropoff_creation_success = True
        else:
            self.log_test("Enhanced Order Creation - Dropoff Location Setup", False, f"Failed to create dropoff location: {response}")
            return False

        # Test 1: Create order using dropoff delivery (should include dropoff cost)
        if self.test_product_ids.get('dropoff_only'):
            dropoff_order_data = {
                "product_id": self.test_product_ids['dropoff_only'],
                "quantity": 2.0,
                "unit": "bag",
                "unit_specification": "50kg",
                "delivery_method": "dropoff",
                "dropoff_location_id": dropoff_location_id
            }

            success, response = self.make_request('POST', '/api/orders/create', dropoff_order_data, 200, use_auth=True)
            
            if success and 'cost_breakdown' in response:
                cost_breakdown = response['cost_breakdown']
                # Expected: 2 bags * ₦800 = ₦1600 product + ₦200 delivery = ₦1800 total
                expected_product_total = 2.0 * 800.0  # 1600
                expected_delivery_cost = 200.0
                expected_total = expected_product_total + expected_delivery_cost  # 1800
                
                if (cost_breakdown.get('product_total') == expected_product_total and
                    cost_breakdown.get('delivery_cost') == expected_delivery_cost and
                    cost_breakdown.get('total_amount') == expected_total):
                    self.log_test("Enhanced Order Creation - Dropoff with Cost", True, 
                                 f"Correct breakdown: Product ₦{expected_product_total}, Delivery ₦{expected_delivery_cost}, Total ₦{expected_total}")
                    dropoff_order_success = True
                else:
                    self.log_test("Enhanced Order Creation - Dropoff with Cost", False, 
                                 f"Incorrect breakdown: {cost_breakdown}")
                    dropoff_order_success = False
            else:
                self.log_test("Enhanced Order Creation - Dropoff with Cost", False, f"Order creation failed: {response}")
                dropoff_order_success = False
        else:
            dropoff_order_success = False

        # Test 2: Create order using shipping delivery (should include shipping cost)
        if self.test_product_ids.get('shipping_only'):
            shipping_order_data = {
                "product_id": self.test_product_ids['shipping_only'],
                "quantity": 1.0,
                "unit": "gallon",
                "unit_specification": "5 litres",
                "delivery_method": "platform",
                "shipping_address": "456 Test Avenue, Test City, Test State"
            }

            success, response = self.make_request('POST', '/api/orders/create', shipping_order_data, 200, use_auth=True)
            
            if success and 'cost_breakdown' in response:
                cost_breakdown = response['cost_breakdown']
                # Expected: 1 gallon * ₦1200 = ₦1200 product + ₦500 delivery = ₦1700 total
                expected_product_total = 1.0 * 1200.0  # 1200
                expected_delivery_cost = 500.0
                expected_total = expected_product_total + expected_delivery_cost  # 1700
                
                if (cost_breakdown.get('product_total') == expected_product_total and
                    cost_breakdown.get('delivery_cost') == expected_delivery_cost and
                    cost_breakdown.get('total_amount') == expected_total):
                    self.log_test("Enhanced Order Creation - Shipping with Cost", True,
                                 f"Correct breakdown: Product ₦{expected_product_total}, Delivery ₦{expected_delivery_cost}, Total ₦{expected_total}")
                    shipping_order_success = True
                else:
                    self.log_test("Enhanced Order Creation - Shipping with Cost", False,
                                 f"Incorrect breakdown: {cost_breakdown}")
                    shipping_order_success = False
            else:
                self.log_test("Enhanced Order Creation - Shipping with Cost", False, f"Order creation failed: {response}")
                shipping_order_success = False
        else:
            shipping_order_success = False

        # Test 3: Test validation - try creating order with unsupported delivery method
        if self.test_product_ids.get('dropoff_only'):
            # Try to use shipping on a dropoff-only product
            invalid_order_data = {
                "product_id": self.test_product_ids['dropoff_only'],
                "quantity": 1.0,
                "unit": "bag",
                "delivery_method": "platform",
                "shipping_address": "Invalid shipping address"
            }

            success, response = self.make_request('POST', '/api/orders/create', invalid_order_data, 400, use_auth=True)
            
            if success:  # Should return 400 error
                self.log_test("Enhanced Order Creation - Unsupported Method Validation", True)
                validation_success = True
            else:
                self.log_test("Enhanced Order Creation - Unsupported Method Validation", False, 
                             f"Should return 400 error: {response}")
                validation_success = False
        else:
            validation_success = False

        # Test 4: Verify cost breakdown in order responses includes product_total and delivery_cost
        if self.test_product_ids.get('different_costs'):
            # Use different_costs product which has free dropoff delivery
            free_order_data = {
                "product_id": self.test_product_ids['different_costs'],
                "quantity": 3.0,
                "unit": "bag",
                "unit_specification": "100kg",
                "delivery_method": "dropoff",
                "dropoff_location_id": dropoff_location_id
            }

            success, response = self.make_request('POST', '/api/orders/create', free_order_data, 200, use_auth=True)
            
            if success and 'cost_breakdown' in response:
                cost_breakdown = response['cost_breakdown']
                # different_costs product has free dropoff delivery, so delivery_cost should be 0
                if (cost_breakdown.get('delivery_cost') == 0.0 and
                    'product_total' in cost_breakdown and
                    'total_amount' in cost_breakdown):
                    self.log_test("Enhanced Order Creation - Free Delivery Breakdown", True,
                                 f"Correct free delivery breakdown: {cost_breakdown}")
                    breakdown_success = True
                else:
                    self.log_test("Enhanced Order Creation - Free Delivery Breakdown", False,
                                 f"Incorrect breakdown: {cost_breakdown}")
                    breakdown_success = False
            else:
                self.log_test("Enhanced Order Creation - Free Delivery Breakdown", False, f"Order creation failed: {response}")
                breakdown_success = False
        else:
            breakdown_success = False

        overall_success = dropoff_order_success and shipping_order_success and validation_success and breakdown_success
        return overall_success

    def test_delivery_options_validation(self):
        """Test validation scenarios for delivery options"""
        print("\n✅ Testing Delivery Options Validation...")
        
        if not self.test_product_ids.get('both_free'):
            self.log_test("Delivery Options Validation", False, "No test products available")
            return False

        # Test 1: Try updating delivery options for products you don't own
        # First create another user
        timestamp = datetime.now().strftime("%H%M%S")
        other_user_data = {
            "first_name": "Other",
            "last_name": "User",
            "username": f"otheruser_{timestamp}",
            "email": f"other_{timestamp}@example.com",
            "password": "OtherPass123!",
            "phone": "+1234567892"
        }

        success, response = self.make_request('POST', '/api/auth/register', other_user_data, 200)
        
        if success and 'token' in response:
            other_user_token = response['token']
            
            # Try to update delivery options with other user's token
            update_data = {
                "supports_dropoff_delivery": False,
                "supports_shipping_delivery": True,
                "delivery_cost_shipping": 1000.0
            }

            # Temporarily switch token
            original_token = self.token
            self.token = other_user_token

            success, response = self.make_request('PUT', f'/api/products/{self.test_product_ids["both_free"]}/delivery-options', 
                                                update_data, 403, use_auth=True)
            
            # Restore original token
            self.token = original_token
            
            if success:  # Should return 403 error
                self.log_test("Delivery Options Validation - Ownership Check", True)
                ownership_success = True
            else:
                self.log_test("Delivery Options Validation - Ownership Check", False, 
                             f"Should return 403 error: {response}")
                ownership_success = False
        else:
            self.log_test("Delivery Options Validation - Ownership Check", False, "Failed to create other user")
            ownership_success = False

        # Test 2: Try disabling both delivery methods (should fail)
        invalid_update_data = {
            "supports_dropoff_delivery": False,
            "supports_shipping_delivery": False
        }

        success, response = self.make_request('PUT', f'/api/products/{self.test_product_ids["both_free"]}/delivery-options', 
                                            invalid_update_data, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Delivery Options Validation - Both Methods Disabled", True)
            both_disabled_success = True
        else:
            self.log_test("Delivery Options Validation - Both Methods Disabled", False, 
                         f"Should return 400 error: {response}")
            both_disabled_success = False

        # Test 3: Test with invalid cost values (negative numbers should be converted to 0)
        negative_cost_data = {
            "supports_dropoff_delivery": True,
            "supports_shipping_delivery": True,
            "delivery_cost_dropoff": -100.0,  # Should be converted to 0
            "delivery_cost_shipping": -200.0   # Should be converted to 0
        }

        success, response = self.make_request('PUT', f'/api/products/{self.test_product_ids["both_free"]}/delivery-options', 
                                            negative_cost_data, 200, use_auth=True)
        
        if success:
            # Verify that negative costs were converted to 0
            success, response = self.make_request('GET', f'/api/products/{self.test_product_ids["both_free"]}/delivery-options')
            
            if (success and response.get('delivery_costs', {}).get('dropoff', {}).get('cost') == 0.0 and
                response.get('delivery_costs', {}).get('shipping', {}).get('cost') == 0.0):
                self.log_test("Delivery Options Validation - Negative Cost Handling", True,
                             "Negative costs correctly converted to 0")
                negative_cost_success = True
            else:
                self.log_test("Delivery Options Validation - Negative Cost Handling", False,
                             f"Negative costs not handled correctly: {response}")
                negative_cost_success = False
        else:
            self.log_test("Delivery Options Validation - Negative Cost Handling", False, 
                         f"Update with negative costs failed: {response}")
            negative_cost_success = False

        # Test 4: Test non-existent product
        fake_product_id = "non-existent-product-id"
        success, response = self.make_request('GET', f'/api/products/{fake_product_id}/delivery-options', expected_status=404)
        
        if success:  # Should return 404 error
            self.log_test("Delivery Options Validation - Non-existent Product", True)
            non_existent_success = True
        else:
            self.log_test("Delivery Options Validation - Non-existent Product", False, 
                         f"Should return 404 error: {response}")
            non_existent_success = False

        overall_success = ownership_success and both_disabled_success and negative_cost_success and non_existent_success
        return overall_success

    def run_all_tests(self):
        """Run all enhanced delivery options tests"""
        print("🚚 Starting Enhanced Delivery Options System Testing...")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 80)

        # Health check first
        success, response = self.make_request('GET', '/api/health')
        if not success or response.get('status') != 'healthy':
            print("❌ Health check failed - stopping tests")
            return False
        self.log_test("Health Check", True)

        # Setup test user with proper role
        if not self.setup_test_user():
            print("❌ Failed to setup test user - stopping tests")
            return False

        # Test 1: Product Creation with Delivery Options
        print("\n📦 Testing Product Creation with Delivery Options...")
        creation_success = self.test_product_creation_with_delivery_options()
        
        # Test 2: Delivery Options API endpoints
        print("\n🔌 Testing Delivery Options API Endpoints...")
        api_success = self.test_delivery_options_api()
        
        # Test 3: Enhanced Order Creation with delivery costs
        print("\n🛒 Testing Enhanced Order Creation with Delivery Costs...")
        order_success = self.test_enhanced_order_creation()
        
        # Test 4: Edge Cases and Validation
        print("\n✅ Testing Delivery Options Validation...")
        validation_success = self.test_delivery_options_validation()
        
        # Overall success
        overall_success = creation_success and api_success and order_success and validation_success
        
        if overall_success:
            self.log_test("Complete Enhanced Delivery Options System", True,
                         "All delivery options functionality working correctly")
        else:
            self.log_test("Complete Enhanced Delivery Options System", False,
                         "One or more delivery options components failed")

        return overall_success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 ENHANCED DELIVERY OPTIONS TEST SUMMARY")
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

        print("\n🎯 Key Findings:")
        if self.tests_passed >= self.tests_run * 0.8:
            print("   ✅ Enhanced Delivery Options System is mostly functional")
        else:
            print("   ⚠️  Enhanced Delivery Options System has significant issues")

        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = DeliveryOptionsAPITester()
    
    try:
        success = tester.run_all_tests()
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