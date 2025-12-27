import React, { useState } from 'react';

const LoginStep = ({ formData, updateFormData, onLogin, switchToRegister, onCancel }) => {
    const [loading, setLoading] = useState(false);
    const [view, setView] = useState('login'); // login, forgot, reset
    const [resetEmail, setResetEmail] = useState('');
    const [otp, setOtp] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await onLogin(formData.email_or_phone, formData.password);
        } catch (error) {
            // Error handling is likely in parent, but safety verify
        } finally {
            setLoading(false);
        }
    };

    const handleForgotPassword = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');
        try {
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/forgot-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: resetEmail })
            });
            const data = await res.json();
            if (res.ok) {
                setMessage(data.message);
                setView('reset');
            } else {
                setMessage(data.detail || "Failed to send reset code");
            }
        } catch (err) {
            setMessage("Network error occurred");
        } finally {
            setLoading(false);
        }
    };

    const handleResetPassword = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');
        try {
            const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: resetEmail, otp, new_password: newPassword })
            });
            const data = await res.json();
            if (res.ok) {
                setMessage("Password reset successfully! Please login.");
                setView('login');
                // clear sensitive fields
                setOtp('');
                setNewPassword('');
            } else {
                setMessage(data.detail || "Failed to reset password");
            }
        } catch (err) {
            setMessage("Network error occurred");
        } finally {
            setLoading(false);
        }
    };

    if (view === 'forgot') {
        return (
            <div className="space-y-4">
                <div className="text-center mb-4">
                    <h3 className="text-lg font-bold">Reset Password</h3>
                    <p className="text-sm text-gray-500">Enter your email to receive a reset code.</p>
                </div>
                {message && <div className={`text-center text-sm p-2 rounded ${message.includes('code') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{message}</div>}
                <form onSubmit={handleForgotPassword} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                        <input
                            type="email"
                            required
                            placeholder="Enter your email"
                            value={resetEmail}
                            onChange={(e) => setResetEmail(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        />
                    </div>
                    <div className="flex space-x-3">
                        <button type="button" onClick={() => setView('login')} className="flex-1 px-4 py-3 border rounded-lg hover:bg-gray-50">Back</button>
                        <button type="submit" disabled={loading} className="flex-1 bg-emerald-600 text-white py-3 rounded-lg hover:bg-emerald-700 disabled:opacity-50">
                            {loading ? 'Sending...' : 'Send Code'}
                        </button>
                    </div>
                </form>
            </div>
        );
    }

    if (view === 'reset') {
        return (
            <div className="space-y-4">
                <div className="text-center mb-4">
                    <h3 className="text-lg font-bold">Create New Password</h3>
                    <p className="text-sm text-gray-500">Enter the code sent to {resetEmail}</p>
                </div>
                {message && <div className="text-center text-sm p-2 rounded bg-blue-100 text-blue-700">{message}</div>}
                <form onSubmit={handleResetPassword} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Reset Code (OTP)</label>
                        <input
                            type="text"
                            required
                            placeholder="Enter 6-digit code"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                        <input
                            type="password"
                            required
                            placeholder="Min 8 characters"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        />
                    </div>
                    <div className="flex space-x-3">
                        <button type="button" onClick={() => setView('forgot')} className="flex-1 px-4 py-3 border rounded-lg hover:bg-gray-50">Back</button>
                        <button type="submit" disabled={loading} className="flex-1 bg-emerald-600 text-white py-3 rounded-lg hover:bg-emerald-700 disabled:opacity-50">
                            {loading ? 'Reset Password' : 'Confirm Reset'}
                        </button>
                    </div>
                </form>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {message && <div className="text-center text-sm p-2 rounded bg-green-100 text-green-700 mb-2">{message}</div>}
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
                    <div className="flex justify-between items-center mb-1">
                        <label className="block text-sm font-medium text-gray-700">Password</label>
                        <button type="button" onClick={() => setView('forgot')} className="text-xs text-emerald-600 hover:underline">Forgot Password?</button>
                    </div>
                    <input
                        type="password"
                        placeholder="Enter password"
                        value={formData.password}
                        onChange={(e) => updateFormData({ password: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                        required
                    />
                </div>

                <div className="flex space-x-3">
                    <button
                        type="button"
                        onClick={onCancel}
                        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        disabled={loading}
                        className="flex-1 bg-emerald-600 text-white py-3 px-4 rounded-lg hover:bg-emerald-700 transition-colors font-medium disabled:bg-emerald-400"
                    >
                        {loading ? 'Signing In...' : 'Sign In'}
                    </button>
                </div>
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
