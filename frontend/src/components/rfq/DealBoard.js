import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import '../../App.css';

const UNIT_OPTIONS = ['Tonnes', 'Crates', 'Baskets', 'Barrels', 'Bags (50kg)', 'Bags (25kg)',
    'Truck (6-wheeler)', 'Truck (10-wheeler)', 'Truck (12-wheeler)', 'Truck (14-wheeler)', 'Custom'];

const ROLE_BADGE = { business: '🏢 Business', agent: '🤝 Agent', farmer: '🌾 Farmer', supplier_food_produce: '🏭 Supplier' };

const CountdownTimer = ({ publishDate, expiryDate }) => {
    const [timeLeft, setTimeLeft] = useState('');

    useEffect(() => {
        if (!expiryDate) return;

        const updateTimer = () => {
            const now = new Date().getTime();

            if (publishDate) {
                const publishTime = new Date(publishDate).getTime();
                if (publishTime > now) {
                    const distToPublish = publishTime - now;
                    const d = Math.floor(distToPublish / (1000 * 60 * 60 * 24));
                    const h = Math.floor((distToPublish % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    setTimeLeft(`Starts in ${d}d ${h}h`);
                    return;
                }
            }

            const distance = new Date(expiryDate).getTime() - now;

            if (distance < 0) {
                setTimeLeft('Expired');
                return;
            }

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));

            if (days > 0) {
                setTimeLeft(`${days}d ${hours}h left`);
            } else {
                setTimeLeft(`${hours}h ${minutes}m left`);
            }
        };

        updateTimer();
        const interval = setInterval(updateTimer, 60000); // UI update every minute
        return () => clearInterval(interval);
    }, [publishDate, expiryDate]);

    return <span>{timeLeft}</span>;
}

