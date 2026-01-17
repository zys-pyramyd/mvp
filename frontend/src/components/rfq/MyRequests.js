import React, { useState } from 'react';
import api from '../../services/api';
import '../../App.css';

const MyRequests = ({ requests, onAcceptOffer, onConfirmDelivery }) => {
    const [expandedRequestId, setExpandedRequestId] = useState(null);

    const toggleExpand = (id) => {
        setExpandedRequestId(expandedRequestId === id ? null : id);
    };

    return (
        <div className="my-requests-container" style={{ padding: '20px' }}>
            <h2>My Requests</h2>

            {requests.length === 0 ? (
                <p>You haven't posted any requests yet.</p>
            ) : (
                <div className="requests-list">
                    {requests.map(req => (
                        <div key={req.id} className="request-item" style={{ marginBottom: '15px', border: '1px solid #eee', borderRadius: '8px', overflow: 'hidden' }}>
                            {/* Header Row */}
                            <div
                                className="request-header"
                                onClick={() => toggleExpand(req.id)}
                                style={{ padding: '15px', background: '#f9f9f9', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                            >
                                <div>
                                    <strong style={{ fontSize: '1.1em' }}>{req.title}</strong>
                                    <br />
                                    <span style={{ fontSize: '0.9em', color: '#666' }}>
                                        {new Date(req.created_at).toLocaleDateString()} • {req.items?.length} Items • Status: <span style={{ color: req.status === 'open' ? 'green' : 'gray' }}>{req.status}</span>
                                    </span>
                                </div>
                                <div>
                                    <span style={{ marginRight: '15px' }}>{req.offers_count || 0} Offers</span>
                                    <span>{expandedRequestId === req.id ? '▲' : '▼'}</span>
                                </div>
                            </div>

                            {/* Expanded Details & Offers */}
                            {expandedRequestId === req.id && (
                                <div className="request-details" style={{ padding: '15px' }}>
                                    {/* Items Table */}
                                    <table style={{ width: '100%', marginBottom: '15px', fontSize: '0.9em' }}>
                                        <thead>
                                            <tr style={{ textAlign: 'left', color: '#888' }}>
                                                <th>Item</th>
                                                <th>Qty</th>
                                                <th>Unit</th>
                                                <th>Specs</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {req.items?.map((item, idx) => (
                                                <tr key={idx}>
                                                    <td>{item.name}</td>
                                                    <td>{item.quantity || "Open"}</td>
                                                    <td>{item.unit}</td>
                                                    <td>{item.specifications || "-"}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>

                                    <h4>Offers</h4>
                                    {(!req.offers || req.offers.length === 0) ? (
                                        <p style={{ color: '#888', fontStyle: 'italic' }}>No offers yet.</p>
                                    ) : (
                                        <div className="offers-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '15px' }}>
                                            {req.offers.map(offer => (
                                                <div key={offer.id} className="offer-card" style={{ border: '1px solid #e0e0e0', borderRadius: '6px', padding: '10px' }}>
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                                        <strong>{offer.seller_username}</strong>
                                                        <span style={{ color: '#2ecc71', fontWeight: 'bold' }}>₦{offer.price.toLocaleString()}</span>
                                                    </div>
                                                    <p style={{ fontSize: '0.9em' }}>Offering: {offer.quantity_offered} units</p>
                                                    <p style={{ fontSize: '0.9em' }}>Delivery: {new Date(offer.delivery_date).toLocaleDateString()}</p>

                                                    {offer.status === 'pending' && (
                                                        <button
                                                            className="btn-primary-sm"
                                                            style={{ width: '100%', marginTop: '10px' }}
                                                            onClick={() => onAcceptOffer(offer.id)}
                                                        >
                                                            Accept Offer
                                                        </button>
                                                    )}

                                                    {offer.status === 'accepted' && (
                                                        <div style={{ marginTop: '10px', background: '#e3f2fd', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
                                                            <small>Tracking ID:</small>
                                                            <h4 style={{ margin: '5px 0', letterSpacing: '1px' }}>{offer.tracking_id}</h4>
                                                            <small style={{ color: '#666' }}>Share this with the agent.</small>
                                                            <br />
                                                            <span style={{ fontSize: '0.8em', color: '#f39c12' }}>Waiting for Agent to Mark Delivered...</span>
                                                        </div>
                                                    )}

                                                    {offer.status === 'delivered' && (
                                                        <div style={{ marginTop: '10px', background: '#e8f5e9', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
                                                            <small style={{ color: 'green', fontWeight: 'bold' }}>Agent marked as Delivered!</small>
                                                            <p style={{ fontSize: '0.9em', margin: '5px 0' }}>Please confirm you received the items.</p>
                                                            <button
                                                                className="btn-primary-sm"
                                                                style={{ width: '100%', background: '#2ecc71' }}
                                                                onClick={async () => {
                                                                    const code = prompt("Enter the LAST 8 CHARACTERS of the Tracking ID to confirm receipt:");
                                                                    if (code) {
                                                                        try {
                                                                            await api.post(`/offers/${offer.id}/confirm-delivery`, { code });
                                                                            alert("Delivery Confirmed! Funds released.");
                                                                            if (onConfirmDelivery) onConfirmDelivery(offer.id); // Triggers refresh if parent handles it
                                                                            // window.location.reload(); // Simple refresh
                                                                        } catch (err) {
                                                                            console.error(err);
                                                                            alert(err.response?.data?.detail || "Confirmation failed");
                                                                        }
                                                                    }
                                                                }}
                                                            >
                                                                Confirm Receipt
                                                            </button>
                                                        </div>
                                                    )}

                                                    {offer.status === 'completed' && (
                                                        <div style={{ marginTop: '10px', textAlign: 'center', color: 'green' }}>
                                                            <strong>✓ Fulfilled & Paid</strong>
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))
                    }
                </div>
            )}
        </div>
    );
};

export default MyRequests;
