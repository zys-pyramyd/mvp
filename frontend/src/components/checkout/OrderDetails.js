import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import './OrderDetails.css';

const OrderDetails = ({ orderId, onClose, onUpdate }) => {
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedItems, setSelectedItems] = useState([]);
    const [actionLoading, setActionLoading] = useState(false);

    useEffect(() => {
        fetchOrderDetails();
    }, [orderId]);

    const fetchOrderDetails = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/orders/${orderId}`);
            setOrder(response.data);
        } catch (error) {
            console.error('Failed to fetch order:', error);
            alert('Failed to load order details');
        } finally {
            setLoading(false);
        }
    };


    if (loading) {
        return (
            <div className="modal-overlay">
                <div className="modal-content order-details-modal">
                    <div className="loading-spinner">Loading order details...</div>
                </div>
            </div>
        );
    }

    if (!order) {
        return null;
    }

    // Normalize items for unified/RFQ handling
    const orderItems = order.items || (order.product_details ? [{
        product_id: order.product_id || order.product_details.id,
        title: order.product_details.title || order.product_details.name,
        price_per_unit: order.product_details.price || order.product_details.price_per_unit,
        quantity: order.quantity,
        total: order.total_amount
    }] : []);

    const canModifyOrder = () => {
        return ['pending', 'held_in_escrow', 'pending_payment'].includes(order.status);
    };

    const handleSelectItem = (productId) => {
        setSelectedItems(prev =>
            prev.includes(productId)
                ? prev.filter(id => id !== productId)
                : [...prev, productId]
        );
    };

    const handleSelectAll = () => {
        if (selectedItems.length === orderItems.length) {
            setSelectedItems([]);
        } else {
            setSelectedItems(orderItems.map(item => item.product_id));
        }
    };

    const calculateSelectedTotal = () => {
        return orderItems
            .filter(item => selectedItems.includes(item.product_id))
            .reduce((sum, item) => sum + (item.total || (item.quantity * item.price_per_unit)), 0);
    };

    const handleRemoveItems = async () => {
        if (selectedItems.length === 0) {
            alert('Please select items to remove');
            return;
        }

        const selectedTotal = calculateSelectedTotal();
        const isFullCancellation = selectedItems.length === orderItems.length;

        const confirmMessage = isFullCancellation
            ? `Cancel entire order?\n\nRefund: ₦${selectedTotal.toLocaleString()}\n\nThis action cannot be undone.`
            : `Remove ${selectedItems.length} item(s)?\n\nRefund: ₦${selectedTotal.toLocaleString()}\nNew Total: ₦${(order.total_amount - selectedTotal).toLocaleString()}\n\nThis action cannot be undone.`;

        if (!confirm(confirmMessage)) return;

        setActionLoading(true);
        try {
            // If checking out via unified, user can't remove items, only cancel full order
            if (!order.items && order.product_details) {
                await handleCancelOrder(); // Redirect to cancel logic
                return;
            }

            const response = await api.post(`/orders/${orderId}/remove-items`, {
                product_ids: selectedItems
            });

            const { refund_processed, refund_amount, items_remaining, message } = response.data;

            if (items_remaining === 0) {
                // Full cancellation
                alert(`✅ ${message}\n\n💰 Refund: ₦${refund_amount.toLocaleString()}\n\nYour order has been cancelled.`);
                if (onUpdate) onUpdate();
                if (onClose) onClose();
            } else {
                // Partial removal
                alert(`✅ ${message}\n\n💰 Refund: ₦${refund_amount.toLocaleString()}\n📦 ${items_remaining} item(s) remaining`);
                setSelectedItems([]);
                fetchOrderDetails(); // Refresh to show updated order
            }
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to remove items');
        } finally {
            setActionLoading(false);
        }
    };

    const handleCancelOrder = async () => {
        if (!confirm(`Cancel this order?\n\nYou will receive a full refund of ₦${order.total_amount.toLocaleString()}\n\nThis action cannot be undone.`)) {
            return;
        }

        setActionLoading(true);
        try {
            const response = await api.post(`/orders/${orderId}/cancel`);
            const { refund_processed, refund_amount, message } = response.data;

            alert(`✅ ${message}\n\n💰 Refund: ₦${refund_amount.toLocaleString()}\n\nFunds have been returned to your wallet.`);

            if (onUpdate) onUpdate();
            if (onClose) onClose();
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to cancel order');
        } finally {
            setActionLoading(false);
        }
    };

    const handleConfirmDelivery = async () => {
        if (!confirm('Have you received this order?\n\nConfirming usage of funds will release payment to the seller.\nThis action helps sellers get paid faster!')) return;

        setActionLoading(true);
        try {
            await api.post(`/orders/${orderId}/confirm-delivery`);
            alert('✅ Delivery Confirmed!\nThank you for shopping with Pyramyd. The order is now complete.');
            if (onUpdate) onUpdate();
            if (onClose) onClose();
        } catch (error) {
            console.error('Delivery confirmation failed:', error);
            alert(error.response?.data?.detail || 'Failed to confirm delivery. Please try again.');
        } finally {
            setActionLoading(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content order-details-modal">
                <div className="modal-header">
                    <h3>Order Details</h3>
                    <button className="close-button" onClick={onClose}>&times;</button>
                </div>

                <div className="modal-body">
                    {/* Order Info */}
                    <div className="order-info-section">
                        <div className="info-row">
                            <span className="label">Order ID:</span>
                            <span className="value">{order.order_id}</span>
                        </div>
                        <div className="info-row">
                            <span className="label">Status:</span>
                            <span className={`status-badge status-${order.status}`}>
                                {order.status.replace(/_/g, ' ').toUpperCase()}
                            </span>
                        </div>
                        <div className="info-row">
                            <span className="label">Payment Method:</span>
                            <span className="value">{order.payment_method}</span>
                        </div>
                        <div className="info-row">
                            <span className="label">Total Amount:</span>
                            <span className="value total-amount">₦{order.total_amount.toLocaleString()}</span>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    {canModifyOrder() && (
                        <div className="order-actions">
                            {/* Logic for Multi-item vs Single Item Cancellation */}
                            {order.items && (
                                <button
                                    className="btn-select-all"
                                    onClick={handleSelectAll}
                                    disabled={actionLoading}
                                >
                                    {selectedItems.length === orderItems.length ? '☑️ Deselect All' : '☐ Select All'}
                                </button>
                            )}

                            {order.items && selectedItems.length > 0 && (
                                <button
                                    className="btn-remove-items"
                                    onClick={handleRemoveItems}
                                    disabled={actionLoading}
                                >
                                    {actionLoading ? '⏳ Processing...' : `🗑️ Remove ${selectedItems.length} Item(s) (₦${calculateSelectedTotal().toLocaleString()})`}
                                </button>
                            )}

                            {(selectedItems.length === 0 || !order.items) && (
                                <button
                                    className="btn-cancel-order"
                                    onClick={handleCancelOrder}
                                    disabled={actionLoading}
                                >
                                    {actionLoading ? '⏳ Cancelling...' : '❌ Cancel Entire Order'}
                                </button>
                            )}
                        </div>
                    )}

                    {/* Items List */}
                    <div className="order-items-section">
                        <h4>Order Items</h4>
                        {orderItems.map((item, index) => (
                            <div key={index} className="order-item">
                                {canModifyOrder() && order.items && (
                                    <input
                                        type="checkbox"
                                        className="item-checkbox"
                                        checked={selectedItems.includes(item.product_id)}
                                        onChange={() => handleSelectItem(item.product_id)}
                                        disabled={actionLoading}
                                    />
                                )}
                                <div className="item-details">
                                    <h5>{item.title}</h5>
                                    <p className="item-meta">
                                        Quantity: {item.quantity} × ₦{(item.price_per_unit || 0).toLocaleString()}
                                    </p>
                                </div>
                                <div className="item-total">
                                    ₦{(item.total || (item.quantity * item.price_per_unit) || 0).toLocaleString()}
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Refund Preview */}
                    {selectedItems.length > 0 && canModifyOrder() && (
                        <div className="refund-preview">
                            <div className="preview-row">
                                <span>Items to Remove:</span>
                                <span>{selectedItems.length}</span>
                            </div>
                            <div className="preview-row">
                                <span>Refund Amount:</span>
                                <span className="refund-amount">₦{calculateSelectedTotal().toLocaleString()}</span>
                            </div>
                            {selectedItems.length < orderItems.length && (
                                <div className="preview-row">
                                    <span>New Order Total:</span>
                                    <span className="new-total">₦{(order.total_amount - calculateSelectedTotal()).toLocaleString()}</span>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Delivery Address */}
                    <div className="delivery-section">
                        <h4>Delivery Address</h4>
                        <p>{order.delivery_address || 'Not specified'}</p>
                    </div>

                    {/* Status Message */}
                    {!canModifyOrder() && (
                        <div className="status-message">
                            <p>ℹ️ This order cannot be modified in its current status.</p>
                            {order.status === 'delivered' && (
                                <div className="delivery-confirm-action" style={{ marginTop: '10px', textAlign: 'center' }}>
                                    <p>Please confirm delivery to complete the order.</p>
                                    <button
                                        className="btn-confirm-delivery"
                                        onClick={handleConfirmDelivery}
                                        disabled={actionLoading}
                                        style={{
                                            backgroundColor: '#00b894',
                                            color: 'white',
                                            padding: '10px 20px',
                                            borderRadius: '5px',
                                            border: 'none',
                                            cursor: 'pointer',
                                            marginTop: '10px',
                                            fontWeight: 'bold'
                                        }}
                                    >
                                        {actionLoading ? 'Processing...' : '✅ Confirm Delivery'}
                                    </button>
                                </div>
                            )}
                            {order.status === 'completed' && <p>This order has been completed.</p>}
                            {order.status === 'cancelled' && <p>This order was cancelled.</p>}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default OrderDetails;
