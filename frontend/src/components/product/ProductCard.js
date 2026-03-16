import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingCart } from 'lucide-react';
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
    const navigate = useNavigate();

    // Helper to safely get images
    const getImages = () => {
        if (product.images && product.images.length > 0) return product.images;
        return [];
    };

    const images = getImages();
    const hasMultipleImages = images.length > 1;

    // Navigation for Carousel - kept for potential future use
    // but controls are hidden since clicking goes to product page

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
        <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow flex flex-col min-h-0 group">
            {/* Image Carousel Area */}
            <div
                className="relative h-48 sm:h-56 bg-gray-100 rounded-t-lg overflow-hidden cursor-pointer"
                onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/product/${product.id || product._id}`);
                }}
            >
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

                {/* Dot indicators if multiple images */}
                {hasMultipleImages && (
                    <div className="absolute bottom-2 left-0 right-0 flex justify-center space-x-1">
                        {images.map((_, idx) => (
                            <div
                                key={idx}
                                className={`w-1.5 h-1.5 rounded-full ${idx === currentImageIndex ? 'bg-white' : 'bg-white bg-opacity-50'}`}
                            />
                        ))}
                    </div>
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
                        <h3 
                            className="font-bold text-gray-800 text-sm sm:text-base line-clamp-1 truncate hover:text-emerald-600 transition-colors cursor-pointer"
                            title={product.title || product.product_name}
                            onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/product/${product.id || product._id}`);
                            }}
                        >
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

                {/* Share Button (Absolute Top Right for easy access) */}
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        const shareData = {
                            title: product.title || product.product_name,
                            text: `Check out ${product.title || product.product_name} on FarmHub!`,
                            url: window.location.href // Ideally this would be a specific product link
                        };
                        if (navigator.share) {
                            navigator.share(shareData).catch(console.error);
                        } else {
                            navigator.clipboard.writeText(window.location.href);
                            alert('Link copied to clipboard!');
                        }
                    }}
                    className="absolute top-2 right-12 bg-white/80 hover:bg-white text-gray-700 p-1.5 rounded-full shadow-sm z-10 transition-colors"
                    title="Share Product"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                    </svg>
                </button>

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

                {/* Action Buttons */}
                <div className="mt-auto pt-3 flex gap-2 w-full">
                    {variant === 'community' ? (
                        <button
                            onClick={(e) => { e.stopPropagation(); onCommit(product); }}
                            className="w-full px-3 py-2 text-sm font-bold text-white bg-purple-600 hover:bg-purple-700 rounded transition-colors shadow-sm"
                        >
                            Commit to Buy
                        </button>
                    ) : (
                        <>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    // Trigger buy now - typically routes to checkout
                                    if (product.id || product._id) {
                                        navigate(`/checkout?product=${product.id || product._id}&buyNow=true`);
                                    }
                                }}
                                className="w-[80%] px-3 py-2 text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded transition-colors shadow-sm text-center"
                            >
                                Buy Now
                            </button>
                            <button
                                onClick={(e) => { 
                                    e.stopPropagation(); 
                                    onAddToCart(product); 
                                }}
                                className="w-[20%] flex items-center justify-center p-2 text-emerald-600 bg-emerald-50 hover:bg-emerald-100 rounded transition-colors shadow-sm border border-emerald-100"
                                title="Add to Cart"
                            >
                                <ShoppingCart size={20} />
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ProductCard;
