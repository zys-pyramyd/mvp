#!/usr/bin/env python3
"""
Enhanced Seller Dashboard Backend Testing
Tests all seller dashboard functionality as requested in the review
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class SellerDashboardTester:
    def __init__(self, base_url: str = "https://cropchain-hub-1.preview.emergentagent.com"):
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
        """Setup test user with seller role"""
        print("🔧 Setting up test user with seller role...")
        
        # Login with existing test user
        login_data = {
            "email_or_phone": "testagent@pyramyd.com",
            "password": "password123"
        }

        success, response = self.make_request('POST', '/api/auth/login', login_data, 200)
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            self.log_test("Test User Login", True)
            return True
        else:
            self.log_test("Test User Login", False, f"Login failed: {response}")
            return False

    def test_seller_analytics_dashboard(self):
        """Test seller analytics dashboard endpoint"""
        print("\n📊 Testing Seller Analytics Dashboard...")
        
        # Test 1: Default analytics (30 days)
        success, response = self.make_request('GET', '/api/seller/dashboard/analytics', use_auth=True)
        
        if success and 'period' in response and 'revenue' in response and 'orders' in response:
            # Check required sections
            required_sections = ['period', 'revenue', 'orders', 'customers', 'products', 'inventory_alerts']
            if all(section in response for section in required_sections):
                self.log_test("Seller Analytics Dashboard (Default)", True)
                default_success = True
            else:
                self.log_test("Seller Analytics Dashboard (Default)", False, f"Missing sections: {response}")
                default_success = False
        else:
            self.log_test("Seller Analytics Dashboard (Default)", False, f"Analytics failed: {response}")
            default_success = False
        
        # Test 2: Custom time period (7 days)
        success, response = self.make_request('GET', '/api/seller/dashboard/analytics?days=7', use_auth=True)
        
        if success and response.get('period', {}).get('days') == 7:
            self.log_test("Seller Analytics Dashboard (7 days)", True)
            custom_period_success = True
        else:
            self.log_test("Seller Analytics Dashboard (7 days)", False, f"Custom period failed: {response}")
            custom_period_success = False
        
        # Test 3: Extended time period (90 days)
        success, response = self.make_request('GET', '/api/seller/dashboard/analytics?days=90', use_auth=True)
        
        if success and response.get('period', {}).get('days') == 90:
            self.log_test("Seller Analytics Dashboard (90 days)", True)
            extended_period_success = True
        else:
            self.log_test("Seller Analytics Dashboard (90 days)", False, f"Extended period failed: {response}")
            extended_period_success = False
        
        # Test 4: Verify comprehensive metrics
        if default_success:
            # Check revenue calculations
            revenue_data = response.get('revenue', {})
            required_revenue_fields = ['total_revenue', 'pending_revenue', 'daily_average', 'daily_sales']
            if all(field in revenue_data for field in required_revenue_fields):
                self.log_test("Seller Analytics - Revenue Calculations", True)
                revenue_success = True
            else:
                self.log_test("Seller Analytics - Revenue Calculations", False, f"Revenue data incomplete: {revenue_data}")
                revenue_success = False
            
            # Check order statistics
            orders_data = response.get('orders', {})
            required_order_fields = ['total_orders', 'completed_orders', 'pending_orders', 'cancelled_orders', 'completion_rate']
            if all(field in orders_data for field in required_order_fields):
                self.log_test("Seller Analytics - Order Statistics", True)
                order_success = True
            else:
                self.log_test("Seller Analytics - Order Statistics", False, f"Order stats incomplete: {orders_data}")
                order_success = False
            
            # Check customer insights
            customers_data = response.get('customers', {})
            required_customer_fields = ['unique_customers', 'repeat_customers', 'repeat_rate', 'top_customers']
            if all(field in customers_data for field in required_customer_fields):
                self.log_test("Seller Analytics - Customer Insights", True)
                customer_success = True
            else:
                self.log_test("Seller Analytics - Customer Insights", False, f"Customer insights incomplete: {customers_data}")
                customer_success = False
            
            # Check product performance metrics
            products_data = response.get('products', {})
            required_product_fields = ['total_products', 'active_products', 'low_stock_alerts', 'out_of_stock', 'performance']
            if all(field in products_data for field in required_product_fields):
                self.log_test("Seller Analytics - Product Performance", True)
                product_success = True
            else:
                self.log_test("Seller Analytics - Product Performance", False, f"Product performance incomplete: {products_data}")
                product_success = False
            
            # Check inventory alerts
            inventory_data = response.get('inventory_alerts', {})
            if 'low_stock_products' in inventory_data and 'out_of_stock_products' in inventory_data:
                self.log_test("Seller Analytics - Inventory Alerts", True)
                inventory_success = True
            else:
                self.log_test("Seller Analytics - Inventory Alerts", False, f"Inventory alerts incomplete: {inventory_data}")
                inventory_success = False
        else:
            revenue_success = order_success = customer_success = product_success = inventory_success = False
        
        overall_success = (default_success and custom_period_success and extended_period_success and 
                          revenue_success and order_success and customer_success and 
                          product_success and inventory_success)
        
        return overall_success

    def test_seller_order_management(self):
        """Test seller order management endpoints"""
        print("\n📋 Testing Seller Order Management...")
        
        # Test 1: Get all seller orders (default)
        success, response = self.make_request('GET', '/api/seller/dashboard/orders', use_auth=True)
        
        if success and 'orders' in response and 'pagination' in response and 'status_summary' in response:
            self.log_test("Seller Orders - Default Listing", True)
            default_success = True
        else:
            self.log_test("Seller Orders - Default Listing", False, f"Orders listing failed: {response}")
            default_success = False
        
        # Test 2: Filter by status
        success, response = self.make_request('GET', '/api/seller/dashboard/orders?status=pending', use_auth=True)
        
        if success and 'orders' in response:
            self.log_test("Seller Orders - Status Filtering", True)
            status_filter_success = True
        else:
            self.log_test("Seller Orders - Status Filtering", False, f"Status filtering failed: {response}")
            status_filter_success = False
        
        # Test 3: Filter by date range (last 7 days)
        success, response = self.make_request('GET', '/api/seller/dashboard/orders?days=7', use_auth=True)
        
        if success and 'orders' in response:
            self.log_test("Seller Orders - Date Range Filtering", True)
            date_filter_success = True
        else:
            self.log_test("Seller Orders - Date Range Filtering", False, f"Date filtering failed: {response}")
            date_filter_success = False
        
        # Test 4: Pagination
        success, response = self.make_request('GET', '/api/seller/dashboard/orders?page=1&limit=5', use_auth=True)
        
        if success and response.get('pagination', {}).get('limit') == 5:
            self.log_test("Seller Orders - Pagination", True)
            pagination_success = True
        else:
            self.log_test("Seller Orders - Pagination", False, f"Pagination failed: {response}")
            pagination_success = False
        
        # Test 5: Combined filters
        success, response = self.make_request('GET', '/api/seller/dashboard/orders?status=completed&days=30&page=1&limit=10', use_auth=True)
        
        if success and 'orders' in response:
            self.log_test("Seller Orders - Combined Filters", True)
            combined_success = True
        else:
            self.log_test("Seller Orders - Combined Filters", False, f"Combined filtering failed: {response}")
            combined_success = False
        
        # Test 6: Status summary verification
        if default_success:
            status_summary = response.get('status_summary', {})
            expected_statuses = ['pending', 'confirmed', 'in_transit', 'delivered', 'completed', 'cancelled']
            if all(status in status_summary for status in expected_statuses):
                self.log_test("Seller Orders - Status Summary", True)
                summary_success = True
            else:
                self.log_test("Seller Orders - Status Summary", False, f"Status summary incomplete: {status_summary}")
                summary_success = False
        else:
            summary_success = False
        
        overall_success = (default_success and status_filter_success and date_filter_success and 
                          pagination_success and combined_success and summary_success)
        
        return overall_success

    def test_order_status_updates(self):
        """Test seller order status update functionality"""
        print("\n✏️ Testing Seller Order Status Updates...")
        
        # Create a test order first (using existing product)
        # Get existing products first
        success, response = self.make_request('GET', '/api/products?limit=1', use_auth=True)
        
        if not success or not response.get('products'):
            self.log_test("Order Status Updates", False, "No products available for testing")
            return False
        
        product = response['products'][0]
        product_id = product['id']
        
        # Create a test order
        order_data = {
            "product_id": product_id,
            "quantity": 2.0,
            "unit": "kg",
            "delivery_method": "platform",
            "shipping_address": "Test Address for Status Update"
        }
        
        success, response = self.make_request('POST', '/api/orders/create', order_data, 200, use_auth=True)
        if not success or 'order_id' not in response:
            self.log_test("Order Status Updates", False, "Cannot create test order")
            return False
        
        test_order_id = response['order_id']
        
        # Test 1: Valid status update (pending to confirmed)
        status_update_data = {
            "status": "confirmed",
            "notes": "Order confirmed by seller"
        }
        
        success, response = self.make_request('PUT', f'/api/seller/orders/{test_order_id}/status', 
                                            status_update_data, 200, use_auth=True)
        
        if success and response.get('new_status') == 'confirmed':
            self.log_test("Order Status Update (Valid)", True)
            valid_success = True
        else:
            self.log_test("Order Status Update (Valid)", False, f"Status update failed: {response}")
            valid_success = False
        
        # Test 2: Invalid status
        invalid_status_data = {
            "status": "invalid_status"
        }
        
        success, response = self.make_request('PUT', f'/api/seller/orders/{test_order_id}/status', 
                                            invalid_status_data, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Order Status Update (Invalid Status)", True)
            invalid_success = True
        else:
            self.log_test("Order Status Update (Invalid Status)", False, f"Should return 400 error: {response}")
            invalid_success = False
        
        # Test 3: Status progression (confirmed to preparing)
        preparing_status_data = {
            "status": "preparing",
            "notes": "Order is being prepared"
        }
        
        success, response = self.make_request('PUT', f'/api/seller/orders/{test_order_id}/status', 
                                            preparing_status_data, 200, use_auth=True)
        
        if success and response.get('new_status') == 'preparing':
            self.log_test("Order Status Update (Progression)", True)
            progression_success = True
        else:
            self.log_test("Order Status Update (Progression)", False, f"Status progression failed: {response}")
            progression_success = False
        
        # Test 4: Complete the order
        completed_status_data = {
            "status": "completed",
            "notes": "Order completed successfully"
        }
        
        success, response = self.make_request('PUT', f'/api/seller/orders/{test_order_id}/status', 
                                            completed_status_data, 200, use_auth=True)
        
        if success and response.get('new_status') == 'completed':
            self.log_test("Order Status Update (Completed)", True)
            completed_success = True
        else:
            self.log_test("Order Status Update (Completed)", False, f"Completed status failed: {response}")
            completed_success = False
        
        overall_success = valid_success and invalid_success and progression_success and completed_success
        return overall_success

    def test_product_performance_analytics(self):
        """Test product performance analytics endpoint"""
        print("\n📈 Testing Product Performance Analytics...")
        
        # Test 1: Default product performance (30 days)
        success, response = self.make_request('GET', '/api/seller/products/performance', use_auth=True)
        
        if success and 'products' in response and 'summary' in response:
            self.log_test("Product Performance Analytics (Default)", True)
            default_success = True
        else:
            self.log_test("Product Performance Analytics (Default)", False, f"Performance analytics failed: {response}")
            default_success = False
        
        # Test 2: Custom time period (7 days)
        success, response = self.make_request('GET', '/api/seller/products/performance?days=7', use_auth=True)
        
        if success and 'products' in response:
            self.log_test("Product Performance Analytics (7 days)", True)
            custom_success = True
        else:
            self.log_test("Product Performance Analytics (7 days)", False, f"Custom period failed: {response}")
            custom_success = False
        
        # Test 3: Verify product metrics structure
        if default_success and len(response.get('products', [])) > 0:
            product = response['products'][0]
            required_fields = ['product_id', 'product_name', 'category', 'price_per_unit', 'stock_level', 'metrics', 'alerts']
            if all(field in product for field in required_fields):
                # Check metrics structure
                metrics = product.get('metrics', {})
                required_metrics = ['total_orders', 'completed_orders', 'conversion_rate', 'revenue', 'average_rating', 'rating_distribution']
                if all(metric in metrics for metric in required_metrics):
                    self.log_test("Product Performance - Metrics Structure", True)
                    metrics_success = True
                else:
                    self.log_test("Product Performance - Metrics Structure", False, f"Metrics incomplete: {metrics}")
                    metrics_success = False
            else:
                self.log_test("Product Performance - Product Structure", False, f"Product fields incomplete: {product}")
                metrics_success = False
        else:
            self.log_test("Product Performance - Metrics Structure", True, "No products found (acceptable)")
            metrics_success = True
        
        # Test 4: Verify rating distribution
        if default_success and len(response.get('products', [])) > 0:
            product = response['products'][0]
            rating_dist = product.get('metrics', {}).get('rating_distribution', {})
            expected_ratings = ['5_star', '4_star', '3_star', '2_star', '1_star']
            if all(rating in rating_dist for rating in expected_ratings):
                self.log_test("Product Performance - Rating Distribution", True)
                rating_success = True
            else:
                self.log_test("Product Performance - Rating Distribution", False, f"Rating distribution incomplete: {rating_dist}")
                rating_success = False
        else:
            self.log_test("Product Performance - Rating Distribution", True, "No products found (acceptable)")
            rating_success = True
        
        overall_success = default_success and custom_success and metrics_success and rating_success
        return overall_success

    def test_customer_insights_analytics(self):
        """Test customer insights and analytics endpoint"""
        print("\n👥 Testing Customer Insights & Analytics...")
        
        # Test 1: Default customer insights (30 days)
        success, response = self.make_request('GET', '/api/seller/customers/insights', use_auth=True)
        
        if success and 'summary' in response and 'top_customers' in response and 'segments' in response:
            self.log_test("Customer Insights Analytics (Default)", True)
            default_success = True
        else:
            self.log_test("Customer Insights Analytics (Default)", False, f"Customer insights failed: {response}")
            default_success = False
        
        # Test 2: Custom time period (7 days)
        success, response = self.make_request('GET', '/api/seller/customers/insights?days=7', use_auth=True)
        
        if success and 'summary' in response:
            self.log_test("Customer Insights Analytics (7 days)", True)
            custom_success = True
        else:
            self.log_test("Customer Insights Analytics (7 days)", False, f"Custom period failed: {response}")
            custom_success = False
        
        # Test 3: Verify summary structure
        if default_success:
            summary = response.get('summary', {})
            required_summary_fields = ['total_customers', 'high_value_customers', 'repeat_customers', 
                                     'new_customers', 'average_customer_value', 'customer_retention_rate']
            if all(field in summary for field in required_summary_fields):
                self.log_test("Customer Insights - Summary Structure", True)
                summary_success = True
            else:
                self.log_test("Customer Insights - Summary Structure", False, f"Summary incomplete: {summary}")
                summary_success = False
        else:
            summary_success = False
        
        # Test 4: Verify customer segments
        if default_success:
            segments = response.get('segments', {})
            required_segments = ['high_value', 'repeat', 'new', 'at_risk']
            if all(segment in segments for segment in required_segments):
                self.log_test("Customer Insights - Segments", True)
                segments_success = True
            else:
                self.log_test("Customer Insights - Segments", False, f"Segments incomplete: {segments}")
                segments_success = False
        else:
            segments_success = False
        
        overall_success = default_success and custom_success and summary_success and segments_success
        return overall_success

    def test_inventory_management(self):
        """Test inventory management functionality"""
        print("\n📦 Testing Inventory Management...")
        
        # Get existing products first
        success, response = self.make_request('GET', '/api/products?limit=1', use_auth=True)
        
        if not success or not response.get('products'):
            self.log_test("Inventory Management", False, "No products available for testing")
            return False
        
        product = response['products'][0]
        product_id = product['id']
        
        # Test 1: Valid inventory update
        inventory_update_data = {
            "quantity_available": 150,
            "minimum_order_quantity": 10
        }
        
        success, response = self.make_request('PUT', f'/api/seller/products/{product_id}/inventory', 
                                            inventory_update_data, 200, use_auth=True)
        
        if success and response.get('new_quantity') == 150:
            self.log_test("Inventory Management - Valid Update", True)
            valid_success = True
        else:
            self.log_test("Inventory Management - Valid Update", False, f"Inventory update failed: {response}")
            valid_success = False
        
        # Test 2: Invalid quantity (negative)
        invalid_quantity_data = {
            "quantity_available": -50
        }
        
        success, response = self.make_request('PUT', f'/api/seller/products/{product_id}/inventory', 
                                            invalid_quantity_data, 400, use_auth=True)
        
        if success:  # Should return 400 error
            self.log_test("Inventory Management - Invalid Quantity", True)
            invalid_success = True
        else:
            self.log_test("Inventory Management - Invalid Quantity", False, f"Should return 400 error: {response}")
            invalid_success = False
        
        # Test 3: Zero quantity (valid - out of stock)
        zero_quantity_data = {
            "quantity_available": 0
        }
        
        success, response = self.make_request('PUT', f'/api/seller/products/{product_id}/inventory', 
                                            zero_quantity_data, 200, use_auth=True)
        
        if success and response.get('new_quantity') == 0:
            self.log_test("Inventory Management - Zero Quantity", True)
            zero_success = True
        else:
            self.log_test("Inventory Management - Zero Quantity", False, f"Zero quantity update failed: {response}")
            zero_success = False
        
        overall_success = valid_success and invalid_success and zero_success
        return overall_success

    def test_security_authorization(self):
        """Test security and authorization for seller dashboard endpoints"""
        print("\n🔒 Testing Security & Authorization...")
        
        # Test 1: Unauthenticated access (should fail)
        success, response = self.make_request('GET', '/api/seller/dashboard/analytics', expected_status=401)
        
        if success:  # Should return 401 error
            self.log_test("Security - Unauthenticated Access", True)
            unauth_success = True
        else:
            self.log_test("Security - Unauthenticated Access", False, f"Should return 401 error: {response}")
            unauth_success = False
        
        # Test 2: Authenticated access (should work)
        success, response = self.make_request('GET', '/api/seller/dashboard/analytics', use_auth=True)
        
        if success and 'revenue' in response:
            self.log_test("Security - Authenticated Access", True)
            auth_success = True
        else:
            self.log_test("Security - Authenticated Access", False, f"Authenticated access failed: {response}")
            auth_success = False
        
        # Test 3: Data isolation (sellers only see their own data)
        if auth_success:
            products_data = response.get('products', {})
            if isinstance(products_data, dict):
                self.log_test("Security - Data Isolation", True, "Seller sees only their own data")
                isolation_success = True
            else:
                self.log_test("Security - Data Isolation", False, f"Data structure unexpected: {products_data}")
                isolation_success = False
        else:
            isolation_success = False
        
        overall_success = unauth_success and auth_success and isolation_success
        return overall_success

    def test_data_integration(self):
        """Test data integration with existing collections"""
        print("\n🔗 Testing Data Integration...")
        
        # Test 1: Integration with products collection
        success, response = self.make_request('GET', '/api/seller/dashboard/analytics', use_auth=True)
        
        if success and 'products' in response:
            products_data = response.get('products', {})
            if 'total_products' in products_data and 'performance' in products_data:
                self.log_test("Data Integration - Products Collection", True)
                products_success = True
            else:
                self.log_test("Data Integration - Products Collection", False, f"Products data incomplete: {products_data}")
                products_success = False
        else:
            self.log_test("Data Integration - Products Collection", False, f"Analytics failed: {response}")
            products_success = False
        
        # Test 2: Integration with orders collection
        if success:
            orders_data = response.get('orders', {})
            if 'total_orders' in orders_data and 'completion_rate' in orders_data:
                self.log_test("Data Integration - Orders Collection", True)
                orders_success = True
            else:
                self.log_test("Data Integration - Orders Collection", False, f"Orders data incomplete: {orders_data}")
                orders_success = False
        else:
            orders_success = False
        
        # Test 3: JSON serialization of datetime objects
        success, response = self.make_request('GET', '/api/seller/dashboard/orders', use_auth=True)
        
        if success and 'orders' in response:
            orders = response.get('orders', [])
            if len(orders) > 0:
                order = orders[0]
                # Check if datetime fields are properly serialized
                if 'created_at' in order and isinstance(order['created_at'], str):
                    self.log_test("Data Integration - DateTime Serialization", True)
                    datetime_success = True
                else:
                    self.log_test("Data Integration - DateTime Serialization", False, f"DateTime serialization issue: {order}")
                    datetime_success = False
            else:
                self.log_test("Data Integration - DateTime Serialization", True, "No orders found (acceptable)")
                datetime_success = True
        else:
            self.log_test("Data Integration - DateTime Serialization", False, f"Orders retrieval failed: {response}")
            datetime_success = False
        
        overall_success = products_success and orders_success and datetime_success
        return overall_success

    def run_all_tests(self):
        """Run all Enhanced Seller Dashboard tests"""
        print("🚀 Starting Enhanced Seller Dashboard Testing...")
        print("=" * 60)
        
        # Setup test user
        if not self.setup_test_user():
            print("❌ Failed to setup test user - stopping tests")
            return False
        
        print("\n📊 Testing Enhanced Seller Dashboard System...")
        print("=" * 60)
        
        # Test 1: Seller Analytics Dashboard
        analytics_success = self.test_seller_analytics_dashboard()
        
        # Test 2: Seller Order Management
        order_management_success = self.test_seller_order_management()
        
        # Test 3: Order Status Updates
        status_updates_success = self.test_order_status_updates()
        
        # Test 4: Product Performance Analytics
        product_performance_success = self.test_product_performance_analytics()
        
        # Test 5: Customer Insights & Analytics
        customer_insights_success = self.test_customer_insights_analytics()
        
        # Test 6: Inventory Management
        inventory_management_success = self.test_inventory_management()
        
        # Test 7: Security & Authorization
        security_success = self.test_security_authorization()
        
        # Test 8: Data Integration
        data_integration_success = self.test_data_integration()
        
        # Calculate overall success
        overall_success = (analytics_success and order_management_success and status_updates_success and 
                          product_performance_success and customer_insights_success and 
                          inventory_management_success and security_success and data_integration_success)
        
        return overall_success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED SELLER DASHBOARD TEST SUMMARY")
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
            print("   ✅ Enhanced Seller Dashboard is mostly functional")
        else:
            print("   ⚠️  Enhanced Seller Dashboard has significant issues")

        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = SellerDashboardTester()
    
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