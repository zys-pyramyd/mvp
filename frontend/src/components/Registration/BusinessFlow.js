import React, { useState } from 'react';
import VerificationStep from './VerificationStep';

const BusinessFlow = ({ step, formData, updateFormData, setStep, onRegister }) => {
    const [localStep, setLocalStep] = useState(step === 'verification' ? 3 : 1); // 1: Info, 2: Status/Docs Info, 3: Verification Upgrade

    const handleInfoSubmit = (e) => {
        e.preventDefault();
        setLocalStep(2);
    };

    const handleStatusSubmit = (e) => {
        e.preventDefault();
        setStep('verification');
        setLocalStep(3);
    };

    // Verification Step Logic
    if (step === 'verification' || localStep === 3) {
        const isRegistered = formData.registration_status === 'registered';

        const requiredDocs = isRegistered
            ? ['cac_document', 'proof_of_address']
            : ['headshot', 'id_document', 'proof_of_address'];

        const docLabels = isRegistered
            ? {
                cac_document: "CAC Certificate",
                proof_of_address: "Proof of Business Address (Utility Bill)"
            }
            : {
                headshot: "Take a Profile Picture (Selfie) of Owner",
                id_document: "Upload NIN Slip or ID Card",
                proof_of_address: "Proof of Business Address"
            };

        return (
            <VerificationStep
                formData={formData}
                updateFormData={updateFormData}
                onRegister={onRegister}
                role="business"
                requiredDocs={requiredDocs}
                docLabels={docLabels}
            />
        );
    }

    // Step 2: Registration Status
    if (localStep === 2) {
        return (
            <form onSubmit={handleStatusSubmit} className="space-y-6">
                <h3 className="text-lg font-bold">Registration Status</h3>

                <div className="space-y-4">
                    <div
                        onClick={() => updateFormData({ registration_status: 'registered' })}
                        className={`p-4 border rounded-lg cursor-pointer ${formData.registration_status === 'registered' ? 'border-purple-600 bg-purple-50' : 'border-gray-200'}`}
                    >
                        <div className="font-bold flex items-center">
                            <div className={`w-4 h-4 rounded-full border mr-3 flex items-center justify-center ${formData.registration_status === 'registered' ? 'border-purple-600 bg-purple-600' : 'border-gray-400'}`}>
                                {formData.registration_status === 'registered' && <div className="w-2 h-2 bg-white rounded-full" />}
                            </div>
                            Registered Business
                        </div>
                        <p className="text-sm text-gray-600 mt-1 ml-7">I have a CAC Certificate and TIN.</p>
                    </div>

                    <div
                        onClick={() => updateFormData({ registration_status: 'unregistered' })}
                        className={`p-4 border rounded-lg cursor-pointer ${formData.registration_status === 'unregistered' ? 'border-purple-600 bg-purple-50' : 'border-gray-200'}`}
                    >
                        <div className="font-bold flex items-center">
                            <div className={`w-4 h-4 rounded-full border mr-3 flex items-center justify-center ${formData.registration_status === 'unregistered' ? 'border-purple-600 bg-purple-600' : 'border-gray-400'}`}>
                                {formData.registration_status === 'unregistered' && <div className="w-2 h-2 bg-white rounded-full" />}
                            </div>
                            Unregistered Business
                        </div>
                        <p className="text-sm text-gray-600 mt-1 ml-7">I don't have corporate documents yet (Requires Owner Verification).</p>
                    </div>
                </div>

                {formData.registration_status === 'registered' && (
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Tax Identification Number (TIN)</label>
                        <input
                            type="text"
                            value={formData.business_info?.tin || ''}
                            onChange={(e) => updateFormData({ business_info: { ...formData.business_info, tin: e.target.value } })}
                            className="w-full px-3 py-2 border rounded-lg"
                            placeholder="Enter TIN"
                            required
                        />
                    </div>
                )}
                {formData.registration_status === 'unregistered' && (
                    <div className="bg-yellow-50 p-3 rounded text-sm text-yellow-800">
                        Note: You will need to verify your identity using your NIN and a selfie.
                    </div>
                )}

                <div className="flex justify-between pt-4">
                    <button type="button" onClick={() => setLocalStep(1)} className="text-gray-500 hover:text-gray-700">Back</button>
                    <button
                        type="submit"
                        disabled={!formData.registration_status}
                        className="bg-purple-600 text-white py-2 px-6 rounded-lg hover:bg-purple-700 disabled:bg-gray-400"
                    >
                        Next
                    </button>
                </div>
            </form>
        );
    }

    // Step 1: Business Info & Category
    return (
        <form onSubmit={handleInfoSubmit} className="space-y-4">
            <h3 className="text-lg font-bold mb-4">Business Information</h3>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Business Name *</label>
                <input
                    type="text"
                    value={formData.business_info?.name || ''}
                    onChange={(e) => updateFormData({ business_info: { ...formData.business_info, name: e.target.value } })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Business Category *</label>
                <select
                    value={formData.business_category}
                    onChange={(e) => updateFormData({ business_category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                >
                    <option value="">Select Category</option>
                    <option value="processor">Processor / Manufacturer</option>
                    <option value="wholesaler">Wholesaler / Supplier</option>
                    <option value="retailer">Retailer</option>
                    <option value="hospitality">Hotel / Cafe / Restaurant</option>
                    <option value="logistics">Logistics / Transport</option>
                    <option value="other">Other</option>
                </select>
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date Operation Started *</label>
                <input
                    type="date"
                    value={formData.business_info?.date_established || ''}
                    onChange={(e) => updateFormData({ business_info: { ...formData.business_info, date_established: e.target.value } })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Business Address *</label>
                <textarea
                    value={formData.business_info?.address || ''}
                    onChange={(e) => updateFormData({ business_info: { ...formData.business_info, address: e.target.value } })}
                    placeholder="Full business address"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    rows="3"
                    required
                />
            </div>

            <button
                type="submit"
                className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 transition-colors font-medium mt-6"
            >
                Continue
            </button>
        </form>
    );
};

export default BusinessFlow;
