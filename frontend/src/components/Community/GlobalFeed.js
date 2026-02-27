import React, { useEffect, useState } from 'react';

const GlobalFeed = ({ API_BASE_URL, onOpenProduct, onJoinCommunity }) => {
    const [feedItems, setFeedItems] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchGlobalFeed = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/communities/global-feed`, {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setFeedItems(data);
                }
            } catch (error) {
                console.error("Failed to fetch global feed", error);
            } finally {
                setLoading(false);
            }
        };

        fetchGlobalFeed();
    }, [API_BASE_URL]);

    if (loading) return <div className="p-4 text-center text-gray-400">Loading feeds...</div>;

    if (feedItems.length === 0) return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <h3 className="text-xl font-bold text-gray-900 mb-2">No activity yet.</h3>
            <p className="text-gray-500">Join a community or check back later!</p>
        </div>
    );

    return (
        <div className="space-y-4 pb-10">
            {feedItems.map((item, index) => (
                <div key={`${item.feed_type}-${item.id || index}`} className="bg-white p-5 rounded-lg shadow-sm border border-gray-100 transition duration-200 hover:shadow-md">
                    <div className="flex justify-between mb-3 items-center">
                        <div className="flex items-center gap-2">
                            <span className="font-semibold text-gray-900">{item.author || item.seller_name || 'Anonymous'}</span>
                            <span className="text-sm text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">in {item.community_name || 'Community'}</span>
                        </div>
                        <span className="text-xs text-gray-400">{item.date}</span>
                    </div>

                    {item.feed_type === 'post' ? (
                        <>
                            <p className="text-gray-700 whitespace-pre-wrap mb-4 text-sm leading-relaxed">{item.content}</p>

                            {/* Engagement Buttons with SVGs */}
                            <div className="flex items-center gap-6 pt-3 border-t border-gray-50">
                                <button className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-red-500 transition-colors group">
                                    <svg className="w-5 h-5 group-hover:fill-current group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                    </svg>
                                    <span>{item.likes_count || 0}</span>
                                </button>

                                <button className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-500 transition-colors group">
                                    <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                    </svg>
                                    <span>{item.comments_count || 0}</span>
                                </button>

                                <button className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-green-500 transition-colors group">
                                    <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                                    </svg>
                                    <span>Share</span>
                                </button>
                            </div>
                        </>
                    ) : (
                        <div className="flex flex-col gap-3">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h4 className="font-bold text-gray-900 group-hover:text-emerald-600 transition-colors">{item.title}</h4>
                                    <p className="text-sm text-emerald-600 font-bold mt-1">₦{item.price_per_unit} / {item.unit_of_measure}</p>
                                </div>
                                <span className="bg-emerald-50 text-emerald-700 text-xs px-2 py-1 rounded font-medium border border-emerald-100">
                                    Selling
                                </span>
                            </div>
                            <p className="text-sm text-gray-600 line-clamp-2">{item.description}</p>

                            <div className="flex items-center gap-3 pt-3 border-t border-gray-50">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        if (onOpenProduct) onOpenProduct(item);
                                    }}
                                    className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700 font-medium transition-colors shadow-sm"
                                >
                                    View Product
                                </button>

                                <button className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-500 transition-colors group ml-4">
                                    <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                    </svg>
                                    <span>{item.comments_count || 0}</span>
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
};

export default GlobalFeed;
