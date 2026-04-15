/**
 * OfferBidModal — Shared bid/offer form component.
 *
 * Used by both DealBoard (seller/agent view) and RequestsPage.
 * Eliminates the ~130-line duplication that previously existed in both files.
 *
 * Props:
 *   request  {object|null} — the RFQ request being bid on; null = closed
 *   onClose  {function}    — called when the modal should close
 *   onSuccess{function}    — called after a successful submission
 */

import React, { useState, useCallback, useEffect } from 'react';
import api from '../../services/api';

const UNIT_OPTIONS = [
  'Tonnes', 'Crates', 'Baskets', 'Barrels',
  'Bags (50kg)', 'Bags (25kg)',
  'Truck (6-wheeler)', 'Truck (10-wheeler)',
  'Truck (12-wheeler)', 'Truck (14-wheeler)',
  'Custom',
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildInitialRows(request) {
  return (request?.items || []).map(item => ({
    name:       item.name,
    quantity:   item.quantity || '',
    unit:       item.unit || 'Tonnes',
    unit_price: '',
    total:      0,
  }));
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

// Spinner uses fixed classes so PurgeCSS never strips them in production.
// Variants: default (white border for dark bg), 'muted' (gray border for light bg)
function Spinner({ muted = false }) {
  return (
    <div
      className={`w-4 h-4 border-2 border-t-transparent rounded-full animate-spin flex-shrink-0 ${
        muted ? 'border-gray-300 border-t-emerald-500' : 'border-white/40 border-t-white'
      }`}
    />
  );
}

function ErrorMsg({ msg }) {
  if (!msg) return null;
  return <p className="text-red-500 text-xs mt-1.5">⚠ {msg}</p>;
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

const OfferBidModal = ({ request, onClose, onSuccess }) => {
  const [rows,           setRows]           = useState([]);
  const [deliveryDate,   setDeliveryDate]   = useState('');
  const [moistureContent,setMoistureContent]= useState('');
  const [notes,          setNotes]          = useState('');
  const [proofImages,    setProofImages]    = useState([]); // { url, name, uploading }
  const [errors,         setErrors]         = useState({});
  const [submitting,     setSubmitting]     = useState(false);
  const [success,        setSuccess]        = useState(false);

  // Re-initialise whenever a new request is opened
  useEffect(() => {
    if (request) {
      setRows(buildInitialRows(request));
      setDeliveryDate('');
      setMoistureContent('');
      setNotes('');
      setProofImages([]);
      setErrors({});
      setSubmitting(false);
      setSuccess(false);
    }
  }, [request]);

  const grandTotal = rows.reduce((sum, r) => sum + (r.total || 0), 0);

  const updateRow = useCallback((idx, field, value) => {
    setRows(prev => {
      const next = [...prev];
      next[idx] = { ...next[idx], [field]: value };
      if (field === 'quantity' || field === 'unit_price') {
        const qty   = parseFloat(field === 'quantity'   ? value : next[idx].quantity)   || 0;
        const price = parseFloat(field === 'unit_price' ? value : next[idx].unit_price) || 0;
        next[idx].total = qty * price;
      }
      return next;
    });
  }, []);

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const placeholder = { url: '', name: file.name, uploading: true };
    setProofImages(prev => [...prev, placeholder]);
    try {
      const { data } = await api.post('/upload/sign-public', {
        folder:      'rfq_images',
        filename:    file.name,
        contentType: file.type,
      });
      await fetch(data.uploadUrl, { method: 'PUT', body: file, headers: { 'Content-Type': file.type } });
      setProofImages(prev =>
        prev.map(p =>
          p.name === file.name && p.uploading
            ? { url: data.publicUrl, name: file.name, uploading: false }
            : p
        )
      );
    } catch {
      setProofImages(prev => prev.filter(p => !(p.name === file.name && p.uploading)));
      setErrors(prev => ({ ...prev, images: 'Image upload failed. Please try again.' }));
    }
  };

  const removeImage = (name) => setProofImages(prev => prev.filter(p => p.name !== name));

  const validate = () => {
    const errs = {};
    if (!deliveryDate) errs.deliveryDate = 'Please select a delivery date.';
    if (rows.some(r => !r.unit_price || parseFloat(r.unit_price) <= 0))
      errs.rows = 'Please enter a unit price for every item.';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setSubmitting(true);
    setErrors({});
    try {
      await api.post(`/requests/${request.id}/offers`, {
        price:     grandTotal,
        items:     rows.map(r => ({
          name:                     r.name,
          quantity:                 parseFloat(r.quantity)   || 0,
          unit:                     r.unit,
          target_price:             parseFloat(r.unit_price) || 0,
          moisture_content_percent: moistureContent ? parseFloat(moistureContent) : null,
        })),
        images:                   proofImages.filter(p => !p.uploading).map(p => p.url),
        moisture_content_percent: moistureContent ? parseFloat(moistureContent) : null,
        delivery_date:            new Date(deliveryDate).toISOString(),
        notes,
        quantity_offered:         rows[0]?.quantity || null,
      });
      setSuccess(true);
      if (onSuccess) onSuccess();
    } catch (err) {
      setErrors(prev => ({
        ...prev,
        submit: err.response?.data?.detail || 'Failed to submit bid. Please try again.',
      }));
    } finally {
      setSubmitting(false);
    }
  };

  if (!request) return null;

  // ── Success state ────────────────────────────────────────────────────────
  if (success) {
    return (
      <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
        <div className="bg-white rounded-2xl p-8 max-w-sm w-full text-center shadow-2xl">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Bid Submitted!</h3>
          <p className="text-gray-500 mb-1 text-sm">
            Your bid of{' '}
            <span className="font-semibold text-emerald-600">₦{grandTotal.toLocaleString()}</span>{' '}
            has been sent to the buyer.
          </p>
          <p className="text-gray-400 text-xs mb-6">You'll be notified when they respond.</p>
          <button
            onClick={onClose}
            className="w-full py-3 bg-emerald-600 text-white rounded-xl font-semibold hover:bg-emerald-700 transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    );
  }

  // ── Main modal ──────────────────────────────────────────────────────────
  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[92vh] flex flex-col shadow-2xl">

        {/* Header */}
        <div className="flex items-start justify-between px-6 py-5 border-b border-gray-100">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Place Bid</h2>
            <p className="text-sm text-gray-500 mt-0.5">
              {request.items?.[0]?.name}
              {request.items?.length > 1 && (
                <span className="text-gray-400"> +{request.items.length - 1} more items</span>
              )}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Scrollable body */}
        <div className="overflow-y-auto flex-1 px-6 py-5 space-y-6">

          {/* ── Quotation table ── */}
          <section>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Quotation
            </h3>
            <div className="overflow-x-auto rounded-xl border border-gray-200">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="text-left px-3 py-2.5 font-medium">Item</th>
                    <th className="text-right px-3 py-2.5 font-medium w-24">Qty</th>
                    <th className="px-3 py-2.5 font-medium w-32">Unit</th>
                    <th className="text-right px-3 py-2.5 font-medium w-32">Price (₦)</th>
                    <th className="text-right px-3 py-2.5 font-medium w-28">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {rows.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50/50">
                      <td className="px-3 py-2.5 font-medium text-gray-800">{row.name}</td>
                      <td className="px-3 py-2.5">
                        <input
                          type="number" min="0"
                          value={row.quantity}
                          onChange={e => updateRow(idx, 'quantity', e.target.value)}
                          className="w-full text-right px-2 py-1.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none"
                        />
                      </td>
                      <td className="px-3 py-2.5">
                        <select
                          value={row.unit}
                          onChange={e => updateRow(idx, 'unit', e.target.value)}
                          className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                        >
                          {UNIT_OPTIONS.map(u => <option key={u}>{u}</option>)}
                        </select>
                      </td>
                      <td className="px-3 py-2.5">
                        <input
                          type="number" min="0"
                          value={row.unit_price}
                          onChange={e => updateRow(idx, 'unit_price', e.target.value)}
                          className={`w-full text-right px-2 py-1.5 border rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none ${
                            errors.rows ? 'border-red-300 bg-red-50' : 'border-gray-200'
                          }`}
                          placeholder="0"
                        />
                      </td>
                      <td className="px-3 py-2.5 text-right font-bold text-emerald-700">
                        ₦{(row.total || 0).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="bg-emerald-50 border-t border-emerald-100">
                    <td colSpan={4} className="px-3 py-3 text-right font-bold text-gray-800">
                      Grand Total
                    </td>
                    <td className="px-3 py-3 text-right font-bold text-emerald-700 text-base">
                      ₦{grandTotal.toLocaleString()}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
            <ErrorMsg msg={errors.rows} />
          </section>

          {/* ── Delivery date & Moisture content ── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Earliest Delivery Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={deliveryDate}
                onChange={e => setDeliveryDate(e.target.value)}
                className={`w-full px-3 py-2.5 border rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none ${
                  errors.deliveryDate ? 'border-red-300 bg-red-50' : 'border-gray-200'
                }`}
              />
              <ErrorMsg msg={errors.deliveryDate} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Moisture Content %
                <span className="text-gray-400 font-normal ml-1">(optional)</span>
              </label>
              <input
                type="number" min="0" max="100"
                value={moistureContent}
                onChange={e => setMoistureContent(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                placeholder="e.g. 12.5"
              />
            </div>
          </div>

          {/* ── Notes ── */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Notes / Additional Info
            </label>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              rows={3}
              className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none resize-none"
              placeholder="Quality details, packaging, payment preference..."
            />
          </div>

          {/* ── Image upload ── */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Proof Images
              <span className="text-gray-400 font-normal ml-1">(optional)</span>
            </label>
            <label className="flex items-center gap-3 px-4 py-3 border-2 border-dashed border-gray-200 rounded-xl cursor-pointer hover:border-emerald-400 hover:bg-emerald-50 transition-colors">
              <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <span className="text-sm text-gray-500">Click to upload a product photo</span>
              <input type="file" accept="image/*" onChange={handleImageUpload} className="sr-only" />
            </label>
            <ErrorMsg msg={errors.images} />
            {proofImages.length > 0 && (
              <div className="flex gap-2 flex-wrap mt-3">
                {proofImages.map((img, i) => (
                  <div key={i} className="relative group">
                    {img.uploading ? (
                      <div className="w-16 h-16 bg-gray-100 rounded-xl flex items-center justify-center">
                        <Spinner muted />
                      </div>
                    ) : (
                      <>
                        <img src={img.url} alt="proof" className="w-16 h-16 object-cover rounded-xl border border-gray-200" />
                        {/* opacity toggle avoids the hidden/flex conflict that breaks group-hover */}
                        <button
                          onClick={() => removeImage(img.name)}
                          className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          ×
                        </button>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* ── Submit error ── */}
          {errors.submit && (
            <div className="p-3.5 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex items-start gap-2">
              <span>⚠</span>
              <span>{errors.submit}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-100 flex gap-3 bg-gray-50/80 rounded-b-2xl">
          <button
            onClick={onClose}
            className="flex-1 py-3 border border-gray-200 bg-white text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting || proofImages.some(p => p.uploading)}
            className="flex-1 py-3 bg-emerald-600 text-white rounded-xl font-semibold hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {submitting ? (
              <><Spinner /> Submitting...</>
            ) : (
              `Submit Bid — ₦${grandTotal.toLocaleString()}`
            )}
          </button>
        </div>

      </div>
    </div>
  );
};

export default OfferBidModal;
