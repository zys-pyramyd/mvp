import React from 'react';

const PartnerTypeSelectionStep = ({ formData, updateFormData, onNext }) => {

    const handleSelect = (type) => {
        updateFormData({ partner_type: type });
        // Small delay to show selection visual
        setTimeout(() => onNext(), 300);
    };

    const types = [
        {
            id: 'agent',
            icon: '🕵️',
            title: 'Agent',
            description: 'Connect buyers and sellers, earn commissions, and manage logistics.'
        },
        {
            id: 'farmer',
            icon: '👨‍🌾',
            title: 'Farmer',
            description: 'List your farm produce, reach more buyers, and grow your business.'
        },
        {
            id: 'business',
            icon: '🏢',
            title: 'Business',
            description: 'Processors, Suppliers, Restaurants, and other agritech businesses.'
        }
    ];

    return (
        <div className="space-y-6">
            <h3 className="text-lg font-medium text-center mb-6">Select your Partner Role</h3>

            <div className="grid grid-cols-1 gap-4">
                {types.map((type) => (
                    <div
                        key={type.id}
                        onClick={() => handleSelect(type.id)}
                        className={`flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all hover:shadow-md ${formData.partner_type === type.id ? 'border-purple-600 bg-purple-50' : 'border-gray-200 hover:border-purple-300'
                            }`}
                    >
                        <div className="text-3xl mr-4">{type.icon}</div>
                        <div className="flex-1">
                            <h4 className="text-lg font-bold text-gray-800">{type.title}</h4>
                            <p className="text-sm text-gray-600">{type.description}</p>
                        </div>
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${formData.partner_type === type.id ? 'border-purple-600 bg-purple-600' : 'border-gray-300'
                            }`}>
                            {formData.partner_type === type.id && <div className="w-2.5 h-2.5 bg-white rounded-full" />}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PartnerTypeSelectionStep;
