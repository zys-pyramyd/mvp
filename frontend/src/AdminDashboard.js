import React, { useState, useEffect } from 'react';

const AdminDashboard = ({ token }) => {
    const [activeTab, setActiveTab] = useState('overview'); // overview, kyc, users
    const [kycApplicants, setKycApplicants] = useState([]);
    const [userSearchQuery, setUserSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);

    // KYC Review Modal State
    const [selectedApplicant, setSelectedApplicant] = useState(null);
    const [rejectReason, setRejectReason] = useState('');

    useEffect(() => {
        fetchStats();
        if (activeTab === 'kyc') fetchPendingKYC();
    }, [activeTab]);

    const fetchStats = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/stats`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (error) {
            console.error("Failed to fetch admin stats", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchPendingKYC = async () => {
        try {
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/kyc/pending`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setKycApplicants(data.users || []);
            }
        } catch (e) {
            console.error("Failed to fetch pending KYC", e);
        }
    };

    const handleSearchUsers = async (e) => {
        e.preventDefault();
        if (!userSearchQuery.trim()) return;

        try {
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/search?query=${encodeURIComponent(userSearchQuery)}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setSearchResults(data.users || []);
            }
        } catch (e) {
            console.error("Search failed", e);
        }
    };

    const handleReviewAction = async (userId, action) => {
        if (action === 'reject' && !rejectReason) {
            alert("Please provide a reason for rejection");
            return;
        }

        try {
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/kyc/review`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    user_id: userId,
                    action: action,
                    reason: action === 'reject' ? rejectReason : null
                })
            });

            if (res.ok) {
                alert(`User ${action === 'approve' ? 'Verified' : 'Rejected'}`);
                setSelectedApplicant(null);
                setRejectReason('');
                fetchPendingKYC();
                fetchStats();
            } else {
                alert("Action failed");
            }
        } catch (e) {
            console.error(e);
            alert("Error processing review");
        }
    };

    const [showCreateUserModal, setShowCreateUserModal] = useState(false);

    const handleCreateUser = async (userData) => {
        try {
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/create-user`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(userData)
            });

            if (res.ok) {
                alert("User created successfully");
                setShowCreateUserModal(false);
            } else {
                const data = await res.json();
                alert(data.detail || "Failed to create user");
            }
        } catch (e) {
            console.error(e);
            alert("Error creating user");
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Dashboard...</div>;

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                    <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
                    <div className="flex gap-2">
                        <button onClick={() => setActiveTab('overview')} className={`px-4 py-2 rounded-lg font-medium transition ${activeTab === 'overview' ? 'bg-gray-800 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}>Overview</button>
                        <button onClick={() => setActiveTab('kyc')} className={`px-4 py-2 rounded-lg font-medium transition ${activeTab === 'kyc' ? 'bg-gray-800 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}>KYC Reviews</button>
                        <button onClick={() => setActiveTab('users')} className={`px-4 py-2 rounded-lg font-medium transition ${activeTab === 'users' ? 'bg-gray-800 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}>User Search</button>
                    </div>
                </div>

                {activeTab === 'overview' && (
                    <>
                        {/* ... Existing Overview Content ... */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                            <StatCard
                                title="Total Revenue"
                                value={`₦${stats.totalRevenue?.toLocaleString() || 0}`}
                                icon="💰"
                                color="bg-emerald-100 text-emerald-800"
                            />
                            <StatCard
                                title="Total Transactions"
                                value={stats.totalTransactions || 0}
                                icon="💳"
                                color="bg-blue-100 text-blue-800"
                            />
                            <StatCard
                                title="Active Users"
                                value={stats.activeUsers || 0}
                                icon="👥"
                                color="bg-purple-100 text-purple-800"
                            />
                            <StatCard
                                title="Pending Orders"
                                value={stats.pendingOrders || 0}
                                icon="📦"
                                color="bg-orange-100 text-orange-800"
                            />
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div className="bg-white rounded-xl shadow-sm p-6">
                                <h2 className="text-xl font-bold mb-4">Pending Actions</h2>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center p-4 bg-yellow-50 rounded-lg">
                                        <div className="flex items-center gap-3">
                                            <span className="text-2xl">📝</span>
                                            <div>
                                                <h3 className="font-semibold text-yellow-900">Pending KYC Reviews</h3>
                                                <p className="text-sm text-yellow-700">{stats.pendingKYC || 0} users waiting for verification</p>
                                            </div>
                                        </div>
                                        <button onClick={() => setActiveTab('kyc')} className="px-4 py-2 bg-yellow-100 text-yellow-800 rounded-lg hover:bg-yellow-200 font-medium">
                                            Review
                                        </button>
                                    </div>
                                    <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
                                        <div className="flex items-center gap-3">
                                            <span className="text-2xl">👤</span>
                                            <div>
                                                <h3 className="font-semibold text-blue-900">User Management</h3>
                                                <p className="text-sm text-blue-700">Manually add new admins or agents</p>
                                            </div>
                                        </div>
                                        <button onClick={() => setShowCreateUserModal(true)} className="px-4 py-2 bg-blue-100 text-blue-800 rounded-lg hover:bg-blue-200 font-medium">
                                            + Create User
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white rounded-xl shadow-sm p-6">
                                <h2 className="text-xl font-bold mb-4">System Status</h2>
                                <div className="space-y-2">
                                    <StatusRow service="API Server" status="Operational" />
                                    <StatusRow service="Database" status="Operational" />
                                    <StatusRow service="Payment Gateway" status="Operational" />
                                    <StatusRow service="Email Service" status="Operational" />
                                </div>
                            </div>
                        </div>
                    </>
                )}

                {activeTab === 'kyc' && (
                    <div className="bg-white rounded-xl shadow-sm p-6">
                        <h2 className="text-xl font-bold mb-6">Pending KYC Applications</h2>
                        {kycApplicants.length === 0 ? (
                            <div className="text-center py-12 text-gray-400">No pending applications</div>
                        ) : (
                            <div className="space-y-4">
                                {kycApplicants.map(user => (
                                    <div key={user.id} className="border p-4 rounded-lg flex justify-between items-center hover:bg-gray-50">
                                        <div>
                                            <h3 className="font-bold">{user.first_name} {user.last_name}</h3>
                                            <p className="text-sm text-gray-500">@{user.username} • {user.role}</p>
                                            <div className="text-xs mt-1 text-gray-400">Applied: {new Date(user.kyc_submitted_at || Date.now()).toLocaleDateString()}</div>
                                        </div>
                                        <button
                                            onClick={() => setSelectedApplicant(user)}
                                            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium"
                                        >
                                            View Details
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'users' && (
                    <div className="bg-white rounded-xl shadow-sm p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-bold">User Search</h2>
                            <button onClick={() => setShowCreateUserModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-blue-700">
                                + Create User
                            </button>
                        </div>

                        <form onSubmit={handleSearchUsers} className="flex gap-4 mb-8">
                            <input
                                type="text"
                                className="flex-1 border rounded-lg p-3"
                                placeholder="Search by name or username..."
                                value={userSearchQuery}
                                onChange={e => setUserSearchQuery(e.target.value)}
                            />
                            <button type="submit" className="bg-gray-900 text-white px-6 py-3 rounded-lg font-bold hover:bg-gray-800">
                                Search
                            </button>
                        </form>

                        <div className="space-y-4">
                            {searchResults.map(user => (
                                <div key={user.id} className="border p-4 rounded-lg flex justify-between items-center">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-gray-200 rounded-full overflow-hidden">
                                            {user.profile_picture ? (
                                                <img src={user.profile_picture} className="w-full h-full object-cover" alt="" />
                                            ) : (
                                                <span className="w-full h-full flex items-center justify-center font-bold text-gray-500">{user.username[0].toUpperCase()}</span>
                                            )}
                                        </div>
                                        <div>
                                            <h3 className="font-bold">{user.first_name} {user.last_name}</h3>
                                            <p className="text-sm text-gray-500">@{user.username} • {user.role}</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => window.location.href = `/admin/chat/${user.username}`}
                                            className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 font-medium text-sm"
                                        >
                                            View Profile
                                        </button>
                                        <button
                                            onClick={() => {
                                                window.dispatchEvent(new CustomEvent('openChat', { detail: { username: user.username } }));
                                            }}
                                            className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 font-medium text-sm flex items-center gap-2"
                                        >
                                            💬 Message
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Create User Modal */}
                {showCreateUserModal && (
                    <CreateUserModal onClose={() => setShowCreateUserModal(false)} onSubmit={handleCreateUser} />
                )}

                {/* KYC Modal */}
                {selectedApplicant && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                        <div className="bg-white rounded-xl max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-xl font-bold">Review Application: @{selectedApplicant.username}</h2>
                                <button onClick={() => setSelectedApplicant(null)} className="text-gray-500 hover:text-gray-900">✕</button>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                                <div>
                                    <h4 className="font-bold text-gray-700 mb-2">User Details</h4>
                                    <div className="bg-gray-50 p-4 rounded-lg space-y-2 text-sm">
                                        <p><span className="font-medium">Full Name:</span> {selectedApplicant.first_name} {selectedApplicant.last_name}</p>
                                        <p><span className="font-medium">Role:</span> {selectedApplicant.role}</p>
                                        <p><span className="font-medium">Email:</span> {selectedApplicant.email}</p>
                                        {/* Handle dynamic KYC data based on role */}
                                        {selectedApplicant.unregistered_entity_kyc && (
                                            <>
                                                <p><span className="font-medium">ID Type:</span> {selectedApplicant.unregistered_entity_kyc.identification_type}</p>
                                                <p><span className="font-medium">ID Number:</span> {selectedApplicant.unregistered_entity_kyc.identification_number}</p>
                                            </>
                                        )}
                                        {selectedApplicant.registered_business_kyc && (
                                            <>
                                                <p><span className="font-medium">Company Name:</span> {selectedApplicant.registered_business_kyc.company_name}</p>
                                                <p><span className="font-medium">RC Number:</span> {selectedApplicant.registered_business_kyc.registration_number}</p>
                                            </>
                                        )}
                                    </div>
                                </div>
                                <div>
                                    <h4 className="font-bold text-gray-700 mb-2">Submitted Documents</h4>
                                    {/* Mock display of documents using generic keys or specific ones */}
                                    {/* Display documents dynamically */}
                                    <div className="space-y-2">
                                        {['headshot_photo', 'national_id_document', 'utility_bill', 'certificate_of_incorporation', 'tin_certificate'].map(docKey => {
                                            let docUrl = selectedApplicant.unregistered_entity_kyc?.documents?.[docKey]
                                                || selectedApplicant.registered_business_kyc?.documents?.[docKey];

                                            if (!docUrl) return null;

                                            // Append token for authenticated access
                                            if (docUrl.startsWith('/api') && token) {
                                                docUrl += `?token=${token}`;
                                            }

                                            return (
                                                <div key={docKey} className="border p-2 rounded flex justify-between items-center">
                                                    <span className="capitalize text-sm">{docKey.replace(/_/g, ' ')}</span>
                                                    <a href={docUrl} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm">View File</a>
                                                </div>
                                            )
                                        })}
                                    </div>
                                </div>
                            </div>

                            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                                <h4 className="font-bold text-gray-700 mb-3">Decision</h4>
                                <div className="space-y-4">
                                    <textarea
                                        className="w-full border rounded-lg p-3 h-24"
                                        placeholder="Reason for rejection (Required if rejecting)..."
                                        value={rejectReason}
                                        onChange={e => setRejectReason(e.target.value)}
                                    ></textarea>
                                    <div className="flex gap-4">
                                        <button
                                            onClick={() => handleReviewAction(selectedApplicant.id, 'approve')}
                                            className="flex-1 bg-emerald-600 text-white py-3 rounded-lg font-bold hover:bg-emerald-700"
                                        >
                                            Approve Application
                                        </button>
                                        <button
                                            onClick={() => handleReviewAction(selectedApplicant.id, 'reject')}
                                            className="flex-1 bg-red-600 text-white py-3 rounded-lg font-bold hover:bg-red-700"
                                        >
                                            Reject Application
                                        </button>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

const StatCard = ({ title, value, icon, color }) => (
    <div className="bg-white rounded-xl shadow-sm p-6 flex items-center gap-4">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-2xl ${color}`}>
            {icon}
        </div>
        <div>
            <p className="text-sm text-gray-500 font-medium">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
    </div>
);

const StatusRow = ({ service, status }) => (
    <div className="flex justify-between items-center py-2 border-b last:border-0">
        <span className="text-gray-600">{service}</span>
        <span className="flex items-center gap-2 text-emerald-600 text-sm font-medium">
            <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
            {status}
        </span>
    </div>
);

const CreateUserModal = ({ onClose, onSubmit }) => {
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        password: '',
        role: 'admin'
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl max-w-md w-full p-6">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold">Create New User</h2>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-900">✕</button>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">First Name</label>
                            <input
                                required
                                className="w-full border rounded p-2"
                                value={formData.first_name}
                                onChange={e => setFormData({ ...formData, first_name: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Last Name</label>
                            <input
                                required
                                className="w-full border rounded p-2"
                                value={formData.last_name}
                                onChange={e => setFormData({ ...formData, last_name: e.target.value })}
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Email</label>
                        <input
                            type="email"
                            required
                            className="w-full border rounded p-2"
                            value={formData.email}
                            onChange={e => setFormData({ ...formData, email: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Username</label>
                        <input
                            required
                            className="w-full border rounded p-2"
                            value={formData.username}
                            onChange={e => setFormData({ ...formData, username: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Password</label>
                        <input
                            type="password"
                            required
                            className="w-full border rounded p-2"
                            value={formData.password}
                            onChange={e => setFormData({ ...formData, password: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Role</label>
                        <select
                            className="w-full border rounded p-2"
                            value={formData.role}
                            onChange={e => setFormData({ ...formData, role: e.target.value })}
                        >
                            <option value="admin">Admin</option>
                            <option value="agent">Agent</option>
                            <option value="moderator">Moderator</option>
                        </select>
                    </div>
                    <button type="submit" className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700">
                        Create User
                    </button>
                </form>
            </div>
        </div>
    );
};

export default AdminDashboard;
