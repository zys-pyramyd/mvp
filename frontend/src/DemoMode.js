import React, { useState, useEffect } from 'react';

// Demo Data Storage Keys
const DEMO_STORAGE_KEYS = {
  DEMO_MODE: 'pyramyd_demo_mode',
  DEMO_USER: 'pyramyd_demo_user',
  DEMO_FARMERS: 'pyramyd_demo_farmers',
  DEMO_PRODUCTS: 'pyramyd_demo_products',
  DEMO_ORDERS: 'pyramyd_demo_orders',
  DEMO_KYC_STATUS: 'pyramyd_demo_kyc_status',
  DEMO_TRANSACTIONS: 'pyramyd_demo_transactions'
};

// Demo Mode Manager
export class DemoModeManager {
  static isDemoMode() {
    return localStorage.getItem(DEMO_STORAGE_KEYS.DEMO_MODE) === 'true';
  }

  static enableDemoMode() {
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_MODE, 'true');
    this.initializeDemoData();
  }

  static disableDemoMode() {
    localStorage.removeItem(DEMO_STORAGE_KEYS.DEMO_MODE);
    this.clearDemoData();
  }

  static clearDemoData() {
    Object.values(DEMO_STORAGE_KEYS).forEach(key => {
      if (key !== DEMO_STORAGE_KEYS.DEMO_MODE) {
        localStorage.removeItem(key);
      }
    });
  }

  static initializeDemoData() {
    // Initialize demo agent user
    const demoAgent = {
      id: 'demo_agent_001',
      username: 'demo_agent',
      first_name: 'Demo',
      last_name: 'Agent',
      email: 'demo.agent@pyramyd.com',
      phone: '+234 800 000 0001',
      role: 'agent',
      account_type: 'agent',
      business_category: 'agriculture',
      kyc_status: 'approved',
      is_registered_business: true,
      business_info: {
        business_name: 'Demo Agricultural Solutions',
        business_address: 'Lagos, Nigeria',
        registration_number: 'RC-DEMO-001',
        tin_number: 'TIN-DEMO-001'
      },
      created_at: new Date().toISOString(),
      demo: true
    };

    // Initialize demo farmers
    const demoFarmers = [
      {
        id: 'demo_farmer_001',
        farmer_name: 'Adebayo Ogundimu',
        farmer_phone: '+234 800 111 0001',
        farmer_location: 'Ogun State, Nigeria',
        agent_id: 'demo_agent_001',
        crops: ['Rice', 'Yam', 'Cassava'],
        farm_size: '5 hectares',
        created_at: new Date().toISOString()
      },
      {
        id: 'demo_farmer_002', 
        farmer_name: 'Fatima Aliyu',
        farmer_phone: '+234 800 111 0002',
        farmer_location: 'Kaduna State, Nigeria',
        agent_id: 'demo_agent_001',
        crops: ['Maize', 'Beans', 'Millet'],
        farm_size: '3 hectares',
        created_at: new Date().toISOString()
      },
      {
        id: 'demo_farmer_003',
        farmer_name: 'Emeka Okafor',
        farmer_phone: '+234 800 111 0003', 
        farmer_location: 'Enugu State, Nigeria',
        agent_id: 'demo_agent_001',
        crops: ['Plantain', 'Cocoyam', 'Vegetables'],
        farm_size: '2.5 hectares',
        created_at: new Date().toISOString()
      }
    ];

    // Initialize demo products
    const demoProducts = [
      {
        id: 'demo_product_001',
        title: 'Premium Local Rice',
        description: 'High-quality local rice from Ogun State farms',
        category: 'grains_legumes',
        subcategory: 'rice',
        processing_level: 'semi_processed',
        price_per_unit: 800,
        unit_of_measure: 'kg',
        quantity_available: 500,
        minimum_order_quantity: 10,
        location: 'Ogun State, Nigeria',
        farm_name: 'Ogundimu Farms',
        seller_id: 'demo_agent_001',
        seller_username: 'demo_agent',
        seller_type: 'agent',
        farmer_id: 'demo_farmer_001',
        farmer_name: 'Adebayo Ogundimu',
        images: ['https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400'],
        can_deliver_shipping: true,
        can_deliver_dropoff: true,
        shipping_cost_per_unit: 50,
        dropoff_delivery_cost: 100,
        free_shipping_threshold: 5000,
        platform: 'fam_deals',
        created_at: new Date().toISOString(),
        demo: true
      },
      {
        id: 'demo_product_002',
        title: 'Fresh White Yam',
        description: 'Premium white yam tubers, freshly harvested',
        category: 'tubers_roots',
        subcategory: 'yams',
        processing_level: 'not_processed',
        price_per_unit: 1200,
        unit_of_measure: 'tuber',
        quantity_available: 200,
        minimum_order_quantity: 5,
        location: 'Ogun State, Nigeria',
        farm_name: 'Ogundimu Farms',
        seller_id: 'demo_agent_001',
        seller_username: 'demo_agent',
        seller_type: 'agent',
        farmer_id: 'demo_farmer_001',
        farmer_name: 'Adebayo Ogundimu',
        images: ['https://images.unsplash.com/photo-1587049016137-d2d2b14b0d61?w=400'],
        can_deliver_shipping: false,
        can_deliver_dropoff: true,
        dropoff_delivery_cost: 200,
        platform: 'fam_deals',
        created_at: new Date().toISOString(),
        demo: true
      },
      {
        id: 'demo_product_003',
        title: 'Organic White Beans',
        description: 'Nutritious white beans from Kaduna farms',
        category: 'grains_legumes',
        subcategory: 'beans',
        processing_level: 'not_processed',
        price_per_unit: 600,
        unit_of_measure: 'kg',
        quantity_available: 300,
        minimum_order_quantity: 20,
        location: 'Kaduna State, Nigeria',
        farm_name: 'Aliyu Farms',
        seller_id: 'demo_agent_001',
        seller_username: 'demo_agent',
        seller_type: 'agent',
        farmer_id: 'demo_farmer_002',
        farmer_name: 'Fatima Aliyu',
        images: ['https://images.unsplash.com/photo-1518077202175-fce4715c29b6?w=400'],
        can_deliver_shipping: true,
        can_deliver_dropoff: true,
        shipping_cost_per_unit: 30,
        dropoff_delivery_cost: 80,
        free_shipping_threshold: 10000,
        platform: 'fam_deals',
        created_at: new Date().toISOString(),
        demo: true
      }
    ];

    // Initialize demo orders
    const demoOrders = [
      {
        id: 'demo_order_001',
        product_id: 'demo_product_001',
        product_name: 'Premium Local Rice',
        buyer_id: 'demo_buyer_001',
        buyer_name: 'Lagos Restaurant Chain',
        seller_id: 'demo_agent_001',
        seller_name: 'demo_agent',
        quantity: 50,
        unit: 'kg',
        total_amount: 42500, // (800 * 50) + (50 * 50) shipping
        delivery_method: 'platform',
        delivery_address: 'Victoria Island, Lagos',
        status: 'confirmed',
        payment_status: 'paid',
        order_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
        demo: true
      },
      {
        id: 'demo_order_002',
        product_id: 'demo_product_003',
        product_name: 'Organic White Beans',
        buyer_id: 'demo_buyer_002',
        buyer_name: 'Abuja Food Processor',
        seller_id: 'demo_agent_001',
        seller_name: 'demo_agent',
        quantity: 100,
        unit: 'kg',
        total_amount: 63000, // (600 * 100) + (30 * 100) shipping
        delivery_method: 'platform',
        delivery_address: 'Wuse 2, Abuja',
        status: 'processing',
        payment_status: 'paid',
        order_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
        demo: true
      },
      {
        id: 'demo_order_003',
        product_id: 'demo_product_002',
        product_name: 'Fresh White Yam',
        buyer_id: 'demo_buyer_003',
        buyer_name: 'Local Market Vendor',
        seller_id: 'demo_agent_001',
        seller_name: 'demo_agent',
        quantity: 20,
        unit: 'tuber',
        total_amount: 24200, // (1200 * 20) + 200 dropoff
        delivery_method: 'offline',
        delivery_address: 'Ikeja Market, Lagos',
        status: 'delivered',
        payment_status: 'paid',
        order_date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
        demo: true
      }
    ];

    // Initialize demo transactions
    const demoTransactions = [
      {
        id: 'demo_trans_001',
        order_id: 'demo_order_001',
        amount: 42500,
        agent_commission: 2125, // 5%
        farmer_payment: 38125,
        platform_fee: 2250,
        type: 'sale',
        status: 'completed',
        transaction_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 'demo_trans_002',
        order_id: 'demo_order_002',
        amount: 63000,
        agent_commission: 3150, // 5%
        farmer_payment: 56700,
        platform_fee: 3150,
        type: 'sale',
        status: 'completed',
        transaction_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 'demo_trans_003',
        order_id: 'demo_order_003',
        amount: 24200,
        agent_commission: 1210, // 5%
        farmer_payment: 21780,
        platform_fee: 1210,
        type: 'sale',
        status: 'completed',
        transaction_date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
      }
    ];

    // Store all demo data in localStorage
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_USER, JSON.stringify(demoAgent));
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_FARMERS, JSON.stringify(demoFarmers));
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_PRODUCTS, JSON.stringify(demoProducts));
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_ORDERS, JSON.stringify(demoOrders));
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_TRANSACTIONS, JSON.stringify(demoTransactions));
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_KYC_STATUS, JSON.stringify({
      status: 'approved',
      submitted_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      approved_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      can_trade: true,
      requires_kyc: false
    }));
  }

  // Demo Data Getters
  static getDemoUser() {
    const userData = localStorage.getItem(DEMO_STORAGE_KEYS.DEMO_USER);
    return userData ? JSON.parse(userData) : null;
  }

  static getDemoFarmers() {
    const farmersData = localStorage.getItem(DEMO_STORAGE_KEYS.DEMO_FARMERS);
    return farmersData ? JSON.parse(farmersData) : [];
  }

  static getDemoProducts() {
    const productsData = localStorage.getItem(DEMO_STORAGE_KEYS.DEMO_PRODUCTS);
    return productsData ? JSON.parse(productsData) : [];
  }

  static getDemoOrders() {
    const ordersData = localStorage.getItem(DEMO_STORAGE_KEYS.DEMO_ORDERS);
    return ordersData ? JSON.parse(ordersData) : [];
  }

  static getDemoTransactions() {
    const transactionsData = localStorage.getItem(DEMO_STORAGE_KEYS.DEMO_TRANSACTIONS);
    return transactionsData ? JSON.parse(transactionsData) : [];
  }

  static getDemoKYCStatus() {
    const kycData = localStorage.getItem(DEMO_STORAGE_KEYS.DEMO_KYC_STATUS);
    return kycData ? JSON.parse(kycData) : null;
  }

  // Demo Data Setters
  static addDemoFarmer(farmer) {
    const farmers = this.getDemoFarmers();
    farmer.id = `demo_farmer_${Date.now()}`;
    farmer.agent_id = 'demo_agent_001';
    farmer.created_at = new Date().toISOString();
    farmers.push(farmer);
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_FARMERS, JSON.stringify(farmers));
    return farmer;
  }

  static addDemoProduct(product) {
    const products = this.getDemoProducts();
    product.id = `demo_product_${Date.now()}`;
    product.seller_id = 'demo_agent_001';
    product.seller_username = 'demo_agent';
    product.seller_type = 'agent';
    product.platform = 'fam_deals';
    product.created_at = new Date().toISOString();
    product.demo = true;
    products.push(product);
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_PRODUCTS, JSON.stringify(products));
    return product;
  }

  static addDemoOrder(order) {
    const orders = this.getDemoOrders();
    order.id = `demo_order_${Date.now()}`;
    order.seller_id = 'demo_agent_001';
    order.seller_name = 'demo_agent';
    order.order_date = new Date().toISOString();
    order.demo = true;
    orders.push(order);
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_ORDERS, JSON.stringify(orders));
    
    // Also add transaction
    const transaction = {
      id: `demo_trans_${Date.now()}`,
      order_id: order.id,
      amount: order.total_amount,
      agent_commission: order.total_amount * 0.05,
      farmer_payment: order.total_amount * 0.90,
      platform_fee: order.total_amount * 0.05,
      type: 'sale',
      status: 'completed',
      transaction_date: new Date().toISOString()
    };
    
    const transactions = this.getDemoTransactions();
    transactions.push(transaction);
    localStorage.setItem(DEMO_STORAGE_KEYS.DEMO_TRANSACTIONS, JSON.stringify(transactions));
    
    return order;
  }
}

// Demo Mode Toggle Component
const DemoModeToggle = ({ isDemoMode, onToggle }) => {
  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">Demo Mode:</span>
          <button
            onClick={onToggle}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              isDemoMode ? 'bg-emerald-600' : 'bg-gray-200'
            }`}
          >
            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
              isDemoMode ? 'translate-x-6' : 'translate-x-1'
            }`} />
          </button>
          {isDemoMode && (
            <span className="text-xs text-emerald-600 font-medium">STAGING</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default DemoModeToggle;