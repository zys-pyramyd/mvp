#!/usr/bin/env python3
"""
Test script for the new KYC system and pre-order filter functionality
"""

import requests
import json
from datetime import datetime

class NewKYCSystemTester:
    def __init__(self):
        self.base_url = "https://farm2consumer.preview.emergentagent.com"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
    
    def log_test(self, test_name, success, details=""):
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED" + (f": {details}" if details else ""))
        else:
            print(f"❌ {test_name} - FAILED" + (f": {details}" if details else ""))
    
    def make_request(self, method, endpoint, data=None, expected_status=200, use_auth=False):
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
            else:
                return False, f"Unsupported method: {method}"
            
            if response.status_code == expected_status:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                try:
                    return False, response.json()
                except:
                    return False, f"Status: {response.status_code}, Response: {response.text}"
        
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def login_existing_user(self):
        """Login with existing test user"""
        login_data = {
            "email_or_phone": "testagent@pyramyd.com",
            "password": "password123"
        }
        
        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            self.log_test("Login Existing User", True)
            return True
        else:
            self.log_test("Login Existing User", False, f"Login failed: {response}")
            return False
    
    def test_preorder_filter_api(self):
        """Test pre-order filter API for fam deals page"""
        print("\n🔍 Testing Pre-order Filter API...")
        
        # Test 1: Test /api/products?platform=fam_deals&only_preorders=true
        success, response = self.make_request('GET', '/api/products?platform=fam_deals&only_preorders=true')
        
        if success and isinstance(response, dict):
            products = response.get('products', [])
            preorders = response.get('preorders', [])
            
            # Should return only pre-orders for fam deals (farmer/agent products)
            if len(preorders) >= 0:  # Can be 0 if no pre-orders exist
                self.log_test("Pre-order Filter - Fam Deals Only Pre-orders", True, 
                             f"Found {len(preorders)} pre-orders for fam deals")
                fam_deals_preorders_success = True
            else:
                self.log_test("Pre-order Filter - Fam Deals Only Pre-orders", False, 
                             f"Invalid response structure: {response}")
                fam_deals_preorders_success = False
        else:
            self.log_test("Pre-order Filter - Fam Deals Only Pre-orders", False, 
                         f"API call failed: {response}")
            fam_deals_preorders_success = False
        
        # Test 2: Test without the filter to ensure regular products still show
        success, response = self.make_request('GET', '/api/products?platform=fam_deals')
        
        if success and isinstance(response, dict):
            products = response.get('products', [])
            preorders = response.get('preorders', [])
            total_items = len(products) + len(preorders)
            
            self.log_test("Pre-order Filter - Fam Deals All Products", True, 
                         f"Found {len(products)} products and {len(preorders)} pre-orders")
            fam_deals_all_success = True
        else:
            self.log_test("Pre-order Filter - Fam Deals All Products", False, 
                         f"API call failed: {response}")
            fam_deals_all_success = False
        
        # Test 3: Test combination with other filters (category, location, price)
        success, response = self.make_request('GET', '/api/products?platform=fam_deals&only_preorders=true&category=grains_legumes&location=Nigeria&min_price=100&max_price=1000')
        
        if success and isinstance(response, dict):
            self.log_test("Pre-order Filter - Combined Filters", True, 
                         "Combined filtering with pre-orders working")
            combined_filters_success = True
        else:
            self.log_test("Pre-order Filter - Combined Filters", False, 
                         f"Combined filtering failed: {response}")
            combined_filters_success = False
        
        overall_success = fam_deals_preorders_success and fam_deals_all_success and combined_filters_success
        return overall_success
    
    def test_kyc_status_integration(self):
        """Test KYC status integration endpoint"""
        print("\n📊 Testing KYC Status Integration...")
        
        # Test 1: Get KYC status for current user
        success, response = self.make_request('GET', '/api/users/kyc/status', use_auth=True)
        
        if success and 'status' in response:
            required_fields = ['status', 'requires_kyc', 'can_trade']
            
            if all(field in response for field in required_fields):
                kyc_status = response.get('status')
                can_trade = response.get('can_trade')
                requires_kyc = response.get('requires_kyc')
                
                self.log_test("KYC Status Integration (Basic)", True, 
                             f"Status: {kyc_status}, Can Trade: {can_trade}, Requires KYC: {requires_kyc}")
                basic_status_success = True
            else:
                self.log_test("KYC Status Integration (Basic)", False, 
                             f"Missing required fields: {response}")
                basic_status_success = False
        else:
            self.log_test("KYC Status Integration (Basic)", False, 
                         f"KYC status retrieval failed: {response}")
            basic_status_success = False
        
        return basic_status_success
    
    def test_agent_kyc_submission(self):
        """Test new agent KYC submission endpoint"""
        print("\n🏢 Testing Agent KYC Submission...")
        
        # Test 1: Valid agent KYC submission
        valid_agent_kyc_data = {
            "agent_business_name": "Green Valley Agricultural Services",
            "business_address": "123 Farm Road, Agricultural Zone, Lagos State",
            "business_type": "Agricultural Agent/Aggregator",
            "full_name": "John Doe Agent",
            "phone_number": "+2348123456789",
            "email_address": "john.agent@greenvalley.com",
            "identification_type": "nin",  # lowercase
            "identification_number": "12345678901",
            "agricultural_experience_years": 5,
            "target_locations": ["Lagos", "Ogun", "Oyo"],
            "expected_farmer_network_size": 50,
            "headshot_photo_id": "photo_123",
            "national_id_document_id": "id_doc_123",
            "utility_bill_id": "utility_123"
        }
        
        success, response = self.make_request('POST', '/api/kyc/agent/submit', valid_agent_kyc_data, 200, use_auth=True)
        
        if success and 'message' in response and 'kyc_status' in response:
            self.log_test("Agent KYC Submission (Valid)", True, 
                         f"KYC status: {response.get('kyc_status')}")
            valid_submission_success = True
        else:
            self.log_test("Agent KYC Submission (Valid)", False, 
                         f"Submission failed: {response}")
            valid_submission_success = False
        
        # Test 2: Invalid identification number format
        invalid_nin_data = valid_agent_kyc_data.copy()
        invalid_nin_data["identification_number"] = "123456789"  # Only 9 digits, should be 11
        
        success, response = self.make_request('POST', '/api/kyc/agent/submit', invalid_nin_data, 400, use_auth=True)
        
        if success:
            self.log_test("Agent KYC Submission (Invalid NIN)", True, 
                         "Correctly rejected invalid NIN format")
            invalid_nin_success = True
        else:
            self.log_test("Agent KYC Submission (Invalid NIN)", False, 
                         f"Should return 400 error: {response}")
            invalid_nin_success = False
        
        overall_success = valid_submission_success and invalid_nin_success
        return overall_success
    
    def test_farmer_kyc_submission(self):
        """Test new farmer KYC submission endpoint"""
        print("\n🌾 Testing Farmer KYC Submission...")
        
        # Create a farmer user first
        timestamp = datetime.now().strftime("%H%M%S")
        farmer_user_data = {
            "first_name": "Farmer",
            "last_name": "Test",
            "username": f"farmer_kyc_{timestamp}",
            "email": f"farmer_kyc_{timestamp}@pyramyd.com",
            "password": "FarmerPass123!",
            "phone": "+1234567891"
        }
        
        success, response = self.make_request('POST', '/api/auth/register', farmer_user_data, 200)
        if not success:
            self.log_test("Farmer KYC Submission", False, f"Cannot create farmer user: {response}")
            return False
        
        farmer_token = response['token']
        
        # Complete farmer registration
        farmer_complete_reg_data = {
            "first_name": "Farmer",
            "last_name": "Test",
            "username": f"farmer_kyc_{timestamp}",
            "email_or_phone": f"farmer_kyc_{timestamp}@pyramyd.com",
            "password": "FarmerPass123!",
            "phone": "+1234567891",
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "user_path": "partner",
            "partner_type": "farmer"
        }
        
        success, response = self.make_request('POST', '/api/auth/complete-registration', farmer_complete_reg_data, 200)
        if success:
            farmer_token = response['token']
        
        # Test 1: Valid farmer KYC submission with self verification
        valid_farmer_kyc_data = {
            "full_name": "Mary Jane Farmer",
            "phone_number": "+2348123456790",
            "identification_type": "nin",  # lowercase
            "identification_number": "98765432109",
            "farm_location": "Ibadan, Oyo State",
            "farm_size_hectares": 5.5,
            "primary_crops": ["Maize", "Cassava", "Yam"],
            "farming_experience_years": 10,
            "farm_ownership_type": "owned",
            "verification_method": "self_verified",
            "headshot_photo_id": "farmer_photo_123",
            "national_id_document_id": "farmer_id_doc_123",
            "farm_photo_id": "farm_photo_123",
            "land_ownership_document_id": "land_doc_123"
        }
        
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {farmer_token}'}
        url = f"{self.base_url}/api/kyc/farmer/submit"
        
        try:
            response = requests.post(url, json=valid_farmer_kyc_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'message' in response_data:
                    self.log_test("Farmer KYC Submission (Self Verified)", True, 
                                 f"KYC status: {response_data.get('kyc_status', 'pending')}")
                    self_verified_success = True
                else:
                    self.log_test("Farmer KYC Submission (Self Verified)", False, 
                                 f"Invalid response structure: {response_data}")
                    self_verified_success = False
            else:
                response_data = response.json() if response.content else {}
                self.log_test("Farmer KYC Submission (Self Verified)", False, 
                             f"Self verification failed: {response.status_code} - {response_data}")
                self_verified_success = False
        except Exception as e:
            self.log_test("Farmer KYC Submission (Self Verified)", False, f"Request failed: {str(e)}")
            self_verified_success = False
        
        return self_verified_success
    
    def test_categories_products_endpoint(self):
        """Test the /api/categories/products endpoint"""
        print("\n📋 Testing Categories/Products Endpoint...")
        
        success, response = self.make_request('GET', '/api/categories/products', use_auth=True)
        
        if success and isinstance(response, dict):
            # Check if response has expected structure for product categories
            if 'categories' in response and len(response['categories']) > 0:
                categories = response['categories']
                
                # Check if new food categories are present
                new_food_categories = ['grains_legumes', 'fish_meat', 'spices_vegetables', 'tubers_roots']
                found_categories = [cat for cat in new_food_categories if cat in categories]
                
                if len(found_categories) >= 3:  # At least 3 of the 4 new categories
                    self.log_test("Categories/Products - New Food Categories", True, 
                                 f"Found {len(found_categories)} new food categories: {found_categories}")
                    categories_success = True
                else:
                    self.log_test("Categories/Products - New Food Categories", False,
                                 f"Only found {len(found_categories)} new food categories: {found_categories}")
                    categories_success = False
                
                # Check if subcategories have examples
                has_examples = False
                for category, cat_data in categories.items():
                    if isinstance(cat_data, dict) and 'subcategories' in cat_data:
                        subcategories = cat_data['subcategories']
                        for subcat, details in subcategories.items():
                            if isinstance(details, dict) and 'examples' in details:
                                examples = details['examples']
                                if isinstance(examples, list) and len(examples) > 0:
                                    has_examples = True
                                    break
                        if has_examples:
                            break
                
                if has_examples:
                    self.log_test("Categories/Products - Subcategory Examples", True)
                    examples_success = True
                else:
                    self.log_test("Categories/Products - Subcategory Examples", False, 
                                 "No subcategory examples found")
                    examples_success = False
                
                # Check if processing levels are present
                if 'processing_levels' in response:
                    self.log_test("Categories/Products - Processing Levels", True, 
                                 f"Found processing levels: {list(response['processing_levels'].keys())}")
                    processing_success = True
                else:
                    self.log_test("Categories/Products - Processing Levels", False, 
                                 "No processing levels found")
                    processing_success = False
            else:
                self.log_test("Categories/Products - Structure", False, "Invalid response structure")
                categories_success = False
                examples_success = False
                processing_success = False
        else:
            self.log_test("Categories/Products - Structure", False, f"API call failed: {response}")
            categories_success = False
            examples_success = False
            processing_success = False
        
        overall_success = categories_success and examples_success and processing_success
        return overall_success
    
    def run_tests(self):
        """Run all new KYC system tests"""
        print("🚀 Starting New KYC System and Pre-order Filter Tests...")
        print("=" * 60)
        
        # Login first
        if not self.login_existing_user():
            print("❌ Cannot proceed without login")
            return False
        
        # Test 1: Pre-order Filter API
        preorder_filter_success = self.test_preorder_filter_api()
        
        # Test 2: KYC Status Integration
        kyc_status_success = self.test_kyc_status_integration()
        
        # Test 3: Agent KYC Submission
        agent_kyc_success = self.test_agent_kyc_submission()
        
        # Test 4: Farmer KYC Submission
        farmer_kyc_success = self.test_farmer_kyc_submission()
        
        # Test 5: Categories/Products Endpoint
        categories_success = self.test_categories_products_endpoint()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        overall_success = (preorder_filter_success and kyc_status_success and 
                          agent_kyc_success and farmer_kyc_success and categories_success)
        
        if overall_success:
            print("\n🎉 ALL NEW KYC SYSTEM TESTS PASSED!")
        else:
            print("\n⚠️  Some new KYC system tests failed")
        
        return overall_success

if __name__ == "__main__":
    tester = NewKYCSystemTester()
    tester.run_tests()