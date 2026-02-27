import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import OrderDetails from '../checkout/OrderDetails';
import './MyOrdersModal.css';

const MyOrdersModal = ({ onClose }) => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedOrderId, setSelectedOrderId] = useState(null);
    const [activeTab, setActiveTab] = useState('all');

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
            'pending_payment': '#ffeaa7',
            'held_in_escrow': '#74b9ff',
            'delivered': '#55efc4',
            'completed': '#81ecec',
            'cancelled': '#fab1a0'
        };
        return colors[status] || '#dfe6e9';
    };

    const filterOrders = () => {
        switch (activeTab) {
            case 'pending':
                return orders.filter(o => ['pending', 'held_in_escrow', 'pending_payment'].includes(o.status));
            case 'delivered':
                return orders.filter(o => o.status === 'delivered');
            case 'completed':
                return orders.filter(o => o.status === 'completed');
            case 'cancelled':
                return orders.filter(o => o.status === 'cancelled');
            default:
                return orders;
        }
    };

    const filteredOrders = filterOrders();

    const getTabCount = (tab) => {
        switch (tab) {
            case 'pending':
                return orders.filter(o => ['pending', 'held_in_escrow', 'pending_payment'].includes(o.status)).length;
            case 'delivered':
                return orders.filter(o => o.status === 'delivered').length;
            case 'completed':
                return orders.filter(o => o.status === 'completed').length;
            case 'cancelled':
                return orders.filter(o => o.status === 'cancelled').length;
            default:
                return orders.length;
        }
    };

    if (loading) {
        return (
            <div className="modal-overlay">
                <div className="modal-content orders-modal">
                    <div className="modal-header">
                        <h3>My Orders</h3>
                        <button className="close-button" onClick={onClose}>&times;</button>
                    </div>
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading your orders...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="modal-overlay">
            <div className="modal-content orders-modal">
                <div className="modal-header">
                    <h3>📦 My Orders</h3>
                    <button className="close-button" onClick={onClose}>&times;</button>
                </div>

                <div className="modal-body">
                    {/* Tabs */}
                    <div className="order-tabs">
                        <button
                            className={`tab-button ${activeTab === 'all' ? 'active' : ''}`}
                            onClick={() => setActiveTab('all')}
                        >
                            All <span className="tab-count">{getTabCount('all')}</span>
                        </button>
                        <button
                            className={`tab-button ${activeTab === 'pending' ? 'active' : ''}`}
                            onClick={() => setActiveTab('pending')}
                        >
                            Pending <span className="tab-count">{getTabCount('pending')}</span>
                        </button>
                        <button
                            className={`tab-button ${activeTab === 'delivered' ? 'active' : ''}`}
                            onClick={() => setActiveTab('delivered')}
                        >
                            Delivered <span className="tab-count">{getTabCount('delivered')}</span>
                        </button>
                        <button
                            className={`tab-button ${activeTab === 'completed' ? 'active' : ''}`}
                            onClick={() => setActiveTab('completed')}
                        >
                            Completed <span className="tab-count">{getTabCount('completed')}</span>
                        </button>
                        <button
                            className={`tab-button ${activeTab === 'cancelled' ? 'active' : ''}`}
                            onClick={() => setActiveTab('cancelled')}
                        >
                            Cancelled <span className="tab-count">{getTabCount('cancelled')}</span>
                        </button>
                    </div>

                    {/* Orders List */}
                    {filteredOrders.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon">📭</div>
                            <h4>No orders found</h4>
                            <p>
                                {activeTab === 'all'
                                    ? "You haven't placed any orders yet"
                                    : `No ${activeTab} orders`}
                            </p>
                        </div>
                    ) : (
                        <div className="orders-list">
                            {filteredOrders.map(order => (
                                <div key={order.order_id} className="order-card-compact">
                                    <div className="order-card-header-compact">
                                        <div className="order-id-compact">{order.order_id}</div>
                                        <span
                                            className="status-badge-compact"
                                            style={{ backgroundColor: getStatusColor(order.status) }}
                                        >
                                            {order.status.replace(/_/g, ' ').toUpperCase()}
                                        </span>
                                    </div>

                                    <div className="order-card-body-compact">
                                        <div className="order-info-compact">
                                            <span className="order-items-compact">
                                                {order.items ? order.items.length : (order.product_details ? 1 : 0)} item(s)
                                            </span>
                                            <span className="order-date-compact">
                                                {new Date(order.created_at).toLocaleDateString('en-US', {
                                                    month: 'short',
                                                    day: 'numeric'
                                                })}
                                            </span>
                                        </div>

                                        <div className="order-amount-compact">
                                            ₦{order.total_amount.toLocaleString()}
                                        </div>
                                    </div>

                                    <div className="order-card-footer-compact">
                                        <button
                                            className="btn-view-compact"
                                            onClick={() => setSelectedOrderId(order.order_id)}
                                        >
                                            View Details
                                        </button>

                                        {['pending', 'held_in_escrow'].includes(order.status) && (
                                            <span className="modifiable-badge">✓ Can modify</span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

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

export default MyOrdersModal;
