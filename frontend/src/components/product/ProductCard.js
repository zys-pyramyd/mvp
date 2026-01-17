import React, { useState } from 'react';
import PreOrderTimer from './PreOrderTimer';

const VerifiedBadge = () => (
    <span className="inline-flex items-center justify-center w-4 h-4 bg-green-500 rounded-full ml-1" title="Verified Seller">
        <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
        </svg>
    </span>
);

const ProductCard = ({ product, variant, onOpenModal, onAddToCart, onCommit }) => {
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    // Helper to safely get images
    const getImages = () => {
        if (product.images && product.images.length > 0) return product.images;
        return [];
    };

    const images = getImages();
    const hasMultipleImages = images.length > 1;

    // Navigation for Carousel
    const nextImage = (e) => {
        e.stopPropagation();
        setCurrentImageIndex((prev) => (prev + 1) % images.length);
    };

    const prevImage = (e) => {
        e.stopPropagation();
        setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length);
    };

    // Click Handler - Default to Open Modal
    const handleClick = () => onOpenModal(product);

    // Communit Progress Calculation (Mock logic if fields missing)
    const getProgress = () => {
        const target = product.target_quantity || 1000;
        const committed = product.committed_quantity || 0;
        const percent = Math.min((committed / target) * 100, 100);
        return { committed, target, percent };
    };

    const progress = getProgress();

    return (
        <div
            className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow flex flex-col min-h-0 cursor-pointer group"
            onClick={handleClick}
        >
            {/* Image Carousel Area */}
            <div className="relative h-48 sm:h-56 bg-gray-100 rounded-t-lg overflow-hidden">
                {images.length > 0 ? (
                    <img
                        src={images[currentImageIndex]}
                        alt={product.title || product.product_name}
                        className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                        <span className="text-3xl">📦</span>
                    </div>
                )}

                {/* Carousel Controls */}
                {hasMultipleImages && (
                    <>
                        <button
                            onClick={prevImage}
                            className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full p-1 hover:bg-opacity-75 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            ←
                        </button>
                        <button
                            onClick={nextImage}
                            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full p-1 hover:bg-opacity-75 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            →
                        </button>
                        {/* Dots */}
                        <div className="absolute bottom-2 left-0 right-0 flex justify-center space-x-1">
                            {images.map((_, idx) => (
                                <div
                                    key={idx}
                                    className={`w-1.5 h-1.5 rounded-full ${idx === currentImageIndex ? 'bg-white' : 'bg-white bg-opacity-50'}`}
                                />
                            ))}
                        </div>
                    </>
                )}

                {/* Badges */}
                {variant === 'wholesale' && (
                    <div className="absolute top-2 left-2 bg-orange-600 text-white px-2 py-1 rounded text-xs font-bold">
                        FARM DEAL
                    </div>
                )}
                {variant === 'community' && (
                    <div className="absolute top-2 left-2 bg-purple-600 text-white px-2 py-1 rounded text-xs font-bold">
                        COMMUNITY
                    </div>
                )}
                {product.discount_value && (
                    <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded text-xs font-bold animate-pulse">
                        DATA SAVE
                    </div>
                )}
            </div>

            {/* Content Area */}
            <div className="p-3 flex-1 flex flex-col">
                {/* Title & Price */}
                <div className="flex justify-between items-start mb-2">
                    <div>
                        <h3 className="font-bold text-gray-900 line-clamp-1" title={product.title || product.product_name}>
                            {product.title || product.product_name}
                        </h3>
                        {variant === 'retail' && product.brand_name && (
                            <p className="text-xs text-gray-500 flex items-center">
                                {product.brand_name}
                                {product.seller_is_verified && <VerifiedBadge />}
                            </p>
                        )}
                    </div>
                    <div className="text-right">
                        <span className="font-bold text-emerald-600 block">
                            ₦{product.price_per_unit || product.price}
                        </span>
                        <span className="text-xs text-gray-500">
                            /{product.unit || product.unit_of_measure}
                        </span>
                    </div>
                </div>

                {/* Description Glimpse */}
                <p className="text-xs text-gray-600 line-clamp-2 mb-3 h-8">
                    {product.description || 'No description available'}
                </p>

                {/* Pre-Order Timer */}
                {product.is_preorder && (
                    <div className="mb-2">
                        <PreOrderTimer
                            availableDate={product.preorder_available_date}
                            endDate={product.preorder_end_date}
                        />
                        {product.preorder_target_quantity && (
                            <div className="mt-2">
                                <div className="flex justify-between text-[10px] text-gray-500 mb-1">
                                    <span>{product.quantity_available} left</span>
                                    <span>Goal: {product.preorder_target_quantity}</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-1.5">
                                    <div
                                        className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500"
                                        style={{ width: `${Math.min(100, Math.max(0, (product.quantity_available / product.preorder_target_quantity) * 100))}%` }}
                                    ></div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Variant Specific Info */}
                <div className="mt-auto space-y-2">

                    {/* Retail Info */}
                    {variant === 'retail' && (
                        <div className="text-xs text-gray-500 space-y-1">
                            <div className="flex items-center gap-1">
                                <span>📦 Min Order:</span>
                                <span className="font-medium text-gray-900">{product.minimum_order_quantity || 1} {product.unit}</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <span>🏷️ Expiry:</span>
                                <span className="font-medium text-gray-900">
                                    {product.expiry_date ? new Date(product.expiry_date).toLocaleDateString() : 'N/A'}
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Wholesale Info */}
                    {variant === 'wholesale' && (
                        <div className="bg-orange-50 p-2 rounded text-xs space-y-1 border border-orange-100">
                            <div className="flex justify-between">
                                <span className="text-orange-800">Available:</span>
                                <span className="font-bold text-orange-900">{product.quantity_available} {product.unit}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-orange-800">Harvest:</span>
                                <span className="font-bold text-orange-900">
                                    {product.best_before ? new Date(product.best_before).toLocaleDateString() : 'Fresh'}
                                </span>
                            </div>
                            {product.agent_name && (
                                <div
                                    className="pt-1 mt-1 border-t border-orange-200 text-blue-600 font-medium cursor-pointer flex items-center gap-1 hover:underline"
                                    onClick={(e) => { e.stopPropagation(); onOpenModal(product); }}
                                >
                                    <span>🤝 {product.agent_name}</span>
                                    {product.seller_is_verified && <VerifiedBadge />}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Community Info */}
                    {variant === 'community' && (
                        <div className="space-y-2">
                            <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                                <div
                                    className="bg-purple-600 h-full transition-all duration-500"
                                    style={{ width: `${progress.percent}%` }}
                                />
                            </div>
                            <div className="flex justify-between text-xs text-purple-700 font-medium">
                                <span>{progress.committed} committed</span>
                                <span>{progress.target} goal</span>
                            </div>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="pt-2 grid grid-cols-2 gap-2">
                        <button
                            onClick={(e) => { e.stopPropagation(); onOpenModal(product); }}
                            className="px-3 py-1.5 text-xs font-bold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                        >
                            More Info
                        </button>

                        {variant === 'community' ? (
                            <button
                                onClick={(e) => { e.stopPropagation(); onCommit(product); }}
                                className="px-3 py-1.5 text-xs font-bold text-white bg-purple-600 hover:bg-purple-700 rounded transition-colors shadow-sm"
                            >
                                Commit
                            </button>
                        ) : (
                            <button
                                onClick={(e) => { e.stopPropagation(); onAddToCart(product); }}
                                className="px-3 py-1.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded transition-colors shadow-sm"
                            >
                                Add Cart
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProductCard;
