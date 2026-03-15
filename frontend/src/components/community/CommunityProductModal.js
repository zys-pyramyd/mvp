import React, { useState } from 'react';
import { NIGERIAN_STATES } from '../../nigerianStates';

const PRODUCT_CATEGORIES = {
    grains_cereals: {
        label: "Grains & Cereals",
        subcategories: ["maize", "rice", "wheat", "oat", "barley", "sorghum", "millet", "rye", "triticale"]
    },
    beans_legumes: {
        label: "Beans & Legumes",
        subcategories: ["lentils", "peas", "beans", "broad_beans", "groundnut", "soybeans"]
    },
    fish_meat: {
        label: "Fish & Meat",
        subcategories: ["fresh_fish", "dried_fish", "poultry", "beef", "goat_mutton", "pork", "snails"]
    },
    spices_vegetables: {
        label: "Spices & Vegetables",
        subcategories: ["leafy_vegetables", "peppers", "tomatoes", "onions", "ginger_garlic", "herbs_spices", "okra", "cucumber"]
    },
    tubers_roots: {
        label: "Tubers & Roots",
        subcategories: ["yam", "cassava", "sweet_potato", "chinese_yam", "taro", "potato", "carrots", "turnips", "parsnips", "radish", "celeriac", "ginger", "turmeric", "beets", "burdock_root"]
    },
    drinks_beverage: {
        label: "Drinks & Beverage",
        subcategories: ["milk", "chocolate_drinks", "water", "soft_drinks_carbonated", "juices_smoothies", "hot_beverage", "energy_drinks", "health_drinks", "dairy_plant_based", "cordials_squash"]
    },
    snacks_confectionaries: {
        label: "Snacks & Confectionaries",
        subcategories: ["chocolates", "candy_gummy", "chips_crisps", "pretzels_crackers", "popcorn", "nuts_seeds", "dried_fruits_trail_mix", "granola_energy_bars", "cookies_biscuits", "snack_cakes_pastries"]
    },
    sweets_sugar: {
        label: "Sweets & Sugar",
        subcategories: ["sugar", "honey", "dates", "agave", "artificial_sweetener", "syrups"]
    },
    farm_inputs: {
        label: "Farm Inputs",
        subcategories: []
    },
    flour_flakes: {
        label: "Flour & Flakes",
        subcategories: ["all_purpose_flour", "yam_flour", "cassava_flakes_garri", "cassava_flour", "bread_flour", "cake_flour", "pastry_flour", "whole_wheat", "self_rising_flour", "semolina_flour", "nut_flour", "coconut_flour", "rice_flour", "others"]
    },
    other: {
        label: "Other",
        subcategories: []
    }
};

