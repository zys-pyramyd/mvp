import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.order.models import CartItem, Order, GroupOrder, OutsourcedOrder
from backend.order.pyexpress_order import process_create_order
from backend.order.community_order import process_create_group_order
from backend.order.farm_deals_order import process_create_outsourced_order

class TestOrderRefactor(unittest.TestCase):
    
    def setUp(self):
        self.user = {
            "id": "user123",
            "username": "testuser",
            "email": "test@example.com",
            "role": "agent"
        }
        self.db = MagicMock()
        self.db.orders = MagicMock()
        self.db.products = MagicMock()
        self.db.group_orders = MagicMock()
        self.db.outsourced_orders = MagicMock()

    def test_pyexpress_order(self):
        # Mock product
        self.db.products.find_one.return_value = {
            "id": "prod1",
            "title": "Test Product",
            "price_per_unit": 1000,
            "quantity_available": 10,
            "minimum_order_quantity": 1,
            "seller_id": "seller1",
            "seller_name": "Test Seller"
        }
        
        items = [CartItem(product_id="prod1", quantity=2)]
        delivery_address = "123 Test St"
        
        result = process_create_order(items, delivery_address, self.user, self.db)
        
        self.assertEqual(result["message"], "Order created successfully")
        self.assertEqual(result["total_amount"], 2000)
        self.db.orders.insert_one.assert_called_once()
        self.db.products.update_one.assert_called_once()

    def test_community_group_order(self):
        order_data = {
            "produce": "Tomatoes",
            "category": "vegetables",
            "quantity": 50,
            "location": "Lagos",
            "buyers": [{"user_id": "buyer1", "quantity": 10}],
            "selectedPrice": {
                "product_id": "prod2",
                "price_per_unit": 500,
                "seller_id": "seller2"
            },
            "commissionType": "pyramyd"
        }
        
        result = process_create_group_order(order_data, self.user, self.db)
        
        self.assertEqual(result["message"], "Group order created successfully")
        # 50 * 500 = 25000
        self.assertEqual(result["total_amount"], 25000)
        # 5% of 25000 = 1250
        self.assertEqual(result["agent_commission"], 1250)
        self.db.group_orders.insert_one.assert_called_once()

    def test_farm_deals_outsourced_order(self):
        result = process_create_outsourced_order(
            produce="Yam",
            category="tubers",
            quantity=100,
            expected_price=20000,
            location="Ibadan",
            current_user=self.user,
            db=self.db
        )
        
        self.assertEqual(result["message"], "Order outsourced successfully")
        self.assertEqual(result["status"], "open")
        self.db.outsourced_orders.insert_one.assert_called_once()

if __name__ == '__main__':
    unittest.main()
