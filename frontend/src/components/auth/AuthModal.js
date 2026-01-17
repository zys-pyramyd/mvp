import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

const AuthModal = () => {
    const {
        showAuthModal, setShowAuthModal,
        authMode, setAuthMode,
        login, register
    } = useAuth();

    // Local State moved from App.js
    const [authForm, setAuthForm] = useState({
        first_name: '',
        last_name: '',
        username: '',
        email_or_phone: '',
        password: '',
        phone: '',
        gender: '',
        date_of_birth: ''
    });

    const [registrationStep, setRegistrationStep] = useState('basic');
    const [selectedUserPath, setSelectedUserPath] = useState('');
    const [selectedBuyerType, setSelectedBuyerType] = useState('');
    const [businessInfo, setBusinessInfo] = useState({
        business_name: '',
        business_address: '',
        city: '',
        state: '',
        country: '',
        home_address: '',
        business_type: ''
    });
    const [partnerType, setPartnerType] = useState('');
    const [businessCategory, setBusinessCategory] = useState('');
    const [verificationInfo, setVerificationInfo] = useState({
        nin: '',
        bvn: '',
        cac_number: '',
        photo: '',
        farm_photo: '',
        farm_info: '',
        verification_type: ''
    });

    if (!showAuthModal) return null;

    const onClose = () => setShowAuthModal(false);

    // Handlers
    const handleBasicRegistration = async (e) => {
        e.preventDefault();
        setRegistrationStep('role_path');
    };

    const handleRolePath = (path) => {
        setSelectedUserPath(path);
        // Previously passed as prop, now local function but used inline in JSX?
        // Wait, JSX used: onClick={() => { setAuthForm(...); handleCompleteRegistration(); }} for personal
        // Or: onClick={() => { setAuthForm(...); setRegistrationStep('business_profile'); }}
        // wait, I need to check the exact JSX logic for the buttons.
    };

    const handleBuyerTypeSelection = (type) => {
        setSelectedBuyerType(type);
        if (type === 'others') {
            setRegistrationStep('business_info');
        } else if (type === 'skip') {
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

    const handleCompleteRegistration = async () => {
        try {
            const registrationData = {
                ...authForm,
                user_path: selectedUserPath,
                buyer_type: selectedBuyerType,
                business_info: businessInfo,
                partner_type: partnerType,
                business_category: businessCategory,
                partner_type: partnerType,
                business_category: businessCategory,
                verification_info: verificationInfo,
                bvn: verificationInfo.bvn // Extract BVN from verification info
            };

            // Use context register
            // Note: Context register takes (endpoint, data)
            const result = await register('/api/auth/complete-registration', registrationData);

            if (result.success) {
                // Check if context handles closing modal (it does)
                // Reset form
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
                alert(result.message);
            }
        } catch (error) {
            console.error('Registration error:', error);
            alert('An error occurred. Please try again.');
        }
    };

    const handleAuth = async (e) => {
        e.preventDefault();

        try {
            const result = await login({
                email_or_phone: authForm.email_or_phone,
                password: authForm.password
            });

            if (result.success) {
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
                alert(result.message);
            }
        } catch (error) {
            console.error('Auth error:', error);
            alert('An error occurred. Please try again.');
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
                {/* Login Form */}
                {authMode === 'login' && (
                    <>
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-bold">Sign In</h2>
                            <button
                                onClick={onClose}
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
                                onChange={(e) => setAuthForm(prev => ({ ...prev, email_or_phone: e.target.value }))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                required
                            />

                            <input
                                type="password"
                                placeholder="Password"
                                value={authForm.password}
                                onChange={(e) => setAuthForm(prev => ({ ...prev, password: e.target.value }))}
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
                                        onClick={onClose}
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
                                            onChange={(e) => setAuthForm(prev => ({ ...prev, first_name: e.target.value }))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                            required
                                        />
                                        <input
                                            type="text"
                                            placeholder="Last Name"
                                            value={authForm.last_name}
                                            onChange={(e) => setAuthForm(prev => ({ ...prev, last_name: e.target.value }))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                            required
                                        />
                                    </div>

                                    <input
                                        type="text"
                                        placeholder="Username (unique)"
                                        value={authForm.username}
                                        onChange={(e) => setAuthForm(prev => ({ ...prev, username: e.target.value }))}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                        required
                                    />

                                    <input
                                        type="text"
                                        placeholder="Email or Phone Number"
                                        value={authForm.email_or_phone}
                                        onChange={(e) => setAuthForm(prev => ({ ...prev, email_or_phone: e.target.value }))}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                        required
                                    />

                                    <input
                                        type="tel"
                                        placeholder="Phone Number (optional)"
                                        value={authForm.phone}
                                        onChange={(e) => setAuthForm(prev => ({ ...prev, phone: e.target.value }))}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                    />

                                    <div className="grid grid-cols-2 gap-3">
                                        <select
                                            value={authForm.gender}
                                            onChange={(e) => setAuthForm(prev => ({ ...prev, gender: e.target.value }))}
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
                                            onChange={(e) => setAuthForm(prev => ({ ...prev, date_of_birth: e.target.value }))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                            required
                                        />
                                    </div>

                                    <input
                                        type="password"
                                        placeholder="Password"
                                        value={authForm.password}
                                        onChange={(e) => setAuthForm(prev => ({ ...prev, password: e.target.value }))}
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
                                                        setAuthForm({ ...authForm, role: 'personal' });
                                                        setSelectedUserPath('buyer');
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
                                                        setAuthForm({ ...authForm, role: 'farmer' });
                                                        setSelectedUserPath('partner');
                                                        setPartnerType('farmer');
                                                        setRegistrationStep('verification');
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
                                                        setAuthForm({ ...authForm, role: 'agent' });
                                                        setSelectedUserPath('partner');
                                                        setPartnerType('agent');
                                                        setRegistrationStep('verification');
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
                                                        setAuthForm({ ...authForm, role: 'business' });
                                                        setSelectedUserPath('partner');
                                                        setPartnerType('business');
                                                        setRegistrationStep('business_category');
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
                                    <form onSubmit={(e) => { e.preventDefault(); handleCompleteRegistration(); }} className="space-y-4">
                                        {selectedBuyerType === 'others' && (
                                            <input
                                                type="text"
                                                placeholder="Specify your business type"
                                                value={businessInfo.business_type}
                                                onChange={(e) => setBusinessInfo(prev => ({ ...prev, business_type: e.target.value }))}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                required
                                            />
                                        )}

                                        <input
                                            type="text"
                                            placeholder="Business Name"
                                            value={businessInfo.business_name}
                                            onChange={(e) => setBusinessInfo(prev => ({ ...prev, business_name: e.target.value }))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                            required
                                        />

                                        <input
                                            type="text"
                                            placeholder="Business Address"
                                            value={businessInfo.business_address}
                                            onChange={(e) => setBusinessInfo(prev => ({ ...prev, business_address: e.target.value }))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                            required
                                        />

                                        <div className="grid grid-cols-3 gap-3">
                                            <input
                                                type="text"
                                                placeholder="City"
                                                value={businessInfo.city}
                                                onChange={(e) => setBusinessInfo(prev => ({ ...prev, city: e.target.value }))}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                required
                                            />
                                            <input
                                                type="text"
                                                placeholder="State"
                                                value={businessInfo.state}
                                                onChange={(e) => setBusinessInfo(prev => ({ ...prev, state: e.target.value }))}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                required
                                            />
                                            <input
                                                type="text"
                                                placeholder="Country"
                                                value={businessInfo.country}
                                                onChange={(e) => setBusinessInfo(prev => ({ ...prev, country: e.target.value }))}
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
                                    <form onSubmit={(e) => { e.preventDefault(); handleCompleteRegistration(); }} className="space-y-4">
                                        <input
                                            type="text"
                                            placeholder="Home Address"
                                            value={businessInfo.home_address}
                                            onChange={(e) => setBusinessInfo(prev => ({ ...prev, home_address: e.target.value }))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                            required
                                        />

                                        <div className="grid grid-cols-3 gap-3">
                                            <input
                                                type="text"
                                                placeholder="City"
                                                value={businessInfo.city}
                                                onChange={(e) => setBusinessInfo(prev => ({ ...prev, city: e.target.value }))}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                required
                                            />
                                            <input
                                                type="text"
                                                placeholder="State"
                                                value={businessInfo.state}
                                                onChange={(e) => setBusinessInfo(prev => ({ ...prev, state: e.target.value }))}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                required
                                            />
                                            <input
                                                type="text"
                                                placeholder="Country"
                                                value={businessInfo.country}
                                                onChange={(e) => setBusinessInfo(prev => ({ ...prev, country: e.target.value }))}
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
                                    <form onSubmit={(e) => { e.preventDefault(); handleCompleteRegistration(); }} className="space-y-4">
                                        {/* Common BVN for all Partners (Required for Wallet/DVA) */}
                                        <div className="mb-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Bank Verification Number (BVN) <span className="text-red-500">*</span>
                                            </label>
                                            <input
                                                type="text"
                                                placeholder="Enter your 11-digit BVN"
                                                value={verificationInfo.bvn}
                                                onChange={(e) => {
                                                    const val = e.target.value.replace(/\D/g, '').slice(0, 11);
                                                    setVerificationInfo(prev => ({ ...prev, bvn: val }));
                                                }}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                minLength={11}
                                                maxLength={11}
                                                required
                                            />
                                            <div className="mt-2 p-2 bg-blue-50 text-xs text-blue-700 rounded border border-blue-100 flex items-start">
                                                <span className="mr-2 text-lg">🏦</span>
                                                <span>
                                                    <strong>Why do we need this?</strong> We use your BVN to automatically create a
                                                    <strong> Dedicated Virtual Account</strong> for you. This allows you to receive payments and withdraw funds securely.
                                                    Your data is encrypted.
                                                </span>
                                            </div>
                                        </div>

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
                                                    onChange={(e) => setVerificationInfo(prev => ({ ...prev, nin: e.target.value }))}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                    required
                                                />
                                                <input
                                                    type="file"
                                                    accept="image/*"
                                                    placeholder="Upload your photo"
                                                    onChange={(e) => setVerificationInfo(prev => ({ ...prev, photo: e.target.files[0]?.name || '' }))}
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
                                                    placeholder="Bank Verification Number (BVN)"
                                                    value={verificationInfo.bvn}
                                                    onChange={(e) => setVerificationInfo(prev => ({ ...prev, bvn: e.target.value }))}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 mb-2"
                                                    required
                                                />
                                                <p className="text-xs text-red-600 mb-3 font-medium">
                                                    IMPORTANT: Your Registered Name MUST match the name on your BVN/NIN for payouts to be processed successfully.
                                                </p>
                                                <input
                                                    type="text"
                                                    placeholder="National Identification Number (NIN)"
                                                    value={verificationInfo.nin}
                                                    onChange={(e) => setVerificationInfo(prev => ({ ...prev, nin: e.target.value }))}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 mb-3"
                                                    required
                                                />
                                                <input
                                                    type="file"
                                                    accept="image/*"
                                                    placeholder="Upload your photo"
                                                    onChange={(e) => setVerificationInfo(prev => ({ ...prev, photo: e.target.files[0]?.name || '' }))}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                    required
                                                />
                                                <input
                                                    type="file"
                                                    accept="image/*"
                                                    placeholder="Upload farm photo"
                                                    onChange={(e) => setVerificationInfo(prev => ({ ...prev, farm_photo: e.target.files[0]?.name || '' }))}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                    required
                                                />
                                                <textarea
                                                    placeholder="Farm Information (location, size, crops grown, etc.)"
                                                    value={verificationInfo.farm_info}
                                                    onChange={(e) => setVerificationInfo(prev => ({ ...prev, farm_info: e.target.value }))}
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
                                                    onChange={(e) => setVerificationInfo(prev => ({ ...prev, cac_number: e.target.value }))}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                    required
                                                />
                                                <input
                                                    type="text"
                                                    placeholder="Business Name"
                                                    value={businessInfo.business_name}
                                                    onChange={(e) => setBusinessInfo(prev => ({ ...prev, business_name: e.target.value }))}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                    required
                                                />
                                                <input
                                                    type="text"
                                                    placeholder="Business Address"
                                                    value={businessInfo.business_address}
                                                    onChange={(e) => setBusinessInfo(prev => ({ ...prev, business_address: e.target.value }))}
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
                                                            onChange={(e) => setVerificationInfo(prev => ({ ...prev, verification_type: e.target.value }))}
                                                            className="mr-2"
                                                        />
                                                        Use NIN (Individual/Unregistered Business)
                                                    </label>
                                                    <label className="flex items-center">
                                                        <input
                                                            type="radio"
                                                            name="supplier_verification"
                                                            value="cac"
                                                            onChange={(e) => setVerificationInfo(prev => ({ ...prev, verification_type: e.target.value }))}
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
                                                        onChange={(e) => setVerificationInfo(prev => ({ ...prev, nin: e.target.value }))}
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
                                                            onChange={(e) => setVerificationInfo(prev => ({ ...prev, cac_number: e.target.value }))}
                                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                            required
                                                        />
                                                        <input
                                                            type="text"
                                                            placeholder="Business Name"
                                                            value={businessInfo.business_name}
                                                            onChange={(e) => setBusinessInfo(prev => ({ ...prev, business_name: e.target.value }))}
                                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                                            required
                                                        />
                                                        <input
                                                            type="text"
                                                            placeholder="Business Address"
                                                            value={businessInfo.business_address}
                                                            onChange={(e) => setBusinessInfo(prev => ({ ...prev, business_address: e.target.value }))}
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
    );
};

export default AuthModal;
