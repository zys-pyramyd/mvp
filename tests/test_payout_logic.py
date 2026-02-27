
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.payout_service import process_order_payout

class TestPayoutService(unittest.IsolatedAsyncioTestCase):
    async def test_process_order_payout_success(self):
        # Mock DB
        mock_db = MagicMock()
        
        # Mock Order
        mock_order = {
            "order_id": "ORDER_123",
            "seller_id": "SELLER_1",
            "total_amount": 10000.0,
            "platform": "farm_deals",
            "status": "delivered"
        }
        
        # Mock find_one_and_update to return the order
        mock_db.orders.find_one_and_update.return_value = mock_order
        
        # Mock Seller User
        mock_seller = {
            "id": "SELLER_1",
            "wallet_balance": 5000.0,
            "bank_details": {
                "account_number": "0123456789",
                "bank_code": "058",
                "account_name": "Test Seller",
                "bank_name": "GTBank"
            }
        }
        mock_db.users.find_one.return_value = mock_seller
        
        # Mock Paystack calls
        with patch('app.services.payout_service.create_transfer_recipient') as mock_create_recipient, \
             patch('app.services.payout_service.initiate_transfer') as mock_transfer:
             
            mock_create_recipient.return_value = {"status": True, "data": {"recipient_code": "RCP_123"}}
            mock_transfer.return_value = {"status": True, "data": {"reference": "TRF_123"}}
            
            # Run function
            success, message = await process_order_payout("ORDER_123", mock_db)
            
            # Assertions
            self.assertTrue(success)
            self.assertEqual(message, "Payout processed successfully")
            
            # Verify Wallet Updates
            # 1. Credit Seller (Total - Fees)
            # Platform fee 10% = 1000. Seller gets 9000.
            # verify update_one called for credit
            
            # Verify Paystack transfer initiated
            mock_transfer.assert_called_once()
            
    async def test_process_order_payout_order_not_found(self):
        mock_db = MagicMock()
        mock_db.orders.find_one_and_update.return_value = None
        mock_db.orders.find_one.return_value = None # double check fails too
        
        success, message = await process_order_payout("INVALID_ORDER", mock_db)
        
        self.assertFalse(success)
        self.assertEqual(message, "Order not found")

if __name__ == '__main__':
    unittest.main()
