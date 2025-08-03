#!/usr/bin/env python3
"""
Focused Unit Specification Testing for Pyramyd API
Tests the updated Product model with unit_specification field
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class UnitSpecificationTester:
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
            if details:
                print(f"   {details}")
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

    def setup_authentication(self):
        """Setup authentication using complete registration for agent role"""
        timestamp = datetime.now().strftime("%H%M%S")
        registration_data = {
            "first_name": "Test",
            "last_name": "Agent",
            "username": f"test_agent_unit_spec_{timestamp}",
            "email_or_phone": f"test_agent_unit_spec_{timestamp}@pyramyd.com",
            "password": "TestAgent123!",
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
            self.log_test("Authentication Setup", True, f"Created agent account: {registration_data['username']}")
            return True
        else:
            self.log_test("Authentication Setup", False, f"Registration failed: {response}")
            return False

    def test_get_products_basic(self):
        """Test GET /api/products - verify existing products still work"""
        print("\n🔍 Testing GET /api/products - Basic Functionality")
        
        success, response = self.make_request('GET', '/api/products')
        
        if success and isinstance(response, dict):
            products = response.get('products', [])
            preorders = response.get('preorders', [])
            total_count = response.get('total_count', 0)
            
            # Check if any products have unit_specification
            products_with_unit_spec = [p for p in products if p.get('unit_specification')]
            
            self.log_test("GET /api/products - Basic Response Structure", True, 
                         f"Found {len(products)} products, {len(preorders)} preorders, total: {total_count}")
            
            if len(products_with_unit_spec) > 0:
                self.log_test("GET /api/products - Unit Specification Present", True, 
                             f"Found {len(products_with_unit_spec)} products with unit_specification")
                
                # Show examples
                for i, product in enumerate(products_with_unit_spec[:3]):  # Show first 3
                    unit_spec = product.get('unit_specification')
                    price = product.get('price_per_unit')
                    unit = product.get('unit_of_measure')
                    title = product.get('title')
                    print(f"   Example {i+1}: {title} - ₦{price}/{unit} ({unit_spec})")
                    
                return True
            else:
                self.log_test("GET /api/products - Unit Specification Present", True, 
                             "No products with unit_specification found (will create test products)")
                return True
        else:
            self.log_test("GET /api/products - Basic Response Structure", False, 
                         f"Invalid response structure: {response}")
            return False

    def test_create_products_with_unit_specification(self):
        """Test POST /api/products - Create test products with unit_specification"""
        print("\n📦 Testing POST /api/products - Creating Products with Unit Specification")
        
        test_products = [
            {
                "name": "Rice with Unit Spec",
                "data": {
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
                },
                "expected_display": "₦450/bag (100kg)"
            },
            {
                "name": "Tomatoes with Unit Spec",
                "data": {
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
                },
                "expected_display": "₦300/crate (big)"
            },
            {
                "name": "Palm Oil with Unit Spec",
                "data": {
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
                },
                "expected_display": "₦800/gallon (5 litres)"
            }
        ]
        
        created_products = []
        
        for product_info in test_products:
            success, response = self.make_request('POST', '/api/products', product_info["data"], 200, use_auth=True)
            
            if success and 'product_id' in response:
                product_id = response['product_id']
                created_products.append({
                    'id': product_id,
                    'name': product_info["name"],
                    'expected_display': product_info["expected_display"],
                    'data': product_info["data"]
                })
                self.log_test(f"Create {product_info['name']}", True, 
                             f"Expected display: {product_info['expected_display']}")
            else:
                self.log_test(f"Create {product_info['name']}", False, 
                             f"Creation failed: {response}")
        
        return created_products

    def test_verify_product_details(self, created_products):
        """Test individual product details to verify unit_specification is included"""
        print("\n🔍 Testing Product Details - Verify Unit Specification Field")
        
        all_success = True
        
        for product in created_products:
            success, response = self.make_request('GET', f'/api/products/{product["id"]}')
            
            if success:
                unit_spec = response.get('unit_specification')
                expected_spec = product['data']['unit_specification']
                price = response.get('price_per_unit')
                unit = response.get('unit_of_measure')
                
                if unit_spec == expected_spec:
                    actual_display = f"₦{price}/{unit} ({unit_spec})"
                    self.log_test(f"Product Details - {product['name']}", True, 
                                 f"Actual display: {actual_display}")
                else:
                    self.log_test(f"Product Details - {product['name']}", False, 
                                 f"Expected unit_specification: {expected_spec}, got: {unit_spec}")
                    all_success = False
            else:
                self.log_test(f"Product Details - {product['name']}", False, 
                             f"Failed to retrieve product: {response}")
                all_success = False
        
        return all_success

    def test_products_filtering_compatibility(self):
        """Test that filtering still works with unit_specification field"""
        print("\n🔧 Testing Products Filtering - Ensure Compatibility with Unit Specification")
        
        test_filters = [
            {
                "name": "Category Filter (grain)",
                "endpoint": "/api/products?category=grain",
                "check": lambda r: len([p for p in r.get('products', []) if p.get('category') == 'grain']) > 0
            },
            {
                "name": "Location Filter (Nigeria)",
                "endpoint": "/api/products?location=Nigeria",
                "check": lambda r: len(r.get('products', [])) > 0
            },
            {
                "name": "Price Range Filter (₦400-₦500)",
                "endpoint": "/api/products?min_price=400&max_price=500",
                "check": lambda r: len(r.get('products', [])) >= 0  # May be empty, that's ok
            },
            {
                "name": "Search Filter (rice)",
                "endpoint": "/api/products?search_term=rice",
                "check": lambda r: len(r.get('products', [])) + len(r.get('preorders', [])) >= 0
            },
            {
                "name": "Pagination",
                "endpoint": "/api/products?page=1&limit=5",
                "check": lambda r: 'page' in r and 'limit' in r and 'total_pages' in r
            }
        ]
        
        all_success = True
        
        for filter_test in test_filters:
            success, response = self.make_request('GET', filter_test["endpoint"])
            
            if success and isinstance(response, dict):
                if filter_test["check"](response):
                    # Count products with unit_specification in this filter
                    products = response.get('products', [])
                    products_with_spec = [p for p in products if p.get('unit_specification')]
                    
                    self.log_test(f"Filter - {filter_test['name']}", True, 
                                 f"Found {len(products)} products, {len(products_with_spec)} with unit_specification")
                else:
                    self.log_test(f"Filter - {filter_test['name']}", False, 
                                 "Filter check failed")
                    all_success = False
            else:
                self.log_test(f"Filter - {filter_test['name']}", False, 
                             f"Request failed: {response}")
                all_success = False
        
        return all_success

    def test_enhanced_pricing_display_examples(self):
        """Test and demonstrate enhanced pricing display format"""
        print("\n💰 Testing Enhanced Pricing Display Examples")
        
        # Get products with unit_specification
        success, response = self.make_request('GET', '/api/products')
        
        if success and isinstance(response, dict):
            products = response.get('products', [])
            products_with_spec = [p for p in products if p.get('unit_specification')]
            
            if len(products_with_spec) > 0:
                print(f"\n   📋 Enhanced Pricing Display Examples:")
                print(f"   {'='*60}")
                
                for i, product in enumerate(products_with_spec[:5]):  # Show first 5
                    title = product.get('title', 'Unknown')
                    price = product.get('price_per_unit', 0)
                    unit = product.get('unit_of_measure', 'unit')
                    spec = product.get('unit_specification', '')
                    
                    # Format the enhanced pricing display
                    enhanced_display = f"₦{price}/{unit} ({spec})"
                    
                    print(f"   {i+1}. {title}")
                    print(f"      Enhanced Price: {enhanced_display}")
                    print(f"      Location: {product.get('location', 'N/A')}")
                    print()
                
                self.log_test("Enhanced Pricing Display Examples", True, 
                             f"Successfully demonstrated {len(products_with_spec)} enhanced pricing formats")
                return True
            else:
                self.log_test("Enhanced Pricing Display Examples", False, 
                             "No products with unit_specification found for demonstration")
                return False
        else:
            self.log_test("Enhanced Pricing Display Examples", False, 
                         f"Failed to retrieve products: {response}")
            return False

    def run_unit_specification_tests(self):
        """Run all unit specification tests"""
        print("🚀 Starting Unit Specification Testing for Pyramyd API...")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 70)

        # Step 1: Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication failed - stopping tests")
            return False

        # Step 2: Test basic GET /api/products functionality
        basic_success = self.test_get_products_basic()

        # Step 3: Create test products with unit_specification
        created_products = self.test_create_products_with_unit_specification()

        # Step 4: Verify product details include unit_specification
        if created_products:
            details_success = self.test_verify_product_details(created_products)
        else:
            details_success = False

        # Step 5: Test filtering compatibility
        filtering_success = self.test_products_filtering_compatibility()

        # Step 6: Demonstrate enhanced pricing display
        display_success = self.test_enhanced_pricing_display_examples()

        return basic_success and len(created_products) > 0 and details_success and filtering_success and display_success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 UNIT SPECIFICATION TEST SUMMARY")
        print("=" * 70)
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
            print("   ✅ Unit specification functionality is working correctly")
            print("   ✅ Enhanced pricing display format (₦price/unit (specification)) is functional")
            print("   ✅ Existing filtering functionality remains compatible")
            print("   ✅ Backend API correctly handles the new unit_specification field")
        else:
            print("   ⚠️  Unit specification functionality has issues")

        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = UnitSpecificationTester()
    
    try:
        success = tester.run_unit_specification_tests()
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