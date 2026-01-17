import React, { useState } from 'react';
import VerificationStep from './VerificationStep';

const BuyerFlow = ({ step, formData, updateFormData, setStep, onRegister }) => {
    const handleDetailsSubmit = (e) => {
        e.preventDefault();
        setStep('verification');
    };

    // Step 2: Verification
    if (step === 'verification') {
        return (
            <VerificationStep
                updateFormData={updateFormData}
                onRegister={onRegister}
                onBack={() => setStep('details')}
                role="buyer"
                requiredDocs={['headshot']} // Only require headshot for buyers
                docLabels={{
                    headshot: "Take a Profile Picture (Selfie)"
                }}
            />
        );
    }

    // Step 1: Personal Details
    return (
        <form onSubmit={handleDetailsSubmit} className="space-y-4">
            <h3 className="text-lg font-bold mb-4">Complete Your Profile</h3>

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
                    value={formData.address}
                    onChange={(e) => updateFormData({ address: e.target.value })}
                    placeholder="Enter your home address or delivery location"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                    rows="3"
                    required
                />
            </div>

            <button
                type="submit"
                className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg hover:bg-emerald-700 transition-colors font-medium mt-6"
            >
                Next: Add Profile Picture
            </button>
        </form>
    );
};

export default BuyerFlow;
