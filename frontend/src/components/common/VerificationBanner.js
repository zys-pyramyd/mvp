import React, { useState } from 'react';
import { ShieldCheck, AlertCircle, Clock, UploadCloud, X, CheckCircle } from 'lucide-react';

/**
 * VerificationBanner
 * Drop this inside any partner dashboard where the user may not yet be verified.
 *
 * Props:
 *   user          — the current user object (needs kyc_status, role, is_verified)
 *   onStatusChange — optional callback after successful document submission (to refresh user)
 */
const VerificationBanner = ({ user, onStatusChange, onGoHome }) => {
    const [expanded, setExpanded] = useState(false);
    const [uploading, setUploading] = useState({});
    const [uploadedDocs, setUploadedDocs] = useState({});  // { key: url }
    const [submitting, setSubmitting] = useState(false);
    const [submitSuccess, setSubmitSuccess] = useState(false);
    const [error, setError] = useState('');

    const kyc = user?.kyc_status;
    const isVerified = user?.is_verified;

    // Nothing to show if already verified
    if (isVerified && kyc === 'approved') return null;
    if (!user || user.role === 'buyer') return null;

    // ── Document sets by role ────────────────────────────────────────────────
    const docSets = {
        farmer:      { headshot: 'Passport Photo', nin: 'NIN / National ID', utility_bill: 'Utility Bill' },
        agent:       { headshot: 'Passport Photo', nin: 'NIN / National ID', utility_bill: 'Utility Bill' },
        business:    { headshot: 'Director Photo', cac: 'CAC Certificate', tin: 'TIN Certificate' },
        cooperative: { headshot: 'Representative Photo', cac: 'Cooperative Reg. Doc', nin: 'NIN / National ID' },
    };
    const requiredDocs = docSets[user.role] || {};

    // ── Status config ────────────────────────────────────────────────────────
    const statusConfig = {
        documents_pending: {
            icon:    <AlertCircle size={20} className="text-amber-600 shrink-0" />,
            bg:      'bg-amber-50 border-amber-300',
            title:   'Complete your verification to start selling',
            message: 'Upload your identity documents so our team can verify your account. Verification is required before you can list products on Pyramyd.',
            cta:     'Upload Documents',
            ctaCls:  'bg-amber-600 hover:bg-amber-700 text-white',
        },
        pending_review: {
            icon:    <Clock size={20} className="text-blue-600 shrink-0" />,
            bg:      'bg-blue-50 border-blue-300',
            title:   'Verification under review',
            message: 'Our team has received your documents and is reviewing them. You will receive a notification once approved — this usually takes 1–2 business days.',
            cta:     null,
        },
        rejected: {
            icon:    <AlertCircle size={20} className="text-red-600 shrink-0" />,
            bg:      'bg-red-50 border-red-300',
            title:   'Verification rejected — please resubmit',
            message: 'Your verification was declined. Please upload clearer copies of your documents and resubmit.',
            cta:     'Resubmit Documents',
            ctaCls:  'bg-red-600 hover:bg-red-700 text-white',
        },
    };

    const cfg = statusConfig[kyc] || statusConfig['documents_pending'];

    // ── Upload a single doc to R2 ────────────────────────────────────────────
    const uploadDoc = async (file, key) => {
        setUploading(prev => ({ ...prev, [key]: true }));
        setError('');
        try {
            const sign = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upload/sign-public`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ folder: 'kyc-docs', filename: file.name, contentType: file.type }),
            });
            if (!sign.ok) throw new Error('Could not get upload URL');
            const { uploadUrl, publicUrl, key: objKey } = await sign.json();

            const put = await fetch(uploadUrl, { method: 'PUT', body: file, headers: { 'Content-Type': file.type } });
            if (!put.ok) throw new Error('Upload failed');

            setUploadedDocs(prev => ({ ...prev, [key]: publicUrl || objKey }));
        } catch (e) {
            setError(`Upload failed for ${requiredDocs[key]}: ${e.message}`);
        } finally {
            setUploading(prev => ({ ...prev, [key]: false }));
        }
    };

    // ── Submit docs to backend ───────────────────────────────────────────────
    const submitDocs = async () => {
        if (Object.keys(uploadedDocs).length === 0) {
            setError('Please upload at least one document before submitting.');
            return;
        }
        setSubmitting(true);
        setError('');
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/kyc/submit-documents`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                body: JSON.stringify(uploadedDocs),
            });
            if (!res.ok) {
                const d = await res.json();
                throw new Error(d.detail || 'Submission failed');
            }
            setSubmitSuccess(true);
            setExpanded(false);
            if (onStatusChange) onStatusChange('pending_review');
        } catch (e) {
            setError(e.message);
        } finally {
            setSubmitting(false);
        }
    };

    if (submitSuccess) {
        return (
            <div className="border border-emerald-300 rounded-xl mb-6 bg-emerald-50 overflow-hidden">
                <div className="flex flex-col items-center text-center px-6 py-8 space-y-4">
                    <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center">
                        <CheckCircle size={32} className="text-emerald-600" />
                    </div>
                    <div>
                        <p className="font-bold text-emerald-900 text-base">Documents submitted!</p>
                        <p className="text-sm text-emerald-700 mt-1 leading-relaxed">
                            Your verification is now <strong>pending review</strong>. Our team will
                            check your documents within 1–2 business days and notify you once approved.
                        </p>
                    </div>
                    <div className="w-full bg-white border border-emerald-200 rounded-lg px-4 py-3 text-xs text-left text-gray-600 space-y-1">
                        <p className="font-semibold text-gray-800">What happens next?</p>
                        <p>1. Admin reviews your uploaded documents.</p>
                        <p>2. You receive a notification once approved.</p>
                        <p>3. Your account is verified — you can now list products.</p>
                    </div>
                    {onGoHome && (
                        <button
                            onClick={onGoHome}
                            className="mt-2 px-8 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 transition-colors"
                        >
                            Return to Home
                        </button>
                    )}
                </div>
            </div>
        );
    }

    const totalRequired = Object.keys(requiredDocs).length;
    const totalUploaded = Object.keys(uploadedDocs).length;
    const allDocsUploaded = totalUploaded >= totalRequired;

    return (
        <div className={`border rounded-xl mb-6 overflow-hidden ${cfg.bg}`}>
            {/* Banner header */}
            <div className="flex items-start gap-3 px-5 py-4">
                {cfg.icon}
                <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-gray-900">{cfg.title}</p>
                    <p className="text-xs text-gray-600 mt-0.5 leading-relaxed">{cfg.message}</p>
                </div>
                {cfg.cta && (
                    <button
                        onClick={() => setExpanded(e => !e)}
                        className={`shrink-0 text-xs font-semibold px-4 py-2 rounded-lg transition-colors ${cfg.ctaCls}`}
                    >
                        {expanded ? 'Close' : cfg.cta}
                    </button>
                )}
            </div>

            {/* Expandable upload form */}
            {expanded && (
                <div className="border-t border-amber-200 bg-white px-5 py-5 space-y-4">
                    <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Upload your documents (JPG, PNG, PDF — max 5MB each)</p>

                    {error && (
                        <div className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 text-xs px-3 py-2 rounded-lg">
                            <span className="shrink-0">⚠️</span>
                            <span>{error}</span>
                            <button onClick={() => setError('')} className="ml-auto text-red-400 hover:text-red-600">
                                <X size={14} />
                            </button>
                        </div>
                    )}

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {Object.entries(requiredDocs).map(([key, label]) => {
                            const uploaded = uploadedDocs[key];
                            const isUp = uploading[key];
                            return (
                                <label
                                    key={key}
                                    className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-4 cursor-pointer transition-colors
                                        ${uploaded ? 'border-emerald-400 bg-emerald-50' : 'border-gray-300 hover:border-amber-400 bg-gray-50'}`}
                                >
                                    <input
                                        type="file"
                                        accept=".jpg,.jpeg,.png,.pdf"
                                        className="hidden"
                                        disabled={isUp}
                                        onChange={e => { if (e.target.files[0]) uploadDoc(e.target.files[0], key); }}
                                    />
                                    {uploaded ? (
                                        <>
                                            <CheckCircle size={22} className="text-emerald-500 mb-1" />
                                            <span className="text-xs font-medium text-emerald-700">{label}</span>
                                            <span className="text-[10px] text-emerald-600">Uploaded ✓</span>
                                        </>
                                    ) : isUp ? (
                                        <>
                                            <UploadCloud size={22} className="text-amber-500 animate-bounce mb-1" />
                                            <span className="text-xs text-gray-500">Uploading…</span>
                                        </>
                                    ) : (
                                        <>
                                            <UploadCloud size={22} className="text-gray-400 mb-1" />
                                            <span className="text-xs font-medium text-gray-700">{label}</span>
                                            <span className="text-[10px] text-gray-400">Click to upload</span>
                                        </>
                                    )}
                                </label>
                            );
                        })}
                    </div>

                    {/* Progress indicator */}
                    <div>
                        <div className="flex justify-between text-xs mb-1">
                            <span className="text-gray-500">Documents uploaded</span>
                            <span className={`font-semibold ${allDocsUploaded ? 'text-emerald-600' : 'text-amber-600'}`}>
                                {totalUploaded} / {totalRequired}
                            </span>
                        </div>
                        <div className="w-full h-1.5 bg-gray-200 rounded-full">
                            <div
                                className={`h-1.5 rounded-full transition-all duration-300 ${allDocsUploaded ? 'bg-emerald-500' : 'bg-amber-400'}`}
                                style={{ width: `${(totalUploaded / totalRequired) * 100}%` }}
                            />
                        </div>
                    </div>

                    {/* Remaining docs note + submit */}
                    {!allDocsUploaded && (
                        <p className="text-xs text-amber-700 text-center">
                            Please upload all {totalRequired} required documents before submitting.
                        </p>
                    )}

                    <button
                        onClick={submitDocs}
                        disabled={submitting || !allDocsUploaded}
                        className="w-full bg-emerald-600 text-white py-3 rounded-xl font-semibold text-sm hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                        <ShieldCheck size={18} />
                        {submitting ? 'Submitting…' : 'Submit for Verification'}
                    </button>
                    <p className="text-center text-[10px] text-gray-400">
                        Your documents are encrypted and only accessed by Pyramyd's compliance team.
                    </p>
                </div>
            )}
        </div>
    );
};

export default VerificationBanner;
