import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import '../../App.css';

const RequestWizard = ({ isOpen, onClose, onSubmit, userProfile, initialType = null, editData = null }) => {
    const [step, setStep] = useState(initialType ? 2 : 1);
    const [requestType, setRequestType] = useState(initialType); // 'instant' | 'standard'

    // Form States
    const [title, setTitle] = useState('');
    const [items, setItems] = useState([{ name: '', quantity: '', unit: '', specifications: '' }]); // Multi for Instant, Single for Standard
    const [deliveryDays, setDeliveryDays] = useState(2); // Standard (Days)
    const [deliveryHours, setDeliveryHours] = useState(4); // Instant (Hours)
    const [publishDate, setPublishDate] = useState(''); // When to publish
    const [expiryDate, setExpiryDate] = useState(''); // When request ends
    const [location, setLocation] = useState(userProfile?.state || '');
    const [contactPhone, setContactPhone] = useState(userProfile?.phone || ''); // Added Phone Field for Instant

    // Review/Payment State
    const [isLoading, setIsLoading] = useState(false);
    const [paymentData, setPaymentData] = useState(null); // { reference, amount, message }

    // Price Estimation State
    const [priceEstimates, setPriceEstimates] = useState({}); // { itemIndex: { average_price, price_range } }
    const [loadingPrices, setLoadingPrices] = useState({});

    // Reset or Initialize when opening
    useEffect(() => {
        if (isOpen) {
            setPaymentData(null);
            if (editData) {
                setStep(2);
                setRequestType(editData.type);
                setTitle(editData.notes || '');
                setItems(editData.items && editData.items.length > 0 ? editData.items : [{ name: '', quantity: '', unit: '', specifications: '' }]);
                setLocation(editData.location || editData.region_state || userProfile?.state || '');
                setContactPhone(editData.contact_phone || userProfile?.phone || '');

                if (editData.publish_date) {
                    const pd = new Date(editData.publish_date);
                    setPublishDate(new Date(pd.getTime() - pd.getTimezoneOffset() * 60000).toISOString().slice(0, 16));
                } else {
                    setPublishDate('');
                }

                if (editData.expiry_date) {
                    const ed = new Date(editData.expiry_date);
                    setExpiryDate(new Date(ed.getTime() - ed.getTimezoneOffset() * 60000).toISOString().slice(0, 16));
                } else {
                    const defaultExpiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
                    setExpiryDate(new Date(defaultExpiry.getTime() - defaultExpiry.getTimezoneOffset() * 60000).toISOString().slice(0, 16));
                }
            } else {
                setStep(initialType ? 2 : 1);
                setRequestType(initialType);
                setItems([{ name: '', quantity: '', unit: '', specifications: '' }]);
                setTitle('');
                setPublishDate('');
                const defaultExpiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
                setExpiryDate(new Date(defaultExpiry.getTime() - defaultExpiry.getTimezoneOffset() * 60000).toISOString().slice(0, 16));
            }
        }
    }, [isOpen, editData, initialType, userProfile]);

    const handleAddItem = () => {
        setItems([...items, { name: '', quantity: '', unit: '', specifications: '' }]);
    };

    const handleRemoveItem = (index) => {
        const newItems = items.filter((_, i) => i !== index);
        setItems(newItems);
    };

    const handleItemChange = (index, field, value) => {
        const newItems = [...items];
        newItems[index][field] = value;
        setItems(newItems);

        // Fetch price estimate when item name changes (for instant requests only)
        if (field === 'name' && value.length > 2 && requestType === 'instant') {
            fetchPriceEstimate(index, value);
        }
    };

    const fetchPriceEstimate = async (itemIndex, itemName) => {
        setLoadingPrices(prev => ({ ...prev, [itemIndex]: true }));
        try {
            const response = await api.get(`/products/recent-prices?name=${encodeURIComponent(itemName)}`);
            if (response.data.status === 'available') {
                setPriceEstimates(prev => ({
                    ...prev,
                    [itemIndex]: {
                        average_price: response.data.average_price,
                        price_range: response.data.price_range,
                        sample_count: response.data.sample_count
                    }
                }));
            } else {
                // Clear estimate if no data
                setPriceEstimates(prev => {
                    const newEstimates = { ...prev };
                    delete newEstimates[itemIndex];
                    return newEstimates;
                });
            }
        } catch (error) {
            console.log('Price estimation unavailable:', error);
            // Clear estimate on error
            setPriceEstimates(prev => {
                const newEstimates = { ...prev };
                delete newEstimates[itemIndex];
                return newEstimates;
            });
        } finally {
            setLoadingPrices(prev => ({ ...prev, [itemIndex]: false }));
        }
    };

    const calculateEstimatedTotal = () => {
        if (requestType === 'standard') return 0; // Standard has no budget estimate usually
        return items.reduce((sum, item, idx) => {
            const price = priceEstimates[idx]?.average_price || 0;
            const qty = parseFloat(item.quantity) || 1;
            return sum + (price * qty);
        }, 0);
    };

    const preparePayment = async () => {
        setIsLoading(true);
        try {
            // Call backend to initialize payment
            const response = await api.post('/requests/initialize-payment', {
                type: requestType,
                items: items.map(i => ({
                    name: i.name,
                    quantity: parseFloat(i.quantity) || 1,
                    unit: i.unit,
                    specifications: i.specifications
                })),
                estimated_budget: calculateEstimatedTotal()
            });

            const { payment_url, payment_reference, amount, service_charge, agent_fee, breakdown } = response.data;

            // Store payment data for display
            setPaymentData({
                estimated_total_price: calculateEstimatedTotal(),
                service_charge: service_charge,
                agent_fee: agent_fee,
                amount_to_pay: amount,
                payment_reference: payment_reference,
                payment_url: payment_url,
                email: userProfile?.email || 'customer@example.com'
            });

            setStep(4); // Move to Payment Step
        } catch (error) {
            console.error('Payment initialization failed:', error);
            alert(error.response?.data?.detail || 'Failed to initialize payment. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };


    const handleSuccessPayment = async (reference) => {
        setIsLoading(true);
        try {
            const payload = {
                type: requestType,
                items: items.map(i => ({
                    name: i.name,
                    quantity: i.quantity ? parseFloat(i.quantity) : 1,
                    unit: i.unit || 'units',
                    specifications: i.specifications || null,
                    moisture_content_percent: i.moisture_content_percent ? parseFloat(i.moisture_content_percent) : null
                })),
                location: location,
                region_country: 'Nigeria',
                region_state: location,
                contact_phone: contactPhone,
                notes: title || null,
                price_range_min: items[0]?.price_range_min ? parseFloat(items[0].price_range_min) : null,
                price_range_max: items[0]?.price_range_max ? parseFloat(items[0].price_range_max) : null,
                currency: 'NGN',
                // Payment Data — backend will verify this reference with Paystack
                payment_reference: reference,
                amount_paid: paymentData.amount_to_pay,
                estimated_budget: paymentData.estimated_total_price || 0,
                // Conditional fields
                ...(requestType === 'instant'
                    ? { delivery_days: Math.ceil(parseInt(deliveryHours) / 24) || 1 }
                    : { delivery_days: parseInt(deliveryDays) }),
                publish_date: publishDate ? new Date(publishDate).toISOString() : null,
                expiry_date: new Date(expiryDate).toISOString()
            };


            // Call verify-payment: backend verifies with Paystack then creates request atomically
            const response = await api.post('/requests/verify-payment', payload);

            alert("Payment confirmed! Your request is now live. Agents & businesses will bid shortly.");
            onSubmit(response.data);
            onClose();

        } catch (error) {
            console.error("Request creation failed:", error);
            alert(error.response?.data?.detail || "Payment verification failed. Please contact support if payment was deducted.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleEditSubmit = async () => {
        if (!expiryDate) {
            alert("Please select an expiry date.");
            return;
        }
        setIsLoading(true);
        try {
            const payload = {
                items: items.map(i => ({
                    name: i.name,
                    quantity: i.quantity ? parseFloat(i.quantity) : 1,
                    unit: i.unit || 'units',
                    specifications: i.specifications || null,
                    moisture_content_percent: i.moisture_content_percent ? parseFloat(i.moisture_content_percent) : null
                })),
                location: location,
                region_state: location,
                contact_phone: contactPhone,
                notes: title || null,
                publish_date: publishDate ? new Date(publishDate).toISOString() : null,
                expiry_date: new Date(expiryDate).toISOString()
            };

            await api.put(`/requests/${editData.id}`, payload);
            alert("Request updated successfully!");
            onSubmit();
            onClose();
        } catch (error) {
            console.error("Failed to update request:", error);
            alert(error.response?.data?.detail || "Failed to update request.");
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-content" style={{ maxWidth: '800px', width: '90%' }}>
                <div className="modal-header">
                    <h3>{editData ? 'Edit Request' : 'Create New Request'}</h3>
                    <button className="close-button" onClick={onClose}>&times;</button>
                </div>

                <div className="modal-body">
                    {/* Stepper (Hidden in Edit Mode) */}
                    {!editData && (
                        <div className="wizard-progress" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
                            <span style={step === 1 ? { color: '#2ecc71', fontWeight: 'bold' } : { color: '#ccc' }}>1. Type</span>
                            <span style={step === 2 ? { color: '#2ecc71', fontWeight: 'bold' } : { color: '#ccc' }}>2. Details</span>
                            <span style={step === 3 ? { color: '#2ecc71', fontWeight: 'bold' } : { color: '#ccc' }}>3. Review</span>
                            <span style={step === 4 ? { color: '#2ecc71', fontWeight: 'bold' } : { color: '#ccc' }}>4. Pay Fee</span>
                        </div>
                    )}

                    {/* Step 1: Type Selection */}
                    {step === 1 && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div
                                className={`p-6 border rounded-lg cursor-pointer transition-all ${requestType === 'standard' ? 'border-green-500 bg-green-50 shadow-md' : 'border-gray-200 hover:border-green-300'}`}
                                onClick={() => setRequestType('standard')}
                            >
                                <h4 className="text-xl font-bold mb-2">Standard Request</h4>
                                <p className="text-sm text-gray-600 mb-4">Post a single commodity. Get competitive bids from verified farmers & agents. Best for bulk.</p>
                                <ul className="text-xs text-gray-500 list-disc pl-4 space-y-1">
                                    <li>Delivery: 2 days - 2 weeks</li>
                                    <li>Agents bid with proof</li>
                                    <li>Tiered Service Charge</li>
                                </ul>
                            </div>

                            <div
                                onClick={() => { }} // Disabled
                                className={`p-6 border rounded-lg relative overflow-hidden bg-gray-50 border-gray-200 cursor-not-allowed opacity-75`}
                            >
                                <div className="absolute top-3 right-3 bg-yellow-500 text-white text-xs font-bold px-2 py-1 rounded-full z-10">
                                    COMING SOON
                                </div>
                                <h4 className="text-xl font-bold mb-2 text-gray-500">Instant Request ⚡</h4>
                                <p className="text-sm text-gray-500 mb-4">Buy directly from warehouses at affordable market prices to pick up now or later.</p>
                                <ul className="text-xs text-gray-500 list-disc pl-4 space-y-1">
                                    <li>Delivery: 2 - 12 Hours</li>
                                    <li>System-generated Price</li>
                                    <li>Multi-item support</li>
                                    <li>5% Service Charge</li>
                                </ul>
                            </div>

                            <div className="col-span-1 md:col-span-2 text-right mt-4">
                                <button
                                    className="btn-primary"
                                    disabled={!requestType}
                                    onClick={() => requestType && setStep(2)}
                                >
                                    Next &rarr;
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 2: Details */}
                    {step === 2 && (
                        <div>
                            <div className="mb-4">
                                <label>Description / Other Details</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder={requestType === 'instant' ? "Quick Grocery Restock" : "Bulk Onions Supply — specify grade, packaging, etc."}
                                />
                            </div>

                            {/* Items */}
                            <div className="mb-4">
                                <div className="flex justify-between items-center mb-2">
                                    <label>Items Needed</label>
                                    {requestType === 'instant' && (
                                        <button className="text-sm text-green-600" onClick={handleAddItem}>+ Add Item</button>
                                    )}
                                </div>

                                {items.map((item, idx) => (
                                    <div key={idx} className="mb-3">
                                        <div className="flex gap-2 flex-wrap">
                                            <input
                                                placeholder="Item Name (e.g. Onions)"
                                                className="form-input flex-2"
                                                style={{ minWidth: '140px' }}
                                                value={item.name}
                                                onChange={(e) => handleItemChange(idx, 'name', e.target.value)}
                                            />
                                            <input
                                                type="number"
                                                placeholder="Qty"
                                                className="form-input"
                                                style={{ width: '70px' }}
                                                value={item.quantity}
                                                onChange={(e) => handleItemChange(idx, 'quantity', e.target.value)}
                                            />
                                            {/* Unit Dropdown */}
                                            <select
                                                className="form-input"
                                                style={{ width: '150px' }}
                                                value={item.unit}
                                                onChange={(e) => handleItemChange(idx, 'unit', e.target.value)}
                                            >
                                                <option value="">Unit</option>
                                                {['Tonnes', 'Crates', 'Baskets', 'Barrels', 'Bags (50kg)', 'Bags (25kg)',
                                                    'Truck (6-wheeler)', 'Truck (10-wheeler)', 'Truck (12-wheeler)', 'Truck (14-wheeler)', 'Custom'].map(u => (
                                                        <option key={u} value={u}>{u}</option>
                                                    ))}
                                            </select>
                                            {requestType === 'instant' && items.length > 1 && (
                                                <button onClick={() => handleRemoveItem(idx)} className="text-red-500 px-2">&times;</button>
                                            )}
                                        </div>
                                        {/* Moisture Content (Standard only) */}
                                        {requestType === 'standard' && (
                                            <div className="mt-2 flex items-center gap-2">
                                                <input
                                                    type="number"
                                                    placeholder="Moisture Content % (optional)"
                                                    className="form-input"
                                                    style={{ width: '220px' }}
                                                    value={item.moisture_content_percent || ''}
                                                    onChange={(e) => handleItemChange(idx, 'moisture_content_percent', e.target.value)}
                                                />
                                                <span className="text-xs text-gray-400">e.g. 12.5%</span>
                                            </div>
                                        )}
                                        {/* Price estimate (Instant) */}
                                        {requestType === 'instant' && item.name && (
                                            <div className="mt-1 ml-1 text-sm">
                                                {loadingPrices[idx] ? (
                                                    <span className="text-gray-400">💭 Checking prices...</span>
                                                ) : priceEstimates[idx] ? (
                                                    <div className="text-green-600">
                                                        💰 Est. Price: ₦{priceEstimates[idx].average_price.toLocaleString()}/{item.unit || 'unit'}
                                                        <span className="text-gray-500 ml-2">
                                                            (₦{priceEstimates[idx].price_range.min.toLocaleString()} - ₦{priceEstimates[idx].price_range.max.toLocaleString()})
                                                        </span>
                                                    </div>
                                                ) : item.name.length > 2 ? (
                                                    <span className="text-gray-400">ℹ️ No recent price data</span>
                                                ) : null}
                                            </div>
                                        )}
                                    </div>
                                ))}
                                {requestType === 'standard' && <p className="text-xs text-gray-500">Standard requests are for a single commodity type.</p>}
                            </div>

                            {/* Region */}
                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label>Country</label>
                                    <input className="form-input" value="Nigeria" readOnly style={{ background: '#f5f5f5', color: '#888' }} />
                                </div>
                                <div>
                                    <label>State *</label>
                                    <select
                                        className="form-input"
                                        value={location}
                                        onChange={(e) => setLocation(e.target.value)}
                                    >
                                        <option value="">Select State</option>
                                        {['Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno', 'Cross River',
                                            'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo', 'Jigawa', 'Kaduna', 'Kano',
                                            'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun',
                                            'Oyo', 'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'].map(s => (
                                                <option key={s} value={s}>{s}</option>
                                            ))}
                                    </select>
                                </div>
                            </div>

                            {/* Delivery Address + Phone */}
                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label>Specific Delivery Address</label>
                                    <input
                                        className="form-input"
                                        value={location}
                                        onChange={(e) => setLocation(e.target.value)}
                                        placeholder="Street / Area / City"
                                    />
                                </div>
                                <div>
                                    <label>Contact Phone</label>
                                    <input
                                        className="form-input"
                                        value={contactPhone}
                                        onChange={(e) => setContactPhone(e.target.value)}
                                        placeholder="+234..."
                                    />
                                </div>
                            </div>

                            {/* Price Range (Standard only) */}
                            {requestType === 'standard' && (
                                <div className="grid grid-cols-3 gap-4 mb-4">
                                    <div>
                                        <label>Budget Min (₦) <span className="text-gray-400 text-xs">optional</span></label>
                                        <input
                                            type="number"
                                            className="form-input"
                                            value={items[0]?.price_range_min || ''}
                                            onChange={(e) => handleItemChange(0, 'price_range_min', e.target.value)}
                                            placeholder="0"
                                        />
                                    </div>
                                    <div>
                                        <label>Budget Max (₦) <span className="text-gray-400 text-xs">optional</span></label>
                                        <input
                                            type="number"
                                            className="form-input"
                                            value={items[0]?.price_range_max || ''}
                                            onChange={(e) => handleItemChange(0, 'price_range_max', e.target.value)}
                                            placeholder="0"
                                        />
                                    </div>
                                    <div>
                                        <label>Currency</label>
                                        <input className="form-input" value="NGN" readOnly style={{ background: '#f5f5f5', color: '#888' }} />
                                    </div>
                                </div>
                            )}

                            {/* Delivery Timeline */}
                            <div className="mb-4">
                                {requestType === 'instant' ? (
                                    <>
                                        <label>Needed Within (Hours)</label>
                                        <div className="flex items-center gap-2">
                                            <input
                                                type="range" min="2" max="12"
                                                value={deliveryHours}
                                                onChange={(e) => setDeliveryHours(e.target.value)}
                                                className="w-full"
                                            />
                                            <span className="font-bold">{deliveryHours}h</span>
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <label>Delivery Timeline (Days)</label>
                                        <input
                                            type="number" min="2"
                                            className="form-input"
                                            value={deliveryDays}
                                            onChange={(e) => setDeliveryDays(e.target.value)}
                                            placeholder="e.g. 14"
                                        />
                                        <small className="text-gray-400">Minimum 2 days for standard requests</small>
                                    </>
                                )}
                            </div>

                            {/* Scheduling & Execution */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label>Publish Date (Optional)</label>
                                    <input
                                        type="datetime-local"
                                        className="form-input"
                                        value={publishDate}
                                        onChange={(e) => setPublishDate(e.target.value)}
                                    />
                                    <small className="text-gray-400">Leave empty to publish now</small>
                                </div>
                                <div>
                                    <label>Expiry Date *</label>
                                    <input
                                        type="datetime-local"
                                        className="form-input"
                                        value={expiryDate}
                                        onChange={(e) => setExpiryDate(e.target.value)}
                                        required
                                    />
                                    <small className="text-gray-400">When should bids close?</small>
                                </div>
                            </div>

                            <div className="flex justify-between mt-6">
                                {!editData && <button className="btn-secondary" onClick={() => setStep(1)}>&larr; Back</button>}
                                {editData ? (
                                    <button className="btn-primary" style={{ marginLeft: 'auto' }} onClick={handleEditSubmit} disabled={isLoading}>
                                        {isLoading ? 'Saving...' : 'Save Changes'}
                                    </button>
                                ) : (
                                    <button className="btn-primary" style={{ marginLeft: !editData && step === 2 ? 'auto' : '0' }} onClick={() => {
                                        if (!expiryDate) { alert('Please select an expiry date.'); return; }
                                        setStep(3)
                                    }}>Next &rarr;</button>
                                )}
                            </div>
                        </div>
                    )}


                    {/* Step 3: Review */}
                    {step === 3 && (
                        <div className="text-center">
                            <h4 className="text-lg font-bold mb-4">Review Your {requestType === 'instant' ? 'Instant' : 'Standard'} Request</h4>

                            <div className="bg-gray-50 p-4 rounded-lg text-left mb-6">
                                <p><strong>Title:</strong> {title}</p>
                                <p><strong>Items:</strong> {items.length} items</p>
                                <ul className="list-disc pl-5 mb-2">
                                    {items.map((i, idx) => (
                                        <li key={idx} className="text-sm">{i.quantity} {i.unit} {i.name}</li>
                                    ))}
                                </ul>
                                <p><strong>Delivery:</strong> {requestType === 'instant' ? `${deliveryHours} Hours` : `${deliveryDays} Days`}</p>
                                <p><strong>Location:</strong> {location}</p>
                            </div>

                            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-6">
                                <p className="text-sm text-blue-800">
                                    <strong>Note:</strong> You will be required to pay a Service Charge to activate this request.
                                    The actual cost of goods is paid on delivery.
                                    {requestType === 'instant' ? (
                                        <>
                                            <br /><br />
                                            <strong>🚚 Delivery Fee:</strong> This estimate covers <strong>Goods Only</strong>.
                                            Standard delivery rates apply and will be added to your total on delivery.
                                        </>
                                    ) : ' Agents will bid competitively.'}
                                </p>
                            </div>

                            <div className="flex justify-between">
                                <button className="btn-secondary" onClick={() => setStep(2)}>&larr; Back</button>
                                <button
                                    className="btn-primary"
                                    onClick={preparePayment}
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Processing...' : 'Proceed to Payment'}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 4: Payment */}
                    {step === 4 && paymentData && (
                        <div className="text-center py-6">
                            <div className="text-green-500 text-5xl mb-4">💳</div>
                            <h4 className="text-2xl font-bold mb-2">Activate Your Request</h4>
                            <p className="text-gray-600 mb-6">Service Charge & Agent Allocation Fee</p>

                            <div className="bg-gray-100 p-6 rounded-lg max-w-sm mx-auto mb-8 text-left">
                                <div className="flex justify-between mb-2">
                                    <span>Estimated Goods Budget:</span>
                                    <span className="font-bold">₦{paymentData.estimated_total_price?.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between mb-1 text-gray-700">
                                    <span>Platform Service Charge:</span>
                                    <span>₦{paymentData.service_charge?.toLocaleString()}</span>
                                </div>
                                {requestType === 'instant' && (
                                    <div className="flex justify-between mb-1 text-gray-700">
                                        <span>Agent Allocation Fee (4%):</span>
                                        <span>₦{paymentData.agent_fee?.toLocaleString()}</span>
                                    </div>
                                )}
                                <hr className="my-2" />
                                <div className="flex justify-between mb-2 text-green-600 font-bold text-lg">
                                    <span>Total To Pay Now:</span>
                                    <span>₦{paymentData.amount_to_pay?.toLocaleString()}</span>
                                </div>
                                <div className="text-xs text-orange-600 mt-2 italic">
                                    * Goods cost is paid separately on delivery.
                                </div>
                            </div>

                            <button
                                className="bg-green-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-green-700 w-full max-w-sm"
                                onClick={() => {
                                    // Use backend-generated payment reference
                                    const PaystackPop = window.PaystackPop;
                                    if (PaystackPop && paymentData.payment_reference) {
                                        const paystack = new PaystackPop();
                                        paystack.newTransaction({
                                            key: process.env.REACT_APP_PAYSTACK_PUBLIC_KEY,
                                            email: paymentData.email,
                                            amount: paymentData.amount_to_pay * 100, // Kobo
                                            ref: paymentData.payment_reference, // Use backend reference
                                            onSuccess: (transaction) => {
                                                handleSuccessPayment(paymentData.payment_reference);
                                            },
                                            onCancel: () => {
                                                alert("Payment Cancelled");
                                            }
                                        });
                                    } else if (paymentData.payment_url) {
                                        // Redirect to Paystack checkout page
                                        window.location.href = paymentData.payment_url;
                                    } else {
                                        alert('Payment initialization failed. Please try again.');
                                    }
                                }}
                            >
                                Pay ₦{paymentData.amount_to_pay?.toLocaleString()} Securely
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RequestWizard;
