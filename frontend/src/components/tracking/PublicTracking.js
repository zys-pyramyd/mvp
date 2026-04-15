/**
 * PublicTracking — Branded, animated order tracking page.
 *
 * Improvements over previous version:
 *  - Full Pyramyd brand identity (logo, colours, typography)
 *  - Animated timeline with status-aware dot colours
 *  - Responsive, mobile-first layout
 *  - Clear empty/error/loading states
 *  - No raw inline styles
 */

import React, { useState } from 'react';
import axios from 'axios';

// ---------------------------------------------------------------------------
// Status colour mapping
// ---------------------------------------------------------------------------

const STATUS_STYLE = {
  picked_up:  { bg: 'bg-blue-500',    ring: 'ring-blue-200'   },
  in_transit: { bg: 'bg-amber-500',   ring: 'ring-amber-200'  },
  delivered:  { bg: 'bg-emerald-500', ring: 'ring-emerald-200'},
  cancelled:  { bg: 'bg-red-400',     ring: 'ring-red-200'    },
  default:    { bg: 'bg-gray-300',    ring: 'ring-gray-100'   },
};

const statusStyle = (s) => STATUS_STYLE[s?.toLowerCase()] || STATUS_STYLE.default;

const CURRENT_STATUS_BADGE = {
  picked_up:  'bg-blue-100 text-blue-800',
  in_transit: 'bg-amber-100 text-amber-900',
  delivered:  'bg-emerald-100 text-emerald-800',
  cancelled:  'bg-red-100 text-red-800',
};

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function SearchBar({ value, onChange, onSubmit, loading }) {
  return (
    <form onSubmit={onSubmit} className="flex gap-2 w-full max-w-xl mx-auto">
      <input
        type="text"
        value={value}
        onChange={e => onChange(e.target.value.toUpperCase())}
        placeholder="Enter Tracking ID — e.g. RFQ-TRK-1234"
        required
        className="flex-1 px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white shadow-sm"
      />
      <button
        type="submit"
        disabled={loading}
        className="px-6 py-3 bg-emerald-600 text-white rounded-xl font-semibold text-sm hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors flex items-center gap-2 shadow-sm"
      >
        {loading ? (
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        )}
        {loading ? 'Tracking…' : 'Track'}
      </button>
    </form>
  );
}

function TimelineDot({ s, isFirst, isLast }) {
  const st = statusStyle(s.status);
  return (
    <div className="flex flex-col items-center">
      <div className={`w-4 h-4 rounded-full ${st.bg} ring-4 ${isFirst ? st.ring : 'ring-gray-100'} flex-shrink-0 z-10`} />
      {!isLast && <div className="w-0.5 flex-1 bg-gray-200 mt-1 min-h-[32px]" />}
    </div>
  );
}

function TimelineEntry({ log, isFirst, isLast }) {
  return (
    <div className="flex gap-4">
      <TimelineDot s={log} isFirst={isFirst} isLast={isLast} />
      <div className={`pb-6 ${isLast ? 'pb-0' : ''} flex-1`}>
        <p className={`font-semibold text-sm ${isFirst ? 'text-gray-900' : 'text-gray-500'}`}>
          {log.status}
        </p>
        <p className="text-xs text-gray-400 mt-0.5">
          {new Date(log.timestamp).toLocaleString('en-NG', {
            day: 'numeric', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit',
          })}
          {log.location && <span className="ml-2">• {log.location}</span>}
        </p>
        {log.note && (
          <p className="mt-1.5 text-xs text-gray-500 bg-gray-50 px-3 py-2 rounded-lg border border-gray-100">
            "{log.note}"
          </p>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

const PublicTracking = () => {
  const [trackingId,   setTrackingId]   = useState('');
  const [trackingData, setTrackingData] = useState(null);
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]        = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setTrackingData(null);

    try {
      const { data } = await axios.get(
        `${process.env.REACT_APP_BACKEND_URL}/api/tracking/${trackingId}`
      );
      setTrackingData(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Tracking ID not found. Please check and try again.');
    } finally {
      setLoading(false);
    }
  };

  const logs = trackingData?.logs ? [...trackingData.logs].reverse() : [];
  const currentStatus = trackingData?.status?.toLowerCase();
  const badgeClass = CURRENT_STATUS_BADGE[currentStatus] || 'bg-gray-100 text-gray-700';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50/30">

      {/* ── Hero header ── */}
      <div className="bg-white border-b border-gray-100 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 py-8 text-center">
          <div className="inline-flex items-center gap-2 bg-emerald-50 px-3 py-1.5 rounded-full mb-4">
            <span className="text-emerald-600 text-sm font-semibold">🌾 Pyramyd Hub</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
            Track Your Order
          </h1>
          <p className="text-gray-500 text-sm mb-6">
            Enter your tracking ID to see real-time status updates.
          </p>
          <SearchBar
            value={trackingId}
            onChange={setTrackingId}
            onSubmit={handleSearch}
            loading={loading}
          />
        </div>
      </div>

      {/* ── Content area ── */}
      <div className="max-w-3xl mx-auto px-4 py-8">

        {/* Error state */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-sm text-red-700 flex items-start gap-2.5 shadow-sm">
            <span className="text-lg flex-shrink-0">⚠️</span>
            <div>
              <p className="font-semibold mb-0.5">Tracking not found</p>
              <p className="text-red-600 opacity-80">{error}</p>
            </div>
          </div>
        )}

        {/* Empty prompt */}
        {!trackingData && !error && !loading && (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">📦</span>
            </div>
            <h2 className="text-gray-700 font-semibold mb-1">Enter your tracking ID above</h2>
            <p className="text-gray-400 text-sm">You'll find it in your order confirmation or receipt.</p>
          </div>
        )}

        {/* Results */}
        {trackingData && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">

            {/* Result header */}
            <div className="flex items-start justify-between px-6 py-5 border-b border-gray-100">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Tracking Number</p>
                <p className="font-bold text-gray-900 font-mono text-lg">{trackingData.tracking_id}</p>
                {trackingData.product_name && (
                  <p className="text-sm text-gray-500 mt-0.5">{trackingData.product_name}</p>
                )}
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Status</p>
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${badgeClass}`}>
                  {trackingData.status}
                </span>
              </div>
            </div>

            {/* Estimated delivery */}
            {trackingData.estimated_delivery && (
              <div className="px-6 py-3 bg-emerald-50 border-b border-emerald-100">
                <p className="text-xs text-emerald-700">
                  📅 Estimated Delivery:{' '}
                  <strong>
                    {new Date(trackingData.estimated_delivery).toLocaleDateString('en-NG', {
                      weekday: 'short', day: 'numeric', month: 'long',
                    })}
                  </strong>
                </p>
              </div>
            )}

            {/* Timeline */}
            <div className="px-6 py-5">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-5">
                Shipment History
              </h3>
              {logs.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-4">
                  No tracking updates yet. Check back soon.
                </p>
              ) : (
                <div>
                  {logs.map((log, idx) => (
                    <TimelineEntry
                      key={idx}
                      log={log}
                      isFirst={idx === 0}
                      isLast={idx === logs.length - 1}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Footer note */}
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
              <p className="text-xs text-gray-400 text-center">
                Updates may take up to 10 minutes to reflect.{' '}
                <a href="mailto:support@pyramydhub.com" className="text-emerald-600 hover:underline">
                  Contact support
                </a>{' '}
                if you need help.
              </p>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default PublicTracking;
