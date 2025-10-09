import React, { useState, useEffect } from 'react';
import { DemoModeManager } from './DemoMode';

const DemoAgentDashboard = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [demoData, setDemoData] = useState({
    farmers: [],
    products: [],
    orders: [],
    transactions: []
  });
  const [showAddFarmerModal, setShowAddFarmerModal] = useState(false);
  const [showAddProductModal, setShowAddProductModal] = useState(false);

  useEffect(() => {
    loadDemoData();
  }, []);

  const loadDemoData = () => {
    setDemoData({
      farmers: DemoModeManager.getDemoFarmers(),
      products: DemoModeManager.getDemoProducts(),
      orders: DemoModeManager.getDemoOrders(),
      transactions: DemoModeManager.getDemoTransactions()
    });
  };

  const calculateMetrics = () => {
    const totalRevenue = demoData.transactions.reduce((sum, trans) => sum + trans.amount, 0);
    const totalCommission = demoData.transactions.reduce((sum, trans) => sum + trans.agent_commission, 0);
    const completedOrders = demoData.orders.filter(order => order.status === 'delivered').length;

    return {
      totalFarmers: demoData.farmers.length,
      totalProducts: demoData.products.length,
      totalOrders: demoData.orders.length,
      completedOrders,
      totalRevenue,
      totalCommission
    };
  };

  const metrics = calculateMetrics();

  const AddFarmerModal = ({ onClose, onAdd }) => {
    const [farmerData, setFarmerData] = useState({
      farmer_name: '',
      farmer_phone: '',
      farmer_location: '',
      crops: '',
      farm_size: ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      const newFarmer = {
        ...farmerData,
        crops: farmerData.crops.split(',').map(crop => crop.trim())
      };
      const addedFarmer = DemoModeManager.addDemoFarmer(newFarmer);
      onAdd(addedFarmer);
      onClose();
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Add New Farmer</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">×</button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Farmer Name</label>
              <input
                type="text"
                required
                value={farmerData.farmer_name}
                onChange={(e) => setFarmerData(prev => ({...prev, farmer_name: e.target.value}))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                placeholder="Enter farmer name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
              <input
                type="tel"
                required
                value={farmerData.farmer_phone}
                onChange={(e) => setFarmerData(prev => ({...prev, farmer_phone: e.target.value}))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                placeholder="+234 XXX XXX XXXX"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input
                type="text"
                required
                value={farmerData.farmer_location}
                onChange={(e) => setFarmerData(prev => ({...prev, farmer_location: e.target.value}))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                placeholder="State, Nigeria"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Crops (comma separated)</label>
              <input
                type="text"
                required
                value={farmerData.crops}
                onChange={(e) => setFarmerData(prev => ({...prev, crops: e.target.value}))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                placeholder="Rice, Yam, Cassava"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Farm Size</label>
              <input
                type="text"
                required
                value={farmerData.farm_size}
                onChange={(e) => setFarmerData(prev => ({...prev, farm_size: e.target.value}))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                placeholder="e.g., 5 hectares"
              />
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
              >
                Add Farmer
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const AddProductModal = ({ onClose, onAdd }) => {
    const [productData, setProductData] = useState({
      title: '',
      description: '',
      category: 'grains_legumes',
      subcategory: 'rice',
      price_per_unit: '',
      unit_of_measure: 'kg',
      quantity_available: '',
      minimum_order_quantity: '',
      location: '',
      farm_name: '',
      farmer_id: demoData.farmers[0]?.id || '',
      farmer_name: demoData.farmers[0]?.farmer_name || '',
      can_deliver_shipping: true,
      can_deliver_dropoff: true,
      shipping_cost_per_unit: '',
      dropoff_delivery_cost: ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      const newProduct = {
        ...productData,
        price_per_unit: parseFloat(productData.price_per_unit),
        quantity_available: parseInt(productData.quantity_available),
        minimum_order_quantity: parseInt(productData.minimum_order_quantity),
        shipping_cost_per_unit: productData.shipping_cost_per_unit ? parseFloat(productData.shipping_cost_per_unit) : 0,
        dropoff_delivery_cost: productData.dropoff_delivery_cost ? parseFloat(productData.dropoff_delivery_cost) : 0,
        processing_level: 'not_processed',
        images: ['https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400']
      };
      
      const addedProduct = DemoModeManager.addDemoProduct(newProduct);
      onAdd(addedProduct);
      onClose();
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Add New Product</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">×</button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Product Title</label>
                <input
                  type="text"
                  required
                  value={productData.title}
                  onChange={(e) => setProductData(prev => ({...prev, title: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  placeholder="e.g., Premium Local Rice"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  required
                  value={productData.description}
                  onChange={(e) => setProductData(prev => ({...prev, description: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  rows="2"
                  placeholder="Product description"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={productData.category}
                  onChange={(e) => setProductData(prev => ({...prev, category: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="grains_legumes">Grains & Legumes</option>
                  <option value="tubers_roots">Tubers & Roots</option>
                  <option value="spices_vegetables">Spices & Vegetables</option>
                  <option value="fish_meat">Fish & Meat</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Price per Unit (₦)</label>
                <input
                  type="number"
                  required
                  min="1"
                  value={productData.price_per_unit}
                  onChange={(e) => setProductData(prev => ({...prev, price_per_unit: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  placeholder="500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Unit of Measure</label>
                <select
                  value={productData.unit_of_measure}
                  onChange={(e) => setProductData(prev => ({...prev, unit_of_measure: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="kg">Kilogram (kg)</option>
                  <option value="tuber">Tuber</option>
                  <option value="bag">Bag</option>
                  <option value="carton">Carton</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantity Available</label>
                <input
                  type="number"
                  required
                  min="1"
                  value={productData.quantity_available}
                  onChange={(e) => setProductData(prev => ({...prev, quantity_available: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  placeholder="100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input
                  type="text"
                  required
                  value={productData.location}
                  onChange={(e) => setProductData(prev => ({...prev, location: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  placeholder="State, Nigeria"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Farm Name</label>
                <input
                  type="text"
                  required
                  value={productData.farm_name}
                  onChange={(e) => setProductData(prev => ({...prev, farm_name: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  placeholder="Farm name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Select Farmer</label>
                <select
                  value={productData.farmer_id}
                  onChange={(e) => {
                    const farmer = demoData.farmers.find(f => f.id === e.target.value);
                    setProductData(prev => ({
                      ...prev, 
                      farmer_id: e.target.value,
                      farmer_name: farmer?.farmer_name || ''
                    }));
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                >
                  {demoData.farmers.map(farmer => (
                    <option key={farmer.id} value={farmer.id}>
                      {farmer.farmer_name} - {farmer.farmer_location}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
              >
                Add Product
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Farmers</p>
              <p className="text-2xl font-bold">{metrics.totalFarmers}</p>
            </div>
            <span className="text-3xl">👨‍🌾</span>
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Products Listed</p>
              <p className="text-2xl font-bold">{metrics.totalProducts}</p>
            </div>
            <span className="text-3xl">📦</span>
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Total Orders</p>
              <p className="text-2xl font-bold">{metrics.totalOrders}</p>
            </div>
            <span className="text-3xl">🛒</span>
          </div>
        </div>

        <div className="bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Total Revenue</p>
              <p className="text-2xl font-bold">₦{metrics.totalRevenue.toLocaleString()}</p>
            </div>
            <span className="text-3xl">💰</span>
          </div>
        </div>

        <div className="bg-gradient-to-r from-red-500 to-red-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-sm">Commission Earned</p>
              <p className="text-2xl font-bold">₦{metrics.totalCommission.toLocaleString()}</p>
            </div>
            <span className="text-3xl">🏆</span>
          </div>
        </div>

        <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-indigo-100 text-sm">Completed Orders</p>
              <p className="text-2xl font-bold">{metrics.completedOrders}</p>
            </div>
            <span className="text-3xl">✅</span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {demoData.orders.slice(0, 5).map((order) => (
            <div key={order.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">{order.product_name}</p>
                <p className="text-sm text-gray-600">Order from {order.buyer_name}</p>
                <p className="text-xs text-gray-500">{new Date(order.order_date).toLocaleDateString()}</p>
              </div>
              <div className="text-right">
                <p className="font-medium">₦{order.total_amount.toLocaleString()}</p>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  order.status === 'delivered' ? 'bg-green-100 text-green-600' :
                  order.status === 'processing' ? 'bg-yellow-100 text-yellow-600' :
                  'bg-blue-100 text-blue-600'
                }`}>
                  {order.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderFarmersTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Farmers Network</h3>
        <button
          onClick={() => setShowAddFarmerModal(true)}
          className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 flex items-center space-x-2"
        >
          <span>+</span>
          <span>Add Farmer</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {demoData.farmers.map((farmer) => (
          <div key={farmer.id} className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{farmer.farmer_name}</h4>
                <p className="text-sm text-gray-600">{farmer.farmer_phone}</p>
                <p className="text-sm text-gray-600">📍 {farmer.farmer_location}</p>
                <p className="text-sm text-gray-600">🏡 {farmer.farm_size}</p>
              </div>
              <span className="text-2xl">👨‍🌾</span>
            </div>
            <div className="mt-3">
              <p className="text-xs text-gray-500 mb-1">Crops:</p>
              <div className="flex flex-wrap gap-1">
                {farmer.crops.map((crop, index) => (
                  <span key={index} className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded">
                    {crop}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderProductsTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Products Management</h3>
        <button
          onClick={() => setShowAddProductModal(true)}
          className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 flex items-center space-x-2"
        >
          <span>+</span>
          <span>Add Product</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {demoData.products.map((product) => (
          <div key={product.id} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <img 
              src={product.images[0]} 
              alt={product.title}
              className="w-full h-32 object-cover"
            />
            <div className="p-4">
              <h4 className="font-medium text-gray-900 mb-2">{product.title}</h4>
              <p className="text-sm text-gray-600 mb-2">{product.description}</p>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Price:</span>
                  <span className="font-medium">₦{product.price_per_unit}/{product.unit_of_measure}</span>
                </div>
                <div className="flex justify-between">
                  <span>Available:</span>
                  <span>{product.quantity_available} {product.unit_of_measure}</span>
                </div>
                <div className="flex justify-between">
                  <span>Farmer:</span>
                  <span>{product.farmer_name}</span>
                </div>
                <div className="flex justify-between">
                  <span>Location:</span>
                  <span>{product.location}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderOrdersTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Orders Management</h3>
      
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Buyer</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {demoData.orders.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">{order.id.slice(-8)}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{order.product_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{order.buyer_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">₦{order.total_amount.toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      order.status === 'delivered' ? 'bg-green-100 text-green-600' :
                      order.status === 'processing' ? 'bg-yellow-100 text-yellow-600' :
                      'bg-blue-100 text-blue-600'
                    }`}>
                      {order.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{new Date(order.order_date).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-gray-100 z-40 overflow-y-auto">
      <div className="min-h-screen">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-3">
                <h1 className="text-xl font-semibold text-gray-900">Demo Agent Dashboard</h1>
                <span className="bg-orange-100 text-orange-600 px-2 py-1 rounded text-xs font-medium">DEMO MODE</span>
              </div>
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Close Dashboard
              </button>
            </div>
          </div>
        </div>

        {/* Tabs Navigation */}
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="flex space-x-8">
              {[
                { id: 'overview', label: 'Overview', icon: '📊' },
                { id: 'farmers', label: 'Farmers', icon: '👨‍🌾' },
                { id: 'products', label: 'Products', icon: '📦' },
                { id: 'orders', label: 'Orders', icon: '🛒' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-emerald-500 text-emerald-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'farmers' && renderFarmersTab()}
          {activeTab === 'products' && renderProductsTab()}
          {activeTab === 'orders' && renderOrdersTab()}
        </div>
      </div>

      {/* Modals */}
      {showAddFarmerModal && (
        <AddFarmerModal
          onClose={() => setShowAddFarmerModal(false)}
          onAdd={(farmer) => {
            setDemoData(prev => ({
              ...prev,
              farmers: [...prev.farmers, farmer]
            }));
          }}
        />
      )}

      {showAddProductModal && (
        <AddProductModal
          onClose={() => setShowAddProductModal(false)}
          onAdd={(product) => {
            setDemoData(prev => ({
              ...prev,
              products: [...prev.products, product]
            }));
          }}
        />
      )}
    </div>
  );
};

export default DemoAgentDashboard;