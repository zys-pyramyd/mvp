import React, { useState, useCallback, lazy, Suspense } from 'react';
import debounce from 'lodash.debounce';
import { X, ArrowLeft } from 'lucide-react';
import LoginStep from './LoginStep';
import BasicDetailsStep from './BasicDetailsStep';
import PathSelectionStep from './PathSelectionStep';
import PartnerTypeSelectionStep from './PartnerTypeSelectionStep';
// Flow components are lazy-loaded below


const RegistrationModal = ({ onClose, onLogin, onRegister }) => {
  const [globalLoading, setGlobalLoading] = useState(false);
  // Debounced form data updater to reduce re-renders
  const debouncedUpdate = useCallback(
    debounce((updates) => {
      setFormData(prev => ({ ...prev, ...updates }));
    }, 200),
    []
  );
  const updateFormData = (updates) => {
    debouncedUpdate(updates);
  };

  // Wrapper for registration submission to manage global loading state
  const [submitError, setSubmitError] = React.useState('');
  const [registrationSuccess, setRegistrationSuccess] = React.useState(false);
  const [registeredPath, setRegisteredPath] = React.useState(''); // 'buyer' | 'partner'

  const handleRegister = async (data) => {
    setGlobalLoading(true);
    setSubmitError('');
    try {
      await onRegister(data);
      // Success — show the completion screen instead of abruptly closing
      setRegisteredPath(data.user_path || 'partner');
      setRegistrationSuccess(true);
    } catch (err) {
      setSubmitError(
        err?.response?.data?.detail ||
        err?.message ||
        'Registration failed. Please try again.'
      );
    } finally {
      setGlobalLoading(false);
    }
  };
    const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'
    const [step, setStep] = useState('basic'); // basic, path_selection, partner_type, details, verification
    const [formData, setFormData] = useState({
        first_name: '',
        middle_name: '',
        last_name: '',
        username: '',
        email_or_phone: '',
        phone: '',
        password: '',
        confirm_password: '',
        gender: '',
        date_of_birth: '',

        user_path: '', // 'buyer' or 'partner'
        buyer_type: '',
        partner_type: '', // 'agent', 'farmer', 'business'

        // Role specific
        business_category: '', // processor, wholesaler, etc.
        business_info: {}, // name, address, etc.
        registration_status: '', // 'registered', 'unregistered'

        farm_details: [], // list of farms

        // Verification
        bio: '',
        id_type: '',
        id_number: '',
        documents: {}, // { headshot: 'url', id_document: 'url', ... }
        verification_info: {}
    });

    const handleBack = () => {
        if (authMode === 'login') return;

        // Logic for back navigation based on current step and choices
        switch (step) {
            case 'basic':
                setAuthMode('login');
                break;
            case 'path_selection':
                setStep('basic');
                break;
            case 'partner_type':
                setStep('path_selection');
                break;
            case 'details':
                if (formData.user_path === 'partner') {
                    setStep('partner_type');
                } else {
                    setStep('path_selection');
                }
                break;
            case 'verification':
                setStep('details');
                break;
            default:
                setStep('basic');
        }
    };

    // Removed original updateFormData; using debounced version above

    const renderCurrentStep = () => {
        if (authMode === 'login') {
            return (
                <LoginStep
                    formData={formData}
                    updateFormData={updateFormData}
                    onLogin={onLogin}
                    switchToRegister={() => setAuthMode('register')}
                    onCancel={onClose}
                />
            );
        }

        switch (step) {
            case 'basic':
                return (
                    <BasicDetailsStep
                        formData={formData}
                        updateFormData={updateFormData}
                        onNext={() => setStep('path_selection')}
                        onCancel={onClose}
                    />
                );
            case 'path_selection':
                return (
                    <PathSelectionStep
                        formData={formData}
                        updateFormData={updateFormData}
                        onNext={(path) => {
                            if (path === 'partner') {
                                setStep('partner_type');
                            } else {
                                setStep('details');
                            }
                        }}
                    />
                );
            case 'partner_type':
                return (
                    <PartnerTypeSelectionStep
                        formData={formData}
                        updateFormData={updateFormData}
                        onNext={() => setStep('details')}
                    />
                );
            case 'details':
            case 'verification':
                // Lazy load heavy flows
                const LazyBuyerFlow = lazy(() => import('./BuyerFlow'));
                const LazyAgentFlow = lazy(() => import('./AgentFlow'));
                const LazyFarmerFlow = lazy(() => import('./FarmerFlow'));
                const LazyBusinessFlow = lazy(() => import('./BusinessFlow'));
                const LazyVerificationStep = lazy(() => import('./VerificationStep'));
                if (formData.user_path === 'buyer') {
                    return (
                        <Suspense fallback={<div className="text-center py-4">Loading...</div>}>
                            <LazyBuyerFlow step={step} formData={formData} updateFormData={updateFormData} setStep={setStep} onRegister={handleRegister} />
                        </Suspense>
                    );
                }
                if (formData.partner_type === 'agent') {
                    return (
                        <Suspense fallback={<div className="text-center py-4">Loading...</div>}>
                            <LazyAgentFlow step={step} formData={formData} updateFormData={updateFormData} setStep={setStep} onRegister={handleRegister} />
                        </Suspense>
                    );
                }
                if (formData.partner_type === 'farmer') {
                    return (
                        <Suspense fallback={<div className="text-center py-4">Loading...</div>}>
                            <LazyFarmerFlow step={step} formData={formData} updateFormData={updateFormData} setStep={setStep} onRegister={handleRegister} />
                        </Suspense>
                    );
                }
                if (formData.partner_type === 'business') {
                    return (
                        <Suspense fallback={<div className="text-center py-4">Loading...</div>}>
                            <LazyBusinessFlow step={step} formData={formData} updateFormData={updateFormData} setStep={setStep} onRegister={handleRegister} />
                        </Suspense>
                    );
                }
                // Fallback to verification step if none matched
                return (
                    <Suspense fallback={<div className="text-center py-4">Loading...</div>}>
                        <LazyVerificationStep step={step} formData={formData} updateFormData={updateFormData} onRegister={handleRegister} onBack={handleBack} role={formData.partner_type} requiredDocs={['headshot','id_document']} docLabels={{headshot:'Headshot',id_document:'ID Document'}} isSubmitting={globalLoading} />
                    </Suspense>
                );
            default:
                return <div>Unknown Step</div>;
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto relative">
                <div className="p-6">

                    {/* ── Registration Success Screen ─────────────────────── */}
                    {registrationSuccess ? (
                        <div className="flex flex-col items-center text-center py-8 px-4 space-y-5">
                            {/* Icon */}
                            <div className="w-20 h-20 rounded-full bg-emerald-100 flex items-center justify-center">
                                <svg className="w-10 h-10 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                </svg>
                            </div>

                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">Registration Complete!</h2>
                                <p className="text-gray-500 mt-2 text-sm leading-relaxed">
                                    {registeredPath === 'buyer'
                                        ? 'Your account is active. You can now shop, place orders, and track deliveries.'
                                        : 'Your account has been created. Verification is required before you can list products — you can submit your documents anytime from your dashboard.'}
                                </p>
                            </div>

                            {registeredPath !== 'buyer' && (
                                <div className="w-full bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm text-amber-800 text-left">
                                    <p className="font-semibold mb-1">🔔 Verification pending</p>
                                    <p className="text-xs text-amber-700 leading-relaxed">
                                        Go to your <strong>Dashboard → Verification</strong> to upload your identity documents.
                                        Once our team approves them, you'll be able to start selling on Pyramyd.
                                    </p>
                                </div>
                            )}

                            <button
                                onClick={onClose}
                                className="w-full max-w-xs bg-emerald-600 text-white py-3 rounded-xl font-semibold hover:bg-emerald-700 transition-colors"
                            >
                                Return to Home
                            </button>
                        </div>
                    ) : (
                        <>
                            <div className="flex justify-between items-center mb-6">
                                <div className="flex items-center">
                                    {authMode === 'register' && (
                                        <button onClick={handleBack} className="mr-3 text-gray-500 hover:text-gray-700">
                                            <ArrowLeft size={24} />
                                        </button>
                                    )}
                                    <h2 className="text-xl font-bold">
                                        {authMode === 'login' ? 'Sign In' : 'Create Account'}
                                    </h2>
                                </div>
                                <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                                    <X size={24} />
                                </button>
                            </div>

                            {renderCurrentStep()}

                            {/* Submit error banner */}
                            {submitError && (
                                <div className="mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800 flex items-start gap-2">
                                    <span className="flex-shrink-0">⚠️</span>
                                    <span>{submitError}</span>
                                    <button onClick={() => setSubmitError('')} className="ml-auto text-red-400 hover:text-red-700 text-lg leading-none flex-shrink-0">&times;</button>
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Global loading overlay */}
                {globalLoading && (
                    <div className="absolute inset-0 bg-white bg-opacity-80 flex flex-col items-center justify-center gap-3 rounded-lg">
                        <div className="w-10 h-10 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin" />
                        <div className="text-emerald-700 font-semibold text-sm">Submitting your registration...</div>
                        <p className="text-gray-400 text-xs">Please wait, do not close this window.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RegistrationModal;
