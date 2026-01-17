import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add backend directory to sys.path
# Add project root to sys.path to allow importing from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.payment.farm_deals_payment import initialize_farmhub_payment
from backend.payment.pyexpress_payment import initialize_pyexpress_payment
from backend.payment.community_payment import initialize_community_payment

class TestPaymentRefactor(unittest.TestCase):
    
    def setUp(self):
        self.user = {
            "id": "user123",
            "email": "test@example.com"
        }
        self.payment_data = {
            "product_total": 1000,
            "product_id": "prod123",
            "order_id": "order123",
            "customer_state": "Lagos",
            "callback_url": "http://localhost:3000/callback"
        }
        self.delivery_fee = 500
        self.delivery_method = "pickup"

    @patch('backend.payment.farm_deals_payment.paystack_request')
    def test_farmhub_payment(self, mock_paystack):
        mock_paystack.return_value = {
            "status": True,
            "data": {
                "authorization_url": "https://paystack.com/auth/farmhub",
                "access_code": "farmhub_code"
            }
        }
        
        result = initialize_farmhub_payment(
            self.payment_data, 
            self.user, 
            self.delivery_fee, 
            self.delivery_method
        )
        
        self.assertTrue(result["response"]["status"])
        self.assertIn("amount_kobo", result)
        # 1000 * 0.10 = 100 service charge
        # 1000 + 100 + 500 = 1600 total
        self.assertEqual(result["amount_kobo"], 160000)
        self.assertEqual(result["split_code"], os.environ.get('FARMHUB_SPLIT_GROUP', ''))

    @patch('backend.payment.pyexpress_payment.paystack_request')
    def test_pyexpress_payment(self, mock_paystack):
        mock_paystack.return_value = {
            "status": True,
            "data": {
                "authorization_url": "https://paystack.com/auth/home",
                "access_code": "home_code"
            }
        }
        
        data = self.payment_data.copy()
        data["subaccount_code"] = "ACCT_123"
        
        result = initialize_pyexpress_payment(
            data, 
            self.user, 
            self.delivery_fee, 
            self.delivery_method
        )
        
        self.assertTrue(result["response"]["status"])
        # 1000 * 0.025 = 25 vendor commission
        # 1000 * 0.03 = 30 buyer service charge
        # Platform cut = 25 + 30 + 500 = 555
        # Total = 1000 + 555 = 1555
        self.assertEqual(result["amount_kobo"], 155500)
        self.assertEqual(result["subaccount_code"], "ACCT_123")

    @patch('backend.payment.community_payment.paystack_request')
    def test_community_payment(self, mock_paystack):
        mock_paystack.return_value = {
            "status": True,
            "data": {
                "authorization_url": "https://paystack.com/auth/community",
                "access_code": "community_code"
            }
        }
        
        data = self.payment_data.copy()
        data["subaccount_code"] = "ACCT_456"
        
        result = initialize_community_payment(
            data, 
            self.user, 
            self.delivery_fee, 
            self.delivery_method
        )
        
        self.assertTrue(result["response"]["status"])
        # 1000 * 0.025 = 25 vendor commission
        # 1000 * 0.05 = 50 buyer service charge
        # Platform cut = 25 + 50 + 500 = 575
        # Total = 1000 + 575 = 1575
        self.assertEqual(result["amount_kobo"], 157500)
        self.assertEqual(result["subaccount_code"], "ACCT_456")

if __name__ == '__main__':
    unittest.main()
