import React, { useState } from 'react';
import VerificationStep from './VerificationStep'; // We will create this reusable component next

const AgentFlow = ({ step, formData, updateFormData, setStep, onRegister }) => {
    const [localStep, setLocalStep] = useState(step === 'verification' ? 2 : 1); // 1: Details, 2: Verification

    const handleDetailsSubmit = (e) => {
        e.preventDefault();
        setStep('verification'); // Update main stepper
        setLocalStep(2);
    };

    if (step === 'verification' || localStep === 2) {
        return (
            <VerificationStep
                formData={formData}
                updateFormData={updateFormData}
                onRegister={onRegister}
                role="agent"
                requiredDocs={['headshot', 'id_document', 'proof_of_address']}
                docLabels={{
                    headshot: "Take a Profile Picture (Selfie)",
                    id_document: "Upload NIN Slip or ID Card",
                    proof_of_address: "proof of Address (Utility Bill/Bank Statement)"
                }}
            />
        );
    }

    return (
        <form onSubmit={handleDetailsSubmit} className="space-y-4">
            <h3 className="text-lg font-bold mb-4">Agent Personal Details</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Gender *</label>
                    <select
                        value={formData.gender}
                        onChange={(e) => updateFormData({ gender: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        required
                    >
                        <option value="">Select Gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth *</label>
                    <input
                        type="date"
                        value={formData.date_of_birth}
                        onChange={(e) => updateFormData({ date_of_birth: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        required
                    />
                </div>
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Residential Address *</label>
                <textarea
                    value={formData.address} // Ensure text area maps to a field in formData (might need to add 'address' to initial state in Modal)
                    onChange={(e) => updateFormData({ address: e.target.value })}
                    placeholder="Enter your full residential address"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                    rows="3"
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bio / About You *</label>
                <textarea
                    value={formData.bio}
                    onChange={(e) => updateFormData({ bio: e.target.value })}
                    placeholder="Tell us briefly about your experience..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                    rows="3"
                    required
                />
            </div>

            <button
                type="submit"
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium mt-6"
            >
                Continue to Verification
            </button>
        </form>
    );
};

export default AgentFlow;
