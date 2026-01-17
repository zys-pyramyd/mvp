import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const WalletModal = ({ isOpen, onClose, userProfile }) => {
    const [walletData, setWalletData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showFundInstructions, setShowFundInstructions] = useState(false);
    const [fundAmount, setFundAmount] = useState('');

    useEffect(() => {
        if (isOpen) {
            fetchWalletBalance();
        }
    }, [isOpen]);

    const fetchWalletBalance = async () => {
        setLoading(true);
        try {
            const response = await api.get('/users/wallet/balance');
            setWalletData(response.data);
        } catch (error) {
            console.error('Failed to fetch wallet balance:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleFundWallet = async () => {
        if (!fundAmount || parseFloat(fundAmount) <= 0) {
            alert('Please enter a valid amount');
            return;
        }

        try {
            const response = await api.post('/users/wallet/fund', {
                amount: parseFloat(fundAmount)
            });
            setShowFundInstructions(true);
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to initiate funding');
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-content" style={{ maxWidth: '600px' }}>
                <div className="modal-header">
                    <h3>💰 My Wallet</h3>
                    <button className="close-button" onClick={onClose}>&times;</button>
                </div>

                <div className="modal-body">
                    {loading ? (
                        <div className="text-center py-8">
                            <p>Loading wallet...</p>
                        </div>
                    ) : walletData ? (
                        <>
                            {/* Balance Display */}
                            <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-lg mb-4">
                                <p className="text-sm text-gray-600 mb-1">Available Balance</p>
                                <h2 className="text-4xl font-bold text-green-600">
                                    ₦{walletData.balance?.toLocaleString() || '0'}
                                </h2>
                            </div>

                            {/* DVA Details */}
                            {walletData.has_dva ? (
                                <div className="bg-blue-50 p-4 rounded-lg mb-4">
                                    <h4 className="font-semibold mb-3 flex items-center">
                                        <span className="text-2xl mr-2">🏦</span>
                                        Dedicated Virtual Account
                                    </h4>
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Bank Name:</span>
                                            <span className="font-semibold">{walletData.dva_bank_name}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Account Number:</span>
                                            <span className="font-semibold text-lg">{walletData.dva_account_number}</span>
                                        </div>
                                    </div>
                                    <div className="mt-3 p-3 bg-white rounded border border-blue-200">
                                        <p className="text-xs text-gray-600">
                                            💡 <strong>How to fund:</strong> Transfer money to this account from any bank.
                                            Your wallet will be credited automatically within minutes.
                                        </p>
                                    </div>
                                </div>
                            ) : (
                                <div className="bg-yellow-50 p-4 rounded-lg mb-4">
                                    <p className="text-sm text-gray-700">
                                        ⚠️ No dedicated virtual account found. Please contact support to activate your wallet.
                                    </p>
                                </div>
                            )}

                            {/* Fund Wallet Section */}
                            {!showFundInstructions ? (
                                <div className="border-t pt-4">
                                    <h4 className="font-semibold mb-3">Fund Wallet</h4>
                                    <div className="flex gap-2">
                                        <input
                                            type="number"
                                            className="form-input flex-1"
                                            placeholder="Enter amount"
                                            value={fundAmount}
                                            onChange={(e) => setFundAmount(e.target.value)}
                                        />
                                        <button
                                            className="btn-primary"
                                            onClick={handleFundWallet}
                                            disabled={!walletData.has_dva}
                                        >
                                            Get Details
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                                    <h4 className="font-semibold text-green-700 mb-2">
                                        ✅ Funding Instructions
                                    </h4>
                                    <p className="text-sm mb-3">
                                        Transfer <strong>₦{parseFloat(fundAmount).toLocaleString()}</strong> to:
                                    </p>
                                    <div className="bg-white p-3 rounded border border-green-300 mb-3">
                                        <p className="font-semibold">{walletData.dva_bank_name}</p>
                                        <p className="text-2xl font-bold text-green-600">{walletData.dva_account_number}</p>
                                    </div>
                                    <p className="text-xs text-gray-600">
                                        Your wallet will be credited automatically once the transfer is confirmed.
                                    </p>
                                    <button
                                        className="btn-secondary mt-3 w-full"
                                        onClick={() => {
                                            setShowFundInstructions(false);
                                            setFundAmount('');
                                        }}
                                    >
                                        Done
                                    </button>
                                </div>
                            )}

                            {/* Quick Actions */}
                            <div className="mt-4 pt-4 border-t">
                                <p className="text-xs text-gray-500 mb-2">Quick Actions:</p>
                                <div className="grid grid-cols-2 gap-2">
                                    <button className="btn-secondary text-sm py-2">
                                        📊 Transaction History
                                    </button>
                                    <button className="btn-secondary text-sm py-2">
                                        💸 Withdraw Funds
                                    </button>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="text-center py-8">
                            <p>Failed to load wallet data</p>
                            <button className="btn-primary mt-4" onClick={fetchWalletBalance}>
                                Retry
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WalletModal;
