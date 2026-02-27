import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../common/Header';
import ProductCard from './ProductCard';

const ProductPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [product, setProduct] = useState(null);
    const [similarProducts, setSimilarProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    const API_URL = process.env.REACT_APP_BACKEND_URL;

    useEffect(() => {
        const fetchProductData = async () => {
            setLoading(true);
            setError(null);
            try {
                // 1. Fetch Product Details
                const response = await fetch(`${API_URL}/api/products/${id}`);
                if (!response.ok) {
                    if (response.status === 404) throw new Error("Product not found");
                    throw new Error("Failed to fetch product");
                }
                const data = await response.json();
                setProduct(data);

                // 2. Fetch Similar Products (based on category)
                if (data.category) {
                    const simResponse = await fetch(`${API_URL}/api/products?category=${data.category}&limit=5`);
                    if (simResponse.ok) {
                        const simData = await simResponse.json();
                        // Filter out the current product itself
                        setSimilarProducts(simData.products.filter(p => p.id !== data.id));
                    }
                }
            } catch (err) {
                console.error(err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchProductData();
        }
    }, [id, API_URL]);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin h-10 w-10 border-4 border-emerald-500 border-t-transparent rounded-full"></div>
            </div>
        );
    }

    if (error || !product) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
                <Header title="Product Details" />
                <div className="bg-white p-8 rounded-xl shadow text-center max-w-md w-full mt-20">
                    <span className="text-5xl mb-4 block">🔍</span>
                    <h2 className="text-xl font-bold text-gray-800 mb-2">Product Not Found</h2>
                    <p className="text-gray-500 mb-6">{error || 'The product you are looking for does not exist or has been removed.'}</p>
                    <button
                        onClick={() => navigate(-1)}
                        className="bg-emerald-600 text-white px-6 py-2 rounded-lg hover:bg-emerald-700 w-full font-medium transition-colors"
                    >
                        Go Back
                    </button>
                </div>
            </div>
        );
    }

    const images = product.images?.length > 0 ? product.images : [];

    const handleShare = async () => {
        const shareData = {
            title: product.title || product.product_name,
            text: `Check out ${product.title || product.product_name} on FarmHub!`,
            url: window.location.href
        };
        try {
            if (navigator.share) {
                await navigator.share(shareData);
            } else {
                await navigator.clipboard.writeText(window.location.href);
                alert('Product link copied to clipboard!');
            }
        } catch (err) {
            console.error('Error sharing:', err);
        }
    };

    const formatLabel = (str) => {
        if (!str) return '';
        return str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    };

    return (
        <div className="min-h-screen bg-gray-50 pb-20">
            <Header title={product.title || "Product Details"} />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
                <button
                    onClick={() => navigate(-1)}
                    className="flex items-center text-gray-600 hover:text-emerald-700 mb-6 font-medium transition-colors"
                >
                    <span className="mr-2">←</span> Back
                </button>

                {/* Main Product Layout */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-12">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12 p-6 md:p-10">

                        {/* Left Column: Images */}
                        <div className="flex flex-col space-y-4">
                            <div className="relative aspect-square bg-gray-100 rounded-xl overflow-hidden border border-gray-100">
                                {images.length > 0 ? (
                                    <img
                                        src={images[currentImageIndex]}
                                        alt={product.title}
                                        className="w-full h-full object-contain bg-white"
                                    />
                                ) : (
                                    <div className="w-full h-full flex flex-col items-center justify-center text-gray-400">
                                        <span className="text-6xl mb-2">📦</span>
                                        <p>No Image Available</p>
                                    </div>
                                )}
                            </div>

                            {/* Thumbnail Gallery */}
                            {images.length > 1 && (
                                <div className="flex space-x-3 overflow-x-auto pb-2 scrollbar-hide">
                                    {images.map((img, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => setCurrentImageIndex(idx)}
                                            className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${idx === currentImageIndex ? 'border-emerald-500 opacity-100' : 'border-transparent opacity-60 hover:opacity-100'
                                                }`}
                                        >
                                            <img src={img} alt="" className="w-full h-full object-cover" />
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Right Column: Details */}
                        <div className="flex flex-col">
                            {/* Badges */}
                            <div className="flex flex-wrap gap-2 mb-4">
                                <span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-bold rounded-full border border-gray-200 uppercase tracking-wide">
                                    {formatLabel(product.category)}
                                </span>
                                {product.subcategory && (
                                    <span className="px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-bold rounded-full border border-emerald-100 uppercase tracking-wide">
                                        {formatLabel(product.subcategory)}
                                    </span>
                                )}
                                {product.processing_level && (
                                    <span className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-bold rounded-full border border-blue-100 uppercase tracking-wide">
                                        {formatLabel(product.processing_level)}
                                    </span>
                                )}
                            </div>

                            <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-2 leading-tight">
                                {product.title || product.product_name}
                            </h1>

                            <div className="flex items-center text-sm text-gray-500 mb-6">
                                <span className="flex items-center">
                                    <svg className="w-4 h-4 mr-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                                    </svg>
                                    {product.location}, Nigeria
                                </span>
                            </div>

                            {/* Price Block */}
                            <div className="bg-gray-50 rounded-xl p-5 mb-8 border border-gray-100">
                                <div className="flex items-end gap-2 mb-1">
                                    <span className="text-4xl font-black text-emerald-600">₦{product.price_per_unit?.toLocaleString()}</span>
                                    <span className="text-lg text-gray-500 font-medium pb-1">/ {product.unit_of_measure}</span>
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex gap-4 mb-10 pb-8 border-b border-gray-100">
                                <button
                                    onClick={() => navigate('/', { state: { openProduct: product } })}
                                    className="flex-1 bg-white border-2 border-emerald-600 text-emerald-700 px-6 py-4 rounded-xl font-bold text-lg hover:bg-emerald-50 transition-colors flex items-center justify-center"
                                >
                                    <span className="mr-2">🛒</span> Add to Cart
                                </button>
                                <button
                                    onClick={() => navigate('/', { state: { openProduct: product } })}
                                    className="flex-1 bg-emerald-600 text-white px-6 py-4 rounded-xl font-bold text-lg hover:bg-emerald-700 shadow-md hover:shadow-lg transition-all flex items-center justify-center transform hover:-translate-y-0.5"
                                >
                                    Buy Now
                                </button>
                                <button
                                    onClick={handleShare}
                                    className="p-4 bg-white border-2 border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-colors flex items-center justify-center group"
                                    title="Share Product"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-500 group-hover:text-emerald-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                                    </svg>
                                </button>
                            </div>

                            {/* Detailed Information Grid */}
                            <div className="grid grid-cols-2 gap-y-6 gap-x-8 mb-8">
                                <div>
                                    <div className="text-xs text-gray-500 uppercase font-bold tracking-wider mb-1">Available Quantity</div>
                                    <div className="font-semibold text-gray-900 text-lg">{product.quantity_available?.toLocaleString()} {product.unit_of_measure}s</div>
                                </div>
                                <div>
                                    <div className="text-xs text-gray-500 uppercase font-bold tracking-wider mb-1">Minimum Order</div>
                                    <div className="font-semibold text-gray-900 text-lg">{product.minimum_order_quantity?.toLocaleString() || 1} {product.unit_of_measure}s</div>
                                </div>
                                {product.agent_name && (
                                    <div>
                                        <div className="text-xs text-gray-500 uppercase font-bold tracking-wider mb-1">Listed By Agent</div>
                                        <div className="font-semibold text-emerald-700 flex items-center text-lg">
                                            {product.agent_name}
                                            {product.seller_is_verified && (
                                                <svg className="w-5 h-5 ml-1 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                </svg>
                                            )}
                                        </div>
                                    </div>
                                )}
                                {(product.best_before || product.expiry_date) && (
                                    <div>
                                        <div className="text-xs text-gray-500 uppercase font-bold tracking-wider mb-1">
                                            {product.best_before ? 'Harvest/Production Date' : 'Expiry Date'}
                                        </div>
                                        <div className="font-semibold text-orange-700 text-lg">
                                            {new Date(product.best_before || product.expiry_date).toLocaleDateString()}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Color Tags if any available */}
                            {product.colors && product.colors.length > 0 && (
                                <div className="mb-8">
                                    <div className="text-xs text-gray-500 uppercase font-bold tracking-wider mb-3">Available Colors</div>
                                    <div className="flex flex-wrap gap-2">
                                        {product.colors.map(c => (
                                            <span key={c} className="px-3 py-1 bg-gray-50 border rounded-lg text-sm font-medium text-gray-700 capitalize">
                                                {c}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Full Description */}
                            <div className="mt-2">
                                <h3 className="text-lg font-bold text-gray-900 mb-3 border-b border-gray-100 pb-2">Description</h3>
                                <div className="prose prose-emerald prose-sm sm:prose-base max-w-none text-gray-600 leading-relaxed whitespace-pre-wrap">
                                    {product.description || "No detailed description provided by the seller."}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Similar Products Section */}
                {similarProducts.length > 0 && (
                    <div className="mt-16 mb-8">
                        <div className="flex items-center justify-between mb-8">
                            <h2 className="text-2xl font-bold text-gray-900">Similar Products</h2>
                            <span className="text-emerald-600 font-medium text-sm hover:underline cursor-pointer">View more category</span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
                            {similarProducts.map((p) => (
                                <ProductCard
                                    key={p.id}
                                    product={p}
                                    variant={"retail"} // Mock variant
                                    onAddToCart={() => navigate('/', { state: { openProduct: p } })}
                                    onOpenModal={() => navigate(`/product/${p.id}`)}
                                    onCommit={() => { }}
                                />
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProductPage;
