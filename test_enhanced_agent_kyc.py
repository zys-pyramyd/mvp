#!/usr/bin/env python3
"""
Enhanced Agent KYC Validation Testing
Tests the enhanced KYC compliance validations specifically for agents
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class EnhancedAgentKYCTester:
    def __init__(self, base_url: str = "https://pyramyd-markets.preview.emergentagent.com"):
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

    def test_enhanced_agent_kyc_validation(self):
        """Test enhanced KYC compliance validations specifically for agents"""
        print("\n🔐 Testing Enhanced Agent KYC Validation...")
        
        # Create test agent users with different KYC statuses
        timestamp = datetime.now().strftime("%H%M%S")
        
        # Test Agent 1: KYC not started
        agent_not_started = {
            "first_name": "Agent",
            "last_name": "NotStarted",
            "username": f"agent_not_started_{timestamp}",
            "email_or_phone": f"agent_not_started_{timestamp}@pyramyd.com",
            "password": "AgentPass123!",
            "phone": "+1234567890",
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "user_path": "partner",
            "partner_type": "agent",
            "business_info": {
                "business_name": "Test Agent Business Not Started",
                "business_address": "Test Address"
            }
        }
        
        # Register agent with KYC not started
        success, response = self.make_request('POST', '/api/auth/complete-registration', agent_not_started, 200)
        if success and 'token' in response:
            agent_not_started_token = response['token']
            agent_not_started_id = response['user']['id']
            self.log_test("Agent Registration (KYC Not Started)", True)
        else:
            self.log_test("Agent Registration (KYC Not Started)", False, f"Registration failed: {response}")
            return False
        
        # Test Agent 2: KYC approved (use existing test agent)
        login_data = {
            "email_or_phone": "testagent@pyramyd.com",
            "password": "password123"
        }
        
        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        if success and 'token' in response:
            agent_approved_token = response['token']
            agent_approved_id = response['user']['id']
            self.log_test("Agent Login (KYC Approved)", True)
        else:
            self.log_test("Agent Login (KYC Approved)", False, f"Login failed: {response}")
            return False
        
        # Test 1: Product Creation with different KYC statuses
        print("\n📦 Testing Product Creation with Enhanced Agent KYC...")
        
        product_data = {
            "title": "Test Product for KYC",
            "description": "Test product for KYC validation",
            "category": "pepper_vegetables",  # Use valid category
            "subcategory": "tomatoes",
            "price_per_unit": 500.0,
            "unit_of_measure": "kg",
            "quantity_available": 100,
            "minimum_order_quantity": 5,
            "location": "Lagos, Nigeria",
            "farm_name": "Test Farm",
            "images": [],
            "platform": "pyhub"
        }
        
        # Test with KYC not started agent
        self.token = agent_not_started_token
        success, response = self.make_request('POST', '/api/products', product_data, 403, use_auth=True)
        if success and response.get('detail', {}).get('error') == 'AGENT_KYC_REQUIRED':
            detail = response.get('detail', {})
            if ('verification_time' in detail and 'access_level' in detail and 
                detail.get('access_level') == 'view_only'):
                self.log_test("Product Creation - Agent KYC Not Started", True, 
                             f"Proper error with verification_time: {detail.get('verification_time')}")
            else:
                self.log_test("Product Creation - Agent KYC Not Started", False, 
                             f"Missing enhanced error fields: {detail}")
        else:
            self.log_test("Product Creation - Agent KYC Not Started", False, 
                         f"Expected AGENT_KYC_REQUIRED error: {response}")
        
        # Test with KYC approved agent (should work)
        self.token = agent_approved_token
        success, response = self.make_request('POST', '/api/products', product_data, 200, use_auth=True)
        if success and 'product_id' in response:
            self.log_test("Product Creation - Agent KYC Approved", True)
            test_product_id = response['product_id']
        else:
            self.log_test("Product Creation - Agent KYC Approved", False, f"Product creation failed: {response}")
            test_product_id = None
        
        # Test 2: Agent Farmer Registration with Enhanced KYC
        print("\n👨‍🌾 Testing Agent Farmer Registration with Enhanced KYC...")
        
        farmer_data = {
            "farmer_name": "Test Farmer",
            "farmer_phone": "+1234567893",
            "farmer_location": "Test Location"
        }
        
        # Test with KYC not started agent
        self.token = agent_not_started_token
        success, response = self.make_request('POST', '/api/agent/farmers/add', farmer_data, 403, use_auth=True)
        if success and response.get('detail', {}).get('error') == 'AGENT_KYC_REQUIRED':
            detail = response.get('detail', {})
            if ('verification_time' in detail and 'access_level' in detail and 
                detail.get('access_level') == 'view_only'):
                self.log_test("Agent Farmer Registration - KYC Not Started", True,
                             f"Proper agent-specific error with access_level: {detail.get('access_level')}")
            else:
                self.log_test("Agent Farmer Registration - KYC Not Started", False,
                             f"Missing enhanced error fields: {detail}")
        else:
            self.log_test("Agent Farmer Registration - KYC Not Started", False,
                         f"Expected AGENT_KYC_REQUIRED error: {response}")
        
        # Test with KYC approved agent (should work)
        self.token = agent_approved_token
        success, response = self.make_request('POST', '/api/agent/farmers/add', farmer_data, 200, use_auth=True)
        if success and 'farmer_id' in response:
            self.log_test("Agent Farmer Registration - KYC Approved", True)
        else:
            self.log_test("Agent Farmer Registration - KYC Approved", False, f"Farmer registration failed: {response}")
        
        # Test 3: Pre-order Creation with Enhanced Agent KYC
        print("\n📦 Testing Pre-order Creation with Enhanced Agent KYC...")
        
        preorder_data = {
            "product_name": "Test Pre-order Product",
            "product_category": "pepper_vegetables",  # Use valid category
            "description": "Test pre-order for KYC validation",
            "total_stock": 100,
            "unit": "kg",
            "price_per_unit": 800.0,
            "partial_payment_percentage": 0.3,
            "location": "Test Location",
            "delivery_date": "2025-03-15T10:00:00Z",
            "business_name": "Test Business",
            "farm_name": "Test Farm",
            "images": []
        }
        
        # Test with KYC not started agent
        self.token = agent_not_started_token
        success, response = self.make_request('POST', '/api/preorders/create', preorder_data, 403, use_auth=True)
        if success and response.get('detail', {}).get('error') == 'AGENT_KYC_REQUIRED':
            detail = response.get('detail', {})
            if ('verification_time' in detail and 'access_level' in detail):
                self.log_test("Pre-order Creation - Agent KYC Not Started", True,
                             f"Proper agent-specific error: {detail.get('message')}")
            else:
                self.log_test("Pre-order Creation - Agent KYC Not Started", False,
                             f"Missing enhanced error fields: {detail}")
        else:
            self.log_test("Pre-order Creation - Agent KYC Not Started", False,
                         f"Expected AGENT_KYC_REQUIRED error: {response}")
        
        # Test with KYC approved agent (should work)
        self.token = agent_approved_token
        success, response = self.make_request('POST', '/api/preorders/create', preorder_data, 200, use_auth=True)
        if success and 'preorder_id' in response:
            self.log_test("Pre-order Creation - Agent KYC Approved", True)
        else:
            self.log_test("Pre-order Creation - Agent KYC Approved", False, f"Pre-order creation failed: {response}")
        
        # Test 4: Verify normal users (non-agent) still work
        print("\n👤 Testing Normal User Product Creation (Should Still Work)...")
        
        # Create a business user (non-agent)
        business_user = {
            "first_name": "Test",
            "last_name": "Business",
            "username": f"test_business_{timestamp}",
            "email_or_phone": f"test_business_{timestamp}@pyramyd.com",
            "password": "BusinessPass123!",
            "phone": "+1234567894",
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "user_path": "partner",
            "partner_type": "business",
            "business_info": {
                "business_name": "Test Business Company",
                "business_address": "Test Address"
            }
        }
        
        success, response = self.make_request('POST', '/api/auth/complete-registration', business_user, 200)
        if success and 'token' in response:
            business_token = response['token']
            self.log_test("Business Registration (Non-Agent)", True)
        else:
            self.log_test("Business Registration (Non-Agent)", False, f"Registration failed: {response}")
            return False
        
        # Test product creation with business user
        self.token = business_token
        success, response = self.make_request('POST', '/api/products', product_data, expected_status=403, use_auth=True)
        if success and response.get('detail', {}).get('error') == 'KYC_REQUIRED':
            self.log_test("Product Creation - Business (Non-Agent)", True, "KYC required for business (expected)")
        elif not success and response.get('detail') == "Not authorized to create products":
            self.log_test("Product Creation - Business (Non-Agent)", True, "Business not authorized (expected)")
        else:
            self.log_test("Product Creation - Business (Non-Agent)", False, f"Unexpected response: {response}")
        
        # Test 5: Test KYC Status Endpoint
        print("\n📋 Testing KYC Status Endpoint...")
        
        # Test with KYC not started agent
        self.token = agent_not_started_token
        success, response = self.make_request('GET', '/api/users/kyc/status', use_auth=True)
        if success and 'kyc_status' in response and 'can_trade' in response:
            if response.get('kyc_status') == 'not_started' and response.get('can_trade') == False:
                self.log_test("KYC Status - Agent Not Started", True)
            else:
                self.log_test("KYC Status - Agent Not Started", False, f"Unexpected status: {response}")
        else:
            self.log_test("KYC Status - Agent Not Started", False, f"KYC status check failed: {response}")
        
        # Test with KYC approved agent
        self.token = agent_approved_token
        success, response = self.make_request('GET', '/api/users/kyc/status', use_auth=True)
        if success and 'kyc_status' in response and 'can_trade' in response:
            self.log_test("KYC Status - Agent Approved", True, f"Status: {response.get('kyc_status')}, Can Trade: {response.get('can_trade')}")
        else:
            self.log_test("KYC Status - Agent Approved", False, f"KYC status check failed: {response}")
        
        print("\n✅ Enhanced Agent KYC Validation Testing Complete")
        return True

    def run_tests(self):
        """Run all enhanced agent KYC validation tests"""
        print("🔐 Starting Enhanced Agent KYC Validation Tests...")
        print("=" * 60)
        
        # Run the enhanced agent KYC validation tests
        self.test_enhanced_agent_kyc_validation()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 TESTING COMPLETE")
        print(f"📊 Results: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"✅ Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print("⚠️  Some tests failed - check details above")
            return False

def main():
    """Main function to run the tests"""
    tester = EnhancedAgentKYCTester()
    success = tester.run_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()