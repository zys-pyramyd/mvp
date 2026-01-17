import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';

const CheckoutModal = ({
    isOpen,
    onClose,
    cart,
    orderSummary,
    checkoutPlatform,
    onCheckoutComplete,
    availableLocations = []
}) => {
    const { user } = useAuth();

    // Modal State
    const [checkoutStep, setCheckoutStep] = useState('review'); // 'review', 'address', 'payment'
    const [addressMode, setAddressMode] = useState('registered'); // 'registered', 'new', 'pickup'

    // Form State
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

    const [selectedPickupLocation, setSelectedPickupLocation] = useState('');

    // Payment State
    const [paymentProcessing, setPaymentProcessing] = useState(false);
    const [paymentStatus, setPaymentStatus] = useState(null); // 'success', 'failed', null
    const [orderConfirmation, setOrderConfirmation] = useState(null);
    const [paymentMethod, setPaymentMethod] = useState('wallet'); // 'wallet' or 'paystack'
    const walletBalance = user?.wallet_balance || 0;
    const canPayWithWallet = walletBalance >= (orderSummary.total || 0);

    // Initialize address from user profile if available
    useEffect(() => {
        if (user && addressMode === 'registered') {
            setShippingAddress({
                full_name: `${user.first_name || ''} ${user.last_name || ''}`.trim(),
                phone: user.phone || '',
                email: user.email || '',
                address_line_1: user.address_line_1 || user.address || '',
                address_line_2: user.address_line_2 || '',
                city: user.city || '',
                state: user.state || '',
                postal_code: user.postal_code || '',
                country: user.country || 'Nigeria',
                delivery_instructions: ''
            });
        } else if (addressMode === 'new') {
            setShippingAddress({
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
        }
    }, [user, addressMode]);

    // Reset state when modal opens
    useEffect(() => {
        if (isOpen) {
            setCheckoutStep('review');
            setPaymentStatus(null);
            setOrderConfirmation(null);
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const validateAddress = () => {
        if (addressMode === 'pickup') {
            if (!selectedPickupLocation) {
                alert('Please select a pickup location');
                return false;
            }
            return true;
        }

        const required = ['full_name', 'phone', 'address_line_1', 'city', 'state'];
        const missing = required.filter(field => !shippingAddress[field]?.trim());

        if (missing.length > 0) {
            alert(`Please fill in the following required fields: ${missing.join(', ')}`);
            return false;
        }

        if (!/^\+?[\d\s-()]+$/.test(shippingAddress.phone)) {
            alert('Please enter a valid phone number');
            return false;
        }

        return true;
    };

    const handleInitializePayment = async () => {
        if (!validateAddress()) return;

        setPaymentProcessing(true);

        try {
            // 1. Calculate totals
            const productTotal = orderSummary.product_total;

            // 2. Prepare Payload
            // Note: In a real app, you might want to create the order *before* payment
            // or use a transaction initialization endpoint that handles it.
            // We'll mimic the existing App.js logic here.

            const subaccountCode = cart[0]?.product?.seller_subaccount_code || null;
            const platformType = checkoutPlatform === 'pyexpress' ? 'home' : 'farmhub';

            const paymentData = {
                product_total: productTotal,
                customer_state: addressMode === 'pickup' ? selectedPickupLocation : shippingAddress.state,
                product_weight: cart.reduce((sum, item) => sum + (item.quantity * 1), 0),
                subaccount_code: subaccountCode,
                product_id: cart.map(item => item.product.id || item.product._id).join(','),
                platform_type: platformType,
                callback_url: `${window.location.origin}/payment-callback`,
                // Include address info in metadata for backend to use after webhook
                metadata: {
                    address_mode: addressMode,
                    shipping_address: addressMode === 'pickup' ? null : shippingAddress,
                    pickup_location: addressMode === 'pickup' ? selectedPickupLocation : null
                }
            };

            // 3. Call API
            const response = await api.post('/paystack/transaction/initialize', paymentData);
            const result = response.data;

            // 4. Confirm Amount
            // (Using window.confirm as in original code, though a modal UI is better)
            const breakdown = result.breakdown;
            const confirmPayment = window.confirm(
                `Payment Breakdown:\n\n` +
                `Product Total: ₦${breakdown.product_total.toLocaleString()}\n` +
                `Delivery Fee (${breakdown.delivery_state}): ₦${breakdown.delivery_fee.toLocaleString()}\n` +
                `Platform Charges: ₦${breakdown.platform_cut.toLocaleString()}\n` +
                `\nTotal Amount: ₦${result.amount.toLocaleString()}\n\n` +
                `Proceed to payment gateway?`
            );

            if (confirmPayment) {
                window.location.href = result.authorization_url;
            } else {
                setPaymentProcessing(false);
            }

        } catch (error) {
            console.error('Payment initialization error:', error);
            alert(`Payment initialization failed: ${error.message || 'Unknown error'}`);
            setPaymentProcessing(false);
        }
    };

    // Note: Actual verification happens on callback page or needs polling.
    // For this refactor, we assume the user is redirected away. 
    // If we want to simulate success for "offline" dev:
    const simulateSuccess = async () => {
        // Create orders logic
        await createOrders();
    };

    const createOrders = async () => {
        if (!validateAddress()) return;
        setPaymentProcessing(true);

        try {
            // Map cart items to backend schema
            const orderItems = cart.map(item => ({
                product_id: item.product.id || item.product._id,
                quantity: item.quantity,
                unit: item.unit,
                unit_specification: item.unit_specification,
                delivery_method: item.deliveryMethod || 'delivery',
                dropoff_location: item.dropoffLocation,
            }));

            let shippingAddressStr = '';
            if (addressMode === 'pickup') {
                // For pickup, we might need a specific field in backend or just put generic info
                shippingAddressStr = `PICKUP: ${selectedPickupLocation}`;
            } else {
                shippingAddressStr = `${shippingAddress.full_name}, ${shippingAddress.address_line_1}, ${shippingAddress.address_line_2 ? shippingAddress.address_line_2 + ', ' : ''}${shippingAddress.city}, ${shippingAddress.state}, ${shippingAddress.country}`;
            }

            const payload = {
                items: orderItems,
                delivery_address: shippingAddressStr,
                payment_method: paymentMethod
            };

            const response = await api.post('/orders', payload);

            // Backend will now return { order_ids: [...] } or { order_id: ... }
            const result = response.data;
            const createdOrders = result.order_ids || (result.order_id ? [result.order_id] : []);

            setPaymentStatus('success');
            setOrderConfirmation({ orders: createdOrders });
            // onCheckoutComplete(createdOrders); // Wait for user to dismiss modal

        } catch (error) {
            console.error("Order creation failed", error);
            alert(`Order creation failed: ${error.response?.data?.detail || error.message}`);
        } finally {
            setPaymentProcessing(false);
        }
    };


    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
            <div className="bg-white rounded-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col lg:flex-row shadow-2xl">

                {/* Main Content Area */}
                <div className="flex-1 overflow-y-auto p-6 lg:p-8">
                    {paymentStatus === 'success' ? (
                        <div className="flex flex-col items-center justify-center p-8 h-full">
                            <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mb-6 animate-bounce">
                                <span className="text-4xl">🎉</span>
                            </div>
                            <h2 className="text-3xl font-bold text-gray-900 mb-4">Order Placed Successfully!</h2>
                            <p className="text-gray-600 mb-8 max-w-md text-center">
                                Thank you for your purchase. Your order has been securely placed and is currently being processed.
                            </p>

                            <div className="bg-gray-50 rounded-xl p-6 mb-8 w-full max-w-md border border-gray-200">
                                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4 text-center">Order Tracking IDs</h3>
                                <div className="space-y-3 max-h-60 overflow-y-auto">
                                    {orderConfirmation?.orders?.map((orderId, idx) => (
                                        <div key={idx} className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                                            <div className="flex items-center">
                                                <span className="mr-2">📦</span>
                                                <span className="font-mono font-medium text-gray-900">{orderId}</span>
                                            </div>
                                            <span className="text-xs px-2 py-1 bg-emerald-100 text-emerald-800 rounded-full font-medium">Confirmed</span>
                                        </div>
                                    ))}
                                </div>
                                <p className="text-xs text-center text-gray-500 mt-4">
                                    You can track your orders in the "Orders" section of your profile.
                                </p>
                            </div>

                            <div className="flex flex-col sm:flex-row gap-4">
                                <button
                                    onClick={() => onCheckoutComplete(orderConfirmation?.orders, 'view_orders')}
                                    className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-bold shadow-lg transform transition hover:scale-105"
                                >
                                    View Orders
                                </button>
                                <button
                                    onClick={() => onCheckoutComplete(orderConfirmation?.orders, 'close')}
                                    className="px-8 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-bold shadow-lg transform transition hover:scale-105"
                                >
                                    Continue Shopping
                                </button>
                            </div>
                        </div>
                    ) : (
                        <>
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-2xl font-bold text-gray-900">Checkout</h2>
                                <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            {/* Stepper */}
                            <div className="flex items-center mb-8 border-b border-gray-100 pb-4">
                                {['Review', 'Address', 'Payment'].map((step, index) => {
                                    const stepKey = step.toLowerCase();
                                    const isActive = checkoutStep === stepKey;
                                    const isCompleted =
                                        (checkoutStep === 'address' && index === 0) ||
                                        (checkoutStep === 'payment' && index <= 1);

                                    return (
                                        <div key={step} className="flex items-center">
                                            <div className={`flex items-center ${isActive ? 'text-emerald-600 font-bold' : isCompleted ? 'text-emerald-600' : 'text-gray-400'}`}>
                                                <span className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 border-2 ${isActive ? 'border-emerald-600 bg-emerald-50' :
                                                    isCompleted ? 'border-emerald-600 bg-emerald-600 text-white' :
                                                        'border-gray-300'
                                                    }`}>
                                                    {isCompleted ? '✓' : index + 1}
                                                </span>
                                                {step}
                                            </div>
                                            {index < 2 && <div className="w-12 h-0.5 bg-gray-200 mx-4" />}
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Steps Content */}
                            {checkoutStep === 'review' && (
                                <div className="space-y-6">
                                    <h3 className="text-lg font-semibold text-gray-900">Review Items</h3>
                                    <div className="bg-gray-50 rounded-lg p-6 space-y-4">
                                        {cart.map((item) => (
                                            <div key={item.id} className="flex justify-between items-start border-b border-gray-200 pb-4 last:border-0 last:pb-0">
                                                <div>
                                                    <div className="font-medium text-gray-900">{item.product.product_name || item.product.crop_type}</div>
                                                    <div className="text-sm text-gray-500">
                                                        Qty: {item.quantity} {item.unit} {item.unit_specification && `(${item.unit_specification})`}
                                                    </div>
                                                </div>
                                                <div className="font-medium text-gray-900">
                                                    ₦{(item.product.price_per_unit * item.quantity).toLocaleString()}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="flex justify-end">
                                        <button
                                            onClick={() => setCheckoutStep('address')}
                                            className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium transition-colors"
                                        >
                                            Continue to Address
                                        </button>
                                    </div>
                                </div>
                            )}

                            {checkoutStep === 'address' && (
                                <div className="space-y-6">
                                    <h3 className="text-lg font-semibold text-gray-900">Delivery Method</h3>

                                    {/* Address Mode Selection */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                        <button
                                            onClick={() => setAddressMode('registered')}
                                            className={`p-4 border-2 rounded-lg text-left transition-all ${addressMode === 'registered' ? 'border-emerald-600 bg-emerald-50 ring-1 ring-emerald-600' : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                        >
                                            <div className="font-medium text-gray-900 mb-1">Registered Address</div>
                                            <div className="text-sm text-gray-500">Use your profile address</div>
                                        </button>
                                        <button
                                            onClick={() => setAddressMode('new')}
                                            className={`p-4 border-2 rounded-lg text-left transition-all ${addressMode === 'new' ? 'border-emerald-600 bg-emerald-50 ring-1 ring-emerald-600' : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                        >
                                            <div className="font-medium text-gray-900 mb-1">New Address</div>
                                            <div className="text-sm text-gray-500">Enter a different address</div>
                                        </button>
                                        <button
                                            onClick={() => setAddressMode('pickup')}
                                            className={`p-4 border-2 rounded-lg text-left transition-all ${addressMode === 'pickup' ? 'border-emerald-600 bg-emerald-50 ring-1 ring-emerald-600' : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                        >
                                            <div className="font-medium text-gray-900 mb-1">Pickup Station</div>
                                            <div className="text-sm text-gray-500">Collect from a hub</div>
                                        </button>
                                    </div>

                                    {/* Address Forms */}
                                    {addressMode === 'pickup' ? (
                                        <div className="bg-white p-6 border border-gray-200 rounded-lg">
                                            <label className="block text-sm font-medium text-gray-700 mb-2">Select Pickup Location</label>
                                            <select
                                                value={selectedPickupLocation}
                                                onChange={(e) => setSelectedPickupLocation(e.target.value)}
                                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                            >
                                                <option value="">Select a location...</option>
                                                {availableLocations.length > 0 ? (
                                                    availableLocations.map((loc, idx) => (
                                                        <option key={idx} value={loc.name || loc}>
                                                            {typeof loc === 'string' ? loc : `${loc.name} - ${loc.city}`}
                                                        </option>
                                                    ))
                                                ) : (
                                                    <option value="Lagos Hub">Lagos Central Hub (Ikeja)</option>
                                                )}
                                            </select>
                                            <p className="mt-2 text-sm text-gray-500">
                                                You will be notified when your items are ready for collection at the selected hub.
                                            </p>
                                        </div>
                                    ) : (
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="md:col-span-2">
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                                                <input
                                                    type="text"
                                                    value={shippingAddress.full_name}
                                                    onChange={(e) => setShippingAddress({ ...shippingAddress, full_name: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500"
                                                    placeholder="Full Name"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                                                <input
                                                    type="tel"
                                                    value={shippingAddress.phone}
                                                    onChange={(e) => setShippingAddress({ ...shippingAddress, phone: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500"
                                                    placeholder="+234..."
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                                                <input
                                                    type="text"
                                                    value={shippingAddress.city}
                                                    onChange={(e) => setShippingAddress({ ...shippingAddress, city: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500"
                                                    placeholder="City"
                                                />
                                            </div>
                                            <div className="md:col-span-2">
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                                                <input
                                                    type="text"
                                                    value={shippingAddress.address_line_1}
                                                    onChange={(e) => setShippingAddress({ ...shippingAddress, address_line_1: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500"
                                                    placeholder="Street Address"
                                                />
                                            </div>
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                                                <input
                                                    type="text"
                                                    value={shippingAddress.state}
                                                    onChange={(e) => setShippingAddress({ ...shippingAddress, state: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500"
                                                    placeholder="State"
                                                />
                                            </div>
                                        </div>
                                    )}

                                    <div className="flex justify-between mt-8">
                                        <button
                                            onClick={() => setCheckoutStep('review')}
                                            className="px-6 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                                        >
                                            Back
                                        </button>
                                        <button
                                            onClick={() => {
                                                if (validateAddress()) setCheckoutStep('payment');
                                            }}
                                            className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium"
                                        >
                                            Continue to Payment
                                        </button>
                                    </div>
                                </div>
                            )}


                            {checkoutStep === 'payment' && (
                                <div className="space-y-6">
                                    <h3 className="text-lg font-semibold text-gray-900">Payment Method</h3>

                                    {/* Wallet Option */}
                                    <div
                                        onClick={() => canPayWithWallet && setPaymentMethod('wallet')}
                                        className={`relative p-4 border-2 rounded-xl cursor-pointer transition-all ${paymentMethod === 'wallet' ? 'border-emerald-600 bg-emerald-50' : 'border-gray-200 hover:border-gray-300'
                                            } ${!canPayWithWallet ? 'opacity-60 cursor-not-allowed' : ''}`}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center">
                                                <span className="text-2xl mr-3">💰</span>
                                                <div>
                                                    <div className="font-semibold text-gray-900">My Wallet</div>
                                                    <div className={`text-sm ${canPayWithWallet ? 'text-emerald-600' : 'text-red-500 font-medium'}`}>
                                                        Balance: ₦{walletBalance.toLocaleString()}
                                                    </div>
                                                </div>
                                            </div>
                                            {paymentMethod === 'wallet' && (
                                                <div className="w-5 h-5 rounded-full bg-emerald-600 flex items-center justify-center">
                                                    <div className="w-2 h-2 bg-white rounded-full" />
                                                </div>
                                            )}
                                        </div>
                                        {!canPayWithWallet && (
                                            <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                                                Insufficient balance. Please fund your wallet.
                                            </div>
                                        )}
                                    </div>

                                    {/* Paystack Option (Direct) */}
                                    {/* Hidden for MVP - Enforcing Wallet Flow for Escrow Consistency 
                            <div 
                                onClick={() => setPaymentMethod('paystack')}
                                className={`p-4 border-2 rounded-xl cursor-pointer transition-all ${
                                    paymentMethod === 'paystack' ? 'border-emerald-600 bg-emerald-50' : 'border-gray-200'
                                }`}
                            >
                                ... Paystack UI ...
                            </div> 
                            */}

                                    <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
                                        <div className="flex">
                                            <div className="ml-3">
                                                <p className="text-sm text-blue-700">
                                                    Total to Pay: <strong>₦{orderSummary.total?.toLocaleString()}</strong>
                                                </p>
                                                {/* Savings Display */}
                                                {orderSummary.you_saved > 0 && (
                                                    <p className="text-xs text-emerald-600 font-bold mt-1">
                                                        🎉 You saved ₦{orderSummary.you_saved.toLocaleString()} on service charges!
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex justify-between mt-8">
                                        <button
                                            onClick={() => setCheckoutStep('address')}
                                            className="px-6 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                                        >
                                            Back
                                        </button>
                                        <button
                                            onClick={createOrders}
                                            disabled={paymentProcessing || (paymentMethod === 'wallet' && !canPayWithWallet)}
                                            className="px-8 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-bold shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            {paymentProcessing ? 'Processing...' : `Pay ₦{orderSummary.total?.toLocaleString()}`}
                                        </button>
                                    </div>
                                    <p className="text-xs text-center text-gray-500 mt-4">
                                        Funds will be held in Escrow until you confirm delivery.
                                    </p>
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Sidebar Order Summary */}
                <div className="w-full lg:w-96 bg-gray-50 p-6 lg:p-8 border-t lg:border-t-0 lg:border-l border-gray-200 overflow-y-auto">
                    <h3 className="text-lg font-semibold text-gray-900 mb-6">Order Summary</h3>
                    <div className="space-y-4 text-sm">
                        <div className="flex justify-between">
                            <span className="text-gray-600">Subtotal ({orderSummary.item_count} items)</span>
                            <span className="font-medium text-gray-900">₦{orderSummary.product_total?.toLocaleString()}</span>
                        </div>
                        {orderSummary.platform_service_charge > 0 && (
                            <div className="flex justify-between">
                                <span className="text-gray-600">Service Charge</span>
                                <span className="font-medium text-gray-900">₦{orderSummary.platform_service_charge?.toLocaleString()}</span>
                            </div>
                        )}
                        <div className="flex justify-between">
                            <span className="text-gray-600">Delivery</span>
                            <span className="font-medium text-gray-900">₦{orderSummary.delivery_total?.toLocaleString()}</span>
                        </div>
                        {orderSummary.you_saved > 0 && (
                            <div className="flex justify-between text-emerald-600 font-medium py-2 border-t border-dashed border-emerald-200 mt-2">
                                <span>Savings</span>
                                <span>- ₦{orderSummary.you_saved?.toLocaleString()}</span>
                            </div>
                        )}
                        <div className="pt-4 border-t border-gray-200">
                            <div className="flex justify-between text-lg font-bold">
                                <span className="text-gray-900">Total</span>
                                <span className="text-emerald-600">₦{orderSummary.total?.toLocaleString()}</span>
                            </div>
                        </div>
                    </div>

                    {/* Shipping To Preview */}
                    {checkoutStep !== 'review' && (addressMode !== 'pickup' ? shippingAddress.full_name : selectedPickupLocation) && (
                        <div className="mt-8 pt-8 border-t border-gray-200">
                            <h4 className="font-medium text-gray-900 mb-3">Shipping To</h4>
                            {addressMode === 'pickup' ? (
                                <div className="bg-white p-3 rounded border border-gray-200 text-gray-600">
                                    <span className="block text-xs uppercase text-gray-400 mb-1">Pickup Station</span>
                                    {selectedPickupLocation}
                                </div>
                            ) : (
                                <div className="text-gray-600 text-sm">
                                    <div className="font-medium text-gray-900">{shippingAddress.full_name}</div>
                                    <div>{shippingAddress.address_line_1}</div>
                                    <div>{shippingAddress.city}, {shippingAddress.state}</div>
                                    <div className="mt-1 text-gray-500">{shippingAddress.phone}</div>
                                </div>
                            )}
                        </div>
                    )}
                </div>

            </div >
        </div >
    );
};

export default CheckoutModal;
