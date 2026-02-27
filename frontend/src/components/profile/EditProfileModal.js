import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const EditProfileModal = ({ isOpen, onClose }) => {
    const { user, login } = useAuth(); // login used to update user context
    const [formData, setFormData] = useState({
        first_name: '',
        middle_name: '',
        last_name: ''
    });
    const [loading, setLoading] = useState(false);
    const [dvaLoading, setDvaLoading] = useState(false);
    const [msg, setMsg] = useState({ type: '', text: '' });
    const [bvn, setBvn] = useState(''); // State for BVN retry

    useEffect(() => {
        if (user) {
            setFormData({
                first_name: user.first_name || '',
                middle_name: user.middle_name || '',
                last_name: user.last_name || ''
            });
        }
    }, [user, isOpen]);

    if (!isOpen) return null;

    const handleUpdate = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMsg({ type: '', text: '' });

        try {
            await api.patch('/auth/profile', formData); // Check auth prefix
            // Refresh user context or manually update
            // Assuming api.patch returns success, we might need a way to refetch user
            // or update local state. For now, we rely on page refresh or simple alert.
            // Better: trigger a user reload if Context supports it, or manual update:
            const updatedUser = { ...user, ...formData };
            login(localStorage.getItem('token'), updatedUser); // Hacky update
            setMsg({ type: 'success', text: 'Profile updated successfully!' });
        } catch (error) {
            console.error(error);
            setMsg({ type: 'error', text: error.response?.data?.detail || 'Update failed' });
        } finally {
            setLoading(false);
        }
    };

    const handleCreateDVA = async () => {
        setDvaLoading(true);
        setMsg({ type: '', text: '' });
        try {
            // Send BVN if provided
            const payload = bvn ? { bvn } : {};
            const response = await api.post('/auth/create-dva', payload);
            const { account_number, bank_name } = response.data;

            const updatedUser = {
                ...user,
                dva_account_number: account_number,
                dva_bank_name: bank_name
            };

            login(localStorage.getItem('token'), updatedUser); // Update context
            setMsg({ type: 'success', text: `Virtual Account Created: ${account_number} (${bank_name})` });
        } catch (error) {
            console.error(error);
            setMsg({ type: 'error', text: error.response?.data?.detail || 'Virtual Account creation failed. Ensure names match BVN.' });
        } finally {
            setDvaLoading(false);
        }
    };

    const isPartner = ['farmer', 'processor', 'aggregator', 'business'].includes(user?.role);

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-2xl relative">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                >
                    ×
                </button>

                <h2 className="text-xl font-bold text-gray-900 mb-6">Edit Profile</h2>

                {msg.text && (
                    <div className={`p-3 rounded mb-4 text-sm ${msg.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {msg.text}
                    </div>
                )}

                <form onSubmit={handleUpdate} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                        <input
                            type="text"
                            value={formData.first_name}
                            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Middle Name</label>
                        <input
                            type="text"
                            value={formData.middle_name}
                            onChange={(e) => setFormData({ ...formData, middle_name: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                        <input
                            type="text"
                            value={formData.last_name}
                            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium disabled:opacity-50"
                    >
                        {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                </form>

                {/* DVA Section */}
                {isPartner && (
                    <div className="mt-8 pt-6 border-t border-gray-200">
                        <h3 className="text-sm font-semibold text-gray-900 mb-2">Virtual Account Status</h3>
                        {user?.dva_account_number ? (
                            <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-100">
                                <p className="text-xs text-emerald-600 uppercase font-bold">Active</p>
                                <p className="font-mono text-lg font-bold text-emerald-800">{user.dva_account_number}</p>
                                <p className="text-sm text-emerald-700">{user.dva_bank_name}</p>
                            </div>
                        ) : (
                            <div>
                                <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200 mb-4 text-sm text-yellow-800">
                                    <p className="font-bold mb-1">No Virtual Account</p>
                                    <p>You cannot receive automated payouts. Ensure your profile name matches your BVN exactly.</p>
                                </div>

                                <div className="mb-4">
                                    <label className="block text-xs font-medium text-gray-700 mb-1">
                                        Update BVN (Optional - if previous attempts failed)
                                    </label>
                                    <input
                                        type="text"
                                        value={bvn}
                                        onChange={(e) => setBvn(e.target.value)}
                                        placeholder="Enter corrected BVN only if needed"
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500 text-sm"
                                        maxLength={11}
                                    />
                                </div>

                                <button
                                    onClick={handleCreateDVA}
                                    disabled={dvaLoading}
                                    className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50"
                                >
                                    {dvaLoading ? 'Verifying...' : 'Create Virtual Account'}
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default EditProfileModal;
