import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const RequestsPage = ({ userRole, onClose }) => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filters, setFilters] = useState({
        type: 'all', // 'all', 'instant', 'standard'
        location: ''
    });
    const [locations, setLocations] = useState([]);
    const [showOfferModal, setShowOfferModal] = useState(false);
    const [selectedRequest, setSelectedRequest] = useState(null);
    const [offerData, setOfferData] = useState({
        price_per_unit: '',
        delivery_days: '',
        notes: ''
    });

    useEffect(() => {
        fetchRequests();
        fetchLocations();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchRequests, 30000);
        return () => clearInterval(interval);
    }, [filters]);

    const fetchRequests = async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            if (filters.type !== 'all') params.append('type', filters.type);
            if (filters.location) params.append('location', filters.location);

            const response = await api.get(`/requests?${params.toString()}`);
            setRequests(response.data || []);
        } catch (error) {
            console.error("Failed to fetch requests", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchLocations = async () => {
        try {
            const response = await api.get('/requests');
            const allRequests = response.data || [];
            const uniqueLocations = [...new Set(allRequests.map(r => r.location).filter(Boolean))];
            setLocations(uniqueLocations);
        } catch (error) {
            console.error("Failed to fetch locations", error);
        }
    };

    const handleMakeOffer = async () => {
        if (!selectedRequest) return;

        try {
            await api.post(`/requests/${selectedRequest.id}/offers`, {
                price_per_unit: parseFloat(offerData.price_per_unit),
                delivery_days: parseInt(offerData.delivery_days),
                notes: offerData.notes
            });
            alert('Offer submitted successfully!');
            setShowOfferModal(false);
            setSelectedRequest(null);
            setOfferData({ price_per_unit: '', delivery_days: '', notes: '' });
            fetchRequests();
        } catch (error) {
            console.error('Error making offer:', error);
            alert(error.response?.data?.detail || 'Failed to submit offer');
        }
    };

    const openOfferModal = (request) => {
        setSelectedRequest(request);
        setShowOfferModal(true);
    };

    const filteredRequests = requests;

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">🎯 Buyer Requests</h1>
                            <p className="text-sm text-gray-600 mt-1">Browse and respond to buyer requests</p>
                        </div>
                        {onClose && (
                            <button
                                onClick={onClose}
                                className="text-gray-500 hover:text-gray-700 text-2xl"
                            >
                                ×
                            </button>
                        )}
                    </div>

                    {/* Filters */}
                    <div className="mt-4 flex flex-wrap gap-3">
                        {/* Type Filter */}
                        <div className="flex gap-2">
                            <button
                                onClick={() => setFilters(prev => ({ ...prev, type: 'all' }))}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filters.type === 'all'
                                        ? 'bg-emerald-600 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                All Requests
                            </button>
                            <button
                                onClick={() => setFilters(prev => ({ ...prev, type: 'instant' }))}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filters.type === 'instant'
                                        ? 'bg-emerald-600 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                ⚡ Instant (2-6hrs)
                            </button>
                            <button
                                onClick={() => setFilters(prev => ({ ...prev, type: 'standard' }))}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filters.type === 'standard'
                                        ? 'bg-orange-600 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                🌾 Standard (Farm Deals)
                            </button>
                        </div>

                        {/* Location Filter */}
                        <select
                            value={filters.location}
                            onChange={(e) => setFilters(prev => ({ ...prev, location: e.target.value }))}
                            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        >
                            <option value="">All Locations</option>
                            {locations.map(loc => (
                                <option key={loc} value={loc}>{loc}</option>
                            ))}
                        </select>

                        {/* Results Count */}
                        <div className="flex items-center text-sm text-gray-600 ml-auto">
                            {filteredRequests.length} request{filteredRequests.length !== 1 ? 's' : ''} found
                        </div>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
                        <p className="text-gray-600">Loading requests...</p>
                    </div>
                ) : filteredRequests.length === 0 ? (
                    <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                        <div className="text-6xl mb-4">📭</div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Requests Found</h3>
                        <p className="text-gray-600">
                            {filters.type !== 'all' || filters.location
                                ? 'Try adjusting your filters to see more requests'
                                : 'There are no active requests at the moment'}
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredRequests.map(request => (
                            <div
                                key={request.id}
                                className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow"
                            >
                                {/* Header */}
                                <div className="flex justify-between items-start mb-3">
                                    <div className="flex-1">
                                        <h3 className="font-bold text-gray-900 text-lg mb-1">
                                            {request.items[0]?.name}
                                            {request.items.length > 1 && (
                                                <span className="text-sm text-gray-500 font-normal">
                                                    {' '}+ {request.items.length - 1} more
                                                </span>
                                            )}
                                        </h3>
                                        <p className="text-xs text-gray-500">
                                            {new Date(request.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                    <span
                                        className={`px-3 py-1 rounded-full text-xs font-bold ${request.type === 'instant'
                                                ? 'bg-emerald-100 text-emerald-800'
                                                : 'bg-orange-100 text-orange-800'
                                            }`}
                                    >
                                        {request.type === 'instant' ? '⚡ Instant' : '🌾 Standard'}
                                    </span>
                                </div>

                                {/* Details */}
                                <div className="space-y-2 mb-4">
                                    <div className="flex items-center text-sm">
                                        <span className="text-gray-600 w-20">Quantity:</span>
                                        <span className="font-medium text-gray-900">
                                            {request.items[0]?.quantity} {request.items[0]?.unit}
                                        </span>
                                    </div>
                                    <div className="flex items-center text-sm">
                                        <span className="text-gray-600 w-20">Location:</span>
                                        <span className="font-medium text-gray-900">📍 {request.location}</span>
                                    </div>
                                    {request.budget && (
                                        <div className="flex items-center text-sm">
                                            <span className="text-gray-600 w-20">Budget:</span>
                                            <span className="font-medium text-emerald-600">
                                                ₦{request.budget.toLocaleString()}
                                            </span>
                                        </div>
                                    )}
                                    <div className="flex items-center text-sm">
                                        <span className="text-gray-600 w-20">Delivery:</span>
                                        <span className="font-medium text-gray-900">
                                            {request.type === 'instant'
                                                ? `${request.delivery_hours || 6}hrs`
                                                : `${request.delivery_days} days`}
                                        </span>
                                    </div>
                                </div>

                                {/* Action Button */}
                                {(userRole === 'agent' || userRole === 'farmer' || userRole === 'business') && (
                                    <button
                                        onClick={() => openOfferModal(request)}
                                        className="w-full bg-emerald-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-emerald-700 transition-colors"
                                    >
                                        Make Offer
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Offer Modal */}
            {showOfferModal && selectedRequest && (
                <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg max-w-md w-full p-6">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">Make an Offer</h2>

                        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-600">Request for:</p>
                            <p className="font-semibold text-gray-900">{selectedRequest.items[0]?.name}</p>
                            <p className="text-sm text-gray-600 mt-1">
                                {selectedRequest.items[0]?.quantity} {selectedRequest.items[0]?.unit}
                            </p>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Price per {selectedRequest.items[0]?.unit} (₦)
                                </label>
                                <input
                                    type="number"
                                    value={offerData.price_per_unit}
                                    onChange={(e) => setOfferData(prev => ({ ...prev, price_per_unit: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                    placeholder="Enter your price"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Delivery Days
                                </label>
                                <input
                                    type="number"
                                    value={offerData.delivery_days}
                                    onChange={(e) => setOfferData(prev => ({ ...prev, delivery_days: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                    placeholder="Number of days"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Notes (Optional)
                                </label>
                                <textarea
                                    value={offerData.notes}
                                    onChange={(e) => setOfferData(prev => ({ ...prev, notes: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                                    rows="3"
                                    placeholder="Add any additional information..."
                                />
                            </div>
                        </div>

                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={() => {
                                    setShowOfferModal(false);
                                    setSelectedRequest(null);
                                    setOfferData({ price_per_unit: '', delivery_days: '', notes: '' });
                                }}
                                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleMakeOffer}
                                disabled={!offerData.price_per_unit || !offerData.delivery_days}
                                className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                            >
                                Submit Offer
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RequestsPage;
