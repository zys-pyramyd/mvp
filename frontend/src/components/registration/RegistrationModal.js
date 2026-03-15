import React, { useState } from 'react';
import { X, ArrowLeft } from 'lucide-react';
import LoginStep from './LoginStep';
import BasicDetailsStep from './BasicDetailsStep';
import PathSelectionStep from './PathSelectionStep';
import PartnerTypeSelectionStep from './PartnerTypeSelectionStep';
import BuyerFlow from './BuyerFlow';
import AgentFlow from './AgentFlow';
import FarmerFlow from './FarmerFlow';
import BusinessFlow from './BusinessFlow';

const RegistrationModal = ({ onClose, onLogin, onRegister }) => {
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

    const updateFormData = (updates) => {
        setFormData(prev => ({ ...prev, ...updates }));
    };

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
                                // Buyer flow now goes to details for extra info
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
                if (formData.user_path === 'buyer') {
                    return <BuyerFlow step={step} formData={formData} updateFormData={updateFormData} setStep={setStep} onRegister={onRegister} />;
                }
                if (formData.partner_type === 'agent') {
                    return <AgentFlow step={step} formData={formData} updateFormData={updateFormData} setStep={setStep} onRegister={onRegister} />;
                }
                if (formData.partner_type === 'farmer') {
                    return <FarmerFlow step={step} formData={formData} updateFormData={updateFormData} setStep={setStep} onRegister={onRegister} />;
                }
                if (formData.partner_type === 'business') {
                    return <BusinessFlow step={step} formData={formData} updateFormData={updateFormData} setStep={setStep} onRegister={onRegister} />;
                }
                return <div>Unknown Role Flow</div>;
            default:
                return <div>Unknown Step</div>;
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto"> {/* Max width 2xl, scrollable */}
                <div className="p-6">
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
                </div>
            </div>
        </div>
    );
};

export default RegistrationModal;
