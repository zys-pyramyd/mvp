import React, { useState } from 'react';

const ProductModal = ({ product, variant, isOpen, onClose, onAddToCart, onCommit, onChatAgent, dropOffLocations = [] }) => {
    const [quantity, setQuantity] = useState(1);
    const [selectedDropOff, setSelectedDropOff] = useState('');
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    if (!isOpen || !product) return null;

    const images = product.images && product.images.length > 0 ? product.images : [];
    const hasMultipleImages = images.length > 1;

    const handleAction = (actionType) => {
        let dropoffLoc = null;
        if (dropOffLocations.length > 0 && actionType !== 'commit') {
            if (!selectedDropOff) {
                alert("Please select a drop-off location.");
                return;
            }
            dropoffLoc = dropOffLocations.find(l => l.id.toString() === selectedDropOff);
        }

        if (actionType === 'commit') {
            onCommit(product, quantity);
        } else {
            onAddToCart(product, quantity, dropoffLoc);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col md:flex-row shadow-2xl animate-scale-in">

                {/* Left Column: Images */}
                <div className="w-full md:w-1/2 bg-gray-100 p-4 flex flex-col justify-center relative">
                    <div className="aspect-w-4 aspect-h-3 mb-4 rounded-lg overflow-hidden bg-white shadow-inner">
                        {images.length > 0 ? (
                            <img
                                src={images[currentImageIndex]}
                                alt={product.title}
                                className="w-full h-full object-contain"
                            />
                        ) : (
                            <div className="flex items-center justify-center h-64 text-gray-300">
                                <span className="text-6xl">📦</span>
                            </div>
                        )}
                    </div>

                    {/* Thumbnails */}
                    {hasMultipleImages && (
                        <div className="flex space-x-2 overflow-x-auto p-2 scrollbar-hide">
                            {images.map((img, idx) => (
                                <div
                                    key={idx}
                                    className={`w-16 h-16 flex-shrink-0 cursor-pointer border-2 rounded-md overflow-hidden ${idx === currentImageIndex ? 'border-emerald-500' : 'border-transparent'}`}
                                    onClick={() => setCurrentImageIndex(idx)}
                                >
                                    <img src={img} alt={`Thumbnail ${idx}`} className="w-full h-full object-cover" />
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Close Button Mobile */}
                    <button onClick={onClose} className="md:hidden absolute top-4 right-4 bg-white p-2 rounded-full shadow-lg">
                        ✕
                    </button>
                </div>

                {/* Right Column: Details */}
                <div className="w-full md:w-1/2 p-6 overflow-y-auto bg-white flex flex-col">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            {variant === 'wholesale' && <span className="text-orange-600 font-bold text-xs tracking-wider">FARM DEAL WHOLESALE</span>}
                            {variant === 'retail' && <span className="text-emerald-600 font-bold text-xs tracking-wider">PYEXPRESS RETAIL</span>}
                            {variant === 'community' && <span className="text-purple-600 font-bold text-xs tracking-wider">COMMUNITY BUY</span>}
                            <h2 className="text-2xl font-bold text-gray-900 mt-1">{product.title || product.product_name}</h2>
                            <p className="text-sm text-gray-500">{product.category}</p>
                        </div>
                        <button onClick={onClose} className="hidden md:block text-gray-400 hover:text-gray-600 text-2xl">
                            ✕
                        </button>
                    </div>

                    {/* Price */}
                    <div className="mb-6 pb-6 border-b border-gray-100">
                        <div className="flex items-baseline space-x-2">
                            <span className="text-3xl font-bold text-emerald-600">₦{product.price_per_unit || product.price}</span>
                            <span className="text-gray-500 font-medium">/ {product.unit}</span>
                        </div>
                        {product.discount_value && (
                            <div className="mt-2 text-sm text-red-600 font-medium bg-red-50 inline-block px-2 py-1 rounded">
                                🔥 Discount Active
                            </div>
                        )}
                    </div>

                    {/* Description & Specs */}
                    <div className="space-y-4 mb-6 flex-1">
                        <div>
                            <h3 className="font-bold text-gray-900 mb-2">Description</h3>
                            <p className="text-gray-600 text-sm leading-relaxed">{product.description || "No description provided."}</p>
                        </div>

                        {product.about_product && (
                            <div className="mt-4">
                                <h3 className="font-bold text-gray-900 mb-2">About Product</h3>
                                <p className="text-gray-600 text-sm leading-relaxed">{product.about_product}</p>
                            </div>
                        )}

                        {product.product_benefits && product.product_benefits.length > 0 && (
                            <div className="mt-4">
                                <h3 className="font-bold text-gray-900 mb-2">Benefits</h3>
                                <ul className="list-disc list-inside text-gray-600 text-sm space-y-1">
                                    {product.product_benefits.map((benefit, idx) => (
                                        <li key={idx}>{benefit}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {product.usage_instructions && (
                            <div className="mt-4">
                                <h3 className="font-bold text-gray-900 mb-2">Usage Instructions</h3>
                                <p className="text-gray-600 text-sm leading-relaxed">{product.usage_instructions}</p>
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-4 text-sm">
                            {product.best_before && (
                                <div className="bg-gray-50 p-2 rounded">
                                    <span className="block text-gray-500 text-xs">Best Before (Raw)</span>
                                    <span className="font-medium">{new Date(product.best_before).toLocaleDateString()}</span>
                                </div>
                            )}
                            {product.expiry_date && (
                                <div className="bg-gray-50 p-2 rounded">
                                    <span className="block text-gray-500 text-xs">Expiry Date (Processed)</span>
                                    <span className="font-medium text-red-600">{new Date(product.expiry_date).toLocaleDateString()}</span>
                                </div>
                            )}
                            <div className="bg-gray-50 p-2 rounded">
                                <span className="block text-gray-500 text-xs">Available Stock</span>
                                <span className="font-medium">{product.quantity_available} {product.unit}</span>
                            </div>
                            <div className="bg-gray-50 p-2 rounded">
                                <span className="block text-gray-500 text-xs">Location</span>
                                <span className="font-medium">{product.location}</span>
                            </div>
                        </div>

                        {/* Seller / Farmer / Agent Profile */}
                        <div className="mt-4 p-3 border border-gray-200 rounded-lg">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center text-xl">
                                    {product.seller_name ? product.seller_name[0].toUpperCase() : 'S'}
                                </div>
                                <div className="flex-1">
                                    <p className="text-sm font-bold text-gray-900">{product.seller_name || "Seller"}</p>
                                    <p className="text-xs text-gray-500 capitalize">{product.seller_type || "Merchant"}</p>
                                </div>
                                {/* Agent Chat Button */}
                                {variant !== 'retail' && product.agent_name && (
                                    <button
                                        onClick={() => onChatAgent && onChatAgent(product)}
                                        className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full hover:bg-blue-200"
                                    >
                                        💬 Chat
                                    </button>
                                )}
                            </div>
                            {product.farm_name && (
                                <div className="mt-2 text-xs text-gray-600 pl-13">
                                    📍 Farm: <span className="font-medium">{product.farm_name}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Actions Footer */}
                    <div className="bg-gray-50 -mx-6 -mb-6 p-6 mt-auto">
                        <div className="mb-4">
                            {/* Quantity Selector */}
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center border border-gray-300 rounded-lg bg-white">
                                    <button onClick={() => setQuantity(Math.max(1, quantity - 1))} className="px-3 py-2 text-gray-600 hover:bg-gray-100">-</button>
                                    <span className="px-3 py-2 font-medium w-12 text-center">{quantity}</span>
                                    <button onClick={() => setQuantity(quantity + 1)} className="px-3 py-2 text-gray-600 hover:bg-gray-100">+</button>
                                </div>
                                <div className="text-right">
                                    <span className="block text-xs text-gray-500">Total</span>
                                    <span className="block text-xl font-bold text-emerald-700">₦{(quantity * (product.price_per_unit || product.price)).toLocaleString()}</span>
                                </div>
                            </div>

                            {/* Dropoff Location Selector */}
                            {dropOffLocations.length > 0 && variant !== 'community' && (
                                <div className="mb-4">
                                    <label className="block text-xs font-medium text-gray-700 mb-1">Select Drop-off Location</label>
                                    <select
                                        value={selectedDropOff}
                                        onChange={(e) => setSelectedDropOff(e.target.value)}
                                        className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                                    >
                                        <option value="">-- Choose Location --</option>
                                        {dropOffLocations.map(loc => (
                                            <option key={loc.id} value={loc.id}>{loc.name} - {loc.city}</option>
                                        ))}
                                    </select>
                                </div>
                            )}
                        </div>

                        <div className="flex space-x-3">
                            {variant === 'community' ? (
                                <button
                                    onClick={() => handleAction('commit')}
                                    className="flex-1 bg-purple-600 text-white py-3 rounded-lg font-bold hover:bg-purple-700 shadow-lg transform active:scale-95 transition-all"
                                >
                                    🤝 Commit to Group Order
                                </button>
                            ) : (
                                <>
                                    <button
                                        onClick={() => handleAction('cart')}
                                        className="flex-1 bg-white border-2 border-emerald-600 text-emerald-700 py-3 rounded-lg font-bold hover:bg-emerald-50 transition-colors"
                                    >
                                        Add to Cart
                                    </button>
                                    <button
                                        onClick={() => handleAction('cart')}
                                        className="flex-1 bg-emerald-600 text-white py-3 rounded-lg font-bold hover:bg-emerald-700 shadow-lg transform active:scale-95 transition-all"
                                    >
                                        Buy Now
                                    </button>
                                </>
                            )}
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default ProductModal;
