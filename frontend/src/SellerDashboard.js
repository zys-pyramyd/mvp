import React, { useState, useEffect } from 'react';
import { NIGERIAN_STATES } from './nigerianStates';

const SellerDashboard = ({ user, token, onOpenChat }) => {
    const [activeTab, setActiveTab] = useState('overview'); // overview, farmers, deliveries, inventory
    const [stats, setStats] = useState(null);
    const [farmers, setFarmers] = useState([]);
    const [deliveries, setDeliveries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddProduct, setShowAddProduct] = useState(false);
    const [deliveryCode, setDeliveryCode] = useState(null);
    const [deliveryBuyer, setDeliveryBuyer] = useState(null);
    const [showDeliveryCodeModal, setShowDeliveryCodeModal] = useState(false);

    useEffect(() => {
        fetchInitialData();
    }, [activeTab]);

    const fetchInitialData = async () => {
        setLoading(true);
        try {
            // Fetch Overview Stats
            if (activeTab === 'overview' && !stats) {
                const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/seller/dashboard/analytics`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) setStats(await res.json());
            }

            // Fetch Farmers (Agent Only)
            if (activeTab === 'farmers' && user.role === 'agent') {
                const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent/farmers`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setFarmers(data.farmers || []);
                }
            }

            // Fetch Deliveries
            if (activeTab === 'deliveries') {
                const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent/deliveries`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setDeliveries(data.orders || []);
                }
            }

        } catch (e) {
            console.error("Dashboard fetch error:", e);
        } finally {
            setLoading(false);
        }
    };

    const updateDeliveryStatus = async (orderId, newStatus, notes, buyerUsername) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/delivery/status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    order_id: orderId,
                    status: newStatus,
                    notes: notes
                })
            });

            if (response.ok) {
                const data = await response.json();

                if (data.status === 'verification_pending') {
                    setDeliveryCode(data.delivery_code);
                    setDeliveryBuyer(buyerUsername);
                    setShowDeliveryCodeModal(true);
                    // Standard alert logic moved to after modal close or separate notice
                } else {
                    alert('Status updated!');
                }

                // Refresh deliveries
                const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent/deliveries`, { headers: { 'Authorization': `Bearer ${token}` } });
                const updatedData = await res.json();
                setDeliveries(updatedData.orders || []);
            } else {
                alert('Failed to update status');
            }
        } catch (error) {
            console.error(error);
            alert('Error updating status');
        }
    };

    const [showAddFarmer, setShowAddFarmer] = useState(false);

    // ... (existing fetchInitialData)

    return (
        <div className="min-h-screen bg-gray-50 p-4 md:p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                        <p className="text-gray-500 capitalize">{user.role} Control Center • @{user.username}</p>
                    </div>
                    <div className="flex gap-2">
                        {user.role === 'agent' && activeTab === 'farmers' && (
                            <button
                                onClick={() => setShowAddFarmer(true)}
                                className="bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700"
                            >
                                + Register Farmer
                            </button>
                        )}
                        <button
                            onClick={() => setShowAddProduct(true)}
                            className="bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-emerald-700"
                        >
                            + Add Product
                        </button>
                    </div>
                </div>

                {/* ... (Existing Tabs and Content) ... */}

                <div className="flex border-b bg-white rounded-t-lg px-4 overflow-x-auto">
                    <TabButton active={activeTab === 'overview'} onClick={() => setActiveTab('overview')} label="📊 Overview" />
                    {user.role === 'agent' && (
                        <TabButton active={activeTab === 'farmers'} onClick={() => setActiveTab('farmers')} label="👨‍🌾 My Farmers" />
                    )}
                    <TabButton active={activeTab === 'deliveries'} onClick={() => setActiveTab('deliveries')} label="📦 Deliveries" />
                    <TabButton active={activeTab === 'inventory'} onClick={() => setActiveTab('inventory')} label="📋 Inventory" />
                    <TabButton active={activeTab === 'wallet'} onClick={() => setActiveTab('wallet')} label="💰 My Earnings" />
                    <TabButton active={activeTab === 'account'} onClick={() => setActiveTab('account')} label="🏦 Account Settings" />
                </div>

                {/* Content Area */}
                <div className="bg-white rounded-b-lg shadow-sm p-6 min-h-[500px]">
                    {loading && <div className="text-center py-12 text-gray-500">Loading data...</div>}

                    {!loading && activeTab === 'overview' && stats && (
                        <div className="space-y-8">
                            {/* Verification Status Badge */}
                            <div className={`p-4 rounded-lg flex justify-between items-center ${user.verification_status === 'verified' ? 'bg-emerald-50 border border-emerald-200' :
                                    user.verification_status === 'pending' ? 'bg-yellow-50 border border-yellow-200' :
                                        user.verification_status === 'rejected' ? 'bg-red-50 border border-red-200' :
                                            'bg-gray-50 border border-gray-200'
                                }`}>
                                <div className="flex items-center gap-3">
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xl ${user.verification_status === 'verified' ? 'bg-emerald-100 text-emerald-600' :
                                            user.verification_status === 'pending' ? 'bg-yellow-100 text-yellow-600' :
                                                user.verification_status === 'rejected' ? 'bg-red-100 text-red-600' :
                                                    'bg-gray-200 text-gray-500'
                                        }`}>
                                        {user.verification_status === 'verified' ? '✓' :
                                            user.verification_status === 'pending' ? '⏳' :
                                                user.verification_status === 'rejected' ? '✕' : '?'}
                                    </div>
                                    <div>
                                        <h3 className={`font-bold ${user.verification_status === 'verified' ? 'text-emerald-900' :
                                                user.verification_status === 'pending' ? 'text-yellow-900' :
                                                    user.verification_status === 'rejected' ? 'text-red-900' :
                                                        'text-gray-900'
                                            }`}>
                                            Account Status: {user.verification_status ? user.verification_status.charAt(0).toUpperCase() + user.verification_status.slice(1) : 'Unverified'}
                                        </h3>
                                        {user.verification_status === 'rejected' && user.verification_note && (
                                            <p className="text-sm text-red-700 mt-1">Reason: {user.verification_note}</p>
                                        )}
                                        {user.verification_status === 'pending' && (
                                            <p className="text-sm text-yellow-700">Your documents are currently under review. This usually takes 24-48 hours.</p>
                                        )}
                                    </div>
                                </div>
                                {user.verification_status === 'rejected' && (
                                    <button
                                        onClick={() => window.location.href = '/register?mode=resubmit'} // Simple redirect to registration for re-submission
                                        className="bg-red-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-red-700"
                                    >
                                        Resubmit KYC
                                    </button>
                                )}
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <StatCard title="Total Revenue" value={`₦${stats.revenue?.total_revenue?.toLocaleString() || 0}`} subtitle="Lifetime Earnings" icon="💰" color="bg-emerald-100 text-emerald-800" />
                                <StatCard title="Total Orders" value={stats.orders?.total_orders || 0} subtitle={`${stats.orders?.completed_orders || 0} completed`} icon="🛍️" color="bg-blue-100 text-blue-800" />
                                <StatCard title="Pending Revenue" value={`₦${stats.revenue?.pending_revenue?.toLocaleString() || 0}`} subtitle="In processing" icon="⏳" color="bg-orange-100 text-orange-800" />
                            </div>
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <div className="border rounded-xl p-4">
                                    <h3 className="font-bold text-gray-800 mb-4">Recent Sales</h3>
                                    {stats.revenue?.daily_sales?.length > 0 ? (
                                        <div className="h-40 flex items-end gap-2">
                                            {stats.revenue.daily_sales.slice(-7).map((d, i) => (
                                                <div key={i} className="flex-1 bg-emerald-100 rounded-t relative group">
                                                    <div
                                                        className="absolute bottom-0 w-full bg-emerald-500 rounded-t transition-all"
                                                        style={{ height: `${(d.daily_total / (Math.max(...stats.revenue.daily_sales.map(s => s.daily_total)) || 1)) * 100}%` }}
                                                    ></div>
                                                    <div className="absolute -bottom-6 w-full text-center text-xs text-gray-500">
                                                        {new Date(d._id).getDate()}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-center py-10 text-gray-400">No sales data yet</div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {!loading && activeTab === 'farmers' && (
                        <div>
                            {/* ... (Existing Farmers List) ... */}
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-xl font-bold">Managed Farmers</h2>
                            </div>
                            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {farmers.map(farmer => (
                                    <div key={farmer.id} className="border rounded-lg p-4 flex gap-4 items-center hover:bg-gray-50 transition">
                                        <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center font-bold text-gray-600 text-lg">
                                            {farmer.first_name?.[0] || 'F'}
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-900">{farmer.first_name} {farmer.last_name}</h3>
                                            <p className="text-sm text-gray-500">@{farmer.username}</p>
                                            <div className="flex gap-3 mt-1 text-xs text-gray-600">
                                                <span>📦 {farmer.product_count} Products</span>
                                                <span>💰 ₦{farmer.total_sales.toLocaleString()} Sales</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {farmers.length === 0 && (
                                    <div className="col-span-full text-center py-12 text-gray-400">
                                        No farmers registered yet. Click "Register Farmer" to add one.
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {!loading && activeTab === 'deliveries' && (
                        <div className="space-y-4">
                            {deliveries.map(order => (
                                <DeliveryCard key={order.order_id} order={order} onUpdate={updateDeliveryStatus} />
                            ))}
                            {deliveries.length === 0 && <div className="text-center py-12 text-gray-400">No active delivery tasks.</div>}
                        </div>
                    )}

                    {!loading && activeTab === 'inventory' && (
                        <div className="text-center py-12 text-gray-400">
                            {/* List products, including those managed for farmers */}
                            <p>Manage your inventory and products here.</p>
                        </div>
                    )}

                    {!loading && activeTab === 'account' && (
                        <AccountSettings user={user} token={token} />
                    )}
                </div>

                {/* Modals */}
                {showAddProduct && (
                    <AddProductModal onClose={() => setShowAddProduct(false)} onSuccess={() => { setShowAddProduct(false); fetchInitialData(); }} token={token} />
                )}
                {showAddFarmer && (
                    <AddFarmerModal onClose={() => setShowAddFarmer(false)} onSuccess={() => { setShowAddFarmer(false); fetchInitialData(); }} token={token} />
                )}
                {showDeliveryCodeModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-60">
                        <div className="bg-white rounded-xl max-w-sm w-full p-6 text-center">
                            <h3 className="text-xl font-bold mb-2">Secure Delivery Code</h3>
                            <p className="text-gray-600 mb-4">Share this code with the buyer to confirm delivery.</p>
                            <div className="text-4xl font-mono font-bold text-emerald-600 tracking-wider mb-6 bg-emerald-50 py-4 rounded-lg border border-emerald-100">
                                {deliveryCode}
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => {
                                        // Copy to clipboard logic if needed
                                        setShowDeliveryCodeModal(false);
                                    }}
                                    className="flex-1 bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200"
                                >
                                    Close
                                </button>
                                {onOpenChat && (
                                    <button
                                        onClick={() => {
                                            onOpenChat(deliveryBuyer, `Hello, I have delivered your order. Please confirm receipt using this code: ${deliveryCode}`);
                                            setShowDeliveryCodeModal(false);
                                        }}
                                        className="flex-1 bg-emerald-600 text-white py-2 rounded-lg hover:bg-emerald-700 font-bold flex items-center justify-center gap-2"
                                    >
                                        <span>💬 Share Code</span>
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div >
    );
};

const AddFarmerModal = ({ onClose, onSuccess, token }) => {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    // Simplified Farmer Data
    const [formData, setFormData] = useState({
        first_name: '', last_name: '', phone: '', gender: '', date_of_birth: '',
        address: '', farm_size: '', farm_location: '', crops: '',
        headshot: '' // We will allow camera capture here soon
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent/farmers/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(formData)
            });
            if (res.ok) {
                alert("Farmer Registered Successfully!");
                onSuccess();
            } else {
                const err = await res.json();
                alert(err.detail || "Failed to register farmer");
            }
        } catch (e) {
            console.error(e);
            alert("Error registering farmer");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl max-w-lg w-full p-6">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Register New Farmer</h2>
                    <button onClick={onClose}>✕</button>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <input className="border p-2 rounded" placeholder="First Name" required value={formData.first_name} onChange={e => setFormData({ ...formData, first_name: e.target.value })} />
                        <input className="border p-2 rounded" placeholder="Last Name" required value={formData.last_name} onChange={e => setFormData({ ...formData, last_name: e.target.value })} />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <input className="border p-2 rounded" placeholder="Phone Number" required value={formData.phone} onChange={e => setFormData({ ...formData, phone: e.target.value })} />
                        <select className="border p-2 rounded" value={formData.gender} onChange={e => setFormData({ ...formData, gender: e.target.value })} required>
                            <option value="">Gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                        </select>
                    </div>
                    <input type="date" className="border p-2 rounded w-full" required value={formData.date_of_birth} onChange={e => setFormData({ ...formData, date_of_birth: e.target.value })} />

                    <div className="space-y-3 pt-2">
                        <h4 className="text-sm font-semibold text-gray-700">Address Details</h4>
                        <input
                            className="border p-2 rounded w-full"
                            placeholder="Address Number & Street Name"
                            required
                            value={formData.address_street || ''}
                            onChange={e => setFormData({ ...formData, address_street: e.target.value })}
                        />
                        <div className="grid grid-cols-2 gap-4">
                            <input
                                className="border p-2 rounded"
                                placeholder="City / Town"
                                required
                                value={formData.city || ''}
                                onChange={e => setFormData({ ...formData, city: e.target.value })}
                            />
                            <select
                                value={formData.state || ''}
                                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                                className="border p-2 rounded"
                                required
                            >
                                <option value="">Select State</option>
                                {["Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT - Abuja", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"].map(state => (
                                    <option key={state} value={state}>{state}</option>
                                ))}
                            </select>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <input
                                className="border p-2 rounded"
                                placeholder="Landmark (Optional)"
                                value={formData.landmark || ''}
                                onChange={e => setFormData({ ...formData, landmark: e.target.value })}
                            />
                            <input
                                className="border p-2 rounded bg-gray-100 text-gray-500"
                                value="Nigeria"
                                disabled
                            />
                        </div>
                    </div>

                    <h3 className="font-bold text-gray-700 pt-2">Farm Details</h3>
                    <input className="border p-2 rounded w-full" placeholder="Farm Location (City/State)" required value={formData.farm_location} onChange={e => setFormData({ ...formData, farm_location: e.target.value })} />
                    <div className="grid grid-cols-2 gap-4">
                        <input className="border p-2 rounded" placeholder="Size (e.g. 5 acres)" required value={formData.farm_size} onChange={e => setFormData({ ...formData, farm_size: e.target.value })} />
                        <input className="border p-2 rounded" placeholder="Main Crops (e.g. Maize)" required value={formData.crops} onChange={e => setFormData({ ...formData, crops: e.target.value })} />
                    </div>

                    <button type="submit" disabled={loading} className="w-full bg-purple-600 text-white py-3 rounded-lg font-bold hover:bg-purple-700 disabled:bg-gray-400">
                        {loading ? 'Registering...' : 'Register Farmer'}
                    </button>
                </form>
            </div>
        </div>
    );
};

const AddProductModal = ({ onClose, onSuccess, token }) => {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        category: 'grains_cereals',
        price_per_unit: '',
        unit: 'kg',
        quantity: '',
        location: '',
        city: '',
        pickup_address: '',
        country: 'Nigeria',
        seller_delivery_fee: 0,
        seller_delivery_fee: 0,
        images: [],
        farmer_id: '', // For agents
        min_order_quantity: 1,
        is_preorder: false,
        preorder_deadline: '',
        target_quantity: ''
    });
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [managedFarmers, setManagedFarmers] = useState([]); // Agents: list of farmers

    // Fetch farmers for agents
    React.useEffect(() => {
        const fetchFarmers = async () => {
            // We can reuse the same endpoint or pass it down. 
            // For modularity, let's fetch if we think we are an agent? 
            // Actually, better to check user role or passed prop 'isAgent'.
            // Let's assume we can fetch if token is present.
            try {
                const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent/farmers`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setManagedFarmers(data.farmers || []);
                }
            } catch (e) {
                console.error("Failed to fetch farmers for dropdown", e);
            }
        };
        // Simple check if we might be an agent (or just try fetching, API will reject if not)
        fetchFarmers();
    }, [token]);

    const handleFarmerSelect = (e) => {
        const farmerId = e.target.value;
        const selectedFarmer = managedFarmers.find(f => f.id === farmerId);

        setFormData(prev => ({
            ...prev,
            farmer_id: farmerId,
            // Auto-fill location from farmer if available
            location: selectedFarmer?.state || prev.location,
            city: selectedFarmer?.city || prev.city,
            pickup_address: selectedFarmer?.address || prev.pickup_address
        }));
    };

    const handleImageUpload = async (e) => {
        const files = Array.from(e.target.files);
        setUploading(true);

        try {
            const uploadedUrls = [];
            for (const file of files) {
                // 1. Get Signed URL
                const signRes = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upload/sign`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        folder: 'products',
                        filename: file.name,
                        contentType: file.type
                    })
                });

                if (!signRes.ok) throw new Error('Failed to get upload signature');
                const { uploadUrl, publicUrl } = await signRes.json();

                // 2. Upload to R2
                const uploadRes = await fetch(uploadUrl, {
                    method: 'PUT',
                    headers: { 'Content-Type': file.type },
                    body: file
                });

                if (!uploadRes.ok) throw new Error('Failed to upload image');
                uploadedUrls.push(publicUrl);
            }

            setFormData(prev => ({
                ...prev,
                images: [...prev.images, ...uploadedUrls]
            }));

        } catch (error) {
            console.error("Upload error:", error);
            alert("Failed to upload image(s)");
        } finally {
            setUploading(false);
        }
    };

    const removeImage = (index) => {
        setFormData(prev => ({
            ...prev,
            images: prev.images.filter((_, i) => i !== index)
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const payload = {
                ...formData,
                type: formData.is_preorder ? 'preorder' : 'standard'
            };

            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/products`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert('Product added successfully!');
                onSuccess();
            } else {
                const error = await response.json();
                alert(error.detail || 'Failed to add product');
            }
        } catch (error) {
            console.error(error);
            alert('Error creating product');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
            <div className="bg-white rounded-xl max-w-2xl w-full p-6 my-8">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold">Add New Product</h2>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Agent: Select Farmer */}
                    {managedFarmers.length > 0 && (
                        <div className="bg-emerald-50 p-3 rounded-lg border border-emerald-200">
                            <label className="block text-sm font-bold text-emerald-800 mb-1">Post on behalf of Farmer</label>
                            <select
                                className="w-full border rounded p-2"
                                value={formData.farmer_id}
                                onChange={handleFarmerSelect}
                            >
                                <option value="">Select Farmer (Optional - you are seller)</option>
                                {managedFarmers.map(f => (
                                    <option key={f.id} value={f.id}>{f.first_name} {f.last_name} ({f.location || 'No Loc'})</option>
                                ))}
                            </select>
                            <p className="text-xs text-emerald-600 mt-1">If selected, sales will be recorded against this farmer.</p>
                        </div>
                    )}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Product Title</label>
                            <input
                                type="text"
                                required
                                className="w-full border rounded p-2"
                                value={formData.title}
                                onChange={e => setFormData({ ...formData, title: e.target.value })}
                                placeholder="e.g. Fresh Red Tomatoes"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Category</label>
                            <select
                                className="w-full border rounded p-2"
                                value={formData.category}
                                onChange={e => setFormData({ ...formData, category: e.target.value })}
                            >
                                <option value="grains_cereals">Grains & Cereals</option>
                                <option value="tubers_roots">Tubers & Roots</option>
                                <option value="fish_meat">Fish & Meat</option>
                                <option value="spices_vegetables">Spices & Vegetables</option>
                                <option value="packaged_goods">Packaged Goods</option>
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="col-span-2">
                            <label className="block text-sm font-medium text-gray-700">Price (₦)</label>
                            <input
                                type="number"
                                required
                                className="w-full border rounded p-2"
                                value={formData.price_per_unit}
                                onChange={e => setFormData({ ...formData, price_per_unit: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Quantity</label>
                            <input
                                type="number"
                                required
                                className="w-full border rounded p-2"
                                value={formData.quantity}
                                onChange={e => setFormData({ ...formData, quantity: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Unit</label>
                            <select
                                className="w-full border rounded p-2"
                                value={formData.unit}
                                onChange={e => setFormData({ ...formData, unit: e.target.value })}
                            >
                                <option value="kg">kg</option>
                                <option value="bag">bag</option>
                                <option value="litre">litre</option>
                                <option value="basket">basket</option>
                                <option value="crate">crate</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Min. Order Qty</label>
                            <input
                                type="number"
                                min="1"
                                className="w-full border rounded p-2"
                                value={formData.min_order_quantity}
                                onChange={e => setFormData({ ...formData, min_order_quantity: e.target.value })}
                                placeholder="Default: 1"
                            />
                        </div>
                    </div>

                    {/* Pre-order Section */}
                    <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                        <div className="flex items-center gap-2 mb-3">
                            <input
                                type="checkbox"
                                id="is_preorder"
                                checked={formData.is_preorder}
                                onChange={e => setFormData({ ...formData, is_preorder: e.target.checked })}
                                className="w-4 h-4 text-orange-600 rounded"
                            />
                            <label htmlFor="is_preorder" className="font-bold text-orange-800">Enable Pre-order / Group Buy</label>
                        </div>

                        {formData.is_preorder && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Target Quantity</label>
                                    <input
                                        type="number"
                                        className="w-full border rounded p-2"
                                        value={formData.target_quantity}
                                        onChange={e => setFormData({ ...formData, target_quantity: e.target.value })}
                                        placeholder="Goal to reach"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Deadline</label>
                                    <input
                                        type="date"
                                        className="w-full border rounded p-2"
                                        value={formData.preorder_deadline}
                                        onChange={e => setFormData({ ...formData, preorder_deadline: e.target.value })}
                                    />
                                </div>
                            </div>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Product Images</label>
                        <div className="flex flex-wrap gap-2 mb-2">
                            {formData.images.map((url, i) => (
                                <div key={i} className="relative w-20 h-20 border rounded overflow-hidden">
                                    <img src={url} alt="Product" className="w-full h-full object-cover" />
                                    <button
                                        type="button"
                                        onClick={() => removeImage(i)}
                                        className="absolute top-0 right-0 bg-red-500 text-white rounded-bl p-1 text-xs"
                                    >✕</button>
                                </div>
                            ))}
                            <div className="w-20 h-20 border-2 border-dashed border-gray-300 rounded flex items-center justify-center relative hover:bg-gray-50">
                                {uploading ? (
                                    <span className="text-xs text-gray-500">Uploading...</span>
                                ) : (
                                    <>
                                        <span className="text-2xl text-gray-400">+</span>
                                        <input
                                            type="file"
                                            accept="image/*"
                                            multiple
                                            onChange={handleImageUpload}
                                            className="absolute inset-0 opacity-0 cursor-pointer"
                                        />
                                    </>
                                )}
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mb-4">First image will be the cover photo.</p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">Description</label>
                        <textarea
                            required
                            className="w-full border rounded p-2 h-24"
                            value={formData.description}
                            onChange={e => setFormData({ ...formData, description: e.target.value })}
                            placeholder="Describe your product freshness, quality, etc."
                        ></textarea>
                    </div>

                    <div className="border-t pt-4">
                        <h3 className="font-semibold text-gray-900 mb-3">Product Location</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Country</label>
                                <input
                                    type="text"
                                    value="Nigeria"
                                    disabled
                                    className="w-full border rounded p-2 bg-gray-100 text-gray-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">State</label>
                                <select
                                    required
                                    className="w-full border rounded p-2"
                                    value={formData.location}
                                    onChange={e => setFormData({ ...formData, location: e.target.value })}
                                >
                                    <option value="">Select State</option>
                                    {NIGERIAN_STATES.map(state => (
                                        <option key={state} value={state}>{state}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">City/LGA</label>
                                <input
                                    type="text"
                                    required
                                    className="w-full border rounded p-2"
                                    value={formData.city}
                                    onChange={e => setFormData({ ...formData, city: e.target.value })}
                                    placeholder="e.g. Ikeja"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Pickup Address (Optional)</label>
                                <input
                                    type="text"
                                    className="w-full border rounded p-2"
                                    value={formData.pickup_address}
                                    onChange={e => setFormData({ ...formData, pickup_address: e.target.value })}
                                    placeholder="e.g. 15 Farm Road"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-4 border-t">
                        <button type="button" onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">Cancel</button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-6 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-50"
                        >
                            {loading ? 'Posting...' : 'Post Product'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const TabButton = ({ active, onClick, label }) => (
    <button
        onClick={onClick}
        className={`px-6 py-4 font-medium text-sm transition-colors border-b-2 ${active ? 'border-emerald-600 text-emerald-700 bg-emerald-50' : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
    >
        {label}
    </button>
);

const NIGERIAN_BANKS = [
    { code: "044", name: "Access Bank" },
    { code: "023", name: "Citibank" },
    { code: "050", name: "Ecobank Nigeria" },
    { code: "070", name: "Fidelity Bank" },
    { code: "011", name: "First Bank of Nigeria" },
    { code: "214", name: "First City Monument Bank" },
    { code: "058", name: "Guaranty Trust Bank" },
    { code: "030", name: "Heritage Bank" },
    { code: "301", name: "Jaiz Bank" },
    { code: "082", name: "Keystone Bank" },
    { code: "014", name: "Mainstreet Bank" },
    { code: "076", name: "Skye Bank" },
    { code: "221", name: "Stanbic IBTC Bank" },
    { code: "068", name: "Standard Chartered Bank" },
    { code: "232", name: "Sterling Bank" },
    { code: "032", name: "Union Bank of Nigeria" },
    { code: "033", name: "United Bank for Africa" },
    { code: "215", name: "Unity Bank" },
    { code: "035", name: "Wema Bank" },
    { code: "057", name: "Zenith Bank" }
];

const AccountSettings = ({ user, token }) => {
    const [formData, setFormData] = useState({
        business_name: user?.business_name || '',
        bank_code: '',
        account_number: ''
    });
    const [loading, setLoading] = useState(false);
    const [currentAccount, setCurrentAccount] = useState(null);

    useEffect(() => {
        fetchAccountDetails();
    }, []);

    const fetchAccountDetails = async () => {
        try {
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payment/subaccount/${user.id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setCurrentAccount(data);
                if (data.bank_details) {
                    setFormData(prev => ({
                        ...prev,
                        business_name: data.bank_details.business_name || prev.business_name,
                        bank_code: data.bank_details.bank_code || '',
                        // Don't auto-fill full account number for security, user must re-enter to change
                    }));
                }
            }
        } catch (e) {
            console.error(e);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payment/subaccount`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });

            if (res.ok) {
                alert('Account details updated successfully!');
                fetchAccountDetails();
            } else {
                const err = await res.json();
                alert(err.detail || 'Failed to update account');
            }
        } catch (e) {
            console.error(e);
            alert('Error updating account');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-xl border p-6 mb-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Payout Account Settings</h2>
                <p className="text-gray-500 mb-6 font-medium">
                    Please provide your bank details to receive payments.
                    <span className="block text-xs mt-1 text-emerald-600">
                        🔒 Your details are sent securely to our payment partner (Paystack) and are not stored in plain text.
                    </span>
                </p>

                {currentAccount && currentAccount.bank_details && (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-6 flex items-start gap-3">
                        <div className="text-2xl">✅</div>
                        <div>
                            <h3 className="font-bold text-emerald-900">Active Payout Account</h3>
                            <p className="text-emerald-800 text-sm">
                                {currentAccount.bank_details.business_name}<br />
                                {NIGERIAN_BANKS.find(b => b.code === currentAccount.bank_details.bank_code)?.name || currentAccount.bank_details.bank_code} • {currentAccount.bank_details.account_number}
                            </p>
                        </div>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Business / Account Name</label>
                        <input
                            type="text"
                            required
                            className="w-full border rounded-lg p-3"
                            value={formData.business_name}
                            onChange={e => setFormData({ ...formData, business_name: e.target.value })}
                            placeholder="e.g. My Farm Ventures"
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Bank Name</label>
                            <select
                                required
                                className="w-full border rounded-lg p-3"
                                value={formData.bank_code}
                                onChange={e => setFormData({ ...formData, bank_code: e.target.value })}
                            >
                                <option value="">Select Bank</option>
                                {NIGERIAN_BANKS.map(bank => (
                                    <option key={bank.code} value={bank.code}>{bank.name}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Account Number</label>
                            <input
                                type="text"
                                required
                                maxLength="10"
                                pattern="\d{10}"
                                className="w-full border rounded-lg p-3"
                                value={formData.account_number}
                                onChange={e => setFormData({ ...formData, account_number: e.target.value.replace(/\D/g, '') })}
                                placeholder="10-digit Account Number"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-emerald-600 text-white font-bold py-3 rounded-lg hover:bg-emerald-700 transition disabled:opacity-50"
                    >
                        {loading ? 'Verifying & Saving...' : 'Save Bank Details'}
                    </button>
                </form>
            </div>
        </div>
    );
};

const StatCard = ({ title, value, subtitle, icon, color }) => (
    <div className="bg-white border rounded-xl p-5 shadow-sm flex items-center gap-4">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-2xl ${color}`}>
            {icon}
        </div>
        <div>
            <p className="text-sm text-gray-500 font-medium">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            <p className="text-xs text-gray-400">{subtitle}</p>
        </div>
    </div>
);

// Reuse DeliveryCard logic from previous dashboard or keep it simple here
const DeliveryCard = ({ order, onUpdate }) => {
    // Simplified version for the dashboard view
    const [status, setStatus] = useState(order.delivery_status || 'pending');

    return (
        <div className="border rounded-lg p-4 flex flex-col md:flex-row justify-between gap-4">
            <div>
                <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-xs text-gray-500">#{order.order_id}</span>
                </div>
                <h4 className="font-bold">{order.product_details.name} (x{order.quantity})</h4>
                <p className="text-sm text-gray-600">To: {order.buyer_username} • {order.shipping_address || 'Drop-off'}</p>
            </div>
            <div className="flex items-center gap-2">
                <select
                    value={status}
                    onChange={(e) => {
                        setStatus(e.target.value);
                        onUpdate(order.order_id, e.target.value, order.delivery_notes, order.buyer_username);
                    }}
                    className="border rounded p-2 text-sm bg-gray-50"
                >
                    <option value="pending">⏳ Pending</option>
                    <option value="ready_for_pickup">📦 Ready for Pickup</option>
                    <option value="out_for_delivery">🚚 Out for Delivery</option>
                    <option value="delivered">✅ Delivered</option>
                </select>
            </div>
        </div >
    )
}

export default SellerDashboard;
