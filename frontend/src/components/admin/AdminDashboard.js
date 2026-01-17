
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';

const AdminDashboard = () => {
    const { user, token } = useAuth();
    const [activeTab, setActiveTab] = useState('overview'); // overview, users, kyc, orders
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState(null);

    // Data States
    const [usersList, setUsersList] = useState([]);
    const [pendingKyc, setPendingKyc] = useState([]);
    const [ordersList, setOrdersList] = useState([]);

    // Fetch Stats on Load
    useEffect(() => {
        fetchAdminStats();
    }, []);

    // Fetch Data based on active tab
    useEffect(() => {
        if (activeTab === 'users') fetchUsers();
        if (activeTab === 'kyc') fetchPendingKyc();
        if (activeTab === 'orders') fetchOrders();
    }, [activeTab]);

    const fetchAdminStats = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/analytics`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) setStats(await response.json());
        } catch (err) { console.error(err); }
    };

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                const data = await response.json();
                setUsersList(data.users);
            }
        } catch (err) { console.error(err); }
        setLoading(false);
    };

    const fetchPendingKyc = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/kyc/admin/pending`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                setPendingKyc(await response.json());
            }
        } catch (err) { console.error(err); }
        setLoading(false);
    };

    const fetchOrders = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/orders`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                const data = await response.json();
                setOrdersList(data.orders);
            }
        } catch (err) { console.error(err); }
        setLoading(false);
    };

    const handleHoldPayment = async (orderId) => {
        if (!window.confirm("⚠️ Are you sure you want to HOLD payment for this order? This will prevent auto-release.")) return;
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/orders/${orderId}/halt-payout`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                alert("Payment placed on HOLD.");
                fetchOrders();
            } else {
                alert("Failed to hold payment.");
            }
        } catch (err) { console.error(err); alert("Error holding payment."); }
    };

    const handleReleasePayment = async (orderId) => {
        if (!window.confirm("✅ Are you sure you want to RELEASE payment manually? This will transfer funds immediately.")) return;
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/orders/${orderId}/manual-release`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                alert("Payment released successfully.");
                fetchOrders();
            } else {
                alert("Failed to release payment.");
            }
        } catch (err) { console.error(err); alert("Error releasing payment."); }
    };

    // Actions
    const toggleBlockUser = async (userId, isBlocked) => {
        const action = isBlocked ? 'unblock' : 'block';
        if (!window.confirm(`Are you sure you want to ${action} this user?`)) return;

        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/${userId}/${action}`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                alert(`User ${action}ed successfully`);
                fetchUsers();
            }
        } catch (err) { alert('Action failed'); }
    };

    const handleKycAction = async (userId, action) => { // action = approve or reject
        const reason = action === 'reject' ? prompt("Enter rejection reason:") : null;
        if (action === 'reject' && !reason) return;

        try {
            const url = `${process.env.REACT_APP_BACKEND_URL}/api/kyc/admin/${action}/${userId}`;
            const body = action === 'reject' ? JSON.stringify({ reason }) : null;

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                },
                body: body
            });

            if (response.ok) {
                alert(`KYC ${action}ed!`);
                fetchPendingKyc();
            }
        } catch (err) { alert('Action failed'); }
    };

    const updateOrderStatus = async (orderId, newStatus) => {
        if (newStatus === 'delivered') {
            if (!window.confirm("⚠️ WARNING: Marking as DELIVERED will release funds to the seller. Use this only when delivery is confirmed. Proceed?")) {
                return;
            }
        }

        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/orders/${orderId}/status`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: newStatus })
            });

            if (response.ok) {
                const data = await response.json();
                alert(data.message);
                fetchOrders();
            } else {
                const error = await response.json();
                alert(`Failed: ${error.detail}`);
            }
        } catch (err) { alert('Update failed'); }
    };

    const viewDocument = async (docId) => {
        // Create a temporary window/tab to show document
        // In a real app we might fetch the blob and show in a modal
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/kyc/admin/document/${docId}`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                const data = await response.json();
                // Data has file_data base64
                const byteCharacters = atob(data.file_data);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], { type: data.mime_type });
                const blobUrl = URL.createObjectURL(blob);
                window.open(blobUrl, '_blank');
            }
        } catch (err) { alert("Failed to load document"); }
    };

    if (!user || user.role !== 'admin') {
        return (
            <div className="flex items-center justify-center h-screen bg-gray-100">
                <div className="text-center">
                    <h1 className="text-4xl">🚫</h1>
                    <h2 className="text-xl font-bold mt-4">Access Denied</h2>
                    <p>You must be an administrator to view this page.</p>
                    <a href="/" className="text-emerald-600 mt-4 block hover:underline">Go Home</a>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100">
            {/* Top Navbar */}
            <div className="bg-white shadow-sm border-b px-6 py-4 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">⚡</span>
                    <h1 className="text-xl font-bold text-gray-800">Pyramyd Admin</h1>
                </div>
                <div className="flex items-center gap-4">
                    <span className="text-sm font-medium">Logged in as {user.username}</span>
                    <img src={user.profile_picture || "https://via.placeholder.com/40"} className="w-8 h-8 rounded-full border border-gray-300" alt="Admin" />
                </div>
            </div>

            <div className="flex">
                {/* Sidebar */}
                <div className="w-64 bg-white min-h-screen shadow-r border-r border-gray-200">
                    <div className="p-4 space-y-2">
                        <button
                            onClick={() => setActiveTab('overview')}
                            className={`w-full text-left px-4 py-3 rounded-lg flex items-center gap-3 font-medium transition-colors ${activeTab === 'overview' ? 'bg-purple-50 text-purple-700' : 'text-gray-600 hover:bg-gray-50'}`}
                        >
                            <span>📊</span> Overview
                        </button>
                        <button
                            onClick={() => setActiveTab('users')}
                            className={`w-full text-left px-4 py-3 rounded-lg flex items-center gap-3 font-medium transition-colors ${activeTab === 'users' ? 'bg-purple-50 text-purple-700' : 'text-gray-600 hover:bg-gray-50'}`}
                        >
                            <span>👥</span> User Management
                        </button>
                        <button
                            onClick={() => setActiveTab('kyc')}
                            className={`w-full text-left px-4 py-3 rounded-lg flex items-center gap-3 font-medium transition-colors ${activeTab === 'kyc' ? 'bg-purple-50 text-purple-700' : 'text-gray-600 hover:bg-gray-50'}`}
                        >
                            <span>🔐</span> KYC Verification
                            {pendingKyc.length > 0 && <span className="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">{pendingKyc.length}</span>}
                        </button>
                        <button
                            onClick={() => setActiveTab('orders')}
                            className={`w-full text-left px-4 py-3 rounded-lg flex items-center gap-3 font-medium transition-colors ${activeTab === 'orders' ? 'bg-purple-50 text-purple-700' : 'text-gray-600 hover:bg-gray-50'}`}
                        >
                            <span>📦</span> Global Orders
                        </button>
                    </div>
                </div>

                {/* Main Content */}
                <div className="flex-1 p-8">
                    {activeTab === 'overview' && stats && (
                        <div className="space-y-6 animate-fade-in">
                            <h2 className="text-2xl font-bold mb-6">Platform Overview</h2>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                    <h3 className="text-gray-500 text-sm font-medium">Total Orders</h3>
                                    <p className="text-3xl font-bold text-gray-800 mt-2">{stats.financials.total_orders}</p>
                                </div>
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                    <h3 className="text-gray-500 text-sm font-medium">GMV</h3>
                                    <p className="text-3xl font-bold text-emerald-600 mt-2">₦{stats.financials.gmv?.toLocaleString()}</p>
                                </div>
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                    <h3 className="text-gray-500 text-sm font-medium">Revenue (Est.)</h3>
                                    <p className="text-3xl font-bold text-blue-600 mt-2">₦{stats.financials.total_revenue?.toLocaleString()}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'users' && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold mb-4">User Management</h2>
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {usersList.map(u => (
                                            <tr key={u.id} className="hover:bg-gray-50">
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <div className="flex items-center">
                                                        <div className="h-10 w-10 flex-shrink-0">
                                                            <img className="h-10 w-10 rounded-full" src={u.profile_picture || `https://ui-avatars.com/api/?name=${u.username}&background=random`} alt="" />
                                                        </div>
                                                        <div className="ml-4">
                                                            <div className="text-sm font-medium text-gray-900">{u.first_name} {u.last_name}</div>
                                                            <div className="text-sm text-gray-500">@{u.username}</div>
                                                            <div className="text-xs text-gray-400">{u.email}</div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 capitalize">
                                                        {u.role ? u.role.replace('_', ' ') : 'User'}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    {u.is_blocked ? (
                                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Blocked</span>
                                                    ) : (
                                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                    <button
                                                        onClick={() => toggleBlockUser(u.id, u.is_blocked)}
                                                        className={`text-${u.is_blocked ? 'green' : 'red'}-600 hover:text-${u.is_blocked ? 'green' : 'red'}-900`}
                                                    >
                                                        {u.is_blocked ? 'Unblock' : 'Block'}
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {activeTab === 'kyc' && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold mb-4">Pending Verifications</h2>
                            {pendingKyc.length === 0 ? (
                                <div className="bg-white p-12 rounded-lg border border-gray-200 text-center text-gray-500">
                                    <span className="text-4xl block mb-2">🎉</span>
                                    All caught up! No pending KYC requests.
                                </div>
                            ) : (
                                <div className="grid gap-6">
                                    {pendingKyc.map(kyc => (
                                        <div key={kyc.user.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                                            <div className="flex justify-between items-start mb-4">
                                                <div className="flex items-center gap-4">
                                                    <img src={kyc.user.profile_picture || "https://via.placeholder.com/50"} className="w-12 h-12 rounded-full" alt="" />
                                                    <div>
                                                        <h3 className="font-bold text-lg">{kyc.user.first_name} {kyc.user.last_name}</h3>
                                                        <p className="text-gray-500">@{kyc.user.username} • <span className="capitalize">{kyc.user.role?.replace('_', ' ')}</span></p>
                                                    </div>
                                                </div>
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={() => handleKycAction(kyc.user.id, 'approve')}
                                                        className="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 font-medium"
                                                    >
                                                        Approve
                                                    </button>
                                                    <button
                                                        onClick={() => handleKycAction(kyc.user.id, 'reject')}
                                                        className="px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 font-medium"
                                                    >
                                                        Reject
                                                    </button>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mt-4 bg-gray-50 p-4 rounded-lg">
                                                {kyc.documents.map(doc => (
                                                    <div key={doc.id} className="border border-gray-200 bg-white p-3 rounded text-center">
                                                        <div className="text-4xl mb-2">📄</div>
                                                        <div className="text-sm font-medium truncate mb-2">{doc.file_name}</div>
                                                        <div className="text-xs text-gray-500 mb-3">{doc.document_type.replace('_', ' ')}</div>
                                                        <button
                                                            onClick={() => viewDocument(doc.id)}
                                                            className="text-blue-600 hover:underline text-xs"
                                                        >
                                                            View Document
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>

                                            <div className="mt-4 text-sm text-gray-600">
                                                <strong>Submission details:</strong>
                                                <pre className="mt-2 bg-gray-100 p-2 rounded text-xs overflow-x-auto">
                                                    {JSON.stringify(kyc.kyc_data, null, 2)}
                                                </pre>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'orders' && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold mb-4">Global Order Tracking</h2>
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Buyer</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Seller</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Payment Status</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {ordersList.map(order => (
                                            <tr key={order.order_id} className="hover:bg-gray-50">
                                                <td className="px-6 py-4 whitespace-nowrap font-mono text-sm text-blue-600">
                                                    {order.order_id}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    @{order.buyer_username}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    @{order.seller_username}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                                                    ₦{order.total_amount?.toLocaleString()}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <select
                                                        value={order.status}
                                                        onChange={(e) => updateOrderStatus(order.order_id, e.target.value)}
                                                        className={`text-xs font-semibold rounded-full px-2 py-1 border-0 cursor-pointer
                                                            ${order.status === 'completed' || order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                                                                order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                                                    'bg-gray-100 text-gray-800'}`}
                                                    >
                                                        <option value="pending">Pending</option>
                                                        <option value="processing">Processing</option>
                                                        <option value="shipped">Shipped</option>
                                                        <option value="delivered">Delivered</option>
                                                        <option value="completed">Completed</option>
                                                        <option value="cancelled">Cancelled</option>
                                                    </select>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    {order.payout_halted ? (
                                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">HELD</span>
                                                    ) : order.status === 'completed' ? (
                                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Released</span>
                                                    ) : (
                                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Pending</span>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                    {new Date(order.created_at).toLocaleDateString()}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                    {!order.payout_halted && order.status !== 'completed' && order.status !== 'cancelled' && (
                                                        <button
                                                            onClick={() => handleHoldPayment(order.order_id)}
                                                            className="text-red-600 hover:text-red-900 mr-4"
                                                        >
                                                            Hold Payment
                                                        </button>
                                                    )}
                                                    {(order.payout_halted || (order.status !== 'completed' && order.status !== 'cancelled')) && (
                                                        <button
                                                            onClick={() => handleReleasePayment(order.order_id)}
                                                            className="text-green-600 hover:text-green-900"
                                                        >
                                                            Release Payment
                                                        </button>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
