#!/usr/bin/env python3
"""
Focused Drop-off Location Testing for Pyramyd Agritech Platform
Tests all drop-off location endpoints and functionality
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class DropoffLocationTester:
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

    def test_existing_user_login(self):
        """Test login with existing test user testagent@pyramyd.com"""
        login_data = {
            "email_or_phone": "testagent@pyramyd.com",
            "password": "password123"
        }

        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']  # Update token for further tests
            self.user_id = response['user']['id']
            self.log_test("Existing User Login (testagent@pyramyd.com)", True)
            return True
        else:
            self.log_test("Existing User Login (testagent@pyramyd.com)", False, f"Login failed: {response}")
            return False

    def test_complete_registration_agent(self):
        """Test complete registration flow for agent"""
        timestamp = datetime.now().strftime("%H%M%S")
        registration_data = {
            "first_name": "Agent",
            "last_name": "Test",
            "username": f"agent_dropoff_{timestamp}",
            "email_or_phone": f"agent_dropoff_{timestamp}@pyramyd.com",
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

    def test_dropoff_location_creation(self):
        """Test drop-off location creation with validation"""
        print("\n📍 Testing Drop-off Location Creation...")
        
        # Test 1: Valid drop-off location creation
        valid_location_data = {
            "name": "Central Market Drop-off Point",
            "address": "123 Central Market Street, Victoria Island",
            "city": "Lagos",
            "state": "Lagos State",
            "country": "Nigeria",
            "coordinates": {"lat": 6.4281, "lng": 3.4219},
            "contact_person": "John Doe",
            "contact_phone": "+234-801-234-5678",
            "operating_hours": "8:00 AM - 6:00 PM",
            "description": "Convenient drop-off point at Central Market for easy pickup"
        }

        success, response = self.make_request('POST', '/api/dropoff-locations', valid_location_data, 200, use_auth=True)
        
        if success and 'location_id' in response:
            self.log_test("Drop-off Location Creation (Valid)", True)
            location_id = response['location_id']
            valid_creation_success = True
        else:
            self.log_test("Drop-off Location Creation (Valid)", False, f"Valid location creation failed: {response}")
            location_id = None
            valid_creation_success = False

        # Test 2: Invalid name (too short)
        invalid_name_data = valid_location_data.copy()
        invalid_name_data["name"] = "AB"  # Less than 3 characters

        success, response = self.make_request('POST', '/api/dropoff-locations', invalid_name_data, 422, use_auth=True)
        
        if success:  # Should return 422 validation error
            self.log_test("Drop-off Location Creation (Invalid Name)", True)
            name_validation_success = True
        else:
            self.log_test("Drop-off Location Creation (Invalid Name)", False, f"Should return 422 error: {response}")
            name_validation_success = False

        # Test 3: Invalid address (too short)
        invalid_address_data = valid_location_data.copy()
        invalid_address_data["address"] = "123"  # Less than 5 characters

        success, response = self.make_request('POST', '/api/dropoff-locations', invalid_address_data, 422, use_auth=True)
        
        if success:  # Should return 422 validation error
            self.log_test("Drop-off Location Creation (Invalid Address)", True)
            address_validation_success = True
        else:
            self.log_test("Drop-off Location Creation (Invalid Address)", False, f"Should return 422 error: {response}")
            address_validation_success = False

        # Test 4: Test with minimal required fields
        minimal_location_data = {
            "name": "Minimal Drop-off Point",
            "address": "456 Simple Street, Ikeja",
            "city": "Lagos",
            "state": "Lagos State"
        }

        success, response = self.make_request('POST', '/api/dropoff-locations', minimal_location_data, 200, use_auth=True)
        
        if success and 'location_id' in response:
            self.log_test("Drop-off Location Creation (Minimal Fields)", True)
            minimal_location_id = response['location_id']
            minimal_creation_success = True
        else:
            self.log_test("Drop-off Location Creation (Minimal Fields)", False, f"Minimal location creation failed: {response}")
            minimal_location_id = None
            minimal_creation_success = False

        overall_success = (valid_creation_success and name_validation_success and 
                          address_validation_success and minimal_creation_success)
        
        return overall_success, location_id, minimal_location_id

    def test_dropoff_location_listing(self):
        """Test drop-off location listing with filtering"""
        print("\n📋 Testing Drop-off Location Listing...")
        
        # Test 1: Basic listing
        success, response = self.make_request('GET', '/api/dropoff-locations')
        
        if success and isinstance(response, list):
            self.log_test("Drop-off Location Listing (Basic)", True)
            basic_success = True
        else:
            self.log_test("Drop-off Location Listing (Basic)", False, f"Basic listing failed: {response}")
            basic_success = False

        # Test 2: State filtering
        success, response = self.make_request('GET', '/api/dropoff-locations?state=Lagos State')
        
        if success and isinstance(response, list):
            self.log_test("Drop-off Location Listing (State Filter)", True)
            state_success = True
        else:
            self.log_test("Drop-off Location Listing (State Filter)", False, f"State filtering failed: {response}")
            state_success = False

        # Test 3: City filtering
        success, response = self.make_request('GET', '/api/dropoff-locations?city=Lagos')
        
        if success and isinstance(response, list):
            self.log_test("Drop-off Location Listing (City Filter)", True)
            city_success = True
        else:
            self.log_test("Drop-off Location Listing (City Filter)", False, f"City filtering failed: {response}")
            city_success = False

        overall_success = basic_success and state_success and city_success
        return overall_success

    def test_dropoff_location_my_locations(self):
        """Test getting agent's created locations"""
        print("\n👤 Testing Agent's Drop-off Locations...")
        
        success, response = self.make_request('GET', '/api/dropoff-locations/my-locations', use_auth=True)
        
        if success and isinstance(response, list):
            self.log_test("Agent's Drop-off Locations", True)
            return True, response
        else:
            self.log_test("Agent's Drop-off Locations", False, f"My locations retrieval failed: {response}")
            return False, []

    def test_dropoff_location_details(self, location_id: str):
        """Test getting specific drop-off location details"""
        print(f"\n📄 Testing Drop-off Location Details for {location_id}...")
        
        success, response = self.make_request('GET', f'/api/dropoff-locations/{location_id}')
        
        if success and response.get('id') == location_id:
            # Check required fields
            required_fields = ['id', 'name', 'address', 'city', 'state', 'agent_username', 'is_active']
            if all(field in response for field in required_fields):
                self.log_test("Drop-off Location Details (Valid)", True)
                return True, response
            else:
                self.log_test("Drop-off Location Details (Valid)", False, f"Missing required fields: {response}")
                return False, response
        else:
            self.log_test("Drop-off Location Details (Valid)", False, f"Details retrieval failed: {response}")
            return False, response

    def test_dropoff_location_update(self, location_id: str):
        """Test updating drop-off location (only by creator)"""
        print(f"\n✏️ Testing Drop-off Location Update for {location_id}...")
        
        # Test 1: Valid update
        update_data = {
            "name": "Updated Central Market Drop-off Point",
            "description": "Updated description with new information",
            "operating_hours": "7:00 AM - 7:00 PM"
        }

        success, response = self.make_request('PUT', f'/api/dropoff-locations/{location_id}', update_data, 200, use_auth=True)
        
        if success and response.get('message'):
            self.log_test("Drop-off Location Update (Valid)", True)
            update_success = True
        else:
            self.log_test("Drop-off Location Update (Valid)", False, f"Update failed: {response}")
            update_success = False

        # Test 2: Invalid name (too short)
        invalid_update_data = {
            "name": "AB"  # Less than 3 characters
        }

        success, response = self.make_request('PUT', f'/api/dropoff-locations/{location_id}', invalid_update_data, 422, use_auth=True)
        
        if success:  # Should return 422 validation error
            self.log_test("Drop-off Location Update (Invalid Name)", True)
            validation_success = True
        else:
            self.log_test("Drop-off Location Update (Invalid Name)", False, f"Should return 422 error: {response}")
            validation_success = False

        overall_success = update_success and validation_success
        return overall_success

    def test_dropoff_location_delete(self, location_id: str):
        """Test soft deleting drop-off location (only by creator)"""
        print(f"\n🗑️ Testing Drop-off Location Delete for {location_id}...")
        
        # Test 1: Valid delete (soft delete)
        success, response = self.make_request('DELETE', f'/api/dropoff-locations/{location_id}', use_auth=True)
        
        if success and response.get('message'):
            self.log_test("Drop-off Location Delete (Valid)", True)
            delete_success = True
        else:
            self.log_test("Drop-off Location Delete (Valid)", False, f"Delete failed: {response}")
            delete_success = False

        return delete_success

    def test_states_cities_endpoint(self):
        """Test states and cities endpoint for location management"""
        print("\n🗺️ Testing States and Cities Endpoint...")
        
        success, response = self.make_request('GET', '/api/dropoff-locations/states-cities')
        
        if success and isinstance(response, dict):
            # Check if it has states data
            if 'states' in response or len(response) > 0:
                self.log_test("States and Cities Endpoint", True)
                return True
            else:
                self.log_test("States and Cities Endpoint", False, f"Empty or invalid response: {response}")
                return False
        else:
            # Try alternative endpoint if the first one fails
            success2, response2 = self.make_request('GET', '/api/states-cities')
            if success2 and isinstance(response2, dict):
                if 'states' in response2 or len(response2) > 0:
                    self.log_test("States and Cities Endpoint", True)
                    return True
                else:
                    self.log_test("States and Cities Endpoint", False, f"Empty response from both endpoints: {response}, {response2}")
                    return False
            else:
                self.log_test("States and Cities Endpoint", False, f"Both endpoints failed: {response}, {response2}")
                return False

    def run_dropoff_tests(self):
        """Run all drop-off location tests"""
        print("🚀 Starting Drop-off Location Testing...")
        print("=" * 60)
        
        # Try existing user login first
        existing_login_success = self.test_existing_user_login()
        
        # If existing user doesn't work or doesn't have proper role, create agent user
        if not existing_login_success:
            print("ℹ️  Existing user login failed, creating new agent user...")
            agent_reg_success, agent_data = self.test_complete_registration_agent()
            if not agent_reg_success:
                print("❌ Agent registration failed - stopping tests")
                return False
        else:
            # Try to create a location to test if user has proper role
            test_location_data = {
                "name": "Test Location",
                "address": "Test Address 123",
                "city": "Lagos",
                "state": "Lagos State"
            }
            test_success, test_response = self.make_request('POST', '/api/dropoff-locations', test_location_data, 200, use_auth=True)
            if not test_success and 'Only agents and sellers can create drop-off locations' in str(test_response):
                print("ℹ️  Existing user doesn't have proper role, creating new agent user...")
                agent_reg_success, agent_data = self.test_complete_registration_agent()
                if not agent_reg_success:
                    print("❌ Agent registration failed - stopping tests")
                    return False
            else:
                # Clean up test location if it was created
                if test_success and 'location_id' in test_response:
                    self.make_request('DELETE', f'/api/dropoff-locations/{test_response["location_id"]}', use_auth=True)
        
        # Step 1: Create drop-off locations
        creation_success, location_id, minimal_location_id = self.test_dropoff_location_creation()
        
        # Step 2: Test listing with filtering
        listing_success = self.test_dropoff_location_listing()
        
        # Step 3: Test agent's locations
        my_locations_success, my_locations = self.test_dropoff_location_my_locations()
        
        # Step 4: Test location details
        if location_id:
            details_success, location_details = self.test_dropoff_location_details(location_id)
        else:
            details_success = False
        
        # Step 5: Test location update
        if location_id:
            update_success = self.test_dropoff_location_update(location_id)
        else:
            update_success = False
        
        # Step 6: Test states/cities endpoint
        states_cities_success = self.test_states_cities_endpoint()
        
        # Step 7: Test location deletion (using minimal location to preserve main location)
        if minimal_location_id:
            delete_success = self.test_dropoff_location_delete(minimal_location_id)
        else:
            delete_success = False
        
        overall_success = (creation_success and listing_success and my_locations_success and 
                          details_success and update_success and states_cities_success and 
                          delete_success)
        
        if overall_success:
            self.log_test("Complete Drop-off Location System", True, 
                         "All drop-off location functionality working correctly")
        else:
            self.log_test("Complete Drop-off Location System", False, 
                         "One or more drop-off location components failed")
        
        return overall_success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 DROP-OFF LOCATION TEST SUMMARY")
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
            print("   ✅ Drop-off Location API is mostly functional")
        else:
            print("   ⚠️  Drop-off Location API has significant issues")

        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = DropoffLocationTester()
    
    try:
        success = tester.run_dropoff_tests()
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