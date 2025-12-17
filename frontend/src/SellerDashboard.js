import React, { useState, useEffect } from 'react';
import { NIGERIAN_STATES } from './nigerianStates';

const SellerDashboard = ({ user, token }) => {
    const [activeTab, setActiveTab] = useState('overview'); // overview, farmers, deliveries, inventory
    const [stats, setStats] = useState(null);
    const [farmers, setFarmers] = useState([]);
    const [deliveries, setDeliveries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddProduct, setShowAddProduct] = useState(false);

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

    const updateDeliveryStatus = async (orderId, newStatus, notes) => {
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
                alert('Status updated!');
                // Refresh deliveries
                const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent/deliveries`, { headers: { 'Authorization': `Bearer ${token}` } });
                const data = await res.json();
                setDeliveries(data.orders || []);
            } else {
                alert('Failed to update status');
            }
        } catch (error) {
            console.error(error);
            alert('Error updating status');
        }
    };

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
                        <button
                            onClick={() => setShowAddProduct(true)}
                            className="bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-emerald-700"
                        >
                            + Add Product
                        </button>
                    </div>
                </div>

                {/* Navigation Tabs */}
                <div className="flex border-b bg-white rounded-t-lg px-4 overflow-x-auto">
                    <TabButton active={activeTab === 'overview'} onClick={() => setActiveTab('overview')} label="📊 Overview" />
                    {user.role === 'agent' && (
                        <TabButton active={activeTab === 'farmers'} onClick={() => setActiveTab('farmers')} label="👨‍🌾 My Farmers" />
                    )}
                    <TabButton active={activeTab === 'deliveries'} onClick={() => setActiveTab('deliveries')} label="📦 Deliveries" />
                    <TabButton active={activeTab === 'inventory'} onClick={() => setActiveTab('inventory')} label="📋 Inventory" />
                    <TabButton active={activeTab === 'wallet'} onClick={() => setActiveTab('wallet')} label="💰 My Earnings" />
                </div>

                {/* Content Area */}
                <div className="bg-white rounded-b-lg shadow-sm p-6 min-h-[500px]">
                    {loading && <div className="text-center py-12 text-gray-500">Loading data...</div>}

                    {!loading && activeTab === 'overview' && stats && (
                        <div className="space-y-8">
                            {/* Stats Cards */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <StatCard title="Total Revenue" value={`₦${stats.revenue?.total_revenue?.toLocaleString() || 0}`} subtitle="Lifetime Earnings" icon="💰" color="bg-emerald-100 text-emerald-800" />
                                <StatCard title="Total Orders" value={stats.orders?.total_orders || 0} subtitle={`${stats.orders?.completed_orders || 0} completed`} icon="🛍️" color="bg-blue-100 text-blue-800" />
                                <StatCard title="Pending Revenue" value={`₦${stats.revenue?.pending_revenue?.toLocaleString() || 0}`} subtitle="In processing" icon="⏳" color="bg-orange-100 text-orange-800" />
                            </div>

                            {/* Charts/Graphs Placeholders */}
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
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-xl font-bold">Managed Farmers</h2>
                                <button className="text-emerald-600 text-sm font-medium hover:underline">Add New Farmer</button>
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
                            Inventory Management Component (Coming Soon)
                            <br />
                            <small>Currently managed via "Add Product" flow</small>
                        </div>
                    )}
                </div>


                {/* Add Product Modal */}
                {
                    showAddProduct && (
                        <AddProductModal
                            onClose={() => setShowAddProduct(false)}
                            onSuccess={() => {
                                setShowAddProduct(false);
                                fetchInitialData(); // Refresh data
                            }}
                            token={token}
                        />
                    )
                }
            </div >
        </div >
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
        location: '', // State
        city: '',
        pickup_address: '',
        country: 'Nigeria', // Fixed
        seller_delivery_fee: 0
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/products`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
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
                        onUpdate(order.order_id, e.target.value, order.delivery_notes);
                    }}
                    className="border rounded p-2 text-sm bg-gray-50"
                >
                    <option value="pending">⏳ Pending</option>
                    <option value="ready_for_pickup">📦 Ready for Pickup</option>
                    <option value="out_for_delivery">🚚 Out for Delivery</option>
                    <option value="delivered">✅ Delivered</option>
                </select>
            </div>
        </div>
    )
}

export default SellerDashboard;
