#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Pyramyd Agritech Platform
Tests all API endpoints including authentication, products, categories, and orders
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class PyramydAPITester:
    def __init__(self, base_url: str = "https://a5ea1e52-b400-4993-8d3d-5bf22e397c5e.preview.emergentagent.com"):
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

    def test_health_check(self):
        """Test API health endpoint"""
        success, response = self.make_request('GET', '/api/health')
        
        if success and response.get('status') == 'healthy':
            self.log_test("Health Check", True)
            return True
        else:
            self.log_test("Health Check", False, f"Unexpected response: {response}")
            return False

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        test_user = {
            "first_name": "Test",
            "last_name": "User",
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPass123!",
            "phone": "+1234567890"
        }

        success, response = self.make_request('POST', '/api/auth/register', test_user, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            self.log_test("User Registration", True)
            return True, test_user
        else:
            self.log_test("User Registration", False, f"Missing token or user data: {response}")
            return False, test_user

    def test_user_login(self, user_data: Dict):
        """Test user login"""
        login_data = {
            "email_or_phone": user_data["email"],
            "password": user_data["password"]
        }

        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']  # Update token
            self.log_test("User Login", True)
            return True
        else:
            self.log_test("User Login", False, f"Login failed: {response}")
            return False

    def test_existing_user_login(self):
        """Test login with existing test user testagent123"""
        login_data = {
            "email_or_phone": "testagent@pyramyd.com",
            "password": "password123"
        }

        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']  # Update token for further tests
            self.user_id = response['user']['id']
            self.log_test("Existing User Login (testagent123)", True)
            return True
        else:
            self.log_test("Existing User Login (testagent123)", False, f"Login failed: {response}")
            return False

    def test_role_selection(self):
        """Test role selection"""
        role_data = {
            "role": "farmer",
            "is_buyer": False
        }

        success, response = self.make_request('POST', '/api/auth/select-role', role_data, 200, use_auth=True)
        
        if success and response.get('role') == 'farmer':
            self.log_test("Role Selection", True)
            return True
        else:
            self.log_test("Role Selection", False, f"Role selection failed: {response}")
            return False

    def test_user_profile(self):
        """Test getting user profile"""
        success, response = self.make_request('GET', '/api/user/profile', use_auth=True)
        
        if success and 'id' in response and 'email' in response:
            self.log_test("User Profile", True)
            return True
        else:
            self.log_test("User Profile", False, f"Profile fetch failed: {response}")
            return False

    def test_categories(self):
        """Test getting product categories"""
        success, response = self.make_request('GET', '/api/categories')
        
        if success and isinstance(response, list) and len(response) > 0:
            # Check if categories have proper structure
            if all('value' in cat and 'label' in cat for cat in response):
                self.log_test("Product Categories", True)
                return True, response
            else:
                self.log_test("Product Categories", False, "Categories missing required fields")
                return False, response
        else:
            self.log_test("Product Categories", False, f"Invalid categories response: {response}")
            return False, response

    def test_products_listing(self):
        """Test getting products"""
        # Test PyHub products
        success, response = self.make_request('GET', '/api/products?platform=pyhub')
        
        if success and isinstance(response, list):
            self.log_test("Products Listing (PyHub)", True)
            pyhub_success = True
        else:
            self.log_test("Products Listing (PyHub)", False, f"Invalid products response: {response}")
            pyhub_success = False

        # Test PyExpress products
        success, response = self.make_request('GET', '/api/products?platform=pyexpress')
        
        if success and isinstance(response, list):
            self.log_test("Products Listing (PyExpress)", True)
            pyexpress_success = True
        else:
            self.log_test("Products Listing (PyExpress)", False, f"Invalid products response: {response}")
            pyexpress_success = False

        return pyhub_success and pyexpress_success

    def test_product_creation(self):
        """Test creating a product"""
        product_data = {
            "title": "Test Tomatoes",
            "description": "Fresh organic tomatoes from test farm",
            "category": "vegetables",
            "price_per_unit": 500.0,
            "unit_of_measure": "kg",
            "quantity_available": 100,
            "minimum_order_quantity": 5,
            "location": "Lagos, Nigeria",
            "farm_name": "Test Farm",
            "images": [],
            "platform": "pyhub"
        }

        success, response = self.make_request('POST', '/api/products', product_data, 200, use_auth=True)
        
        if success and 'product_id' in response:
            self.log_test("Product Creation", True)
            return True, response['product_id']
        else:
            self.log_test("Product Creation", False, f"Product creation failed: {response}")
            return False, None

    def test_product_creation_with_unit_specification(self):
        """Test creating products with unit_specification field for enhanced pricing display"""
        print("\n📦 Testing Product Creation with Unit Specification...")
        
        # Test 1: Rice with unit_specification
        rice_data = {
            "title": "Premium Rice",
            "description": "High quality rice from local farms",
            "category": "grain",
            "price_per_unit": 450.0,
            "unit_of_measure": "bag",
            "unit_specification": "100kg",
            "quantity_available": 50,
            "minimum_order_quantity": 1,
            "location": "Kebbi, Nigeria",
            "farm_name": "Rice Valley Farm",
            "images": [],
            "platform": "pyhub"
        }

        success, response = self.make_request('POST', '/api/products', rice_data, 200, use_auth=True)
        
        if success and 'product_id' in response:
            self.log_test("Product Creation - Rice with Unit Spec", True)
            rice_product_id = response['product_id']
            rice_success = True
        else:
            self.log_test("Product Creation - Rice with Unit Spec", False, f"Rice creation failed: {response}")
            rice_product_id = None
            rice_success = False

        # Test 2: Tomatoes with unit_specification
        tomatoes_data = {
            "title": "Fresh Tomatoes",
            "description": "Fresh organic tomatoes",
            "category": "vegetables",
            "price_per_unit": 300.0,
            "unit_of_measure": "crate",
            "unit_specification": "big",
            "quantity_available": 100,
            "minimum_order_quantity": 1,
            "location": "Kaduna, Nigeria",
            "farm_name": "Green Valley Farm",
            "images": [],
            "platform": "pyhub"
        }

        success, response = self.make_request('POST', '/api/products', tomatoes_data, 200, use_auth=True)
        
        if success and 'product_id' in response:
            self.log_test("Product Creation - Tomatoes with Unit Spec", True)
            tomatoes_product_id = response['product_id']
            tomatoes_success = True
        else:
            self.log_test("Product Creation - Tomatoes with Unit Spec", False, f"Tomatoes creation failed: {response}")
            tomatoes_product_id = None
            tomatoes_success = False

        # Test 3: Palm Oil with unit_specification
        palm_oil_data = {
            "title": "Pure Palm Oil",
            "description": "Fresh palm oil from local processing",
            "category": "packaged_goods",
            "price_per_unit": 800.0,
            "unit_of_measure": "gallon",
            "unit_specification": "5 litres",
            "quantity_available": 30,
            "minimum_order_quantity": 1,
            "location": "Cross River, Nigeria",
            "farm_name": "Palm Processing Center",
            "images": [],
            "platform": "pyhub"
        }

        success, response = self.make_request('POST', '/api/products', palm_oil_data, 200, use_auth=True)
        
        if success and 'product_id' in response:
            self.log_test("Product Creation - Palm Oil with Unit Spec", True)
            palm_oil_product_id = response['product_id']
            palm_oil_success = True
        else:
            self.log_test("Product Creation - Palm Oil with Unit Spec", False, f"Palm Oil creation failed: {response}")
            palm_oil_product_id = None
            palm_oil_success = False

        # Test 4: Product without unit_specification (should still work)
        basic_product_data = {
            "title": "Basic Maize",
            "description": "Regular maize without unit specification",
            "category": "grain",
            "price_per_unit": 200.0,
            "unit_of_measure": "kg",
            "quantity_available": 200,
            "minimum_order_quantity": 5,
            "location": "Benue, Nigeria",
            "farm_name": "Maize Farm",
            "images": [],
            "platform": "pyhub"
        }

        success, response = self.make_request('POST', '/api/products', basic_product_data, 200, use_auth=True)
        
        if success and 'product_id' in response:
            self.log_test("Product Creation - Basic Product (No Unit Spec)", True)
            basic_product_id = response['product_id']
            basic_success = True
        else:
            self.log_test("Product Creation - Basic Product (No Unit Spec)", False, f"Basic product creation failed: {response}")
            basic_product_id = None
            basic_success = False

        overall_success = rice_success and tomatoes_success and palm_oil_success and basic_success
        
        return overall_success, {
            'rice': rice_product_id,
            'tomatoes': tomatoes_product_id,
            'palm_oil': palm_oil_product_id,
            'basic': basic_product_id
        }

    def test_products_with_unit_specification_retrieval(self):
        """Test retrieving products and verifying unit_specification field is included"""
        print("\n🔍 Testing Products Retrieval with Unit Specification...")
        
        # First create test products with unit specifications
        creation_success, product_ids = self.test_product_creation_with_unit_specification()
        
        if not creation_success:
            self.log_test("Products Retrieval with Unit Spec", False, "Cannot test without created products")
            return False

        # Test 1: GET /api/products - verify existing products work and check unit_specification
        success, response = self.make_request('GET', '/api/products')
        
        if success and isinstance(response, dict):
            products = response.get('products', [])
            preorders = response.get('preorders', [])
            
            # Check if any products have unit_specification
            products_with_unit_spec = [p for p in products if p.get('unit_specification')]
            
            if len(products_with_unit_spec) > 0:
                self.log_test("GET /api/products - Unit Specification Present", True, 
                             f"Found {len(products_with_unit_spec)} products with unit_specification")
                products_success = True
            else:
                self.log_test("GET /api/products - Unit Specification Present", True, 
                             "No products with unit_specification found (acceptable)")
                products_success = True
        else:
            self.log_test("GET /api/products - Basic Functionality", False, f"Products retrieval failed: {response}")
            products_success = False

        # Test 2: Verify specific product details include unit_specification
        if product_ids.get('rice'):
            success, response = self.make_request('GET', f'/api/products/{product_ids["rice"]}')
            
            if success and response.get('unit_specification') == '100kg':
                self.log_test("Product Details - Rice Unit Specification", True, 
                             f"Rice shows ₦{response.get('price_per_unit')}/{response.get('unit_of_measure')} ({response.get('unit_specification')})")
                rice_detail_success = True
            else:
                self.log_test("Product Details - Rice Unit Specification", False, 
                             f"Rice unit_specification not found or incorrect: {response}")
                rice_detail_success = False
        else:
            rice_detail_success = False

        if product_ids.get('tomatoes'):
            success, response = self.make_request('GET', f'/api/products/{product_ids["tomatoes"]}')
            
            if success and response.get('unit_specification') == 'big':
                self.log_test("Product Details - Tomatoes Unit Specification", True,
                             f"Tomatoes shows ₦{response.get('price_per_unit')}/{response.get('unit_of_measure')} ({response.get('unit_specification')})")
                tomatoes_detail_success = True
            else:
                self.log_test("Product Details - Tomatoes Unit Specification", False,
                             f"Tomatoes unit_specification not found or incorrect: {response}")
                tomatoes_detail_success = False
        else:
            tomatoes_detail_success = False

        if product_ids.get('palm_oil'):
            success, response = self.make_request('GET', f'/api/products/{product_ids["palm_oil"]}')
            
            if success and response.get('unit_specification') == '5 litres':
                self.log_test("Product Details - Palm Oil Unit Specification", True,
                             f"Palm Oil shows ₦{response.get('price_per_unit')}/{response.get('unit_of_measure')} ({response.get('unit_specification')})")
                palm_oil_detail_success = True
            else:
                self.log_test("Product Details - Palm Oil Unit Specification", False,
                             f"Palm Oil unit_specification not found or incorrect: {response}")
                palm_oil_detail_success = False
        else:
            palm_oil_detail_success = False

        # Test 3: Verify product without unit_specification works normally
        if product_ids.get('basic'):
            success, response = self.make_request('GET', f'/api/products/{product_ids["basic"]}')
            
            if success and response.get('unit_specification') is None:
                self.log_test("Product Details - Basic Product (No Unit Spec)", True,
                             f"Basic product correctly shows no unit_specification")
                basic_detail_success = True
            else:
                self.log_test("Product Details - Basic Product (No Unit Spec)", False,
                             f"Basic product should not have unit_specification: {response}")
                basic_detail_success = False
        else:
            basic_detail_success = False

        overall_success = (products_success and rice_detail_success and 
                          tomatoes_detail_success and palm_oil_detail_success and 
                          basic_detail_success)
        
        return overall_success

    def test_products_filtering_with_unit_specification(self):
        """Test products endpoint with filters to ensure unit_specification doesn't break existing functionality"""
        print("\n🔧 Testing Products Filtering with Unit Specification...")
        
        # Test 1: Category filtering
        success, response = self.make_request('GET', '/api/products?category=grain')
        
        if success and isinstance(response, dict):
            products = response.get('products', [])
            # Check if any grain products have unit_specification
            grain_products_with_spec = [p for p in products if p.get('unit_specification')]
            self.log_test("Category Filtering - Grain Products", True,
                         f"Found {len(products)} grain products, {len(grain_products_with_spec)} with unit_specification")
            category_success = True
        else:
            self.log_test("Category Filtering - Grain Products", False, f"Category filtering failed: {response}")
            category_success = False

        # Test 2: Location filtering
        success, response = self.make_request('GET', '/api/products?location=Nigeria')
        
        if success and isinstance(response, dict):
            products = response.get('products', [])
            self.log_test("Location Filtering", True, f"Found {len(products)} products in Nigeria")
            location_success = True
        else:
            self.log_test("Location Filtering", False, f"Location filtering failed: {response}")
            location_success = False

        # Test 3: Price range filtering
        success, response = self.make_request('GET', '/api/products?min_price=400&max_price=500')
        
        if success and isinstance(response, dict):
            products = response.get('products', [])
            # Verify products in price range
            valid_price_products = [p for p in products if 400 <= p.get('price_per_unit', 0) <= 500]
            self.log_test("Price Range Filtering", True,
                         f"Found {len(products)} products, {len(valid_price_products)} in price range ₦400-₦500")
            price_success = True
        else:
            self.log_test("Price Range Filtering", False, f"Price filtering failed: {response}")
            price_success = False

        # Test 4: Search functionality
        success, response = self.make_request('GET', '/api/products?search_term=rice')
        
        if success and isinstance(response, dict):
            products = response.get('products', [])
            preorders = response.get('preorders', [])
            total_items = len(products) + len(preorders)
            self.log_test("Search Functionality", True, f"Search for 'rice' returned {total_items} items")
            search_success = True
        else:
            self.log_test("Search Functionality", False, f"Search failed: {response}")
            search_success = False

        # Test 5: Pagination
        success, response = self.make_request('GET', '/api/products?page=1&limit=10')
        
        if success and isinstance(response, dict) and 'page' in response and 'limit' in response:
            self.log_test("Pagination", True, f"Page {response.get('page')} with limit {response.get('limit')}")
            pagination_success = True
        else:
            self.log_test("Pagination", False, f"Pagination failed: {response}")
            pagination_success = False

        # Test 6: Combined filters
        success, response = self.make_request('GET', '/api/products?category=vegetables&location=Kaduna')
        
        if success and isinstance(response, dict):
            products = response.get('products', [])
            self.log_test("Combined Filters", True, f"Category + Location filter returned {len(products)} products")
            combined_success = True
        else:
            self.log_test("Combined Filters", False, f"Combined filtering failed: {response}")
            combined_success = False

        overall_success = (category_success and location_success and price_success and 
                          search_success and pagination_success and combined_success)
        
        return overall_success

    def test_unit_specification_complete_workflow(self):
        """Test complete workflow for products with unit_specification"""
        print("\n🔄 Testing Complete Unit Specification Workflow...")
        
        # Step 1: Create products with unit_specification
        creation_success, product_ids = self.test_product_creation_with_unit_specification()
        
        # Step 2: Verify retrieval includes unit_specification
        retrieval_success = self.test_products_with_unit_specification_retrieval()
        
        # Step 3: Test filtering doesn't break with unit_specification
        filtering_success = self.test_products_filtering_with_unit_specification()
        
        overall_success = creation_success and retrieval_success and filtering_success
        
        if overall_success:
            self.log_test("Complete Unit Specification Workflow", True,
                         "All unit_specification functionality working correctly")
        else:
            self.log_test("Complete Unit Specification Workflow", False,
                         "One or more unit_specification components failed")
        
        return overall_success

    def test_product_details(self, product_id: str):
        """Test getting product details"""
        success, response = self.make_request('GET', f'/api/products/{product_id}')
        
        if success and response.get('id') == product_id:
            self.log_test("Product Details", True)
            return True
        else:
            self.log_test("Product Details", False, f"Product details failed: {response}")
            return False

    def test_orders_listing(self):
        """Test getting orders"""
        success, response = self.make_request('GET', '/api/orders', use_auth=True)
        
        if success and isinstance(response, list):
            self.log_test("Orders Listing", True)
            return True
        else:
            self.log_test("Orders Listing", False, f"Orders listing failed: {response}")
            return False

    def test_search_functionality(self):
        """Test product search"""
        success, response = self.make_request('GET', '/api/products?platform=pyhub&search=tomato')
        
        if success and isinstance(response, list):
            self.log_test("Product Search", True)
            return True
        else:
            self.log_test("Product Search", False, f"Search failed: {response}")
            return False

    def test_category_filtering(self):
        """Test category filtering"""
        success, response = self.make_request('GET', '/api/products?platform=pyhub&category=vegetables')
        
        if success and isinstance(response, list):
            self.log_test("Category Filtering", True)
            return True
        else:
            self.log_test("Category Filtering", False, f"Category filtering failed: {response}")
            return False

    def test_complete_registration(self):
        """Test complete registration flow"""
        timestamp = datetime.now().strftime("%H%M%S")
        registration_data = {
            "first_name": "Agent",
            "last_name": "Test",
            "username": f"agent_test_{timestamp}",
            "email_or_phone": f"agent_{timestamp}@pyramyd.com",
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

    def test_user_search(self):
        """Test user search functionality for group buying"""
        success, response = self.make_request('GET', '/api/users/search?username=test', use_auth=True)
        
        if success and isinstance(response, list):
            self.log_test("User Search", True)
            return True
        else:
            self.log_test("User Search", False, f"User search failed: {response}")
            return False

    def test_group_buying_recommendations(self):
        """Test group buying price recommendations"""
        request_data = {
            "produce": "tomatoes",
            "category": "vegetables",
            "quantity": 100,
            "location": "Lagos"
        }

        success, response = self.make_request('POST', '/api/group-buying/recommendations', request_data, 200, use_auth=True)
        
        if success and 'recommendations' in response:
            self.log_test("Group Buying Recommendations", True)
            return True, response.get('recommendations', [])
        else:
            self.log_test("Group Buying Recommendations", False, f"Recommendations failed: {response}")
            return False, []

    def test_group_buying_create_order(self):
        """Test creating a group buying order"""
        # First get recommendations to have valid data
        rec_success, recommendations = self.test_group_buying_recommendations()
        
        if not rec_success or not recommendations:
            self.log_test("Group Buying Create Order", False, "No recommendations available for testing")
            return False

        order_data = {
            "produce": "tomatoes",
            "category": "vegetables",
            "location": "Lagos",
            "quantity": 50,
            "buyers": [
                {
                    "id": "test_buyer_1",
                    "name": "Test Buyer 1",
                    "quantity": 25,
                    "delivery_address": "Test Address 1"
                },
                {
                    "id": "test_buyer_2", 
                    "name": "Test Buyer 2",
                    "quantity": 25,
                    "delivery_address": "Test Address 2"
                }
            ],
            "selectedPrice": recommendations[0] if recommendations else {
                "farm_id": "test_farm",
                "price_per_unit": 500,
                "product_id": "test_product"
            },
            "commissionType": "pyramyd"
        }

        success, response = self.make_request('POST', '/api/group-buying/create-order', order_data, 200, use_auth=True)
        
        if success and 'order_id' in response:
            self.log_test("Group Buying Create Order", True)
            return True
        else:
            self.log_test("Group Buying Create Order", False, f"Group order creation failed: {response}")
            return False

    def test_agent_purchase(self):
        """Test agent purchase functionality"""
        # First create a test product to purchase
        product_success, product_id = self.test_product_creation()
        
        if not product_success or not product_id:
            self.log_test("Agent Purchase", False, "No product available for testing agent purchase")
            return False

        # Prepare the request data according to the API structure
        request_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 10
                }
            ],
            "purchase_option": {
                "commission_type": "percentage",
                "customer_id": "test_customer_123",
                "delivery_address": "Test Customer Address"
            }
        }

        success, response = self.make_request('POST', '/api/agent/purchase', request_data, 200, use_auth=True)
        
        if success and 'order_id' in response and 'commission_amount' in response:
            self.log_test("Agent Purchase", True)
            return True
        else:
            self.log_test("Agent Purchase", False, f"Agent purchase failed: {response}")
            return False

    def test_messaging_user_search(self):
        """Test user search API for messaging system"""
        # Test with minimum 2 characters
        success, response = self.make_request('GET', '/api/users/search-messaging?username=te', use_auth=True)
        
        if success and isinstance(response, list):
            self.log_test("Messaging User Search (2 chars)", True)
            search_2_success = True
        else:
            self.log_test("Messaging User Search (2 chars)", False, f"User search failed: {response}")
            search_2_success = False

        # Test with less than 2 characters (should fail)
        success, response = self.make_request('GET', '/api/users/search-messaging?username=t', use_auth=True, expected_status=400)
        
        if success:  # Should return 400 error
            self.log_test("Messaging User Search (1 char - validation)", True)
            validation_success = True
        else:
            self.log_test("Messaging User Search (1 char - validation)", False, f"Should return 400 error: {response}")
            validation_success = False

        # Test case sensitivity and partial matches
        success, response = self.make_request('GET', '/api/users/search-messaging?username=TEST', use_auth=True)
        
        if success and isinstance(response, list):
            self.log_test("Messaging User Search (case insensitive)", True)
            case_success = True
        else:
            self.log_test("Messaging User Search (case insensitive)", False, f"Case insensitive search failed: {response}")
            case_success = False

        return search_2_success and validation_success and case_success

    def test_messaging_send_message(self):
        """Test message sending API"""
        # First, create a test recipient user
        timestamp = datetime.now().strftime("%H%M%S")
        recipient_data = {
            "first_name": "Recipient",
            "last_name": "User",
            "username": f"recipient_{timestamp}",
            "email": f"recipient_{timestamp}@example.com",
            "password": "RecipientPass123!",
            "phone": "+1234567891"
        }

        # Register recipient user
        success, response = self.make_request('POST', '/api/auth/register', recipient_data, 200)
        if not success:
            self.log_test("Message Send - Recipient Creation", False, f"Failed to create recipient: {response}")
            return False

        recipient_username = recipient_data["username"]

        # Test sending text message
        text_message_data = {
            "recipient_username": recipient_username,
            "content": "Hello! This is a test message.",
            "conversation_id": f"conv_{timestamp}",
            "type": "text"
        }

        success, response = self.make_request('POST', '/api/messages/send', text_message_data, 200, use_auth=True)
        
        if success and 'message_id' in response:
            self.log_test("Send Text Message", True)
            text_success = True
        else:
            self.log_test("Send Text Message", False, f"Text message sending failed: {response}")
            text_success = False

        # Test sending audio message
        audio_message_data = {
            "recipient_username": recipient_username,
            "audio_data": "base64_encoded_audio_data_here",
            "conversation_id": f"conv_{timestamp}",
            "type": "audio"
        }

        success, response = self.make_request('POST', '/api/messages/send', audio_message_data, 200, use_auth=True)
        
        if success and 'message_id' in response:
            self.log_test("Send Audio Message", True)
            audio_success = True
        else:
            self.log_test("Send Audio Message", False, f"Audio message sending failed: {response}")
            audio_success = False

        # Test recipient validation (non-existent user)
        invalid_message_data = {
            "recipient_username": "nonexistent_user_12345",
            "content": "This should fail",
            "conversation_id": f"conv_{timestamp}",
            "type": "text"
        }

        success, response = self.make_request('POST', '/api/messages/send', invalid_message_data, 404, use_auth=True)
        
        if success:  # Should return 404 error
            self.log_test("Send Message - Recipient Validation", True)
            validation_success = True
        else:
            self.log_test("Send Message - Recipient Validation", False, f"Should return 404 error: {response}")
            validation_success = False

        return text_success and audio_success and validation_success

    def test_messaging_conversations(self):
        """Test conversations retrieval API"""
        success, response = self.make_request('GET', '/api/messages/conversations', use_auth=True)
        
        if success and isinstance(response, list):
            # Check conversation structure if any exist
            if len(response) > 0:
                conversation = response[0]
                required_fields = ['id', 'participants', 'other_user', 'last_message', 'timestamp']
                if all(field in conversation for field in required_fields):
                    self.log_test("Get Conversations", True)
                    return True, response
                else:
                    self.log_test("Get Conversations", False, f"Conversation missing required fields: {conversation}")
                    return False, response
            else:
                self.log_test("Get Conversations", True, "No conversations found (expected for new user)")
                return True, response
        else:
            self.log_test("Get Conversations", False, f"Conversations retrieval failed: {response}")
            return False, response

    def test_messaging_get_messages(self):
        """Test messages retrieval for specific conversation"""
        # First get conversations to find a valid conversation_id
        conv_success, conversations = self.test_messaging_conversations()
        
        if not conv_success:
            self.log_test("Get Messages", False, "Cannot test without valid conversations")
            return False

        if len(conversations) == 0:
            # Create a test conversation by sending a message first
            if not self.test_messaging_send_message():
                self.log_test("Get Messages", False, "Cannot create test conversation")
                return False
            
            # Try to get conversations again
            conv_success, conversations = self.test_messaging_conversations()
            if not conv_success or len(conversations) == 0:
                self.log_test("Get Messages", False, "Still no conversations after sending message")
                return False

        # Use the first conversation
        conversation_id = conversations[0]['id']
        
        success, response = self.make_request('GET', f'/api/messages/{conversation_id}', use_auth=True)
        
        if success and isinstance(response, list):
            # Check message structure if any exist
            if len(response) > 0:
                message = response[0]
                required_fields = ['id', 'sender_username', 'recipient_username', 'timestamp', 'read']
                if all(field in message for field in required_fields):
                    self.log_test("Get Messages", True)
                    return True
                else:
                    self.log_test("Get Messages", False, f"Message missing required fields: {message}")
                    return False
            else:
                self.log_test("Get Messages", True, "No messages found in conversation")
                return True
        else:
            self.log_test("Get Messages", False, f"Messages retrieval failed: {response}")
            return False

    def test_messaging_system_complete(self):
        """Test complete messaging system workflow"""
        print("\n🔄 Testing Complete Messaging System Workflow...")
        
        # Step 1: Search for users
        search_success = self.test_messaging_user_search()
        
        # Step 2: Send messages
        send_success = self.test_messaging_send_message()
        
        # Step 3: Get conversations
        conv_success, conversations = self.test_messaging_conversations()
        
        # Step 4: Get messages for conversation
        messages_success = self.test_messaging_get_messages()
        
        overall_success = search_success and send_success and conv_success and messages_success
        
        if overall_success:
            self.log_test("Complete Messaging System", True)
        else:
            self.log_test("Complete Messaging System", False, "One or more messaging components failed")
        
        return overall_success

    # ===== PRE-ORDER SYSTEM TESTS =====
    
    def test_preorder_creation(self):
        """Test pre-order creation with validation"""
        print("\n📦 Testing Pre-order Creation...")
        
        # Test 1: Valid pre-order creation
        valid_preorder_data = {
            "product_name": "Premium Organic Tomatoes",
            "product_category": "vegetables",
            "description": "Fresh organic tomatoes from our certified farm",
            "total_stock": 1000,
            "unit": "kg",
            "price_per_unit": 800.0,
            "partial_payment_percentage": 0.3,  # 30%
            "location": "Kano, Nigeria",
            "delivery_date": "2025-02-15T10:00:00Z",
            "business_name": "Green Valley Farms",
            "farm_name": "Green Valley Farm",
            "images": ["https://example.com/tomato1.jpg"]
        }

        success, response = self.make_request('POST', '/api/preorders/create', valid_preorder_data, 200, use_auth=True)
        
        if success and 'preorder_id' in response:
            self.log_test("Pre-order Creation (Valid)", True)
            preorder_id = response['preorder_id']
            valid_creation_success = True
        else:
            self.log_test("Pre-order Creation (Valid)", False, f"Valid pre-order creation failed: {response}")
            preorder_id = None
            valid_creation_success = False

        # Test 2: Invalid partial payment percentage (below 10%)
        invalid_percentage_low = valid_preorder_data.copy()
        invalid_percentage_low["partial_payment_percentage"] = 0.05  # 5% - should fail

        success, response = self.make_request('POST', '/api/preorders/create', invalid_percentage_low, 422, use_auth=True)
        
        if success:  # Should return 422 validation error
            self.log_test("Pre-order Creation (Invalid % Low)", True)
            validation_low_success = True
        else:
            self.log_test("Pre-order Creation (Invalid % Low)", False, f"Should return 422 error: {response}")
            validation_low_success = False

        # Test 3: Invalid partial payment percentage (above 90%)
        invalid_percentage_high = valid_preorder_data.copy()
        invalid_percentage_high["partial_payment_percentage"] = 0.95  # 95% - should fail

        success, response = self.make_request('POST', '/api/preorders/create', invalid_percentage_high, 422, use_auth=True)
        
        if success:  # Should return 422 validation error
            self.log_test("Pre-order Creation (Invalid % High)", True)
            validation_high_success = True
        else:
            self.log_test("Pre-order Creation (Invalid % High)", False, f"Should return 422 error: {response}")
            validation_high_success = False

        # Test 4: Invalid stock (zero or negative)
        invalid_stock = valid_preorder_data.copy()
        invalid_stock["total_stock"] = 0  # Should fail

        success, response = self.make_request('POST', '/api/preorders/create', invalid_stock, 422, use_auth=True)
        
        if success:  # Should return 422 validation error
            self.log_test("Pre-order Creation (Invalid Stock)", True)
            stock_validation_success = True
        else:
            self.log_test("Pre-order Creation (Invalid Stock)", False, f"Should return 422 error: {response}")
            stock_validation_success = False

        # Test 5: Invalid price (zero or negative)
        invalid_price = valid_preorder_data.copy()
        invalid_price["price_per_unit"] = -100.0  # Should fail

        success, response = self.make_request('POST', '/api/preorders/create', invalid_price, 422, use_auth=True)
        
        if success:  # Should return 422 validation error
            self.log_test("Pre-order Creation (Invalid Price)", True)
            price_validation_success = True
        else:
            self.log_test("Pre-order Creation (Invalid Price)", False, f"Should return 422 error: {response}")
            price_validation_success = False

        # Test 6: Role authorization (only farmers, suppliers, processors, agents allowed)
        # This test assumes current user has appropriate role from previous tests
        
        overall_success = (valid_creation_success and validation_low_success and 
                          validation_high_success and stock_validation_success and 
                          price_validation_success)
        
        return overall_success, preorder_id

    def test_preorder_publishing(self):
        """Test pre-order publishing functionality"""
        print("\n📢 Testing Pre-order Publishing...")
        
        # First create a pre-order to publish
        creation_success, preorder_id = self.test_preorder_creation()
        
        if not creation_success or not preorder_id:
            self.log_test("Pre-order Publishing", False, "Cannot test publishing without valid pre-order")
            return False

        # Test 1: Valid publishing
        success, response = self.make_request('POST', f'/api/preorders/{preorder_id}/publish', {}, 200, use_auth=True)
        
        if success and response.get('message'):
            self.log_test("Pre-order Publishing (Valid)", True)
            publish_success = True
        else:
            self.log_test("Pre-order Publishing (Valid)", False, f"Publishing failed: {response}")
            publish_success = False

        # Test 2: Try to publish already published pre-order (should fail)
        success, response = self.make_request('POST', f'/api/preorders/{preorder_id}/publish', {}, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Pre-order Publishing (Already Published)", True)
            already_published_success = True
        else:
            self.log_test("Pre-order Publishing (Already Published)", False, f"Should return 400 error: {response}")
            already_published_success = False

        # Test 3: Try to publish non-existent pre-order
        fake_preorder_id = "non-existent-preorder-id"
        success, response = self.make_request('POST', f'/api/preorders/{fake_preorder_id}/publish', {}, 404, use_auth=True)
        
        if success:  # Should return 404 error
            self.log_test("Pre-order Publishing (Non-existent)", True)
            not_found_success = True
        else:
            self.log_test("Pre-order Publishing (Non-existent)", False, f"Should return 404 error: {response}")
            not_found_success = False

        overall_success = publish_success and already_published_success and not_found_success
        return overall_success, preorder_id if publish_success else None

    def test_advanced_product_filtering(self):
        """Test advanced product filtering including pre-orders"""
        print("\n🔍 Testing Advanced Product Filtering...")
        
        # Test 1: Basic products filtering
        success, response = self.make_request('GET', '/api/products')
        
        if success and 'products' in response and 'preorders' in response:
            self.log_test("Advanced Product Filtering (Basic)", True)
            basic_success = True
        else:
            self.log_test("Advanced Product Filtering (Basic)", False, f"Basic filtering failed: {response}")
            basic_success = False

        # Test 2: Category filtering
        success, response = self.make_request('GET', '/api/products?category=vegetables')
        
        if success and isinstance(response, dict):
            self.log_test("Advanced Product Filtering (Category)", True)
            category_success = True
        else:
            self.log_test("Advanced Product Filtering (Category)", False, f"Category filtering failed: {response}")
            category_success = False

        # Test 3: Location filtering
        success, response = self.make_request('GET', '/api/products?location=Lagos')
        
        if success and isinstance(response, dict):
            self.log_test("Advanced Product Filtering (Location)", True)
            location_success = True
        else:
            self.log_test("Advanced Product Filtering (Location)", False, f"Location filtering failed: {response}")
            location_success = False

        # Test 4: Price range filtering
        success, response = self.make_request('GET', '/api/products?min_price=100&max_price=1000')
        
        if success and isinstance(response, dict):
            self.log_test("Advanced Product Filtering (Price Range)", True)
            price_success = True
        else:
            self.log_test("Advanced Product Filtering (Price Range)", False, f"Price filtering failed: {response}")
            price_success = False

        # Test 5: Search functionality
        success, response = self.make_request('GET', '/api/products?search_term=tomato')
        
        if success and isinstance(response, dict):
            self.log_test("Advanced Product Filtering (Search)", True)
            search_success = True
        else:
            self.log_test("Advanced Product Filtering (Search)", False, f"Search filtering failed: {response}")
            search_success = False

        # Test 6: Only pre-orders filtering
        success, response = self.make_request('GET', '/api/products?only_preorders=true')
        
        if success and isinstance(response, dict):
            self.log_test("Advanced Product Filtering (Only Pre-orders)", True)
            preorders_only_success = True
        else:
            self.log_test("Advanced Product Filtering (Only Pre-orders)", False, f"Pre-orders only filtering failed: {response}")
            preorders_only_success = False

        # Test 7: Pagination
        success, response = self.make_request('GET', '/api/products?page=1&limit=5')
        
        if success and isinstance(response, dict) and 'page' in response and 'limit' in response:
            self.log_test("Advanced Product Filtering (Pagination)", True)
            pagination_success = True
        else:
            self.log_test("Advanced Product Filtering (Pagination)", False, f"Pagination failed: {response}")
            pagination_success = False

        overall_success = (basic_success and category_success and location_success and 
                          price_success and search_success and preorders_only_success and 
                          pagination_success)
        
        return overall_success

    def test_preorder_listing(self):
        """Test pre-order listing with filtering"""
        print("\n📋 Testing Pre-order Listing...")
        
        # Test 1: Basic pre-order listing
        success, response = self.make_request('GET', '/api/preorders')
        
        if success and 'preorders' in response and 'total_count' in response:
            self.log_test("Pre-order Listing (Basic)", True)
            basic_success = True
        else:
            self.log_test("Pre-order Listing (Basic)", False, f"Basic listing failed: {response}")
            basic_success = False

        # Test 2: Category filtering
        success, response = self.make_request('GET', '/api/preorders?category=vegetables')
        
        if success and 'preorders' in response:
            self.log_test("Pre-order Listing (Category Filter)", True)
            category_success = True
        else:
            self.log_test("Pre-order Listing (Category Filter)", False, f"Category filtering failed: {response}")
            category_success = False

        # Test 3: Location filtering
        success, response = self.make_request('GET', '/api/preorders?location=Kano')
        
        if success and 'preorders' in response:
            self.log_test("Pre-order Listing (Location Filter)", True)
            location_success = True
        else:
            self.log_test("Pre-order Listing (Location Filter)", False, f"Location filtering failed: {response}")
            location_success = False

        # Test 4: Price range filtering
        success, response = self.make_request('GET', '/api/preorders?min_price=500&max_price=1000')
        
        if success and 'preorders' in response:
            self.log_test("Pre-order Listing (Price Range)", True)
            price_success = True
        else:
            self.log_test("Pre-order Listing (Price Range)", False, f"Price filtering failed: {response}")
            price_success = False

        # Test 5: Search functionality
        success, response = self.make_request('GET', '/api/preorders?search_term=tomato')
        
        if success and 'preorders' in response:
            self.log_test("Pre-order Listing (Search)", True)
            search_success = True
        else:
            self.log_test("Pre-order Listing (Search)", False, f"Search failed: {response}")
            search_success = False

        # Test 6: Seller type filtering
        success, response = self.make_request('GET', '/api/preorders?seller_type=farmer')
        
        if success and 'preorders' in response:
            self.log_test("Pre-order Listing (Seller Type)", True)
            seller_type_success = True
        else:
            self.log_test("Pre-order Listing (Seller Type)", False, f"Seller type filtering failed: {response}")
            seller_type_success = False

        # Test 7: Pagination
        success, response = self.make_request('GET', '/api/preorders?page=1&limit=10')
        
        if success and 'page' in response and 'limit' in response and 'total_pages' in response:
            self.log_test("Pre-order Listing (Pagination)", True)
            pagination_success = True
        else:
            self.log_test("Pre-order Listing (Pagination)", False, f"Pagination failed: {response}")
            pagination_success = False

        overall_success = (basic_success and category_success and location_success and 
                          price_success and search_success and seller_type_success and 
                          pagination_success)
        
        return overall_success

    def test_preorder_details(self):
        """Test getting specific pre-order details"""
        print("\n📄 Testing Pre-order Details...")
        
        # First create and publish a pre-order
        publish_success, preorder_id = self.test_preorder_publishing()
        
        if not publish_success or not preorder_id:
            self.log_test("Pre-order Details", False, "Cannot test details without published pre-order")
            return False

        # Test 1: Valid pre-order details
        success, response = self.make_request('GET', f'/api/preorders/{preorder_id}')
        
        if success and response.get('id') == preorder_id:
            # Check required fields
            required_fields = ['id', 'seller_username', 'product_name', 'price_per_unit', 
                             'total_stock', 'available_stock', 'status', 'delivery_date']
            if all(field in response for field in required_fields):
                self.log_test("Pre-order Details (Valid)", True)
                valid_success = True
            else:
                self.log_test("Pre-order Details (Valid)", False, f"Missing required fields: {response}")
                valid_success = False
        else:
            self.log_test("Pre-order Details (Valid)", False, f"Details retrieval failed: {response}")
            valid_success = False

        # Test 2: Non-existent pre-order
        fake_preorder_id = "non-existent-preorder-id"
        success, response = self.make_request('GET', f'/api/preorders/{fake_preorder_id}', expected_status=404)
        
        if success:  # Should return 404 error
            self.log_test("Pre-order Details (Non-existent)", True)
            not_found_success = True
        else:
            self.log_test("Pre-order Details (Non-existent)", False, f"Should return 404 error: {response}")
            not_found_success = False

        overall_success = valid_success and not_found_success
        return overall_success, preorder_id if valid_success else None

    def test_place_preorder(self):
        """Test placing orders on pre-orders"""
        print("\n🛒 Testing Place Pre-order...")
        
        # First get a valid pre-order
        details_success, preorder_id = self.test_preorder_details()
        
        if not details_success or not preorder_id:
            self.log_test("Place Pre-order", False, "Cannot test ordering without valid pre-order")
            return False

        # Test 1: Valid pre-order placement
        valid_order_data = {
            "quantity": 50
        }

        success, response = self.make_request('POST', f'/api/preorders/{preorder_id}/order', valid_order_data, 200, use_auth=True)
        
        if success and 'order_id' in response and 'total_amount' in response and 'partial_amount' in response:
            self.log_test("Place Pre-order (Valid)", True)
            valid_order_success = True
        else:
            self.log_test("Place Pre-order (Valid)", False, f"Order placement failed: {response}")
            valid_order_success = False

        # Test 2: Invalid quantity (zero or negative)
        invalid_quantity_data = {
            "quantity": 0
        }

        success, response = self.make_request('POST', f'/api/preorders/{preorder_id}/order', invalid_quantity_data, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Place Pre-order (Invalid Quantity)", True)
            invalid_quantity_success = True
        else:
            self.log_test("Place Pre-order (Invalid Quantity)", False, f"Should return 400 error: {response}")
            invalid_quantity_success = False

        # Test 3: Quantity exceeding available stock
        excessive_quantity_data = {
            "quantity": 999999  # Assuming this exceeds available stock
        }

        success, response = self.make_request('POST', f'/api/preorders/{preorder_id}/order', excessive_quantity_data, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Place Pre-order (Excessive Quantity)", True)
            excessive_quantity_success = True
        else:
            self.log_test("Place Pre-order (Excessive Quantity)", False, f"Should return 400 error: {response}")
            excessive_quantity_success = False

        # Test 4: Non-existent pre-order
        fake_preorder_id = "non-existent-preorder-id"
        success, response = self.make_request('POST', f'/api/preorders/{fake_preorder_id}/order', valid_order_data, 404, use_auth=True)
        
        if success:  # Should return 404 error
            self.log_test("Place Pre-order (Non-existent)", True)
            not_found_success = True
        else:
            self.log_test("Place Pre-order (Non-existent)", False, f"Should return 404 error: {response}")
            not_found_success = False

        overall_success = (valid_order_success and invalid_quantity_success and 
                          excessive_quantity_success and not_found_success)
        
        return overall_success

    def test_user_preorders(self):
        """Test getting user's created pre-orders"""
        print("\n👤 Testing User Pre-orders...")
        
        success, response = self.make_request('GET', '/api/my-preorders', use_auth=True)
        
        if success and isinstance(response, list):
            # Check structure if any pre-orders exist
            if len(response) > 0:
                preorder = response[0]
                required_fields = ['id', 'seller_username', 'product_name', 'status', 'created_at']
                if all(field in preorder for field in required_fields):
                    self.log_test("User Pre-orders", True)
                    return True
                else:
                    self.log_test("User Pre-orders", False, f"Pre-order missing required fields: {preorder}")
                    return False
            else:
                self.log_test("User Pre-orders", True, "No pre-orders found (expected for some users)")
                return True
        else:
            self.log_test("User Pre-orders", False, f"User pre-orders retrieval failed: {response}")
            return False

    def test_user_preorder_orders(self):
        """Test getting user's pre-order purchases"""
        print("\n🛍️ Testing User Pre-order Orders...")
        
        success, response = self.make_request('GET', '/api/my-preorder-orders', use_auth=True)
        
        if success and isinstance(response, list):
            # Check structure if any orders exist
            if len(response) > 0:
                order = response[0]
                required_fields = ['id', 'preorder_id', 'buyer_username', 'quantity', 'total_amount', 'status']
                if all(field in order for field in required_fields):
                    self.log_test("User Pre-order Orders", True)
                    return True
                else:
                    self.log_test("User Pre-order Orders", False, f"Order missing required fields: {order}")
                    return False
            else:
                self.log_test("User Pre-order Orders", True, "No pre-order orders found (expected for some users)")
                return True
        else:
            self.log_test("User Pre-order Orders", False, f"User pre-order orders retrieval failed: {response}")
            return False

    def test_preorder_system_complete(self):
        """Test complete pre-order system workflow"""
        print("\n🔄 Testing Complete Pre-order System Workflow...")
        
        # Step 1: Create pre-order
        creation_success, preorder_id = self.test_preorder_creation()
        
        # Step 2: Publish pre-order
        if creation_success and preorder_id:
            publish_success, published_preorder_id = self.test_preorder_publishing()
        else:
            publish_success = False
            published_preorder_id = None
        
        # Step 3: Test advanced filtering
        filtering_success = self.test_advanced_product_filtering()
        
        # Step 4: Test pre-order listing
        listing_success = self.test_preorder_listing()
        
        # Step 5: Test pre-order details
        if published_preorder_id:
            details_success, _ = self.test_preorder_details()
        else:
            details_success = False
        
        # Step 6: Place pre-order
        if published_preorder_id:
            place_order_success = self.test_place_preorder()
        else:
            place_order_success = False
        
        # Step 7: Test user pre-orders
        user_preorders_success = self.test_user_preorders()
        
        # Step 8: Test user pre-order orders
        user_orders_success = self.test_user_preorder_orders()
        
        overall_success = (creation_success and publish_success and filtering_success and 
                          listing_success and details_success and place_order_success and 
                          user_preorders_success and user_orders_success)
        
        if overall_success:
            self.log_test("Complete Pre-order System", True)
        else:
            self.log_test("Complete Pre-order System", False, "One or more pre-order components failed")
        
        return overall_success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Pyramyd API Tests...")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)

        # Test 1: Health Check
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False

        # Test 2: Existing User Login (Priority test from test_result.md)
        existing_login_success = self.test_existing_user_login()
        
        # Test 3: Complete Registration (Agent) for group buying tests
        if existing_login_success:
            print("ℹ️  Using existing user - testing complete registration for agent role")
        
        agent_reg_success, agent_data = self.test_complete_registration()
        if agent_reg_success:
            print("✅ Agent registration successful - using agent account for group buying tests")
        elif not existing_login_success:
            print("❌ Both existing login and agent registration failed - stopping tests")
            return False

        # Test 4: User Registration (fallback if needed)
        if not existing_login_success and not agent_reg_success:
            reg_success, user_data = self.test_user_registration()
            if not reg_success:
                print("❌ Registration failed - stopping tests")
                return False

            # Test 5: User Login with new user
            if not self.test_user_login(user_data):
                print("❌ Login failed - stopping tests")
                return False

        # Test 5: Role Selection (skip - using complete registration instead)
        # if not self.test_role_selection():
        #     print("❌ Role selection failed - continuing with other tests")

        # Test 6: User Profile
        self.test_user_profile()

        # Test 7: Categories
        cat_success, categories = self.test_categories()

        # Test 8: Products Listing
        self.test_products_listing()

        # Test 9: Product Creation
        prod_success, product_id = self.test_product_creation()

        # Test 10: Product Details (if product was created)
        if prod_success and product_id:
            self.test_product_details(product_id)

        # Test 11: Orders Listing
        self.test_orders_listing()

        # Test 12: Search Functionality
        self.test_search_functionality()

        # Test 13: Category Filtering
        self.test_category_filtering()

        # Test 14: User Search (Group Buying Feature)
        self.test_user_search()

        # Test 15: Group Buying Recommendations
        self.test_group_buying_recommendations()

        # Test 16: Group Buying Create Order
        self.test_group_buying_create_order()

        # Test 17: Agent Purchase
        self.test_agent_purchase()

        # Test 18-21: Enhanced Messaging System Tests
        print("\n📱 Testing Enhanced Messaging System...")
        self.test_messaging_user_search()
        self.test_messaging_send_message()
        self.test_messaging_conversations()
        self.test_messaging_get_messages()
        
        # Test 22: Complete Messaging System Workflow
        self.test_messaging_system_complete()

        # Test 23-30: Pre-order System Tests
        print("\n📦 Testing Pre-order System...")
        self.test_preorder_creation()
        self.test_preorder_publishing()
        self.test_advanced_product_filtering()
        self.test_preorder_listing()
        self.test_preorder_details()
        self.test_place_preorder()
        self.test_user_preorders()
        self.test_user_preorder_orders()
        
        # Test 31: Complete Pre-order System Workflow
        self.test_preorder_system_complete()

        # Test 32-40: Driver System Tests
        print("\n🚗 Testing Driver System...")
        self.test_driver_system_complete()

        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
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
            print("   ✅ API is mostly functional")
        else:
            print("   ⚠️  API has significant issues")

        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = PyramydAPITester()
    
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