const formatLabel = (str) => {
    return str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const PREDEFINED_COLORS = ['white', 'brown', 'green', 'red', 'yellow', 'silver', 'black', 'grey', 'ash'];

const CommunityProductModal = ({ community, onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        category: 'grains_cereals',
        subcategory: '',
        processing_level: 'unprocessed',
        price_per_unit: '',
        unit: 'kg',
        quantity: '',
        location: community.location || '',
        city: '',
        pickup_address: '',
        country: 'Nigeria',
        colors: [],
        seller_delivery_fee: 0,
        images: [],
        min_order_quantity: 1,
        is_preorder: false,
        preorder_deadline: '',
        target_quantity: '',
        community_id: community.id // Pre-fill community ID
    });
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);

    const token = localStorage.getItem('token');

    const handleImageUpload = async (e) => {
        const files = Array.from(e.target.files);
        setUploading(true);

        try {
            const uploadedUrls = [];
            for (const file of files) {
                // 1. Get Signed URL
                const signRes = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upload/sign`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        folder: 'products',
                        filename: file.name,
                        contentType: file.type
                    })
                });

                if (!signRes.ok) throw new Error('Failed to get upload signature');
                const { uploadUrl, publicUrl } = await signRes.json();

                // 2. Upload to R2
                const uploadRes = await fetch(uploadUrl, {
                    method: 'PUT',
                    headers: { 'Content-Type': file.type },
                    body: file
                });

                if (!uploadRes.ok) throw new Error('Failed to upload image');
                uploadedUrls.push(publicUrl);
            }

            setFormData(prev => ({
                ...prev,
                images: [...prev.images, ...uploadedUrls]
            }));

        } catch (error) {
            console.error("Upload error:", error);
            alert("Failed to upload image(s)");
        } finally {
            setUploading(false);
        }
    };

    const removeImage = (index) => {
        setFormData(prev => ({
            ...prev,
            images: prev.images.filter((_, i) => i !== index)
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const payload = {
                ...formData,
                type: formData.is_preorder ? 'preorder' : 'standard',
                platform: 'community', // Explicitly set platform
                unit_of_measure: formData.unit,
                quantity_available: parseInt(formData.quantity) || 0,
                minimum_order_quantity: parseInt(formData.min_order_quantity) || 1,
                colors: formData.colors,
                // Category and Subcategory and processing_level pass smoothly without hacky mapping
            };

            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/products`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert('Item listed in community marketplace!');
                onSuccess();
            } else {
                const error = await response.json();
                alert(error.detail || 'Failed to list item');
            }
        } catch (error) {
            console.error(error);
            alert('Error creating listing');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
            <div className="bg-white rounded-xl max-w-2xl w-full p-6 my-8 max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h2 className="text-xl font-bold">Sell in {community.name}</h2>
                        <p className="text-sm text-gray-500">List an item for community members</p>
                    </div>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Title</label>
                            <input
                                type="text"
                                required
                                className="w-full border rounded p-2"
                                value={formData.title}
                                onChange={e => setFormData({ ...formData, title: e.target.value })}
                                placeholder="What are you selling?"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Category</label>
                            <select
                                className="w-full border rounded p-2"
                                value={formData.category}
                                onChange={e => setFormData({ ...formData, category: e.target.value, subcategory: '' })}
                            >
                                {Object.entries(PRODUCT_CATEGORIES).map(([key, cat]) => (
                                    <option key={key} value={key}>{cat.label}</option>
                                ))}
                            </select>
                        </div>
                        {PRODUCT_CATEGORIES[formData.category]?.subcategories?.length > 0 && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Subcategory</label>
                                <select
                                    required
                                    className="w-full border rounded p-2"
                                    value={formData.subcategory}
                                    onChange={e => setFormData({ ...formData, subcategory: e.target.value })}
                                >
                                    <option value="">Select Subcategory</option>
                                    {PRODUCT_CATEGORIES[formData.category].subcategories.map(sub => (
                                        <option key={sub} value={sub}>{formatLabel(sub)}</option>
                                    ))}
                                </select>
                            </div>
                        )}
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Nutritional Mode</label>
                            <select
                                className="w-full border rounded p-2"
                                value={formData.processing_level}
                                onChange={e => setFormData({ ...formData, processing_level: e.target.value })}
                            >
                                <option value="unprocessed">Unprocessed</option>
                                <option value="processed">Processed</option>
                                <option value="ultraprocessed">Ultra-processed</option>
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="col-span-2">
                            <label className="block text-sm font-medium text-gray-700">Price (₦)</label>
                            <input
                                type="number"
                                required
                                className="w-full border rounded p-2"
                                value={formData.price_per_unit}
                                onChange={e => setFormData({ ...formData, price_per_unit: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Quantity</label>
                            <input
                                type="number"
                                required
                                className="w-full border rounded p-2"
                                value={formData.quantity}
                                onChange={e => setFormData({ ...formData, quantity: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Unit</label>
                            <select
                                className="w-full border rounded p-2"
                                value={formData.unit}
                                onChange={e => setFormData({ ...formData, unit: e.target.value })}
                            >
                                <option value="kg">kg</option>
                                <option value="bag">bag</option>
                                <option value="litre">litre</option>
                                <option value="basket">basket</option>
                                <option value="crate">crate</option>
                                <option value="piece">piece</option>
                            </select>
                        </div>
                    </div>

                    <div className="border border-gray-200 p-4 rounded-lg my-4">
                        <label className="block text-sm font-bold text-gray-700 mb-2">Available Colors (Optional)</label>
                        <p className="text-xs text-gray-500 mb-3">Select one or multiple colors if applicable to your product.</p>
                        <div className="flex flex-wrap gap-3">
                            {PREDEFINED_COLORS.map(c => (
                                <label key={c} className="flex items-center gap-2 text-sm bg-gray-50 px-3 py-2 rounded-lg border cursor-pointer hover:bg-gray-100 transition-colors">
                                    <input
                                        type="checkbox"
                                        checked={formData.colors.includes(c)}
                                        onChange={e => {
                                            if (e.target.checked) setFormData({ ...formData, colors: [...formData.colors, c] });
                                            else setFormData({ ...formData, colors: formData.colors.filter(col => col !== c) });
                                        }}
                                        className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                                    />
                                    {c.charAt(0).toUpperCase() + c.slice(1)}
                                </label>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Photos</label>
                        <div className="flex flex-wrap gap-2 mb-2">
                            {formData.images.map((url, i) => (
                                <div key={i} className="relative w-20 h-20 border rounded overflow-hidden">
                                    <img src={url} alt="Product" className="w-full h-full object-cover" />
                                    <button
                                        type="button"
                                        onClick={() => removeImage(i)}
                                        className="absolute top-0 right-0 bg-red-500 text-white rounded-bl p-1 text-xs"
                                    >✕</button>
                                </div>
                            ))}
                            <div className="w-20 h-20 border-2 border-dashed border-gray-300 rounded flex items-center justify-center relative hover:bg-gray-50">
                                {uploading ? (
                                    <span className="text-xs text-gray-500">Uploading...</span>
                                ) : (
                                    <>
                                        <span className="text-2xl text-gray-400">+</span>
                                        <input
                                            type="file"
                                            accept="image/*"
                                            multiple
                                            onChange={handleImageUpload}
                                            className="absolute inset-0 opacity-0 cursor-pointer"
                                        />
                                    </>
                                )}
                            </div>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">Description</label>
                        <textarea
                            required
                            className="w-full border rounded p-2 h-24"
                            value={formData.description}
                            onChange={e => setFormData({ ...formData, description: e.target.value })}
                            placeholder="Describe your item..."
                        ></textarea>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">State</label>
                            <select
                                required
                                className="w-full border rounded p-2"
                                value={formData.location}
                                onChange={e => setFormData({ ...formData, location: e.target.value })}
                            >
                                <option value="">Select State</option>
                                {NIGERIAN_STATES.map(state => (
                                    <option key={state} value={state}>{state}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">City / Location</label>
                            <input
                                type="text"
                                required
                                className="w-full border rounded p-2"
                                value={formData.city}
                                onChange={e => setFormData({ ...formData, city: e.target.value })}
                                placeholder="e.g. Ikeja"
                            />
                        </div>
                    </div>

                    <div className="flex justify-end gap-2 pt-4 border-t">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-gray-600 hover:text-gray-800"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading || uploading}
                            className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:bg-gray-400"
                        >
                            {loading ? 'Listing...' : 'List Item'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CommunityProductModal;
