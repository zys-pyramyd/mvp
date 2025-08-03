#!/usr/bin/env python3
"""
Simple test to verify the pre-order structure issue and provide solution
"""

import requests
import json

def test_preorder_structure():
    base_url = "https://7153c80b-e670-44f1-b4af-554c09ef9392.preview.emergentagent.com"
    
    print("🔍 TESTING PRE-ORDER STRUCTURE ISSUE")
    print("=" * 50)
    
    # Test /api/products endpoint
    response = requests.get(f"{base_url}/api/products")
    
    if response.status_code == 200:
        data = response.json()
        
        print("📊 /api/products Response Structure:")
        print(f"   - Products count: {len(data.get('products', []))}")
        print(f"   - Pre-orders count: {len(data.get('preorders', []))}")
        
        # Check if any products have type='preorder'
        products = data.get('products', [])
        preorder_type_products = [p for p in products if p.get('type') == 'preorder']
        print(f"   - Products with type='preorder': {len(preorder_type_products)}")
        
        # Check pre-orders structure
        preorders = data.get('preorders', [])
        if len(preorders) > 0:
            first_preorder = preorders[0]
            print(f"   - First pre-order has 'type' field: {'type' in first_preorder}")
            if 'type' in first_preorder:
                print(f"   - First pre-order type value: {first_preorder['type']}")
        
        print("\n🎯 ISSUE ANALYSIS:")
        print("   - Frontend expects: All items in 'products' array with type='preorder' for pre-orders")
        print("   - Backend provides: Pre-orders in separate 'preorders' array")
        print("   - Solution needed: Merge arrays and add type field to pre-orders")
        
        print("\n💡 SOLUTION:")
        print("   Frontend should combine both arrays:")
        print("   const allProducts = [")
        print("     ...data.products,")
        print("     ...data.preorders.map(preorder => ({ ...preorder, type: 'preorder' }))")
        print("   ];")
        
        return True
    else:
        print(f"❌ Failed to fetch products: {response.status_code}")
        return False

if __name__ == "__main__":
    test_preorder_structure()