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
    def __init__(self, base_url: str = "https://f85d82b5-c3d9-4b5c-ac39-13c8f9f753c8.preview.emergentagent.com"):
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
        success, response = self.make_request('GET', '/api/users/search?username=te', use_auth=True)
        
        if success and isinstance(response, list):
            self.log_test("Messaging User Search (2 chars)", True)
            search_2_success = True
        else:
            self.log_test("Messaging User Search (2 chars)", False, f"User search failed: {response}")
            search_2_success = False

        # Test with less than 2 characters (should fail)
        success, response = self.make_request('GET', '/api/users/search?username=t', use_auth=True, expected_status=400)
        
        if success:  # Should return 400 error
            self.log_test("Messaging User Search (1 char - validation)", True)
            validation_success = True
        else:
            self.log_test("Messaging User Search (1 char - validation)", False, f"Should return 400 error: {response}")
            validation_success = False

        # Test case sensitivity and partial matches
        success, response = self.make_request('GET', '/api/users/search?username=TEST', use_auth=True)
        
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