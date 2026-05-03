import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

// ---------------------------------------------------------------------------
// Micro-components (inline — no extra files needed)
// ---------------------------------------------------------------------------

/** Simple toast — auto-hides after 4 s */
function AdminToast({ toast, onDismiss }) {
  if (!toast) return null;
  const bg = toast.type === 'success' ? 'bg-emerald-700' : toast.type === 'error' ? 'bg-red-700' : 'bg-gray-800';
  return (
    <div className={`fixed bottom-6 left-1/2 -translate-x-1/2 z-[200] px-5 py-3 rounded-xl shadow-2xl text-white text-sm font-medium flex items-center gap-3 ${bg}`}>
      <span>{toast.type === 'success' ? '✅' : toast.type === 'error' ? '❌' : 'ℹ️'}</span>
      <span>{toast.message}</span>
      <button onClick={onDismiss} className="ml-2 opacity-70 hover:opacity-100 text-lg leading-none">&times;</button>
    </div>
  );
}

/** Inline confirm modal — replaces window.confirm() and prompt() */
function ConfirmModal({ config, onConfirm, onCancel }) {
  const [reason, setReason] = React.useState('');
  if (!config) return null;
  return (
    <div className="fixed inset-0 bg-black/50 z-[100] flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 text-center">
        <div className={`w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl ${config.iconBg || 'bg-amber-100'}`}>
          {config.icon || '⚠️'}
        </div>
        <h3 className="text-lg font-bold text-gray-900 mb-2">{config.title}</h3>
        <p className="text-sm text-gray-500 mb-4">{config.description}</p>
        {config.requireReason && (
          <textarea
            value={reason}
            onChange={e => setReason(e.target.value)}
            placeholder="Enter reason (required)"
            rows={3}
            className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-red-400 outline-none resize-none mb-4"
          />
        )}
        <div className="flex gap-3">
          <button onClick={onCancel} className="flex-1 py-2.5 border border-gray-200 rounded-xl text-sm font-medium hover:bg-gray-50">Cancel</button>
          <button
            onClick={() => onConfirm(reason)}
            disabled={config.requireReason && !reason.trim()}
            className={`flex-1 py-2.5 rounded-xl text-sm font-semibold text-white disabled:opacity-40 ${config.confirmCls || 'bg-amber-500 hover:bg-amber-600'}`}
          >
            {config.confirmLabel || 'Confirm'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
const AdminDashboard = () => {
    const { user } = useAuth();
    const location = useLocation();
    
    // Parse query params
    const queryParams = new URLSearchParams(location.search);
    const initialTab = queryParams.get('tab') || 'overview';
    const highlightUserId = queryParams.get('user') || null;

    const [activeTab, setActiveTab] = useState(initialTab);
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState(null);
    const [toast, setToast] = useState(null);
    const [confirm, setConfirm] = useState(null); // { title, description, icon, iconBg, confirmLabel, confirmCls, requireReason, onConfirm }
    const highlightRef = useRef(null);

    const showToast = (type, message) => {
        setToast({ type, message });
        setTimeout(() => setToast(null), 4000);
    };

    const askConfirm = (config) => new Promise((resolve) => {
        setConfirm({ ...config, _resolve: resolve });
    });
    const handleConfirm = (reason) => { const r = confirm._resolve; setConfirm(null); r({ confirmed: true, reason }); };
    const handleCancel  = ()       => { const r = confirm._resolve; setConfirm(null); r({ confirmed: false }); };

    // Data States
    const [usersList, setUsersList] = useState([]);
    const [pendingKyc, setPendingKyc] = useState([]);
    const [ordersList, setOrdersList] = useState([]);
    const [orderSearchTerm, setOrderSearchTerm] = useState(''); // Global Orders filter
    const [pendingReconciliations, setPendingReconciliations] = useState([]);
    const [communitiesList, setCommunitiesList] = useState([]);
    
    // Messaging States
    const [adminConversations, setAdminConversations] = useState([]);
    const [adminMessageRecipient, setAdminMessageRecipient] = useState('');
    const [adminMessageContent, setAdminMessageContent] = useState('');

    // Fetch Stats on Load
    useEffect(() => {
        fetchAdminStats();
    }, []);

    // Fetch Data based on active tab
    useEffect(() => {
        if (activeTab === 'users') fetchUsers();
        if (activeTab === 'kyc') fetchPendingKyc();
        if (activeTab === 'orders') fetchOrders();
        if (activeTab === 'reconciliations') fetchReconciliations();
        if (activeTab === 'communities') fetchCommunities();
        if (activeTab === 'messaging') fetchConversations();
    }, [activeTab]);

    // Scroll to highlighted user after KYC tab loads
    useEffect(() => {
        if (highlightUserId && activeTab === 'kyc' && highlightRef.current) {
            setTimeout(() => highlightRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' }), 300);
        }
    }, [highlightUserId, activeTab, pendingKyc]);

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

    const fetchReconciliations = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/reconciliations`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                const data = await response.json();
                setPendingReconciliations(data);
            }
        } catch (err) { console.error(err); }
        setLoading(false);
    };

    const fetchCommunities = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/communities`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                const data = await response.json();
                setCommunitiesList(data.communities);
            }
        } catch (err) { console.error(err); }
        setLoading(false);
    };

    const fetchConversations = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/messages/conversations`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                const data = await response.json();
                setAdminConversations(data || []);
            }
        } catch (err) { console.error(err); }
    };

    const sendAdminMessage = async (e) => {
        if (e) e.preventDefault();
        if (!adminMessageRecipient.trim() || !adminMessageContent.trim()) return;
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/messages/send`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    recipient_username: adminMessageRecipient.trim(),
                    content: adminMessageContent.trim(),
                    type: 'text'
                })
            });
            if (response.ok) {
                showToast('success', 'Message dispatched successfully.');
                setAdminMessageContent('');
                fetchConversations();
            } else {
                const errorData = await response.json();
                showToast('error', errorData.detail || 'Failed to send message.');
            }
        } catch (err) { console.error(err); showToast('error', 'Message dispatch failed.'); }
    };

    const handleHoldPayment = async (orderId) => {
        const { confirmed } = await askConfirm({
            title: 'Hold Payment?',
            description: 'This will prevent automatic fund release for this order.',
            icon: '⚠️', iconBg: 'bg-amber-100',
            confirmLabel: 'Hold Payment', confirmCls: 'bg-amber-500 hover:bg-amber-600',
        });
        if (!confirmed) return;
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/orders/${orderId}/halt-payout`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) { showToast('success', 'Payment placed on HOLD.'); fetchOrders(); }
            else showToast('error', 'Failed to hold payment.');
        } catch (err) { console.error(err); showToast('error', 'Error holding payment.'); }
    };

    const handleReleasePayment = async (orderId) => {
        const { confirmed } = await askConfirm({
            title: 'Release Payment?',
            description: 'This will transfer funds to the seller immediately. Only proceed when delivery is confirmed.',
            icon: '✅', iconBg: 'bg-emerald-100',
            confirmLabel: 'Release Now', confirmCls: 'bg-emerald-600 hover:bg-emerald-700',
        });
        if (!confirmed) return;
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/orders/${orderId}/manual-release`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) { showToast('success', 'Payment released successfully.'); fetchOrders(); }
            else showToast('error', 'Failed to release payment.');
        } catch (err) { console.error(err); showToast('error', 'Error releasing payment.'); }
    };

    // Actions
    const toggleBlockUser = async (userId, isBlocked) => {
        const action = isBlocked ? 'unblock' : 'block';
        const { confirmed } = await askConfirm({
            title: `${isBlocked ? 'Unblock' : 'Block'} User?`,
            description: isBlocked
                ? 'This user will be able to log in and use the platform again.'
                : 'This user will be immediately locked out of the platform.',
            icon: isBlocked ? '✅' : '🚫',
            iconBg: isBlocked ? 'bg-emerald-100' : 'bg-red-100',
            confirmLabel: isBlocked ? 'Unblock' : 'Block',
            confirmCls: isBlocked ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-red-600 hover:bg-red-700',
        });
        if (!confirmed) return;
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/${userId}/${action}`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) { showToast('success', `User ${action}ed successfully.`); fetchUsers(); }
            else showToast('error', 'Action failed.');
        } catch (err) { showToast('error', 'Action failed.'); }
    };

    const toggleCommunityStatus = async (communityId, isActive) => {
        const { confirmed } = await askConfirm({
            title: isActive ? 'Block Community?' : 'Unblock Community?',
            description: isActive
                ? 'This community will be immediately hidden from public search and feeds.'
                : 'This community will be reinstated to public sections.',
            icon: isActive ? '🚫' : '✅',
            iconBg: isActive ? 'bg-red-100' : 'bg-emerald-100',
            confirmLabel: isActive ? 'Block Community' : 'Unblock',
            confirmCls: isActive ? 'bg-red-600 hover:bg-red-700' : 'bg-emerald-600 hover:bg-emerald-700',
        });
        if (!confirmed) return;
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/communities/${communityId}/toggle-status`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) { showToast('success', 'Community status updated.'); fetchCommunities(); }
            else showToast('error', 'Action failed.');
        } catch (err) { showToast('error', 'Action failed.'); }
    };

    const handleKycAction = async (userId, action) => {
        const isReject = action === 'reject';
        const { confirmed, reason } = await askConfirm({
            title: isReject ? 'Reject Verification?' : 'Approve Verification?',
            description: isReject
                ? 'The applicant will be notified with your reason. Their account stays inactive.'
                : 'The applicant will be verified and can immediately use all partner features.',
            icon: isReject ? '❌' : '✅',
            iconBg: isReject ? 'bg-red-100' : 'bg-emerald-100',
            confirmLabel: isReject ? 'Reject' : 'Approve',
            confirmCls: isReject ? 'bg-red-600 hover:bg-red-700' : 'bg-emerald-600 hover:bg-emerald-700',
            requireReason: isReject,
        });
        if (!confirmed) return;

        try {
            const url = `${process.env.REACT_APP_BACKEND_URL}/api/kyc/admin/${action}/${userId}`;
            const body = isReject ? JSON.stringify({ reason }) : null;
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' },
                body,
            });
            if (response.ok) { showToast('success', `KYC ${action}d successfully.`); fetchPendingKyc(); }
            else showToast('error', `KYC ${action} failed.`);
        } catch (err) { showToast('error', 'Action failed.'); }
    };

    const updateOrderStatus = async (orderId, newStatus) => {
        if (newStatus === 'delivered') {
            const { confirmed } = await askConfirm({
                title: 'Mark as Delivered?',
                description: 'This will release funds to the seller. Only confirm when physical delivery is confirmed.',
                icon: '📦', iconBg: 'bg-amber-100',
                confirmLabel: 'Yes, Mark Delivered', confirmCls: 'bg-amber-500 hover:bg-amber-600',
            });
            if (!confirmed) return;
        }
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/orders/${orderId}/status`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            if (response.ok) { const d = await response.json(); showToast('success', d.message); fetchOrders(); }
            else { const e = await response.json(); showToast('error', `Failed: ${e.detail}`); }
        } catch (err) { showToast('error', 'Update failed.'); }
    };

    const viewDocument = async (docId) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/kyc/admin/document/${docId}`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                const data = await response.json();
                const byteCharacters = atob(data.file_data);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) byteNumbers[i] = byteCharacters.charCodeAt(i);
                const blob = new Blob([new Uint8Array(byteNumbers)], { type: data.mime_type });
                window.open(URL.createObjectURL(blob), '_blank');
            } else showToast('error', 'Failed to load document.');
        } catch (err) { showToast('error', 'Failed to load document.'); }
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

    // Process Orders Filtering
    const filteredOrdersList = ordersList.filter(o => {
        if (!orderSearchTerm) return true;
        const term = orderSearchTerm.toLowerCase();
        
        // Search usernames
        if (o.buyer_username?.toLowerCase().includes(term)) return true;
        if (o.seller_username?.toLowerCase().includes(term)) return true;
        if (o.order_id?.toLowerCase().includes(term)) return true;
        
        // Search dropoff location details
        if (o.dropoff_location_details) {
            if (o.dropoff_location_details.city?.toLowerCase().includes(term)) return true;
            if (o.dropoff_location_details.state?.toLowerCase().includes(term)) return true;
            if (o.dropoff_location_details.country?.toLowerCase().includes(term)) return true;
            if (o.dropoff_location_details.name?.toLowerCase().includes(term)) return true;
        }
        
        // Search raw shipping address string
        if (o.shipping_address?.toLowerCase().includes(term)) return true;
        
        return false;
    });

    return (
        <div className="min-h-screen bg-gray-100">
            <AdminToast toast={toast} onDismiss={() => setToast(null)} />
            <ConfirmModal config={confirm} onConfirm={handleConfirm} onCancel={handleCancel} />
            {/* Top Navbar */}
            <div className="bg-white shadow-sm border-b px-6 py-4 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">⚡</span>
                    <h1 className="text-xl font-bold text-gray-800">Pyramyd Admin</h1>
                </div>
                <div className="flex items-center gap-4">
                    <span className="text-sm font-medium">Logged in as {user?.username}</span>
                    <a href="/" className="px-3 py-1.5 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors text-sm font-medium">
                        Return to App
                    </a>
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
                        <button
                            onClick={() => setActiveTab('reconciliations')}
                            className={`w-full text-left px-4 py-3 rounded-lg flex items-center gap-3 font-medium transition-colors ${activeTab === 'reconciliations' ? 'bg-purple-50 text-purple-700' : 'text-gray-600 hover:bg-gray-50'}`}
                        >
                            <span>🏦</span> Reconciliations
                            {pendingReconciliations.length > 0 && <span className="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">{pendingReconciliations.length}</span>}
                        </button>
                        <button
                            onClick={() => setActiveTab('communities')}
                            className={`w-full text-left px-4 py-3 rounded-lg flex items-center gap-3 font-medium transition-colors ${activeTab === 'communities' ? 'bg-purple-50 text-purple-700' : 'text-gray-600 hover:bg-gray-50'}`}
                        >
                            <span>🌍</span> Communities
                        </button>
                        <button
                            onClick={() => setActiveTab('messaging')}
                            className={`w-full text-left px-4 py-3 rounded-lg flex items-center gap-3 font-medium transition-colors ${activeTab === 'messaging' ? 'bg-purple-50 text-purple-700' : 'text-gray-600 hover:bg-gray-50'}`}
                        >
                            <span>💬</span> Dispatches
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
                                    <p className="text-3xl font-bold text-gray-800 mt-2">{stats.metrics.total_orders}</p>
                                </div>
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                    <h3 className="text-gray-500 text-sm font-medium">GMV</h3>
                                    <p className="text-3xl font-bold text-emerald-600 mt-2">₦{stats.metrics.gmv?.toLocaleString()}</p>
                                </div>
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                    <h3 className="text-gray-500 text-sm font-medium">Revenue (Est.)</h3>
                                    <p className="text-3xl font-bold text-blue-600 mt-2">₦{stats.metrics.revenue?.toLocaleString()}</p>
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
                                    {pendingKyc.map(kyc => {
                                        const isHighlighted = highlightUserId && kyc.user.id === highlightUserId;
                                        return (
                                        <div
                                            key={kyc.user.id}
                                            ref={isHighlighted ? highlightRef : null}
                                            className={`bg-white rounded-lg shadow-sm border p-6 transition-all ${
                                                isHighlighted ? 'border-emerald-400 ring-2 ring-emerald-300' : 'border-gray-200'
                                            }`}
                                        >
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
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'orders' && (
                        <div className="space-y-6">
                            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
                                <h2 className="text-2xl font-bold">Global Order Tracking</h2>
                                <div className="relative w-full sm:w-96">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                        </svg>
                                    </div>
                                    <input
                                        type="text"
                                        placeholder="Filter by city, state, country or username..."
                                        value={orderSearchTerm}
                                        onChange={(e) => setOrderSearchTerm(e.target.value)}
                                        className="pl-10 block w-full shadow-sm text-sm border-gray-300 rounded-md focus:ring-emerald-500 focus:border-emerald-500 min-h-[40px]"
                                    />
                                </div>
                            </div>
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
                                        {filteredOrdersList.map(order => (
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

                    {activeTab === 'reconciliations' && (
                        <div className="space-y-6">
                            <div className="flex justify-between items-center mb-4">
                                <div>
                                    <h2 className="text-2xl font-bold">Manual Reconciliations</h2>
                                    <p className="text-gray-500 text-sm mt-1">Funds held in platform account due to missing user bank details.</p>
                                </div>
                            </div>

                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                                {pendingReconciliations.length === 0 ? (
                                    <div className="p-12 text-center text-gray-500">
                                        <span className="text-4xl block mb-2">🏛️</span>
                                        No pending reconciliations found in the vault.
                                    </div>
                                ) : (
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order/Ref ID</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User ID</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role Type</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount Held</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {pendingReconciliations.map((rec, i) => (
                                                <tr key={rec._id || i} className="hover:bg-gray-50">
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {new Date(rec.created_at).toLocaleDateString()}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap font-mono text-sm text-blue-600">
                                                        {rec.order_id}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap font-mono text-sm text-gray-900">
                                                        {rec.user_id}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full capitalize 
                                                            ${rec.role === 'seller' ? 'bg-indigo-100 text-indigo-800' : 'bg-orange-100 text-orange-800'}`}>
                                                            {rec.role}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-red-600">
                                                        ₦{rec.amount?.toLocaleString()}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${rec.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                                                            {rec.status.toUpperCase()}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                        {rec.status === 'pending' && (
                                                            <button
                                                                className="text-emerald-600 hover:text-emerald-900 bg-emerald-50 px-3 py-1 rounded border border-emerald-200"
                                                                onClick={() => showToast('info', 'Ask user to provide bank details first, then use Wallet payout API to release.')}
                                                            >
                                                                Resolve Vault
                                                            </button>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>
                    )}

                    {activeTab === 'communities' && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold mb-4">Platform Communities</h2>
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Group Name</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Creator</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Members</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Privacy</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {communitiesList.map(comm => (
                                            <tr key={comm.id} className="hover:bg-gray-50">
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <div className="font-bold text-gray-900">{comm.name}</div>
                                                    <div className="text-xs text-gray-500 max-w-[200px] truncate">{comm.description}</div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    @{comm.creator_username || 'Unknown'}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                                                    {comm.members_count || 1}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${comm.is_private ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-800'}`}>
                                                        {comm.is_private ? 'Private' : 'Public'}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    {comm.is_active !== False ? (
                                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>
                                                    ) : (
                                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Blocked</span>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                    <button
                                                        onClick={() => toggleCommunityStatus(comm.id, comm.is_active !== false)}
                                                        className={`text-${comm.is_active !== false ? 'red' : 'green'}-600 hover:text-${comm.is_active !== false ? 'red' : 'green'}-900 font-bold`}
                                                    >
                                                        {comm.is_active !== false ? 'Suspend / Block' : 'Unblock Group'}
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                        {communitiesList.length === 0 && (
                                            <tr><td colSpan="6" className="text-center py-8 text-gray-500">No communities on the platform yet.</td></tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {activeTab === 'messaging' && (
                        <div className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold">Admin Dispatch 💬</h2>
                                <p className="text-gray-500 text-sm mt-1">Send a direct message to any user. It will appear natively in their chat list as if sent by "@pyadmin".</p>
                            </div>

                            <form onSubmit={sendAdminMessage} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                                <div className="grid grid-cols-1 md:grid-cols-[200px_1fr_auto] gap-4">
                                    <div>
                                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Recipient Username</label>
                                        <input 
                                            type="text" 
                                            value={adminMessageRecipient}
                                            onChange={e => setAdminMessageRecipient(e.target.value)}
                                            placeholder="e.g. johndoe123"
                                            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Message</label>
                                        <input 
                                            type="text" 
                                            value={adminMessageContent}
                                            onChange={e => setAdminMessageContent(e.target.value)}
                                            placeholder="Type your official message here..."
                                            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                                            required
                                        />
                                    </div>
                                    <div className="flex items-end">
                                        <button type="submit" className="h-[48px] px-6 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg shadow-sm">
                                            Send Dispatch
                                        </button>
                                    </div>
                                </div>
                            </form>

                            <div className="mt-8">
                                <h3 className="text-lg font-bold mb-4">Recent Dispatches / Conversations</h3>
                                {adminConversations.length === 0 ? (
                                    <div className="bg-white p-8 rounded-xl border border-gray-100 text-center text-gray-500">
                                        No recent dispatched messages.
                                    </div>
                                ) : (
                                    <div className="grid gap-4">
                                        {adminConversations.map(conv => (
                                            <div key={conv.id} className="bg-white p-4 rounded-xl border border-gray-200 flex justify-between items-center hover:border-purple-300">
                                                <div className="flex items-center gap-4">
                                                    <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center text-purple-700 font-bold uppercase">
                                                        {conv.other_user?.username?.charAt(0) || '?'}
                                                    </div>
                                                    <div>
                                                        <h4 className="font-bold">@{conv.other_user?.username}</h4>
                                                        <p className="text-sm text-gray-500 truncate max-w-[400px]">
                                                            <span className="opacity-50">
                                                                {conv.last_message?.sender_username === user?.username ? 'You: ' : ''}
                                                            </span>
                                                            {conv.last_message?.content || 'Audio Message'}
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="text-xs text-gray-400">
                                                    {new Date(conv.timestamp).toLocaleDateString()}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
