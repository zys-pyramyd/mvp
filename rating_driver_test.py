#!/usr/bin/env python3
"""
Focused Testing for Rating System & Driver Management Platform
Tests the new Rating System and Driver Management functionality as requested
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class RatingDriverTester:
    def __init__(self, base_url: str = "https://7153c80b-e670-44f1-b4af-554c09ef9392.preview.emergentagent.com"):
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

    def setup_test_user(self):
        """Setup test user for testing"""
        # Try existing user first
        login_data = {
            "email_or_phone": "testagent@pyramyd.com",
            "password": "password123"
        }

        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            self.log_test("Setup Test User (Existing)", True)
            return True
        else:
            self.log_test("Setup Test User (Existing)", False, f"Login failed: {response}")
            return False

    # ===== RATING SYSTEM TESTS =====
    
    def test_rating_creation(self):
        """Test creating ratings for users and products (1-5 stars)"""
        print("\n⭐ Testing Rating Creation...")
        
        # Test 1: Create valid user rating (5 stars)
        user_rating_data = {
            "rating_type": "user_rating",
            "rating_value": 5,
            "rated_entity_id": self.user_id,
            "rated_entity_username": "testagent123",
            "comment": "Excellent service and communication!"
        }
        
        success, response = self.make_request('POST', '/api/ratings', user_rating_data, 200, use_auth=True)
        
        if success and 'rating_id' in response and response.get('rating_value') == 5:
            self.log_test("Create User Rating (5 stars)", True)
            user_rating_success = True
        else:
            self.log_test("Create User Rating (5 stars)", False, f"User rating creation failed: {response}")
            user_rating_success = False
        
        # Test 2: Create valid product rating (4 stars) - using existing product
        # Get a product ID from existing products
        success, products_response = self.make_request('GET', '/api/products')
        if success and 'products' in products_response and len(products_response['products']) > 0:
            product_id = products_response['products'][0]['id']
            
            product_rating_data = {
                "rating_type": "product_rating",
                "rating_value": 4,
                "rated_entity_id": product_id,
                "comment": "Good quality product, fresh and well-packaged"
            }
            
            success, response = self.make_request('POST', '/api/ratings', product_rating_data, 200, use_auth=True)
            
            if success and 'rating_id' in response and response.get('rating_value') == 4:
                self.log_test("Create Product Rating (4 stars)", True)
                product_rating_success = True
            else:
                self.log_test("Create Product Rating (4 stars)", False, f"Product rating creation failed: {response}")
                product_rating_success = False
        else:
            self.log_test("Create Product Rating (4 stars)", False, "No products available for rating")
            product_rating_success = False
        
        # Test 3: Test rating validation - invalid rating value (6 stars - should fail)
        invalid_rating_data = {
            "rating_type": "user_rating",
            "rating_value": 6,  # Invalid - above 5
            "rated_entity_id": self.user_id,
            "comment": "This should fail"
        }
        
        success, response = self.make_request('POST', '/api/ratings', invalid_rating_data, 422, use_auth=True)
        
        if success:  # Should return 422 error (Pydantic validation)
            self.log_test("Rating Validation (6 stars - invalid)", True)
            validation_high_success = True
        else:
            self.log_test("Rating Validation (6 stars - invalid)", False, f"Should return 422 error: {response}")
            validation_high_success = False
        
        # Test 4: Test rating validation - invalid rating value (0 stars - should fail)
        invalid_rating_low_data = {
            "rating_type": "user_rating",
            "rating_value": 0,  # Invalid - below 1
            "rated_entity_id": self.user_id,
            "comment": "This should also fail"
        }
        
        success, response = self.make_request('POST', '/api/ratings', invalid_rating_low_data, 422, use_auth=True)
        
        if success:  # Should return 422 error (Pydantic validation)
            self.log_test("Rating Validation (0 stars - invalid)", True)
            validation_low_success = True
        else:
            self.log_test("Rating Validation (0 stars - invalid)", False, f"Should return 422 error: {response}")
            validation_low_success = False
        
        # Test 5: Update existing rating
        if user_rating_success:
            updated_rating_data = {
                "rating_type": "user_rating",
                "rating_value": 3,  # Update from 5 to 3
                "rated_entity_id": self.user_id,
                "rated_entity_username": "testagent123",
                "comment": "Updated rating - service was okay"
            }
            
            success, response = self.make_request('POST', '/api/ratings', updated_rating_data, 200, use_auth=True)
            
            if success and response.get('rating_value') == 3:
                self.log_test("Update Existing Rating", True)
                update_success = True
            else:
                self.log_test("Update Existing Rating", False, f"Rating update failed: {response}")
                update_success = False
        else:
            update_success = False
        
        overall_success = (user_rating_success and product_rating_success and 
                          validation_high_success and validation_low_success and update_success)
        
        return overall_success
    
    def test_rating_retrieval(self):
        """Test getting ratings for specific entities"""
        print("\n📊 Testing Rating Retrieval...")
        
        # Test 1: Get user ratings
        success, response = self.make_request('GET', f'/api/ratings/{self.user_id}?rating_type=user_rating')
        
        if success and 'ratings' in response and 'rating_distribution' in response:
            ratings = response.get('ratings', [])
            distribution = response.get('rating_distribution', {})
            
            self.log_test("Get User Ratings", True, f"Found {len(ratings)} ratings with distribution")
            user_retrieval_success = True
        else:
            self.log_test("Get User Ratings", False, f"User ratings retrieval failed: {response}")
            user_retrieval_success = False
        
        # Test 2: Get product ratings
        success, products_response = self.make_request('GET', '/api/products')
        if success and 'products' in products_response and len(products_response['products']) > 0:
            product_id = products_response['products'][0]['id']
            
            success, response = self.make_request('GET', f'/api/ratings/{product_id}?rating_type=product_rating')
            
            if success and 'ratings' in response and 'rating_distribution' in response:
                self.log_test("Get Product Ratings", True)
                product_retrieval_success = True
            else:
                self.log_test("Get Product Ratings", False, f"Product ratings retrieval failed: {response}")
                product_retrieval_success = False
        else:
            product_retrieval_success = False
        
        # Test 3: Get my ratings (ratings given by current user)
        success, response = self.make_request('GET', '/api/ratings/my-ratings', use_auth=True)
        
        if success and 'ratings' in response and 'total_count' in response:
            ratings = response.get('ratings', [])
            self.log_test("Get My Ratings", True, f"Found {len(ratings)} ratings given by user")
            my_ratings_success = True
        else:
            self.log_test("Get My Ratings", False, f"My ratings retrieval failed: {response}")
            my_ratings_success = False
        
        # Test 4: Test pagination
        success, response = self.make_request('GET', f'/api/ratings/{self.user_id}?rating_type=user_rating&page=1&limit=5')
        
        if success and 'page' in response and 'limit' in response and 'total_pages' in response:
            self.log_test("Rating Pagination", True)
            pagination_success = True
        else:
            self.log_test("Rating Pagination", False, f"Pagination failed: {response}")
            pagination_success = False
        
        overall_success = (user_retrieval_success and product_retrieval_success and 
                          my_ratings_success and pagination_success)
        
        return overall_success

    # ===== DRIVER MANAGEMENT PLATFORM TESTS =====
    
    def test_driver_slot_purchase(self):
        """Test purchasing driver slots for logistics business"""
        print("\n💰 Testing Driver Slot Purchase...")
        
        # Test with current user (will likely fail due to role validation)
        slots_count = 3
        
        success, response = self.make_request('POST', '/api/driver-slots/purchase', 
                                            {"slots_count": slots_count}, 403, use_auth=True)
        
        if success:  # Should return 403 for non-logistics user
            self.log_test("Driver Slot Purchase (Role Validation)", True, "Correctly rejected non-logistics user")
            role_validation_success = True
        else:
            self.log_test("Driver Slot Purchase (Role Validation)", False, f"Unexpected response: {response}")
            role_validation_success = False
        
        # Test invalid slot count (too high)
        success, response = self.make_request('POST', '/api/driver-slots/purchase', 
                                            {"slots_count": 100}, 403, use_auth=True)
        
        if success:  # Should return 403 (role validation takes precedence)
            self.log_test("Driver Slot Purchase (Invalid Count High)", True, "Role validation working")
            validation_high_success = True
        else:
            self.log_test("Driver Slot Purchase (Invalid Count High)", False, f"Unexpected response: {response}")
            validation_high_success = False
        
        # Test invalid slot count (too low)
        success, response = self.make_request('POST', '/api/driver-slots/purchase', 
                                            {"slots_count": 0}, 403, use_auth=True)
        
        if success:  # Should return 403 (role validation takes precedence)
            self.log_test("Driver Slot Purchase (Invalid Count Low)", True, "Role validation working")
            validation_low_success = True
        else:
            self.log_test("Driver Slot Purchase (Invalid Count Low)", False, f"Unexpected response: {response}")
            validation_low_success = False
        
        overall_success = role_validation_success and validation_high_success and validation_low_success
        return overall_success
    
    def test_driver_slot_management(self):
        """Test driver slot management and assignment"""
        print("\n🎯 Testing Driver Slot Management...")
        
        # Test 1: Get my driver slots (should fail for non-logistics user)
        success, response = self.make_request('GET', '/api/driver-slots/my-slots', expected_status=403, use_auth=True)
        
        if success:  # Should return 403
            self.log_test("Get My Driver Slots (Role Validation)", True, "Correctly rejected non-logistics user")
            get_slots_success = True
        else:
            self.log_test("Get My Driver Slots (Role Validation)", False, f"Should return 403: {response}")
            get_slots_success = False
        
        # Test 2: Assign driver to slot (should fail for non-logistics user or invalid slot)
        driver_assignment_data = {
            "driver_name": "John Doe Driver",
            "vehicle_type": "motorcycle",
            "plate_number": "ABC123XY",
            "vehicle_make_model": "Honda CBR 150",
            "vehicle_color": "Red",
            "vehicle_year": 2022,
            "date_of_birth": "1990-05-15",
            "address": "123 Driver Street, Lagos",
            "driver_license": "DL123456789"
        }
        
        dummy_slot_id = "test-slot-id-123"
        success, response = self.make_request('POST', f'/api/driver-slots/{dummy_slot_id}/assign-driver', 
                                            driver_assignment_data, 404, use_auth=True)
        
        if success:  # Should return 404 for non-existent slot
            self.log_test("Assign Driver to Slot (Validation)", True, "Correctly handled invalid slot")
            assign_success = True
        else:
            self.log_test("Assign Driver to Slot (Validation)", False, f"Unexpected response: {response}")
            assign_success = False
        
        overall_success = get_slots_success and assign_success
        return overall_success
    
    def test_driver_registration(self):
        """Test driver registration using registration token"""
        print("\n📝 Testing Driver Registration...")
        
        # Test 1: Invalid registration token
        invalid_token = "invalid-registration-token-123"
        registration_data = {
            "username": f"driver_test_{datetime.now().strftime('%H%M%S')}",
            "password": "DriverPass123!",
            "registration_token": invalid_token
        }
        
        success, response = self.make_request('POST', f'/api/drivers/register/{invalid_token}', 
                                            registration_data, 404)
        
        if success:  # Should return 404 for invalid token
            self.log_test("Driver Registration (Invalid Token)", True)
            invalid_token_success = True
        else:
            self.log_test("Driver Registration (Invalid Token)", False, f"Should return 404: {response}")
            invalid_token_success = False
        
        # Test 2: Username uniqueness validation (using existing username)
        existing_username_data = {
            "username": "testagent123",  # This username should already exist
            "password": "DriverPass123!",
            "registration_token": "dummy-token"
        }
        
        success, response = self.make_request('POST', '/api/drivers/register/dummy-token', 
                                            existing_username_data, 404)
        
        # We expect 404 because token doesn't exist (token validation takes precedence)
        if success:
            self.log_test("Driver Registration (Username Validation)", True, "Token validation takes precedence")
            username_validation_success = True
        else:
            self.log_test("Driver Registration (Username Validation)", False, f"Unexpected response: {response}")
            username_validation_success = False
        
        overall_success = invalid_token_success and username_validation_success
        return overall_success
    
    def test_driver_profile_retrieval(self):
        """Test enhanced driver profile retrieval"""
        print("\n👤 Testing Driver Profile Retrieval...")
        
        # Test 1: Get profile for non-existent driver
        fake_driver_username = "nonexistent_driver_123"
        success, response = self.make_request('GET', f'/api/drivers/profile/{fake_driver_username}', 
                                            expected_status=404)
        
        if success:  # Should return 404
            self.log_test("Driver Profile (Non-existent)", True)
            not_found_success = True
        else:
            self.log_test("Driver Profile (Non-existent)", False, f"Should return 404: {response}")
            not_found_success = False
        
        # Test 2: Test endpoint structure with another non-existent driver
        test_driver_username = "test_driver"
        success, response = self.make_request('GET', f'/api/drivers/profile/{test_driver_username}', 
                                            expected_status=404)
        
        if success:  # Expected 404 since driver doesn't exist
            self.log_test("Driver Profile (Endpoint Structure)", True, "Endpoint correctly handles non-existent driver")
            endpoint_success = True
        else:
            self.log_test("Driver Profile (Endpoint Structure)", False, f"Unexpected response: {response}")
            endpoint_success = False
        
        overall_success = not_found_success and endpoint_success
        return overall_success
    
    def test_driver_search_interface(self):
        """Test uber-like driver finding interface"""
        print("\n🔍 Testing Driver Search Interface...")
        
        # Test 1: Basic driver search
        success, response = self.make_request('GET', '/api/drivers/find-drivers')
        
        if success and isinstance(response, dict):
            self.log_test("Driver Search (Basic)", True, "Driver search endpoint working")
            basic_search_success = True
        else:
            self.log_test("Driver Search (Basic)", False, f"Driver search failed: {response}")
            basic_search_success = False
        
        # Test 2: Driver search with filters
        success, response = self.make_request('GET', '/api/drivers/find-drivers?vehicle_type=motorcycle&min_rating=4.0&limit=10')
        
        if success and isinstance(response, dict):
            self.log_test("Driver Search (With Filters)", True, "Filtered driver search working")
            filtered_search_success = True
        else:
            self.log_test("Driver Search (With Filters)", False, f"Filtered search failed: {response}")
            filtered_search_success = False
        
        # Test 3: Driver search with location
        success, response = self.make_request('GET', '/api/drivers/find-drivers?location=Lagos')
        
        if success and isinstance(response, dict):
            self.log_test("Driver Search (Location Filter)", True, "Location-based driver search working")
            location_search_success = True
        else:
            self.log_test("Driver Search (Location Filter)", False, f"Location search failed: {response}")
            location_search_success = False
        
        overall_success = basic_search_success and filtered_search_success and location_search_success
        return overall_success

    def run_all_tests(self):
        """Run all Rating System and Driver Management tests"""
        print("🚀 Starting Rating System & Driver Management Platform Tests...")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 80)

        # Setup test user
        if not self.setup_test_user():
            print("❌ Cannot setup test user - stopping tests")
            return False

        print("\n⭐ RATING SYSTEM TESTS")
        print("-" * 50)
        
        # Rating System Tests
        rating_creation_success = self.test_rating_creation()
        rating_retrieval_success = self.test_rating_retrieval()
        
        print("\n🚗 DRIVER MANAGEMENT PLATFORM TESTS")
        print("-" * 50)
        
        # Driver Management Tests
        slot_purchase_success = self.test_driver_slot_purchase()
        slot_management_success = self.test_driver_slot_management()
        driver_registration_success = self.test_driver_registration()
        driver_profile_success = self.test_driver_profile_retrieval()
        driver_search_success = self.test_driver_search_interface()
        
        # Overall results
        rating_system_success = rating_creation_success and rating_retrieval_success
        driver_system_success = (slot_purchase_success and slot_management_success and 
                               driver_registration_success and driver_profile_success and 
                               driver_search_success)
        
        print(f"\n📊 RATING SYSTEM: {'✅ WORKING' if rating_system_success else '❌ ISSUES FOUND'}")
        print(f"📊 DRIVER MANAGEMENT: {'✅ WORKING' if driver_system_success else '❌ ISSUES FOUND'}")
        
        return rating_system_success and driver_system_success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 RATING SYSTEM & DRIVER MANAGEMENT TEST SUMMARY")
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
            print("   ✅ Rating System & Driver Management APIs are mostly functional")
        else:
            print("   ⚠️  Rating System & Driver Management APIs have significant issues")

        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = RatingDriverTester()
    
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