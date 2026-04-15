import React, { useState } from 'react';
import AddressFields from '../common/AddressFields';

const BasicDetailsStep = ({ formData, updateFormData, onNext, onCancel }) => {
    const [error, setError] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirm_password) {
            setError('Passwords do not match');
            return;
        }
        const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
        if (!passwordRegex.test(formData.password)) {
            setError('Password must be at least 8 characters and include a letter, a number, and a symbol (@$!%*#?&)');
            return;
        }

        onNext();
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            {/* Important Notice */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-blue-800">
                    <span className="font-semibold">Important:</span> Please use your full name exactly as it appears on your NIN or BVN for verification purposes.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                    <input
                        type="text"
                        value={formData.first_name}
                        onChange={(e) => updateFormData({ first_name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                    <input
                        type="text"
                        value={formData.last_name}
                        onChange={(e) => updateFormData({ last_name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Middle Name (Optional)</label>
                    <input
                        type="text"
                        value={formData.middle_name || ''}
                        onChange={(e) => updateFormData({ middle_name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    />
                </div>
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => updateFormData({ username: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email or Phone</label>
                <input
                    type="text"
                    value={formData.email_or_phone}
                    onChange={(e) => updateFormData({ email_or_phone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    required
                />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                    <input
                        type="password"
                        value={formData.password}
                        onChange={(e) => updateFormData({ password: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
                    <input
                        type="password"
                        value={formData.confirm_password}
                        onChange={(e) => updateFormData({ confirm_password: e.target.value })}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 ${formData.confirm_password && formData.password !== formData.confirm_password ? 'border-red-500' : 'border-gray-300'
                            }`}
                        required
                    />
                </div>
            </div>

            <div className="pt-4 border-t border-gray-200">
                <AddressFields
                    label="Address Details"
                    values={{
                        street: formData.address_street || '',
                        city: formData.city || '',
                        state: formData.state || '',
                        country: formData.country || 'Nigeria',
                    }}
                    onChange={patch => {
                        const map = {};
                        if ('street'  in patch) map.address_street = patch.street;
                        if ('city'    in patch) map.city    = patch.city;
                        if ('state'   in patch) map.state   = patch.state;
                        if ('country' in patch) map.country = patch.country;
                        updateFormData(map);
                    }}
                    accentColor="emerald"
                />
                {/* Landmark stays as an optional extra */}
                <div className="mt-3">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nearest Landmark <span className="text-gray-400 font-normal">(Optional)</span></label>
                    <input
                        type="text"
                        value={formData.landmark || ''}
                        onChange={(e) => updateFormData({ landmark: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="e.g. Opposite Shoprite"
                    />
                </div>
            </div>


            {error && <p className="text-red-500 text-sm">{error}</p>}

            <div className="flex space-x-3 mt-6">
                <button
                    type="button"
                    onClick={onCancel}
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    className="flex-1 bg-emerald-600 text-white py-3 px-4 rounded-lg hover:bg-emerald-700 transition-colors font-medium"
                >
                    Continue
                </button>
            </div>
        </form>
    );
};

export default BasicDetailsStep;
