import React, { useEffect, useState } from 'react';

const TrendingProducts = ({ API_BASE_URL, onOpenProduct }) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTrending = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/communities/trending-products?limit=5`, {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setProducts(data);
                }
            } catch (error) {
                console.error("Failed to fetch trending products", error);
            } finally {
                setLoading(false);
            }
        };

        fetchTrending();
    }, [API_BASE_URL]);

    if (loading) return <div className="p-4 text-center text-gray-400 text-xs">Loading trending...</div>;

    if (products.length === 0) return null;

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sticky top-4">
            <h3 className="font-bold text-gray-900 mb-4 text-sm flex items-center gap-2">
                <svg className="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                High Commits
            </h3>
            <div className="space-y-4">
                {products.map((product, idx) => (
                    <div key={product.id}
                        onClick={() => onOpenProduct && onOpenProduct(product)}
                        className="flex flex-col gap-1 border-b border-gray-100 pb-3 last:border-0 last:pb-0 cursor-pointer group hover:bg-gray-50 p-2 -mx-2 rounded transition-colors"
                    >
                        <div className="flex justify-between items-start">
                            <h4 className="font-semibold text-sm text-gray-800 group-hover:text-emerald-600 transition-colors line-clamp-1">
                                {idx + 1}. {product.title}
                            </h4>
                        </div>
                        <p className="text-xs font-bold text-emerald-600">₦{product.price_per_unit} / {product.unit_of_measure}</p>

                        <div className="flex justify-between items-center mt-2">
                            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full line-clamp-1 max-w-[120px]">
                                {product.community_name || 'Community'}
                            </span>
                            <span className="text-xs font-medium text-orange-600 bg-orange-50 px-2 py-0.5 rounded flex items-center gap-1 border border-orange-100">
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                                {product.quantity_available || 0} req
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TrendingProducts;
