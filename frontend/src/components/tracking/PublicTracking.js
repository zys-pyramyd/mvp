import React, { useState } from 'react';
import axios from 'axios';
import '../../App.css'; // Global Styles

const PublicTracking = () => {
    const [trackingId, setTrackingId] = useState('');
    const [trackingData, setTrackingData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSearch = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setTrackingData(null);

        try {
            // Public Endpoint
            const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/tracking/${trackingId}`);
            setTrackingData(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || "Tracking ID not found or network error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h2 style={{ textAlign: 'center', color: '#2c3e50' }}>Track Your Order</h2>

            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <input
                    type="text"
                    value={trackingId}
                    onChange={(e) => setTrackingId(e.target.value.toUpperCase())}
                    placeholder="Enter Tracking ID (e.g. RFQ-TRK-1234)"
                    style={{ flex: 1, padding: '12px', fontSize: '16px', border: '1px solid #ddd', borderRadius: '4px' }}
                    required
                />
                <button
                    type="submit"
                    className="btn-primary"
                    disabled={loading}
                    style={{ padding: '0 30px' }}
                >
                    {loading ? 'Tracking...' : 'Track'}
                </button>
            </form>

            {error && (
                <div style={{ padding: '15px', background: '#fee', color: '#c0392b', borderRadius: '4px', marginTop: '20px', textAlign: 'center' }}>
                    {error}
                </div>
            )}

            {trackingData && (
                <div style={{ marginTop: '40px', background: 'white', padding: '30px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #eee', paddingBottom: '20px', marginBottom: '20px' }}>
                        <div>
                            <span style={{ fontSize: '14px', color: '#7f8c8d' }}>Tracking Number</span>
                            <h3 style={{ margin: '5px 0 0', color: '#34495e' }}>{trackingData.tracking_id}</h3>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <span style={{ fontSize: '14px', color: '#7f8c8d' }}>Current Status</span>
                            <h3 style={{ margin: '5px 0 0', color: '#27ae60' }}>{trackingData.status.toUpperCase()}</h3>
                        </div>
                    </div>

                    {/* Timeline */}
                    <div className="timeline">
                        {trackingData.logs.slice().reverse().map((log, index) => (
                            <div key={index} style={{ display: 'flex', gap: '20px', marginBottom: '25px', position: 'relative' }}>
                                {/* Dot & Line */}
                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                    <div style={{ width: '16px', height: '16px', background: index === 0 ? '#27ae60' : '#bdc3c7', borderRadius: '50%', zIndex: 2 }}></div>
                                    {index !== trackingData.logs.length - 1 && (
                                        <div style={{ flex: 1, width: '2px', background: '#ecf0f1', minHeight: '30px' }}></div>
                                    )}
                                </div>

                                {/* Content */}
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 'bold', fontSize: '16px', color: '#2c3e50' }}>{log.status}</div>
                                    <div style={{ fontSize: '14px', color: '#7f8c8d', marginTop: '4px' }}>
                                        {new Date(log.timestamp).toLocaleString()}
                                        {log.location && ` • ${log.location}`}
                                    </div>
                                    {log.note && (
                                        <div style={{ marginTop: '8px', fontSize: '14px', background: '#f8f9fa', padding: '8px', borderRadius: '4px', color: '#555' }}>
                                            "{log.note}"
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default PublicTracking;
