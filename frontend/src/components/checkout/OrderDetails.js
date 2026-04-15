/**
 * OrderDetails — Order detail modal for buyers.
 *
 * Design principles:
 *  - NO browser alert() / confirm() dialogs.  All confirmation flows are
 *    inline within the modal using a <ConfirmPanel> component.
 *  - When order.status === 'delivered', a prominent delivery banner is shown
 *    at the TOP of the modal — not buried in a conditional block.
 *  - Notification toast replaces alert() for success/error feedback.
 *  - Full status-colour system via CSS custom properties.
 */

import React, { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import './OrderDetails.css';

// ---------------------------------------------------------------------------
// Status helpers
// ---------------------------------------------------------------------------

const STATUS_META = {
  pending:          { label: 'Pending',           cls: 'status-pending'   },
  pending_payment:  { label: 'Awaiting Payment',  cls: 'status-pending'   },
  held_in_escrow:   { label: 'Held in Escrow',    cls: 'status-escrow'    },
  processing:       { label: 'Processing',        cls: 'status-processing'},
  shipped:          { label: 'Shipped',            cls: 'status-shipped'   },
  delivered:        { label: 'Delivered',          cls: 'status-delivered' },
  completed:        { label: 'Completed',          cls: 'status-completed' },
  cancelled:        { label: 'Cancelled',          cls: 'status-cancelled' },
};

const statusMeta = (status) =>
  STATUS_META[status] || { label: status?.replace(/_/g, ' '), cls: 'status-pending' };

const canModify = (status) =>
  ['pending', 'held_in_escrow', 'pending_payment'].includes(status);

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function InlineSpinner() {
  return <div className="od-spinner" />;
}

function Toast({ toast }) {
  if (!toast) return null;
  return (
    <div className={`od-toast od-toast--${toast.type}`}>
      {toast.type === 'success' ? '✅' : '❌'} {toast.message}
    </div>
  );
}

/**
 * ConfirmPanel — replaces window.confirm().
 * Slides in at the bottom of the modal body.
 */
function ConfirmPanel({ action, order, selectedItemCount, selectedTotal, onConfirm, onCancel, loading }) {
  if (!action) return null;

  const isDelivery  = action === 'delivery';
  const isCancel    = action === 'cancel';
  const isRemove    = action === 'remove';

  return (
    <div className="od-confirm-panel">
      {isDelivery && (
        <>
          <div className="od-confirm-icon od-confirm-icon--green">🛡️</div>
          <h4 className="od-confirm-title">Confirm Delivery Receipt</h4>
          <p className="od-confirm-desc">
            Confirming will release{' '}
            <strong>₦{order.total_amount?.toLocaleString()}</strong> from escrow to the seller.
          </p>
          <p className="od-confirm-note">Only confirm once you've physically received your items.</p>
        </>
      )}
      {isCancel && (
        <>
          <div className="od-confirm-icon od-confirm-icon--red">🚫</div>
          <h4 className="od-confirm-title">Cancel Entire Order?</h4>
          <p className="od-confirm-desc">
            You'll receive a full refund of{' '}
            <strong>₦{order.total_amount?.toLocaleString()}</strong> to your wallet.
          </p>
          <p className="od-confirm-note">This action cannot be undone.</p>
        </>
      )}
      {isRemove && (
        <>
          <div className="od-confirm-icon od-confirm-icon--amber">🗑️</div>
          <h4 className="od-confirm-title">Remove {selectedItemCount} Item{selectedItemCount !== 1 ? 's' : ''}?</h4>
          <p className="od-confirm-desc">
            Refund of <strong>₦{selectedTotal?.toLocaleString()}</strong> will be returned to your wallet.
          </p>
          <p className="od-confirm-note">
            {selectedItemCount === (order.items?.length ?? 1)
              ? 'This will cancel the entire order.'
              : `${(order.items?.length ?? 1) - selectedItemCount} item(s) will remain in the order.`}
          </p>
        </>
      )}
      <div className="od-confirm-actions">
        <button className="od-btn od-btn--ghost" onClick={onCancel} disabled={loading}>
          Go Back
        </button>
        <button
          className={`od-btn ${isDelivery ? 'od-btn--green' : isCancel ? 'od-btn--red' : 'od-btn--amber'}`}
          onClick={onConfirm}
          disabled={loading}
        >
          {loading ? <><InlineSpinner /> Processing...</> : isDelivery ? '✅ Yes, Confirm Receipt' : isCancel ? '🚫 Yes, Cancel Order' : '🗑️ Remove Items'}
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

const OrderDetails = ({ orderId, onClose, onUpdate }) => {
  const [order,         setOrder]         = useState(null);
  const [loading,       setLoading]       = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [pendingAction, setPendingAction] = useState(null); // 'delivery' | 'cancel' | 'remove'
  const [toast,         setToast]         = useState(null);

  const showToast = useCallback((type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4500);
  }, []);

  const fetchOrder = useCallback(async () => {
    try {
      setLoading(true);
      const { data } = await api.get(`/orders/${orderId}`);
      setOrder(data);
    } catch {
      showToast('error', 'Failed to load order details. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [orderId, showToast]);

  useEffect(() => { fetchOrder(); }, [fetchOrder]);

  // ── Derived values ────────────────────────────────────────────────────────

  const orderItems = order
    ? order.items || (order.product_details ? [{
        product_id:     order.product_id || order.product_details.id,
        title:          order.product_details.title || order.product_details.name,
        price_per_unit: order.product_details.price || order.product_details.price_per_unit,
        quantity:       order.quantity,
        total:          order.total_amount,
      }] : [])
    : [];

  const selectedTotal = orderItems
    .filter(i => selectedItems.includes(i.product_id))
    .reduce((sum, i) => sum + (i.total || (i.quantity * i.price_per_unit) || 0), 0);

  // ── Select helpers ────────────────────────────────────────────────────────

  const toggleItem    = (id) => setSelectedItems(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  const toggleAll     = ()  => setSelectedItems(prev => prev.length === orderItems.length ? [] : orderItems.map(i => i.product_id));

  // ── API actions ───────────────────────────────────────────────────────────

  const executeAction = async () => {
    setActionLoading(true);
    try {
      if (pendingAction === 'delivery') {
        await api.post(`/orders/${orderId}/confirm-delivery`);
        showToast('success', '✅ Delivery confirmed! Payment has been released to the seller.');
        setPendingAction(null);
        if (onUpdate) onUpdate();
        if (onClose)  onClose();

      } else if (pendingAction === 'cancel') {
        const { data } = await api.post(`/orders/${orderId}/cancel`);
        showToast('success', `Order cancelled. ₦${data.refund_amount?.toLocaleString()} refunded to your wallet.`);
        setPendingAction(null);
        if (onUpdate) onUpdate();
        if (onClose)  onClose();

      } else if (pendingAction === 'remove') {
        const isFullCancel = selectedItems.length === orderItems.length;

        if (isFullCancel || !order.items) {
          // Single-item orders — just cancel
          const { data } = await api.post(`/orders/${orderId}/cancel`);
          showToast('success', `Order cancelled. ₦${data.refund_amount?.toLocaleString()} refunded to your wallet.`);
          setPendingAction(null);
          if (onUpdate) onUpdate();
          if (onClose)  onClose();
        } else {
          const { data } = await api.post(`/orders/${orderId}/remove-items`, { product_ids: selectedItems });
          showToast('success', `Items removed. ₦${data.refund_amount?.toLocaleString()} refunded to your wallet.`);
          setSelectedItems([]);
          setPendingAction(null);
          fetchOrder();
          if (onUpdate) onUpdate();
        }
      }
    } catch (err) {
      showToast('error', err.response?.data?.detail || 'Action failed. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };

  // ── Loading / null states ─────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="od-overlay">
        <div className="od-modal">
          <div className="od-loading">
            <div className="od-spinner od-spinner--lg" />
            <p>Loading order details…</p>
          </div>
        </div>
      </div>
    );
  }

  if (!order) return null;

  const meta    = statusMeta(order.status);
  const modifiable = canModify(order.status);

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="od-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="od-modal">
        <Toast toast={toast} />

        {/* ── Delivery prompt banner — shown prominently when delivered ── */}
        {order.status === 'delivered' && !pendingAction && (
          <div className="od-delivery-banner">
            <div className="od-delivery-banner__icon">📦</div>
            <div className="od-delivery-banner__body">
              <p className="od-delivery-banner__title">Your order has arrived!</p>
              <p className="od-delivery-banner__sub">
                Confirm receipt to release payment from escrow to the seller.
              </p>
            </div>
            <button
              className="od-delivery-banner__cta"
              onClick={() => setPendingAction('delivery')}
            >
              Confirm Delivery
            </button>
          </div>
        )}

        {/* ── Header ── */}
        <div className="od-header">
          <div>
            <p className="od-order-id">Order #{order.order_id}</p>
            <span className={`od-status-badge ${meta.cls}`}>{meta.label}</span>
          </div>
          <button className="od-close" onClick={onClose} aria-label="Close">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* ── Body ── */}
        <div className="od-body">

          {/* Inline confirm panel replaces window.confirm() */}
          {pendingAction ? (
            <ConfirmPanel
              action={pendingAction}
              order={order}
              selectedItemCount={selectedItems.length}
              selectedTotal={selectedTotal}
              onConfirm={executeAction}
              onCancel={() => setPendingAction(null)}
              loading={actionLoading}
            />
          ) : (
            <>
              {/* ── Order meta ── */}
              <section className="od-section">
                <div className="od-meta-grid">
                  <div className="od-meta-row">
                    <span className="od-meta-label">Payment</span>
                    <span className="od-meta-value">{order.payment_method ?? '—'}</span>
                  </div>
                  <div className="od-meta-row">
                    <span className="od-meta-label">Total</span>
                    <span className="od-meta-value od-meta-value--total">
                      ₦{order.total_amount?.toLocaleString()}
                    </span>
                  </div>
                  {order.created_at && (
                    <div className="od-meta-row">
                      <span className="od-meta-label">Placed</span>
                      <span className="od-meta-value">
                        {new Date(order.created_at).toLocaleDateString('en-NG', {
                          day: 'numeric', month: 'short', year: 'numeric'
                        })}
                      </span>
                    </div>
                  )}
                </div>
              </section>

              {/* ── Items ── */}
              <section className="od-section">
                <div className="od-section-header">
                  <h4 className="od-section-title">Items</h4>
                  {modifiable && order.items && (
                    <button className="od-select-all" onClick={toggleAll}>
                      {selectedItems.length === orderItems.length ? 'Deselect All' : 'Select All'}
                    </button>
                  )}
                </div>

                <div className="od-items-list">
                  {orderItems.map((item, i) => (
                    <div
                      key={i}
                      className={`od-item ${selectedItems.includes(item.product_id) ? 'od-item--selected' : ''}`}
                      onClick={() => modifiable && order.items && toggleItem(item.product_id)}
                    >
                      {modifiable && order.items && (
                        <input
                          type="checkbox"
                          className="od-checkbox"
                          checked={selectedItems.includes(item.product_id)}
                          onChange={() => toggleItem(item.product_id)}
                          onClick={e => e.stopPropagation()}
                        />
                      )}
                      <div className="od-item__info">
                        <p className="od-item__title">{item.title}</p>
                        <p className="od-item__meta">
                          {item.quantity} × ₦{(item.price_per_unit || 0).toLocaleString()}
                        </p>
                      </div>
                      <span className="od-item__total">
                        ₦{(item.total || (item.quantity * item.price_per_unit) || 0).toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Refund preview when items selected */}
                {selectedItems.length > 0 && modifiable && (
                  <div className="od-refund-preview">
                    <div className="od-refund-row">
                      <span>Items selected</span><span>{selectedItems.length}</span>
                    </div>
                    <div className="od-refund-row od-refund-row--highlight">
                      <span>Refund amount</span>
                      <span>₦{selectedTotal.toLocaleString()}</span>
                    </div>
                    {selectedItems.length < orderItems.length && (
                      <div className="od-refund-row">
                        <span>Remaining total</span>
                        <span>₦{(order.total_amount - selectedTotal).toLocaleString()}</span>
                      </div>
                    )}
                  </div>
                )}
              </section>

              {/* ── Delivery address ── */}
              <section className="od-section">
                <h4 className="od-section-title">Delivery Address</h4>
                <p className="od-address">{order.delivery_address || 'Not specified'}</p>
              </section>

              {/* ── Action footer ── */}
              {modifiable && (
                <section className="od-section od-actions">
                  {order.items && selectedItems.length > 0 ? (
                    <button
                      className="od-btn od-btn--amber"
                      onClick={() => setPendingAction('remove')}
                      disabled={actionLoading}
                    >
                      🗑️ Remove {selectedItems.length} Item{selectedItems.length !== 1 ? 's' : ''}
                    </button>
                  ) : (
                    <button
                      className="od-btn od-btn--red"
                      onClick={() => setPendingAction('cancel')}
                      disabled={actionLoading}
                    >
                      Cancel Order
                    </button>
                  )}
                </section>
              )}

              {/* ── Status info for non-modifiable states ── */}
              {!modifiable && order.status !== 'delivered' && (
                <section className="od-section">
                  <div className={`od-status-info od-status-info--${order.status}`}>
                    {order.status === 'completed' && '🎉 This order has been completed successfully.'}
                    {order.status === 'cancelled' && '🚫 This order was cancelled and refunded.'}
                    {!['completed', 'cancelled', 'delivered'].includes(order.status) &&
                      'ℹ️ This order is currently being processed and cannot be modified.'
                    }
                  </div>
                </section>
              )}

            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrderDetails;
