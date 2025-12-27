import React, { useState, useEffect } from 'react';
import { X, ShoppingBag, CreditCard, TrendingUp, Info } from 'lucide-react';

const PersonalDashboard = ({ onClose, user, API_BASE_URL }) => {
    const [analytics, setAnalytics] = useState({
        totalSpent: 0,
        totalSaved: 0,
        orderCount: 0
    });
    const [recentActivity, setRecentActivity] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Mock data fetch - replace with actual API when available
        const fetchDashboardData = async () => {
            setLoading(true);
            // Simulate API delay
            setTimeout(() => {
                setAnalytics({
                    totalSpent: 125000,
                    totalSaved: 15000, // From coupons/discounts
                    orderCount: 8
                });
                setRecentActivity([
                    { id: 1, type: 'order', description: 'Bought 2kg Tomatoes', date: '2024-12-25', amount: 4500 },
                    { id: 2, type: 'coupon', description: 'Used "FARMFRESH" Coupon', date: '2024-12-25', amount: -500 },
                    { id: 3, type: 'order', description: 'Bought 5kg Rice', date: '2024-12-20', amount: 35000 },
                ]);
                setLoading(false);
            }, 800);
        };

        if (user) fetchDashboardData();
    }, [user]);

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="flex justify-between items-center p-6 border-b sticky top-0 bg-white z-10">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">My Dashboard</h2>
                        <p className="text-sm text-gray-500">Welcome back, {user?.first_name || 'User'}!</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full">
                        <X size={24} className="text-gray-500" />
                    </button>
                </div>

                <div className="p-6">
                    {/* Analytics Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                        <div className="bg-emerald-50 rounded-xl p-6 border border-emerald-100">
                            <div className="flex items-center gap-4 mb-2">
                                <div className="p-3 bg-emerald-100 rounded-lg text-emerald-600">
                                    <ShoppingBag size={24} />
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600 font-medium">Total Spent</p>
                                    <h3 className="text-2xl font-bold text-gray-900">
                                        {loading ? '...' : `₦${analytics.totalSpent.toLocaleString()}`}
                                    </h3>
                                </div>
                            </div>
                        </div>

                        <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
                            <div className="flex items-center gap-4 mb-2">
                                <div className="p-3 bg-blue-100 rounded-lg text-blue-600">
                                    <TrendingUp size={24} />
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600 font-medium">Total Saved</p>
                                    <h3 className="text-2xl font-bold text-gray-900">
                                        {loading ? '...' : `₦${analytics.totalSaved.toLocaleString()}`}
                                    </h3>
                                    <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded inline-block mt-1">
                                        Using Coupons
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-purple-50 rounded-xl p-6 border border-purple-100">
                            <div className="flex items-center gap-4 mb-2">
                                <div className="p-3 bg-purple-100 rounded-lg text-purple-600">
                                    <CreditCard size={24} />
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600 font-medium">Total Orders</p>
                                    <h3 className="text-2xl font-bold text-gray-900">
                                        {loading ? '...' : analytics.orderCount}
                                    </h3>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Content Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Main Content: Activity History */}
                        <div className="lg:col-span-2">
                            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                Recent Activity
                            </h3>
                            <div className="bg-white border rounded-xl overflow-hidden">
                                {loading ? (
                                    <div className="p-8 text-center text-gray-500">Loading activity...</div>
                                ) : recentActivity.length > 0 ? (
                                    <div className="divide-y">
                                        {recentActivity.map((activity) => (
                                            <div key={activity.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                                                <div className="flex items-center gap-3">
                                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${activity.type === 'coupon' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                                                        }`}>
                                                        {activity.type === 'coupon' ? <TrendingUp size={18} /> : <ShoppingBag size={18} />}
                                                    </div>
                                                    <div>
                                                        <p className="font-medium text-gray-900">{activity.description}</p>
                                                        <p className="text-xs text-gray-500">{new Date(activity.date).toLocaleDateString()}</p>
                                                    </div>
                                                </div>
                                                <div className={`font-bold ${activity.type === 'coupon' ? 'text-green-600' : 'text-gray-900'}`}>
                                                    {activity.type === 'coupon' ? '+' : '-'}₦{Math.abs(activity.amount).toLocaleString()}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="p-8 text-center text-gray-500">No recent activity found.</div>
                                )}
                            </div>
                        </div>

                        {/* Sidebar: Upgrade Options */}
                        <div>
                            <h3 className="text-lg font-bold text-gray-900 mb-4">Upgrade Account</h3>
                            <div className="space-y-4">
                                <div className="bg-gradient-to-br from-emerald-600 to-teal-700 rounded-xl p-5 text-white">
                                    <h4 className="font-bold mb-1">Become a Seller</h4>
                                    <p className="text-emerald-100 text-xs mb-3">Sell your farm produce or products to thousands of customers.</p>
                                    <button className="w-full py-2 bg-white text-emerald-700 rounded-lg text-sm font-bold hover:bg-emerald-50 transition">
                                        Start Selling
                                    </button>
                                </div>

                                <div className="bg-gradient-to-br from-purple-600 to-indigo-700 rounded-xl p-5 text-white">
                                    <h4 className="font-bold mb-1">Become an Agent</h4>
                                    <p className="text-purple-100 text-xs mb-3">Earn money by fulfilling orders and managing logistics.</p>
                                    <button className="w-full py-2 bg-white text-purple-700 rounded-lg text-sm font-bold hover:bg-purple-50 transition">
                                        Join as Agent
                                    </button>
                                </div>
                            </div>

                            <div className="mt-6 bg-gray-50 p-4 rounded-xl border border-gray-200">
                                <div className="flex items-start gap-2">
                                    <Info className="text-gray-400 shrink-0 mt-0.5" size={16} />
                                    <p className="text-xs text-gray-500">
                                        Need help with your account? Visit our <a href="#" className="text-emerald-600 hover:underline">Help Center</a> or contact support.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PersonalDashboard;
