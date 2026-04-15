/**
 * RequestsPage — Buyer's view of active RFQ requests (seller/agent can make offers).
 *
 * Clean-ups:
 *  - Fixed critical URL bug: `/requests₦${params}` → `/requests?${params}`
 *  - Duplicate bid form (~130 lines) removed; now uses <OfferBidModal>
 *  - alert() replaced with an inline notification banner
 *  - Locations fetched from a dedicated endpoint to avoid double-fetch
 *  - Empty, loading, and error states handled explicitly
 */

import React, { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import OfferBidModal from './OfferBidModal';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function TypeBadge({ type }) {
  return type === 'instant'
    ? <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">⚡ Instant</span>
    : <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800">🌾 Standard</span>;
}

function InlineNotification({ note, onDismiss }) {
  if (!note) return null;
  return (
    <div className={`flex items-center justify-between gap-3 px-4 py-3 rounded-xl text-sm font-medium mb-4 ${
      note.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                               : 'bg-red-50 text-red-800 border border-red-200'
    }`}>
      <span>{note.type === 'success' ? '✅' : '❌'} {note.message}</span>
      <button onClick={onDismiss} className="text-current opacity-60 hover:opacity-100 text-lg leading-none">×</button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

const RequestsPage = ({ userRole, onClose }) => {
  const [requests,  setRequests]  = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);
  const [filters,   setFilters]   = useState({
    status: 'active',
    type:   'all',
    location: '',
  });

  // Bid modal state — drives <OfferBidModal>
  const [selectedRequest, setSelectedRequest] = useState(null);

  // Inline notification (replaces alert())
  const [note, setNote] = useState(null);
  const showNote = useCallback((type, message) => {
    setNote({ type, message });
    setTimeout(() => setNote(null), 4500);
  }, []);

  const fetchRequests = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // ✅ Fixed: was `/requests₦${params}` — the ₦ broke every filter call
      const params = new URLSearchParams();
      if (filters.status)         params.append('status',   filters.status);
      if (filters.type !== 'all') params.append('type',     filters.type);
      if (filters.location)       params.append('location', filters.location);

      const { data } = await api.get(`/requests?${params.toString()}`);
      const list = data || [];
      setRequests(list);

      // Derive location options from results — avoids a second GET /requests
      if (filters.type === 'all' && !filters.location) {
        setLocations(prev => {
          const merged = [...new Set([...prev, ...list.map(r => r.location).filter(Boolean)])];
          return merged;
        });
      }
    } catch {
      setError('Failed to load requests. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  // Auto-refresh every 30 s
  useEffect(() => {
    const id = setInterval(fetchRequests, 30_000);
    return () => clearInterval(id);
  }, [fetchRequests]);

  const canBid = ['agent', 'farmer', 'business'].includes(userRole);

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50">

      {/* ── Sticky header ── */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-xl font-bold text-gray-900">🎯 Buyer Requests</h1>
              <p className="text-xs text-gray-500 mt-0.5">Browse and respond to live procurement requests</p>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Status tabs */}
          <div className="flex border-b border-gray-200 mb-3 -mx-1">
            {[
              { key: 'active',    label: 'Live Requests' },
              { key: 'completed', label: 'Delivered'     },
              { key: 'on_hold',   label: 'On Hold'       },
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setFilters(f => ({ ...f, status: tab.key }))}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  filters.status === tab.key
                    ? 'border-emerald-500 text-emerald-700'
                    : 'border-transparent text-gray-500 hover:text-gray-800'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Type + location filters */}
          <div className="flex flex-wrap items-center gap-2">
            {[
              { key: 'all',      label: 'All'                  },
              { key: 'standard', label: '🌾 Farm Deals'        },
              { key: 'instant',  label: '⚡ PyExpress (Instant)'},
            ].map(f => (
              <button
                key={f.key}
                onClick={() => setFilters(prev => ({ ...prev, type: f.key }))}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  filters.type === f.key
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {f.label}
              </button>
            ))}

            {locations.length > 0 && (
              <select
                value={filters.location}
                onChange={e => setFilters(prev => ({ ...prev, location: e.target.value }))}
                className="px-3 py-1.5 border border-gray-200 rounded-lg text-xs bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 text-gray-700"
              >
                <option value="">All Locations</option>
                {locations.map(loc => <option key={loc} value={loc}>{loc}</option>)}
              </select>
            )}

            <button
              onClick={fetchRequests}
              className="ml-auto px-3 py-1.5 text-xs text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg flex items-center gap-1 transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* ── Content ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <InlineNotification note={note} onDismiss={() => setNote(null)} />

        {loading ? (
          <div className="text-center py-16">
            <div className="w-10 h-10 border-2 border-gray-200 border-t-emerald-500 rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-gray-500">Loading requests…</p>
          </div>
        ) : error ? (
          <div className="text-center py-16">
            <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">⚠️</span>
            </div>
            <p className="text-gray-700 font-medium mb-2">{error}</p>
            <button
              onClick={fetchRequests}
              className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : requests.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
            <div className="text-5xl mb-3">📭</div>
            <h3 className="text-base font-semibold text-gray-900 mb-1">No Requests Found</h3>
            <p className="text-sm text-gray-500">Try adjusting your filters or check back soon.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {requests.map(req => (
              <article
                key={req.id}
                className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1 min-w-0 pr-3">
                    <h3 className="font-bold text-gray-900 text-base leading-snug truncate">
                      {req.items?.[0]?.name}
                      {req.items?.length > 1 && (
                        <span className="text-xs text-gray-400 font-normal ml-1">
                          +{req.items.length - 1} more
                        </span>
                      )}
                    </h3>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {new Date(req.created_at).toLocaleDateString('en-NG', {
                        day: 'numeric', month: 'short', year: 'numeric',
                      })}
                    </p>
                  </div>
                  <TypeBadge type={req.type} />
                </div>

                <div className="space-y-1.5 mb-4 text-sm">
                  <div className="flex gap-2">
                    <span className="text-gray-400 w-20 flex-shrink-0">Quantity</span>
                    <span className="font-medium text-gray-800">
                      {req.items?.[0]?.quantity} {req.items?.[0]?.unit}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-gray-400 w-20 flex-shrink-0">Location</span>
                    <span className="font-medium text-gray-800">📍 {req.location}</span>
                  </div>
                  {req.price_range?.min && (
                    <div className="flex gap-2">
                      <span className="text-gray-400 w-20 flex-shrink-0">Budget</span>
                      <span className="font-medium text-emerald-700">
                        ₦{req.price_range.min.toLocaleString()}
                        {req.price_range.max && ` – ₦${req.price_range.max.toLocaleString()}`}
                      </span>
                    </div>
                  )}
                  <div className="flex gap-2">
                    <span className="text-gray-400 w-20 flex-shrink-0">Delivery</span>
                    <span className="font-medium text-gray-800">
                      {req.type === 'instant'
                        ? `${req.delivery_hours || 6} hrs`
                        : `${req.delivery_days} days`}
                    </span>
                  </div>
                </div>

                {canBid && (
                  <button
                    onClick={() => setSelectedRequest(req)}
                    className="w-full py-2.5 bg-emerald-600 text-white rounded-lg text-sm font-semibold hover:bg-emerald-700 transition-colors"
                  >
                    Make Offer
                  </button>
                )}
              </article>
            ))}
          </div>
        )}
      </div>

      {/* ── Shared bid modal ── */}
      <OfferBidModal
        request={selectedRequest}
        onClose={() => setSelectedRequest(null)}
        onSuccess={() => {
          setSelectedRequest(null);
          fetchRequests();
          showNote('success', 'Your bid has been submitted successfully!');
        }}
      />
    </div>
  );
};

export default RequestsPage;
