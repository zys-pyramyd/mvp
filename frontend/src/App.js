import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

// Custom Icons as SVG components using provided designs
const AddToCartIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M9.25 8V5.25H6.5V3.75H9.25V1H10.75V3.75H13.5V5.25H10.75V8H9.25ZM5.49563 18C5.08188 18 4.72917 17.8527 4.4375 17.5581C4.14583 17.2635 4 16.9094 4 16.4956C4 16.0819 4.14729 15.7292 4.44188 15.4375C4.73646 15.1458 5.09062 15 5.50437 15C5.91813 15 6.27083 15.1473 6.5625 15.4419C6.85417 15.7365 7 16.0906 7 16.5044C7 16.9181 6.85271 17.2708 6.55813 17.5625C6.26354 17.8542 5.90938 18 5.49563 18ZM14.4956 18C14.0819 18 13.7292 17.8527 13.4375 17.5581C13.1458 17.2635 13 16.9094 13 16.4956C13 16.0819 13.1473 15.7292 13.4419 15.4375C13.7365 15.1458 14.0906 15 14.5044 15C14.9181 15 15.2708 15.1473 15.5625 15.4419C15.8542 15.7365 16 16.0906 16 16.5044C16 16.9181 15.8527 17.2708 15.5581 17.5625C15.2635 17.8542 14.9094 18 14.4956 18ZM1 3.5V2H3.77083L7 9.5H13.2708L15.625 4H17.25L14.6458 10.0833C14.5208 10.3611 14.3368 10.5833 14.0938 10.75C13.8507 10.9167 13.5764 11 13.2708 11H6.60417L5.72917 12.5H16V14H5.75C5.16667 14 4.72917 13.7465 4.4375 13.2396C4.14583 12.7326 4.14583 12.2361 4.4375 11.75L5.52083 9.875L2.79167 3.5H1Z" fill="currentColor"/>
  </svg>
);

const TruckIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M5.75 16.5C5.0556 16.5 4.4653 16.2569 3.9792 15.7708C3.4931 15.2847 3.25 14.6944 3.25 14H1.5L2 12.5H3.75C3.9861 12.1944 4.2794 11.9514 4.63 11.7708C4.9804 11.5903 5.3538 11.5 5.75 11.5C6.1462 11.5 6.5196 11.5903 6.87 11.7708C7.2206 11.9514 7.5139 12.1944 7.75 12.5H11.8333L13.5833 5.5H4.5L4.6667 5C4.7778 4.69444 4.9618 4.45139 5.2188 4.27083C5.4757 4.09028 5.7639 4 6.0833 4H15.5L14.75 7H16.5L19 10.5L18 14H17C17 14.6944 16.7569 15.2847 16.2708 15.7708C15.7847 16.2569 15.1944 16.5 14.5 16.5C13.8056 16.5 13.2153 16.2569 12.7292 15.7708C12.2431 15.2847 12 14.6944 12 14H8.25C8.25 14.6944 8.0069 15.2847 7.5208 15.7708C7.0347 16.2569 6.4444 16.5 5.75 16.5ZM13.75 11H17.2917L17.3542 10.7708L15.7292 8.5H14.375L13.75 11ZM0.5 11.1667L0.875 9.66667H5L4.625 11.1667H0.5ZM2 8.33333L2.375 6.83333H7.25L6.875 8.33333H2ZM5.75 15C6.0333 15 6.2708 14.9042 6.4625 14.7125C6.6542 14.5208 6.75 14.2833 6.75 14C6.75 13.7167 6.6542 13.4792 6.4625 13.2875C6.2708 13.0958 6.0333 13 5.75 13C5.4667 13 5.2292 13.0958 5.0375 13.2875C4.8458 13.4792 4.75 13.7167 4.75 14C4.75 14.2833 4.8458 14.5208 4.0375 14.7125C5.2292 14.9042 5.4667 15 5.75 15ZM14.5 15C14.7833 15 15.0208 14.9042 15.2125 14.7125C15.4042 14.5208 15.5 14.2833 15.5 14C15.5 13.7167 15.4042 13.4792 15.2125 13.2875C15.0208 13.0958 14.7833 13 14.5 13C14.2167 13 13.9792 13.0958 13.7875 13.2875C13.5958 13.4792 13.5 13.7167 13.5 14C13.5 14.2833 13.5958 14.5208 13.7875 14.7125C13.9792 14.9042 14.2167 15 14.5 15Z" fill="currentColor"/>
  </svg>
);

const MessageIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M18 18L15 15H7.5C7.0875 15 6.7344 14.8531 6.4406 14.5594C6.1469 14.2656 6 13.9125 6 13.5V12.5H14C14.4125 12.5 14.7656 12.3531 15.0594 12.0594C15.3531 11.7656 15.5 11.4125 15.5 11V6H16.5C16.9125 6 17.2656 6.14688 17.5594 6.44063C17.8531 6.73438 18 7.0875 18 7.5V18ZM3.5 10.375L4.375 9.5H12.5V3.5H3.5V10.375ZM2 14V3.5C2 3.0875 2.1469 2.73438 2.4406 2.44063C2.7344 2.14688 3.0875 2 3.5 2H12.5C12.9125 2 13.2656 2.14688 13.5594 2.44063C13.8531 2.73438 14 3.0875 14 3.5V9.5C14 9.9125 13.8531 10.2656 13.5594 10.5594C13.2656 10.8531 12.9125 11 12.5 11H5L2 14Z" fill="currentColor"/>
  </svg>
);

const ProfileIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4.938 14.0625C5.688 13.5347 6.49 13.1424 7.344 12.8854C8.198 12.6285 9.083 12.5 10 12.5C10.917 12.5 11.802 12.6285 12.656 12.8854C13.51 13.1424 14.312 13.5347 15.062 14.0625C15.549 13.4931 15.91 12.8611 16.146 12.1667C16.382 11.4722 16.5 10.75 16.5 10C16.5 8.19903 15.866 6.66542 14.599 5.39917C13.332 4.13305 11.798 3.5 9.995 3.5C8.193 3.5 6.66 4.13305 5.396 5.39917C4.132 6.66542 3.5 8.19903 3.5 10C3.5 10.75 3.618 11.4722 3.854 12.1667C4.09 12.8611 4.451 13.4931 4.938 14.0625ZM10 11.5C9.167 11.5 8.458 11.2083 7.875 10.625C7.292 10.0417 7 9.33333 7 8.5C7 7.66667 7.292 6.95833 7.875 6.375C8.458 5.79167 9.167 5.5 10 5.5C10.833 5.5 11.542 5.79167 12.125 6.375C12.708 6.95833 13 7.66667 13 8.5C13 9.33333 12.708 10.0417 12.125 10.625C11.542 11.2083 10.833 11.5 10 11.5ZM10.006 18C8.905 18 7.868 17.7917 6.896 17.375C5.924 16.9583 5.073 16.3854 4.344 15.6562C3.615 14.9271 3.042 14.0767 2.625 13.105C2.208 12.1333 2 11.0951 2 9.99042C2 8.88569 2.208 7.85069 2.625 6.88542C3.042 5.92014 3.615 5.07292 4.344 4.34375C5.073 3.61458 5.923 3.04167 6.895 2.625C7.867 2.20833 8.905 2 10.01 2C11.114 2 12.149 2.20833 13.115 2.625C14.08 3.04167 14.927 3.61458 15.656 4.34375C16.385 5.07292 16.958 5.92167 17.375 6.89C17.792 7.85847 18 8.89319 18 9.99417C18 11.0953 17.792 12.1319 17.375 13.1042C16.958 14.0764 16.385 14.9271 15.656 15.6562C14.927 16.3854 14.078 16.9583 13.11 17.375C12.142 17.7917 11.107 18 10.006 18ZM10 16.5C10.722 16.5 11.417 16.3854 12.083 16.1562C12.75 15.9271 13.375 15.5903 13.958 15.1458C13.361 14.7708 12.729 14.4861 12.062 14.2917C11.396 14.0972 10.708 14 10 14C9.292 14 8.601 14.0938 7.927 14.2812C7.253 14.4688 6.625 14.7569 6.042 15.1458C6.625 15.5903 7.25 15.9271 7.917 16.1562C8.583 16.3854 9.278 16.5 10 16.5ZM10 10C10.417 10 10.771 9.85417 11.062 9.5625C11.354 9.27083 11.5 8.91667 11.5 8.5C11.5 8.08333 11.354 7.72917 11.062 7.4375C10.771 7.14583 10.417 7 10 7C9.583 7 9.229 7.14583 8.938 7.4375C8.646 7.72917 8.5 8.08333 8.5 8.5C8.5 8.91667 8.646 9.27083 8.938 9.5625C9.229 9.85417 9.583 10 10 10Z" fill="currentColor"/>
  </svg>
);

