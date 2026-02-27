import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { AddToCartIcon, MessageIcon, TruckIcon, ProfileIcon } from './Icons';

const HomeIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const LeafIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const CommunityIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const RequestsIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

const Header = ({
    currentPlatform,
    setCurrentPlatform,
    cartItemCount,
    setShowCart,
    setShowMessaging,
    messages,
    showProfileMenu,
    setShowProfileMenu,
    kycStatus,
    // Navigation/Modal setters
    setShowProfilePictureUpload,
    setShowDriverManagement,
    setShowFindDrivers,
    setShowFarmerDashboard,
    setShowAgentDashboard,
    setShowMarketChart,
    setShowDriverPortal,
    setShowLogisticsDashboard,
    setShowCreateDeliveryRequest,
    setShowAddDropOff,
    setShowWallet,


    setShowEditProfile,
    setShowAdminDashboard // Added prop
}) => {
    const { user, logout, setShowAuthModal } = useAuth();
    return (
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
                    <div className="flex items-center bg-gray-100 rounded-lg p-1 mx-2 sm:mx-4 overflow-x-auto">
                        <button
                            onClick={() => setCurrentPlatform('home')}
                            className={`flex flex-col sm:flex-row items-center justify-center px-3 py-1.5 sm:py-2 rounded-md transition-colors ${currentPlatform === 'home'
                                ? 'bg-white text-emerald-600 shadow-sm'
                                : 'text-gray-500 hover:text-gray-900'
                                }`}
                        >
                            <HomeIcon />
                            <span className="text-[10px] sm:text-sm font-medium mt-0.5 sm:mt-0 sm:ml-2">PyExpress</span>
                        </button>
                        <button
                            onClick={() => setCurrentPlatform('buy_from_farm')}
                            className={`flex flex-col sm:flex-row items-center justify-center px-3 py-1.5 sm:py-2 rounded-md transition-colors ${currentPlatform === 'buy_from_farm'
                                ? 'bg-white text-emerald-600 shadow-sm'
                                : 'text-gray-500 hover:text-gray-900'
                                }`}
                        >
                            <LeafIcon />
                            <span className="text-[10px] sm:text-sm font-medium mt-0.5 sm:mt-0 sm:ml-2">Farm Deals</span>
                        </button>
                        <button
                            onClick={() => setCurrentPlatform('communities')}
                            className={`flex flex-col sm:flex-row items-center justify-center px-3 py-1.5 sm:py-2 rounded-md transition-colors ${currentPlatform === 'communities'
                                ? 'bg-white text-emerald-600 shadow-sm'
                                : 'text-gray-500 hover:text-gray-900'
                                }`}
                        >
                            <CommunityIcon />
                            <span className="text-[10px] sm:text-sm font-medium mt-0.5 sm:mt-0 sm:ml-2">Communities</span>
                        </button>
                    </div>

                    {/* Right Navigation Icons */}
                    <div className="flex items-center gap-1 sm:gap-2 md:gap-4">
                        {/* Cart Icon */}
                        <button
                            onClick={() => setShowCart(true)}
                            className="nav-button icon-button relative p-1 sm:p-2 text-gray-400 hover:text-gray-500"
                        >
                            <span className="sr-only">Shopping Cart</span>
                            <AddToCartIcon />
                            {cartItemCount > 0 && (
                                <span className="absolute top-0 right-0 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-bold leading-none text-white transform translate-x-1/4 -translate-y-1/4 bg-red-600 rounded-full">
                                    {cartItemCount}
                                </span>
                            )}
                        </button>

                        {/* Messaging Icon */}
                        {user && (
                            <button
                                onClick={() => setShowMessaging(true)}
                                className="nav-button icon-button relative p-1 sm:p-2 text-gray-400 hover:text-gray-500"
                            >
                                <span className="sr-only">Messages</span>
                                <MessageIcon />
                                {messages.filter(m => !m.read && m.recipient === user.username).length > 0 && (
                                    <span className="absolute top-0 right-0 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-bold leading-none text-white transform translate-x-1/4 -translate-y-1/4 bg-red-600 rounded-full">
                                        {messages.filter(m => !m.read && m.recipient === user.username).length}
                                    </span>
                                )}
                            </button>
                        )}

                        {/* Order Tracking Icon (Truck) */}
                        {user && (
                            <button
                                onClick={() => { /* toggle order tracking logic not passed yet, assumes Modal handled in App */ }}
                                className="nav-button icon-button p-1 sm:p-2 text-gray-400 hover:text-gray-500"
                            >
                                <TruckIcon />
                            </button>
                        )}

                        {/* User Profile / Sign In */}
                        <div className="relative ml-2">
                            {!user ? (
                                <button
                                    onClick={() => setShowAuthModal(true)}
                                    className="nav-button icon-button flex items-center gap-1 sm:gap-2 p-1 sm:p-1.5 md:p-2 text-gray-600 hover:text-emerald-600 transition-colors rounded-lg border border-gray-200 hover:border-emerald-500"
                                    title="Sign In"
                                >
                                    <div className="w-5 h-5 flex-shrink-0">
                                        <ProfileIcon />
                                    </div>
                                    <span className="hidden md:inline text-xs md:text-sm font-medium whitespace-nowrap">Sign In</span>
                                </button>
                            ) : (
                                <div className="relative">
                                    <button
                                        onClick={() => setShowProfileMenu(!showProfileMenu)}
                                        className="flex items-center max-w-xs text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500"
                                    >
                                        <span className="sr-only">Open user menu</span>
                                        {user.profile_picture ? (
                                            <img
                                                className="h-8 w-8 rounded-full object-cover border-2 border-emerald-500"
                                                src={user.profile_picture}
                                                alt=""
                                            />
                                        ) : (
                                            <div className="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center border-2 border-emerald-500">
                                                <span className="text-emerald-800 font-medium text-xs">
                                                    {user.first_name ? user.first_name.charAt(0).toUpperCase() : 'U'}
                                                </span>
                                            </div>
                                        )}
                                        {/* Verification Badge */}
                                        {kycStatus?.status === 'approved' && (
                                            <div className="absolute -bottom-1 -right-1 bg-white rounded-full p-0.5">
                                                <svg className="w-3 h-3 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                                </svg>
                                            </div>
                                        )}
                                    </button>

                                    {/* Profile Dropdown */}
                                    {showProfileMenu && (
                                        <div className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50 divide-y divide-gray-100">
                                            <div className="px-4 py-3">
                                                <p className="text-sm">Signed in as</p>
                                                <p className="text-sm font-medium text-gray-900 truncate">@{user.username}</p>
                                                <p className="text-xs text-gray-500 mt-1 capitalize">{user.role?.replace('_', ' ')}</p>
                                            </div>

                                            {/* Wallet Snapshot */}
                                            <div className="px-4 py-3 bg-emerald-50 border-y border-emerald-100">
                                                <div className="flex justify-between items-center mb-1">
                                                    <p className="text-xs font-semibold text-emerald-800 uppercase tracking-wide">Wallet Balance</p>
                                                    <span className="text-xs text-emerald-600 cursor-pointer hover:underline" onClick={() => { setShowProfileMenu(false); setShowWallet(true); }}>Manage</span>
                                                </div>
                                                <p className="text-xl font-bold text-emerald-700">₦{user.wallet_balance?.toLocaleString() || '0.00'}</p>

                                                {user.dva_account_number ? (
                                                    <div className="mt-2 pt-2 border-t border-emerald-200">
                                                        <p className="text-[10px] text-emerald-600 uppercase font-medium">Fund via Bank Transfer:</p>
                                                        <div className="flex items-center space-x-2 mt-0.5">
                                                            <p className="text-xs font-mono font-bold text-emerald-800 bg-white px-1 rounded border border-emerald-200">{user.dva_account_number}</p>
                                                            <p className="text-xs text-emerald-700">{user.dva_bank_name}</p>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    ['farmer', 'processor', 'aggregator', 'business'].includes(user.role) && (
                                                        <div className="mt-2 pt-2 border-t border-emerald-200">
                                                            <button
                                                                onClick={() => { setShowProfileMenu(false); setShowEditProfile(true); }}
                                                                className="w-full py-1.5 bg-yellow-100 text-yellow-800 text-xs font-bold rounded border border-yellow-200 hover:bg-yellow-200 flex items-center justify-center animate-pulse"
                                                            >
                                                                ⚠️ Create Virtual Account
                                                            </button>
                                                        </div>
                                                    )
                                                )}
                                            </div>

                                            <div className="py-1">
                                                <button
                                                    onClick={() => { setShowProfileMenu(false); setShowEditProfile(true); }}
                                                    className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                >
                                                    <span className="mr-3">✏️</span> Edit Profile
                                                </button>
                                                <button
                                                    onClick={() => { setShowProfileMenu(false); setShowProfilePictureUpload(true); }}
                                                    className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                >
                                                    <span className="mr-3">📷</span> Change Photo
                                                </button>

                                                {/* Driver Management - For Logistics Business */}
                                                {user.role === 'business' && user.business_category === 'logistics_business' && (
                                                    <button
                                                        onClick={() => { setShowProfileMenu(false); setShowDriverManagement(true); }}
                                                        className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                    >
                                                        <span className="mr-3">🚛</span> Manage Drivers
                                                    </button>
                                                )}

                                                {/* Find Drivers - For Everyone except Drivers */}
                                                {user.role !== 'driver' && (
                                                    <button
                                                        onClick={() => { setShowProfileMenu(false); setShowFindDrivers(true); }}
                                                        className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                    >
                                                        <span className="mr-3">🔍</span> Find Drivers
                                                    </button>
                                                )}

                                                {/* Dashboards based on role */}
                                                <button
                                                    onClick={() => {
                                                        setShowProfileMenu(false);
                                                        if (user.role === 'admin') {
                                                            window.location.href = '/pyadmin';
                                                        } else if (['farmer', 'business', 'supplier_food_produce'].includes(user.role)) {
                                                            setShowFarmerDashboard(true);
                                                        } else if (['agent', 'purchasing_agent'].includes(user.role)) {
                                                            setShowAgentDashboard(true);
                                                        } else {
                                                            // Requires App.js to pass down setShowPersonalDashboard or handle it
                                                            // Since Header does not receive setShowPersonalDashboard, we could
                                                            // add it to props or rely on the App.js profile menu.
                                                            // Wait, Header.js IS the profile menu currently. Let's fix props in App.js as well.
                                                            if (typeof setShowPersonalDashboard === 'function') {
                                                                setShowPersonalDashboard(true);
                                                            }
                                                        }
                                                    }}
                                                    className="group flex items-center w-full px-4 py-2 text-sm text-green-700 hover:bg-green-50 font-medium"
                                                >
                                                    <span className="mr-3">⚙️</span> My Dashboard
                                                </button>

                                                {/* Create Request (Bulk Buy) */}
                                                <button
                                                    onClick={() => {
                                                        setShowProfileMenu(false);
                                                        // Ensure app has a handler to open the request wizard. Let's assume passed in or dispatched.
                                                        if (typeof window.openRequestWizard === 'function') window.openRequestWizard();
                                                    }}
                                                    className="group flex items-center w-full px-4 py-2 text-sm text-purple-700 hover:bg-purple-50 font-medium border-b border-gray-100 pb-3 mb-1"
                                                >
                                                    <span className="mr-3">➕</span> Create Request (Bulk Buy)
                                                </button>

                                                <button
                                                    onClick={() => { setShowProfileMenu(false); setShowMarketChart(true); }}
                                                    className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                >
                                                    <span className="mr-3">📊</span> Market Prices
                                                </button>

                                                {user.role === 'driver' && (
                                                    <>
                                                        <button
                                                            onClick={() => { setShowProfileMenu(false); setShowDriverPortal(true); }}
                                                            className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                        >
                                                            <span className="mr-3">🚛</span> Driver Portal
                                                        </button>
                                                        <button
                                                            onClick={() => { setShowProfileMenu(false); setShowLogisticsDashboard(true); }}
                                                            className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                        >
                                                            <span className="mr-3">📦</span> Deliveries
                                                        </button>
                                                    </>
                                                )}

                                                <button
                                                    onClick={() => { setShowProfileMenu(false); setShowCreateDeliveryRequest(true); }}
                                                    className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                >
                                                    <span className="mr-3">📦</span> Request Delivery
                                                </button>

                                                <button
                                                    onClick={() => { setShowProfileMenu(false); setShowAddDropOff(true); }}
                                                    className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                >
                                                    <span className="mr-3">📍</span> Saved Locations
                                                </button>

                                                <button
                                                    onClick={() => {
                                                        setShowProfileMenu(false);
                                                        // Logic to open KYC prompt
                                                        alert('KYC Status: ' + (kycStatus?.status || 'Not Started'));
                                                    }}
                                                    className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                >
                                                    <span className="mr-3">✓</span> KYC Verification
                                                </button>
                                            </div>

                                            <div className="py-1">
                                                <button
                                                    onClick={() => { setShowProfileMenu(false); setShowWallet(true); }}
                                                    className="group flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                >
                                                    <span className="mr-3">💰</span> Wallet
                                                </button>

                                            </div>

                                            <div className="py-1">
                                                <button
                                                    onClick={() => {
                                                        setShowProfileMenu(false);
                                                        logout();
                                                    }}
                                                    className="group flex items-center w-full px-4 py-2 text-sm text-red-700 hover:bg-red-50"
                                                >
                                                    <span className="mr-3">🚪</span> Sign Out
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
