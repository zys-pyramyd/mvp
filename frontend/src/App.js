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
  // Initialize with Home page (formerly PyExpress) as default
  const [currentPlatform, setCurrentPlatform] = useState('home');
  const [showBuyFromFarm, setShowBuyFromFarm] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [showRoleSelection, setShowRoleSelection] = useState(false);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState([]);
  const [showCart, setShowCart] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Enhanced messaging state
  const [showMessaging, setShowMessaging] = useState(false);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [usernameSearch, setUsernameSearch] = useState('');
  const [foundUsers, setFoundUsers] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [showOrderTracking, setShowOrderTracking] = useState(false);
  const [orders, setOrders] = useState([]);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  
  // Pre-order and filtering state
  const [showCreatePreOrder, setShowCreatePreOrder] = useState(false);
  const [showPreOrderDetails, setShowPreOrderDetails] = useState(false);
  const [selectedPreOrder, setSelectedPreOrder] = useState(null);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  
  // Product Detail Page state
  const [showProductDetail, setShowProductDetail] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  const [filters, setFilters] = useState({
    category: '',
    location: '',
    min_price: '',
    max_price: '',
    only_preorders: false,
    seller_type: ''
  });
  // Driver system state
  const [showDriverPortal, setShowDriverPortal] = useState(false);
  const [showLogisticsDashboard, setShowLogisticsDashboard] = useState(false);
  const [showAddDriver, setShowAddDriver] = useState(false);
  const [showCreateDeliveryRequest, setShowCreateDeliveryRequest] = useState(false);
  const [driverStatus, setDriverStatus] = useState('offline');
  const [availableDeliveries, setAvailableDeliveries] = useState([]);
  const [myDrivers, setMyDrivers] = useState([]);
  const [myVehicles, setMyVehicles] = useState([]);
  const [newDriverForm, setNewDriverForm] = useState({
    driver_name: '',
    phone_number: '',
    email: '',
    profile_picture: '',
    driver_license: '',
    vehicle_type: 'motorcycle',
    plate_number: '',
    make_model: '',
    color: '',
    year: ''
  });
  // Enhanced driver system state
  const [driverSearch, setDriverSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [showDriverMessages, setShowDriverMessages] = useState(false);
  const [deliveryMessages, setDeliveryMessages] = useState([]);
  const [currentDeliveryChat, setCurrentDeliveryChat] = useState('');
  const [newDeliveryMessage, setNewDeliveryMessage] = useState('');
  const [pickupCoordinates, setPickupCoordinates] = useState(null);
  const [deliveryCoordinates, setDeliveryCoordinates] = useState([]);
  const [showMap, setShowMap] = useState(false);
  const [trackingData, setTrackingData] = useState(null);
  const [multipleDestinations, setMultipleDestinations] = useState(['']);
  
  // Checkout and cart management state
  const [showCheckout, setShowCheckout] = useState(false);
  const [checkoutStep, setCheckoutStep] = useState('review'); // 'review', 'address', 'payment'
  const [shippingAddress, setShippingAddress] = useState({
    full_name: '',
    phone: '',
    email: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'Nigeria',
    delivery_instructions: ''
  });
  const [deliveryFees, setDeliveryFees] = useState({});
  const [orderSummary, setOrderSummary] = useState({
    subtotal: 0,
    delivery_total: 0,
    total: 0,
    item_count: 0
  });
  
  const [enhancedDeliveryForm, setEnhancedDeliveryForm] = useState({
    order_id: '',
    order_type: 'regular',
    pickup_address: '',
    delivery_addresses: [''],
    total_quantity: '',
    quantity_unit: 'kg',
    product_details: '',
    weight_kg: '',
    special_instructions: '',
    estimated_price: '',
    preferred_driver_username: ''
  });
  const [preOrderForm, setPreOrderForm] = useState({
    product_name: '',
    product_category: 'vegetables',
    description: '',
    total_stock: '',
    unit: 'kg',
    price_per_unit: '',
    partial_payment_percentage: 0.3,
    location: '',
    delivery_date: '',
    business_name: '',
    farm_name: '',
    images: []
  });
  
  // Slide state
  const [currentSlide, setCurrentSlide] = useState(0);
  
  // Slide content with different background colors and CTAs
  const slideContent = [
    {
      title: currentPlatform === 'buy_from_farm' ? 'PyHub - Buy from Farm' : 'Pyramyd',
      description: currentPlatform === 'buy_from_farm' 
        ? 'Buy fresh produce directly from farms and get the best quality at source prices'
        : 'Your comprehensive agricultural marketplace connecting farmers, suppliers, and buyers',
      bgGradient: 'from-emerald-100 to-emerald-50',
      cta: null
    },
    {
      title: 'Join Our Agent Network',
      description: 'Earn commissions while helping farmers reach more customers. Connect producers with buyers and grow your income.',
      bgGradient: 'from-blue-100 to-blue-50',
      cta: {
        text: 'Become an Agent',
        action: 'agent_register'
      }
    },
    {
      title: 'Suppliers & Processors Welcome',
      description: 'List your products and reach thousands of buyers. Expand your market reach with our platform.',
      bgGradient: 'from-purple-100 to-purple-50',
      cta: {
        text: 'Become a Supplier',
        action: 'supplier_register'
      }
    },
    {
      title: 'Hotels, Cafes & Restaurants',
      description: 'Source fresh ingredients directly from farms and suppliers. Get the best prices for your business needs.',
      bgGradient: 'from-orange-100 to-orange-50',
      cta: {
        text: 'Register Your Business',
        action: 'business_register'
      }
    },
    {
      title: 'Fast & Reliable Delivery',
      description: 'Quick delivery with our network of verified drivers and logistics partners nationwide.',
      bgGradient: 'from-green-100 to-green-50',
      cta: null
    }
  ];
  
  // Auth form states - Updated structure
  const [authForm, setAuthForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email_or_phone: '', // Can be email or phone
    password: '',
    phone: '', // Optional additional phone
    gender: '',
    date_of_birth: ''
  });

  // Registration flow states
  const [registrationStep, setRegistrationStep] = useState('basic'); // 'basic', 'role_path', 'buyer_type', 'business_info', 'partner_type', 'verification'
  const [selectedUserPath, setSelectedUserPath] = useState(''); // 'buyer' or 'partner'
  const [selectedBuyerType, setSelectedBuyerType] = useState('');
  const [businessInfo, setBusinessInfo] = useState({
    business_name: '',
    business_address: '',
    city: '',
    state: '',
    country: '',
    home_address: '' // For non-business users
  });
  const [partnerType, setPartnerType] = useState('');
  const [businessCategory, setBusinessCategory] = useState(''); // For business partners
  const [verificationInfo, setVerificationInfo] = useState({
    nin: '',
    cac_number: '',
    photo: '',
    farm_photo: '',
    farm_info: ''
  });

  // Category data with images
  const categoryData = [
    { 
      value: 'sea_food', 
      label: 'Sea Food', 
      image: 'https://images.unsplash.com/photo-1615141982883-c7ad0e69fd62?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxzZWFmb29kfGVufDB8fHx8MTc1Mzk1MzU5NHww&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'grain', 
      label: 'Grain', 
      image: 'https://images.unsplash.com/photo-1499529112087-3cb3b73cec95?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwzfHxhZ3JpY3VsdHVyYWwlMjBwcm9kdWN0c3xlbnwwfHx8fDE3NTM5NTM1ODd8MA&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'legumes', 
      label: 'Legumes', 
      image: 'https://images.unsplash.com/photo-1709236550338-e2bcc3beee70?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwxfHxhZ3JpY3VsdHVyYWwlMjBwcm9kdWN0c3xlbnwwfHx8fDE3NTM5NTM1ODd8MA&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'vegetables', 
      label: 'Vegetables', 
      image: 'https://images.unsplash.com/photo-1529313780224-1a12b68bed16?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHw0fHxhZ3JpY3VsdHVyYWwlMjBwcm9kdWN0c3xlbnwwfHx8fDE3NTM5NTM1ODd8MA&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'spices', 
      label: 'Spices', 
      image: 'https://images.unsplash.com/photo-1506368249639-73a05d6f6488?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxzcGljZXN8ZW58MHx8fHwxNzUzOTUzNjAwfDA&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'fruits', 
      label: 'Fruits', 
      image: 'https://images.unsplash.com/photo-1610832958506-aa56368176cf?crop=entropy&cs=srgb&fm=jpg&ixid=M3w0MjI5Nzh8MHwxfHNlYXJjaHwxfHxmcnVpdHN8ZW58MHx8fHwxNzUzOTUzNjUwfDA&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'cash_crop', 
      label: 'Cash Crop', 
      image: 'https://images.unsplash.com/photo-1502395809857-fd80069897d0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHwxfHxjb3R0b258ZW58MHx8fHwxNzUzOTUzNjM4fDA&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'fertilizer', 
      label: 'Fertilizer', 
      image: 'https://images.unsplash.com/photo-1655130944329-b3a63166f6b5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwxfHxmZXJ0aWxpemVyfGVufDB8fHx8MTc1Mzk1MzYwOHww&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'herbicides', 
      label: 'Herbicides', 
      image: 'https://images.unsplash.com/photo-1581578017093-cd30fce4eeb7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwzfHxmZXJ0aWxpemVyfGVufDB8fHx8MTc1Mzk1MzYwOHww&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'pesticides', 
      label: 'Pesticides', 
      image: 'https://images.unsplash.com/photo-1581578017093-cd30fce4eeb7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwzfHxmZXJ0aWxpemVyfGVufDB8fHx8MTc1Mzk1MzYwOHww&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'seeds', 
      label: 'Seeds', 
      image: 'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwxfHxzZWVkc3xlbnwwfHx8fDE3NTM5NTM2MTZ8MA&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'fish', 
      label: 'Fish', 
      image: 'https://images.pexels.com/photos/725992/pexels-photo-725992.jpeg' 
    },
    { 
      value: 'meat', 
      label: 'Meat', 
      image: 'https://images.unsplash.com/photo-1551028150-64b9f398f678?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxtZWF0fGVufDB8fHx8MTc1Mzk1MzYyMnww&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'packaged_goods', 
      label: 'Packaged Goods', 
      image: 'https://images.unsplash.com/photo-1741522226997-a34b5a45c648?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwxfHxwYWNrYWdlZCUyMGZvb2R8ZW58MHx8fHwxNzUzOTUzNjQ0fDA&ixlib=rb-4.1.0&q=85' 
    },
    { 
      value: 'feeds', 
      label: 'Feeds', 
      image: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwxfHxhbmltYWwlMjBmZWVkfGVufDB8fHx8MTc1Mzk1MzY1MHww&ixlib=rb-4.1.0&q=85' 
    }
  ];

  useEffect(() => {
    // Enforce platform restrictions based on user role
    if (user && user.role) {
      const allowedPlatforms = getUserPlatformAccess(user.role);
      if (!allowedPlatforms.includes(currentPlatform)) {
        setCurrentPlatform(allowedPlatforms[0]); // Set to the first allowed platform
      }
    }
  }, [user]);

  useEffect(() => {
    // Check for saved token
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserProfile(token);
    }
    
    fetchProducts();
    fetchCategories();
    
    // Migrate existing cart items to ensure proper structure
    if (cart.length > 0) {
      migrateCartItems();
    }
  }, [currentPlatform, selectedCategory, searchTerm]);

  // Auto-change slides every 5 seconds
  useEffect(() => {
    const slideInterval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slideContent.length);
    }, 5000);

    return () => clearInterval(slideInterval);
  }, [slideContent.length]);

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
      const platform = currentPlatform === 'buy_from_farm' ? 'buy_from_farm' : 'home';
      let url = `${process.env.REACT_APP_BACKEND_URL}/api/products?platform=${platform}`;
      
      // Add category filter
      const categoryFilter = selectedCategory || filters.category;
      if (categoryFilter) {
        url += `&category=${categoryFilter}`;
      }
      
      // Add search term
      if (searchTerm) {
        url += `&search_term=${searchTerm}`;
      }
      
      // Add advanced filters
      if (filters.location) {
        url += `&location=${filters.location}`;
      }
      if (filters.min_price) {
        url += `&min_price=${filters.min_price}`;
      }
      if (filters.max_price) {
        url += `&max_price=${filters.max_price}`;
      }
      if (filters.only_preorders) {
        url += `&only_preorders=true`;
      }
      if (filters.seller_type) {
        url += `&seller_type=${filters.seller_type}`;
      }
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        
        // Handle new API response format with both products and preorders
        let allProducts = [];
        if (data.products && Array.isArray(data.products)) {
          allProducts = [...allProducts, ...data.products];
        }
        if (data.preorders && Array.isArray(data.preorders)) {
          // Ensure pre-orders have type='preorder' for filtering
          const preordersWithType = data.preorders.map(preorder => ({ ...preorder, type: 'preorder' }));
          allProducts = [...allProducts, ...preordersWithType];
        }
        
        // Fallback for legacy API response
        if (Array.isArray(data)) {
          allProducts = data;
        }
        
        setProducts(allProducts);
      } else {
        console.error('Failed to fetch products');
        setProducts([]); // Set empty array on error
      }
    } catch (error) {
      console.error('Error fetching products:', error);
      setProducts([]); // Set empty array on error
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

  const handleBasicRegistration = async (e) => {
    e.preventDefault();
    // Just move to role path selection after basic form
    setRegistrationStep('role_path');
  };

  const handleRolePath = (path) => {
    setSelectedUserPath(path);
    if (path === 'buyer') {
      setRegistrationStep('buyer_type');
    } else {
      setRegistrationStep('partner_type');
    }
  };

  const handleBuyerTypeSelection = (type) => {
    setSelectedBuyerType(type);
    if (type === 'others') {
      // Will need custom business type input
      setRegistrationStep('business_info');
    } else if (type === 'skip') {
      // Just collect home address
      setRegistrationStep('home_address');
    } else {
      setRegistrationStep('business_info');
    }
  };

  const handlePartnerTypeSelection = (type) => {
    setPartnerType(type);
    if (type === 'business') {
      setRegistrationStep('business_category');
    } else {
      setRegistrationStep('verification');
    }
  };

  const handleBusinessCategory = (category) => {
    setBusinessCategory(category);
    setRegistrationStep('verification');
  };

  const completeRegistration = async () => {
    try {
      // Submit complete registration to backend
      const registrationData = {
        ...authForm,
        user_path: selectedUserPath,
        buyer_type: selectedBuyerType,
        business_info: businessInfo,
        partner_type: partnerType,
        business_category: businessCategory,
        verification_info: verificationInfo
      };

      const response = await fetch(`${API_BASE_URL}/api/auth/complete-registration`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(registrationData)
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        setUser(data.user);
        setShowAuthModal(false);
        
        // Reset registration flow
        setRegistrationStep('basic');
        setSelectedUserPath('');
        setSelectedBuyerType('');
        setPartnerType('');
        setBusinessCategory('');
        
        setAuthForm({
          first_name: '',
          last_name: '',
          username: '',
          email_or_phone: '',
          password: '',
          phone: '',
          gender: '',
          date_of_birth: ''
        });
      } else {
        const error = await response.json();
        alert(error.detail);
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('An error occurred. Please try again.');
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    
    try {
      // Handle login
      const body = { 
        email_or_phone: authForm.email_or_phone, 
        password: authForm.password 
      };

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
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
        
        setAuthForm({
          first_name: '',
          last_name: '',
          username: '',
          email_or_phone: '',
          password: '',
          phone: '',
          gender: '',
          date_of_birth: ''
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

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.product_id === product.id);
    
    if (existingItem) {
      setCart(cart.map(item => 
        item.product_id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      const cartItem = {
        id: `cart-${Date.now()}-${product.id}`, // Unique cart item ID
        product_id: product.id,
        quantity: 1,
        product,
        unit: product.unit || 'kg',
        unit_specification: product.unit_specification || '',
        delivery_method: 'platform' // Default delivery method
      };
      setCart([...cart, cartItem]);
    }
    
    // Calculate order summary after adding
    setTimeout(() => calculateOrderSummary(), 100);
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
    
    // Calculate order summary after updating
    setTimeout(() => calculateOrderSummary(), 100);
  };

  // Migrate existing cart items to ensure they have proper structure
  const migrateCartItems = () => {
    setCart(prevCart => 
      prevCart.map(item => {
        if (!item.id) {
          return {
            ...item,
            id: `cart-${Date.now()}-${item.product_id}`,
            unit: item.unit || item.product?.unit || 'kg',
            unit_specification: item.unit_specification || item.product?.unit_specification || '',
            delivery_method: item.delivery_method || 'platform'
          };
        }
        return item;
      })
    );
  };

  // Product Detail functions
  const openProductDetail = (product) => {
    setSelectedProduct(product);
    setShowProductDetail(true);
  };

  const closeProductDetail = () => {
    setShowProductDetail(false);
    setSelectedProduct(null);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setCart([]);
    setShowProfileMenu(false);
  };

  // Audio recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];
      
      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
      setMediaRecorder(null);
    }
  };

  const sendAudioMessage = async () => {
    if (audioBlob && selectedConversation) {
      // Convert audio blob to base64
      const reader = new FileReader();
      reader.onload = () => {
        const base64Audio = reader.result;
        const audioMessage = {
          id: Date.now(),
          type: 'audio',
          content: base64Audio,
          sender: user.username,
          timestamp: new Date().toISOString(),
          conversation_id: selectedConversation.id
        };
        
        setMessages(prev => [...prev, audioMessage]);
        setAudioBlob(null);
        
        // Here you would send to backend
        // sendMessageToBackend(audioMessage);
      };
      reader.readAsDataURL(audioBlob);
    }
  };

  // Username search function
  const searchUsers = async (searchTerm) => {
    if (searchTerm.length < 2) {
      setFoundUsers([]);
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/search?username=${searchTerm}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const users = await response.json();
        setFoundUsers(users);
      }
    } catch (error) {
      console.error('Error searching users:', error);
    }
  };

  // Driver system functions
  const fetchAvailableDeliveries = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/delivery/available`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAvailableDeliveries(data.delivery_requests || []);
      }
    } catch (error) {
      console.error('Error fetching deliveries:', error);
    }
  };

  const updateDriverStatus = async (status) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/drivers/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status })
      });
      
      if (response.ok) {
        setDriverStatus(status);
        if (status === 'online') {
          fetchAvailableDeliveries();
        }
      }
    } catch (error) {
      console.error('Error updating driver status:', error);
    }
  };

  const acceptDelivery = async (requestId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/delivery/${requestId}/accept`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Delivery accepted! OTP: ${result.delivery_otp}\nPickup: ${result.pickup_address}\nDelivery: ${result.delivery_address}`);
        fetchAvailableDeliveries();
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error accepting delivery:', error);
      alert('Error accepting delivery');
    }
  };

  // Enhanced driver system functions
  const searchDrivers = async (pickupLocation) => {
    try {
      const token = localStorage.getItem('token');
      let url = `${process.env.REACT_APP_BACKEND_URL}/api/drivers/search?min_rating=3.0&radius_km=50`;
      
      if (pickupLocation && pickupLocation.lat && pickupLocation.lng) {
        url += `&pickup_lat=${pickupLocation.lat}&pickup_lng=${pickupLocation.lng}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.drivers || []);
      }
    } catch (error) {
      console.error('Error searching drivers:', error);
    }
  };

  const createEnhancedDeliveryRequest = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/delivery/request-enhanced`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...enhancedDeliveryForm,
          total_quantity: parseFloat(enhancedDeliveryForm.total_quantity),
          weight_kg: enhancedDeliveryForm.weight_kg ? parseFloat(enhancedDeliveryForm.weight_kg) : null,
          estimated_price: parseFloat(enhancedDeliveryForm.estimated_price),
          pickup_coordinates: pickupCoordinates,
          delivery_coordinates: deliveryCoordinates
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Delivery request created successfully! 
        Request ID: ${result.request_id}
        Total destinations: ${result.total_destinations}
        Quantity: ${result.total_quantity} ${result.quantity_unit}
        Estimated price: ₦${result.estimated_price}
        OTP: ${result.delivery_otp}`);
        
        setShowCreateDeliveryRequest(false);
        // Reset form
        setEnhancedDeliveryForm({
          order_id: '',
          order_type: 'regular',
          pickup_address: '',
          delivery_addresses: [''],
          total_quantity: '',
          quantity_unit: 'kg',
          product_details: '',
          weight_kg: '',
          special_instructions: '',
          estimated_price: '',
          preferred_driver_username: ''
        });
        setMultipleDestinations(['']);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || 'Failed to create delivery request'}`);
      }
    } catch (error) {
      console.error('Error creating delivery request:', error);
      alert('Error creating delivery request. Please try again.');
    }
  };

  const sendDeliveryMessage = async (requestId, content, type = 'text') => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/delivery/${requestId}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content,
          type,
          location_data: type === 'location' ? pickupCoordinates : null
        })
      });

      if (response.ok) {
        fetchDeliveryMessages(requestId); // Refresh messages
        setNewDeliveryMessage('');
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const fetchDeliveryMessages = async (requestId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/delivery/${requestId}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDeliveryMessages(data.messages || []);
        setTrackingData(data.delivery_request);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const updateDriverLocation = async (lat, lng, address) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/drivers/location`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ lat, lng, address })
      });
    } catch (error) {
      console.error('Error updating location:', error);
    }
  };

  const addDeliveryDestination = () => {
    setMultipleDestinations([...multipleDestinations, '']);
    setEnhancedDeliveryForm(prev => ({
      ...prev,
      delivery_addresses: [...prev.delivery_addresses, '']
    }));
  };

  const removeDeliveryDestination = (index) => {
    const newDestinations = multipleDestinations.filter((_, i) => i !== index);
    setMultipleDestinations(newDestinations);
    setEnhancedDeliveryForm(prev => ({
      ...prev,
      delivery_addresses: prev.delivery_addresses.filter((_, i) => i !== index)
    }));
  };

  const updateDeliveryDestination = (index, value) => {
    const newDestinations = [...multipleDestinations];
    newDestinations[index] = value;
    setMultipleDestinations(newDestinations);
    
    const newAddresses = [...enhancedDeliveryForm.delivery_addresses];
    newAddresses[index] = value;
    setEnhancedDeliveryForm(prev => ({
      ...prev,
      delivery_addresses: newAddresses
    }));
  };

  const fetchMyDrivers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/logistics/my-drivers`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMyDrivers(data.drivers || []);
        setMyVehicles(data.vehicles || []);
      }
    } catch (error) {
      console.error('Error fetching drivers:', error);
    }
  };

  const addEnhancedToCart = (product, quantity, unit, specification, deliveryMethod) => {
    const existingItem = cart.find(item => item.product_id === (product.id || product._id));
    
    if (existingItem) {
      // Update existing item
      setCart(prevCart => prevCart.map(item => 
        item.product_id === (product.id || product._id)
          ? { 
              ...item, 
              quantity: item.quantity + quantity,
              unit: unit,
              unit_specification: specification,
              delivery_method: deliveryMethod
            }
          : item
      ));
    } else {
      // Add new item with consistent structure
      const cartItem = {
        id: `cart-${Date.now()}-${product.id || product._id}`,
        product_id: product.id || product._id,
        product: product,
        quantity: quantity,
        unit: unit,
        unit_specification: specification,
        delivery_method: deliveryMethod
      };
      
      setCart(prevCart => [...prevCart, cartItem]);
    }
    
    const quantityDisplay = `${quantity} ${unit}${specification ? ` (${specification})` : ''}`;
    const deliveryDisplay = deliveryMethod === 'offline' ? 'Offline Delivery' : 'Platform Driver';
    
    // Calculate order summary after adding
    setTimeout(() => calculateOrderSummary(), 100);
    
    alert(`Added to cart: ${quantityDisplay} of ${product.product_name || product.crop_type}\nDelivery: ${deliveryDisplay}`);
  };

  const updateOrderStatus = async (orderId, status, deliveryStatus = null) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/${orderId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          order_id: orderId,
          status: status,
          delivery_status: deliveryStatus
        })
      });

      if (response.ok) {
        alert(`Order status updated to: ${status}${deliveryStatus ? ` (${deliveryStatus})` : ''}`);
        // Refresh orders if orders view is open
        fetchMyOrders('seller');
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error updating order status:', error);
      alert('Error updating order status');
    }
  };

  const fetchMyOrders = async (orderType = 'buyer') => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/my-orders?order_type=${orderType}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setOrders(data.orders || []);
      }
    } catch (error) {
      console.error('Error fetching orders:', error);
    }
  };

  // Checkout and cart management functions
  const calculateOrderSummary = () => {
    let subtotal = 0;
    let deliveryTotal = 0;
    let itemCount = 0;

    cart.forEach(item => {
      const itemTotal = item.product.price_per_unit * item.quantity;
      subtotal += itemTotal;
      itemCount += item.quantity;
      
      // Calculate delivery fees based on method
      if (item.delivery_method === 'platform') {
        // Platform delivery fee calculation (could be based on distance, weight, etc.)
        const baseDeliveryFee = 500; // Base fee of ₦500
        const weightMultiplier = (item.product.weight_kg || 1) * 50; // ₦50 per kg
        deliveryTotal += baseDeliveryFee + weightMultiplier;
      } else {
        // Offline delivery - might have different fee structure or be free
        deliveryTotal += 200; // Minimal handling fee for offline delivery
      }
    });

    const total = subtotal + deliveryTotal;
    
    setOrderSummary({
      subtotal,
      delivery_total: deliveryTotal,
      total,
      item_count: itemCount
    });
    
    return { subtotal, delivery_total: deliveryTotal, total, item_count: itemCount };
  };

  const updateCartItemQuantity = (itemId, newQuantity) => {
    if (newQuantity <= 0) {
      removeCartItem(itemId);
      return;
    }
    
    setCart(prevCart => 
      prevCart.map(item => 
        item.id === itemId 
          ? { ...item, quantity: newQuantity }
          : item
      )
    );
    calculateOrderSummary();
  };

  const removeCartItem = (itemId) => {
    setCart(prevCart => prevCart.filter(item => item.id !== itemId));
    calculateOrderSummary();
  };

  const updateCartItemDeliveryMethod = (itemId, deliveryMethod) => {
    setCart(prevCart => 
      prevCart.map(item => 
        item.id === itemId 
          ? { ...item, delivery_method: deliveryMethod }
          : item
      )
    );
    calculateOrderSummary();
  };

  const proceedToCheckout = () => {
    if (cart.length === 0) {
      alert('Your cart is empty!');
      return;
    }
    
    calculateOrderSummary();
    setCheckoutStep('review');
    setShowCheckout(true);
    setShowCart(false);
  };

  const validateAddress = () => {
    const required = ['full_name', 'phone', 'address_line_1', 'city', 'state'];
    const missing = required.filter(field => !shippingAddress[field].trim());
    
    if (missing.length > 0) {
      alert(`Please fill in the following required fields: ${missing.join(', ')}`);
      return false;
    }
    
    // Basic phone validation
    if (!/^\+?[\d\s-()]+$/.test(shippingAddress.phone)) {
      alert('Please enter a valid phone number');
      return false;
    }
    
    return true;
  };

  const createOrder = async () => {
    try {
      if (!validateAddress()) return;
      
      const token = localStorage.getItem('token');
      const orders = [];
      
      // Create individual orders for each cart item (to handle different sellers)
      for (const item of cart) {
        const orderData = {
          product_id: item.product.id || item.product._id,
          quantity: item.quantity,
          unit: item.unit,
          unit_specification: item.unit_specification,
          shipping_address: `${shippingAddress.full_name}, ${shippingAddress.address_line_1}, ${shippingAddress.address_line_2 ? shippingAddress.address_line_2 + ', ' : ''}${shippingAddress.city}, ${shippingAddress.state}, ${shippingAddress.country}`,
          delivery_method: item.delivery_method
        };
        
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/create`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(orderData)
        });
        
        if (response.ok) {
          const result = await response.json();
          orders.push(result);
        } else {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to create order');
        }
      }
      
      // Clear cart and show success
      setCart([]);
      setShowCheckout(false);
      
      alert(`Orders created successfully! 
      Total orders: ${orders.length}
      Total amount: ₦${orderSummary.total}
      Order IDs: ${orders.map(o => o.order_id).join(', ')}`);
      
      return orders;
      
    } catch (error) {
      console.error('Error creating orders:', error);
      alert(`Error creating orders: ${error.message}`);
      return null;
    }
  };

  const startConversation = (targetUser) => {
    const conversation = {
      id: `conv_${user.username}_${targetUser.username}`,
      participants: [user.username, targetUser.username],
      name: targetUser.first_name + ' ' + targetUser.last_name,
      avatar: targetUser.username.charAt(0).toUpperCase()
    };
    
    setSelectedConversation(conversation);
    setFoundUsers([]);
    setUsernameSearch('');
  };

  const sendMessage = () => {
    if (newMessage.trim() && selectedConversation) {
      const message = {
        id: Date.now(),
        type: 'text',
        content: newMessage,
        sender: user.username,
        timestamp: new Date().toISOString(),
        conversation_id: selectedConversation.id
      };
      setMessages(prev => [...prev, message]);
      setNewMessage('');
      
      // Here you would send to backend
      // sendMessageToBackend(message);
    }
  };

  const fetchOrders = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/orders`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setOrders(data);
      }
    } catch (error) {
      console.error('Error fetching orders:', error);
    }
  };

  // Pre-order Functions (replacing Group Buying Functions)
  // TODO: Implement pre-order functionality
  /*
  const searchBuyers = async (username) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/users/search?username=${username}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFoundBuyers(data);
      }
    } catch (error) {
      console.error('Error searching buyers:', error);
    }
  };

  const addBuyerToGroup = (buyer, quantity) => {
    const existingBuyer = groupBuyingData.buyers.find(b => b.id === buyer.id);
    if (!existingBuyer) {
      setGroupBuyingData(prev => ({
        ...prev,
        buyers: [...prev.buyers, { ...buyer, quantity }],
        quantity: prev.quantity + quantity
      }));
    }
  };

  const removeBuyerFromGroup = (buyerId) => {
    const buyer = groupBuyingData.buyers.find(b => b.id === buyerId);
    if (buyer) {
      setGroupBuyingData(prev => ({
        ...prev,
        buyers: prev.buyers.filter(b => b.id !== buyerId),
        quantity: prev.quantity - buyer.quantity
      }));
    }
  };

  const fetchPriceRecommendations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/group-buying/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          produce: groupBuyingData.produce,
          category: groupBuyingData.category,
          quantity: groupBuyingData.quantity,
          location: groupBuyingData.location
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setGroupBuyingData(prev => ({
          ...prev,
          recommendations: data.recommendations
        }));
        setGroupBuyingStep('recommendations');
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const createGroupOrder = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/group-buying/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...groupBuyingData,
          agent_id: user.id
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert('Group order created successfully!');
        setShowGroupBuying(false);
        // Reset group buying data
        setGroupBuyingData({
          produce: '',
          category: '',
          quantity: 0,
          location: '',
          buyers: [],
          recommendations: [],
          selectedPrice: null,
          commissionType: 'pyramyd'
        });
        setGroupBuyingStep('search');
      }
    } catch (error) {
      console.error('Error creating group order:', error);
    }
  };
  */

  const getUserPlatformAccess = (userRole) => {
    // All users can access both home page and buy from farm
    return ['home', 'buy_from_farm'];
  };

  const canSwitchPlatforms = (userRole) => {
    // All users can switch between main page and buy from farm
    return true;
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.product.price_per_unit * item.quantity), 0);
  const cartItemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  // CTA Handlers for slides
  const handleSlideAction = (action) => {
    if (action === 'agent_register') {
      setSelectedUserPath('partner');
      setPartnerType('agent');
      setRegistrationStep('basic');
      setAuthMode('register');
      setShowAuthModal(true);
    } else if (action === 'supplier_register') {
      setSelectedUserPath('partner');
      setPartnerType('business');
      setBusinessCategory('supplier');
      setRegistrationStep('basic');
      setAuthMode('register');
      setShowAuthModal(true);
    } else if (action === 'business_register') {
      setSelectedUserPath('buyer');
      setSelectedBuyerType('hotel'); // Default to hotel, user can change
      setRegistrationStep('basic');
      setAuthMode('register');
      setShowAuthModal(true);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            {/* Logo */}
            <div className="flex items-center flex-shrink-0">
              <img 
                src="https://customer-assets.emergentagent.com/job_pyramyd-agritech/artifacts/ml8alcyl_image.png" 
                alt="Pyramyd" 
                className="h-6 w-auto sm:h-8 lg:h-10"
              />
            </div>

            {/* Platform Navigation - Responsive */}
            <div className="flex items-center bg-gray-100 rounded-lg p-1 mx-2 sm:mx-4">
              <button
                onClick={() => setCurrentPlatform('home')}
                className={`px-2 sm:px-3 py-1 sm:py-2 rounded-md text-xs sm:text-sm font-medium transition-colors ${
                  currentPlatform === 'home'
                    ? 'bg-emerald-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Home
              </button>
              <button
                onClick={() => setCurrentPlatform('buy_from_farm')}
                className={`px-2 sm:px-3 py-1 sm:py-2 rounded-md text-xs sm:text-sm font-medium transition-colors ${
                  currentPlatform === 'buy_from_farm'
                    ? 'bg-emerald-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <span className="hidden sm:inline">Buy from Farm</span>
                <span className="sm:hidden">Farm</span>
              </button>
            </div>

            {/* Right side navigation icons - Responsive */}
            <div className="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
              {/* Cart - Responsive */}
              <button
                onClick={() => setShowCart(true)}
                className="nav-button icon-button relative p-1.5 sm:p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg border border-gray-200 hover:border-emerald-500"
                title="Shopping Cart"
              >
                <div className="w-5 h-5 sm:w-6 sm:h-6">
                  <AddToCartIcon />
                </div>
                {cartItemCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-emerald-600 text-white text-xs rounded-full h-4 w-4 sm:h-5 sm:w-5 flex items-center justify-center font-semibold text-xs">
                    {cartItemCount}
                  </span>
                )}
              </button>

              {/* Messaging - Responsive */}
              <button
                onClick={() => {
                  if (!user) {
                    setShowAuthModal(true);
                  } else {
                    setShowMessaging(true);
                  }
                }}
                className="nav-button icon-button relative p-1.5 sm:p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg border border-gray-200 hover:border-emerald-500"
                title="Messages"
              >
                <div className="w-5 h-5 sm:w-6 sm:h-6">
                  <MessageIcon />
                </div>
                {user && messages.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 sm:h-5 sm:w-5 flex items-center justify-center font-semibold text-xs">
                    {messages.length}
                  </span>
                )}
              </button>

              {/* Order Tracking - Responsive */}
              <button
                onClick={() => {
                  if (!user) {
                    setShowAuthModal(true);
                  } else {
                    setShowOrderTracking(true);
                    fetchOrders();
                  }
                }}
                className="nav-button icon-button p-1.5 sm:p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg border border-gray-200 hover:border-emerald-500"
                title="Track Orders / Find Drivers"
              >
                <div className="w-5 h-5 sm:w-6 sm:h-6">
                  <TruckIcon />
                </div>
              </button>

              {/* Profile Icon with Dropdown - Responsive */}
              <div className="relative">
                {!user ? (
                  <button
                    onClick={() => setShowAuthModal(true)}
                    className="nav-button icon-button flex items-center space-x-1 sm:space-x-2 p-1.5 sm:p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg border border-gray-200 hover:border-emerald-500"
                    title="Sign In"
                  >
                    <div className="w-5 h-5 sm:w-6 sm:h-6">
                      <ProfileIcon />
                    </div>
                    <span className="hidden md:block text-sm font-medium">Sign In</span>
                  </button>
                ) : (
                  <button
                    onClick={() => setShowProfileMenu(!showProfileMenu)}
                    className="nav-button icon-button flex items-center space-x-1 sm:space-x-2 p-1.5 sm:p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg border border-gray-200 hover:border-emerald-500"
                    title="Profile Menu"
                  >
                    <div className="w-5 h-5 sm:w-6 sm:h-6">
                      <ProfileIcon />
                    </div>
                    <span className="hidden md:block text-sm font-medium">
                      {user.first_name}
                    </span>
                  </button>
                )}

                {/* Profile Dropdown */}
                {showProfileMenu && (
                  <div className="profile-dropdown absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                    <div className="py-1">
                      <div className="px-4 py-3 border-b border-gray-100">
                        <p className="text-sm font-medium text-gray-900">{user.first_name} {user.last_name}</p>
                        <p className="text-xs text-gray-500">{user.role?.replace('_', ' ').toUpperCase()}</p>
                      </div>
                      
                      <button
                        onClick={() => {
                          setShowProfileMenu(false);
                          // Add profile management functionality here
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        👤 My Profile
                      </button>

                      <button
                        onClick={() => {
                          setShowProfileMenu(false);
                          // Add dashboard functionality where users manage all activities
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-50 font-medium"
                      >
                        🏠 My Dashboard
                      </button>

                      {/* Show "Become a Partner" for non-agents */}
                      {user.role !== 'agent' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            handleSlideAction('agent_register');
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-emerald-600 hover:bg-gray-50 font-medium"
                        >
                          🤝 Become a Partner
                        </button>
                      )}
                      
                      {/* Group Buying menu item - commented out for pre-order functionality */}
                      {/* 
                      {user.role === 'agent' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            setShowGroupBuying(true);
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        >
                          Group Buying
                        </button>
                      )}
                      */}
                      
                      <button
                        onClick={() => {
                          setShowProfileMenu(false);
                          fetchOrders();
                          setShowOrderTracking(true);
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        My Orders
                      </button>
                      
                      <button
                        onClick={() => {
                          setShowProfileMenu(false);
                          // Add wallet functionality here
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        My Wallet
                      </button>
                      
                      {/* Driver Portal - For independent drivers */}
                      {user.role === 'driver' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            setShowDriverPortal(true);
                            fetchAvailableDeliveries();
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-50 font-medium"
                        >
                          🚛 Driver Portal
                        </button>
                      )}
                      
                      {/* Logistics Dashboard - For logistics businesses */}
                      {user.partner_type === 'business' && user.business_category === 'logistics_business' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            setShowLogisticsDashboard(true);
                            fetchMyDrivers();
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-gray-50 font-medium"
                        >
                          📋 Logistics Dashboard
                        </button>
                      )}
                      
                      {/* Seller Dashboard - For sellers to manage orders */}
                      {user.role && ['agent', 'farmer', 'supplier', 'processor'].includes(user.role) && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            fetchMyOrders('seller');
                            setShowOrderTracking(true);
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-gray-50 font-medium"
                        >
                          📊 Seller Dashboard
                        </button>
                      )}
                      
                      {/* Request Delivery - For sellers */}
                      {user.role && ['agent', 'farmer', 'supplier', 'processor'].includes(user.role) && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            setShowCreateDeliveryRequest(true);
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-orange-600 hover:bg-gray-50 font-medium"
                        >
                          🚚 Request Delivery
                        </button>
                      )}
                      
                      {/* Show "Become an Agent" for non-agents */}
                      {user.role !== 'agent' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            handleSlideAction('agent_register');
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-emerald-600 hover:bg-gray-50 font-medium"
                        >
                          Become an Agent
                        </button>
                      )}
                      
                      <button
                        onClick={() => {
                          setShowProfileMenu(false);
                          window.open('https://hilorgx.com', '_blank');
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Report an Issue
                      </button>
                      
                      <div className="border-t border-gray-100">
                        <button
                          onClick={logout}
                          className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50"
                        >
                          Logout
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-base"
            />
            <button className="absolute right-3 top-3 text-emerald-600 hover:text-emerald-700">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Auto-changing Slides */}
        <div className="mb-6">
          <div className={`relative bg-gradient-to-r ${slideContent[currentSlide].bgGradient} rounded-xl p-6 overflow-hidden transition-all duration-500`}>
            <div className="text-center">
              <div className="min-h-[100px] flex flex-col items-center justify-center">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-3">
                    {slideContent[currentSlide].title}
                  </h2>
                  <p className="text-gray-600 text-sm mb-4">
                    {slideContent[currentSlide].description}
                  </p>
                  
                  {/* CTA Button */}
                  {slideContent[currentSlide].cta && (
                    <button
                      onClick={() => handleSlideAction(slideContent[currentSlide].cta.action)}
                      className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors shadow-md hover:shadow-lg transform hover:scale-105 duration-200"
                    >
                      {slideContent[currentSlide].cta.text}
                    </button>
                  )}
                </div>
              </div>
              
              {/* Pagination dots */}
              <div className="flex justify-center space-x-2 mt-4">
                {slideContent.map((_, index) => (
                  <div 
                    key={index}
                    onClick={() => setCurrentSlide(index)}
                    className={`w-2 h-2 rounded-full cursor-pointer transition-colors ${
                      index === currentSlide ? 'bg-emerald-500' : 'bg-gray-300 hover:bg-gray-400'
                    }`}
                  ></div>
                ))}
              </div>
            </div>
            
            {/* Background decoration */}
            <div className="absolute top-0 right-0 transform translate-x-4 -translate-y-4 opacity-10">
              <svg className="w-32 h-32" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        {/* Advanced Filters Toggle */}
        <div className="mb-4 flex justify-between items-center">
          <button
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
            </svg>
            <span>Advanced Filters</span>
            <svg className={`w-4 h-4 transition-transform ${showAdvancedFilters ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {/* Create Pre-order Button - Only for sellers */}
          {user && ['farmer', 'supplier', 'processor', 'agent'].includes(user.role) && (
            <button
              onClick={() => setShowCreatePreOrder(true)}
              className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium"
            >
              + Create Pre-order
            </button>
          )}
        </div>

        {/* Advanced Filters Panel */}
        {showAdvancedFilters && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Location Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input
                  type="text"
                  placeholder="e.g., Lagos, Kano"
                  value={filters.location}
                  onChange={(e) => setFilters(prev => ({ ...prev, location: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              {/* Price Range */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Min Price (₦)</label>
                <input
                  type="number"
                  placeholder="Min price"
                  value={filters.min_price}
                  onChange={(e) => setFilters(prev => ({ ...prev, min_price: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Price (₦)</label>
                <input
                  type="number"
                  placeholder="Max price"
                  value={filters.max_price}
                  onChange={(e) => setFilters(prev => ({ ...prev, max_price: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              {/* Seller Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Seller Type</label>
                <select
                  value={filters.seller_type}
                  onChange={(e) => setFilters(prev => ({ ...prev, seller_type: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                >
                  <option value="">All Sellers</option>
                  <option value="farmer">Farmers</option>
                  <option value="supplier">Suppliers</option>
                  <option value="processor">Processors</option>
                  <option value="agent">Agents</option>
                </select>
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between">
              {/* Pre-orders Only Toggle */}
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={filters.only_preorders}
                  onChange={(e) => setFilters(prev => ({ ...prev, only_preorders: e.target.checked }))}
                  className="w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500"
                />
                <span className="text-sm font-medium text-gray-700">Show only pre-orders</span>
              </label>

              {/* Filter Actions */}
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    setFilters({
                      category: '',
                      location: '',
                      min_price: '',
                      max_price: '',
                      only_preorders: false,
                      seller_type: ''
                    });
                    setSelectedCategory('');
                  }}
                  className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Clear All
                </button>
                <button
                  onClick={() => {
                    fetchProducts();
                    setShowAdvancedFilters(false);
                  }}
                  className="px-4 py-1 text-sm text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Categories - Swipeable Cards */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Shop by Category</h3>
          <div className="flex overflow-x-auto space-x-4 pb-4 scrollbar-hide">
            {/* All Categories Card */}
            <div
              onClick={() => setSelectedCategory('')}
              className={`flex-shrink-0 cursor-pointer transition-all duration-200 ${
                selectedCategory === '' ? 'transform scale-105' : 'hover:transform hover:scale-105'
              }`}
            >
              <div className="w-24 h-24 rounded-xl overflow-hidden mb-2 bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
                <span className="text-white text-xs font-medium">All</span>
              </div>
              <p className="text-xs text-center text-gray-700 font-medium">All Categories</p>
            </div>

            {/* Category Cards */}
            {categoryData.map(category => (
              <div
                key={category.value}
                onClick={() => setSelectedCategory(category.value)}
                className={`flex-shrink-0 cursor-pointer transition-all duration-200 ${
                  selectedCategory === category.value ? 'transform scale-105' : 'hover:transform hover:scale-105'
                }`}
              >
                <div className={`w-24 h-24 rounded-xl overflow-hidden mb-2 border-2 transition-colors ${
                  selectedCategory === category.value ? 'border-emerald-500' : 'border-gray-200'
                }`}>
                  <img
                    src={category.image}
                    alt={category.label}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96" fill="%23f3f4f6"><rect width="96" height="96" fill="%23f3f4f6"/><text x="48" y="48" text-anchor="middle" dy="0.3em" font-family="Arial" font-size="12" fill="%236b7280">' + category.label + '</text></svg>';
                    }}
                  />
                </div>
                <p className="text-xs text-center text-gray-700 font-medium">{category.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Pre-Order Sales Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900">🔥 Pre-Order Sales</h3>
              <p className="text-sm text-gray-600">Secure your products in advance with special pre-order pricing!</p>
            </div>
            <button
              onClick={() => {
                setFilters(prev => ({ ...prev, only_preorders: true }));
                fetchProducts();
              }}
              className="px-3 sm:px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors font-medium text-xs sm:text-sm"
            >
              See More →
            </button>
          </div>

          {/* Pre-Order Products Horizontal Scroll */}
          <div className="relative">
            <div className="flex overflow-x-auto space-x-3 sm:space-x-4 pb-4 scrollbar-hide">
              {products.filter(product => product.type === 'preorder').slice(0, 6).map((product, index) => (
                <div key={`preorder-${product.id || product._id || index}`} className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg shadow-md hover:shadow-lg transition-all flex-shrink-0 w-72 sm:w-80 border-2 border-orange-200 hover:border-orange-300 cursor-pointer">
                  {/* Pre-Order Badge */}
                  <div 
                    className="relative"
                    onClick={() => openProductDetail(product)}
                    title="Click to view product details"
                  >
                    {product.images && product.images.length > 0 ? (
                      <img 
                        src={product.images[0]} 
                        alt={product.product_name || product.crop_type}
                        className="w-full h-32 sm:h-40 object-cover rounded-t-lg"
                      />
                    ) : (
                      <div className="w-full h-32 sm:h-40 bg-gradient-to-r from-orange-200 to-orange-300 flex items-center justify-center rounded-t-lg">
                        <span className="text-orange-600 font-medium text-sm sm:text-base">🌾 Pre-Order Product</span>
                      </div>
                    )}
                    
                    <div className="absolute top-2 left-2 bg-orange-500 text-white px-2 sm:px-3 py-1 rounded-full text-xs font-bold flex items-center">
                      ⚡ PRE-ORDER
                    </div>
                    
                    {/* Pre-order percentage badge */}
                    <div className="absolute top-2 right-2 bg-red-500 text-white px-1.5 sm:px-2 py-1 rounded-full text-xs font-bold">
                      -{Math.round((1 - (product.partial_payment_percentage || 0.3)) * 100)}% OFF
                    </div>
                  </div>

                  <div className="p-3 sm:p-4">
                    <h4 className="font-bold text-gray-900 mb-2 text-sm sm:text-base line-clamp-1">
                      {product.product_name || product.crop_type}
                    </h4>
                    
                    {/* Enhanced Pricing for Pre-orders */}
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-base sm:text-lg font-bold text-orange-600">
                        ₦{product.price_per_unit}/{product.unit || product.unit_of_measure || 'kg'}
                        {(product.unit_specification || product.unit_of_measure !== (product.unit || 'kg')) && 
                          <span className="text-xs sm:text-sm font-medium text-gray-600 ml-1">
                            ({product.unit_specification || product.unit_of_measure || 'standard'})
                          </span>
                        }
                      </span>
                    </div>

                    {/* Pre-order specific info */}
                    <div className="mb-3 p-2 sm:p-3 bg-orange-50 rounded-lg border border-orange-200">
                      <div className="text-xs text-orange-800 space-y-1">
                        <div className="flex justify-between">
                          <span>💰 Partial Payment:</span>
                          <span className="font-bold">{Math.round((product.partial_payment_percentage || 0.3) * 100)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>📦 Available:</span>
                          <span className="font-bold">{product.available_stock || product.total_stock} {product.unit}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>🚚 Delivery:</span>
                          <span className="font-bold text-xs">{new Date(product.delivery_date).toLocaleDateString()}</span>
                        </div>
                        {product.orders_count > 0 && (
                          <div className="flex justify-between">
                            <span>👥 Pre-orders:</span>
                            <span className="font-bold text-green-600">{product.orders_count}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Location */}
                    <div className="text-xs text-gray-600 mb-3 flex items-center line-clamp-1">
                      📍 {product.location}
                    </div>

                    {/* Action button */}
                    <button
                      onClick={() => {
                        const quantity = 1;
                        const unit = product.unit || 'kg';
                        const specification = product.unit_specification || '';
                        const deliveryMethod = 'platform';
                        
                        addEnhancedToCart(product, quantity, unit, specification, deliveryMethod);
                      }}
                      className="w-full py-2 px-3 sm:px-4 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-medium transition-colors text-xs sm:text-sm"
                    >
                      🛒 Add Pre-order to Cart
                    </button>
                  </div>
                </div>
              ))}
              
              {/* Show message if no pre-orders */}
              {products.filter(product => product.type === 'preorder').length === 0 && (
                <div className="w-full text-center py-6 sm:py-8 bg-orange-50 rounded-lg border-2 border-dashed border-orange-200">
                  <div className="text-orange-600">
                    <div className="text-xl sm:text-2xl mb-2">📦</div>
                    <h4 className="font-medium text-gray-700 text-sm sm:text-base">No Pre-Orders Available</h4>
                    <p className="text-xs sm:text-sm text-gray-500">Check back soon for exciting pre-order deals!</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Products Grid - Responsive */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6 auto-rows-auto items-start">{/* Made responsive and reduced gap for mobile */}
          {products.length === 0 ? (
            <div className="col-span-full text-center py-8 sm:py-12">
              <p className="text-gray-500 text-base sm:text-lg">No products found</p>
            </div>
          ) : (
            products.map((product, index) => (
              <div key={product.id || product._id || index} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow flex flex-col min-h-0">
                {/* Product Image - Responsive */}
                <div 
                  className="relative cursor-pointer" 
                  onClick={() => openProductDetail(product)}
                  title="Click to view product details"
                >
                  {product.images && product.images.length > 0 ? (
                    <img 
                      src={product.images[0]} 
                      alt={product.product_name || product.crop_type}
                      className="w-full h-40 sm:h-48 object-cover hover:opacity-90 transition-opacity rounded-t-lg"
                    />
                  ) : (
                    <div className="w-full h-40 sm:h-48 bg-gray-200 flex items-center justify-center hover:bg-gray-300 transition-colors rounded-t-lg">
                      <span className="text-gray-500 text-sm sm:text-base">Click to View Details</span>
                    </div>
                  )}
                  
                  {/* View Details Overlay */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all flex items-center justify-center rounded-t-lg">
                    <div className="bg-white bg-opacity-0 hover:bg-opacity-90 text-transparent hover:text-gray-800 px-2 sm:px-3 py-1 rounded-lg text-xs sm:text-sm font-medium transition-all">
                      👁️ View Details
                    </div>
                  </div>
                  
                  {/* Pre-order Badge */}
                  {product.type === 'preorder' && (
                    <div className="absolute top-2 left-2 bg-orange-500 text-white px-2 py-1 rounded-lg text-xs font-semibold">
                      PRE-ORDER
                    </div>
                  )}
                  
                  {/* Seller Type Badge */}
                  {product.seller_type && (
                    <div className="absolute top-2 right-2 bg-emerald-500 text-white px-2 py-1 rounded-lg text-xs font-semibold capitalize">
                      {product.seller_type}
                    </div>
                  )}
                </div>

                <div className="p-4 flex-1 flex flex-col">{/* Changed to flex-1 flex flex-col to allow content to expand */}
                  <h3 className="font-semibold text-gray-900 mb-2">
                    {product.product_name || product.crop_type}
                  </h3>
                  
                  {/* Description */}
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                    {product.description || 'Fresh organic produce from test farm'}
                  </p>

                  {/* Price with Enhanced Specification Display */}
                  <div className="text-xl font-bold text-emerald-600 mb-2">
                    ₦{product.price_per_unit}/{product.unit || product.unit_of_measure || 'kg'}
                    {(product.unit_specification || product.unit_of_measure !== (product.unit || 'kg')) && 
                      <span className="text-sm font-medium text-gray-600 ml-1">
                        ({product.unit_specification || product.unit_of_measure || 'standard'})
                      </span>
                    }
                  </div>

                  {/* Stock Info */}
                  <div className="text-sm text-gray-500 mb-2">
                    {product.type === 'preorder' ? (
                      <>
                        <span className="text-orange-600 font-medium">
                          {product.available_stock || product.total_stock} {product.unit} available
                        </span>
                        {product.orders_count > 0 && (
                          <span className="ml-2">({product.orders_count} pre-orders)</span>
                        )}
                      </>
                    ) : (
                      <span>{product.quantity || '100'} available</span>
                    )}
                  </div>

                  {/* Business/Farm Info */}
                  <div className="text-sm text-gray-600 mb-2">
                    {product.business_name && (
                      <div className="font-medium">{product.business_name}</div>
                    )}
                    {product.farm_name && (
                      <div>{product.farm_name}</div>
                    )}
                    {product.agent_username && (
                      <div className="text-blue-600">Agent: @{product.agent_username}</div>
                    )}
                  </div>

                  {/* Location */}
                  <div className="text-sm text-gray-500 mb-3">
                    📍 {product.location}
                  </div>

                  {/* Pre-order specific info */}
                  {product.type === 'preorder' && (
                    <div className="mb-3 p-2 bg-orange-50 rounded-lg border border-orange-200">
                      <div className="text-xs text-orange-700">
                        <div>Partial payment: {Math.round((product.partial_payment_percentage || 0.3) * 100)}%</div>
                        <div>Delivery: {new Date(product.delivery_date).toLocaleDateString()}</div>
                      </div>
                    </div>
                  )}

                  {/* Seller Info */}
                  <div className="text-xs text-gray-500 mb-3">
                    Seller: {product.seller_username || `agent_${Math.random().toString().substr(2, 6)}`}
                  </div>

                  {/* Enhanced Add to Cart - includes delivery method and unit specification */}
                  <div className="mt-auto pt-4 space-y-3">{/* Removed debug styling */}
                    {/* Quantity Selection */}
                    <div className="grid grid-cols-3 gap-2">
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Quantity</label>
                        <input
                          type="number"
                          min="1"
                          defaultValue="1"
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-emerald-500"
                          id={`quantity-${index}`}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Unit</label>
                        <select
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-emerald-500"
                          id={`unit-${index}`}
                        >
                          <option value="kg">kg</option>
                          <option value="g">g</option>
                          <option value="pieces">pieces</option>
                          <option value="bags">bags</option>
                          <option value="crates">crates</option>
                          <option value="gallons">gallons</option>
                          <option value="liters">liters</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Spec (optional)</label>
                        <input
                          type="text"
                          placeholder="e.g., 100kg"
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-emerald-500"
                          id={`spec-${index}`}
                        />
                      </div>
                    </div>

                    {/* Delivery Method Selection */}
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Delivery Method</label>
                      <div className="flex space-x-2">
                        <label className="flex items-center">
                          <input
                            type="radio"
                            name={`delivery-method-${index}`}
                            value="platform"
                            defaultChecked
                            className="w-3 h-3 text-emerald-600 border-gray-300 focus:ring-emerald-500"
                          />
                          <span className="ml-1 text-xs text-gray-700">🚛 Platform Driver</span>
                        </label>
                        <label className="flex items-center">
                          <input
                            type="radio"
                            name={`delivery-method-${index}`}
                            value="offline"
                            className="w-3 h-3 text-emerald-600 border-gray-300 focus:ring-emerald-500"
                          />
                          <span className="ml-1 text-xs text-gray-700">🚚 Offline Delivery</span>
                        </label>
                      </div>
                    </div>

                    {/* Enhanced Add to Cart Button */}
                    <button
                      onClick={() => {
                        const quantityEl = document.getElementById(`quantity-${index}`);
                        const unitEl = document.getElementById(`unit-${index}`);
                        const specEl = document.getElementById(`spec-${index}`);
                        const deliveryEl = document.querySelector(`input[name="delivery-method-${index}"]:checked`);
                        
                        const quantity = parseFloat(quantityEl?.value) || 1;
                        const unit = unitEl?.value || 'kg';
                        const specification = specEl?.value || '';
                        const deliveryMethod = deliveryEl?.value || 'platform';
                        
                        addEnhancedToCart(product, quantity, unit, specification, deliveryMethod);
                      }}
                      className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                        product.type === 'preorder'
                          ? 'bg-orange-600 hover:bg-orange-700 text-white'
                          : 'bg-emerald-600 hover:bg-emerald-700 text-white'
                      }`}
                    >
                      {product.type === 'preorder' ? 'Add Pre-order to Cart' : 'Add to Cart'}
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </main>

      {/* Enhanced Registration Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            {/* Login Form */}
            {authMode === 'login' && (
              <>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-bold">Sign In</h2>
                  <button
                    onClick={() => setShowAuthModal(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ×
                  </button>
                </div>

                <form onSubmit={handleAuth} className="space-y-4">
                  <input
                    type="text"
                    placeholder="Email or Phone"
                    value={authForm.email_or_phone}
                    onChange={(e) => setAuthForm(prev => ({...prev, email_or_phone: e.target.value}))}
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
                    Sign In
                  </button>
                </form>

                <p className="mt-4 text-center text-sm text-gray-600">
                  Don't have an account? 
                  <button
                    onClick={() => setAuthMode('register')}
                    className="text-emerald-600 hover:text-emerald-700 font-medium ml-1"
                  >
                    Sign Up
                  </button>
                </p>
              </>
            )}

            {/* Registration Flow */}
            {authMode === 'register' && (
              <>
                {registrationStep === 'basic' && (
                  <>
                    <div className="flex justify-between items-center mb-4">
                      <h2 className="text-xl font-bold">Create Account</h2>
                      <button
                        onClick={() => setShowAuthModal(false)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        ×
                      </button>
                    </div>

                    <form onSubmit={handleBasicRegistration} className="space-y-4">
                      <div className="grid grid-cols-2 gap-3">
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
                      </div>
                      
                      <input
                        type="text"
                        placeholder="Username (unique)"
                        value={authForm.username}
                        onChange={(e) => setAuthForm(prev => ({...prev, username: e.target.value}))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        required
                      />
                      
                      <input
                        type="text"
                        placeholder="Email or Phone Number"
                        value={authForm.email_or_phone}
                        onChange={(e) => setAuthForm(prev => ({...prev, email_or_phone: e.target.value}))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        required
                      />
                      
                      <input
                        type="tel"
                        placeholder="Phone Number (optional)"
                        value={authForm.phone}
                        onChange={(e) => setAuthForm(prev => ({...prev, phone: e.target.value}))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      />

                      <div className="grid grid-cols-2 gap-3">
                        <select
                          value={authForm.gender}
                          onChange={(e) => setAuthForm(prev => ({...prev, gender: e.target.value}))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                          required
                        >
                          <option value="">Select Gender</option>
                          <option value="male">Male</option>
                          <option value="female">Female</option>
                          <option value="other">Other</option>
                        </select>
                        
                        <input
                          type="date"
                          placeholder="Date of Birth"
                          value={authForm.date_of_birth}
                          onChange={(e) => setAuthForm(prev => ({...prev, date_of_birth: e.target.value}))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                          required
                        />
                      </div>
                      
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
                        className="w-full bg-emerald-600 text-white py-2 px-4 rounded-full hover:bg-emerald-700 transition-colors font-medium"
                      >
                        Continue
                      </button>
                    </form>

                    <p className="mt-4 text-center text-sm text-gray-600">
                      Already have an account? 
                      <button
                        onClick={() => setAuthMode('login')}
                        className="text-emerald-600 hover:text-emerald-700 font-medium ml-1"
                      >
                        Sign In
                      </button>
                    </p>
                  </>
                )}

                {/* Role Path Selection Step */}
                {registrationStep === 'role_path' && (
                  <>
                    <div className="flex justify-between items-center mb-6">
                      <h2 className="text-2xl font-bold text-center w-full text-emerald-600">Welcome to Pyramyd!</h2>
                    </div>

                    <div className="bg-gradient-to-br from-emerald-50 to-blue-50 p-6 rounded-2xl">
                      <p className="text-gray-600 mb-6 text-center">
                        Choose how you'd like to use the platform:
                      </p>

                      <div className="grid grid-cols-1 gap-6">
                        {/* Buyer Path */}
                        <div className="bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-emerald-300 transition-colors cursor-pointer">
                          <div className="text-center">
                            <div className="text-4xl mb-3">🛒</div>
                            <h3 className="text-lg font-semibold mb-2 text-gray-800">Explore as a Buyer</h3>
                            <p className="text-sm text-gray-600 mb-4">Find fresh produce for your needs!</p>
                            <button
                              onClick={() => handleRolePath('buyer')}
                              className="w-full bg-blue-600 text-white py-3 px-4 rounded-full hover:bg-blue-700 transition-colors font-medium"
                            >
                              Continue as Buyer
                            </button>
                          </div>
                        </div>

                        {/* Partner Path */}
                        <div className="bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-emerald-300 transition-colors cursor-pointer">
                          <div className="text-center">
                            <div className="text-4xl mb-3">🤝</div>
                            <h3 className="text-lg font-semibold mb-2 text-gray-800">Register as a Partner</h3>
                            <p className="text-sm text-gray-600 mb-4">Grow your business with Pyramyd!</p>
                            <button
                              onClick={() => handleRolePath('partner')}
                              className="w-full bg-emerald-600 text-white py-3 px-4 rounded-full hover:bg-emerald-700 transition-colors font-medium"
                            >
                              Continue as Partner
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Buyer Type Selection Step */}
                {registrationStep === 'buyer_type' && (
                  <>
                    <div className="flex justify-between items-center mb-6">
                      <button
                        onClick={() => setRegistrationStep('role_path')}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        ← Back
                      </button>
                      <h2 className="text-xl font-bold text-emerald-600">Select Your Business Type</h2>
                      <div></div>
                    </div>

                    <div className="bg-gradient-to-br from-blue-50 to-purple-50 p-6 rounded-2xl">
                      <div className="space-y-3">
                        <button
                          onClick={() => handleBuyerTypeSelection('retailer')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all"
                        >
                          <div className="font-medium">Retailer</div>
                          <div className="text-sm text-gray-600">Buy and sell to end consumers</div>
                        </button>
                        
                        <button
                          onClick={() => handleBuyerTypeSelection('hotel')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all"
                        >
                          <div className="font-medium">Hotel</div>
                          <div className="text-sm text-gray-600">Hospitality business</div>
                        </button>
                        
                        <button
                          onClick={() => handleBuyerTypeSelection('cafe')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all"
                        >
                          <div className="font-medium">Cafe</div>
                          <div className="text-sm text-gray-600">Coffee shop or cafe business</div>
                        </button>
                        
                        <button
                          onClick={() => handleBuyerTypeSelection('restaurant')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all"
                        >
                          <div className="font-medium">Restaurant</div>
                          <div className="text-sm text-gray-600">Food service business</div>
                        </button>
                        
                        <button
                          onClick={() => handleBuyerTypeSelection('others')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all"
                        >
                          <div className="font-medium">Others</div>
                          <div className="text-sm text-gray-600">Specify your business type</div>
                        </button>
                      </div>
                      
                      <div className="mt-6 flex justify-end">
                        <button
                          onClick={() => handleBuyerTypeSelection('skip')}
                          className="text-gray-500 hover:text-gray-700 text-sm font-medium px-4 py-2 rounded-full border border-gray-300 hover:border-gray-400 transition-colors"
                        >
                          Skip (if you're not a business)
                        </button>
                      </div>
                    </div>
                  </>
                )}

                {/* Business Info Step */}
                {registrationStep === 'business_info' && (
                  <>
                    <div className="flex justify-between items-center mb-6">
                      <button
                        onClick={() => setRegistrationStep('buyer_type')}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        ← Back
                      </button>
                      <h2 className="text-xl font-bold text-emerald-600">Business Information</h2>
                      <div></div>
                    </div>

                    <div className="bg-gradient-to-br from-emerald-50 to-green-50 p-6 rounded-2xl">
                      <form onSubmit={(e) => { e.preventDefault(); completeRegistration(); }} className="space-y-4">
                        {selectedBuyerType === 'others' && (
                          <input
                            type="text"
                            placeholder="Specify your business type"
                            value={businessInfo.business_type}
                            onChange={(e) => setBusinessInfo(prev => ({...prev, business_type: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                            required
                          />
                        )}
                        
                        <input
                          type="text"
                          placeholder="Business Name"
                          value={businessInfo.business_name}
                          onChange={(e) => setBusinessInfo(prev => ({...prev, business_name: e.target.value}))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                          required
                        />
                        
                        <input
                          type="text"
                          placeholder="Business Address"
                          value={businessInfo.business_address}
                          onChange={(e) => setBusinessInfo(prev => ({...prev, business_address: e.target.value}))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                          required
                        />
                        
                        <div className="grid grid-cols-3 gap-3">
                          <input
                            type="text"
                            placeholder="City"
                            value={businessInfo.city}
                            onChange={(e) => setBusinessInfo(prev => ({...prev, city: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                            required
                          />
                          <input
                            type="text"
                            placeholder="State"
                            value={businessInfo.state}
                            onChange={(e) => setBusinessInfo(prev => ({...prev, state: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                            required
                          />
                          <input
                            type="text"
                            placeholder="Country"
                            value={businessInfo.country}
                            onChange={(e) => setBusinessInfo(prev => ({...prev, country: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                            required
                          />
                        </div>

                        <button
                          type="submit"
                          className="w-full bg-emerald-600 text-white py-3 px-4 rounded-full hover:bg-emerald-700 transition-colors font-medium"
                        >
                          Complete Registration
                        </button>
                      </form>
                    </div>
                  </>
                )}

                {/* Home Address Step (for skip option) */}
                {registrationStep === 'home_address' && (
                  <>
                    <div className="flex justify-between items-center mb-6">
                      <button
                        onClick={() => setRegistrationStep('buyer_type')}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        ← Back
                      </button>
                      <h2 className="text-xl font-bold text-emerald-600">Your Address</h2>
                      <div></div>
                    </div>

                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl">
                      <form onSubmit={(e) => { e.preventDefault(); completeRegistration(); }} className="space-y-4">
                        <input
                          type="text"
                          placeholder="Home Address"
                          value={businessInfo.home_address}
                          onChange={(e) => setBusinessInfo(prev => ({...prev, home_address: e.target.value}))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                          required
                        />
                        
                        <div className="grid grid-cols-3 gap-3">
                          <input
                            type="text"
                            placeholder="City"
                            value={businessInfo.city}
                            onChange={(e) => setBusinessInfo(prev => ({...prev, city: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                            required
                          />
                          <input
                            type="text"
                            placeholder="State"
                            value={businessInfo.state}
                            onChange={(e) => setBusinessInfo(prev => ({...prev, state: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                            required
                          />
                          <input
                            type="text"
                            placeholder="Country"
                            value={businessInfo.country}
                            onChange={(e) => setBusinessInfo(prev => ({...prev, country: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                            required
                          />
                        </div>

                        <button
                          type="submit"
                          className="w-full bg-emerald-600 text-white py-3 px-4 rounded-full hover:bg-emerald-700 transition-colors font-medium"
                        >
                          Complete Registration
                        </button>
                      </form>
                    </div>
                  </>
                )}

                {/* Partner Type Selection Step */}
                {registrationStep === 'partner_type' && (
                  <>
                    <div className="flex justify-between items-center mb-6">
                      <button
                        onClick={() => setRegistrationStep('role_path')}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        ← Back
                      </button>
                      <h2 className="text-xl font-bold text-emerald-600">Select Your Role</h2>
                      <div></div>
                    </div>

                    <div className="bg-gradient-to-br from-emerald-50 to-teal-50 p-6 rounded-2xl">
                      <div className="space-y-3">
                        <button
                          onClick={() => handlePartnerTypeSelection('agent')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-emerald-300 hover:bg-emerald-50 transition-all"
                        >
                          <div className="font-medium">Agent</div>
                          <div className="text-sm text-gray-600">Field agent facilitating transactions</div>
                        </button>
                        
                        <button
                          onClick={() => handlePartnerTypeSelection('farmer')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-emerald-300 hover:bg-emerald-50 transition-all"
                        >
                          <div className="font-medium">Farmer</div>
                          <div className="text-sm text-gray-600">Individual farmer growing produce</div>
                        </button>
                        
                        <button
                          onClick={() => handlePartnerTypeSelection('driver')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-emerald-300 hover:bg-emerald-50 transition-all"
                        >
                          <div className="font-medium">Driver</div>
                          <div className="text-sm text-gray-600">Delivery driver for transport services</div>
                        </button>
                        
                        <button
                          onClick={() => handlePartnerTypeSelection('storage_owner')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-emerald-300 hover:bg-emerald-50 transition-all"
                        >
                          <div className="font-medium">Storage Owner</div>
                          <div className="text-sm text-gray-600">Provide storage facilities</div>
                        </button>
                        
                        <button
                          onClick={() => handlePartnerTypeSelection('business')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-emerald-300 hover:bg-emerald-50 transition-all"
                        >
                          <div className="font-medium">Business</div>
                          <div className="text-sm text-gray-600">Supplier, Processor, or Logistics Business</div>
                        </button>
                      </div>
                    </div>
                  </>
                )}

                {/* Business Category Selection Step */}
                {registrationStep === 'business_category' && (
                  <>
                    <div className="flex justify-between items-center mb-6">
                      <button
                        onClick={() => setRegistrationStep('partner_type')}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        ← Back
                      </button>
                      <h2 className="text-xl font-bold text-emerald-600">Business Category</h2>
                      <div></div>
                    </div>

                    <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-2xl">
                      <div className="space-y-3">
                        <button
                          onClick={() => handleBusinessCategory('supplier')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all"
                        >
                          <div className="font-medium">Supplier</div>
                          <div className="text-sm text-gray-600">Supply agricultural products</div>
                        </button>
                        
                        <button
                          onClick={() => handleBusinessCategory('processor')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all"
                        >
                          <div className="font-medium">Processor</div>
                          <div className="text-sm text-gray-600">Process raw materials into finished goods</div>
                        </button>
                        
                        <button
                          onClick={() => handleBusinessCategory('logistics_business')}
                          className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all"
                        >
                          <div className="font-medium">Logistics Business</div>
                          <div className="text-sm text-gray-600">Transport and logistics services</div>
                        </button>
                      </div>
                    </div>
                  </>
                )}

                {/* Verification Step */}
                {registrationStep === 'verification' && (
                  <>
                    <div className="flex justify-between items-center mb-6">
                      <button
                        onClick={() => setRegistrationStep(partnerType === 'business' ? 'business_category' : 'partner_type')}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        ← Back
                      </button>
                      <h2 className="text-xl font-bold text-emerald-600">Verification Requirements</h2>
                      <div></div>
                    </div>

                    <div className="bg-gradient-to-br from-yellow-50 to-orange-50 p-6 rounded-2xl">
                      <form onSubmit={(e) => { e.preventDefault(); completeRegistration(); }} className="space-y-4">
                        {/* Different verification based on role */}
                        {(partnerType === 'agent' || partnerType === 'driver') && (
                          <>
                            <div className="mb-4 p-3 bg-blue-100 rounded-lg">
                              <p className="text-sm text-blue-800 font-medium">Required: NIN and Photo for verification</p>
                            </div>
                            <input
                              type="text"
                              placeholder="National Identification Number (NIN)"
                              value={verificationInfo.nin}
                              onChange={(e) => setVerificationInfo(prev => ({...prev, nin: e.target.value}))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                              required
                            />
                            <input
                              type="file"
                              accept="image/*"
                              placeholder="Upload your photo"
                              onChange={(e) => setVerificationInfo(prev => ({...prev, photo: e.target.files[0]?.name || ''}))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                              required
                            />
                          </>
                        )}

                        {partnerType === 'farmer' && (
                          <>
                            <div className="mb-4 p-3 bg-green-100 rounded-lg">
                              <p className="text-sm text-green-800 font-medium">Required: Photo, NIN, Farm Photo, and Farm Information</p>
                            </div>
                            <input
                              type="text"
                              placeholder="National Identification Number (NIN)"
                              value={verificationInfo.nin}
                              onChange={(e) => setVerificationInfo(prev => ({...prev, nin: e.target.value}))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                              required
                            />
                            <input
                              type="file"
                              accept="image/*"
                              placeholder="Upload your photo"
                              onChange={(e) => setVerificationInfo(prev => ({...prev, photo: e.target.files[0]?.name || ''}))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                              required
                            />
                            <input
                              type="file"
                              accept="image/*"
                              placeholder="Upload farm photo"
                              onChange={(e) => setVerificationInfo(prev => ({...prev, farm_photo: e.target.files[0]?.name || ''}))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                              required
                            />
                            <textarea
                              placeholder="Farm Information (location, size, crops grown, etc.)"
                              value={verificationInfo.farm_info}
                              onChange={(e) => setVerificationInfo(prev => ({...prev, farm_info: e.target.value}))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                              rows="3"
                              required
                            />
                          </>
                        )}

                        {(businessCategory === 'processor' || businessCategory === 'logistics_business' || (partnerType === 'business' && businessCategory)) && (
                          <>
                            <div className="mb-4 p-3 bg-purple-100 rounded-lg">
                              <p className="text-sm text-purple-800 font-medium">Required: CAC Number, Business Name, and Address</p>
                            </div>
                            <input
                              type="text"
                              placeholder="CAC Registration Number"
                              value={verificationInfo.cac_number}
                              onChange={(e) => setVerificationInfo(prev => ({...prev, cac_number: e.target.value}))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                              required
                            />
                            <input
                              type="text"
                              placeholder="Business Name"
                              value={businessInfo.business_name}
                              onChange={(e) => setBusinessInfo(prev => ({...prev, business_name: e.target.value}))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                              required
                            />
                            <input
                              type="text"
                              placeholder="Business Address"
                              value={businessInfo.business_address}
                              onChange={(e) => setBusinessInfo(prev => ({...prev, business_address: e.target.value}))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                              required
                            />
                          </>
                        )}

                        {businessCategory === 'supplier' && (
                          <>
                            <div className="mb-4 p-3 bg-orange-100 rounded-lg">
                              <p className="text-sm text-orange-800 font-medium">Suppliers can submit either NIN or CAC Number</p>
                            </div>
                            <div className="space-y-3">
                              <label className="flex items-center">
                                <input
                                  type="radio"
                                  name="supplier_verification"
                                  value="nin"
                                  onChange={(e) => setVerificationInfo(prev => ({...prev, verification_type: e.target.value}))}
                                  className="mr-2"
                                />
                                Use NIN (Individual/Unregistered Business)
                              </label>
                              <label className="flex items-center">
                                <input
                                  type="radio"
                                  name="supplier_verification"
                                  value="cac"
                                  onChange={(e) => setVerificationInfo(prev => ({...prev, verification_type: e.target.value}))}
                                  className="mr-2"
                                />
                                Use CAC (Registered Business)
                              </label>
                            </div>
                            
                            {verificationInfo.verification_type === 'nin' && (
                              <input
                                type="text"
                                placeholder="National Identification Number (NIN)"
                                value={verificationInfo.nin}
                                onChange={(e) => setVerificationInfo(prev => ({...prev, nin: e.target.value}))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                required
                              />
                            )}
                            
                            {verificationInfo.verification_type === 'cac' && (
                              <>
                                <input
                                  type="text"
                                  placeholder="CAC Registration Number"
                                  value={verificationInfo.cac_number}
                                  onChange={(e) => setVerificationInfo(prev => ({...prev, cac_number: e.target.value}))}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                  required
                                />
                                <input
                                  type="text"
                                  placeholder="Business Name"
                                  value={businessInfo.business_name}
                                  onChange={(e) => setBusinessInfo(prev => ({...prev, business_name: e.target.value}))}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                  required
                                />
                                <input
                                  type="text"
                                  placeholder="Business Address"
                                  value={businessInfo.business_address}
                                  onChange={(e) => setBusinessInfo(prev => ({...prev, business_address: e.target.value}))}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                  required
                                />
                              </>
                            )}
                          </>
                        )}

                        <button
                          type="submit"
                          className="w-full bg-emerald-600 text-white py-3 px-4 rounded-full hover:bg-emerald-700 transition-colors font-medium"
                        >
                          Complete Registration
                        </button>
                      </form>
                    </div>
                  </>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Comprehensive Checkout Page */}
      {showCheckout && (
        <div className="modal-backdrop-blur fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold text-gray-900">🛒 Checkout</h2>
                <button
                  onClick={() => setShowCheckout(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              
              {/* Progress Steps */}
              <div className="mt-4 flex items-center space-x-4">
                <div className={`flex items-center ${checkoutStep === 'review' ? 'text-emerald-600' : 'text-gray-400'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                    checkoutStep === 'review' ? 'bg-emerald-100 text-emerald-600' : 'bg-gray-100 text-gray-400'
                  }`}>1</div>
                  <span className="ml-2 text-sm font-medium">Review Order</span>
                </div>
                <div className="h-px bg-gray-200 flex-1"></div>
                <div className={`flex items-center ${checkoutStep === 'address' ? 'text-emerald-600' : 'text-gray-400'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                    checkoutStep === 'address' ? 'bg-emerald-100 text-emerald-600' : 'bg-gray-100 text-gray-400'
                  }`}>2</div>
                  <span className="ml-2 text-sm font-medium">Shipping Address</span>
                </div>
                <div className="h-px bg-gray-200 flex-1"></div>
                <div className={`flex items-center ${checkoutStep === 'payment' ? 'text-emerald-600' : 'text-gray-400'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                    checkoutStep === 'payment' ? 'bg-emerald-100 text-emerald-600' : 'bg-gray-100 text-gray-400'
                  }`}>3</div>
                  <span className="ml-2 text-sm font-medium">Payment</span>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Content */}
                <div className="lg:col-span-2">
                  {/* Step 1: Review Order */}
                  {checkoutStep === 'review' && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-semibold text-gray-900">📦 Review Your Order</h3>
                      
                      {cart.length === 0 ? (
                        <div className="text-center py-8">
                          <div className="text-gray-500">Your cart is empty</div>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {cart.map((item) => (
                            <div key={item.id} className="bg-gray-50 rounded-lg p-4">
                              <div className="flex justify-between items-start">
                                <div className="flex-1">
                                  <h4 className="font-semibold text-gray-900">
                                    {item.product.product_name || item.product.crop_type}
                                  </h4>
                                  <p className="text-sm text-gray-600 mb-2">
                                    {item.product.description || 'Fresh organic produce'}
                                  </p>
                                  
                                  <div className="flex items-center space-x-4 text-sm">
                                    <span className="text-gray-700">
                                      <strong>Quantity:</strong> {item.quantity} {item.unit}
                                      {item.unit_specification && ` (${item.unit_specification})`}
                                    </span>
                                    <span className="text-gray-700">
                                      <strong>Price:</strong> ₦{item.product.price_per_unit}/{item.unit}
                                    </span>
                                    <span className={`px-2 py-1 rounded-full text-xs ${
                                      item.delivery_method === 'platform' 
                                        ? 'bg-blue-100 text-blue-800' 
                                        : 'bg-green-100 text-green-800'
                                    }`}>
                                      {item.delivery_method === 'platform' ? '🚛 Platform Driver' : '🚚 Offline Delivery'}
                                    </span>
                                  </div>
                                  
                                  <div className="mt-2 text-sm text-gray-600">
                                    <strong>Seller:</strong> {item.product.seller_username}
                                    {item.product.business_name && ` (${item.product.business_name})`}
                                  </div>
                                </div>
                                
                                <div className="text-right">
                                  <div className="text-lg font-semibold text-gray-900">
                                    ₦{(item.product.price_per_unit * item.quantity).toLocaleString()}
                                  </div>
                                  <button
                                    onClick={() => removeCartItem(item.id)}
                                    className="text-red-600 hover:text-red-800 text-sm mt-1"
                                  >
                                    Remove
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      <div className="flex justify-end">
                        <button
                          onClick={() => setCheckoutStep('address')}
                          className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium"
                        >
                          Continue to Shipping
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {/* Step 2: Shipping Address */}
                  {checkoutStep === 'address' && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-semibold text-gray-900">📍 Shipping Address</h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                          <input
                            type="text"
                            value={shippingAddress.full_name}
                            onChange={(e) => setShippingAddress(prev => ({...prev, full_name: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            placeholder="Enter your full name"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number *</label>
                          <input
                            type="tel"
                            value={shippingAddress.phone}
                            onChange={(e) => setShippingAddress(prev => ({...prev, phone: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            placeholder="+234 xxx xxx xxxx"
                          />
                        </div>
                        
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                          <input
                            type="email"
                            value={shippingAddress.email}
                            onChange={(e) => setShippingAddress(prev => ({...prev, email: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            placeholder="your.email@example.com"
                          />
                        </div>
                        
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 1 *</label>
                          <input
                            type="text"
                            value={shippingAddress.address_line_1}
                            onChange={(e) => setShippingAddress(prev => ({...prev, address_line_1: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            placeholder="Street address, P.O. box, company name"
                          />
                        </div>
                        
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 2</label>
                          <input
                            type="text"
                            value={shippingAddress.address_line_2}
                            onChange={(e) => setShippingAddress(prev => ({...prev, address_line_2: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            placeholder="Apartment, suite, unit, building, floor, etc."
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">City *</label>
                          <input
                            type="text"
                            value={shippingAddress.city}
                            onChange={(e) => setShippingAddress(prev => ({...prev, city: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            placeholder="Lagos"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">State *</label>
                          <input
                            type="text"
                            value={shippingAddress.state}
                            onChange={(e) => setShippingAddress(prev => ({...prev, state: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            placeholder="Lagos State"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
                          <input
                            type="text"
                            value={shippingAddress.postal_code}
                            onChange={(e) => setShippingAddress(prev => ({...prev, postal_code: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            placeholder="100001"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                          <select
                            value={shippingAddress.country}
                            onChange={(e) => setShippingAddress(prev => ({...prev, country: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                          >
                            <option value="Nigeria">Nigeria</option>
                            <option value="Ghana">Ghana</option>
                            <option value="Kenya">Kenya</option>
                          </select>
                        </div>
                        
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Instructions</label>
                          <textarea
                            value={shippingAddress.delivery_instructions}
                            onChange={(e) => setShippingAddress(prev => ({...prev, delivery_instructions: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            rows="3"
                            placeholder="Any special delivery instructions..."
                          />
                        </div>
                      </div>
                      
                      <div className="flex justify-between">
                        <button
                          onClick={() => setCheckoutStep('review')}
                          className="px-6 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
                        >
                          Back to Review
                        </button>
                        <button
                          onClick={() => {
                            if (validateAddress()) {
                              setCheckoutStep('payment');
                            }
                          }}
                          className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium"
                        >
                          Continue to Payment
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {/* Step 3: Payment */}
                  {checkoutStep === 'payment' && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-semibold text-gray-900">💳 Payment</h3>
                      
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex items-center">
                          <svg className="w-5 h-5 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <div>
                            <div className="font-medium text-blue-900">Payment Integration Ready</div>
                            <div className="text-sm text-blue-700">Paystack payment gateway will be integrated here</div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="font-medium text-gray-900">Payment Methods Available:</div>
                        <div className="space-y-2">
                          <div className="flex items-center p-3 border border-gray-200 rounded-lg">
                            <input type="radio" name="payment_method" defaultChecked className="w-4 h-4 text-emerald-600" />
                            <div className="ml-3">
                              <div className="font-medium">💳 Card Payment</div>
                              <div className="text-sm text-gray-600">Visa, Mastercard, Verve</div>
                            </div>
                          </div>
                          <div className="flex items-center p-3 border border-gray-200 rounded-lg">
                            <input type="radio" name="payment_method" className="w-4 h-4 text-emerald-600" />
                            <div className="ml-3">
                              <div className="font-medium">🏦 Bank Transfer</div>
                              <div className="text-sm text-gray-600">Direct bank transfer</div>
                            </div>
                          </div>
                          <div className="flex items-center p-3 border border-gray-200 rounded-lg">
                            <input type="radio" name="payment_method" className="w-4 h-4 text-emerald-600" />
                            <div className="ml-3">
                              <div className="font-medium">📱 Mobile Money</div>
                              <div className="text-sm text-gray-600">MTN, Airtel, etc.</div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex justify-between">
                        <button
                          onClick={() => setCheckoutStep('address')}
                          className="px-6 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
                        >
                          Back to Address
                        </button>
                        <button
                          onClick={createOrder}
                          className="px-8 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium"
                        >
                          Place Order (₦{orderSummary.total?.toLocaleString() || 0})
                        </button>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Order Summary Sidebar */}
                <div className="lg:col-span-1">
                  <div className="bg-gray-50 rounded-lg p-6 sticky top-0">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Order Summary</h3>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Subtotal ({orderSummary.item_count} items)</span>
                        <span className="font-medium">₦{orderSummary.subtotal?.toLocaleString()}</span>
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Delivery Fees</span>
                        <span className="font-medium">₦{orderSummary.delivery_total?.toLocaleString()}</span>
                      </div>
                      
                      <div className="border-t border-gray-200 pt-3">
                        <div className="flex justify-between">
                          <span className="text-lg font-semibold text-gray-900">Total</span>
                          <span className="text-lg font-semibold text-emerald-600">₦{orderSummary.total?.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Shipping Address Summary */}
                    {checkoutStep !== 'review' && shippingAddress.full_name && (
                      <div className="mt-6 pt-6 border-t border-gray-200">
                        <h4 className="font-medium text-gray-900 mb-2">📍 Shipping To:</h4>
                        <div className="text-sm text-gray-600">
                          <div>{shippingAddress.full_name}</div>
                          <div>{shippingAddress.address_line_1}</div>
                          {shippingAddress.address_line_2 && <div>{shippingAddress.address_line_2}</div>}
                          <div>{shippingAddress.city}, {shippingAddress.state}</div>
                          <div>{shippingAddress.country}</div>
                          <div className="mt-1 font-medium">{shippingAddress.phone}</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Delivery Request Modal */}
      {showCreateDeliveryRequest && (
        <div className="modal-backdrop-blur fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">🚚 Create Delivery Request</h2>
                <button
                  onClick={() => setShowCreateDeliveryRequest(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left Column - Form */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Order Details</h3>
                  
                  {/* Order Information */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Order ID</label>
                      <input
                        type="text"
                        value={enhancedDeliveryForm.order_id}
                        onChange={(e) => setEnhancedDeliveryForm(prev => ({ ...prev, order_id: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="e.g., ORD-12345"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Order Type</label>
                      <select
                        value={enhancedDeliveryForm.order_type}
                        onChange={(e) => setEnhancedDeliveryForm(prev => ({ ...prev, order_type: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      >
                        <option value="regular">Regular Order</option>
                        <option value="preorder">Pre-order</option>
                      </select>
                    </div>
                  </div>

                  {/* Product Details */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Product Details *</label>
                    <textarea
                      value={enhancedDeliveryForm.product_details}
                      onChange={(e) => setEnhancedDeliveryForm(prev => ({ ...prev, product_details: e.target.value }))}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      placeholder="Describe the products to be delivered..."
                    />
                  </div>

                  {/* Quantity and Weight */}
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Total Quantity *</label>
                      <input
                        type="number"
                        value={enhancedDeliveryForm.total_quantity}
                        onChange={(e) => setEnhancedDeliveryForm(prev => ({ ...prev, total_quantity: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="100"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
                      <select
                        value={enhancedDeliveryForm.quantity_unit}
                        onChange={(e) => setEnhancedDeliveryForm(prev => ({ ...prev, quantity_unit: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      >
                        <option value="kg">Kilograms</option>
                        <option value="pieces">Pieces</option>
                        <option value="bags">Bags</option>
                        <option value="crates">Crates</option>
                        <option value="liters">Liters</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Weight (kg)</label>
                      <input
                        type="number"
                        value={enhancedDeliveryForm.weight_kg}
                        onChange={(e) => setEnhancedDeliveryForm(prev => ({ ...prev, weight_kg: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="50"
                      />
                    </div>
                  </div>

                  {/* Locations */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">📍 Pickup Address *</label>
                    <input
                      type="text"
                      value={enhancedDeliveryForm.pickup_address}
                      onChange={(e) => setEnhancedDeliveryForm(prev => ({ ...prev, pickup_address: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      placeholder="Enter pickup address..."
                    />
                  </div>

                  {/* Multiple Delivery Destinations */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="block text-sm font-medium text-gray-700">🎯 Delivery Destinations *</label>
                      <button
                        type="button"
                        onClick={addDeliveryDestination}
                        className="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
                      >
                        + Add Destination
                      </button>
                    </div>
                    
                    <div className="space-y-2">
                      {multipleDestinations.map((destination, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <div className="flex-1">
                            <input
                              type="text"
                              value={destination}
                              onChange={(e) => updateDeliveryDestination(index, e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                              placeholder={`Destination ${index + 1} address...`}
                            />
                          </div>
                          {multipleDestinations.length > 1 && (
                            <button
                              type="button"
                              onClick={() => removeDeliveryDestination(index)}
                              className="text-red-600 hover:text-red-700 p-1"
                            >
                              ✕
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Pricing */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">💰 Estimated Price (₦) *</label>
                    <input
                      type="number"
                      value={enhancedDeliveryForm.estimated_price}
                      onChange={(e) => setEnhancedDeliveryForm(prev => ({ ...prev, estimated_price: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      placeholder="5000"
                    />
                  </div>

                  {/* Special Instructions */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">📝 Special Instructions</label>
                    <textarea
                      value={enhancedDeliveryForm.special_instructions}
                      onChange={(e) => setEnhancedDeliveryForm(prev => ({ ...prev, special_instructions: e.target.value }))}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      placeholder="Any special handling requirements..."
                    />
                  </div>
                </div>

                {/* Right Column - Driver Search & Map */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 Find & Select Driver</h3>
                  
                  {/* Driver Search */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Search Drivers</label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={driverSearch}
                        onChange={(e) => setDriverSearch(e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="Search by driver name or username..."
                      />
                      <button
                        type="button"
                        onClick={() => searchDrivers(pickupCoordinates)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        🔍
                      </button>
                    </div>
                  </div>

                  {/* Search Results */}
                  {searchResults.length > 0 && (
                    <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-lg">
                      <div className="p-2 bg-gray-50 border-b border-gray-200 text-sm font-medium text-gray-700">
                        Available Drivers ({searchResults.length})
                      </div>
                      {searchResults.map((driver) => (
                        <div
                          key={driver.driver_id}
                          onClick={() => {
                            setSelectedDriver(driver);
                            setEnhancedDeliveryForm(prev => ({ ...prev, preferred_driver_username: driver.driver_username }));
                          }}
                          className={`p-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                            selectedDriver?.driver_id === driver.driver_id ? 'bg-emerald-50 border-emerald-200' : ''
                          }`}
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium text-gray-900">{driver.driver_name}</div>
                              <div className="text-sm text-gray-600">@{driver.driver_username}</div>
                              <div className="text-sm text-gray-500">
                                ⭐ {driver.rating} • {driver.total_deliveries} deliveries
                              </div>
                              <div className="text-sm text-blue-600">
                                🚗 {driver.vehicle_info.make_model} ({driver.vehicle_info.plate_number})
                              </div>
                            </div>
                            <div className="text-right">
                              <div className={`text-sm px-2 py-1 rounded-full ${
                                driver.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                              }`}>
                                {driver.status}
                              </div>
                              {driver.distance_km && (
                                <div className="text-sm text-gray-500 mt-1">
                                  📍 {driver.distance_km} km away
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Selected Driver */}
                  {selectedDriver && (
                    <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                      <div className="text-sm font-medium text-emerald-800 mb-2">✅ Selected Driver</div>
                      <div className="font-medium text-gray-900">{selectedDriver.driver_name}</div>
                      <div className="text-sm text-gray-600">@{selectedDriver.driver_username}</div>
                      <div className="text-sm text-gray-500">
                        ⭐ {selectedDriver.rating} • {selectedDriver.total_deliveries} deliveries
                      </div>
                    </div>
                  )}

                  {/* Map Placeholder */}
                  <div className="h-48 bg-gray-100 border border-gray-200 rounded-lg flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <div className="text-2xl mb-2">🗺️</div>
                      <div className="text-sm">Interactive Map</div>
                      <div className="text-xs">Pickup & delivery locations will be shown here</div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowCreateDeliveryRequest(false)}
                      className="flex-1 px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      onClick={createEnhancedDeliveryRequest}
                      className="flex-1 px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium"
                    >
                      Create Request
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delivery Messages Modal */}
      {showDriverMessages && (
        <div className="modal-backdrop-blur fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex">
            {/* Left Side - Delivery Info */}
            <div className="w-1/3 bg-gray-50 border-r border-gray-200 p-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">📦 Delivery Info</h3>
                <button
                  onClick={() => setShowDriverMessages(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
              
              {trackingData && (
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-medium text-gray-700">Status</div>
                    <div className="text-lg font-semibold text-emerald-600">{trackingData.status}</div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-gray-700">Product</div>
                    <div className="text-sm text-gray-900">{trackingData.product_details}</div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-gray-700">Quantity</div>
                    <div className="text-sm text-gray-900">{trackingData.total_quantity} {trackingData.quantity_unit}</div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-gray-700">Pickup</div>
                    <div className="text-sm text-gray-900">{trackingData.pickup_location.address}</div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-gray-700">Destinations</div>
                    {trackingData.delivery_locations.map((location, index) => (
                      <div key={index} className="text-sm text-gray-900">
                        {index + 1}. {location.address}
                      </div>
                    ))}
                  </div>
                  
                  <div>
                    <div className="text-sm font-medium text-gray-700">Price</div>
                    <div className="text-sm text-gray-900">
                      ₦{trackingData.negotiated_price || trackingData.estimated_price}
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Right Side - Chat */}
            <div className="flex-1 flex flex-col">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">💬 Delivery Chat</h3>
              </div>
              
              {/* Messages */}
              <div className="flex-1 p-4 overflow-y-auto">
                {deliveryMessages.length === 0 ? (
                  <div className="text-center text-gray-500 mt-8">
                    <div className="text-2xl mb-2">💬</div>
                    <div>No messages yet</div>
                    <div className="text-sm">Start a conversation with your driver</div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {deliveryMessages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.sender_username === user.username ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-xs px-3 py-2 rounded-lg ${
                          message.sender_username === user.username 
                            ? 'bg-emerald-500 text-white' 
                            : 'bg-gray-200 text-gray-900'
                        }`}>
                          <div className="text-sm">
                            {message.message_type === 'location' ? (
                              <div>
                                <div className="font-medium">📍 Location shared</div>
                                <div className="text-xs opacity-75">Tap to view on map</div>
                              </div>
                            ) : (
                              message.content
                            )}
                          </div>
                          <div className="text-xs mt-1 opacity-75">
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Message Input */}
              <div className="p-4 border-t border-gray-200">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newDeliveryMessage}
                    onChange={(e) => setNewDeliveryMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && newDeliveryMessage.trim() && sendDeliveryMessage(currentDeliveryChat, newDeliveryMessage)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                    placeholder="Type a message..."
                  />
                  <button
                    onClick={() => sendDeliveryMessage(currentDeliveryChat, 'Current location', 'location')}
                    className="px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                    title="Share location"
                  >
                    📍
                  </button>
                  <button
                    onClick={() => newDeliveryMessage.trim() && sendDeliveryMessage(currentDeliveryChat, newDeliveryMessage)}
                    className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Pre-order Details Modal */}
      {showPreOrderDetails && selectedPreOrder && (
        <div className="modal-backdrop-blur fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Pre-order Details</h2>
                <button
                  onClick={() => {
                    setShowPreOrderDetails(false);
                    setSelectedPreOrder(null);
                  }}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              {/* Product Image */}
              {selectedPreOrder.images && selectedPreOrder.images.length > 0 ? (
                <img 
                  src={selectedPreOrder.images[0]} 
                  alt={selectedPreOrder.product_name}
                  className="w-full h-48 object-cover rounded-lg mb-4"
                />
              ) : (
                <div className="w-full h-48 bg-gray-200 flex items-center justify-center rounded-lg mb-4">
                  <span className="text-gray-500">No Image</span>
                </div>
              )}

              {/* Product Info */}
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{selectedPreOrder.product_name}</h3>
              <p className="text-gray-600 mb-4">{selectedPreOrder.description}</p>

              {/* Price and Stock */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-emerald-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Price per unit</div>
                  <div className="text-xl font-bold text-emerald-600">
                    ₦{selectedPreOrder.price_per_unit}/{selectedPreOrder.unit}
                  </div>
                </div>
                <div className="bg-orange-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Available stock</div>
                  <div className="text-xl font-bold text-orange-600">
                    {selectedPreOrder.available_stock} {selectedPreOrder.unit}
                  </div>
                </div>
              </div>

              {/* Business Info */}
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Seller Information</h4>
                <div className="space-y-1 text-sm">
                  <div><span className="font-medium">Business:</span> {selectedPreOrder.business_name}</div>
                  {selectedPreOrder.farm_name && (
                    <div><span className="font-medium">Farm:</span> {selectedPreOrder.farm_name}</div>
                  )}
                  {selectedPreOrder.agent_username && (
                    <div><span className="font-medium">Agent:</span> @{selectedPreOrder.agent_username}</div>
                  )}
                  <div><span className="font-medium">Location:</span> {selectedPreOrder.location}</div>
                  <div><span className="font-medium">Seller Type:</span> {selectedPreOrder.seller_type}</div>
                </div>
              </div>

              {/* Pre-order Details */}
              <div className="mb-4 p-4 bg-orange-50 rounded-lg border border-orange-200">
                <h4 className="font-semibold text-orange-900 mb-2">Pre-order Information</h4>
                <div className="space-y-1 text-sm text-orange-800">
                  <div>
                    <span className="font-medium">Partial payment required:</span> 
                    {Math.round(selectedPreOrder.partial_payment_percentage * 100)}% upfront
                  </div>
                  <div>
                    <span className="font-medium">Remaining payment:</span> 
                    {100 - Math.round(selectedPreOrder.partial_payment_percentage * 100)}% on delivery
                  </div>
                  <div>
                    <span className="font-medium">Expected delivery:</span> 
                    {new Date(selectedPreOrder.delivery_date).toLocaleDateString()}
                  </div>
                  {selectedPreOrder.orders_count > 0 && (
                    <div>
                      <span className="font-medium">Current orders:</span> 
                      {selectedPreOrder.orders_count} ({selectedPreOrder.total_ordered_quantity} {selectedPreOrder.unit})
                    </div>
                  )}
                </div>
              </div>

              {/* Order Form */}
              {user ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Quantity ({selectedPreOrder.unit})
                    </label>
                    <input
                      type="number"
                      min="1"
                      max={selectedPreOrder.available_stock}
                      defaultValue="1"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      id="preorder-quantity"
                      onChange={(e) => {
                        const quantity = parseInt(e.target.value) || 1;
                        const total = quantity * selectedPreOrder.price_per_unit;
                        const partial = Math.round(total * selectedPreOrder.partial_payment_percentage);
                        
                        document.getElementById('summary-quantity').textContent = `${quantity} ${selectedPreOrder.unit}`;
                        document.getElementById('summary-total').textContent = `₦${total}`;
                        document.getElementById('summary-partial').textContent = `₦${partial}`;
                        document.getElementById('summary-remaining').textContent = `₦${total - partial}`;
                      }}
                    />
                  </div>

                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Order Summary</div>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span>Unit price:</span>
                        <span>₦{selectedPreOrder.price_per_unit}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Quantity:</span>
                        <span id="summary-quantity">1 {selectedPreOrder.unit}</span>
                      </div>
                      <div className="flex justify-between font-medium">
                        <span>Total amount:</span>
                        <span id="summary-total">₦{selectedPreOrder.price_per_unit}</span>
                      </div>
                      <div className="flex justify-between text-orange-600">
                        <span>Partial payment now:</span>
                        <span id="summary-partial">₦{Math.round(selectedPreOrder.price_per_unit * selectedPreOrder.partial_payment_percentage)}</span>
                      </div>
                      <div className="flex justify-between text-gray-600">
                        <span>Remaining on delivery:</span>
                        <span id="summary-remaining">₦{selectedPreOrder.price_per_unit - Math.round(selectedPreOrder.price_per_unit * selectedPreOrder.partial_payment_percentage)}</span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={async () => {
                      const quantity = parseInt(document.getElementById('preorder-quantity').value);
                      if (quantity <= 0 || quantity > selectedPreOrder.available_stock) {
                        alert('Please enter a valid quantity');
                        return;
                      }

                      try {
                        const token = localStorage.getItem('token');
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/preorders/${selectedPreOrder.id}/order`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                          },
                          body: JSON.stringify({ quantity })
                        });

                        if (response.ok) {
                          const result = await response.json();
                          alert(`Pre-order placed successfully! Order ID: ${result.order_id}\nPartial payment: ₦${result.partial_amount}\nRemaining: ₦${result.remaining_amount}`);
                          setShowPreOrderDetails(false);
                          setSelectedPreOrder(null);
                          fetchProducts(); // Refresh products to update stock
                        } else {
                          const error = await response.json();
                          alert(`Error: ${error.detail || 'Failed to place pre-order'}`);
                        }
                      } catch (error) {
                        console.error('Error placing pre-order:', error);
                        alert('Error placing pre-order. Please try again.');
                      }
                    }}
                    className="w-full bg-orange-600 text-white py-3 px-4 rounded-lg hover:bg-orange-700 font-medium transition-colors"
                  >
                    Place Pre-order
                  </button>
                </div>
              ) : (
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-600 mb-3">Please sign in to place pre-orders</p>
                  <button
                    onClick={() => {
                      setShowPreOrderDetails(false);
                      setAuthMode('login');
                      setShowAuthModal(true);
                    }}
                    className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
                  >
                    Sign In
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Create Pre-order Modal */}
      {showCreatePreOrder && (
        <div className="modal-backdrop-blur fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Create Pre-order</h2>
                <button
                  onClick={() => setShowCreatePreOrder(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              <form onSubmit={async (e) => {
                e.preventDefault();
                try {
                  const token = localStorage.getItem('token');
                  const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/preorders/create`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                      ...preOrderForm,
                      total_stock: parseInt(preOrderForm.total_stock),
                      price_per_unit: parseFloat(preOrderForm.price_per_unit),
                      delivery_date: new Date(preOrderForm.delivery_date).toISOString()
                    })
                  });

                  if (response.ok) {
                    const result = await response.json();
                    alert('Pre-order created successfully! You can publish it from your dashboard.');
                    setShowCreatePreOrder(false);
                    setPreOrderForm({
                      product_name: '',
                      product_category: 'vegetables',
                      description: '',
                      total_stock: '',
                      unit: 'kg',
                      price_per_unit: '',
                      partial_payment_percentage: 0.3,
                      location: '',
                      delivery_date: '',
                      business_name: '',
                      farm_name: '',
                      images: []
                    });
                  } else {
                    const error = await response.json();
                    alert(`Error: ${error.detail || 'Failed to create pre-order'}`);
                  }
                } catch (error) {
                  console.error('Error creating pre-order:', error);
                  alert('Error creating pre-order. Please try again.');
                }
              }}>
                <div className="space-y-4">
                  {/* Product Information */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Product Name *</label>
                      <input
                        type="text"
                        required
                        value={preOrderForm.product_name}
                        onChange={(e) => setPreOrderForm(prev => ({ ...prev, product_name: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="e.g., Organic Tomatoes"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
                      <select
                        required
                        value={preOrderForm.product_category}
                        onChange={(e) => setPreOrderForm(prev => ({ ...prev, product_category: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      >
                        <option value="vegetables">Vegetables</option>
                        <option value="fruits">Fruits</option>
                        <option value="grains">Grains</option>
                        <option value="legumes">Legumes</option>
                        <option value="spices">Spices</option>
                        <option value="feeds">Feeds</option>
                        <option value="fertilizer">Fertilizer</option>
                        <option value="seeds">Seeds</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
                    <textarea
                      required
                      value={preOrderForm.description}
                      onChange={(e) => setPreOrderForm(prev => ({ ...prev, description: e.target.value }))}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      placeholder="Describe your product, quality, farming methods, etc."
                    />
                  </div>

                  {/* Stock and Pricing */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Total Stock *</label>
                      <input
                        type="number"
                        required
                        min="1"
                        value={preOrderForm.total_stock}
                        onChange={(e) => setPreOrderForm(prev => ({ ...prev, total_stock: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="e.g., 1000"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Unit *</label>
                      <select
                        required
                        value={preOrderForm.unit}
                        onChange={(e) => setPreOrderForm(prev => ({ ...prev, unit: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      >
                        <option value="kg">Kilogram (kg)</option>
                        <option value="g">Gram (g)</option>
                        <option value="ton">Ton</option>
                        <option value="pieces">Pieces</option>
                        <option value="liters">Liters</option>
                        <option value="bags">Bags</option>
                        <option value="crates">Crates</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Price per Unit (₦) *</label>
                      <input
                        type="number"
                        required
                        min="0"
                        step="0.01"
                        value={preOrderForm.price_per_unit}
                        onChange={(e) => setPreOrderForm(prev => ({ ...prev, price_per_unit: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="e.g., 500"
                      />
                    </div>
                  </div>

                  {/* Partial Payment */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Partial Payment Required ({Math.round(preOrderForm.partial_payment_percentage * 100)}%)
                    </label>
                    <input
                      type="range"
                      min="0.1"
                      max="0.9"
                      step="0.05"
                      value={preOrderForm.partial_payment_percentage}
                      onChange={(e) => setPreOrderForm(prev => ({ ...prev, partial_payment_percentage: parseFloat(e.target.value) }))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>10%</span>
                      <span>90%</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      Buyers will pay {Math.round(preOrderForm.partial_payment_percentage * 100)}% upfront, remaining on delivery
                    </p>
                  </div>

                  {/* Location and Business Info */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Location *</label>
                      <input
                        type="text"
                        required
                        value={preOrderForm.location}
                        onChange={(e) => setPreOrderForm(prev => ({ ...prev, location: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="e.g., Lagos, Nigeria"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Date *</label>
                      <input
                        type="datetime-local"
                        required
                        value={preOrderForm.delivery_date}
                        onChange={(e) => setPreOrderForm(prev => ({ ...prev, delivery_date: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Business Name *</label>
                      <input
                        type="text"
                        required
                        value={preOrderForm.business_name}
                        onChange={(e) => setPreOrderForm(prev => ({ ...prev, business_name: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="e.g., Green Valley Farms"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Farm Name (optional)</label>
                      <input
                        type="text"
                        value={preOrderForm.farm_name}
                        onChange={(e) => setPreOrderForm(prev => ({ ...prev, farm_name: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="e.g., Green Valley Farm"
                      />
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                    <button
                      type="button"
                      onClick={() => setShowCreatePreOrder(false)}
                      className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium"
                    >
                      Create Pre-order
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Cart Modal */}
      {showCart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50">
          <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-lg flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold">🛒 Shopping Cart ({cart.length})</h2>
                <button
                  onClick={() => setShowCart(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {cart.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-gray-500 mb-4">
                    <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.1 5H17M9 19a2 2 0 1 0 4 0 2 2 0 0 0-4 0zM20 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" />
                    </svg>
                    <p className="text-lg">Your cart is empty</p>
                    <p className="text-sm">Add some products to get started!</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {cart.map((item) => (
                    <div key={item.id} className="bg-gray-50 rounded-lg p-3">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900 text-sm">
                            {item.product.product_name || item.product.crop_type}
                          </h3>
                          <p className="text-xs text-gray-600">
                            ₦{item.product.price_per_unit}/{item.unit}
                            {item.unit_specification && <span className="text-gray-500"> ({item.unit_specification})</span>} • {item.product.seller_username}
                          </p>
                        </div>
                        <button
                          onClick={() => removeCartItem(item.id)}
                          className="text-red-500 hover:text-red-700 text-sm"
                        >
                          ✕
                        </button>
                      </div>
                      
                      {/* Quantity Controls */}
                      <div className="flex items-center space-x-2 mb-2">
                        <button
                          onClick={() => updateCartItemQuantity(item.id, item.quantity - 1)}
                          className="w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-sm"
                        >
                          -
                        </button>
                        <span className="text-sm font-medium w-12 text-center">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => updateCartItemQuantity(item.id, item.quantity + 1)}
                          className="w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-sm"
                        >
                          +
                        </button>
                        <span className="text-xs text-gray-600">
                          {item.unit}{item.unit_specification && ` (${item.unit_specification})`}
                        </span>
                      </div>
                      
                      {/* Delivery Method Toggle */}
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-xs text-gray-600">Delivery:</span>
                        <button
                          onClick={() => updateCartItemDeliveryMethod(
                            item.id, 
                            item.delivery_method === 'platform' ? 'offline' : 'platform'
                          )}
                          className={`text-xs px-2 py-1 rounded-full ${
                            item.delivery_method === 'platform'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-green-100 text-green-700'
                          }`}
                        >
                          {item.delivery_method === 'platform' ? '🚛 Platform' : '🚚 Offline'}
                        </button>
                      </div>
                      
                      {/* Item Total */}
                      <div className="text-right">
                        <span className="font-semibold text-emerald-600">
                          ₦{(item.product.price_per_unit * item.quantity).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Cart Footer */}
            {cart.length > 0 && (
              <div className="p-4 border-t border-gray-200 bg-white">
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Items ({cart.reduce((sum, item) => sum + item.quantity, 0)})</span>
                    <span className="font-medium">₦{cart.reduce((sum, item) => sum + (item.product.price_per_unit * item.quantity), 0).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Est. Delivery</span>
                    <span className="font-medium">₦{Math.round(cart.length * 350).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between font-semibold text-emerald-600 pt-2 border-t border-gray-200">
                    <span>Total</span>
                    <span>₦{(cart.reduce((sum, item) => sum + (item.product.price_per_unit * item.quantity), 0) + Math.round(cart.length * 350)).toLocaleString()}</span>
                  </div>
                </div>
                
                <button
                  onClick={() => {
                    calculateOrderSummary();
                    proceedToCheckout();
                  }}
                  className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg hover:bg-emerald-700 font-medium transition-colors"
                >
                  Proceed to Checkout
                </button>
                
                <button
                  onClick={() => setShowCart(false)}
                  className="w-full mt-2 text-gray-600 hover:text-gray-800 py-2 text-sm"
                >
                  Continue Shopping
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Enhanced Messaging Modal */}
      {showMessaging && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50">
          <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-lg flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold">Messages</h2>
                <button
                  onClick={() => setShowMessaging(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>

            {!selectedConversation ? (
              <div className="flex-1 p-4">
                {/* Username Search */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Search users by username
                  </label>
                  <input
                    type="text"
                    value={usernameSearch}
                    onChange={(e) => {
                      setUsernameSearch(e.target.value);
                      searchUsers(e.target.value);
                    }}
                    placeholder="Enter username..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>

                {/* Search Results */}
                {foundUsers.length > 0 && (
                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Found Users</h3>
                    <div className="space-y-2">
                      {foundUsers.map(foundUser => (
                        <div
                          key={foundUser.username}
                          onClick={() => startConversation(foundUser)}
                          className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-emerald-500 text-white rounded-full flex items-center justify-center font-semibold">
                              {foundUser.username.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">
                                {foundUser.first_name} {foundUser.last_name}
                              </p>
                              <p className="text-sm text-gray-500">@{foundUser.username}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recent Conversations */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Recent Conversations</h3>
                  {conversations.length === 0 ? (
                    <p className="text-gray-500 text-center">No conversations yet. Search for users to start messaging!</p>
                  ) : (
                    <div className="space-y-2">
                      {conversations.map(conversation => (
                        <div
                          key={conversation.id}
                          onClick={() => setSelectedConversation(conversation)}
                          className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                              {conversation.avatar}
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">{conversation.name}</p>
                              <p className="text-sm text-gray-500">Click to view messages</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col">
                {/* Conversation Header */}
                <div className="p-3 border-b border-gray-200 bg-gray-50">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => setSelectedConversation(null)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      ←
                    </button>
                    <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                      {selectedConversation.avatar}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{selectedConversation.name}</p>
                      <p className="text-sm text-gray-500">Online</p>
                    </div>
                  </div>
                </div>

                {/* Messages Area */}
                <div className="flex-1 p-4 overflow-y-auto">
                  {messages.filter(msg => msg.conversation_id === selectedConversation.id).length === 0 ? (
                    <p className="text-gray-500 text-center">No messages yet. Start the conversation!</p>
                  ) : (
                    <div className="space-y-3">
                      {messages.filter(msg => msg.conversation_id === selectedConversation.id).map(message => (
                        <div
                          key={message.id}
                          className={`flex ${message.sender === user.username ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`max-w-xs px-3 py-2 rounded-lg ${
                            message.sender === user.username 
                              ? 'bg-emerald-500 text-white' 
                              : 'bg-gray-200 text-gray-900'
                          }`}>
                            {message.type === 'audio' ? (
                              <div>
                                <audio controls className="w-full">
                                  <source src={message.content} type="audio/webm" />
                                  Your browser does not support the audio element.
                                </audio>
                                <p className="text-xs mt-1 opacity-75">Voice message</p>
                              </div>
                            ) : (
                              <p>{message.content || message.text}</p>
                            )}
                            <p className="text-xs mt-1 opacity-75">
                              {new Date(message.timestamp).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Message Input Area */}
                <div className="p-4 border-t border-gray-200">
                  {audioBlob && (
                    <div className="mb-3 p-2 bg-green-50 rounded-lg border border-green-200">
                      <p className="text-sm text-green-700 mb-2">Voice message recorded</p>
                      <div className="flex space-x-2">
                        <button
                          onClick={sendAudioMessage}
                          className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                        >
                          Send
                        </button>
                        <button
                          onClick={() => setAudioBlob(null)}
                          className="px-3 py-1 bg-gray-500 text-white text-sm rounded hover:bg-gray-600"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                  
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      placeholder="Type a message..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    />
                    <button
                      onClick={isRecording ? stopRecording : startRecording}
                      className={`px-3 py-2 rounded-lg font-medium ${
                        isRecording 
                          ? 'bg-red-500 text-white hover:bg-red-600' 
                          : 'bg-blue-500 text-white hover:bg-blue-600'
                      }`}
                    >
                      {isRecording ? '⏹️' : '🎤'}
                    </button>
                    <button
                      onClick={sendMessage}
                      className="px-3 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 font-medium"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Order Tracking Modal */}
      {showOrderTracking && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-96 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold">Order Tracking</h2>
                <button
                  onClick={() => setShowOrderTracking(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-4 overflow-y-auto max-h-80">
              {orders.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No orders found</p>
              ) : (
                <div className="space-y-4">
                  {orders.map(order => (
                    <div key={order.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold text-gray-900">Order #{order.id.slice(-8)}</h3>
                          <p className="text-sm text-gray-600">
                            {new Date(order.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                          order.status === 'in_transit' ? 'bg-blue-100 text-blue-800' :
                          order.status === 'confirmed' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {order.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600 mb-2">
                        <p><strong>Total:</strong> ₦{order.total_amount.toLocaleString()}</p>
                        <p><strong>Items:</strong> {order.items.length} item(s)</p>
                        <p><strong>Delivery:</strong> {order.delivery_address}</p>
                      </div>

                      <div className="space-y-1">
                        {order.items.map((item, index) => (
                          <div key={index} className="flex justify-between text-sm">
                            <span>{item.title} × {item.quantity}</span>
                            <span>₦{item.total.toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Product Detail Modal - Simplified Version */}
      {showProductDetail && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-emerald-50 to-blue-50">
              <div className="flex justify-between items-start">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">
                    {selectedProduct.product_name || selectedProduct.crop_type}
                  </h1>
                  <div className="flex items-center space-x-4">
                    {/* Enhanced Pricing Display */}
                    <div className="text-3xl font-bold text-emerald-600">
                      ₦{selectedProduct.price_per_unit}/{selectedProduct.unit || selectedProduct.unit_of_measure || 'kg'}
                      {(selectedProduct.unit_specification) && 
                        <span className="text-lg font-medium text-gray-600 ml-2">
                          ({selectedProduct.unit_specification})
                        </span>
                      }
                    </div>
                    
                    {/* Pre-order Badge */}
                    {selectedProduct.type === 'preorder' && (
                      <div className="bg-orange-500 text-white px-4 py-2 rounded-full text-sm font-bold">
                        ⚡ PRE-ORDER
                      </div>
                    )}
                  </div>
                </div>
                
                <button
                  onClick={closeProductDetail}
                  className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
                >
                  ×
                </button>
              </div>
            </div>

            {/* Content - Scrollable */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left Column - Product Image and Info */}
                <div>
                  {/* Product Image */}
                  {selectedProduct.images && selectedProduct.images.length > 0 ? (
                    <img 
                      src={selectedProduct.images[0]} 
                      alt={selectedProduct.product_name || selectedProduct.crop_type}
                      className="w-full h-64 object-cover rounded-lg shadow-lg mb-4"
                    />
                  ) : (
                    <div className="w-full h-64 bg-gradient-to-r from-gray-200 to-gray-300 flex items-center justify-center rounded-lg shadow-lg mb-4">
                      <span className="text-gray-500 text-lg">📦 Product Image</span>
                    </div>
                  )}

                  {/* Product Description */}
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Product Description</h3>
                    <p className="text-gray-600 leading-relaxed">
                      {selectedProduct.description || 'High quality organic produce from certified farms. Fresh, nutritious, and carefully handled to ensure maximum freshness and quality.'}
                    </p>
                  </div>

                  {/* Location and Seller Info */}
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Seller Information</h3>
                    
                    {selectedProduct.farm_name && (
                      <div className="mb-2">
                        <span className="text-sm text-gray-600">Farm:</span>
                        <div className="font-medium text-gray-800">{selectedProduct.farm_name}</div>
                      </div>
                    )}

                    {selectedProduct.agent_username && (
                      <div className="mb-2">
                        <span className="text-sm text-gray-600">Agent:</span>
                        <div className="font-medium text-blue-600">@{selectedProduct.agent_username}</div>
                        <div className="flex items-center mt-1">
                          <span className="text-yellow-400">★★★★☆</span>
                          <span className="text-sm text-gray-600 ml-2">4.2/5 (Agent Rating)</span>
                        </div>
                      </div>
                    )}

                    <div>
                      <span className="text-sm text-gray-600">Location:</span>
                      <div className="font-medium text-gray-800">📍 {selectedProduct.location}</div>
                    </div>
                  </div>
                </div>

                {/* Right Column - Purchase Options */}
                <div>
                  {/* Stock Information */}
                  <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Stock Information</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-sm text-gray-600">Available:</span>
                        <div className="font-semibold text-emerald-600">
                          {selectedProduct.type === 'preorder' ? (
                            `${selectedProduct.available_stock || selectedProduct.total_stock || 100} ${selectedProduct.unit || 'kg'}`
                          ) : (
                            `${selectedProduct.quantity || '100'} ${selectedProduct.unit || 'kg'}`
                          )}
                        </div>
                      </div>
                      
                      {selectedProduct.type === 'preorder' && (
                        <>
                          <div>
                            <span className="text-sm text-gray-600">Pre-orders:</span>
                            <div className="font-semibold text-orange-600">
                              {selectedProduct.orders_count || 0}
                            </div>
                          </div>
                          <div>
                            <span className="text-sm text-gray-600">Partial Payment:</span>
                            <div className="font-semibold text-blue-600">
                              {Math.round((selectedProduct.partial_payment_percentage || 0.3) * 100)}%
                            </div>
                          </div>
                          <div>
                            <span className="text-sm text-gray-600">Delivery:</span>
                            <div className="font-semibold text-gray-700">
                              {new Date(selectedProduct.delivery_date).toLocaleDateString()}
                            </div>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Purchase Options */}
                  <div className="p-4 bg-emerald-50 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Purchase Options</h3>
                    
                    <div className="space-y-4">
                      {/* Quantity Selection */}
                      <div className="grid grid-cols-3 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                          <input
                            type="number"
                            min="1"
                            defaultValue="1"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            id={`detail-quantity`}
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
                          <select
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            id={`detail-unit`}
                          >
                            <option value="kg">kg</option>
                            <option value="bags">bags</option>
                            <option value="crates">crates</option>
                            <option value="gallons">gallons</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Spec</label>
                          <input
                            type="text"
                            placeholder="e.g., 100kg"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            id={`detail-spec`}
                          />
                        </div>
                      </div>

                      {/* Delivery Method */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Delivery Method</label>
                        <div className="flex space-x-4">
                          <label className="flex items-center">
                            <input
                              type="radio"
                              name="detail-delivery"
                              value="platform"
                              defaultChecked
                              className="w-4 h-4 text-emerald-600"
                            />
                            <span className="ml-2 text-sm text-gray-700">🚛 Platform Driver</span>
                          </label>
                          <label className="flex items-center">
                            <input
                              type="radio"
                              name="detail-delivery"
                              value="offline"
                              className="w-4 h-4 text-emerald-600"
                            />
                            <span className="ml-2 text-sm text-gray-700">🚚 Offline Delivery</span>
                          </label>
                        </div>
                      </div>

                      {/* Add to Cart Button */}
                      <button
                        onClick={() => {
                          const quantity = parseFloat(document.getElementById('detail-quantity')?.value) || 1;
                          const unit = document.getElementById('detail-unit')?.value || 'kg';
                          const specification = document.getElementById('detail-spec')?.value || '';
                          const deliveryMethod = document.querySelector('input[name="detail-delivery"]:checked')?.value || 'platform';
                          
                          addEnhancedToCart(selectedProduct, quantity, unit, specification, deliveryMethod);
                          closeProductDetail();
                        }}
                        className={`w-full py-3 px-6 rounded-lg font-bold text-lg transition-colors ${
                          selectedProduct.type === 'preorder'
                            ? 'bg-orange-600 hover:bg-orange-700 text-white'
                            : 'bg-emerald-600 hover:bg-emerald-700 text-white'
                        }`}
                      >
                        {selectedProduct.type === 'preorder' ? '🛒 Add Pre-order to Cart' : '🛒 Add to Cart'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Simple Pre-Order and Recommended Sections */}
              <div className="mt-8 pt-8 border-t border-gray-200">
                <h2 className="text-xl font-bold text-gray-900 mb-4">🔥 More Pre-Orders Available</h2>
                <div className="flex space-x-4 overflow-x-auto pb-4">
                  {products.filter(product => 
                    product.type === 'preorder' && 
                    (product.id || product._id) !== (selectedProduct.id || selectedProduct._id)
                  ).slice(0, 3).map((product, index) => (
                    <div key={index} className="flex-shrink-0 w-48 bg-orange-50 rounded-lg p-3 border border-orange-200 cursor-pointer"
                         onClick={() => setSelectedProduct(product)}>
                      <h4 className="font-bold text-sm text-gray-900 mb-1">
                        {product.product_name || product.crop_type}
                      </h4>
                      <div className="text-orange-600 font-bold">
                        ₦{product.price_per_unit}/{product.unit || 'kg'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;