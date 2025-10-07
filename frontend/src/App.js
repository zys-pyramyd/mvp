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
  
  // Drop-off locations state
  const [dropOffLocations, setDropOffLocations] = useState([]);
  const [showAddDropOff, setShowAddDropOff] = useState(false);
  const [showCreatePreOrder, setShowCreatePreOrder] = useState(false);
  const [showPreOrderDetails, setShowPreOrderDetails] = useState(false);
  const [selectedPreOrder, setSelectedPreOrder] = useState(null);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  
  // Enhanced delivery options state
  const [productDeliveryOptions, setProductDeliveryOptions] = useState({});
  const [selectedDeliveryMethod, setSelectedDeliveryMethod] = useState('dropoff');

  // Rating system state
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [ratingModalData, setRatingModalData] = useState(null);
  const [userRatings, setUserRatings] = useState({});
  const [productRatings, setProductRatings] = useState({});

  // Driver management state (for logistics businesses)
  const [showDriverManagement, setShowDriverManagement] = useState(false);
  const [driverSlots, setDriverSlots] = useState([]);
  const [availableDrivers, setAvailableDrivers] = useState([]);
  const [showFindDrivers, setShowFindDrivers] = useState(false);
  const [driverSearchFilters, setDriverSearchFilters] = useState({
    location: '',
    vehicle_type: '',
    min_rating: null
  });

  // Digital wallet state
  const [showWallet, setShowWallet] = useState(false);
  const [walletSummary, setWalletSummary] = useState(null);
  const [walletTransactions, setWalletTransactions] = useState([]);
  const [bankAccounts, setBankAccounts] = useState([]);
  const [showFundWallet, setShowFundWallet] = useState(false);
  const [showWithdrawFunds, setShowWithdrawFunds] = useState(false);
  const [showAddBankAccount, setShowAddBankAccount] = useState(false);
  
  // Gift card state
  const [showGiftCards, setShowGiftCards] = useState(false);
  const [userGiftCards, setUserGiftCards] = useState([]);
  const [showCreateGiftCard, setShowCreateGiftCard] = useState(false);
  const [showRedeemGiftCard, setShowRedeemGiftCard] = useState(false);
  const [giftCardDetails, setGiftCardDetails] = useState(null);

  // Categories and business profile state
  const [businessCategories, setBusinessCategories] = useState({});
  const [productCategories, setProductCategories] = useState({});
  const [showBusinessProfile, setShowBusinessProfile] = useState(false);
  const [showKYCPrompt, setShowKYCPrompt] = useState(false);
  const [kycStatus, setKycStatus] = useState(null);

  // Dashboard and trading platform state
  const [showFarmerDashboard, setShowFarmerDashboard] = useState(false);
  const [showAgentDashboard, setShowAgentDashboard] = useState(false);
  const [farmerDashboardData, setFarmerDashboardData] = useState(null);
  const [agentDashboardData, setAgentDashboardData] = useState(null);
  const [showMarketChart, setShowMarketChart] = useState(false);
  const [marketPrices, setMarketPrices] = useState([]);
  
  // Location and filtering state
  const [locationFilter, setLocationFilter] = useState('');
  const [availableLocations, setAvailableLocations] = useState([]);
  
  // Enhanced Buy from Farm state
  const [bulkListings, setBulkListings] = useState([]);
  const [showBulkListing, setShowBulkListing] = useState(false);
  
  // Category navigation state
  const [categoryScrollPosition, setCategoryScrollPosition] = useState(0);
  
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
    fetchDropOffLocations();
    fetchMarketPrices();
    fetchBulkListings();
    
    // Migrate existing cart items to ensure proper structure
    if (cart.length > 0) {
      migrateCartItems();
    }
  }, [currentPlatform, selectedCategory, searchTerm]);

  // Update available locations when products change
  useEffect(() => {
    if (products.length > 0) {
      fetchAvailableLocations();
    }
  }, [products]);

  // Auto-change slides every 5 seconds
  useEffect(() => {
    const slideInterval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slideContent.length);
    }, 5000);

    return () => clearInterval(slideInterval);
  }, [slideContent.length]);

  // Load driver slots for logistics businesses
  useEffect(() => {
    if (user && user.role === 'logistics') {
      fetchDriverSlots();
    }
    // Load wallet data for authenticated users
    if (user) {
      fetchWalletSummary();
      fetchKYCStatus();
    }
  }, [user]);

  // Load categories on app initialization
  useEffect(() => {
    fetchBusinessCategories();
    fetchProductCategories();
  }, []);

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

  const fetchDropOffLocations = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/dropoff-locations?active_only=true&limit=100`);
      if (response.ok) {
        const data = await response.json();
        setDropOffLocations(data.locations || []);
      }
    } catch (error) {
      console.error('Error fetching drop-off locations:', error);
    }
  };

  // Fetch product delivery options
  const fetchProductDeliveryOptions = async (productId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/products/${productId}/delivery-options`);
      if (response.ok) {
        const data = await response.json();
        setProductDeliveryOptions(prev => ({
          ...prev,
          [productId]: data
        }));
        return data;
      }
    } catch (error) {
      console.error('Error fetching product delivery options:', error);
    }
    return null;
  };

  // Rating system functions
  const submitRating = async (ratingData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ratings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(ratingData)
      });

      if (response.ok) {
        const result = await response.json();
        // Update local state
        if (ratingData.rating_type === 'user_rating') {
          await fetchUserRatings(ratingData.rated_entity_id);
        } else if (ratingData.rating_type === 'product_rating') {
          await fetchProductRatings(ratingData.rated_entity_id);
        }
        return result;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to submit rating');
      }
    } catch (error) {
      console.error('Error submitting rating:', error);
      throw error;
    }
  };

  const fetchUserRatings = async (userId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ratings/${userId}?rating_type=user_rating`);
      if (response.ok) {
        const data = await response.json();
        setUserRatings(prev => ({
          ...prev,
          [userId]: data
        }));
        return data;
      }
    } catch (error) {
      console.error('Error fetching user ratings:', error);
    }
    return null;
  };

  const fetchProductRatings = async (productId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ratings/${productId}?rating_type=product_rating`);
      if (response.ok) {
        const data = await response.json();
        setProductRatings(prev => ({
          ...prev,
          [productId]: data
        }));
        return data;
      }
    } catch (error) {
      console.error('Error fetching product ratings:', error);
    }
    return null;
  };

  const openRatingModal = (ratingType, entityId, entityUsername = null, orderId = null) => {
    setRatingModalData({
      rating_type: ratingType,
      rated_entity_id: entityId,
      rated_entity_username: entityUsername,
      order_id: orderId
    });
    setShowRatingModal(true);
  };

  const closeRatingModal = () => {
    setShowRatingModal(false);
    setRatingModalData(null);
  };

  // Driver management functions (for logistics businesses)
  const fetchDriverSlots = async () => {
    if (!user || user.role !== 'logistics') return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/driver-slots/my-slots`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDriverSlots(data.slots || []);
        return data;
      }
    } catch (error) {
      console.error('Error fetching driver slots:', error);
    }
    return null;
  };

  const purchaseDriverSlots = async (slotsCount) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/driver-slots/purchase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ slots_count: slotsCount })
      });

      if (response.ok) {
        const result = await response.json();
        await fetchDriverSlots(); // Refresh slots
        return result;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to purchase driver slots');
      }
    } catch (error) {
      console.error('Error purchasing driver slots:', error);
      throw error;
    }
  };

  const assignDriverToSlot = async (slotId, driverData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/driver-slots/${slotId}/assign-driver`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(driverData)
      });

      if (response.ok) {
        const result = await response.json();
        await fetchDriverSlots(); // Refresh slots
        return result;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to assign driver to slot');
      }
    } catch (error) {
      console.error('Error assigning driver:', error);
      throw error;
    }
  };

  const fetchAvailableDrivers = async (filters = {}) => {
    try {
      const queryParams = new URLSearchParams();
      if (filters.location) queryParams.append('location', filters.location);
      if (filters.vehicle_type) queryParams.append('vehicle_type', filters.vehicle_type);
      if (filters.min_rating) queryParams.append('min_rating', filters.min_rating);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/drivers/find-drivers?${queryParams}`);
      if (response.ok) {
        const data = await response.json();
        setAvailableDrivers(data.drivers || []);
        return data;
      }
    } catch (error) {
      console.error('Error fetching available drivers:', error);
    }
    return null;
  };

  // Digital Wallet management functions
  const fetchWalletSummary = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wallet/summary`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setWalletSummary(data);
        return data;
      }
    } catch (error) {
      console.error('Error fetching wallet summary:', error);
    }
    return null;
  };

  const fundWallet = async (amount, fundingMethod, description) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wallet/fund`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          transaction_type: 'wallet_funding',
          amount: parseFloat(amount),
          description: description,
          funding_method: fundingMethod
        })
      });

      if (response.ok) {
        const result = await response.json();
        await fetchWalletSummary(); // Refresh wallet data
        await fetchWalletTransactions(); // Refresh transactions
        return result;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fund wallet');
      }
    } catch (error) {
      console.error('Error funding wallet:', error);
      throw error;
    }
  };

  const withdrawFunds = async (amount, bankAccountId, description) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wallet/withdraw`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          amount: parseFloat(amount),
          bank_account_id: bankAccountId,
          description: description
        })
      });

      if (response.ok) {
        const result = await response.json();
        await fetchWalletSummary(); // Refresh wallet data
        await fetchWalletTransactions(); // Refresh transactions
        return result;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to withdraw funds');
      }
    } catch (error) {
      console.error('Error withdrawing funds:', error);
      throw error;
    }
  };

  const fetchWalletTransactions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wallet/transactions?limit=50`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setWalletTransactions(data.transactions || []);
        return data;
      }
    } catch (error) {
      console.error('Error fetching wallet transactions:', error);
    }
    return null;
  };

  const fetchBankAccounts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wallet/bank-accounts`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBankAccounts(data.accounts || []);
        return data;
      }
    } catch (error) {
      console.error('Error fetching bank accounts:', error);
    }
    return null;
  };

  const addBankAccount = async (accountData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wallet/bank-accounts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(accountData)
      });

      if (response.ok) {
        const result = await response.json();
        await fetchBankAccounts(); // Refresh bank accounts
        return result;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add bank account');
      }
    } catch (error) {
      console.error('Error adding bank account:', error);
      throw error;
    }
  };

  // Gift Card management functions
  const createGiftCard = async (amount, recipientEmail, recipientName, message) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wallet/gift-cards`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          amount: parseFloat(amount),
          recipient_email: recipientEmail || null,
          recipient_name: recipientName || null,
          message: message || null
        })
      });

      if (response.ok) {
        const result = await response.json();
        await fetchWalletSummary(); // Refresh wallet data
        await fetchUserGiftCards(); // Refresh gift cards
        return result;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create gift card');
      }
    } catch (error) {
      console.error('Error creating gift card:', error);
      throw error;
    }
  };

  const redeemGiftCard = async (cardCode, amount = null) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wallet/gift-cards/redeem`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          card_code: cardCode.toUpperCase(),
          amount: amount ? parseFloat(amount) : null
        })
      });

      if (response.ok) {
        const result = await response.json();
        await fetchWalletSummary(); // Refresh wallet data
        return result;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to redeem gift card');
      }
    } catch (error) {
      console.error('Error redeeming gift card:', error);
      throw error;
    }
  };

  const fetchUserGiftCards = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wallet/gift-cards/my-cards`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserGiftCards(data.gift_cards || []);
        return data;
      }
    } catch (error) {
      console.error('Error fetching user gift cards:', error);
    }
    return null;
  };

  const fetchGiftCardDetails = async (cardCode) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/wallet/gift-cards/${cardCode.toUpperCase()}`);
      
      if (response.ok) {
        const data = await response.json();
        setGiftCardDetails(data);
        return data;
      } else {
        setGiftCardDetails(null);
        return null;
      }
    } catch (error) {
      console.error('Error fetching gift card details:', error);
      setGiftCardDetails(null);
      return null;
    }
  };

  // Categories and business functions
  const fetchBusinessCategories = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/categories/business`);
      if (response.ok) {
        const data = await response.json();
        setBusinessCategories(data.categories || {});
        return data;
      }
    } catch (error) {
      console.error('Error fetching business categories:', error);
    }
    return null;
  };

  const fetchProductCategories = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/categories/products`);
      if (response.ok) {
        const data = await response.json();
        setProductCategories(data.categories || {});
        return data;
      }
    } catch (error) {
      console.error('Error fetching product categories:', error);
    }
    return null;
  };

  const updateBusinessProfile = async (businessData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/business-profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(businessData)
      });

      if (response.ok) {
        const result = await response.json();
        return result;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update business profile');
      }
    } catch (error) {
      console.error('Error updating business profile:', error);
      throw error;
    }
  };

  const fetchKYCStatus = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/kyc/status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setKycStatus(data);
        
        // Show KYC prompt for non-personal accounts that haven't completed KYC
        if (data.requires_kyc && data.status === 'not_started' && !showKYCPrompt) {
          setTimeout(() => setShowKYCPrompt(true), 3000); // Show after 3 seconds
        }
        
        return data;
      }
    } catch (error) {
      console.error('Error fetching KYC status:', error);
    }
    return null;
  };

  // Dashboard functions
  const fetchFarmerDashboard = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/farmer/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFarmerDashboardData(data);
        return data;
      }
    } catch (error) {
      console.error('Error fetching farmer dashboard:', error);
    }
    return null;
  };

  const fetchAgentDashboard = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAgentDashboardData(data);
        return data;
      }
    } catch (error) {
      console.error('Error fetching agent dashboard:', error);
    }
    return null;
  };

  // Market price functions
  const fetchMarketPrices = async () => {
    try {
      // Mock market price data - in production this would come from market data API
      const mockMarketData = [
        { product: 'Rice (50kg bag)', price: 35000, trend: '+5%', category: 'raw_food' },
        { product: 'Beans (100kg bag)', price: 85000, trend: '+2%', category: 'raw_food' },
        { product: 'Yam (100kg)', price: 45000, trend: '-3%', category: 'raw_food' },
        { product: 'Tomatoes (big basket)', price: 8000, trend: '+8%', category: 'pepper_vegetables' },
        { product: 'Onions (50kg bag)', price: 25000, trend: '+1%', category: 'pepper_vegetables' },
        { product: 'Garri (50kg bag)', price: 32000, trend: '+4%', category: 'packaged_food' },
        { product: 'Palm Oil (25L tin)', price: 22000, trend: '+6%', category: 'raw_food' },
        { product: 'Fresh Fish (kg)', price: 2500, trend: '+3%', category: 'fish_meat' }
      ];
      
      setMarketPrices(mockMarketData);
      return mockMarketData;
    } catch (error) {
      console.error('Error fetching market prices:', error);
    }
    return [];
  };

  // Location functions
  const fetchAvailableLocations = async () => {
    try {
      // Extract unique locations from products
      const productLocations = [...new Set(products.map(p => p.location))];
      setAvailableLocations(productLocations);
      return productLocations;
    } catch (error) {
      console.error('Error fetching locations:', error);
    }
    return [];
  };

  // Bulk listings for Buy from Farm
  const fetchBulkListings = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/products`);
      if (response.ok) {
        const data = await response.json();
        
        // Filter for bulk listings by farmers and agents
        const bulk = data.products.filter(product => 
          (product.listed_by_agent || product.seller_name?.toLowerCase().includes('farmer') || 
           product.farm_name) && product.minimum_order_quantity >= 10
        );
        
        setBulkListings(bulk);
        return bulk;
      }
    } catch (error) {
      console.error('Error fetching bulk listings:', error);
    }
    return [];
  };

  // Category navigation functions  
  const scrollCategories = (direction) => {
    const container = document.getElementById('categories-container');
    if (container) {
      const scrollAmount = 200;
      const newPosition = direction === 'left' 
        ? Math.max(0, categoryScrollPosition - scrollAmount)
        : Math.min(container.scrollWidth - container.clientWidth, categoryScrollPosition + scrollAmount);
      
      container.scrollTo({ left: newPosition, behavior: 'smooth' });
      setCategoryScrollPosition(newPosition);
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
  const openProductDetail = async (product) => {
    setSelectedProduct(product);
    setShowProductDetail(true);
    
    // Fetch delivery options for this product
    const productId = product.id || product._id;
    if (productId) {
      const deliveryOptions = await fetchProductDeliveryOptions(productId);
      
      // Set default delivery method based on what's supported
      if (deliveryOptions) {
        if (deliveryOptions.supports_dropoff_delivery) {
          setSelectedDeliveryMethod('dropoff');
        } else if (deliveryOptions.supports_shipping_delivery) {
          setSelectedDeliveryMethod('shipping');
        }
      }
    }
  };

  const closeProductDetail = () => {
    setShowProductDetail(false);
    setSelectedProduct(null);
    setSelectedDeliveryMethod('dropoff'); // Reset to default
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

  const addEnhancedToCart = (product, quantity, unit, specification, deliveryMethod, dropoffLocation = null, shippingAddress = null) => {
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
              delivery_method: deliveryMethod,
              dropoff_location: dropoffLocation,
              shipping_address: shippingAddress
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
        delivery_method: deliveryMethod,
        dropoff_location: dropoffLocation,
        shipping_address: shippingAddress
      };
      
      setCart(prevCart => [...prevCart, cartItem]);
    }
    
    const quantityDisplay = `${quantity} ${unit}${specification ? ` (${specification})` : ''}`;
    let deliveryDisplay = 'Platform Driver';
    if (deliveryMethod === 'offline') {
      deliveryDisplay = 'Offline Delivery';
    } else if (deliveryMethod === 'dropoff' && dropoffLocation) {
      deliveryDisplay = `Drop-off at ${dropoffLocation.name}`;
    } else if (shippingAddress) {
      deliveryDisplay = 'Home Delivery';
    }
    
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
      // Check what types of delivery methods we have in cart
      const hasDropoffItems = cart.some(item => item.delivery_method === 'dropoff');
      const hasShippingItems = cart.some(item => item.delivery_method !== 'dropoff' && item.shipping_address);
      const hasOldShippingItems = cart.some(item => item.delivery_method !== 'dropoff' && !item.shipping_address);
      
      // Validate traditional shipping address form if we have old-style shipping items
      if (hasOldShippingItems && !validateAddress()) return;
      
      const token = localStorage.getItem('token');
      const orders = [];
      
      // Create individual orders for each cart item (to handle different sellers)
      for (const item of cart) {
        const orderData = {
          product_id: item.product.id || item.product._id,
          quantity: item.quantity,
          unit: item.unit,
          unit_specification: item.unit_specification,
          delivery_method: item.delivery_method
        };
        
        // Add appropriate delivery details based on method
        if (item.delivery_method === 'dropoff' && item.dropoff_location) {
          orderData.dropoff_location_id = item.dropoff_location.id;
        } else if (item.shipping_address) {
          // Use shipping address from cart item (new enhanced delivery system)
          orderData.shipping_address = item.shipping_address;
        } else if (item.delivery_method !== 'dropoff') {
          // Use traditional shipping address form (backward compatibility)
          orderData.shipping_address = `${shippingAddress.full_name}, ${shippingAddress.address_line_1}, ${shippingAddress.address_line_2 ? shippingAddress.address_line_2 + ', ' : ''}${shippingAddress.city}, ${shippingAddress.state}, ${shippingAddress.country}`;
        }
        
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
          
          // Handle KYC-specific errors
          if (error.detail && typeof error.detail === 'object' && error.detail.error === 'KYC_REQUIRED') {
            const kycError = error.detail;
            alert(`KYC Verification Required\n\n${kycError.message}\n\nRequired Documents:\n${kycError.required_actions.documents.join('\n• ')}\n\nStatus: ${kycError.kyc_status}\n\nPlease complete your KYC verification in your profile settings to continue.`);
            return;
          }
          
          throw new Error(error.detail || 'Failed to create order');
        }
      }
      
      // Clear cart and show success
      setCart([]);
      setShowCheckout(false);
      
      // Calculate total from orders with delivery costs
      const totalAmount = orders.reduce((sum, order) => sum + (order.cost_breakdown?.total_amount || order.total_amount || 0), 0);
      
      let successMessage = `Orders created successfully! 
      Total orders: ${orders.length}
      Total amount: ₦${totalAmount.toLocaleString()}
      Order IDs: ${orders.map(o => o.order_id).join(', ')}`;
      
      // Add delivery cost breakdown if applicable
      const totalDeliveryCost = orders.reduce((sum, order) => sum + (order.cost_breakdown?.delivery_cost || 0), 0);
      if (totalDeliveryCost > 0) {
        successMessage += `\n\nCost Breakdown:
        Product Total: ₦${(totalAmount - totalDeliveryCost).toLocaleString()}
        Delivery Cost: ₦${totalDeliveryCost.toLocaleString()}`;
      }
      // Add drop-off location info if applicable
      const dropoffOrders = orders.filter(o => o.delivery_info?.method === 'dropoff');
      if (dropoffOrders.length > 0) {
        successMessage += `\n\nDrop-off Locations:`;
        dropoffOrders.forEach(order => {
          if (order.delivery_info?.dropoff_location) {
            const loc = order.delivery_info.dropoff_location;
            successMessage += `\n• ${loc.name} - ${loc.city}, ${loc.state}`;
          }
        });
      }
      
      alert(successMessage);
      
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
    // All users can access both home page and buy from farm for viewing
    return ['home', 'buy_from_farm'];
  };

  const canPostOnPlatform = (userRole, platform) => {
    // Role-based posting restrictions
    if (platform === 'home') {
      // Only businesses can post on home page (main business page)
      return userRole === 'business';
    } else if (platform === 'buy_from_farm') {
      // Only farmers and agents can post on buy from farm page
      return userRole === 'farmer' || userRole === 'agent';
    }
    return false;
  };

  const canSwitchPlatforms = (userRole) => {
    // All users can switch between main page and buy from farm for viewing
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
      {/* KYC Notification Banner - Only for non-personal accounts who need KYC */}
      {user && user.role !== 'personal' && kycStatus && kycStatus.status !== 'approved' && (
        <div className={`${
          kycStatus.status === 'not_started' 
            ? 'bg-red-500' 
            : kycStatus.status === 'pending'
            ? 'bg-yellow-500'
            : 'bg-red-500'
        } text-white px-4 py-2 text-center text-sm`}>
          <div className="max-w-7xl mx-auto flex items-center justify-center space-x-4">
            <span>
              {kycStatus.status === 'not_started' && '⚠️ Complete your KYC verification to start receiving payments'}
              {kycStatus.status === 'pending' && '⏳ Your KYC is under review. You\'ll be able to receive payments once approved'}
              {kycStatus.status === 'rejected' && '❌ Your KYC was rejected. Please resubmit with correct documents'}
            </span>
            {kycStatus.status !== 'pending' && (
              <button
                onClick={() => {
                  // Navigate to KYC completion
                  alert('KYC completion form will open here. This includes:\n\n' +
                        'For Registered Businesses:\n- Business Registration Number\n- TIN Certificate\n- Certificate of Incorporation\n\n' +
                        'For Others (Farmers/Agents/Unregistered):\n- NIN or BVN\n- Headshot photo (camera)\n- National ID upload\n- Utility bill');
                }}
                className="bg-white text-red-600 px-3 py-1 rounded text-xs font-medium hover:bg-gray-100 transition-colors"
              >
                Complete Now
              </button>
            )}
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            {/* Logo - Better Responsive Scaling */}
            <div className="flex items-center flex-shrink-0">
              <img 
                src="https://customer-assets.emergentagent.com/job_pyramyd-agritech/artifacts/ml8alcyl_image.png" 
                alt="Pyramyd" 
                className="h-5 sm:h-6 md:h-8 lg:h-10 w-auto"
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

            {/* Right side navigation icons - Responsive Priority */}
            <div className="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
              {/* Cart - Always Visible */}
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

              {/* Messaging - Hidden on mobile, shown in profile menu */}
              <button
                onClick={() => {
                  if (!user) {
                    setShowAuthModal(true);
                  } else {
                    setShowMessaging(true);
                  }
                }}
                className="nav-button icon-button relative p-1.5 sm:p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg border border-gray-200 hover:border-emerald-500 hidden md:flex"
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

              {/* Order Tracking - Hidden on mobile, shown in profile menu */}
              <button
                onClick={() => {
                  if (!user) {
                    setShowAuthModal(true);
                  } else {
                    setShowOrderTracking(true);
                    fetchOrders();
                  }
                }}
                className="nav-button icon-button p-1.5 sm:p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg border border-gray-200 hover:border-emerald-500 hidden md:flex"
                title="Track Orders / Find Drivers"
              >
                <div className="w-5 h-5 sm:w-6 sm:h-6">
                  <TruckIcon />
                </div>
              </button>

              {/* Profile Icon with Dropdown - Always Visible */}
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
                        
                        {/* KYC Status Badge */}
                        {user.role !== 'personal' && kycStatus && (
                          <div className="mt-2">
                            <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              kycStatus.status === 'approved' 
                                ? 'bg-green-100 text-green-800' 
                                : kycStatus.status === 'pending'
                                ? 'bg-yellow-100 text-yellow-800'
                                : kycStatus.status === 'rejected'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {kycStatus.status === 'approved' && '✅ KYC Verified'}
                              {kycStatus.status === 'pending' && '⏳ KYC Pending'}
                              {kycStatus.status === 'rejected' && '❌ KYC Rejected'}
                              {kycStatus.status === 'not_started' && '⚠️ KYC Required'}
                            </div>
                            
                            {/* Payment capability indicator */}
                            <div className="text-xs text-gray-500 mt-1">
                              {kycStatus.status === 'approved' 
                                ? '✅ Can receive payments' 
                                : '⚠️ Cannot receive payments'}
                            </div>
                          </div>
                        )}
                        
                        {/* Personal account badge */}
                        {user.role === 'personal' && (
                          <div className="mt-2">
                            <div className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              👤 Personal Account
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              ✅ Can purchase products
                            </div>
                          </div>
                        )}
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

                      {/* Mobile-only options - show on tablets and smaller */}
                      <div className="md:hidden border-t border-gray-200 pt-2 mt-2">
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            setShowMessaging(true);
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        >
                          💬 Messages
                        </button>
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            setShowOrderTracking(true);
                            fetchOrders();
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        >
                          🚛 Order Tracking
                        </button>
                      </div>

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

                      {/* Show agent-specific options for agents */}
                      {user.role === 'agent' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            setShowAddDropOff(true);
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-gray-50 font-medium"
                        >
                          📍 Add Drop-off Location
                        </button>
                      )}
                      
                      {/* Complete KYC - Only show for non-personal accounts who haven't completed KYC */}
                      {user.role !== 'personal' && kycStatus && kycStatus.status !== 'approved' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            // Navigate to KYC completion - would implement KYC modal
                            alert('KYC completion form will open here. This includes:\n\n' +
                                  'For Registered Businesses:\n- Business Registration Number\n- TIN Certificate\n- Certificate of Incorporation\n\n' +
                                  'For Others (Farmers/Agents/Unregistered):\n- NIN or BVN\n- Headshot photo (camera)\n- National ID upload\n- Utility bill');
                          }}
                          className={`block w-full text-left px-4 py-2 text-sm font-medium border-l-4 ${
                            kycStatus.status === 'not_started' 
                              ? 'text-red-600 hover:bg-red-50 border-red-400 bg-red-25' 
                              : kycStatus.status === 'pending'
                              ? 'text-yellow-600 hover:bg-yellow-50 border-yellow-400 bg-yellow-25'
                              : 'text-blue-600 hover:bg-blue-50 border-blue-400 bg-blue-25'
                          }`}
                        >
                          {kycStatus.status === 'not_started' && '🔐 Complete KYC (Required)'}
                          {kycStatus.status === 'pending' && '⏳ KYC Under Review'}
                          {kycStatus.status === 'rejected' && '❌ Resubmit KYC'}
                        </button>
                      )}

                      {/* Digital Wallet */}
                      <button
                        onClick={() => {
                          setShowProfileMenu(false);
                          setShowWallet(true);
                          fetchWalletSummary();
                          fetchWalletTransactions();
                          fetchBankAccounts();
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-gray-50 font-medium"
                      >
                        💰 My Wallet
                      </button>

                      {/* Gift Cards */}
                      <button
                        onClick={() => {
                          setShowProfileMenu(false);
                          setShowGiftCards(true);
                          fetchUserGiftCards();
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-pink-600 hover:bg-gray-50 font-medium"
                      >
                        🎁 Gift Cards
                      </button>

                      {/* Rating & Reviews */}
                      <button
                        onClick={() => {
                          setShowProfileMenu(false);
                          alert('Feature coming soon! View and manage your ratings and reviews.');
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        ⭐ My Ratings & Reviews
                      </button>

                      {/* Driver Management for logistics businesses */}
                      {user.role === 'logistics' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            setShowDriverManagement(true);
                            fetchDriverSlots();
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-50 font-medium"
                        >
                          🚗 Manage Drivers
                        </button>
                      )}

                      {/* Find Drivers option for all users */}
                      <button
                        onClick={() => {
                          setShowProfileMenu(false);
                          setShowFindDrivers(true);
                          fetchAvailableDrivers();
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        🔍 Find Drivers
                      </button>

                      {/* Farmer Dashboard */}
                      {user.role === 'farmer' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            setShowFarmerDashboard(true);
                            fetchFarmerDashboard();
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-gray-50 font-medium"
                        >
                          🌾 Farmer Dashboard
                        </button>
                      )}

                      {/* Agent Dashboard */}
                      {user.role === 'agent' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            setShowAgentDashboard(true);
                            fetchAgentDashboard();
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-gray-50 font-medium"
                        >
                          🤝 Agent Dashboard
                        </button>
                      )}

                      {/* Market Prices */}
                      <button
                        onClick={() => {
                          setShowProfileMenu(false);
                          setShowMarketChart(true);
                          fetchMarketPrices();
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-50 font-medium"
                      >
                        📈 Market Prices
                      </button>

                      {/* Driver Portal Access (for drivers) */}
                      {user.role === 'driver' && (
                        <button
                          onClick={() => {
                            setShowProfileMenu(false);
                            alert('Driver Portal Access - Feature coming soon!\nTrack your deliveries, earnings, and ratings.');
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-gray-50 font-medium"
                        >
                          🚛 Driver Portal
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
                      {product.partial_payment_percentage ? 
                        `${Math.round(product.partial_payment_percentage * 100)}% Payment` : 
                        '100% Payment'
                      }
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
                          <span>💰 Payment Required:</span>
                          <span className="font-bold">
                            {product.partial_payment_percentage ? 
                              `${Math.round(product.partial_payment_percentage * 100)}%` : 
                              '100%'
                            }
                          </span>
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

        {/* Enhanced Category Navigation & Filters */}
        <div className="mb-6 space-y-4">
          {/* Location Filter */}
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-700">📍 Location:</span>
              <select
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
              >
                <option value="">All Locations</option>
                {availableLocations.map(location => (
                  <option key={location} value={location}>{location}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Enhanced Category Navigation */}
          <div className="relative">
            <div className="flex items-center">
              {/* Left Scroll Button */}
              <button
                onClick={() => scrollCategories('left')}
                className="hidden md:flex items-center justify-center w-10 h-10 bg-white shadow-md rounded-full border hover:bg-gray-50 transition-colors mr-2 z-10"
              >
                <span className="text-gray-600">←</span>
              </button>

              {/* Categories Container */}
              <div 
                id="categories-container"
                className="flex overflow-x-auto space-x-3 scrollbar-hide flex-1 py-2"
                style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
              >
                {Object.entries(productCategories).map(([key, category]) => (
                  <div
                    key={key}
                    className="flex-shrink-0 bg-white border border-gray-200 rounded-lg p-3 hover:border-emerald-300 transition-colors cursor-pointer min-w-[120px]"
                    onClick={() => {
                      // Filter products by category
                      const filtered = products.filter(p => p.category === key);
                      // You could implement category filtering here
                    }}
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-1">
                        {key === 'farm_input' ? '🌱' :
                         key === 'raw_food' ? '🌾' :
                         key === 'packaged_food' ? '📦' :
                         key === 'fish_meat' ? '🐟' :
                         key === 'pepper_vegetables' ? '🌶️' : '📦'}
                      </div>
                      <div className="text-xs font-medium text-gray-700">{category.name}</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Right Scroll Button */}
              <button
                onClick={() => scrollCategories('right')}
                className="hidden md:flex items-center justify-center w-10 h-10 bg-white shadow-md rounded-full border hover:bg-gray-50 transition-colors ml-2 z-10"
              >
                <span className="text-gray-600">→</span>
              </button>
            </div>

            {/* Mobile Swipe Hint */}
            <div className="md:hidden text-center text-xs text-gray-500 mt-2">
              👆 Swipe to see more categories
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
            products
              .filter(product => 
                // Apply location filter
                locationFilter === '' || product.location === locationFilter
              )
              .map((product, index) => (
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

                <div className="p-3 sm:p-4 flex-1 flex flex-col">{/* Responsive padding */}
                  <h3 className="font-semibold text-gray-900 mb-2 text-sm sm:text-base line-clamp-1">
                    {product.product_name || product.crop_type}
                  </h3>
                  
                  {/* Description */}
                  <p className="text-gray-600 text-xs sm:text-sm mb-3 line-clamp-2">
                    {product.description || 'Fresh organic produce from certified farms'}
                  </p>

                  {/* Price with Enhanced Specification Display - Responsive */}
                  <div className="text-lg sm:text-xl font-bold text-emerald-600 mb-2">
                    ₦{product.price_per_unit}/{product.unit || product.unit_of_measure || 'kg'}
                    {(product.unit_specification || product.unit_of_measure !== (product.unit || 'kg')) && 
                      <span className="text-xs sm:text-sm font-medium text-gray-600 ml-1">
                        ({product.unit_specification || product.unit_of_measure || 'standard'})
                      </span>
                    }
                  </div>

                  {/* Stock Info - Responsive */}
                  <div className="text-xs sm:text-sm text-gray-500 mb-2">
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

                  {/* Business/Farm Info - Responsive */}
                  <div className="text-xs sm:text-sm text-gray-600 mb-2">
                    {product.business_name && (
                      <div className="font-medium line-clamp-1">{product.business_name}</div>
                    )}
                    {product.farm_name && (
                      <div className="line-clamp-1">{product.farm_name}</div>
                    )}
                    {product.agent_username && (
                      <div className="text-blue-600 line-clamp-1">Agent: @{product.agent_username}</div>
                    )}
                  </div>

                  {/* Location - Responsive */}
                  <div className="text-xs sm:text-sm text-gray-500 mb-2 line-clamp-1">
                    📍 {product.location}
                  </div>

                  {/* Rating Display - New */}
                  <div className="flex items-center mb-3">
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <span
                          key={i}
                          className={`text-sm ${
                            i < Math.floor(product.average_rating || 5)
                              ? 'text-yellow-400'
                              : 'text-gray-300'
                          }`}
                        >
                          ⭐
                        </span>
                      ))}
                    </div>
                    <span className="text-xs text-gray-600 ml-2">
                      {product.average_rating ? product.average_rating.toFixed(1) : '5.0'}
                    </span>
                    {product.total_ratings > 0 && (
                      <span className="text-xs text-gray-500 ml-1">
                        ({product.total_ratings} reviews)
                      </span>
                    )}
                  </div>

                  {/* Pre-order specific info - Responsive */}
                  {product.type === 'preorder' && (
                    <div className="mb-3 p-2 bg-orange-50 rounded-lg border border-orange-200">
                      <div className="text-xs text-orange-700">
                        <div>Partial payment: {Math.round((product.partial_payment_percentage || 0.3) * 100)}%</div>
                        <div>Delivery: {new Date(product.delivery_date).toLocaleDateString()}</div>
                      </div>
                    </div>
                  )}

                  {/* Seller Info - Responsive */}
                  <div className="text-xs text-gray-500 mb-3 line-clamp-1">
                    Seller: {product.seller_username || `agent_${Math.random().toString().substr(2, 6)}`}
                  </div>

                  {/* Enhanced Add to Cart - Buyer Interface */}
                  <div className="mt-auto pt-3 sm:pt-4 space-y-2 sm:space-y-3">
                    {/* Product Unit Display (Read-only for buyers) */}
                    <div className="mb-2 p-2 bg-emerald-50 rounded-lg border border-emerald-200">
                      <div className="text-xs sm:text-sm font-medium text-emerald-700">
                        Unit: {product.unit || product.unit_of_measure || 'kg'}
                        {(product.unit_specification) && 
                          <span className="ml-2 text-emerald-600">({product.unit_specification})</span>
                        }
                      </div>
                      <div className="text-xs text-emerald-600">
                        Select how many {product.unit || product.unit_of_measure || 'units'} you want to buy
                      </div>
                    </div>

                    {/* Quantity and Drop-off Location Selection */}
                    <div className="grid grid-cols-1 gap-2 sm:gap-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Quantity (Number of {product.unit || product.unit_of_measure || 'units'})
                        </label>
                        <input
                          type="number"
                          min="1"
                          max={product.quantity || product.available_stock || product.total_stock || 100}
                          defaultValue="1"
                          className="w-full px-1.5 sm:px-2 py-1 text-xs sm:text-sm border border-gray-300 rounded focus:ring-1 focus:ring-emerald-500"
                          id={`quantity-${index}`}
                          placeholder="1, 2, 3..."
                        />
                        <div className="text-xs text-gray-500 mt-1">
                          Max available: {product.quantity || product.available_stock || product.total_stock || 100}
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Drop-off Location</label>
                        <select
                          className="w-full px-1.5 sm:px-2 py-1 text-xs sm:text-sm border border-gray-300 rounded focus:ring-1 focus:ring-emerald-500"
                          id={`dropoff-${index}`}
                        >
                          <option value="">Select drop-off location</option>
                          {dropOffLocations.map(location => (
                            <option key={location.id} value={location.id}>
                              {location.name} - {location.city}, {location.state}
                            </option>
                          ))}
                        </select>
                        <div className="text-xs text-gray-500 mt-1">
                          📍 Pick up your order at a convenient location
                        </div>
                      </div>
                    </div>

                    {/* Enhanced Add to Cart Button */}
                    <button
                      onClick={() => {
                        const quantityEl = document.getElementById(`quantity-${index}`);
                        const dropoffEl = document.getElementById(`dropoff-${index}`);
                        
                        const quantity = parseFloat(quantityEl?.value) || 1;
                        const unit = product.unit || product.unit_of_measure || 'kg';
                        const specification = product.unit_specification || 'standard';
                        const dropoffLocationId = dropoffEl?.value;
                        
                        if (!dropoffLocationId) {
                          alert('Please select a drop-off location');
                          return;
                        }
                        
                        const dropoffLocation = dropOffLocations.find(loc => loc.id.toString() === dropoffLocationId);
                        const cartItem = {
                          ...product,
                          cartQuantity: quantity,
                          cartUnit: unit,
                          cartSpecification: specification,
                          dropoffLocation: dropoffLocation
                        };
                        
                        addEnhancedToCart(cartItem, quantity, unit, specification, 'dropoff');
                      }}
                      className={`w-full py-2 px-3 sm:px-4 rounded-lg font-medium transition-colors text-xs sm:text-sm ${
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

                {/* Account Type Selection Step */}
                {registrationStep === 'role_path' && (
                  <>
                    <div className="flex justify-between items-center mb-6">
                      <h2 className="text-2xl font-bold text-center w-full text-emerald-600">Choose Account Type</h2>
                    </div>

                    <div className="bg-gradient-to-br from-emerald-50 to-blue-50 p-6 rounded-2xl">
                      <p className="text-gray-600 mb-6 text-center">
                        Select the account type that best describes you:
                      </p>

                      <div className="grid grid-cols-1 gap-4">
                        {/* Personal Account */}
                        <div className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-blue-300 transition-colors cursor-pointer">
                          <div className="flex items-center">
                            <div className="text-3xl mr-4">👤</div>
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-gray-800">Personal</h3>
                              <p className="text-sm text-gray-600">Individual buyer - shop for personal needs</p>
                            </div>
                            <button
                              onClick={() => {
                                setAuthForm({...authForm, role: 'personal'});
                                handleCompleteRegistration();
                              }}
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                            >
                              Select
                            </button>
                          </div>
                        </div>

                        {/* Farmer Account */}
                        <div className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-green-300 transition-colors cursor-pointer">
                          <div className="flex items-center">
                            <div className="text-3xl mr-4">🌾</div>
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-gray-800">Farmer</h3>
                              <p className="text-sm text-gray-600">Agricultural producer - sell your farm produce</p>
                            </div>
                            <button
                              onClick={() => {
                                setAuthForm({...authForm, role: 'farmer'});
                                setRegistrationStep('business_profile');
                              }}
                              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                            >
                              Select
                            </button>
                          </div>
                        </div>

                        {/* Agent Account */}
                        <div className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-purple-300 transition-colors cursor-pointer">
                          <div className="flex items-center">
                            <div className="text-3xl mr-4">🤝</div>
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-gray-800">Agent</h3>
                              <p className="text-sm text-gray-600">Market aggregator - connect buyers and sellers</p>
                            </div>
                            <button
                              onClick={() => {
                                setAuthForm({...authForm, role: 'agent'});
                                setRegistrationStep('business_profile');
                              }}
                              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                            >
                              Select
                            </button>
                          </div>
                        </div>

                        {/* Business Account */}
                        <div className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-emerald-300 transition-colors cursor-pointer">
                          <div className="flex items-center">
                            <div className="text-3xl mr-4">🏢</div>
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-gray-800">Business</h3>
                              <p className="text-sm text-gray-600">Enterprise buyer/seller - restaurants, suppliers, etc.</p>
                            </div>
                            <button
                              onClick={() => {
                                setAuthForm({...authForm, role: 'business'});
                                setRegistrationStep('business_profile');
                              }}
                              className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                            >
                              Select
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
                        <option value="tins">Tins</option>
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
                        <option value="tins">Tins</option>
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

      {/* Add Drop-off Location Modal */}
      {showAddDropOff && user && user.role === 'agent' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-pink-50">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">📍 Add Drop-off Location</h2>
                  <p className="text-gray-600 mt-1">Create a convenient pickup location for buyers</p>
                </div>
                <button
                  onClick={() => setShowAddDropOff(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
                >
                  ×
                </button>
              </div>
            </div>

            {/* Form Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <form 
                onSubmit={async (e) => {
                  e.preventDefault();
                  const formData = new FormData(e.target);
                  
                  const locationData = {
                    name: formData.get('name'),
                    address: formData.get('address'),
                    city: formData.get('city'),
                    state: formData.get('state'),
                    country: formData.get('country') || 'Nigeria',
                    contact_person: formData.get('contact_person'),
                    contact_phone: formData.get('contact_phone'),
                    operating_hours: formData.get('operating_hours'),
                    description: formData.get('description')
                  };

                  try {
                    const token = localStorage.getItem('token');
                    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/dropoff-locations`, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                      },
                      body: JSON.stringify(locationData)
                    });

                    if (response.ok) {
                      const result = await response.json();
                      alert(`Drop-off location "${result.location.name}" created successfully!`);
                      
                      // Add to local state
                      setDropOffLocations(prev => [...prev, {
                        id: result.location.id,
                        name: result.location.name,
                        address: result.location.address,
                        city: result.location.city,
                        state: result.location.state
                      }]);
                      
                      setShowAddDropOff(false);
                      e.target.reset();
                    } else {
                      const error = await response.json();
                      alert(`Error: ${error.detail}`);
                    }
                  } catch (error) {
                    console.error('Error creating drop-off location:', error);
                    alert('Error creating drop-off location. Please try again.');
                  }
                }}
                className="space-y-6"
              >
                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Location Name *
                    </label>
                    <input
                      type="text"
                      name="name"
                      required
                      placeholder="e.g., Mile 12 Market, Kano Central Market"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      State *
                    </label>
                    <select
                      name="state"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    >
                      <option value="">Select State</option>
                      <option value="Lagos">Lagos</option>
                      <option value="Kano">Kano</option>
                      <option value="Anambra">Anambra</option>
                      <option value="Rivers">Rivers</option>
                      <option value="Kaduna">Kaduna</option>
                      <option value="Oyo">Oyo</option>
                      <option value="Delta">Delta</option>
                      <option value="Imo">Imo</option>
                      <option value="Ogun">Ogun</option>
                      <option value="FCT">FCT Abuja</option>
                      <option value="Cross River">Cross River</option>
                      <option value="Plateau">Plateau</option>
                      <option value="Abia">Abia</option>
                      <option value="Enugu">Enugu</option>
                      <option value="Benue">Benue</option>
                      <option value="Edo">Edo</option>
                      <option value="Kwara">Kwara</option>
                      <option value="Akwa Ibom">Akwa Ibom</option>
                      <option value="Osun">Osun</option>
                      <option value="Kogi">Kogi</option>
                      <option value="Zamfara">Zamfara</option>
                      <option value="Sokoto">Sokoto</option>
                      <option value="Kebbi">Kebbi</option>
                      <option value="Niger">Niger</option>
                      <option value="Jigawa">Jigawa</option>
                      <option value="Yobe">Yobe</option>
                      <option value="Borno">Borno</option>
                      <option value="Gombe">Gombe</option>
                      <option value="Bauchi">Bauchi</option>
                      <option value="Adamawa">Adamawa</option>
                      <option value="Taraba">Taraba</option>
                      <option value="Nasarawa">Nasarawa</option>
                      <option value="Ebonyi">Ebonyi</option>
                      <option value="Ekiti">Ekiti</option>
                      <option value="Ondo">Ondo</option>
                      <option value="Bayelsa">Bayelsa</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      City *
                    </label>
                    <input
                      type="text"
                      name="city"
                      required
                      placeholder="e.g., Lagos, Kano, Onitsha"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Country
                    </label>
                    <input
                      type="text"
                      name="country"
                      defaultValue="Nigeria"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-gray-50"
                      readOnly
                    />
                  </div>
                </div>

                {/* Address */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Address *
                  </label>
                  <textarea
                    name="address"
                    required
                    rows="3"
                    placeholder="e.g., Shop 45, Mile 12 International Market, Mile 12, Lagos State"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  ></textarea>
                </div>

                {/* Contact Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Contact Person
                    </label>
                    <input
                      type="text"
                      name="contact_person"
                      placeholder="e.g., Mr. John Doe"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Contact Phone
                    </label>
                    <input
                      type="tel"
                      name="contact_phone"
                      placeholder="e.g., +234 801 234 5678"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>
                </div>

                {/* Operating Hours */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Operating Hours
                  </label>
                  <input
                    type="text"
                    name="operating_hours"
                    placeholder="e.g., 6:00 AM - 6:00 PM (Mon-Sat)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Additional Notes
                  </label>
                  <textarea
                    name="description"
                    rows="2"
                    placeholder="e.g., Near Gate 3, look for the blue sign"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  ></textarea>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowAddDropOff(false)}
                    className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium"
                  >
                    📍 Add Location
                  </button>
                </div>
              </form>
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
                            <span className="text-sm text-gray-600">Payment Required:</span>
                            <div className="font-semibold text-blue-600">
                              {selectedProduct.partial_payment_percentage ? 
                                `${Math.round(selectedProduct.partial_payment_percentage * 100)}%` : 
                                '100%'
                              }
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
                    
                    {/* Product Unit Display (Read-only for buyers) */}
                    <div className="mb-4 p-3 bg-emerald-100 rounded-lg border border-emerald-300">
                      <div className="text-sm font-medium text-emerald-700">
                        Unit: {selectedProduct.unit || selectedProduct.unit_of_measure || 'kg'}
                        {(selectedProduct.unit_specification) && 
                          <span className="ml-2 text-emerald-600">({selectedProduct.unit_specification})</span>
                        }
                      </div>
                      <div className="text-xs text-emerald-600 mt-1">
                        Select how many {selectedProduct.unit || selectedProduct.unit_of_measure || 'units'} you want to buy
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      {/* Quantity and Drop-off Location Selection */}
                      <div className="grid grid-cols-1 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Quantity (Number of {selectedProduct.unit || selectedProduct.unit_of_measure || 'units'})
                          </label>
                          <input
                            type="number"
                            min="1"
                            max={selectedProduct.quantity || selectedProduct.available_stock || selectedProduct.total_stock || 100}
                            defaultValue="1"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                            id={`detail-quantity`}
                            placeholder="1, 2, 3..."
                          />
                          <div className="text-xs text-gray-500 mt-1">
                            Max available: {selectedProduct.quantity || selectedProduct.available_stock || selectedProduct.total_stock || 100}
                          </div>
                        </div>

                        {/* Enhanced Delivery Options Selection */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Delivery Options</label>
                          
                          {(() => {
                            const productId = selectedProduct.id || selectedProduct._id;
                            const deliveryOptions = productDeliveryOptions[productId];
                            
                            if (!deliveryOptions) {
                              return (
                                <div className="p-3 bg-gray-100 rounded-lg">
                                  <div className="text-gray-600">Loading delivery options...</div>
                                </div>
                              );
                            }
                            
                            const supportsBoth = deliveryOptions.supports_dropoff_delivery && deliveryOptions.supports_shipping_delivery;
                            const supportsDropoff = deliveryOptions.supports_dropoff_delivery;
                            const supportsShipping = deliveryOptions.supports_shipping_delivery;
                            
                            return (
                              <div className="space-y-3">
                                {/* Delivery Method Selection (only show if both are supported) */}
                                {supportsBoth && (
                                  <div className="grid grid-cols-2 gap-2">
                                    <button
                                      type="button"
                                      onClick={() => setSelectedDeliveryMethod('dropoff')}
                                      className={`p-3 rounded-lg border-2 transition-colors ${
                                        selectedDeliveryMethod === 'dropoff'
                                          ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                                          : 'border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100'
                                      }`}
                                    >
                                      <div className="text-sm font-medium">📍 Drop-off Location</div>
                                      <div className="text-xs mt-1">
                                        {deliveryOptions.delivery_costs.dropoff.is_free 
                                          ? 'Free' 
                                          : `₦${deliveryOptions.delivery_costs.dropoff.cost}`
                                        }
                                      </div>
                                    </button>
                                    <button
                                      type="button"
                                      onClick={() => setSelectedDeliveryMethod('shipping')}
                                      className={`p-3 rounded-lg border-2 transition-colors ${
                                        selectedDeliveryMethod === 'shipping'
                                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                                          : 'border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100'
                                      }`}
                                    >
                                      <div className="text-sm font-medium">🚚 Home Delivery</div>
                                      <div className="text-xs mt-1">
                                        {deliveryOptions.delivery_costs.shipping.is_free 
                                          ? 'Free' 
                                          : `₦${deliveryOptions.delivery_costs.shipping.cost}`
                                        }
                                      </div>
                                    </button>
                                  </div>
                                )}
                                
                                {/* Drop-off Location Selection */}
                                {(selectedDeliveryMethod === 'dropoff' || (supportsDropoff && !supportsBoth)) && (
                                  <div>
                                    <select
                                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                                      id="detail-dropoff"
                                    >
                                      <option value="">Select drop-off location</option>
                                      {dropOffLocations.map(location => (
                                        <option key={location.id} value={location.id}>
                                          {location.name} - {location.city}, {location.state}
                                        </option>
                                      ))}
                                    </select>
                                    <div className="text-xs text-gray-500 mt-1">
                                      📍 Pick up your order at a convenient market or location
                                      {deliveryOptions.delivery_costs.dropoff.cost > 0 && (
                                        <span className="text-emerald-600 font-medium ml-2">
                                          (₦{deliveryOptions.delivery_costs.dropoff.cost} fee)
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                )}
                                
                                {/* Shipping Address Input */}
                                {(selectedDeliveryMethod === 'shipping' || (supportsShipping && !supportsBoth)) && (
                                  <div>
                                    <textarea
                                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                      id="detail-shipping-address"
                                      placeholder="Enter your full delivery address..."
                                      rows="3"
                                    ></textarea>
                                    <div className="text-xs text-gray-500 mt-1">
                                      🚚 We'll deliver directly to your address
                                      {deliveryOptions.delivery_costs.shipping.cost > 0 && (
                                        <span className="text-blue-600 font-medium ml-2">
                                          (₦{deliveryOptions.delivery_costs.shipping.cost} fee)
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                )}
                                
                                {/* Delivery Notes */}
                                {deliveryOptions.delivery_notes && (
                                  <div className="p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                                    <div className="text-xs font-medium text-yellow-800">Delivery Notes:</div>
                                    <div className="text-xs text-yellow-700 mt-1">{deliveryOptions.delivery_notes}</div>
                                  </div>
                                )}
                              </div>
                            );
                          })()}
                        </div>
                      </div>

                      {/* Enhanced Add to Cart Button */}
                      <button
                        onClick={() => {
                          const quantity = parseFloat(document.getElementById('detail-quantity')?.value) || 1;
                          const unit = selectedProduct.unit || selectedProduct.unit_of_measure || 'kg';
                          const specification = selectedProduct.unit_specification || 'standard';
                          
                          const productId = selectedProduct.id || selectedProduct._id;
                          const deliveryOptions = productDeliveryOptions[productId];
                          
                          if (!deliveryOptions) {
                            alert('Unable to determine delivery options. Please try again.');
                            return;
                          }
                          
                          // Determine actual delivery method based on what's supported
                          let deliveryMethod = selectedDeliveryMethod;
                          if (!deliveryOptions.supports_dropoff_delivery && !deliveryOptions.supports_shipping_delivery) {
                            alert('This product has no available delivery methods. Please contact the supplier.');
                            return;
                          }
                          
                          // Default to available method if current selection isn't supported
                          if (deliveryMethod === 'dropoff' && !deliveryOptions.supports_dropoff_delivery) {
                            deliveryMethod = 'shipping';
                          } else if (deliveryMethod === 'shipping' && !deliveryOptions.supports_shipping_delivery) {
                            deliveryMethod = 'dropoff';
                          }
                          
                          let deliveryDetails = null;
                          
                          // Validate and get delivery details based on method
                          if (deliveryMethod === 'dropoff') {
                            const dropoffLocationId = document.getElementById('detail-dropoff')?.value;
                            if (!dropoffLocationId) {
                              alert('Please select a drop-off location');
                              return;
                            }
                            
                            const dropoffLocation = dropOffLocations.find(loc => loc.id.toString() === dropoffLocationId);
                            if (!dropoffLocation) {
                              alert('Invalid drop-off location selected');
                              return;
                            }
                            
                            deliveryDetails = {
                              type: 'dropoff',
                              dropoffLocation: dropoffLocation,
                              cost: deliveryOptions.delivery_costs.dropoff.cost
                            };
                          } else if (deliveryMethod === 'shipping') {
                            const shippingAddress = document.getElementById('detail-shipping-address')?.value?.trim();
                            if (!shippingAddress) {
                              alert('Please enter your delivery address');
                              return;
                            }
                            
                            deliveryDetails = {
                              type: 'shipping',
                              shippingAddress: shippingAddress,
                              cost: deliveryOptions.delivery_costs.shipping.cost
                            };
                          }
                          
                          const cartItem = {
                            ...selectedProduct,
                            cartQuantity: quantity,
                            cartUnit: unit,
                            cartSpecification: specification,
                            deliveryMethod: deliveryMethod,
                            deliveryDetails: deliveryDetails
                          };
                          
                          // Use the appropriate parameters for addEnhancedToCart based on delivery method
                          if (deliveryMethod === 'dropoff') {
                            addEnhancedToCart(cartItem, quantity, unit, specification, 'dropoff', deliveryDetails.dropoffLocation);
                          } else {
                            addEnhancedToCart(cartItem, quantity, unit, specification, 'platform', null, deliveryDetails.shippingAddress);
                          }
                          
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

                      {/* Rate Product Button */}
                      {user && (
                        <button
                          onClick={() => {
                            const productId = selectedProduct.id || selectedProduct._id;
                            openRatingModal('product_rating', productId, null, null);
                          }}
                          className="w-full mt-3 py-2 px-6 border-2 border-yellow-400 text-yellow-600 rounded-lg font-medium text-sm hover:bg-yellow-50 transition-colors"
                        >
                          ⭐ Rate this Product
                        </button>
                      )}
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
      
      {/* Rating Modal */}
      {showRatingModal && ratingModalData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Rate & Review</h2>
              <button
                onClick={closeRatingModal}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={async (e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              const ratingValue = parseInt(formData.get('rating'));
              const comment = formData.get('comment');
              
              try {
                await submitRating({
                  ...ratingModalData,
                  rating_value: ratingValue,
                  comment: comment || null
                });
                
                alert('Rating submitted successfully!');
                closeRatingModal();
                
                // Refresh products to show updated ratings
                fetchProducts();
              } catch (error) {
                alert('Failed to submit rating: ' + error.message);
              }
            }}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Rating
                </label>
                <div className="flex space-x-1">
                  {[1, 2, 3, 4, 5].map(star => (
                    <label key={star} className="cursor-pointer">
                      <input
                        type="radio"
                        name="rating"
                        value={star}
                        required
                        className="hidden"
                      />
                      <span className="text-2xl text-gray-300 hover:text-yellow-400 transition-colors">
                        ⭐
                      </span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Review (Optional)
                </label>
                <textarea
                  name="comment"
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  placeholder="Share your experience..."
                ></textarea>
              </div>
              
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={closeRatingModal}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
                >
                  Submit Rating
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Driver Management Modal (for logistics businesses) */}
      {showDriverManagement && user && user.role === 'logistics' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold">Driver Management</h2>
                <button
                  onClick={() => setShowDriverManagement(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              {/* Purchase New Slots Section */}
              <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg">
                <h3 className="text-lg font-semibold mb-4">Purchase Driver Slots</h3>
                <p className="text-gray-600 mb-4">
                  Each driver slot costs ₦500/month with a 14-day free trial. Purchase slots to add drivers to your fleet.
                </p>
                <div className="flex space-x-4">
                  <input
                    type="number"
                    min="1"
                    max="10"
                    placeholder="Number of slots"
                    className="px-3 py-2 border border-gray-300 rounded-lg"
                    id="slots-count"
                  />
                  <button
                    onClick={async () => {
                      const slotsCount = parseInt(document.getElementById('slots-count').value);
                      if (slotsCount >= 1 && slotsCount <= 10) {
                        try {
                          const result = await purchaseDriverSlots(slotsCount);
                          alert(`Successfully purchased ${result.slots_created} driver slots!\nTotal cost: ${result.total_monthly_cost}/month\n14-day free trial included`);
                        } catch (error) {
                          alert('Error: ' + error.message);
                        }
                      } else {
                        alert('Please enter a valid number of slots (1-10)');
                      }
                    }}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Purchase Slots
                  </button>
                </div>
              </div>
              
              {/* Current Driver Slots */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Your Driver Slots</h3>
                  <button
                    onClick={fetchDriverSlots}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Refresh
                  </button>
                </div>
                
                {driverSlots.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>No driver slots found. Purchase slots to get started!</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {driverSlots.map(slot => (
                      <div key={slot.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium">Slot #{slot.slot_number}</h4>
                          <span className={`text-xs px-2 py-1 rounded ${
                            slot.subscription_status === 'trial' 
                              ? 'bg-green-100 text-green-800' 
                              : slot.subscription_status === 'active'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {slot.subscription_status}
                          </span>
                        </div>
                        
                        {slot.driver_id ? (
                          <div className="space-y-2">
                            <div className="text-sm">
                              <strong>Driver:</strong> {slot.driver_name}
                            </div>
                            <div className="text-sm">
                              <strong>Vehicle:</strong> {slot.vehicle_make_model} ({slot.plate_number})
                            </div>
                            <div className="text-sm">
                              <strong>Rating:</strong> ⭐ {slot.average_rating}/5.0
                            </div>
                            <div className="text-sm">
                              <strong>Trips:</strong> {slot.total_trips}
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-3">
                            <p className="text-gray-500 text-sm">No driver assigned</p>
                            <button
                              onClick={() => {
                                // Simple driver assignment form
                                const driverName = prompt('Driver Name:');
                                const plateNumber = prompt('Plate Number:');
                                const vehicleMake = prompt('Vehicle Make/Model:');
                                const vehicleColor = prompt('Vehicle Color:');
                                const dob = prompt('Date of Birth (YYYY-MM-DD):');
                                const address = prompt('Address:');
                                
                                if (driverName && plateNumber && vehicleMake && vehicleColor && dob && address) {
                                  assignDriverToSlot(slot.id, {
                                    driver_name: driverName,
                                    vehicle_type: 'motorcycle', // Default, could be improved
                                    plate_number: plateNumber,
                                    vehicle_make_model: vehicleMake,
                                    vehicle_color: vehicleColor,
                                    date_of_birth: dob,
                                    address: address
                                  }).then(result => {
                                    alert(`Driver assigned successfully!\nRegistration link: ${result.registration_link}`);
                                  }).catch(error => {
                                    alert('Error: ' + error.message);
                                  });
                                }
                              }}
                              className="w-full px-3 py-2 bg-emerald-600 text-white rounded text-sm hover:bg-emerald-700"
                            >
                              Assign Driver
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Find Drivers Modal (Uber-like interface) */}
      {showFindDrivers && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold">🚗 Find Drivers</h2>
                <button
                  onClick={() => setShowFindDrivers(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              {/* Search Filters */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <input
                  type="text"
                  placeholder="Location..."
                  value={driverSearchFilters.location}
                  onChange={(e) => setDriverSearchFilters(prev => ({...prev, location: e.target.value}))}
                  className="px-3 py-2 border border-gray-300 rounded-lg"
                />
                <select
                  value={driverSearchFilters.vehicle_type}
                  onChange={(e) => setDriverSearchFilters(prev => ({...prev, vehicle_type: e.target.value}))}
                  className="px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">All Vehicle Types</option>
                  <option value="motorcycle">Motorcycle</option>
                  <option value="car">Car</option>
                  <option value="van">Van</option>
                  <option value="truck">Truck</option>
                </select>
                <select
                  value={driverSearchFilters.min_rating || ''}
                  onChange={(e) => setDriverSearchFilters(prev => ({...prev, min_rating: e.target.value ? parseFloat(e.target.value) : null}))}
                  className="px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Any Rating</option>
                  <option value="4.5">4.5+ Stars</option>
                  <option value="4.0">4.0+ Stars</option>
                  <option value="3.5">3.5+ Stars</option>
                </select>
              </div>
              
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Available Drivers</h3>
                <button
                  onClick={() => fetchAvailableDrivers(driverSearchFilters)}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
                >
                  Search Drivers
                </button>
              </div>
              
              {availableDrivers.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>Click "Search Drivers" to find available drivers</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {availableDrivers.map(driver => (
                    <div key={driver.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                          <span className="text-emerald-600 font-semibold">
                            {driver.name?.charAt(0) || 'D'}
                          </span>
                        </div>
                        <div>
                          <h4 className="font-semibold">{driver.name}</h4>
                          <div className="flex items-center">
                            <span className="text-yellow-400">⭐</span>
                            <span className="ml-1 text-sm text-gray-600">
                              {driver.average_rating.toFixed(1)} ({driver.total_trips} trips)
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="text-sm">
                          <strong>Vehicle:</strong> {driver.vehicle_info?.make_model || 'N/A'}
                        </div>
                        <div className="text-sm">
                          <strong>Type:</strong> {driver.vehicle_info?.type || 'N/A'}
                        </div>
                        <div className="text-sm">
                          <strong>Plate:</strong> {driver.vehicle_info?.plate_number || 'N/A'}
                        </div>
                        {driver.logistics_business && (
                          <div className="text-sm">
                            <strong>Company:</strong> @{driver.logistics_business}
                          </div>
                        )}
                      </div>
                      
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            // Could integrate with order creation or messaging
                            alert(`Driver: ${driver.name}\nContact through platform messaging`);
                          }}
                          className="flex-1 px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                        >
                          View Profile
                        </button>
                        <button
                          onClick={() => {
                            alert(`Request sent to ${driver.name}!`);
                          }}
                          className="flex-1 px-3 py-2 bg-emerald-600 text-white rounded text-sm hover:bg-emerald-700"
                        >
                          Request Driver
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Digital Wallet Dashboard */}
      {showWallet && user && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold">💰 My Wallet</h2>
                <button
                  onClick={() => setShowWallet(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              {/* Wallet Balance Card */}
              <div className="mb-8 p-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg">
                <h3 className="text-lg font-semibold mb-2">Wallet Balance</h3>
                <div className="text-3xl font-bold mb-4">
                  ₦{walletSummary ? walletSummary.balance.toLocaleString() : '0'}
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-purple-200">Total Funded</div>
                    <div className="font-medium">₦{walletSummary ? walletSummary.total_funded.toLocaleString() : '0'}</div>
                  </div>
                  <div>
                    <div className="text-purple-200">Total Spent</div>
                    <div className="font-medium">₦{walletSummary ? walletSummary.total_spent.toLocaleString() : '0'}</div>
                  </div>
                  <div>
                    <div className="text-purple-200">Withdrawn</div>
                    <div className="font-medium">₦{walletSummary ? walletSummary.total_withdrawn.toLocaleString() : '0'}</div>
                  </div>
                </div>
              </div>
              
              {/* Quick Actions */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <button
                  onClick={() => setShowFundWallet(true)}
                  className="p-4 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                >
                  <div className="text-2xl mb-2">💳</div>
                  <div className="font-medium">Fund Wallet</div>
                </button>
                <button
                  onClick={() => setShowWithdrawFunds(true)}
                  className="p-4 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                >
                  <div className="text-2xl mb-2">🏦</div>
                  <div className="font-medium">Withdraw</div>
                </button>
                <button
                  onClick={() => setShowCreateGiftCard(true)}
                  className="p-4 bg-pink-100 text-pink-700 rounded-lg hover:bg-pink-200 transition-colors"
                >
                  <div className="text-2xl mb-2">🎁</div>
                  <div className="font-medium">Buy Gift Card</div>
                </button>
                <button
                  onClick={() => setShowAddBankAccount(true)}
                  className="p-4 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <div className="text-2xl mb-2">🏧</div>
                  <div className="font-medium">Add Bank</div>
                </button>
              </div>
              
              {/* Transaction History */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
                {walletTransactions.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>No transactions yet. Start by funding your wallet!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {walletTransactions.slice(0, 10).map(transaction => (
                      <div key={transaction.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`text-2xl ${
                            transaction.transaction_type.includes('funding') || transaction.transaction_type.includes('redemption') 
                              ? 'text-green-600' 
                              : 'text-red-600'
                          }`}>
                            {transaction.transaction_type.includes('funding') ? '⬇️' : 
                             transaction.transaction_type.includes('withdrawal') ? '⬆️' :
                             transaction.transaction_type.includes('gift_card') ? '🎁' : '💰'}
                          </div>
                          <div>
                            <div className="font-medium">{transaction.description}</div>
                            <div className="text-sm text-gray-500">
                              {new Date(transaction.created_at).toLocaleDateString()} • {transaction.reference}
                            </div>
                          </div>
                        </div>
                        <div className={`text-right ${
                          transaction.transaction_type.includes('funding') || transaction.transaction_type.includes('redemption') 
                            ? 'text-green-600' 
                            : 'text-red-600'
                        }`}>
                          <div className="font-semibold">
                            {transaction.transaction_type.includes('funding') || transaction.transaction_type.includes('redemption') ? '+' : '-'}
                            ₦{transaction.amount.toLocaleString()}
                          </div>
                          <div className="text-xs text-gray-500">
                            Status: {transaction.status}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Fund Wallet Modal */}
      {showFundWallet && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-60 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">💳 Fund Wallet</h3>
              <button
                onClick={() => setShowFundWallet(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={async (e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              const amount = formData.get('amount');
              const fundingMethod = formData.get('funding_method');
              const description = formData.get('description');
              
              try {
                await fundWallet(amount, fundingMethod, description);
                alert(`Successfully funded wallet with ₦${parseFloat(amount).toLocaleString()}`);
                setShowFundWallet(false);
              } catch (error) {
                alert('Failed to fund wallet: ' + error.message);
              }
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Amount (₦)
                  </label>
                  <input
                    type="number"
                    name="amount"
                    min="100"
                    max="500000"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="Enter amount to fund"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Funding Method
                  </label>
                  <select
                    name="funding_method"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">Select funding method</option>
                    <option value="bank_transfer">Bank Transfer</option>
                    <option value="debit_card">Debit Card</option>
                    <option value="ussd">USSD</option>
                    <option value="bank_deposit">Bank Deposit</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description (Optional)
                  </label>
                  <input
                    type="text"
                    name="description"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="Wallet funding"
                  />
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowFundWallet(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Fund Wallet
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Gift Cards Modal */}
      {showGiftCards && user && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold">🎁 Gift Cards</h2>
                <button
                  onClick={() => setShowGiftCards(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              {/* Quick Actions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                <button
                  onClick={() => setShowCreateGiftCard(true)}
                  className="p-6 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-lg hover:from-pink-600 hover:to-purple-700 transition-colors"
                >
                  <div className="text-3xl mb-2">🎁</div>
                  <div className="text-lg font-semibold">Create Gift Card</div>
                  <div className="text-sm text-pink-100">Purchase gift cards for others</div>
                </button>
                <button
                  onClick={() => setShowRedeemGiftCard(true)}
                  className="p-6 bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-lg hover:from-green-600 hover:to-blue-700 transition-colors"
                >
                  <div className="text-3xl mb-2">💰</div>
                  <div className="text-lg font-semibold">Redeem Gift Card</div>
                  <div className="text-sm text-green-100">Add gift card value to wallet</div>
                </button>
              </div>
              
              {/* User's Gift Cards */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">My Gift Cards</h3>
                  <button
                    onClick={fetchUserGiftCards}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Refresh
                  </button>
                </div>
                
                {userGiftCards.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>No gift cards purchased yet. Create your first gift card!</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {userGiftCards.map(giftCard => (
                      <div key={giftCard.id} className="border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-pink-50 to-purple-50">
                        <div className="flex justify-between items-start mb-3">
                          <div className="text-2xl">🎁</div>
                          <span className={`text-xs px-2 py-1 rounded ${
                            giftCard.status === 'active' 
                              ? 'bg-green-100 text-green-800' 
                              : giftCard.status === 'redeemed'
                              ? 'bg-gray-100 text-gray-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {giftCard.status}
                          </span>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="font-mono text-sm font-semibold text-purple-600">
                            {giftCard.card_code}
                          </div>
                          <div className="text-lg font-bold">
                            ₦{giftCard.amount.toLocaleString()}
                          </div>
                          <div className="text-sm text-gray-600">
                            Balance: ₦{giftCard.balance.toLocaleString()}
                          </div>
                          {giftCard.recipient_name && (
                            <div className="text-sm text-gray-600">
                              For: {giftCard.recipient_name}
                            </div>
                          )}
                          <div className="text-xs text-gray-500">
                            Expires: {new Date(giftCard.expiry_date).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Gift Card Modal */}
      {showCreateGiftCard && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-60 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">🎁 Create Gift Card</h3>
              <button
                onClick={() => setShowCreateGiftCard(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={async (e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              const amount = formData.get('amount');
              const recipientEmail = formData.get('recipient_email');
              const recipientName = formData.get('recipient_name');
              const message = formData.get('message');
              
              try {
                const result = await createGiftCard(amount, recipientEmail, recipientName, message);
                alert(`Gift card created successfully!\nCard Code: ${result.gift_card.card_code}\nAmount: ₦${parseFloat(amount).toLocaleString()}`);
                setShowCreateGiftCard(false);
              } catch (error) {
                alert('Failed to create gift card: ' + error.message);
              }
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Gift Card Amount (₦)
                  </label>
                  <input
                    type="number"
                    name="amount"
                    min="100"
                    max="100000"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
                    placeholder="Enter gift card value"
                  />
                  <div className="text-xs text-gray-500 mt-1">Min: ₦100, Max: ₦100,000</div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Recipient Name (Optional)
                  </label>
                  <input
                    type="text"
                    name="recipient_name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
                    placeholder="Who is this gift card for?"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Recipient Email (Optional)
                  </label>
                  <input
                    type="email"
                    name="recipient_email"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
                    placeholder="Recipient's email address"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Gift Message (Optional)
                  </label>
                  <textarea
                    name="message"
                    rows="3"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
                    placeholder="Add a personal message..."
                  ></textarea>
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateGiftCard(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700"
                >
                  Create Gift Card
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Redeem Gift Card Modal */}
      {showRedeemGiftCard && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-60 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">💰 Redeem Gift Card</h3>
              <button
                onClick={() => {
                  setShowRedeemGiftCard(false);
                  setGiftCardDetails(null);
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={async (e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              const cardCode = formData.get('card_code');
              const amount = formData.get('amount');
              
              try {
                const result = await redeemGiftCard(cardCode, amount);
                alert(`Gift card redeemed successfully!\nRedeemed: ₦${result.redeemed_amount.toLocaleString()}\nNew wallet balance: ₦${result.new_wallet_balance.toLocaleString()}`);
                setShowRedeemGiftCard(false);
                setGiftCardDetails(null);
              } catch (error) {
                alert('Failed to redeem gift card: ' + error.message);
              }
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Gift Card Code
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      name="card_code"
                      required
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 uppercase"
                      placeholder="GIFT-XXXXXXXX"
                      onChange={async (e) => {
                        const code = e.target.value.trim();
                        if (code.length >= 8) {
                          await fetchGiftCardDetails(code);
                        }
                      }}
                    />
                    <button
                      type="button"
                      onClick={async () => {
                        const code = document.querySelector('input[name="card_code"]').value;
                        if (code) await fetchGiftCardDetails(code);
                      }}
                      className="px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                    >
                      Check
                    </button>
                  </div>
                </div>
                
                {giftCardDetails && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="space-y-2">
                      <div className="font-semibold text-green-800">
                        Gift Card Found!
                      </div>
                      <div className="text-sm text-green-700">
                        Available Balance: ₦{giftCardDetails.balance.toLocaleString()}
                      </div>
                      <div className="text-sm text-green-600">
                        Status: {giftCardDetails.status} • 
                        Expires: {new Date(giftCardDetails.expiry_date).toLocaleDateString()}
                      </div>
                      {giftCardDetails.message && (
                        <div className="text-sm text-green-600 italic">
                          "{giftCardDetails.message}"
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Amount to Redeem (Optional)
                  </label>
                  <input
                    type="number"
                    name="amount"
                    min="1"
                    max={giftCardDetails ? giftCardDetails.balance : 100000}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    placeholder="Leave empty to redeem full amount"
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    Leave empty to redeem the full gift card balance
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowRedeemGiftCard(false);
                    setGiftCardDetails(null);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!giftCardDetails}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                >
                  Redeem Gift Card
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* KYC Completion Prompt */}
      {showKYCPrompt && kycStatus && kycStatus.requires_kyc && kycStatus.status === 'not_started' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-60 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 border-2 border-yellow-200">
            <div className="text-center">
              <div className="text-4xl mb-4">🔐</div>
              <h3 className="text-xl font-semibold mb-2 text-gray-800">Complete Your KYC</h3>
              <p className="text-gray-600 mb-4">
                Complete your KYC verification to start receiving payments on the platform.
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-yellow-800">
                  <strong>Important:</strong> KYC completion is required to receive payments from buyers. 
                  Without KYC, you can browse and purchase but cannot receive funds.
                </p>
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowKYCPrompt(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Later
                </button>
                <button
                  onClick={() => {
                    setShowKYCPrompt(false);
                    // Navigate to KYC completion - would implement KYC modal
                    alert('KYC completion form will open here. This includes:\n\n' +
                          'For Registered Businesses:\n- Business Registration Number\n- TIN Certificate\n- Certificate of Incorporation\n\n' +
                          'For Others (Farmers/Agents/Unregistered):\n- NIN or BVN\n- Headshot photo (camera)\n- National ID upload\n- Utility bill');
                  }}
                  className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
                >
                  Complete KYC
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Farmer Dashboard */}
      {showFarmerDashboard && user && user.role === 'farmer' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold">🌾 Farmer Dashboard</h2>
                <button
                  onClick={() => setShowFarmerDashboard(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>
            
            {farmerDashboardData ? (
              <div className="p-6">
                {/* Profile Summary */}
                <div className="mb-8 p-6 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">Welcome, {farmerDashboardData.farmer_profile.name}!</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-green-200">KYC Status</div>
                      <div className="font-medium capitalize">{farmerDashboardData.farmer_profile.kyc_status}</div>
                    </div>
                    <div>
                      <div className="text-green-200">Rating</div>
                      <div className="font-medium">⭐ {farmerDashboardData.farmer_profile.average_rating}/5</div>
                    </div>
                    <div>
                      <div className="text-green-200">Products</div>
                      <div className="font-medium">{farmerDashboardData.business_metrics.total_products}</div>
                    </div>
                    <div>
                      <div className="text-green-200">Revenue</div>
                      <div className="font-medium">₦{farmerDashboardData.business_metrics.total_revenue.toLocaleString()}</div>
                    </div>
                  </div>
                </div>

                {/* Business Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl text-blue-600 mb-2">📦</div>
                    <div className="text-2xl font-bold text-blue-600">{farmerDashboardData.business_metrics.active_products}</div>
                    <div className="text-sm text-blue-600">Active Products</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl text-green-600 mb-2">🌾</div>
                    <div className="text-2xl font-bold text-green-600">{farmerDashboardData.business_metrics.total_farmlands}</div>
                    <div className="text-sm text-green-600">Farmlands</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="text-2xl text-yellow-600 mb-2">📋</div>
                    <div className="text-2xl font-bold text-yellow-600">{farmerDashboardData.business_metrics.pending_orders}</div>
                    <div className="text-sm text-yellow-600">Pending Orders</div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-2xl text-purple-600 mb-2">📏</div>
                    <div className="text-2xl font-bold text-purple-600">{farmerDashboardData.business_metrics.total_hectares}</div>
                    <div className="text-sm text-purple-600">Total Hectares</div>
                  </div>
                </div>

                {/* Recent Orders */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Recent Orders</h3>
                  {farmerDashboardData.recent_orders.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <p>No recent orders. Start listing your products to get orders!</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {farmerDashboardData.recent_orders.map((order, index) => (
                        <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                          <div>
                            <div className="font-medium">{order.product}</div>
                            <div className="text-sm text-gray-500">Buyer: {order.buyer}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold">₦{order.amount.toLocaleString()}</div>
                            <div className={`text-xs px-2 py-1 rounded ${
                              order.status === 'completed' ? 'bg-green-100 text-green-800' :
                              order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {order.status}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-6">
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
                  <p>Loading dashboard data...</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Agent Dashboard */}
      {showAgentDashboard && user && user.role === 'agent' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold">🤝 Agent Dashboard</h2>
                <button
                  onClick={() => setShowAgentDashboard(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>
            
            {agentDashboardData ? (
              <div className="p-6">
                {/* Profile Summary */}
                <div className="mb-8 p-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">Welcome, {agentDashboardData.agent_profile.name}!</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-purple-200">KYC Status</div>
                      <div className="font-medium capitalize">{agentDashboardData.agent_profile.kyc_status}</div>
                    </div>
                    <div>
                      <div className="text-purple-200">Rating</div>
                      <div className="font-medium">⭐ {agentDashboardData.agent_profile.average_rating}/5</div>
                    </div>
                    <div>
                      <div className="text-purple-200">Farmers</div>
                      <div className="font-medium">{agentDashboardData.business_metrics.total_farmers}</div>
                    </div>
                    <div>
                      <div className="text-purple-200">Commission</div>
                      <div className="font-medium">₦{agentDashboardData.business_metrics.agent_commission.toLocaleString()}</div>
                    </div>
                  </div>
                </div>

                {/* Business Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl text-green-600 mb-2">👨‍🌾</div>
                    <div className="text-2xl font-bold text-green-600">{agentDashboardData.business_metrics.active_farmers}</div>
                    <div className="text-sm text-green-600">Active Farmers</div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl text-blue-600 mb-2">📦</div>
                    <div className="text-2xl font-bold text-blue-600">{agentDashboardData.business_metrics.active_products}</div>
                    <div className="text-sm text-blue-600">Active Products</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="text-2xl text-yellow-600 mb-2">💰</div>
                    <div className="text-2xl font-bold text-yellow-600">₦{agentDashboardData.business_metrics.total_revenue.toLocaleString()}</div>
                    <div className="text-sm text-yellow-600">Total Revenue</div>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <div className="text-2xl text-red-600 mb-2">📋</div>
                    <div className="text-2xl font-bold text-red-600">{agentDashboardData.business_metrics.pending_orders}</div>
                    <div className="text-sm text-red-600">Pending Orders</div>
                  </div>
                </div>

                {/* Top Farmers */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Top Performing Farmers</h3>
                  {agentDashboardData.top_farmers.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <p>No farmers in your network yet. Start adding farmers to grow your business!</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {agentDashboardData.top_farmers.map((farmer, index) => (
                        <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                          <div>
                            <div className="font-medium">{farmer.name}</div>
                            <div className="text-sm text-gray-500">{farmer.location} • Joined: {new Date(farmer.linked_date).toLocaleDateString()}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold">₦{farmer.total_sales.toLocaleString()}</div>
                            <div className="text-sm text-gray-500">{farmer.total_listings} listings</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-6">
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
                  <p>Loading dashboard data...</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Market Prices Chart */}
      {showMarketChart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold">📈 Market Prices</h2>
                <button
                  onClick={() => setShowMarketChart(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              <div className="mb-6">
                <p className="text-gray-600">
                  Current market prices for agricultural products. Prices are updated regularly based on market conditions.
                </p>
              </div>
              
              {marketPrices.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <p>Loading market prices...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {marketPrices.map((item, index) => (
                    <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold text-gray-800">{item.product}</h3>
                          <div className="text-xs text-gray-500 capitalize">{item.category.replace('_', ' ')}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-xl font-bold text-gray-900">₦{item.price.toLocaleString()}</div>
                          <div className={`text-sm font-medium ${
                            item.trend.startsWith('+') ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {item.trend}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="text-sm text-blue-800">
                  <strong>Note:</strong> Prices are indicative and may vary based on quality, location, and market conditions. 
                  Use these as reference for your pricing decisions.
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