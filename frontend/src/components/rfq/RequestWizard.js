import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import '../../App.css';

const RequestWizard = ({ isOpen, onClose, onSubmit, userProfile, initialType = null }) => {
    const [step, setStep] = useState(initialType ? 2 : 1);
    const [requestType, setRequestType] = useState(initialType); // 'instant' | 'standard'

    // Form States
    const [title, setTitle] = useState('');
    const [items, setItems] = useState([{ name: '', quantity: '', unit: '', specifications: '' }]); // Multi for Instant, Single for Standard
    const [deliveryDays, setDeliveryDays] = useState(2); // Standard (Days)
    const [deliveryHours, setDeliveryHours] = useState(4); // Instant (Hours)
    const [location, setLocation] = useState(userProfile?.state || '');

    // Review/Payment State
    const [isLoading, setIsLoading] = useState(false);
    const [paymentData, setPaymentData] = useState(null); // { reference, amount, message }

    // Price Estimation State
    const [priceEstimates, setPriceEstimates] = useState({}); // { itemIndex: { average_price, price_range } }
    const [loadingPrices, setLoadingPrices] = useState({});

    // Reset when opening
    useEffect(() => {
        if (isOpen) {
            setStep(initialType ? 2 : 1);
            setRequestType(initialType);
            setPaymentData(null);
            setItems([{ name: '', quantity: '', unit: '', specifications: '' }]);
            setTitle('');
        }
    }, [isOpen]);

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

    const handleCreateRequest = async () => {
        setIsLoading(true);
        try {
            const payload = {
                request_type: requestType,
                title: title || `${requestType === 'instant' ? 'Instant' : 'Standard'} Request for ${items[0].name}`,
                items: items.map(i => ({
                    ...i,
                    quantity: i.quantity ? parseFloat(i.quantity) : 1 // Default to 1 if empty?
                })),
                location,
                unit_of_measure: items[0].unit || "mixed",
                persona: "Business",
                business_category: userProfile?.business_category || "General",
                // Conditional fields
                ...(requestType === 'instant' ? { delivery_hours: parseInt(deliveryHours) } : { delivery_days: parseInt(deliveryDays) })
            };

            const response = await api.post('/requests', payload);

            if (response.data.status === 'pending_payment') {
                setPaymentData(response.data);
                setStep(4); // Move to Payment Step
            } else {
                // Should not happen with new logic, but fallback
                onSubmit(response.data);
                onClose();
            }
        } catch (error) {
            console.error("Request creation failed:", error);
            alert(error.response?.data?.detail || "Failed to create request");
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-content" style={{ maxWidth: '800px', width: '90%' }}>
                <div className="modal-header">
                    <h3>Create New Request</h3>
                    <button className="close-button" onClick={onClose}>&times;</button>
                </div>

                <div className="modal-body">
                    {/* Stepper */}
                    <div className="wizard-progress" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
                        <span style={step === 1 ? { color: '#2ecc71', fontWeight: 'bold' } : { color: '#ccc' }}>1. Type</span>
                        <span style={step === 2 ? { color: '#2ecc71', fontWeight: 'bold' } : { color: '#ccc' }}>2. Details</span>
                        <span style={step === 3 ? { color: '#2ecc71', fontWeight: 'bold' } : { color: '#ccc' }}>3. Review</span>
                        <span style={step === 4 ? { color: '#2ecc71', fontWeight: 'bold' } : { color: '#ccc' }}>4. Pay Fee</span>
                    </div>

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
                                className={`p-6 border rounded-lg cursor-pointer transition-all ${requestType === 'instant' ? 'border-green-500 bg-green-50 shadow-md' : 'border-gray-200 hover:border-green-300'}`}
                                onClick={() => setRequestType('instant')}
                            >
                                <h4 className="text-xl font-bold mb-2">Instant Request ⚡</h4>
                                <p className="text-sm text-gray-600 mb-4">Need it NOW? PyExpress agents will pick up and deliver immediately. Fixed market pricing.</p>
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
                                <label>Request Title</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder={requestType === 'instant' ? "Quick Grocery Restock" : "Bulk Onions Supply"}
                                />
                            </div>

                            <div className="mb-4">
                                <div className="flex justify-between items-center mb-2">
                                    <label>Items Needed</label>
                                    {requestType === 'instant' && (
                                        <button className="text-sm text-green-600" onClick={handleAddItem}>+ Add Item</button>
                                    )}
                                </div>

                                {items.map((item, idx) => (
                                    <div key={idx} className="mb-3">
                                        <div className="flex gap-2">
                                            <input
                                                placeholder="Item Name"
                                                className="form-input flex-2"
                                                value={item.name}
                                                onChange={(e) => handleItemChange(idx, 'name', e.target.value)}
                                            />
                                            <input
                                                type="number"
                                                placeholder="Qty"
                                                className="form-input w-20"
                                                value={item.quantity}
                                                onChange={(e) => handleItemChange(idx, 'quantity', e.target.value)}
                                            />
                                            <input
                                                placeholder="Unit"
                                                className="form-input w-24"
                                                value={item.unit}
                                                onChange={(e) => handleItemChange(idx, 'unit', e.target.value)}
                                            />
                                            {requestType === 'instant' && items.length > 1 && (
                                                <button onClick={() => handleRemoveItem(idx)} className="text-red-500 px-2">&times;</button>
                                            )}
                                        </div>

                                        {/* Price Estimate Display */}
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
                                                        <span className="text-xs text-gray-400 ml-2">
                                                            Based on {priceEstimates[idx].sample_count} recent orders
                                                        </span>
                                                    </div>
                                                ) : item.name.length > 2 ? (
                                                    <span className="text-gray-400">ℹ️ No recent price data available</span>
                                                ) : null}
                                            </div>
                                        )}
                                    </div>
                                ))}
                                {requestType === 'standard' && <p className="text-xs text-gray-500">Standard requests are limited to 1 item type per request.</p>}
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label>Location</label>
                                    <input
                                        className="form-input"
                                        value={location}
                                        onChange={(e) => setLocation(e.target.value)}
                                        placeholder="Delivery Address"
                                    />
                                </div>
                                <div>
                                    {requestType === 'instant' ? (
                                        <>
                                            <label>Needed Within (Hours)</label>
                                            <div className="flex items-center gap-2">
                                                <input
                                                    type="range"
                                                    min="2" max="12"
                                                    value={deliveryHours}
                                                    onChange={(e) => setDeliveryHours(e.target.value)}
                                                    className="w-full"
                                                />
                                                <span className="font-bold">{deliveryHours}h</span>
                                            </div>
                                        </>
                                    ) : (
                                        <>
                                            <label>Needed Within (Days)</label>
                                            <input
                                                type="number"
                                                min="2"
                                                className="form-input"
                                                value={deliveryDays}
                                                onChange={(e) => setDeliveryDays(e.target.value)}
                                            />
                                        </>
                                    )}
                                </div>
                            </div>

                            <div className="flex justify-between mt-6">
                                <button className="btn-secondary" onClick={() => setStep(1)}>&larr; Back</button>
                                <button className="btn-primary" onClick={() => setStep(3)}>Next &rarr;</button>
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
                                    onClick={handleCreateRequest}
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Creating...' : 'Create & Proceed to Payment'}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 4: Payment */}
                    {step === 4 && paymentData && (
                        <div className="text-center py-6">
                            <div className="text-green-500 text-5xl mb-4">💳</div>
                            <h4 className="text-2xl font-bold mb-2">Service Charge Payment</h4>
                            <p className="text-gray-600 mb-6">Please complete the payment to activate your request.</p>

                            <div className="bg-gray-100 p-6 rounded-lg max-w-sm mx-auto mb-8">
                                <div className="flex justify-between mb-2">
                                    <span>Estimated Goods Value:</span>
                                    <span className="font-bold">₦{paymentData.estimated_total_price?.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between mb-2 text-blue-600 font-bold">
                                    <span>Service Charge:</span>
                                    <span>₦{paymentData.amount_to_pay?.toLocaleString()}</span>
                                </div>
                                <div className="text-xs text-orange-600 mt-2 italic">
                                    * Delivery fee not included. Paid on delivery.
                                </div>
                                <hr className="my-2" />
                                <div className="text-xs text-gray-500">
                                    Payment Reference: <br />
                                    <code className="bg-white px-2 py-1 rounded border">{paymentData.payment_reference}</code>
                                </div>
                            </div>

                            <button
                                className="bg-green-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-green-700 w-full max-w-sm"
                                onClick={() => {
                                    // In a real app, this triggers Paystack Modal
                                    // For MVP/Demo, alert user
                                    alert(`Starting Paystack Payment for Ref: ${paymentData.payment_reference}\nAmount: ₦${paymentData.amount_to_pay}`);
                                    alert("Payment Simulated! Reference verified.");

                                    // Simulate Webhook / Success
                                    onClose(); // Close Wizard
                                    onSubmit(); // Refresh parent
                                }}
                            >
                                Pay Now (Paystack)
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RequestWizard;