const DealBoard = ({ requests, onMakeOffer, onRefresh, userRole }) => {
    const [activeTab, setActiveTab] = useState('FarmDeals');
    const [selectedRequest, setSelectedRequest] = useState(null);
    const [myOffers, setMyOffers] = useState([]);

    // Quotation table rows — pre-filled from request items
    const [quotationRows, setQuotationRows] = useState([]);
    const [offerNotes, setOfferNotes] = useState('');
    const [offerDate, setOfferDate] = useState('');
    const [moistureContent, setMoistureContent] = useState('');
    const [proofImages, setProofImages] = useState([]); // [{url, uploading}]
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Terms view modal (agent sees buyer's accepted terms)
    const [termsOffer, setTermsOffer] = useState(null);

    const fetchMyOffers = async () => {
        try {
            const response = await api.get('/requests/offers/mine');
            setMyOffers(response.data);
        } catch (error) {
            console.error("Failed to fetch my offers", error);
        }
    };

    const filteredRequests = requests.filter(req => {
        if (req.status !== 'active') return false;
        return activeTab === 'FarmDeals'
            ? req.platform === 'farm_deals' || req.type === 'standard'
            : req.platform === 'pyexpress' || req.type === 'instant';
    });

    // Instant: Take Job
    const handleTakeJob = async (requestId) => {
        if (!window.confirm("Confirm you want to take this job instantly? You are agreeing to the fixed price.")) return;
        try {
            const response = await api.post(`/requests/${requestId}/take`);
            alert(`Job Taken! Tracking ID: ${response.data.tracking_id}`);
            if (onRefresh) onRefresh();
            fetchMyOffers();
        } catch (error) {
            alert(error.response?.data?.detail || "Failed to take job");
        }
    };

    // Standard: Open Bid Modal
    const handleOpenOffer = (request) => {
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

    const handleCloseOffer = () => {
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

    // Image upload via presigned URL
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
            handleCloseOffer();
            if (onRefresh) onRefresh();
        } catch (error) {
            alert(error.response?.data?.detail || "Failed to submit bid");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleMarkDelivered = async (offerId) => {
        if (!window.confirm("Confirm you have delivered this order?")) return;
        try {
            await api.post(`/requests/offers/${offerId}/delivered`);
            alert("Marked as delivered!");
            fetchMyOffers();
        } catch (error) {
            alert(error.response?.data?.detail || "Error marking delivered");
        }
    };

    const handleConfirmTerms = async (offerId) => {
        if (!window.confirm("Accept the buyer's terms and create the order?")) return;
        try {
            const res = await api.post(`/requests/offers/${offerId}/confirm-terms`);
            alert(`Terms accepted! Order created: ${res.data.order_id}`);
            setTermsOffer(null);
            fetchMyOffers();
        } catch (error) {
            alert(error.response?.data?.detail || "Failed to confirm terms");
        }
    };

    const handleRejectTerms = async (offerId) => {
        if (!window.confirm("Reject the buyer's terms? They will be notified.")) return;
        try {
            await api.post(`/requests/offers/${offerId}/reject-terms`);
            alert("Terms rejected. Buyer has been notified.");
            setTermsOffer(null);
            fetchMyOffers();
        } catch (error) {
            alert(error.response?.data?.detail || "Failed to reject terms");
        }
    };

    return (
        <div className="rfq-container" style={{ padding: '20px' }}>
            {/* Tabs */}
            <div className="tabs-header" style={{ display: 'flex', gap: '20px', borderBottom: '2px solid #eee', marginBottom: '20px' }}>
                <button
                    onClick={() => setActiveTab('FarmDeals')}
                    style={{ padding: '10px 20px', border: 'none', background: 'none', borderBottom: activeTab === 'FarmDeals' ? '3px solid #f39c12' : 'none', fontWeight: 'bold', cursor: 'pointer' }}
                >
                    🌾 Farm Deals (Standard)
                </button>
                <button
                    onClick={() => setActiveTab('PyExpress')}
                    style={{ padding: '10px 20px', border: 'none', background: 'none', borderBottom: activeTab === 'PyExpress' ? '3px solid #2ecc71' : 'none', fontWeight: 'bold', cursor: 'pointer' }}
                >
                    ⚡ PyExpress (Instant)
                </button>
                <button
                    onClick={() => { setActiveTab('MyOffers'); fetchMyOffers(); }}
                    style={{ padding: '10px 20px', border: 'none', background: 'none', borderBottom: activeTab === 'MyOffers' ? '3px solid #9b59b6' : 'none', fontWeight: 'bold', cursor: 'pointer', position: 'relative' }}
                >
                    📋 My Offers
                    {myOffers.filter(o => o.status === 'accepted_by_buyer').length > 0 && (
                        <span style={{ position: 'absolute', top: '0', right: '5px', background: '#e74c3c', color: 'white', borderRadius: '50%', padding: '2px 6px', fontSize: '0.7em' }}>
                            {myOffers.filter(o => o.status === 'accepted_by_buyer').length}
                        </span>
                    )}
                </button>
                <button
                    onClick={() => { setActiveTab('MyJobs'); fetchMyOffers(); }}
                    style={{ padding: '10px 20px', border: 'none', background: 'none', borderBottom: activeTab === 'MyJobs' ? '3px solid #3498db' : 'none', fontWeight: 'bold', cursor: 'pointer' }}
                >
                    🚚 My Active Jobs
                </button>
            </div>

            {/* Request Cards */}
            <div className="deals-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                {activeTab === 'MyJobs' ? (
                    myOffers.filter(o => ['accepted', 'delivered', 'completed'].includes(o.status)).length === 0 ? <p>No active jobs found.</p> : (
                        myOffers.filter(o => ['accepted', 'delivered', 'completed'].includes(o.status)).map(offer => (
                            <div key={offer.id} className="deal-card" style={{ padding: '15px', border: '1px solid #eee', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', position: 'relative' }}>
                                <div style={{ position: 'absolute', top: '10px', right: '10px', background: offer.status === 'accepted' ? '#f1c40f' : '#eee', color: '#333', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75em', fontWeight: 'bold' }}>
                                    {offer.status.toUpperCase()}
                                </div>
                                <h3 style={{ marginRight: '100px' }}>{offer.request_title || 'Unknown Request'}</h3>
                                <p style={{ color: '#666', fontSize: '0.9em' }}>My Bid: ₦{offer.price?.toLocaleString()}</p>
                                {offer.status === 'delivered' && (
                                    <div style={{ marginTop: '12px', padding: '10px', background: '#d1ecf1', borderRadius: '4px', color: '#0c5460' }}>
                                        ✅ Delivered. Waiting for buyer confirmation.
                                    </div>
                                )}
                            </div>
                        ))
                    )
                ) : activeTab === 'MyOffers' ? (
                    myOffers.filter(o => ['pending', 'accepted_by_buyer', 'terms_rejected'].includes(o.status)).length === 0 ? <p>No pending offers found.</p> : (
                        myOffers.filter(o => ['pending', 'accepted_by_buyer', 'terms_rejected'].includes(o.status)).map(offer => (
                            <div key={offer.id} className="deal-card" style={{ padding: '15px', border: '1px solid #eee', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', position: 'relative' }}>
                                <div style={{ position: 'absolute', top: '10px', right: '10px', background: offer.status === 'accepted_by_buyer' ? '#e74c3c' : '#eee', color: offer.status === 'accepted_by_buyer' ? '#fff' : '#333', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75em', fontWeight: 'bold' }}>
                                    {offer.status === 'accepted_by_buyer' ? '⚠️ ACTION REQUIRED' : offer.status.toUpperCase()}
                                </div>
                                <h3 style={{ marginRight: '100px' }}>{offer.request_title || 'Unknown Request'}</h3>
                                <p style={{ color: '#666', fontSize: '0.9em' }}>My Bid: ₦{offer.price?.toLocaleString()}</p>

                                {/* Buyer accepted — seller must review terms */}
                                {offer.status === 'accepted_by_buyer' && (
                                    <div style={{ marginTop: '12px', padding: '10px', background: '#fef3cd', borderRadius: '6px', border: '1px solid #ffc107' }}>
                                        <p style={{ fontSize: '0.85em', color: '#856404', marginBottom: '8px' }}>
                                            🎉 Buyer accepted your bid! Review their terms and respond.
                                        </p>
                                        <button
                                            onClick={() => setTermsOffer(offer)}
                                            style={{ width: '100%', padding: '8px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                                        >
                                            View Terms & Respond
                                        </button>
                                    </div>
                                )}

                                {offer.status === 'terms_rejected' && (
                                    <div style={{ marginTop: '12px', padding: '10px', background: '#f8d7da', borderRadius: '4px', color: '#721c24' }}>
                                        ❌ You rejected the buyer's terms. They may re-negotiate.
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
                                <div style={{ position: 'absolute', top: '10px', right: '10px', background: '#eee', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8em' }}>
                                    {req.type === 'instant' ? '⚡ INSTANT' : '🌾 STANDARD'}
                                </div>
                                <h3 style={{ marginRight: '80px' }}>{req.items?.[0]?.name || req.title || 'Request'}</h3>
                                <p style={{ color: '#666', fontSize: '0.85em', marginBottom: '8px' }}>
                                    📍 {req.region_state || req.location}
                                    {req.expiry_date && <span style={{ marginLeft: '8px', color: '#e67e22' }}>⏳ <CountdownTimer publishDate={req.publish_date} expiryDate={req.expiry_date} /></span>}
                                </p>

                                {/* Items */}
                                <div style={{ margin: '8px 0', padding: '8px', background: '#f9f9f9', borderRadius: '4px' }}>
                                    {req.items?.slice(0, 3).map((item, i) => (
                                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88em' }}>
                                            <span>{item.name}</span>
                                            <span style={{ color: '#555' }}>{item.quantity} {item.unit}</span>
                                        </div>
                                    ))}
                                    {req.items?.length > 3 && <small style={{ color: '#888' }}>+{req.items.length - 3} more items</small>}
                                </div>

                                {/* Price range */}
                                {(req.price_range?.min || req.price_range?.max) && (
                                    <p style={{ fontSize: '0.85em', color: '#27ae60' }}>
                                        💰 Budget: ₦{req.price_range?.min?.toLocaleString()} – ₦{req.price_range?.max?.toLocaleString()}
                                    </p>
                                )}

                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px' }}>
                                    <span style={{ fontSize: '0.8em', color: '#888' }}>{req.offers_count || 0} bids</span>
                                    {req.type === 'instant' ? (
                                        <button
                                            onClick={() => handleTakeJob(req.id)}
                                            style={{ padding: '8px 16px', background: '#2ecc71', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                                        >
                                            ⚡ Take Job
                                        </button>
                                    ) : (
                                        <button
                                            onClick={() => handleOpenOffer(req)}
                                            style={{ padding: '8px 16px', background: '#f39c12', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
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

            {/* ── Bid Modal (Standard) ── */}
            {selectedRequest && (
                <div className="modal-overlay">
                    <div className="modal-content" style={{ maxWidth: '620px', width: '95%', maxHeight: '90vh', overflowY: 'auto' }}>
                        <div className="modal-header">
                            <h3>Place Bid — {selectedRequest.items?.[0]?.name}</h3>
                            <button className="close-button" onClick={handleCloseOffer}>×</button>
                        </div>
                        <div className="modal-body">

                            {/* Quotation Table */}
                            <h4 style={{ marginBottom: '8px' }}>Quotation</h4>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88em', marginBottom: '12px' }}>
                                <thead>
                                    <tr style={{ background: '#f5f5f5' }}>
                                        <th style={{ padding: '6px 8px', textAlign: 'left' }}>Item</th>
                                        <th style={{ padding: '6px 8px', textAlign: 'right', width: '80px' }}>Qty</th>
                                        <th style={{ padding: '6px 8px', width: '120px' }}>Unit</th>
                                        <th style={{ padding: '6px 8px', textAlign: 'right', width: '110px' }}>Unit Price (₦)</th>
                                        <th style={{ padding: '6px 8px', textAlign: 'right', width: '100px' }}>Total (₦)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {quotationRows.map((row, idx) => (
                                        <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                                            <td style={{ padding: '6px 8px' }}>{row.name}</td>
                                            <td style={{ padding: '4px 8px' }}>
                                                <input
                                                    type="number"
                                                    value={row.quantity}
                                                    onChange={e => updateRow(idx, 'quantity', e.target.value)}
                                                    style={{ width: '70px', padding: '4px', border: '1px solid #ddd', borderRadius: '4px', textAlign: 'right' }}
                                                />
                                            </td>
                                            <td style={{ padding: '4px 8px' }}>
                                                <select
                                                    value={row.unit}
                                                    onChange={e => updateRow(idx, 'unit', e.target.value)}
                                                    style={{ width: '100%', padding: '4px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '0.85em' }}
                                                >
                                                    {UNIT_OPTIONS.map(u => <option key={u}>{u}</option>)}
                                                </select>
                                            </td>
                                            <td style={{ padding: '4px 8px' }}>
                                                <input
                                                    type="number"
                                                    value={row.unit_price}
                                                    onChange={e => updateRow(idx, 'unit_price', e.target.value)}
                                                    style={{ width: '100px', padding: '4px', border: '1px solid #ddd', borderRadius: '4px', textAlign: 'right' }}
                                                    placeholder="0"
                                                />
                                            </td>
                                            <td style={{ padding: '6px 8px', textAlign: 'right', fontWeight: 'bold', color: '#27ae60' }}>
                                                ₦{(row.total || 0).toLocaleString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                                <tfoot>
                                    <tr style={{ background: '#f0fdf4' }}>
                                        <td colSpan={4} style={{ padding: '8px', textAlign: 'right', fontWeight: 'bold' }}>Grand Total:</td>
                                        <td style={{ padding: '8px', textAlign: 'right', fontWeight: 'bold', color: '#16a34a', fontSize: '1.05em' }}>₦{grandTotal.toLocaleString()}</td>
                                    </tr>
                                </tfoot>
                            </table>

                            {/* Moisture Content */}
                            <div className="form-group" style={{ marginBottom: '12px' }}>
                                <label style={{ fontSize: '0.88em', fontWeight: '500' }}>Moisture Content % <span style={{ color: '#888' }}>(optional)</span></label>
                                <input
                                    type="number"
                                    className="form-input"
                                    value={moistureContent}
                                    onChange={e => setMoistureContent(e.target.value)}
                                    placeholder="e.g. 12.5"
                                    style={{ width: '120px' }}
                                />
                            </div>

                            {/* Delivery Date */}
                            <div className="form-group" style={{ marginBottom: '12px' }}>
                                <label style={{ fontSize: '0.88em', fontWeight: '500' }}>Earliest Delivery Date *</label>
                                <input type="date" className="form-input" value={offerDate} onChange={e => setOfferDate(e.target.value)} />
                            </div>

                            {/* Notes */}
                            <div className="form-group" style={{ marginBottom: '12px' }}>
                                <label style={{ fontSize: '0.88em', fontWeight: '500' }}>Notes / Additional Info</label>
                                <textarea
                                    className="form-input"
                                    rows={2}
                                    value={offerNotes}
                                    onChange={e => setOfferNotes(e.target.value)}
                                    placeholder="Quality details, packaging, payment preference..."
                                />
                            </div>

                            {/* Image Upload */}
                            <div className="form-group" style={{ marginBottom: '16px' }}>
                                <label style={{ fontSize: '0.88em', fontWeight: '500' }}>Proof Images <span style={{ color: '#888' }}>(optional)</span></label>
                                <input type="file" accept="image/*" onChange={handleImageUpload} style={{ display: 'block', marginBottom: '8px' }} />
                                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                                    {proofImages.map((img, i) => (
                                        <div key={i} style={{ position: 'relative' }}>
                                            {img.uploading
                                                ? <div style={{ width: '60px', height: '60px', background: '#f0f0f0', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7em', color: '#888' }}>Uploading…</div>
                                                : <img src={img.url} alt="proof" style={{ width: '60px', height: '60px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #ddd' }} />
                                            }
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
                                <button className="btn-secondary" onClick={handleCloseOffer}>Cancel</button>
                                <button
                                    className="btn-primary"
                                    onClick={submitOffer}
                                    disabled={isSubmitting || proofImages.some(p => p.uploading)}
                                >
                                    {isSubmitting ? 'Submitting…' : `Submit Bid — ₦${grandTotal.toLocaleString()}`}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* ── Terms Review Modal (Agent/Seller) ── */}
            {termsOffer && (
                <div className="modal-overlay">
                    <div className="modal-content" style={{ maxWidth: '500px', width: '95%' }}>
                        <div className="modal-header">
                            <h3>📋 Buyer's Terms</h3>
                            <button className="close-button" onClick={() => setTermsOffer(null)}>×</button>
                        </div>
                        <div className="modal-body">
                            <div style={{ background: '#f8f9fa', padding: '14px', borderRadius: '8px', marginBottom: '16px' }}>
                                <p><strong>Your Bid:</strong> ₦{termsOffer.price?.toLocaleString()}</p>
                                {termsOffer.buyer_terms?.confirmed_delivery_date && (
                                    <p><strong>Confirmed Delivery:</strong> {new Date(termsOffer.buyer_terms.confirmed_delivery_date).toLocaleDateString()}</p>
                                )}
                                {termsOffer.buyer_terms?.payment_terms && (
                                    <p><strong>Payment Terms:</strong> {JSON.stringify(termsOffer.buyer_terms.payment_terms)}</p>
                                )}
                                {termsOffer.buyer_terms?.acknowledgment_note && (
                                    <div style={{ marginTop: '8px', padding: '8px', background: '#fff', borderRadius: '4px', border: '1px solid #dee2e6' }}>
                                        <strong>Note from Buyer:</strong>
                                        <p style={{ marginTop: '4px', color: '#555' }}>{termsOffer.buyer_terms.acknowledgment_note}</p>
                                    </div>
                                )}
                                {termsOffer.buyer_terms?.acknowledgment_files?.length > 0 && (
                                    <div style={{ marginTop: '10px' }}>
                                        <strong>Attached Documents:</strong>
                                        <ul style={{ marginTop: '4px' }}>
                                            {termsOffer.buyer_terms.acknowledgment_files.map((url, i) => (
                                                <li key={i}><a href={url} target="_blank" rel="noreferrer" style={{ color: '#007bff' }}>Document {i + 1}</a></li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                            <div style={{ display: 'flex', gap: '12px' }}>
                                <button
                                    onClick={() => handleRejectTerms(termsOffer.id)}
                                    style={{ flex: 1, padding: '10px', background: '#dc3545', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                                >
                                    ✗ Reject Terms
                                </button>
                                <button
                                    onClick={() => handleConfirmTerms(termsOffer.id)}
                                    style={{ flex: 1, padding: '10px', background: '#28a745', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                                >
                                    ✓ Accept Terms & Create Order
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DealBoard;
