import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const UNIT_OPTIONS = ['Tonnes', 'Crates', 'Baskets', 'Barrels', 'Bags (50kg)', 'Bags (25kg)',
    'Truck (6-wheeler)', 'Truck (10-wheeler)', 'Truck (12-wheeler)', 'Truck (14-wheeler)', 'Custom'];

const RequestsPage = ({ userRole, onClose }) => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filters, setFilters] = useState({
        type: 'all', // 'all', 'instant', 'standard'
        location: '',
        status: 'active'
    });
    const [locations, setLocations] = useState([]);

    // Offer Modal State
    const [selectedRequest, setSelectedRequest] = useState(null);
    const [quotationRows, setQuotationRows] = useState([]);
    const [offerNotes, setOfferNotes] = useState('');
    const [offerDate, setOfferDate] = useState(''); // Deliver By Date
    const [moistureContent, setMoistureContent] = useState('');
    const [proofImages, setProofImages] = useState([]); // [{url, uploading}]
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        fetchRequests();
        fetchLocations();
        const interval = setInterval(fetchRequests, 30000);
        return () => clearInterval(interval);
    }, [filters]);

    const fetchRequests = async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            if (filters.status) params.append('status', filters.status);
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

    // --- Modal Logic ---

    const openOfferModal = (request) => {
        setSelectedRequest(request);
        // Pre-fill quotation rows from request items
        setQuotationRows((request.items || []).map(item => ({
            name: item.name,
            quantity: item.quantity || '',
            unit: item.unit || 'Tonnes',
            unit_price: '',
            total: 0
        })));
        setOfferNotes('');
        setOfferDate('');
        setMoistureContent('');
        setProofImages([]);
    };

    const closeOfferModal = () => {
        setSelectedRequest(null);
        setQuotationRows([]);
    };

    const updateRow = (idx, field, value) => {
        setQuotationRows(prev => {
            const rows = [...prev];
            rows[idx] = { ...rows[idx], [field]: value };
            if (field === 'quantity' || field === 'unit_price') {
                const qty = parseFloat(field === 'quantity' ? value : rows[idx].quantity) || 0;
                const price = parseFloat(field === 'unit_price' ? value : rows[idx].unit_price) || 0;
                rows[idx].total = qty * price;
            }
            return rows;
        });
    };

    const grandTotal = quotationRows.reduce((sum, r) => sum + (r.total || 0), 0);

    const handleImageUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const placeholder = { url: '', uploading: true, name: file.name };
        setProofImages(prev => [...prev, placeholder]);
        try {
            const signRes = await api.post('/upload/sign-public', {
                folder: 'rfq_images',
                filename: file.name,
                contentType: file.type
            });
            await fetch(signRes.data.uploadUrl, { method: 'PUT', body: file, headers: { 'Content-Type': file.type } });
            setProofImages(prev => prev.map(p =>
                p.name === file.name && p.uploading ? { url: signRes.data.publicUrl, uploading: false, name: file.name } : p
            ));
        } catch (err) {
            alert('Image upload failed. Please try again.');
            setProofImages(prev => prev.filter(p => !(p.name === file.name && p.uploading)));
        }
    };

    const submitOffer = async () => {
        if (!offerDate) { alert('Please select a delivery date.'); return; }
        if (quotationRows.some(r => !r.unit_price)) { alert('Please fill in unit prices for all items.'); return; }
        setIsSubmitting(true);
        try {
            const offerData = {
                price: grandTotal,
                items: quotationRows.map(r => ({
                    name: r.name,
                    quantity: parseFloat(r.quantity) || 0,
                    unit: r.unit,
                    target_price: parseFloat(r.unit_price) || 0,
                    moisture_content_percent: moistureContent ? parseFloat(moistureContent) : null
                })),
                images: proofImages.filter(p => !p.uploading).map(p => p.url),
                moisture_content_percent: moistureContent ? parseFloat(moistureContent) : null,
                delivery_date: new Date(offerDate).toISOString(),
                notes: offerNotes,
                quantity_offered: quotationRows[0]?.quantity || null
            };
            await api.post(`/requests/${selectedRequest.id}/offers`, offerData);
            alert("Bid Submitted Successfully!");
            closeOfferModal();
            fetchRequests();
        } catch (error) {
            alert(error.response?.data?.detail || "Failed to submit bid");
        } finally {
            setIsSubmitting(false);
        }
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
                            <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
                        )}
                    </div>

                    {/* Filters */}
                    <div className="mt-4 flex flex-col space-y-4">
                        <div className="flex border-b border-gray-200">
                            <button onClick={() => setFilters(prev => ({ ...prev, status: 'active' }))} className={`px-6 py-2 border-b-2 font-medium text-sm transition-colors ${filters.status === 'active' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500'}`}>Live Requests</button>
                            <button onClick={() => setFilters(prev => ({ ...prev, status: 'completed' }))} className={`px-6 py-2 border-b-2 font-medium text-sm transition-colors ${filters.status === 'completed' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500'}`}>Delivered</button>
                            <button onClick={() => setFilters(prev => ({ ...prev, status: 'on_hold' }))} className={`px-6 py-2 border-b-2 font-medium text-sm transition-colors ${filters.status === 'on_hold' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500'}`}>On Hold</button>
                        </div>

                        <div className="flex flex-wrap gap-3">
                            <button onClick={() => setFilters(prev => ({ ...prev, type: 'all' }))} className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filters.type === 'all' ? 'bg-emerald-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>All Requests</button>
                            <button onClick={() => setFilters(prev => ({ ...prev, type: 'standard' }))} className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filters.type === 'standard' ? 'bg-orange-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>🌾 Standard (Farm Deals)</button>
                            <select value={filters.location} onChange={(e) => setFilters(prev => ({ ...prev, location: e.target.value }))} className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500">
                                <option value="">All Locations</option>
                                {locations.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                {loading ? (
                    <div className="text-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div><p>Loading requests...</p></div>
                ) : filteredRequests.length === 0 ? (
                    <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                        <div className="text-6xl mb-4">📭</div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Requests Found</h3>
                        <p className="text-gray-600">Try adjusting your filters.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredRequests.map(request => (
                            <div key={request.id} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex justify-between items-start mb-3">
                                    <div className="flex-1">
                                        <h3 className="font-bold text-gray-900 text-lg mb-1">{request.items[0]?.name}{request.items.length > 1 && <span className="text-sm text-gray-500 font-normal"> + {request.items.length - 1} more</span>}</h3>
                                        <p className="text-xs text-gray-500">{new Date(request.created_at).toLocaleString()}</p>
                                    </div>
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${request.type === 'instant' ? 'bg-emerald-100 text-emerald-800' : 'bg-orange-100 text-orange-800'}`}>{request.type === 'instant' ? '⚡ Instant' : '🌾 Standard'}</span>
                                </div>

                                <div className="space-y-2 mb-4">
                                    <div className="flex items-center text-sm"><span className="text-gray-600 w-20">Quantity:</span><span className="font-medium text-gray-900">{request.items[0]?.quantity} {request.items[0]?.unit}</span></div>
                                    <div className="flex items-center text-sm"><span className="text-gray-600 w-20">Location:</span><span className="font-medium text-gray-900">📍 {request.location}</span></div>
                                    {request.price_range?.min && (
                                        <div className="flex items-center text-sm"><span className="text-gray-600 w-20">Budget:</span><span className="font-medium text-emerald-600">₦{request.price_range.min.toLocaleString()} - {request.price_range.max?.toLocaleString()}</span></div>
                                    )}
                                    <div className="flex items-center text-sm"><span className="text-gray-600 w-20">Delivery:</span><span className="font-medium text-gray-900">{request.type === 'instant' ? `${request.delivery_hours || 6}hrs` : `${request.delivery_days} days`}</span></div>
                                </div>

                                {(userRole === 'agent' || userRole === 'farmer' || userRole === 'business') && (
                                    <button onClick={() => openOfferModal(request)} className="w-full bg-emerald-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-emerald-700 transition-colors">Make Offer</button>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Offer Modal */}
            {selectedRequest && (
                <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-bold text-gray-900">Place Bid — {selectedRequest.items?.[0]?.name}</h2>
                            <button onClick={closeOfferModal} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
                        </div>

                        {/* Quotation Table */}
                        <div className="mb-4 overflow-x-auto">
                            <table className="w-full text-sm border-collapse">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="p-2 text-left">Item</th>
                                        <th className="p-2 text-right w-20">Qty</th>
                                        <th className="p-2 w-32">Unit</th>
                                        <th className="p-2 text-right w-28">Price (₦)</th>
                                        <th className="p-2 text-right w-28">Total (₦)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {quotationRows.map((row, idx) => (
                                        <tr key={idx} className="border-b border-gray-100">
                                            <td className="p-2">{row.name}</td>
                                            <td className="p-2"><input type="number" value={row.quantity} onChange={e => updateRow(idx, 'quantity', e.target.value)} className="w-full text-right p-1 border rounded" /></td>
                                            <td className="p-2">
                                                <select value={row.unit} onChange={e => updateRow(idx, 'unit', e.target.value)} className="w-full p-1 border rounded">
                                                    {UNIT_OPTIONS.map(u => <option key={u}>{u}</option>)}
                                                </select>
                                            </td>
                                            <td className="p-2"><input type="number" value={row.unit_price} onChange={e => updateRow(idx, 'unit_price', e.target.value)} className="w-full text-right p-1 border rounded" placeholder="0" /></td>
                                            <td className="p-2 text-right font-bold text-emerald-600">₦{(row.total || 0).toLocaleString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                                <tfoot>
                                    <tr className="bg-emerald-50">
                                        <td colSpan={4} className="p-2 text-right font-bold">Grand Total:</td>
                                        <td className="p-2 text-right font-bold text-emerald-700 text-lg">₦{grandTotal.toLocaleString()}</td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>

                        {/* Additional Fields */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Earliest Delivery Date *</label>
                                <input type="date" value={offerDate} onChange={e => setOfferDate(e.target.value)} className="w-full p-2 border rounded-lg" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Moisture Content % (Optional)</label>
                                <input type="number" value={moistureContent} onChange={e => setMoistureContent(e.target.value)} className="w-full p-2 border rounded-lg" placeholder="e.g. 12.5" />
                            </div>
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Notes / Additional Info</label>
                            <textarea value={offerNotes} onChange={e => setOfferNotes(e.target.value)} className="w-full p-2 border rounded-lg" rows="3" placeholder="Quality details, packaging, payment preference..."></textarea>
                        </div>

                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Proof Images (Optional)</label>
                            <input type="file" accept="image/*" onChange={handleImageUpload} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 mb-2" />
                            <div className="flex gap-2 flex-wrap">
                                {proofImages.map((img, i) => (
                                    <div key={i} className="relative">
                                        {img.uploading ? <div className="w-16 h-16 bg-gray-100 flex items-center justify-center text-xs text-gray-500 rounded">...</div> : <img src={img.url} alt="proof" className="w-16 h-16 object-cover rounded border" />}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <button onClick={closeOfferModal} className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">Cancel</button>
                            <button onClick={submitOffer} disabled={isSubmitting || proofImages.some(p => p.uploading)} className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed">
                                {isSubmitting ? 'Submitting...' : `Submit Bid — ₦${grandTotal.toLocaleString()}`}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RequestsPage;
