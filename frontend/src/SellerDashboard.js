import React, { useState, useEffect } from 'react';

const SellerDashboard = ({ user, token }) => {
    const [activeTab, setActiveTab] = useState('overview'); // overview, farmers, deliveries, inventory
    const [stats, setStats] = useState(null);
    const [farmers, setFarmers] = useState([]);
    const [deliveries, setDeliveries] = useState([]);
    const [loading, setLoading] = useState(true);

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
                        <button className="bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-emerald-700">
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
