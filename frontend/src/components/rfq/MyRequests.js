import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import '../../App.css';
import RequestWizard from './RequestWizard';

const ROLE_BADGE = {
    business: { label: '🏢 Business', color: '#6f42c1' },
    agent: { label: '🤝 Agent', color: '#0d6efd' },
    farmer: { label: '🌾 Farmer', color: '#198754' },
    supplier_food_produce: { label: '🏭 Supplier', color: '#fd7e14' }
};

const STATUS_COLOR = {
    pending: '#6c757d',
    accepted_by_buyer: '#ffc107',
    accepted: '#198754',
    delivered: '#0dcaf0',
    completed: '#198754',
    rejected: '#dc3545',
    terms_rejected: '#dc3545',
    on_hold: '#ffc107',
    closed: '#6c757d'
};

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
        const interval = setInterval(updateTimer, 60000);
        return () => clearInterval(interval);
    }, [publishDate, expiryDate]);

    return <span>{timeLeft}</span>;
}


const MyRequests = ({ requests, myOffers = [], onRefresh }) => {
    const [activeTab, setActiveTab] = useState('requests'); // 'requests' | 'offers'
    const [expandedRequestId, setExpandedRequestId] = useState(null);
    const [zoomedImage, setZoomedImage] = useState(null);
    const [editRequestModal, setEditRequestModal] = useState(null);

    // Accept modal state
    const [acceptModal, setAcceptModal] = useState(null); // { offer }
    const [ackNote, setAckNote] = useState('');
    const [confirmedDate, setConfirmedDate] = useState('');
    const [paymentTerms, setPaymentTerms] = useState({ upfront_percent: 50, on_delivery_percent: 50 });
    const [ackFiles, setAckFiles] = useState([]); // [{url, uploading, name}]
    const [isAccepting, setIsAccepting] = useState(false);

    const toggleExpand = (id) => setExpandedRequestId(expandedRequestId === id ? null : id);

    const openAcceptModal = (offer) => {
        setAcceptModal(offer);
        setAckNote('');
        setConfirmedDate('');
        setPaymentTerms({ upfront_percent: 50, on_delivery_percent: 50 });
        setAckFiles([]);
    };

    const handleDocUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const placeholder = { url: '', uploading: true, name: file.name };
        setAckFiles(prev => [...prev, placeholder]);
        try {
            const signRes = await api.post('/upload/sign-public', {
                folder: 'rfq_docs',
                filename: file.name,
                contentType: file.type
            });
            await fetch(signRes.data.uploadUrl, { method: 'PUT', body: file, headers: { 'Content-Type': file.type } });
            setAckFiles(prev => prev.map(p =>
                p.name === file.name && p.uploading ? { url: signRes.data.publicUrl, uploading: false, name: file.name } : p
            ));
        } catch {
            alert('Document upload failed.');
            setAckFiles(prev => prev.filter(p => !(p.name === file.name && p.uploading)));
        }
    };

    const handleAcceptOffer = async () => {
        if (!confirmedDate) { alert('Please select a confirmed delivery date.'); return; }
        setIsAccepting(true);
        try {
            await api.post(`/requests/offers/${acceptModal.id}/accept`, {
                acknowledgment_note: ackNote || null,
                acknowledgment_files: ackFiles.filter(f => !f.uploading).map(f => f.url),
                confirmed_delivery_date: new Date(confirmedDate).toISOString(),
                payment_terms: paymentTerms
            });
            alert("Terms sent to seller! Waiting for their confirmation.");
            setAcceptModal(null);
            if (onRefresh) onRefresh();
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to accept offer");
        } finally {
            setIsAccepting(false);
        }
    };

    const handleRejectOffer = async (offerId) => {
        if (!window.confirm("Reject this bid? The seller will be notified.")) return;
        try {
            await api.post(`/requests/offers/${offerId}/reject`);
            alert("Bid rejected.");
            if (onRefresh) onRefresh();
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to reject offer");
        }
    };

    const handleConfirmDelivery = async (offerId) => {
        const code = prompt("Enter the LAST 8 CHARACTERS of the Tracking ID to confirm receipt:");
        if (!code) return;
        try {
            await api.post(`/requests/offers/${offerId}/confirm-delivery`, { code });
            alert("Delivery Confirmed! Funds released.");
            if (onRefresh) onRefresh();
        } catch (err) {
            alert(err.response?.data?.detail || "Confirmation failed");
        }
    };

    const handleStatusUpdate = async (reqId, currentStatus, newStatus) => {
        if (newStatus === 'closed') {
            if (!window.confirm("Close this request? Bidders will no longer be able to submit quotes.")) return;
        } else if (newStatus === 'on_hold') {
            if (!window.confirm("Put this request on hold? It will be hidden from bidders and the timer will pause.")) return;
        } else if (newStatus === 'active') {
            if (!window.confirm("Open this request? It will be visible to bidders again.")) return;
        }

        try {
            await api.put(`/requests/${reqId}/status`, { status: newStatus });
            alert(`Request status updated to ${newStatus}`);
            if (onRefresh) onRefresh();
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to update status");
        }
    };

    return (
        <div className="my-requests-container" style={{ padding: '20px' }}>
            <h2 className="text-2xl font-bold mb-6">📦 My Deals</h2>

            {/* Tabs */}
            <div className="flex gap-6 border-b border-gray-200 mb-6">
                <button
                    onClick={() => setActiveTab('requests')}
                    className={`py-3 px-2 font-medium border-b-2 transition-colors ${activeTab === 'requests' ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                >
                    My Requests
                </button>
                <button
                    onClick={() => setActiveTab('offers')}
                    className={`relative py-3 px-2 font-medium border-b-2 transition-colors ${activeTab === 'offers' ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                >
                    My Bids (Offers)
                    {myOffers?.filter(o => o.status === 'accepted_by_buyer').length > 0 && (
                        <span className="absolute -top-1 -right-4 bg-red-500 text-white rounded-full px-2 py-0.5 text-xs font-bold shadow-sm">
                            {myOffers.filter(o => o.status === 'accepted_by_buyer').length}
                        </span>
                    )}
                </button>
            </div>

            {activeTab === 'requests' ? (
                <>
                    {requests.length === 0 ? (
                        <p style={{ color: '#888' }}>You haven't posted any requests yet.</p>
                    ) : (
                        <div className="requests-list">
                            {requests.map(req => (
                                <div key={req.id} className="request-item" style={{ marginBottom: '15px', border: '1px solid #eee', borderRadius: '8px', overflow: 'hidden' }}>
                                    {/* Header */}
                                    <div
                                        onClick={() => toggleExpand(req.id)}
                                        style={{ padding: '15px', background: '#f9f9f9', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                                    >
                                        <div>
                                            <strong style={{ fontSize: '1.05em' }}>{req.items?.[0]?.name || req.title || req.id}</strong>
                                            <br />
                                            <span style={{ fontSize: '0.85em', color: '#666' }}>
                                                {new Date(req.created_at).toLocaleDateString()} • {req.items?.length} item(s) •{' '}
                                                <span style={{ color: req.status === 'active' || req.status === 'open' ? '#198754' : '#6c757d', fontWeight: '600' }}>
                                                    {req.status}
                                                </span>
                                                {req.region_state && <span> • 📍 {req.region_state}</span>}
                                                {req.status === 'on_hold' && <span style={{ color: '#dc3545', fontWeight: 'bold' }}> • ⏸ On Hold</span>}
                                                {req.status === 'closed' && <span style={{ color: '#6c757d', fontWeight: 'bold' }}> • 🔒 Closed</span>}
                                                {req.status === 'active' && req.expiry_date && <span style={{ color: '#e67e22' }}> • ⏳ <CountdownTimer publishDate={req.publish_date} expiryDate={req.expiry_date} /></span>}
                                            </span>
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                            <span style={{ background: '#e9ecef', padding: '2px 10px', borderRadius: '12px', fontSize: '0.85em' }}>
                                                {req.offers_count || 0} bids
                                            </span>
                                            <span>{expandedRequestId === req.id ? '▲' : '▼'}</span>
                                        </div>
                                    </div>

                                    {/* Expanded */}
                                    {expandedRequestId === req.id && (
                                        <div style={{ padding: '15px' }}>
                                            {/* Items table */}
                                            <table style={{ width: '100%', marginBottom: '15px', fontSize: '0.88em', borderCollapse: 'collapse' }}>
                                                <thead>
                                                    <tr style={{ textAlign: 'left', color: '#888', borderBottom: '1px solid #eee' }}>
                                                        <th style={{ padding: '4px 8px' }}>Item</th>
                                                        <th style={{ padding: '4px 8px' }}>Qty</th>
                                                        <th style={{ padding: '4px 8px' }}>Unit</th>
                                                        <th style={{ padding: '4px 8px' }}>Specs</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {req.items?.map((item, idx) => (
                                                        <tr key={idx} style={{ borderBottom: '1px solid #f5f5f5' }}>
                                                            <td style={{ padding: '4px 8px' }}>{item.name}</td>
                                                            <td style={{ padding: '4px 8px' }}>{item.quantity || 'Open'}</td>
                                                            <td style={{ padding: '4px 8px' }}>{item.unit || '—'}</td>
                                                            <td style={{ padding: '4px 8px', color: '#666' }}>{item.specifications || '—'}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>

                                            {/* Action Buttons */}
                                            {(req.status === 'active' || req.status === 'on_hold') && (
                                                <div style={{ display: 'flex', gap: '10px', marginBottom: '15px', alignItems: 'center' }}>
                                                    <button
                                                        onClick={() => setEditRequestModal(req)}
                                                        style={{ padding: '6px 12px', background: '#0d6efd', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                                                    >
                                                        ✎ Edit
                                                    </button>

                                                    <select
                                                        value={req.status}
                                                        onChange={(e) => handleStatusUpdate(req.id, req.status, e.target.value)}
                                                        style={{ padding: '6px', borderRadius: '4px', border: '1px solid #ccc' }}
                                                    >
                                                        <option value="active">Open (Active)</option>
                                                        <option value="on_hold">Hold (Paused)</option>
                                                        <option value="closed">Close (End Request)</option>
                                                    </select>
                                                </div>
                                            )}

                                            <h4 style={{ marginBottom: '12px' }}>Bids ({req.offers?.length || 0})</h4>
                                            {(!req.offers || req.offers.length === 0) ? (
                                                <p style={{ color: '#888', fontStyle: 'italic' }}>No bids yet.</p>
                                            ) : (
                                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(270px, 1fr))', gap: '15px' }}>
                                                    {req.offers.map(offer => {
                                                        const badge = ROLE_BADGE[offer.seller_role];
                                                        const statusColor = STATUS_COLOR[offer.status] || '#6c757d';
                                                        return (
                                                            <div key={offer.id} style={{ border: '1px solid #e0e0e0', borderRadius: '8px', padding: '12px', position: 'relative' }}>
                                                                {/* Status badge */}
                                                                <div style={{ position: 'absolute', top: '10px', right: '10px', background: statusColor, color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '0.72em', fontWeight: 'bold' }}>
                                                                    {offer.status?.toUpperCase()}
                                                                </div>

                                                                {/* Seller info */}
                                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', marginRight: '80px' }}>
                                                                    <strong style={{ fontSize: '0.95em' }}>{offer.seller_username}</strong>
                                                                    {badge && (
                                                                        <span style={{ background: badge.color, color: '#fff', padding: '1px 7px', borderRadius: '10px', fontSize: '0.72em', fontWeight: '600' }}>
                                                                            {badge.label}
                                                                        </span>
                                                                    )}
                                                                </div>

                                                                {/* Price */}
                                                                <div style={{ fontSize: '1.1em', fontWeight: 'bold', color: '#198754', marginBottom: '6px' }}>
                                                                    ₦{offer.price?.toLocaleString()}
                                                                </div>

                                                                {/* Quotation items */}
                                                                {offer.items?.length > 0 && (
                                                                    <div style={{ background: '#f8f9fa', padding: '8px', borderRadius: '4px', marginBottom: '8px', fontSize: '0.82em' }}>
                                                                        {offer.items.map((item, i) => (
                                                                            <div key={i} style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                                                <span>{item.name} ({item.quantity} {item.unit})</span>
                                                                                <span>₦{item.target_price?.toLocaleString()}/unit</span>
                                                                            </div>
                                                                        ))}
                                                                        {offer.moisture_content_percent && (
                                                                            <div style={{ color: '#666', marginTop: '4px' }}>Moisture: {offer.moisture_content_percent}%</div>
                                                                        )}
                                                                    </div>
                                                                )}

                                                                <p style={{ fontSize: '0.85em', color: '#555', marginBottom: '4px' }}>
                                                                    📅 Delivery: {offer.delivery_date ? new Date(offer.delivery_date).toLocaleDateString() : '—'}
                                                                </p>
                                                                {offer.notes && <p style={{ fontSize: '0.82em', color: '#777', marginBottom: '8px' }}>{offer.notes}</p>}

                                                                {/* Proof images */}
                                                                {offer.images?.length > 0 && (
                                                                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '10px' }}>
                                                                        {offer.images.map((url, i) => (
                                                                            <img
                                                                                key={i}
                                                                                src={url}
                                                                                alt="proof"
                                                                                onClick={() => setZoomedImage(url)}
                                                                                style={{ width: '52px', height: '52px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #ddd', cursor: 'zoom-in' }}
                                                                            />
                                                                        ))}
                                                                    </div>
                                                                )}

                                                                {/* Actions */}
                                                                {offer.status === 'pending' && (
                                                                    <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                                                                        <button
                                                                            onClick={() => handleRejectOffer(offer.id)}
                                                                            style={{ flex: 1, padding: '7px', background: '#fff', color: '#dc3545', border: '1px solid #dc3545', borderRadius: '5px', cursor: 'pointer', fontWeight: '600', fontSize: '0.85em' }}
                                                                        >
                                                                            Reject
                                                                        </button>
                                                                        <button
                                                                            onClick={() => openAcceptModal(offer)}
                                                                            style={{ flex: 2, padding: '7px', background: '#198754', color: '#fff', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: '600', fontSize: '0.85em' }}
                                                                        >
                                                                            Accept & Set Terms
                                                                        </button>
                                                                    </div>
                                                                )}

                                                                {offer.status === 'accepted_by_buyer' && (
                                                                    <div style={{ marginTop: '8px', padding: '8px', background: '#fff3cd', borderRadius: '4px', fontSize: '0.82em', color: '#856404' }}>
                                                                        ⏳ Waiting for seller to confirm your terms…
                                                                    </div>
                                                                )}

                                                                {offer.status === 'terms_rejected' && (
                                                                    <div style={{ marginTop: '8px', padding: '8px', background: '#f8d7da', borderRadius: '4px', fontSize: '0.82em', color: '#721c24' }}>
                                                                        ❌ Seller rejected your terms. You may re-negotiate or choose another bid.
                                                                        <button
                                                                            onClick={() => openAcceptModal(offer)}
                                                                            style={{ display: 'block', marginTop: '6px', width: '100%', padding: '6px', background: '#dc3545', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85em' }}
                                                                        >
                                                                            Re-send Terms
                                                                        </button>
                                                                    </div>
                                                                )}

                                                                {offer.status === 'accepted' && (
                                                                    <div style={{ marginTop: '8px', background: '#d1e7dd', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
                                                                        <small>Tracking ID:</small>
                                                                        <div style={{ fontWeight: 'bold', letterSpacing: '1px', margin: '4px 0' }}>{offer.tracking_id || offer.order_id}</div>
                                                                        <small style={{ color: '#f39c12' }}>Waiting for agent to mark delivered…</small>
                                                                    </div>
                                                                )}

                                                                {offer.status === 'delivered' && (
                                                                    <div style={{ marginTop: '8px', background: '#e8f5e9', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
                                                                        <p style={{ color: '#198754', fontWeight: '600', marginBottom: '8px' }}>✅ Agent marked as Delivered!</p>
                                                                        <button
                                                                            onClick={() => handleConfirmDelivery(offer.id)}
                                                                            style={{ width: '100%', padding: '8px', background: '#2ecc71', color: '#fff', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' }}
                                                                        >
                                                                            Confirm Receipt
                                                                        </button>
                                                                    </div>
                                                                )}

                                                                {offer.status === 'completed' && (
                                                                    <div style={{ marginTop: '8px', textAlign: 'center', color: '#198754', fontWeight: 'bold' }}>✓ Fulfilled & Paid</div>
                                                                )}
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </>
            ) : (
                /* My Offers Tab View */
                <div className="deals-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                    {myOffers.length === 0 ? (
                        <p className="text-gray-500 text-center py-8 w-full block">No bids submitted yet.</p>
                    ) : (
                        myOffers.map(offer => (
                            <div key={offer.id} className="deal-card" style={{ padding: '15px', border: '1px solid #eee', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', position: 'relative' }}>
                                <div style={{ position: 'absolute', top: '10px', right: '10px', background: offer.status === 'accepted_by_buyer' ? '#e74c3c' : (offer.status === 'accepted' ? '#f1c40f' : '#eee'), color: offer.status === 'accepted_by_buyer' ? '#fff' : '#333', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75em', fontWeight: 'bold' }}>
                                    {offer.status === 'accepted_by_buyer' ? '⚠️ ACTION REQUIRED' : offer.status.replace(/_/g, ' ').toUpperCase()}
                                </div>
                                <h3 style={{ marginRight: '100px', fontWeight: 'bold', fontSize: '1.1em', marginBottom: '8px' }}>{offer.request_title || 'Unknown Request'}</h3>
                                <p style={{ color: '#666', fontSize: '0.9em' }}>My Bid: <span className="font-bold text-gray-900">₦{offer.price?.toLocaleString()}</span></p>

                                {/* Buyer accepted — seller must review terms */}
                                {offer.status === 'accepted_by_buyer' && (
                                    <div style={{ marginTop: '12px', padding: '10px', background: '#fef3cd', borderRadius: '6px', border: '1px solid #ffc107' }}>
                                        <p style={{ fontSize: '0.85em', color: '#856404', marginBottom: '8px' }}>
                                            🎉 Buyer accepted your bid! Please review and finalize the terms.
                                        </p>
                                        <button
                                            onClick={() => {
                                                // Alerting for now indicating what this action does as DealBoard usually handles this modal
                                                alert("Action Required: Please visit the 'Seller Dashboard' -> 'DealBoard' -> 'My Offers' to finalize the contract terms and schedule delivery.");
                                            }}
                                            style={{ width: '100%', padding: '8px', background: '#e67e22', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                                        >
                                            View Terms & Finalize
                                        </button>
                                    </div>
                                )}

                                {offer.status === 'terms_rejected' && (
                                    <div style={{ marginTop: '12px', padding: '10px', background: '#f8d7da', borderRadius: '4px', color: '#721c24' }}>
                                        ❌ You rejected the buyer's terms. They may re-negotiate.
                                    </div>
                                )}

                                {offer.status === 'delivered' && (
                                    <div style={{ marginTop: '12px', padding: '10px', background: '#d1ecf1', borderRadius: '4px', color: '#0c5460' }}>
                                        ✅ Delivered. Waiting for buyer confirmation.
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* ── Accept / Terms Modal ── */}
            {acceptModal && (
                <div className="modal-overlay">
                    <div className="modal-content" style={{ maxWidth: '480px', width: '95%' }}>
                        <div className="modal-header">
                            <h3>Accept Bid & Set Terms</h3>
                            <button className="close-button" onClick={() => setAcceptModal(null)}>×</button>
                        </div>
                        <div className="modal-body">
                            <p style={{ color: '#555', marginBottom: '16px' }}>
                                Bid from <strong>{acceptModal.seller_username}</strong> — ₦{acceptModal.price?.toLocaleString()}
                            </p>

                            <div className="form-group" style={{ marginBottom: '12px' }}>
                                <label style={{ fontWeight: '500', fontSize: '0.9em' }}>Confirmed Delivery Date *</label>
                                <input type="date" className="form-input" value={confirmedDate} onChange={e => setConfirmedDate(e.target.value)} />
                            </div>

                            <div className="form-group" style={{ marginBottom: '12px' }}>
                                <label style={{ fontWeight: '500', fontSize: '0.9em' }}>Payment Terms</label>
                                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                                    <div>
                                        <small>Upfront %</small>
                                        <input
                                            type="number" min="0" max="100"
                                            className="form-input"
                                            value={paymentTerms.upfront_percent}
                                            onChange={e => setPaymentTerms(p => ({ ...p, upfront_percent: parseInt(e.target.value) || 0, on_delivery_percent: 100 - (parseInt(e.target.value) || 0) }))}
                                            style={{ width: '80px' }}
                                        />
                                    </div>
                                    <span style={{ marginTop: '16px', color: '#888' }}>/</span>
                                    <div>
                                        <small>On Delivery %</small>
                                        <input type="number" className="form-input" value={paymentTerms.on_delivery_percent} readOnly style={{ width: '80px', background: '#f5f5f5' }} />
                                    </div>
                                </div>
                            </div>

                            <div className="form-group" style={{ marginBottom: '12px' }}>
                                <label style={{ fontWeight: '500', fontSize: '0.9em' }}>Acknowledgment Note <span style={{ color: '#888' }}>(optional)</span></label>
                                <textarea
                                    className="form-input"
                                    rows={3}
                                    value={ackNote}
                                    onChange={e => setAckNote(e.target.value)}
                                    placeholder="Any special instructions, quality requirements, or notes for the seller…"
                                />
                            </div>

                            <div className="form-group" style={{ marginBottom: '16px' }}>
                                <label style={{ fontWeight: '500', fontSize: '0.9em' }}>Attach Document <span style={{ color: '#888' }}>(Contract/Agreement, optional)</span></label>
                                <input type="file" accept=".pdf,.doc,.docx,image/*" onChange={handleDocUpload} style={{ display: 'block', marginBottom: '6px' }} />
                                {ackFiles.map((f, i) => (
                                    <div key={i} style={{ fontSize: '0.82em', color: f.uploading ? '#888' : '#198754' }}>
                                        {f.uploading ? `⏳ Uploading ${f.name}…` : `✅ ${f.name}`}
                                    </div>
                                ))}
                            </div>

                            <div style={{ display: 'flex', gap: '10px' }}>
                                <button className="btn-secondary" onClick={() => setAcceptModal(null)} style={{ flex: 1 }}>Cancel</button>
                                <button
                                    onClick={handleAcceptOffer}
                                    disabled={isAccepting || ackFiles.some(f => f.uploading)}
                                    style={{ flex: 2, padding: '10px', background: '#198754', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                                >
                                    {isAccepting ? 'Sending…' : 'Send Terms to Seller'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* ── Image Zoom Modal ── */}
            {zoomedImage && (
                <div
                    className="modal-overlay"
                    onClick={() => setZoomedImage(null)}
                    style={{ cursor: 'zoom-out' }}
                >
                    <img src={zoomedImage} alt="zoomed" style={{ maxWidth: '90vw', maxHeight: '90vh', borderRadius: '8px', boxShadow: '0 8px 32px rgba(0,0,0,0.4)' }} />
                </div>
            )}

            {editRequestModal && (
                <RequestWizard
                    isOpen={!!editRequestModal}
                    onClose={() => setEditRequestModal(null)}
                    onSubmit={() => {
                        setEditRequestModal(null);
                        if (onRefresh) onRefresh();
                    }}
                    editData={editRequestModal}
                />
            )}
        </div>
    );
};

export default MyRequests;
