import React from 'react';

const PathSelectionStep = ({ formData, updateFormData, onNext }) => {
    const handleSelect = (path) => {
        const updates = { user_path: path };
        if (path === 'buyer') {
            updates.buyer_type = 'personal';
        }
        updateFormData(updates);
        onNext(path);
    };

    return (
        <div className="space-y-6">
            <h3 className="text-lg font-medium text-center mb-6">How would you like to use Pyramyd?</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Buyer Option */}
                <div
                    onClick={() => handleSelect('buyer')}
                    className={`p-6 border-2 rounded-xl cursor-pointer transition-all hover:shadow-lg ${formData.user_path === 'buyer' ? 'border-emerald-600 bg-emerald-50' : 'border-gray-200 hover:border-emerald-300'
                        }`}
                >
                    <div className="text-4xl mb-4 text-center">🛍️</div>
                    <h4 className="text-xl font-bold text-center mb-2">Join as Buyer</h4>
                    <p className="text-gray-600 text-center text-sm">
                        Access fresh farm produce at the best prices. Join community buy groups and save more.
                    </p>
                </div>

                {/* Partner Option */}
                <div
                    onClick={() => handleSelect('partner')}
                    className={`p-6 border-2 rounded-xl cursor-pointer transition-all hover:shadow-lg ${formData.user_path === 'partner' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'
                        }`}
                >
                    <div className="text-4xl mb-4 text-center">🤝</div>
                    <h4 className="text-xl font-bold text-center mb-2">Join as Partner</h4>
                    <p className="text-gray-600 text-center text-sm">
                        Sell your produce, become an agent, or list your business on Pyramyd.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default PathSelectionStep;
