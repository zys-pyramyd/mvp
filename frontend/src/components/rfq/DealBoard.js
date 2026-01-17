import React, { useState } from 'react';
import api from '../../services/api';
import '../../App.css';

const DealBoard = ({ requests, onMakeOffer, onRefresh }) => {
    const [activeTab, setActiveTab] = useState('PyExpress'); // PyExpress | FarmDeals | MyJobs
    const [selectedRequest, setSelectedRequest] = useState(null);
    const [myOffers, setMyOffers] = useState([]);

    // Offer Form States
    const [offerPrice, setOfferPrice] = useState('');
    const [offerQty, setOfferQty] = useState('');
    const [offerDate, setOfferDate] = useState('');
    const [proofImage, setProofImage] = useState(''); // URL for MVP

    const fetchMyOffers = async () => {
        try {
            // Updated endpoint to fetch Agent's active offers/jobs
            const response = await api.get('/requests/offers/mine');
            setMyOffers(response.data);
        } catch (error) {
            console.error("Failed to fetch my offers", error);
        }
    };

    // Filter Requests by Platform
    // Note: PyExpress platform usually means Instant Request (but mostly).
    const filteredRequests = requests.filter(req => req.platform === activeTab);

    // Instant: Take Job
    const handleTakeJob = async (requestId) => {
        if (!window.confirm("Confirm you want to take this job instantly? You are agreeing to the fixed price.")) return;

        try {
            const response = await api.post(`/requests/${requestId}/take`);
            alert(`Job Taken! Tracking ID: ${response.data.tracking_id}`);
            if (onRefresh) onRefresh();
            fetchMyOffers(); // Update my jobs
        } catch (error) {
            console.error(error);
            alert(error.response?.data?.detail || "Failed to take job");
        }
    };

    // Standard: Make Offer
    const handleOpenOffer = (request) => {
        setSelectedRequest(request);
        setOfferQty(request.quantity_remaining || '');
    };

    const handleCloseOffer = () => {
        setSelectedRequest(null);
        setOfferPrice('');
        setOfferQty('');
        setOfferDate('');
        setProofImage('');
    };

    const submitOffer = async () => {
        const offerData = {
            price: parseFloat(offerPrice),
            quantity_offered: parseFloat(offerQty),
            delivery_date: offerDate,
            images: [proofImage] // Array of strings
        };

        // Use parent handler or call API directly? 
        // Original code used onMakeOffer. I'll modify to use API directly for consistency if onMakeOffer isn't passed updated.
        // Actually, let's just call API here.
        try {
            await api.post(`/requests/${selectedRequest.id}/offers`, offerData);
            alert("Bid Submitted Successfully!");
            handleCloseOffer();
            if (onRefresh) onRefresh();
        } catch (error) {
            console.error(error);
            alert(error.response?.data?.detail || "Failed to submit bid");
        }
    };

    const handleMarkDelivered = async (offerId) => {
        if (!window.confirm("Confirm you have delivered this order?")) return;
        try {
            await api.post(`/offers/${offerId}/delivered`);
            alert("Marked as delivered!");
            fetchMyOffers();
        } catch (error) {
            console.error(error);
            alert("Error marking delivered");
        }
    };

    return (
        <div className="rfq-container" style={{ padding: '20px' }}>
            <div className="tabs-header" style={{ display: 'flex', gap: '20px', borderBottom: '2px solid #eee', marginBottom: '20px' }}>
                <button
                    className={activeTab === 'PyExpress' ? 'tab-active' : 'tab-inactive'}
                    onClick={() => setActiveTab('PyExpress')}
                    style={{ padding: '10px 20px', border: 'none', background: 'none', borderBottom: activeTab === 'PyExpress' ? '3px solid #2ecc71' : 'none', fontWeight: 'bold', cursor: 'pointer' }}
                >
                    PyExpress (Instant)
                </button>
                <button
                    className={activeTab === 'FarmDeals' ? 'tab-active' : 'tab-inactive'}
                    onClick={() => setActiveTab('FarmDeals')}
                    style={{ padding: '10px 20px', border: 'none', background: 'none', borderBottom: activeTab === 'FarmDeals' ? '3px solid #f39c12' : 'none', fontWeight: 'bold', cursor: 'pointer' }}
                >
                    Farm Deals (Standard)
                </button>
                <button
                    className={activeTab === 'MyJobs' ? 'tab-active' : 'tab-inactive'}
                    onClick={() => { setActiveTab('MyJobs'); fetchMyOffers(); }}
                    style={{ padding: '10px 20px', border: 'none', background: 'none', borderBottom: activeTab === 'MyJobs' ? '3px solid #3498db' : 'none', fontWeight: 'bold', cursor: 'pointer' }}
                >
                    My Active Jobs
                </button>
            </div>

            <div className="deals-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                {activeTab === 'MyJobs' ? (
                    myOffers.length === 0 ? <p>No active jobs found.</p> : (
                        myOffers.map(offer => (
                            <div key={offer.id} className="deal-card" style={{ padding: '15px', border: '1px solid #eee', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', position: 'relative' }}>
                                <div className="badge" style={{ position: 'absolute', top: '10px', right: '10px', background: offer.status === 'accepted' ? '#f1c40f' : '#eee', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8em', fontWeight: 'bold' }}>
                                    {offer.status.toUpperCase()}
                                </div>
                                <h3>{offer.request_title || 'Unknown Request'}</h3>
                                <p style={{ color: '#666', fontSize: '0.9em' }}>My Offer: ₦{offer.price.toLocaleString()} for {offer.quantity_offered} units</p>

                                {offer.status === 'accepted' && (
                                    <div style={{ marginTop: '15px', padding: '10px', background: '#fff3cd', borderRadius: '4px' }}>
                                        <p style={{ fontSize: '0.9em', color: '#856404' }}>🚀 Job Active! Deliver by {new Date(offer.delivery_date).toLocaleDateString()}.</p>
                                        <div className="bg-white p-2 mt-2 rounded border">
                                            <small className="block text-gray-500">Tracking Code (Give to Buyer):</small>
                                            <code className="text-lg font-bold">{offer.delivery_otp || 'XXXX'}</code>
                                        </div>
                                        <button
                                            className="btn-primary-sm"
                                            style={{ width: '100%', marginTop: '10px', background: '#e67e22' }}
                                            onClick={() => handleMarkDelivered(offer.id)}
                                        >
                                            🚚 Mark as Delivered
                                        </button>
                                    </div>
                                )}

                                {offer.status === 'delivered' && (
                                    <div style={{ marginTop: '15px', padding: '10px', background: '#d1ecf1', borderRadius: '4px', color: '#0c5460' }}>
                                        ✅ Delivered. Waiting for Confirmation.
                                    </div>
                                )}
                            </div>
                        ))
                    )
                ) : (
                    filteredRequests.length === 0 ? (
                        <p>No active requests in this category.</p>
                    ) : (
                        filteredRequests.map(req => (
                            <div key={req.id} className="deal-card" style={{ padding: '15px', border: '1px solid #eee', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', position: 'relative' }}>
                                <div className="badge" style={{ position: 'absolute', top: '10px', right: '10px', background: '#eee', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8em' }}>
                                    {req.request_type === 'instant' ? '⚡ INSTANT' : '📝 STANDARD'}
                                </div>
                                <h3>{req.title}</h3>
                                <p style={{ color: '#666', fontSize: '0.9em' }}>
                                    {req.items?.length} Items •
                                    <span className="font-bold text-green-600"> ₦{req.budget ? req.budget.toLocaleString() : 'Open'}</span>
                                </p>

                                <div style={{ margin: '10px 0', padding: '10px', background: '#f9f9f9', borderRadius: '4px' }}>
                                    <small>Need:</small>
                                    {req.items?.slice(0, 3).map((item, i) => (
                                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9em' }}>
                                            <span>{item.name}</span>
                                            <span>{item.quantity ? `${item.quantity} ${item.unit}` : ""}</span>
                                        </div>
                                    ))}
                                </div>

                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '15px' }}>
                                    <span style={{ fontSize: '0.8em', color: '#888' }}>
                                        To: {req.location}
                                    </span>

                                    {req.request_type === 'instant' ? (
                                        <button
                                            className="btn-primary-sm bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
                                            onClick={() => handleTakeJob(req.id)}
                                        >
                                            ⚡ Take Job
                                        </button>
                                    ) : (
                                        <button
                                            className="btn-primary-sm bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded"
                                            onClick={() => handleOpenOffer(req)}
                                        >
                                            Place Bid
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))
                    )
                )}
            </div>

            {/* Offer Modal (Standard) */}
            {selectedRequest && (
                <div className="modal-overlay">
                    <div className="modal-content" style={{ maxWidth: '400px' }}>
                        <h3>Bid on: {selectedRequest.title}</h3>
                        <div className="form-group">
                            <label>Your Bid Price (₦)</label>
                            <input type="number" className="form-input" value={offerPrice} onChange={e => setOfferPrice(e.target.value)} />
                        </div>
                        <div className="form-group">
                            <label>Quantity You Can Supply</label>
                            <input type="number" className="form-input" value={offerQty} onChange={e => setOfferQty(e.target.value)} />
                            <small>Required: {selectedRequest.quantity_required || 'Open'}</small>
                        </div>
                        <div className="form-group">
                            <label>Earliest Delivery Date</label>
                            <input type="date" className="form-input" value={offerDate} onChange={e => setOfferDate(e.target.value)} />
                        </div>
                        <div className="form-group">
                            <label>Proof Image URL</label>
                            <input type="text" className="form-input" value={proofImage} onChange={e => setProofImage(e.target.value)} placeholder="http://..." />
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
                            <button className="btn-secondary" onClick={handleCloseOffer}>Cancel</button>
                            <button className="btn-primary" onClick={submitOffer}>Submit Bid</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DealBoard;
