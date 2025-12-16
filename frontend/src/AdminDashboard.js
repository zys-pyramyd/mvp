import React, { useState, useEffect } from 'react';

const AdminDashboard = ({ token }) => {
    const [stats, setStats] = useState({
        totalTransactions: 0,
        totalRevenue: 0,
        activeUsers: 0,
        pendingOrders: 0,
        pendingKYC: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

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

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Dashboard...</div>;

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <StatCard
                        title="Total Revenue"
                        value={`₦${stats.totalRevenue.toLocaleString()}`}
                        icon="💰"
                        color="bg-emerald-100 text-emerald-800"
                    />
                    <StatCard
                        title="Total Transactions"
                        value={stats.totalTransactions}
                        icon="💳"
                        color="bg-blue-100 text-blue-800"
                    />
                    <StatCard
                        title="Active Users"
                        value={stats.activeUsers}
                        icon="👥"
                        color="bg-purple-100 text-purple-800"
                    />
                    <StatCard
                        title="Pending Orders"
                        value={stats.pendingOrders}
                        icon="📦"
                        color="bg-orange-100 text-orange-800"
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Pending Actions */}
                    <div className="bg-white rounded-xl shadow-sm p-6">
                        <h2 className="text-xl font-bold mb-4">Pending Actions</h2>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center p-4 bg-yellow-50 rounded-lg">
                                <div className="flex items-center gap-3">
                                    <span className="text-2xl">📝</span>
                                    <div>
                                        <h3 className="font-semibold text-yellow-900">Pending KYC Reviews</h3>
                                        <p className="text-sm text-yellow-700">{stats.pendingKYC} users waiting for verification</p>
                                    </div>
                                </div>
                                <button className="px-4 py-2 bg-yellow-100 text-yellow-800 rounded-lg hover:bg-yellow-200 font-medium">
                                    Review
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* System Health */}
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

export default AdminDashboard;
