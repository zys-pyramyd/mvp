import React, { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import VerificationStep from './VerificationStep';

const FarmerFlow = ({ step, formData, updateFormData, setStep, onRegister }) => {
    const [localStep, setLocalStep] = useState(step === 'verification' ? 3 : 1); // 1: Personal, 2: Farms, 3: Verification
    const [showAddFarm, setShowAddFarm] = useState(false);
    const [newFarm, setNewFarm] = useState({
        size: '',
        size_unit: 'acres',
        products: [], // list of strings
        output_qty: '',
        output_unit: 'kg',
        address: ''
    });
    const [currentProduct, setCurrentProduct] = useState('');

    // Predefined lists
    const commonCrops = [
        'Maize', 'Rice', 'Cassava', 'Yam', 'Beans', 'Soybeans',
        'Tomatoes', 'Pepper', 'Broccoli', 'Onions', 'Potatoes',
        'Poultry', 'Fish', 'Cattle', 'Goat', 'Pig'
    ];

    const handlePersonalSubmit = (e) => {
        e.preventDefault();
        setLocalStep(2);
    };

    const handleFarmSubmit = () => {
        if ((formData.farm_details || []).length === 0) {
            alert("Please add at least one farm.");
            return;
        }
        setStep('verification');
        setLocalStep(3);
    };

    const addFarm = () => {
        if (!newFarm.size || !newFarm.address || newFarm.products.length === 0) {
            alert("Please fill all farm details and add at least one product.");
            return;
        }
        updateFormData({
            farm_details: [...(formData.farm_details || []), newFarm]
        });
        setNewFarm({ size: '', size_unit: 'acres', products: [], output_qty: '', output_unit: 'kg', address: '' });
        setShowAddFarm(false);
    };

    const addProductToFarm = () => {
        if (currentProduct && !newFarm.products.includes(currentProduct)) {
            setNewFarm(prev => ({ ...prev, products: [...prev.products, currentProduct] }));
            setCurrentProduct('');
        }
    };

    if (step === 'verification' || localStep === 3) {
        return (
            <VerificationStep
                formData={formData}
                updateFormData={updateFormData}
                onRegister={onRegister}
                role="farmer"
                requiredDocs={['headshot', 'id_document', 'proof_of_address']}
                docLabels={{
                    headshot: "Take a Profile Picture (Selfie)",
                    id_document: "Upload NIN Slip or ID Card",
                    proof_of_address: "Proof of Residential Address"
                }}
            />
        );
    }

    if (localStep === 2) {
        return (
            <div className="space-y-6">
                <h3 className="text-lg font-bold">Farm Details</h3>
                <p className="text-sm text-gray-600">Tell us about your farm capacity. You can add multiple farms.</p>

                {/* List of Added Farms */}
                <div className="space-y-3">
                    {(formData.farm_details || []).map((farm, idx) => (
                        <div key={idx} className="p-4 border rounded-lg bg-gray-50 flex justify-between items-start">
                            <div>
                                <p className="font-bold text-gray-900">{farm.size} {farm.size_unit} Farm</p>
                                <p className="text-sm text-gray-600">{farm.address}</p>
                                <p className="text-sm text-gray-600 mt-1">
                                    Products: <span className="font-medium">{farm.products.join(', ')}</span>
                                </p>
                                <p className="text-sm text-gray-600">
                                    Output: {farm.output_qty} {farm.output_unit}
                                </p>
                            </div>
                            <button
                                onClick={() => {
                                    const newFarms = [...formData.farm_details];
                                    newFarms.splice(idx, 1);
                                    updateFormData({ farm_details: newFarms });
                                }}
                                className="text-red-500 hover:text-red-700 p-1"
                            >
                                <Trash2 size={20} />
                            </button>
                        </div>
                    ))}
                </div>

                {/* Add Farm Button */}
                {!showAddFarm && (
                    <button
                        onClick={() => setShowAddFarm(true)}
                        className="w-full py-3 border-2 border-dashed border-emerald-500 text-emerald-600 rounded-lg font-medium hover:bg-emerald-50 flex items-center justify-center gap-2"
                    >
                        <Plus size={20} /> Add Farm
                    </button>
                )}

                {/* Add Farm Form */}
                {showAddFarm && (
                    <div className="p-4 border rounded-lg bg-white shadow-sm space-y-4">
                        <h4 className="font-bold text-gray-800">New Farm Information</h4>

                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <label className="text-xs font-medium text-gray-700">Size</label>
                                <div className="flex">
                                    <input
                                        type="number"
                                        value={newFarm.size}
                                        onChange={e => setNewFarm({ ...newFarm, size: e.target.value })}
                                        className="w-full border p-2 rounded-l"
                                        placeholder="0"
                                    />
                                    <select
                                        value={newFarm.size_unit}
                                        onChange={e => setNewFarm({ ...newFarm, size_unit: e.target.value })}
                                        className="border border-l-0 p-2 rounded-r bg-gray-100"
                                    >
                                        <option value="acres">Acres</option>
                                        <option value="hectares">Hectares</option>
                                        <option value="plots">Plots</option>
                                    </select>
                                </div>
                            </div>
                            <div>
                                <label className="text-xs font-medium text-gray-700">Est. Output</label>
                                <div className="flex">
                                    <input
                                        type="number"
                                        value={newFarm.output_qty}
                                        onChange={e => setNewFarm({ ...newFarm, output_qty: e.target.value })}
                                        className="w-full border p-2 rounded-l"
                                        placeholder="Qty"
                                    />
                                    <select
                                        value={newFarm.output_unit}
                                        onChange={e => setNewFarm({ ...newFarm, output_unit: e.target.value })}
                                        className="border border-l-0 p-2 rounded-r bg-gray-100"
                                    >
                                        <option value="kg">Kg</option>
                                        <option value="bags_50kg">50kg Bag</option>
                                        <option value="bags_100kg">100kg Bag</option>
                                        <option value="crates">Crates</option>
                                        <option value="baskets">Baskets</option>
                                        <option value="tonnes">Tonnes</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="text-xs font-medium text-gray-700">Farm Address</label>
                            <input
                                type="text"
                                value={newFarm.address}
                                onChange={e => setNewFarm({ ...newFarm, address: e.target.value })}
                                className="w-full border p-2 rounded"
                                placeholder="Location of farm..."
                            />
                        </div>

                        <div>
                            <label className="text-xs font-medium text-gray-700">Products Produced</label>
                            <div className="flex gap-2 mb-2">
                                <input
                                    list="crops"
                                    value={currentProduct}
                                    onChange={e => setCurrentProduct(e.target.value)}
                                    className="flex-1 border p-2 rounded"
                                    placeholder="Type or select crop..."
                                />
                                <datalist id="crops">
                                    {commonCrops.map(c => <option key={c} value={c} />)}
                                </datalist>
                                <button
                                    onClick={addProductToFarm}
                                    className="bg-emerald-600 text-white px-4 rounded hover:bg-emerald-700"
                                >Add</button>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {newFarm.products.map(p => (
                                    <span key={p} className="bg-emerald-100 text-emerald-800 text-xs px-2 py-1 rounded-full flex items-center">
                                        {p}
                                        <button
                                            onClick={() => setNewFarm(prev => ({ ...prev, products: prev.products.filter(pr => pr !== p) }))}
                                            className="ml-1 hover:text-emerald-900"
                                        >×</button>
                                    </span>
                                ))}
                            </div>
                        </div>

                        <div className="flex gap-2 pt-2">
                            <button
                                onClick={() => setShowAddFarm(false)}
                                className="flex-1 py-2 border rounded hover:bg-gray-50 text-gray-600"
                            >Cancel</button>
                            <button
                                onClick={addFarm}
                                className="flex-1 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700"
                            >Save Farm</button>
                        </div>
                    </div>
                )}

                <div className="flex justify-between pt-4">
                    <button onClick={() => setLocalStep(1)} className="text-gray-500 hover:text-gray-700">Back</button>
                    <button
                        onClick={handleFarmSubmit}
                        disabled={showAddFarm}
                        className="bg-emerald-600 text-white py-2 px-6 rounded-lg hover:bg-emerald-700 disabled:bg-gray-400"
                    >
                        Next
                    </button>
                </div>
            </div>
        );
    }

    // Local Step 1: Personal Details (Gender, DOB)
    return (
        <form onSubmit={handlePersonalSubmit} className="space-y-4">
            <h3 className="text-lg font-bold mb-4">Farmer Personal Details</h3>

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
                    placeholder="Enter your home address"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                    rows="3"
                    required
                />
            </div>

            <button
                type="submit"
                className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg hover:bg-emerald-700 transition-colors font-medium mt-6"
            >
                Continue to Farm Details
            </button>
        </form>
    );
};

export default FarmerFlow;
