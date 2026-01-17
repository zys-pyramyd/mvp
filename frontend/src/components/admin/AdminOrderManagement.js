import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const AdminOrderManagement = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchOrders = async () => {
        try {
            setLoading(true);
            const response = await api.get('/admin/orders');
            setOrders(response.data.orders);
        } catch (error) {
            console.error("Failed to fetch orders", error);
            alert("Failed to load orders");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    const handleHaltPayout = async (orderId) => {
        if (!window.confirm("Are you sure you want to HALT payments for this order?")) return;
        try {
            await api.post(`/admin/orders/${orderId}/halt-payout`);
            alert("Payout Halted.");
            fetchOrders();
        } catch (error) {
            console.error(error);
            alert("Failed to halt payout");
        }
    };

    const handleManualRelease = async (orderId) => {
        if (!window.confirm("Are you sure you want to MANUALLY RELEASE funds? This overrides safety checks.")) return;
        try {
            await api.post(`/admin/orders/${orderId}/manual-release`);
            alert("Funds Released.");
            fetchOrders();
        } catch (error) {
            console.error(error);
            alert("Failed to release funds");
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <h2>Admin - Order Management</h2>
            <button onClick={fetchOrders} className="btn-secondary" style={{ marginBottom: '20px' }}>Refresh</button>

            {loading ? <p>Loading...</p> : (
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9em' }}>
                        <thead>
                            <tr style={{ background: '#eee', borderBottom: '2px solid #ddd' }}>
                                <th style={{ padding: '10px' }}>Order ID</th>
                                <th style={{ padding: '10px' }}>Buyer</th>
                                <th style={{ padding: '10px' }}>Seller</th>
                                <th style={{ padding: '10px' }}>Status</th>
                                <th style={{ padding: '10px' }}>Amount</th>
                                <th style={{ padding: '10px' }}>Date</th>
                                <th style={{ padding: '10px' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {orders.map(order => (
                                <tr key={order.order_id} style={{ borderBottom: '1px solid #eee', background: order.payout_halted ? '#ffebee' : 'white' }}>
                                    <td style={{ padding: '10px' }}>{order.order_id}</td>
                                    <td style={{ padding: '10px' }}>{order.buyer_username}</td>
                                    <td style={{ padding: '10px' }}>{order.seller_username}</td>
                                    <td style={{ padding: '10px' }}>
                                        <span style={{
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            background: order.status === 'delivered' ? '#e8f5e9' : '#f5f5f5',
                                            color: order.status === 'delivered' ? 'green' : 'black'
                                        }}>
                                            {order.status}
                                        </span>
                                        {order.payout_halted && <div style={{ color: 'red', fontWeight: 'bold', fontSize: '0.8em' }}>HALTED</div>}
                                    </td>
                                    <td style={{ padding: '10px' }}>₦{order.total_amount?.toLocaleString()}</td>
                                    <td style={{ padding: '10px' }}>{new Date(order.created_at).toLocaleDateString()}</td>
                                    <td style={{ padding: '10px' }}>
                                        <div style={{ display: 'flex', gap: '5px' }}>
                                            {!order.payout_halted && order.status !== 'completed' && (
                                                <button
                                                    onClick={() => handleHaltPayout(order.order_id)}
                                                    style={{ padding: '5px 10px', background: '#d32f2f', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                                                >
                                                    Halt Payout
                                                </button>
                                            )}
                                            {order.status !== 'completed' && (
                                                <button
                                                    onClick={() => handleManualRelease(order.order_id)}
                                                    style={{ padding: '5px 10px', background: '#388e3c', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                                                >
                                                    Release Funds
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default AdminOrderManagement;
