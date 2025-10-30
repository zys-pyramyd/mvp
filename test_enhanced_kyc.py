#!/usr/bin/env python3
"""
Enhanced KYC System & User Dashboards Testing
Tests all the new Enhanced KYC functionality as requested
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class EnhancedKYCTester:
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

    def setup_authentication(self):
        """Setup authentication with existing user"""
        print("🔐 Setting up authentication...")
        
        # Try to login with existing test user
        login_data = {
            "email_or_phone": "testagent@pyramyd.com",
            "password": "password123"
        }

        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            self.log_test("Authentication Setup", True)
            return True
        else:
            self.log_test("Authentication Setup", False, f"Login failed: {response}")
            return False

    def create_farmer_user(self):
        """Create a farmer user for testing"""
        print("🚜 Creating farmer user for testing...")
        
        farmer_data = {
            "first_name": "Test",
            "last_name": "Farmer",
            "username": f"testfarmer_kyc_{datetime.now().strftime('%H%M%S')}",
            "email_or_phone": f"testfarmer_kyc_{datetime.now().strftime('%H%M%S')}@test.com",
            "phone": "+2348012345678",
            "password": "password123",
            "gender": "male",
            "date_of_birth": "1990-01-01",
            "user_path": "partner",
            "partner_type": "farmer",
            "business_info": {
                "farm_name": "Test KYC Farm",
                "location": "Lagos, Nigeria"
            }
        }
        
        success, response = self.make_request('POST', '/api/auth/complete-registration', farmer_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.log_test("Create Farmer User", True)
            return response['token'], response['user']['id']
        else:
            self.log_test("Create Farmer User", False, f"Farmer creation failed: {response}")
            return None, None

    def create_agent_user(self):
        """Create an agent user for testing"""
        print("🤝 Creating agent user for testing...")
        
        agent_data = {
            "first_name": "Test",
            "last_name": "Agent",
            "username": f"testagent_kyc_{datetime.now().strftime('%H%M%S')}",
            "email_or_phone": f"testagent_kyc_{datetime.now().strftime('%H%M%S')}@test.com",
            "phone": "+2348087654321",
            "password": "password123",
            "gender": "female",
            "date_of_birth": "1985-01-01",
            "user_path": "partner",
            "partner_type": "agent",
            "business_info": {
                "business_name": "Test KYC Agency",
                "location": "Abuja, Nigeria"
            }
        }
        
        success, response = self.make_request('POST', '/api/auth/complete-registration', agent_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.log_test("Create Agent User", True)
            return response['token'], response['user']['id']
        else:
            self.log_test("Create Agent User", False, f"Agent creation failed: {response}")
            return None, None

    def create_business_user(self):
        """Create a business user for testing"""
        print("🏢 Creating business user for testing...")
        
        business_data = {
            "first_name": "Test",
            "last_name": "Business",
            "username": f"testbusiness_kyc_{datetime.now().strftime('%H%M%S')}",
            "email_or_phone": f"testbusiness_kyc_{datetime.now().strftime('%H%M%S')}@test.com",
            "phone": "+2348098765432",
            "password": "password123",
            "gender": "male",
            "date_of_birth": "1980-01-01",
            "user_path": "partner",
            "partner_type": "business",
            "business_category": "processor",
            "business_info": {
                "business_name": "Test KYC Processing Ltd",
                "location": "Lagos, Nigeria"
            }
        }
        
        success, response = self.make_request('POST', '/api/auth/complete-registration', business_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.log_test("Create Business User", True)
            return response['token'], response['user']['id']
        else:
            self.log_test("Create Business User", False, f"Business creation failed: {response}")
            return None, None

    def test_kyc_document_upload(self):
        """Test KYC document upload functionality"""
        print("\n📄 Testing KYC Document Upload...")
        
        # Test 1: Valid document upload - Certificate of Incorporation
        cert_doc_data = {
            "document_type": "certificate_of_incorporation",
            "file_data": "base64_encoded_certificate_data_here",
            "file_name": "certificate_of_incorporation.pdf",
            "mime_type": "application/pdf"
        }
        
        success, response = self.make_request('POST', '/api/kyc/documents/upload', cert_doc_data, 200, use_auth=True)
        
        if success and 'document_id' in response:
            self.log_test("KYC Document Upload - Certificate", True)
            cert_doc_id = response['document_id']
            cert_success = True
        else:
            self.log_test("KYC Document Upload - Certificate", False, f"Certificate upload failed: {response}")
            cert_doc_id = None
            cert_success = False
        
        # Test 2: Valid document upload - TIN Certificate
        tin_doc_data = {
            "document_type": "tin_certificate",
            "file_data": "base64_encoded_tin_certificate_data_here",
            "file_name": "tin_certificate.pdf",
            "mime_type": "application/pdf"
        }
        
        success, response = self.make_request('POST', '/api/kyc/documents/upload', tin_doc_data, 200, use_auth=True)
        
        if success and 'document_id' in response:
            self.log_test("KYC Document Upload - TIN Certificate", True)
            tin_doc_id = response['document_id']
            tin_success = True
        else:
            self.log_test("KYC Document Upload - TIN Certificate", False, f"TIN certificate upload failed: {response}")
            tin_doc_id = None
            tin_success = False
        
        # Test 3: Valid document upload - Utility Bill
        utility_doc_data = {
            "document_type": "utility_bill",
            "file_data": "base64_encoded_utility_bill_data_here",
            "file_name": "utility_bill.pdf",
            "mime_type": "application/pdf"
        }
        
        success, response = self.make_request('POST', '/api/kyc/documents/upload', utility_doc_data, 200, use_auth=True)
        
        if success and 'document_id' in response:
            self.log_test("KYC Document Upload - Utility Bill", True)
            utility_doc_id = response['document_id']
            utility_success = True
        else:
            self.log_test("KYC Document Upload - Utility Bill", False, f"Utility bill upload failed: {response}")
            utility_doc_id = None
            utility_success = False
        
        # Test 4: Valid document upload - National ID Document
        national_id_doc_data = {
            "document_type": "national_id_doc",
            "file_data": "base64_encoded_national_id_data_here",
            "file_name": "national_id.jpg",
            "mime_type": "image/jpeg"
        }
        
        success, response = self.make_request('POST', '/api/kyc/documents/upload', national_id_doc_data, 200, use_auth=True)
        
        if success and 'document_id' in response:
            self.log_test("KYC Document Upload - National ID", True)
            national_id_doc_id = response['document_id']
            national_id_success = True
        else:
            self.log_test("KYC Document Upload - National ID", False, f"National ID upload failed: {response}")
            national_id_doc_id = None
            national_id_success = False
        
        # Test 5: Valid document upload - Headshot Photo
        headshot_doc_data = {
            "document_type": "headshot_photo",
            "file_data": "base64_encoded_headshot_photo_data_here",
            "file_name": "headshot.jpg",
            "mime_type": "image/jpeg"
        }
        
        success, response = self.make_request('POST', '/api/kyc/documents/upload', headshot_doc_data, 200, use_auth=True)
        
        if success and 'document_id' in response:
            self.log_test("KYC Document Upload - Headshot Photo", True)
            headshot_doc_id = response['document_id']
            headshot_success = True
        else:
            self.log_test("KYC Document Upload - Headshot Photo", False, f"Headshot upload failed: {response}")
            headshot_doc_id = None
            headshot_success = False
        
        # Test 6: Invalid document type
        invalid_doc_data = {
            "document_type": "invalid_document_type",
            "file_data": "base64_encoded_data",
            "file_name": "invalid.pdf",
            "mime_type": "application/pdf"
        }
        
        success, response = self.make_request('POST', '/api/kyc/documents/upload', invalid_doc_data, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("KYC Document Upload - Invalid Type", True)
            invalid_type_success = True
        else:
            self.log_test("KYC Document Upload - Invalid Type", False, f"Should return 400 error: {response}")
            invalid_type_success = False
        
        # Test 7: Missing required fields
        missing_fields_data = {
            "document_type": "utility_bill",
            "file_name": "utility.pdf"
            # Missing file_data and mime_type
        }
        
        success, response = self.make_request('POST', '/api/kyc/documents/upload', missing_fields_data, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("KYC Document Upload - Missing Fields", True)
            missing_fields_success = True
        else:
            self.log_test("KYC Document Upload - Missing Fields", False, f"Should return 400 error: {response}")
            missing_fields_success = False
        
        overall_success = (cert_success and tin_success and utility_success and 
                          national_id_success and headshot_success and invalid_type_success and 
                          missing_fields_success)
        
        return overall_success, {
            'certificate': cert_doc_id,
            'tin': tin_doc_id,
            'utility': utility_doc_id,
            'national_id': national_id_doc_id,
            'headshot': headshot_doc_id
        }
    
    def test_kyc_documents_retrieval(self):
        """Test retrieving user's uploaded KYC documents"""
        print("\n📋 Testing KYC Documents Retrieval...")
        
        # Test retrieving documents
        success, response = self.make_request('GET', '/api/kyc/documents/my-documents', use_auth=True)
        
        if success and 'documents' in response and 'total_documents' in response:
            documents = response['documents']
            if len(documents) > 0:
                # Check document structure
                doc = documents[0]
                required_fields = ['id', 'user_id', 'document_type', 'file_name', 'uploaded_at']
                if all(field in doc for field in required_fields):
                    self.log_test("KYC Documents Retrieval", True, f"Retrieved {len(documents)} documents")
                    return True
                else:
                    self.log_test("KYC Documents Retrieval", False, f"Document missing required fields: {doc}")
                    return False
            else:
                self.log_test("KYC Documents Retrieval", True, "No documents found (acceptable)")
                return True
        else:
            self.log_test("KYC Documents Retrieval", False, f"Documents retrieval failed: {response}")
            return False
    
    def test_unregistered_entity_kyc_submission(self, farmer_token, farmer_user_id):
        """Test unregistered entity KYC submission with farmer user"""
        print("\n👤 Testing Unregistered Entity KYC Submission...")
        
        # Switch to farmer token
        original_token = self.token
        original_user_id = self.user_id
        self.token = farmer_token
        self.user_id = farmer_user_id
        
        # First upload required documents
        upload_success, doc_ids = self.test_kyc_document_upload()
        
        if not upload_success:
            self.log_test("Unregistered Entity KYC", False, "Cannot test without uploaded documents")
            # Restore original token
            self.token = original_token
            self.user_id = original_user_id
            return False
        
        # Test 1: Valid unregistered entity KYC with NIN
        kyc_data_nin = {
            "identification_type": "nin",
            "identification_number": "12345678901",  # 11 digits
            "headshot_photo_id": doc_ids.get('headshot'),
            "national_id_document_id": doc_ids.get('national_id'),
            "utility_bill_id": doc_ids.get('utility')
        }
        
        success, response = self.make_request('POST', '/api/kyc/unregistered-entity/submit', kyc_data_nin, 200, use_auth=True)
        
        if success and response.get('status') == 'pending':
            self.log_test("Unregistered Entity KYC - NIN", True)
            nin_success = True
        else:
            self.log_test("Unregistered Entity KYC - NIN", False, f"NIN KYC submission failed: {response}")
            nin_success = False
        
        # Test 2: Valid unregistered entity KYC with BVN
        kyc_data_bvn = {
            "identification_type": "bvn",
            "identification_number": "98765432109",  # 11 digits
            "headshot_photo_id": doc_ids.get('headshot'),
            "national_id_document_id": doc_ids.get('national_id'),
            "utility_bill_id": doc_ids.get('utility')
        }
        
        success, response = self.make_request('POST', '/api/kyc/unregistered-entity/submit', kyc_data_bvn, 200, use_auth=True)
        
        if success and response.get('status') == 'pending':
            self.log_test("Unregistered Entity KYC - BVN", True)
            bvn_success = True
        else:
            self.log_test("Unregistered Entity KYC - BVN", False, f"BVN KYC submission failed: {response}")
            bvn_success = False
        
        # Test 3: Invalid NIN format (not 11 digits)
        kyc_data_invalid_nin = {
            "identification_type": "nin",
            "identification_number": "123456789",  # Only 9 digits - should fail
            "headshot_photo_id": doc_ids.get('headshot'),
            "national_id_document_id": doc_ids.get('national_id'),
            "utility_bill_id": doc_ids.get('utility')
        }
        
        success, response = self.make_request('POST', '/api/kyc/unregistered-entity/submit', kyc_data_invalid_nin, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Unregistered Entity KYC - Invalid NIN", True)
            invalid_nin_success = True
        else:
            self.log_test("Unregistered Entity KYC - Invalid NIN", False, f"Should return 400 error: {response}")
            invalid_nin_success = False
        
        # Test 4: Invalid BVN format (not 11 digits)
        kyc_data_invalid_bvn = {
            "identification_type": "bvn",
            "identification_number": "12345678901234",  # 14 digits - should fail
            "headshot_photo_id": doc_ids.get('headshot'),
            "national_id_document_id": doc_ids.get('national_id'),
            "utility_bill_id": doc_ids.get('utility')
        }
        
        success, response = self.make_request('POST', '/api/kyc/unregistered-entity/submit', kyc_data_invalid_bvn, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Unregistered Entity KYC - Invalid BVN", True)
            invalid_bvn_success = True
        else:
            self.log_test("Unregistered Entity KYC - Invalid BVN", False, f"Should return 400 error: {response}")
            invalid_bvn_success = False
        
        # Restore original token
        self.token = original_token
        self.user_id = original_user_id
        
        overall_success = nin_success and bvn_success and invalid_nin_success and invalid_bvn_success
        return overall_success
    
    def test_farmer_farmland_management(self, farmer_token, farmer_user_id):
        """Test farmer farmland management with farmer user"""
        print("\n🚜 Testing Farmer Farmland Management...")
        
        # Switch to farmer token
        original_token = self.token
        original_user_id = self.user_id
        self.token = farmer_token
        self.user_id = farmer_user_id
        
        # Test 1: Add farmland record
        farmland_data = {
            "location": "Kaduna State, Nigeria",
            "size_hectares": 5.5,
            "crop_types": ["maize", "rice", "yam"],
            "soil_type": "loamy",
            "irrigation_method": "rain-fed",
            "coordinates": {"lat": 10.5264, "lng": 7.4388}
        }
        
        success, response = self.make_request('POST', '/api/farmer/farmland', farmland_data, 200, use_auth=True)
        
        if success and 'farmland_id' in response:
            self.log_test("Add Farmland Record", True)
            farmland_id = response['farmland_id']
            add_success = True
        else:
            self.log_test("Add Farmland Record", False, f"Farmland addition failed: {response}")
            farmland_id = None
            add_success = False
        
        # Test 2: Add another farmland record
        farmland_data_2 = {
            "location": "Kano State, Nigeria",
            "size_hectares": 3.2,
            "crop_types": ["wheat", "millet"],
            "soil_type": "sandy",
            "irrigation_method": "irrigation"
        }
        
        success, response = self.make_request('POST', '/api/farmer/farmland', farmland_data_2, 200, use_auth=True)
        
        if success and 'farmland_id' in response:
            self.log_test("Add Second Farmland Record", True)
            add_second_success = True
        else:
            self.log_test("Add Second Farmland Record", False, f"Second farmland addition failed: {response}")
            add_second_success = False
        
        # Test 3: Get farmer's farmland records
        success, response = self.make_request('GET', '/api/farmer/farmland', use_auth=True)
        
        if success and 'farmlands' in response and 'summary' in response:
            farmlands = response['farmlands']
            summary = response['summary']
            
            # Check summary statistics
            if (summary.get('total_farmlands') >= 1 and 
                summary.get('total_hectares') > 0 and 
                summary.get('unique_crop_types') > 0):
                self.log_test("Get Farmer Farmland", True, 
                             f"Retrieved {summary['total_farmlands']} farmlands, {summary['total_hectares']} hectares")
                get_success = True
            else:
                self.log_test("Get Farmer Farmland", False, f"Invalid summary data: {summary}")
                get_success = False
        else:
            self.log_test("Get Farmer Farmland", False, f"Farmland retrieval failed: {response}")
            get_success = False
        
        # Test 4: Missing required fields
        invalid_farmland_data = {
            "location": "Test Location"
            # Missing size_hectares and crop_types
        }
        
        success, response = self.make_request('POST', '/api/farmer/farmland', invalid_farmland_data, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Add Farmland - Missing Fields", True)
            validation_success = True
        else:
            self.log_test("Add Farmland - Missing Fields", False, f"Should return 400 error: {response}")
            validation_success = False
        
        # Restore original token
        self.token = original_token
        self.user_id = original_user_id
        
        overall_success = add_success and add_second_success and get_success and validation_success
        return overall_success
    
    def test_farmer_dashboard(self, farmer_token, farmer_user_id):
        """Test farmer dashboard data retrieval with farmer user"""
        print("\n📊 Testing Farmer Dashboard...")
        
        # Switch to farmer token
        original_token = self.token
        original_user_id = self.user_id
        self.token = farmer_token
        self.user_id = farmer_user_id
        
        # Test farmer dashboard
        success, response = self.make_request('GET', '/api/farmer/dashboard', use_auth=True)
        
        if success and 'farmer_profile' in response and 'business_metrics' in response:
            farmer_profile = response['farmer_profile']
            business_metrics = response['business_metrics']
            
            # Check required profile fields
            profile_fields = ['name', 'username', 'kyc_status', 'average_rating']
            if all(field in farmer_profile for field in profile_fields):
                profile_valid = True
            else:
                profile_valid = False
            
            # Check required metrics fields
            metrics_fields = ['total_products', 'active_products', 'total_revenue', 'pending_orders', 'total_farmlands', 'total_hectares']
            if all(field in business_metrics for field in metrics_fields):
                metrics_valid = True
            else:
                metrics_valid = False
            
            if profile_valid and metrics_valid:
                self.log_test("Farmer Dashboard", True, 
                             f"Dashboard loaded: {business_metrics['total_farmlands']} farmlands, {business_metrics['total_hectares']} hectares")
                result = True
            else:
                self.log_test("Farmer Dashboard", False, f"Missing required fields in dashboard data")
                result = False
        else:
            self.log_test("Farmer Dashboard", False, f"Dashboard retrieval failed: {response}")
            result = False
        
        # Restore original token
        self.token = original_token
        self.user_id = original_user_id
        
        return result
    
    def test_agent_farmer_management(self, agent_token, agent_user_id):
        """Test agent farmer network management with agent user"""
        print("\n🤝 Testing Agent Farmer Management...")
        
        # Switch to agent token
        original_token = self.token
        original_user_id = self.user_id
        self.token = agent_token
        self.user_id = agent_user_id
        
        # Test 1: Add farmer to agent network
        farmer_data = {
            "farmer_name": "John Farmer",
            "farmer_phone": "+2348012345678",
            "farmer_location": "Kaduna State, Nigeria"
        }
        
        success, response = self.make_request('POST', '/api/agent/farmers/add', farmer_data, 200, use_auth=True)
        
        if success and 'farmer_id' in response:
            self.log_test("Add Farmer to Agent Network", True)
            farmer_id = response['farmer_id']
            add_success = True
        else:
            self.log_test("Add Farmer to Agent Network", False, f"Farmer addition failed: {response}")
            farmer_id = None
            add_success = False
        
        # Test 2: Add another farmer
        farmer_data_2 = {
            "farmer_name": "Mary Farmer",
            "farmer_phone": "+2348087654321",
            "farmer_location": "Kano State, Nigeria"
        }
        
        success, response = self.make_request('POST', '/api/agent/farmers/add', farmer_data_2, 200, use_auth=True)
        
        if success and 'farmer_id' in response:
            self.log_test("Add Second Farmer to Network", True)
            add_second_success = True
        else:
            self.log_test("Add Second Farmer to Network", False, f"Second farmer addition failed: {response}")
            add_second_success = False
        
        # Test 3: Try to add duplicate farmer (should fail)
        success, response = self.make_request('POST', '/api/agent/farmers/add', farmer_data, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Add Duplicate Farmer - Validation", True)
            duplicate_validation_success = True
        else:
            self.log_test("Add Duplicate Farmer - Validation", False, f"Should return 400 error: {response}")
            duplicate_validation_success = False
        
        # Test 4: Get agent's farmers
        success, response = self.make_request('GET', '/api/agent/farmers', use_auth=True)
        
        if success and 'farmers' in response and 'summary' in response:
            farmers = response['farmers']
            summary = response['summary']
            
            # Check summary statistics
            if (summary.get('total_farmers') >= 1 and 
                summary.get('active_farmers') >= 0):
                self.log_test("Get Agent Farmers", True, 
                             f"Retrieved {summary['total_farmers']} farmers, {summary['active_farmers']} active")
                get_success = True
            else:
                self.log_test("Get Agent Farmers", False, f"Invalid summary data: {summary}")
                get_success = False
        else:
            self.log_test("Get Agent Farmers", False, f"Farmers retrieval failed: {response}")
            get_success = False
        
        # Test 5: Missing required fields
        invalid_farmer_data = {
            "farmer_name": "Test Farmer"
            # Missing farmer_location
        }
        
        success, response = self.make_request('POST', '/api/agent/farmers/add', invalid_farmer_data, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Add Farmer - Missing Fields", True)
            validation_success = True
        else:
            self.log_test("Add Farmer - Missing Fields", False, f"Should return 400 error: {response}")
            validation_success = False
        
        # Restore original token
        self.token = original_token
        self.user_id = original_user_id
        
        overall_success = (add_success and add_second_success and duplicate_validation_success and 
                          get_success and validation_success)
        return overall_success
    
    def test_agent_dashboard(self, agent_token, agent_user_id):
        """Test agent dashboard data retrieval with agent user"""
        print("\n📈 Testing Agent Dashboard...")
        
        # Switch to agent token
        original_token = self.token
        original_user_id = self.user_id
        self.token = agent_token
        self.user_id = agent_user_id
        
        # Test agent dashboard
        success, response = self.make_request('GET', '/api/agent/dashboard', use_auth=True)
        
        if success and 'agent_profile' in response and 'business_metrics' in response:
            agent_profile = response['agent_profile']
            business_metrics = response['business_metrics']
            
            # Check required profile fields
            profile_fields = ['name', 'username', 'kyc_status', 'average_rating']
            if all(field in agent_profile for field in profile_fields):
                profile_valid = True
            else:
                profile_valid = False
            
            # Check required metrics fields
            metrics_fields = ['total_farmers', 'active_farmers', 'total_products', 'total_revenue', 'agent_commission']
            if all(field in business_metrics for field in metrics_fields):
                metrics_valid = True
            else:
                metrics_valid = False
            
            if profile_valid and metrics_valid:
                self.log_test("Agent Dashboard", True, 
                             f"Dashboard loaded: {business_metrics['total_farmers']} farmers, ₦{business_metrics['agent_commission']} commission")
                result = True
            else:
                self.log_test("Agent Dashboard", False, f"Missing required fields in dashboard data")
                result = False
        else:
            self.log_test("Agent Dashboard", False, f"Dashboard retrieval failed: {response}")
            result = False
        
        # Restore original token
        self.token = original_token
        self.user_id = original_user_id
        
        return result
    
    def test_audit_logs(self):
        """Test audit log system"""
        print("\n📝 Testing Audit Log System...")
        
        # Test 1: Get audit logs (basic)
        success, response = self.make_request('GET', '/api/admin/audit-logs', use_auth=True)
        
        if success and 'logs' in response and 'pagination' in response:
            logs = response['logs']
            pagination = response['pagination']
            
            # Check pagination structure
            pagination_fields = ['total_count', 'page', 'limit', 'total_pages']
            if all(field in pagination for field in pagination_fields):
                self.log_test("Get Audit Logs - Basic", True, f"Retrieved {len(logs)} logs")
                basic_success = True
            else:
                self.log_test("Get Audit Logs - Basic", False, f"Invalid pagination structure: {pagination}")
                basic_success = False
        else:
            self.log_test("Get Audit Logs - Basic", False, f"Audit logs retrieval failed: {response}")
            basic_success = False
        
        # Test 2: Get audit logs with user_id filter
        success, response = self.make_request('GET', f'/api/admin/audit-logs?user_id={self.user_id}', use_auth=True)
        
        if success and 'logs' in response:
            self.log_test("Get Audit Logs - User Filter", True, f"Retrieved logs for user {self.user_id}")
            user_filter_success = True
        else:
            self.log_test("Get Audit Logs - User Filter", False, f"User filtered logs failed: {response}")
            user_filter_success = False
        
        # Test 3: Get audit logs with action filter
        success, response = self.make_request('GET', '/api/admin/audit-logs?action=document_upload', use_auth=True)
        
        if success and 'logs' in response:
            self.log_test("Get Audit Logs - Action Filter", True, "Retrieved logs for document_upload action")
            action_filter_success = True
        else:
            self.log_test("Get Audit Logs - Action Filter", False, f"Action filtered logs failed: {response}")
            action_filter_success = False
        
        # Test 4: Get audit logs with date range
        success, response = self.make_request('GET', '/api/admin/audit-logs?days=7', use_auth=True)
        
        if success and 'logs' in response:
            self.log_test("Get Audit Logs - Date Range", True, "Retrieved logs for last 7 days")
            date_filter_success = True
        else:
            self.log_test("Get Audit Logs - Date Range", False, f"Date filtered logs failed: {response}")
            date_filter_success = False
        
        # Test 5: Get audit logs with pagination
        success, response = self.make_request('GET', '/api/admin/audit-logs?page=1&limit=10', use_auth=True)
        
        if success and 'logs' in response and 'pagination' in response:
            pagination = response['pagination']
            if pagination.get('page') == 1 and pagination.get('limit') == 10:
                self.log_test("Get Audit Logs - Pagination", True, "Pagination working correctly")
                pagination_success = True
            else:
                self.log_test("Get Audit Logs - Pagination", False, f"Invalid pagination: {pagination}")
                pagination_success = False
        else:
            self.log_test("Get Audit Logs - Pagination", False, f"Paginated logs failed: {response}")
            pagination_success = False
        
        overall_success = (basic_success and user_filter_success and action_filter_success and 
                          date_filter_success and pagination_success)
        return overall_success

    def run_all_tests(self):
        """Run all Enhanced KYC tests"""
        print("🚀 Starting Enhanced KYC System & User Dashboards Testing...")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 80)

        # Setup authentication with main user
        if not self.setup_authentication():
            print("❌ Authentication failed - stopping tests")
            return False

        # Create test users with appropriate roles
        farmer_token, farmer_user_id = self.create_farmer_user()
        agent_token, agent_user_id = self.create_agent_user()
        business_token, business_user_id = self.create_business_user()

        # Test 1: KYC Document Upload System (with main user)
        upload_success, doc_ids = self.test_kyc_document_upload()
        
        # Test 2: KYC Documents Retrieval (with main user)
        retrieval_success = self.test_kyc_documents_retrieval()
        
        # Test 3: Unregistered Entity KYC Submission (with farmer user)
        if farmer_token:
            unregistered_kyc_success = self.test_unregistered_entity_kyc_submission(farmer_token, farmer_user_id)
        else:
            print("⚠️ Skipping Unregistered Entity KYC tests - farmer user creation failed")
            unregistered_kyc_success = False
        
        # Test 4: Farmer Dashboard System (with farmer user)
        if farmer_token:
            farmer_farmland_success = self.test_farmer_farmland_management(farmer_token, farmer_user_id)
            farmer_dashboard_success = self.test_farmer_dashboard(farmer_token, farmer_user_id)
        else:
            print("⚠️ Skipping Farmer Dashboard tests - farmer user creation failed")
            farmer_farmland_success = False
            farmer_dashboard_success = False
        
        # Test 5: Agent Dashboard System (with agent user)
        if agent_token:
            agent_farmer_success = self.test_agent_farmer_management(agent_token, agent_user_id)
            agent_dashboard_success = self.test_agent_dashboard(agent_token, agent_user_id)
        else:
            print("⚠️ Skipping Agent Dashboard tests - agent user creation failed")
            agent_farmer_success = False
            agent_dashboard_success = False
        
        # Test 6: Audit Log System (with main user)
        audit_logs_success = self.test_audit_logs()

        # Print final results
        print("\n" + "=" * 80)
        print("🏁 ENHANCED KYC TESTING COMPLETE")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Overall success assessment
        overall_success = (upload_success and retrieval_success and unregistered_kyc_success and 
                          farmer_farmland_success and farmer_dashboard_success and 
                          agent_farmer_success and agent_dashboard_success and audit_logs_success)
        
        if overall_success:
            print("✅ OVERALL ASSESSMENT: All Enhanced KYC functionality working correctly")
        else:
            print("❌ OVERALL ASSESSMENT: One or more Enhanced KYC components failed")
        
        return success_rate >= 90

if __name__ == "__main__":
    tester = EnhancedKYCTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)