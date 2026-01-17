import React, { useState, useEffect } from 'react';

const RequestFeed = ({ type, userRole }) => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(false);

    // Auto-refresh every 30 seconds
    useEffect(() => {
        fetchRequests();
        const interval = setInterval(fetchRequests, 30000);
        return () => clearInterval(interval);
    }, [type]);

    const fetchRequests = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/requests?type=${type}`, {
                headers
            });

            if (response.ok) {
                const data = await response.json();
                setRequests(data);
            }
        } catch (error) {
            console.error("Failed to fetch requests", error);
        } finally {
            setLoading(false);
        }
    };

    if (requests.length === 0 && !loading) return null;

    return (
        <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="text-xl font-bold text-gray-900">
                        {type === 'instant' ? '⚡ Live Instant Requests' : '🌾 Active Farm Requests'}
                    </h3>
                    <p className="text-sm text-gray-600">
                        {type === 'instant'
                            ? 'Urgent orders needing delivery in 2-6 hours'
                            : 'Bulk commodity requests to be filled'}
                    </p>
                </div>
            </div>

            <div className="space-y-4">
                {requests.slice(0, 5).map(req => ( // Show top 5
                    <div key={req.id} className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start mb-2">
                            <div>
                                <h4 className="font-bold text-gray-900">{req.items[0]?.name} {req.items.length > 1 && `+ ${req.items.length - 1} others`}</h4>
                                <p className="text-xs text-gray-500">
                                    {new Date(req.created_at).toLocaleString()} • {req.location}
                                </p>
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs font-bold ${type === 'instant' ? 'bg-emerald-100 text-emerald-800' : 'bg-green-100 text-green-800'
                                }`}>
                                {type === 'instant' ? `${req.delivery_hours}h Delivery` : `${req.delivery_days} Days`}
                            </span>
                        </div>

                        <div className="flex justify-between items-center text-sm">
                            <div className="text-gray-700">
                                <span className="font-medium">{req.items[0]?.quantity} {req.items[0]?.unit}</span>
                                {req.budget && <span className="text-gray-400"> • Budget: ₦{req.budget.toLocaleString()}</span>}
                            </div>

                            {/* Make Offer Button - Only for Agents/Farmers */}
                            {(userRole === 'agent' || userRole === 'farmer' || userRole === 'business') && (
                                <button className="text-emerald-600 font-medium hover:text-emerald-700 text-sm">
                                    Make Offer →
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {requests.length > 5 && (
                <div className="text-center mt-4">
                    <button className="text-emerald-600 font-medium text-sm hover:underline">
                        View All Requests ({requests.length})
                    </button>
                </div>
            )}
        </div>
    );
};

export default RequestFeed;
