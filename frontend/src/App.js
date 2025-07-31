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
  
  // New state for enhanced features
  const [showMessaging, setShowMessaging] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [showOrderTracking, setShowOrderTracking] = useState(false);
  const [orders, setOrders] = useState([]);
  
  // Group buying state
  const [showGroupBuying, setShowGroupBuying] = useState(false);
  const [groupBuyingStep, setGroupBuyingStep] = useState('search'); // 'search', 'buyers', 'recommendations', 'commission'
  const [groupBuyingData, setGroupBuyingData] = useState({
    produce: '',
    category: '',
    quantity: 0,
    location: '',
    buyers: [],
    recommendations: [],
    selectedPrice: null,
    commissionType: 'pyramyd' // 'pyramyd' (5%) or 'after_delivery'
  });
  const [buyerSearch, setBuyerSearch] = useState('');
  const [foundBuyers, setFoundBuyers] = useState([]);
  
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
      // Map the frontend platforms to backend platforms
      const platformParam = currentPlatform === 'buy_from_farm' ? 'pyhub' : 'pyexpress';
      
      let url = `${API_BASE_URL}/api/products?platform=${platformParam}`;
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
    setShowProfileMenu(false);
  };

  const sendMessage = () => {
    if (newMessage.trim()) {
      const message = {
        id: Date.now(),
        text: newMessage,
        sender: user?.username || 'You',
        timestamp: new Date().toLocaleTimeString(),
        isOwn: true
      };
      setMessages([...messages, message]);
      setNewMessage('');
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <img 
                src="https://customer-assets.emergentagent.com/job_pyramyd-agritech/artifacts/ml8alcyl_image.png" 
                alt="Pyramyd" 
                className="h-8 w-auto sm:h-10"
              />
            </div>

            {/* Platform Navigation - All users can access both */}
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setCurrentPlatform('home')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentPlatform === 'home'
                    ? 'bg-emerald-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Home
              </button>
              <button
                onClick={() => setCurrentPlatform('buy_from_farm')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentPlatform === 'buy_from_farm'
                    ? 'bg-emerald-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Buy from Farm
              </button>
            </div>

            {/* Right side navigation icons */}
            <div className="flex items-center space-x-1 sm:space-x-2">
              {/* Order Tracking / Find Drivers */}
              {user && (
                <button
                  onClick={() => {
                    setShowOrderTracking(true);
                    fetchOrders();
                  }}
                  className="nav-button icon-button p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg"
                  title="Track Orders / Find Drivers"
                >
                  <TruckIcon />
                </button>
              )}

              {/* Messaging */}
              {user && (
                <button
                  onClick={() => setShowMessaging(true)}
                  className="nav-button icon-button relative p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg"
                  title="Messages"
                >
                  <MessageIcon />
                  {messages.length > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                      {messages.length}
                    </span>
                  )}
                </button>
              )}

              {/* Cart */}
              <button
                onClick={() => setShowCart(true)}
                className="nav-button icon-button relative p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg"
                title="Shopping Cart"
              >
                <AddToCartIcon />
                {cartItemCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-emerald-600 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                    {cartItemCount}
                  </span>
                )}
              </button>

              {/* Profile Menu or Sign In */}
              {user ? (
                <div className="relative">
                  <button
                    onClick={() => setShowProfileMenu(!showProfileMenu)}
                    className="nav-button icon-button flex items-center space-x-1 p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg"
                    title="Profile Menu"
                  >
                    <ProfileIcon />
                    <span className="hidden sm:block text-sm font-medium">
                      {user.first_name}
                    </span>
                  </button>

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
                          Manage Profile
                        </button>
                        
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
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="bg-emerald-600 text-white px-3 py-2 rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium"
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
            {currentPlatform === 'buy_from_farm' ? 'PyHub - Buy from Farm' : 'Pyramyd Home'}
          </h1>
          <p className="text-gray-600">
            {currentPlatform === 'buy_from_farm' 
              ? 'Buy fresh produce directly from farms and get the best quality at source prices'
              : 'Your comprehensive agricultural marketplace connecting farmers, suppliers, and buyers'
            }
          </p>
        </div>

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

        {/* Advertisement Slider */}
        <div className="mb-6">
          <div className="relative bg-gradient-to-r from-emerald-100 to-emerald-50 rounded-xl p-6 overflow-hidden">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Slice Show about the app
              </h3>
              <p className="text-gray-600 text-sm mb-4">
                Connect directly with farmers and suppliers for the freshest produce
              </p>
              
              {/* Pagination dots */}
              <div className="flex justify-center space-x-2">
                <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
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

      {/* Messaging Modal */}

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

      {/* Messaging Modal */}
      {showMessaging && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50">
          <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-lg">
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

            <div className="flex-1 p-4 h-96 overflow-y-auto">
              {messages.length === 0 ? (
                <p className="text-gray-500 text-center">No messages yet</p>
              ) : (
                <div className="space-y-3">
                  {messages.map(message => (
                    <div key={message.id} className={`flex ${message.isOwn ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs p-3 rounded-lg ${
                        message.isOwn 
                          ? 'bg-emerald-600 text-white' 
                          : 'bg-gray-200 text-gray-900'
                      }`}>
                        <p className="text-sm">{message.text}</p>
                        <p className="text-xs mt-1 opacity-75">{message.timestamp}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                />
                <button
                  onClick={sendMessage}
                  className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors"
                >
                  Send
                </button>
              </div>
            </div>
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
    </div>
  );
}

export default App;