function App() {
  const [user, setUser] = useState(null);
  const [currentPlatform, setCurrentPlatform] = useState('pyhub');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [showRoleSelection, setShowRoleSelection] = useState(false);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState([]);
  const [showCart, setShowCart] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Auth form states
  const [authForm, setAuthForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    password: '',
    phone: ''
  });

  useEffect(() => {
    // Check for saved token
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserProfile(token);
    }
    
    fetchProducts();
    fetchCategories();
  }, [currentPlatform, selectedCategory, searchTerm]);

  const fetchUserProfile = async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        
        // Set platform based on role
        if (userData.role) {
          const platformMap = {
            'farmer': 'pyhub',
            'agent': 'pyhub',
            'storage_owner': 'pyhub',
            'logistics_business': 'pyhub',
            'super_agent': 'pyhub'
          };
          setCurrentPlatform(platformMap[userData.role] || 'pyexpress');
        }
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      let url = `${API_BASE_URL}/api/products?platform=${currentPlatform}`;
      if (selectedCategory) url += `&category=${selectedCategory}`;
      if (searchTerm) url += `&search=${searchTerm}`;
      
      const response = await fetch(url);
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/categories`);
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    
    try {
      const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const body = authMode === 'login' 
        ? { email: authForm.email, password: authForm.password }
        : authForm;

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        setUser(data.user);
        setShowAuthModal(false);
        
        if (!data.user.role) {
          setShowRoleSelection(true);
        }
        
        setAuthForm({
          first_name: '',
          last_name: '',
          username: '',
          email: '',
          password: '',
          phone: ''
        });
      } else {
        const error = await response.json();
        alert(error.detail);
      }
    } catch (error) {
      console.error('Auth error:', error);
      alert('An error occurred. Please try again.');
    }
  };

  const handleRoleSelection = async (role, isBuyer = false) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/auth/select-role`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ role, is_buyer: isBuyer })
      });

      if (response.ok) {
        const data = await response.json();
        setUser(prev => ({ ...prev, role: data.role }));
        setCurrentPlatform(data.platform);
        setShowRoleSelection(false);
      }
    } catch (error) {
      console.error('Role selection error:', error);
    }
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.product_id === product.id);
    
    if (existingItem) {
      setCart(cart.map(item => 
        item.product_id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { product_id: product.id, quantity: 1, product }]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.product_id !== productId));
  };

  const updateCartQuantity = (productId, quantity) => {
    if (quantity === 0) {
      removeFromCart(productId);
    } else {
      setCart(cart.map(item => 
        item.product_id === productId 
          ? { ...item, quantity }
          : item
      ));
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setCart([]);
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.product.price_per_unit * item.quantity), 0);
  const cartItemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <img 
                src="https://customer-assets.emergentagent.com/job_pyramyd-agritech/artifacts/ml8alcyl_image.png" 
                alt="Pyramyd" 
                className="h-8 w-auto"
              />
            </div>

            {/* Platform Toggle */}
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setCurrentPlatform('pyhub')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentPlatform === 'pyhub'
                    ? 'bg-emerald-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                PyHub
              </button>
              <button
                onClick={() => setCurrentPlatform('pyexpress')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentPlatform === 'pyexpress'
                    ? 'bg-emerald-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                PyExpress
              </button>
            </div>

            {/* Right side actions */}
            <div className="flex items-center space-x-4">
              {/* Cart */}
              <button
                onClick={() => setShowCart(true)}
                className="relative p-2 text-gray-600 hover:text-emerald-600 transition-colors"
              >
                <CartIcon />
                {cartItemCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-emerald-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {cartItemCount}
                  </span>
                )}
              </button>

              {/* User Menu */}
              {user ? (
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-gray-700">
                    Welcome, {user.first_name}
                  </span>
                  <button
                    onClick={logout}
                    className="text-sm text-gray-600 hover:text-gray-900"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors"
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Platform Description */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {currentPlatform === 'pyhub' ? 'PyHub - Farm Direct' : 'PyExpress - Quick Delivery'}
          </h1>
          <p className="text-gray-600">
            {currentPlatform === 'pyhub' 
              ? 'Connect directly with farmers and agents for fresh produce from the source'
              : 'Fast delivery of quality produce from suppliers and processors'
            }
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map(product => (
            <div key={product.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
              <div className="h-48 bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">No Image</span>
              </div>
              
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-1">{product.title}</h3>
                <p className="text-sm text-gray-600 mb-2 truncate">{product.description}</p>
                
                <div className="flex justify-between items-center mb-2">
                  <span className="text-lg font-bold text-emerald-600">
                    ₦{product.price_per_unit.toLocaleString()}/{product.unit_of_measure}
                  </span>
                  <span className="text-sm text-gray-500">
                    {product.quantity_available} available
                  </span>
                </div>
                
                <div className="text-xs text-gray-500 mb-3">
                  {product.listed_by_agent ? (
                    <>
                      <div>Listed by: {product.agent_name}</div>
                      <div>Farm: {product.farm_name}</div>
                    </>
                  ) : (
                    <div>Seller: {product.seller_name}</div>
                  )}
                  <div>Location: {product.location}</div>
                </div>
                
                <button
                  onClick={() => addToCart(product)}
                  className="w-full bg-emerald-600 text-white py-2 px-4 rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium"
                >
                  Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>

        {products.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No products found</p>
          </div>
        )}
      </main>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                {authMode === 'login' ? 'Sign In' : 'Sign Up'}
              </h2>
              <button
                onClick={() => setShowAuthModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleAuth} className="space-y-4">
              {authMode === 'register' && (
                <>
                  <input
                    type="text"
                    placeholder="First Name"
                    value={authForm.first_name}
                    onChange={(e) => setAuthForm(prev => ({...prev, first_name: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                  <input
                    type="text"
                    placeholder="Last Name"
                    value={authForm.last_name}
                    onChange={(e) => setAuthForm(prev => ({...prev, last_name: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                  <input
                    type="text"
                    placeholder="Username"
                    value={authForm.username}
                    onChange={(e) => setAuthForm(prev => ({...prev, username: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                  />
                  <input
                    type="tel"
                    placeholder="Phone (optional)"
                    value={authForm.phone}
                    onChange={(e) => setAuthForm(prev => ({...prev, phone: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </>
              )}
              
              <input
                type="email"
                placeholder="Email"
                value={authForm.email}
                onChange={(e) => setAuthForm(prev => ({...prev, email: e.target.value}))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                required
              />
              
              <input
                type="password"
                placeholder="Password"
                value={authForm.password}
                onChange={(e) => setAuthForm(prev => ({...prev, password: e.target.value}))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                required
              />

              <button
                type="submit"
                className="w-full bg-emerald-600 text-white py-2 px-4 rounded-lg hover:bg-emerald-700 transition-colors font-medium"
              >
                {authMode === 'login' ? 'Sign In' : 'Sign Up'}
              </button>
            </form>

            <p className="mt-4 text-center text-sm text-gray-600">
              {authMode === 'login' ? "Don't have an account? " : "Already have an account? "}
              <button
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                className="text-emerald-600 hover:text-emerald-700 font-medium"
              >
                {authMode === 'login' ? 'Sign Up' : 'Sign In'}
              </button>
            </p>
          </div>
        </div>
      )}

      {/* Role Selection Modal */}
      {showRoleSelection && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <h2 className="text-2xl font-bold mb-6 text-center">Welcome to Pyramyd!</h2>
            <p className="text-gray-600 mb-6 text-center">
              Choose how you'd like to use the platform:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Buyer Path */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4 text-center">🛒 Explore as a Buyer</h3>
                <p className="text-sm text-gray-600 mb-4 text-center">
                  Find fresh produce for your needs!
                </p>
                
                <div className="space-y-2">
                  <button
                    onClick={() => handleRoleSelection('general_buyer', true)}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    General Consumer
                  </button>
                  <button
                    onClick={() => handleRoleSelection('retailer', true)}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    Retailer
                  </button>
                  <button
                    onClick={() => handleRoleSelection('restaurant', true)}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    Restaurant
                  </button>
                  <button
                    onClick={() => handleRoleSelection('hotel', true)}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    Hotel
                  </button>
                  <button
                    onClick={() => handleRoleSelection('cafe', true)}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    Cafe
                  </button>
                </div>
              </div>

              {/* Partner Path */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4 text-center">🤝 Register as a Partner</h3>
                <p className="text-sm text-gray-600 mb-4 text-center">
                  Grow your business with Pyramyd!
                </p>
                
                <div className="space-y-2">
                  <button
                    onClick={() => handleRoleSelection('farmer')}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    Farmer
                  </button>
                  <button
                    onClick={() => handleRoleSelection('agent')}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    Agent
                  </button>
                  <button
                    onClick={() => handleRoleSelection('supplier')}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    Supplier
                  </button>
                  <button
                    onClick={() => handleRoleSelection('processor')}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    Processor
                  </button>
                  <button
                    onClick={() => handleRoleSelection('storage_owner')}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    Storage Owner
                  </button>
                  <button
                    onClick={() => handleRoleSelection('logistics_business')}
                    className="w-full text-left px-3 py-2 rounded border hover:bg-gray-50"
                  >
                    Logistics Business
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cart Sidebar */}
      {showCart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50">
          <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-lg">
            <div className="p-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold">Shopping Cart</h2>
                <button
                  onClick={() => setShowCart(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-4 flex-1 overflow-y-auto">
              {cart.length === 0 ? (
                <p className="text-gray-500 text-center">Your cart is empty</p>
              ) : (
                <div className="space-y-4">
                  {cart.map(item => (
                    <div key={item.product_id} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-medium">{item.product.title}</h4>
                        <p className="text-sm text-gray-600">
                          ₦{item.product.price_per_unit.toLocaleString()}/{item.product.unit_of_measure}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => updateCartQuantity(item.product_id, item.quantity - 1)}
                          className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50"
                        >
                          -
                        </button>
                        <span className="w-8 text-center">{item.quantity}</span>
                        <button
                          onClick={() => updateCartQuantity(item.product_id, item.quantity + 1)}
                          className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50"
                        >
                          +
                        </button>
                      </div>
                      
                      <button
                        onClick={() => removeFromCart(item.product_id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {cart.length > 0 && (
              <div className="p-4 border-t border-gray-200">
                <div className="flex justify-between items-center mb-4">
                  <span className="font-semibold">Total:</span>
                  <span className="font-bold text-lg">₦{cartTotal.toLocaleString()}</span>
                </div>
                
                <button
                  disabled={!user}
                  className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg hover:bg-emerald-700 transition-colors font-medium disabled:bg-gray-400 disabled:cursor-not-allowed"
                  onClick={() => {
                    if (!user) {
                      setShowAuthModal(true);
                    } else {
                      alert('Checkout functionality coming soon!');
                    }
                  }}
                >
                  {user ? 'Proceed to Checkout' : 'Sign In to Checkout'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;