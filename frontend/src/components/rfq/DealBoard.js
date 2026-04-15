/**
 * DealBoard — Seller/Agent view of the RFQ marketplace.
 *
 * Tabs:
 *   Farm Deals  — Standard (open-bid) requests
 *   PyExpress   — Instant (take-job) requests
 *   My Offers   — Awaiting buyer response or action required
 *   My Jobs     — Accepted/in-progress/delivered jobs
 *
 * Clean-ups from previous version:
 *  - Bid form logic extracted to <OfferBidModal> (no duplication)
 *  - window.confirm() / alert() replaced with inline confirmation panel
 *  - "Mark as Delivered" added to accepted jobs in My Jobs tab
 *  - Notification toast replaces alert() for success/error feedback
 */

import React, { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import OfferBidModal from './OfferBidModal';
import '../../App.css';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const STATUS_COLORS = {
  pending:          'bg-gray-100 text-gray-700',
  accepted:         'bg-amber-100 text-amber-800',
  accepted_by_buyer:'bg-red-100 text-red-800',
  terms_rejected:   'bg-red-50 text-red-600',
  delivered:        'bg-blue-100 text-blue-800',
  completed:        'bg-emerald-100 text-emerald-800',
};

function CountdownTimer({ publishDate, expiryDate }) {
  const [label, setLabel] = useState('');

  useEffect(() => {
    if (!expiryDate) return;
    const tick = () => {
      const now = Date.now();
      if (publishDate && new Date(publishDate).getTime() > now) {
        const diff = new Date(publishDate).getTime() - now;
        const d = Math.floor(diff / 86400000);
        const h = Math.floor((diff % 86400000) / 3600000);
        setLabel(`Starts in ${d}d ${h}h`);
        return;
      }
      const dist = new Date(expiryDate).getTime() - now;
      if (dist < 0) { setLabel('Expired'); return; }
      const d = Math.floor(dist / 86400000);
      const h = Math.floor((dist % 86400000) / 3600000);
      const m = Math.floor((dist % 3600000) / 60000);
      setLabel(d > 0 ? `${d}d ${h}h left` : `${h}h ${m}m left`);
    };
    tick();
    const id = setInterval(tick, 60_000);
    return () => clearInterval(id);
  }, [publishDate, expiryDate]);

  return <span>{label}</span>;
}

function Toast({ toast, onDismiss }) {
  if (!toast) return null;
  return (
    <div
      className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium flex items-center gap-2 transition-all ${
        toast.type === 'success' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
      }`}
    >
      <span>{toast.type === 'success' ? '✅' : '❌'}</span>
      <span>{toast.message}</span>
      <button onClick={onDismiss} className="ml-2 opacity-70 hover:opacity-100">×</button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

const DealBoard = ({ requests = [], onRefresh, userRole }) => {
  const [activeTab,      setActiveTab]      = useState('FarmDeals');
  const [myOffers,       setMyOffers]       = useState([]);
  const [selectedRequest,setSelectedRequest]= useState(null); // drives OfferBidModal

  // Inline "Take Job" confirmation — avoids window.confirm()
  const [takeJobTarget,  setTakeJobTarget]  = useState(null); // { id, title }
  const [taking,         setTaking]         = useState(false);

  // Success/error notification
  const [toast, setToast] = useState(null);

  const showToast = useCallback((type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4000);
  }, []);

  const fetchMyOffers = useCallback(async () => {
    try {
      const { data } = await api.get('/requests/offers/mine');
      setMyOffers(data);
    } catch {
      // Non-blocking — offers simply won't refresh
    }
  }, []);

  // Load my offers on mount so My Offers / My Jobs tabs aren't empty on first open
  useEffect(() => { fetchMyOffers(); }, [fetchMyOffers]);

  // Filtered request lists
  const farmDeals  = requests.filter(r => r.status === 'active' && (r.platform === 'farm_deals'  || r.type === 'standard'));
  const pyExpress  = requests.filter(r => r.status === 'active' && (r.platform === 'pyexpress'   || r.type === 'instant'));
  const pendingOffers = myOffers.filter(o => ['pending', 'accepted_by_buyer', 'terms_rejected'].includes(o.status));
  const activeJobs    = myOffers.filter(o => ['accepted', 'delivered', 'completed'].includes(o.status));

  const actionRequiredCount = myOffers.filter(o => o.status === 'accepted_by_buyer').length;

  // ── Handlers ──────────────────────────────────────────────────────────────

  const confirmTakeJob = async () => {
    if (!takeJobTarget) return;
    setTaking(true);
    try {
      const { data } = await api.post(`/requests/${takeJobTarget.id}/take`);
      showToast('success', `Job taken! Tracking ID: ${data.tracking_id}`);
      setTakeJobTarget(null);
      if (onRefresh) onRefresh();
      fetchMyOffers();
    } catch (err) {
      showToast('error', err.response?.data?.detail || 'Failed to take job');
      setTakeJobTarget(null);
    } finally {
      setTaking(false);
    }
  };

  const handleMarkDelivered = async (offerId) => {
    try {
      await api.post(`/requests/offers/${offerId}/delivered`);
      showToast('success', 'Marked as delivered. Waiting for buyer confirmation.');
      fetchMyOffers();
    } catch (err) {
      showToast('error', err.response?.data?.detail || 'Error marking as delivered');
    }
  };

  const handleConfirmTerms = async (offerId) => {
    try {
      const { data } = await api.post(`/requests/offers/${offerId}/confirm-terms`);
      showToast('success', `Terms accepted! Order created: ${data.order_id}`);
      fetchMyOffers();
    } catch (err) {
      showToast('error', err.response?.data?.detail || 'Failed to confirm terms');
    }
  };

  const handleRejectTerms = async (offerId) => {
    try {
      await api.post(`/requests/offers/${offerId}/reject-terms`);
      showToast('success', 'Terms rejected. The buyer has been notified.');
      fetchMyOffers();
    } catch (err) {
      showToast('error', err.response?.data?.detail || 'Failed to reject terms');
    }
  };

  // ── Tab label helper ───────────────────────────────────────────────────────
  const tabs = [
    { key: 'FarmDeals', label: '🌾 Farm Deals',   count: null,               color: '#f39c12' },
    { key: 'PyExpress', label: '⚡ PyExpress',     count: null,               color: '#2ecc71' },
    { key: 'MyOffers',  label: '📋 My Offers',     count: actionRequiredCount, color: '#9b59b6' },
    { key: 'MyJobs',    label: '🚚 My Active Jobs', count: null,              color: '#3498db' },
  ];

  const switchTab = (key) => {
    setActiveTab(key);
    if (key === 'MyOffers' || key === 'MyJobs') fetchMyOffers();
  };

  // ── Card renderers ─────────────────────────────────────────────────────────

  const renderRequestCard = (req) => (
    <div key={req.id} className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm hover:shadow-md transition-shadow relative">
      <div className="absolute top-3 right-3">
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
          req.type === 'instant' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
        }`}>
          {req.type === 'instant' ? '⚡ Instant' : '🌾 Standard'}
        </span>
      </div>

      <h3 className="font-bold text-gray-900 text-base leading-snug pr-20 mb-1">
        {req.items?.[0]?.name || req.title || 'Request'}
        {req.items?.length > 1 && (
          <span className="text-xs text-gray-400 font-normal ml-1">+{req.items.length - 1} items</span>
        )}
      </h3>
      <p className="text-sm text-gray-500 mb-3">
        📍 {req.region_state || req.location}
        {req.expiry_date && (
          <span className="ml-2 text-amber-600 font-medium">
            ⏳ <CountdownTimer publishDate={req.publish_date} expiryDate={req.expiry_date} />
          </span>
        )}
      </p>

      {/* Items summary */}
      <div className="bg-gray-50 rounded-lg p-2.5 mb-3 space-y-1">
        {req.items?.slice(0, 3).map((item, i) => (
          <div key={i} className="flex justify-between text-xs text-gray-700">
            <span>{item.name}</span>
            <span className="text-gray-500">{item.quantity} {item.unit}</span>
          </div>
        ))}
        {req.items?.length > 3 && (
          <p className="text-xs text-gray-400">+{req.items.length - 3} more items</p>
        )}
      </div>

      {(req.price_range?.min || req.price_range?.max) && (
        <p className="text-sm text-emerald-700 font-medium mb-3">
          💰 Budget: ₦{req.price_range?.min?.toLocaleString()} – ₦{req.price_range?.max?.toLocaleString()}
        </p>
      )}

      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400">{req.offers_count || 0} bids</span>
        {req.type === 'instant' ? (
          <button
            onClick={() => setTakeJobTarget({ id: req.id, title: req.items?.[0]?.name || 'this job', price: req.fixed_price })}
            className="px-4 py-2 bg-emerald-600 text-white text-sm rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
          >
            ⚡ Take Job
          </button>
        ) : (
          <button
            onClick={() => setSelectedRequest(req)}
            className="px-4 py-2 bg-amber-500 text-white text-sm rounded-lg font-semibold hover:bg-amber-600 transition-colors"
          >
            Place Bid
          </button>
        )}
      </div>
    </div>
  );

  const renderOfferCard = (offer) => (
    <div key={offer.id} className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm relative">
      <div className="absolute top-3 right-3">
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${STATUS_COLORS[offer.status] || 'bg-gray-100 text-gray-700'}`}>
          {offer.status === 'accepted_by_buyer' ? '⚠️ Action Required' : offer.status.replace(/_/g, ' ')}
        </span>
      </div>

      <h3 className="font-bold text-gray-900 pr-28 mb-1">{offer.request_title || 'Unknown Request'}</h3>
      <p className="text-sm text-gray-500 mb-3">My Bid: <span className="font-semibold text-gray-800">₦{offer.price?.toLocaleString()}</span></p>

      {offer.status === 'accepted_by_buyer' && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg mb-3">
          <p className="text-sm text-amber-800 font-medium mb-2">🎉 Buyer accepted your bid! Review their terms and respond.</p>
          <div className="flex gap-2">
            <button
              onClick={() => handleRejectTerms(offer.id)}
              className="flex-1 py-2 bg-red-500 text-white text-sm rounded-lg font-medium hover:bg-red-600 transition-colors"
            >
              ✗ Reject
            </button>
            <button
              onClick={() => handleConfirmTerms(offer.id)}
              className="flex-1 py-2 bg-emerald-600 text-white text-sm rounded-lg font-medium hover:bg-emerald-700 transition-colors"
            >
              ✓ Accept & Create Order
            </button>
          </div>
        </div>
      )}

      {offer.status === 'terms_rejected' && (
        <div className="p-2.5 bg-red-50 rounded-lg text-sm text-red-700">
          ❌ You rejected the buyer's terms. They may re-negotiate.
        </div>
      )}
    </div>
  );

  const renderJobCard = (offer) => (
    <div key={offer.id} className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm relative">
      <div className="absolute top-3 right-3">
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${STATUS_COLORS[offer.status] || 'bg-gray-100 text-gray-700'}`}>
          {offer.status.replace(/_/g, ' ').toUpperCase()}
        </span>
      </div>

      <h3 className="font-bold text-gray-900 pr-24 mb-1">{offer.request_title || 'Unknown Request'}</h3>
      <p className="text-sm text-gray-500 mb-3">My Bid: <span className="font-semibold text-gray-800">₦{offer.price?.toLocaleString()}</span></p>

      {offer.status === 'accepted' && (
        <button
          onClick={() => handleMarkDelivered(offer.id)}
          className="w-full py-2.5 bg-blue-600 text-white text-sm rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          📦 Mark as Delivered
        </button>
      )}

      {offer.status === 'delivered' && (
        <div className="p-2.5 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
          ✅ Marked as delivered — waiting for buyer confirmation.
        </div>
      )}

      {offer.status === 'completed' && (
        <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-800">
          🎉 Completed. Payment has been released to your wallet.
        </div>
      )}
    </div>
  );

  const renderEmpty = (msg) => (
    <div className="col-span-full text-center py-16 text-gray-400">
      <div className="text-5xl mb-3">📭</div>
      <p className="text-sm">{msg}</p>
    </div>
  );

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="rfq-container p-4 sm:p-6">
      <Toast toast={toast} onDismiss={() => setToast(null)} />

      {/* Tab bar */}
      <div className="flex gap-1 border-b border-gray-100 mb-6 overflow-x-auto pb-px">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => switchTab(tab.key)}
            className={`relative px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.key
                ? 'text-gray-900 border-b-2'
                : 'text-gray-500 hover:text-gray-800'
            }`}
            style={activeTab === tab.key ? { borderColor: tab.color } : {}}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className="ml-1.5 bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5 font-bold">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Cards grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {activeTab === 'FarmDeals'  && (farmDeals.length  === 0 ? renderEmpty('No active Farm Deal requests.') : farmDeals.map(renderRequestCard))}
        {activeTab === 'PyExpress'  && (pyExpress.length  === 0 ? renderEmpty('No active PyExpress jobs.')     : pyExpress.map(renderRequestCard))}
        {activeTab === 'MyOffers'   && (pendingOffers.length === 0 ? renderEmpty('No pending offers.')         : pendingOffers.map(renderOfferCard))}
        {activeTab === 'MyJobs'     && (activeJobs.length    === 0 ? renderEmpty('No active jobs.')            : activeJobs.map(renderJobCard))}
      </div>

      {/* Bid modal */}
      <OfferBidModal
        request={selectedRequest}
        onClose={() => setSelectedRequest(null)}
        onSuccess={() => {
          setSelectedRequest(null);
          if (onRefresh) onRefresh();
        }}
      />

      {/* Inline "Take Job" confirmation — replaces window.confirm() */}
      {takeJobTarget && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl text-center">
            <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">⚡</span>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-1">Take This Job?</h3>
            <p className="text-gray-500 text-sm mb-1">{takeJobTarget.title}</p>
            {takeJobTarget.price && (
              <p className="text-emerald-600 font-bold text-lg mb-4">₦{takeJobTarget.price?.toLocaleString()}</p>
            )}
            <p className="text-xs text-gray-400 mb-5">
              By accepting, you agree to fulfil this order at the fixed price and timeline stated.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setTakeJobTarget(null)}
                className="flex-1 py-3 border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmTakeJob}
                disabled={taking}
                className="flex-1 py-3 bg-emerald-600 text-white rounded-xl font-semibold hover:bg-emerald-700 transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
              >
                {taking
                  ? <><div className="w-4 h-4 border-2 border-white/50 border-t-white rounded-full animate-spin flex-shrink-0" /> Confirming...</>
                  : '⚡ Confirm & Take'
                }
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DealBoard;
