import React, { useState } from 'react';

const LoginStep = ({ formData, updateFormData, onLogin, switchToRegister }) => {
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        await onLogin(formData.email_or_phone, formData.password);
        setLoading(false);
    };

    return (
        <div className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email or Phone</label>
                    <input
                        type="text"
                        placeholder="Enter email or phone"
                        value={formData.email_or_phone}
                        onChange={(e) => updateFormData({ email_or_phone: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                    <input
                        type="password"
                        placeholder="Enter password"
                        value={formData.password}
                        onChange={(e) => updateFormData({ password: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        required
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg hover:bg-emerald-700 transition-colors font-medium disabled:bg-emerald-400"
                >
                    {loading ? 'Signing In...' : 'Sign In'}
                </button>
            </form>

            <p className="text-center text-sm text-gray-600 mt-4">
                Don't have an account?
                <button
                    onClick={switchToRegister}
                    className="text-emerald-600 hover:text-emerald-700 font-medium ml-1"
                >
                    Sign Up
                </button>
            </p>
        </div>
    );
};

export default LoginStep;
