import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import OrderDetails from '../checkout/OrderDetails';
import './MyOrders.css';

const MyOrders = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedOrderId, setSelectedOrderId] = useState(null);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            setLoading(true);
            const response = await api.get('/orders/');
            setOrders(response.data);
        } catch (error) {
            console.error('Failed to fetch orders:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        const colors = {
            'pending': '#ffeaa7',
            'held_in_escrow': '#74b9ff',
            'delivered': '#55efc4',
            'completed': '#81ecec',
            'cancelled': '#fab1a0'
        };
        return colors[status] || '#dfe6e9';
    };

    const filteredOrders = orders.filter(order => {
        if (filter === 'all') return true;
        if (filter === 'active') return ['pending', 'held_in_escrow', 'delivered'].includes(order.status);
        if (filter === 'completed') return order.status === 'completed';
        if (filter === 'cancelled') return order.status === 'cancelled';
        return true;
    });

    if (loading) {
        return (
            <div className="my-orders-container">
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading your orders...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="my-orders-container">
            <div className="orders-header">
                <h2>My Orders</h2>
                <div className="filter-buttons">
                    <button
                        className={filter === 'all' ? 'active' : ''}
                        onClick={() => setFilter('all')}
                    >
                        All ({orders.length})
                    </button>
                    <button
                        className={filter === 'active' ? 'active' : ''}
                        onClick={() => setFilter('active')}
                    >
                        Active ({orders.filter(o => ['pending', 'held_in_escrow', 'delivered'].includes(o.status)).length})
                    </button>
                    <button
                        className={filter === 'completed' ? 'active' : ''}
                        onClick={() => setFilter('completed')}
                    >
                        Completed ({orders.filter(o => o.status === 'completed').length})
                    </button>
                    <button
                        className={filter === 'cancelled' ? 'active' : ''}
                        onClick={() => setFilter('cancelled')}
                    >
                        Cancelled ({orders.filter(o => o.status === 'cancelled').length})
                    </button>
                </div>
            </div>

            {filteredOrders.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">📦</div>
                    <h3>No orders found</h3>
                    <p>
                        {filter === 'all'
                            ? "You haven't placed any orders yet"
                            : `No ${filter} orders`}
                    </p>
                </div>
            ) : (
                <div className="orders-grid">
                    {filteredOrders.map(order => (
                        <div key={order.order_id} className="order-card">
                            <div className="order-card-header">
                                <span className="order-id">{order.order_id}</span>
                                <span
                                    className="order-status"
                                    style={{ backgroundColor: getStatusColor(order.status) }}
                                >
                                    {order.status.replace(/_/g, ' ').toUpperCase()}
                                </span>
                            </div>

                            <div className="order-card-body">
                                <div className="order-info">
                                    <p className="order-items">
                                        {order.items.length} item(s)
                                    </p>
                                    <p className="order-date">
                                        {new Date(order.created_at).toLocaleDateString('en-US', {
                                            year: 'numeric',
                                            month: 'short',
                                            day: 'numeric'
                                        })}
                                    </p>
                                </div>

                                <div className="order-amount">
                                    ₦{order.total_amount.toLocaleString()}
                                </div>
                            </div>

                            <div className="order-card-footer">
                                <button
                                    className="btn-view-details"
                                    onClick={() => setSelectedOrderId(order.order_id)}
                                >
                                    View Details
                                </button>

                                {['pending', 'held_in_escrow'].includes(order.status) && (
                                    <span className="cancellable-badge">
                                        ✓ Can modify
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {selectedOrderId && (
                <OrderDetails
                    orderId={selectedOrderId}
                    onClose={() => setSelectedOrderId(null)}
                    onUpdate={fetchOrders}
                />
            )}
        </div>
    );
};

export default MyOrders;
