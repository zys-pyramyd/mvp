import React, { useState } from 'react';
import api from '../../services/api';

const DVAPromptModal = ({ isOpen, onClose, user, onUpdateUser }) => {
    const [bvn, setBvn] = useState('');
    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState({ type: '', text: '' });

    if (!isOpen) return null;

    const handleCreateDVA = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMsg({ type: '', text: '' });

        try {
            // Send BVN if provided, otherwise backend uses stored one
            const payload = bvn ? { bvn } : {};
            const response = await api.post('/auth/create-dva', payload);
            const { account_number, bank_name } = response.data;

            const updatedUser = {
                ...user,
                dva_account_number: account_number,
                dva_bank_name: bank_name,
                // Update BVN in verification info if needed (optional)
            };

            onUpdateUser(updatedUser);
            setMsg({ type: 'success', text: `Success! Account: ${account_number} (${bank_name})` });

            // Close after short delay
            setTimeout(() => {
                onClose();
            }, 2000);

        } catch (error) {
            console.error(error);
            setMsg({
                type: 'error',
                text: error.response?.data?.detail || 'Creation failed. Please verify your BVN matches your URL profile name.'
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-70 z-[60] flex items-center justify-center p-4">
            <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-2xl relative">
                {/* No close button - Forces action? Or allow close? User said "Prompt... everytime they log in". 
                    This implies blocking or nagging. I will add a close button but maybe make it less prominent, 
                    or maybe this modal IS the prompt. */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                >
                    Skip
                </button>

// ... (imports)

                <div className="text-center mb-6">
                    <div className="bg-amber-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900">Action Required</h2>
                    <p className="text-gray-600 mt-2">
                        Your Virtual Account could not be created automatically.
                        This is required to receive payments.
                    </p>
                </div>

                {msg.text && (
                    <div className={`p-3 rounded mb-4 text-sm ${msg.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {msg.text}
                    </div>
                )}

                <form onSubmit={handleCreateDVA} className="space-y-4">
                    <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 text-sm">
                        <p className="mb-2"><span className="font-semibold">Current Name:</span> {user?.first_name} {user?.last_name}</p>
                        <p className="text-xs text-gray-500">Your BVN name must match this exactly.</p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Confirm / Update BVN
                        </label>
                        <input
                            type="text"
                            value={bvn}
                            onChange={(e) => setBvn(e.target.value)}
                            placeholder="Enter corrected BVN (optional)"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                            maxLength={11}
                        />
                        <p className="text-xs text-gray-500 mt-1">Leave empty to retry with stored BVN.</p>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 font-bold shadow-lg disabled:opacity-50"
                    >
                        {loading ? 'Processing...' : 'Create Virtual Account'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default DVAPromptModal;
