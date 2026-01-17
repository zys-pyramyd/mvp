
import React, { useEffect, useState } from 'react';

const CommunityFeed = ({ community, onBack }) => {
    const [activeTab, setActiveTab] = useState('feed'); // 'feed' | 'products'
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showPostModal, setShowPostModal] = useState(false);
    const [newPostContent, setNewPostContent] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

    const fetchItems = async () => {
        setLoading(true);
        try {
            const endpoint = activeTab === 'feed'
                ? `${API_BASE_URL}/api/communities/${community.id}/posts`
                : `${API_BASE_URL}/api/communities/${community.id}/products`;

            const token = localStorage.getItem('token');
            const response = await fetch(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setItems(data);
            }
            setLoading(false);

        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems();
    }, [activeTab, community]);

    const handleCreatePost = async (e) => {
        e.preventDefault();
        if (!newPostContent.trim()) return;

        setSubmitting(true);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/api/communities/${community.id}/posts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ content: newPostContent })
            });

            if (response.ok) {
                setNewPostContent('');
                setShowPostModal(false);
                fetchItems(); // Refresh feed
            } else {
                const err = await response.json();
                alert(err.detail || "Failed to post");
            }
        } catch (error) {
            alert("Error creating post");
        } finally {
            setSubmitting(false);
        }
    };

    const handleLikePost = async (postId) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/api/communities/posts/${postId}/like`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const result = await response.json();
                setItems(items.map(item =>
                    item.id === postId
                        ? { ...item, user_liked: result.liked, likes_count: result.liked ? (item.likes_count || 0) + 1 : Math.max((item.likes_count || 0) - 1, 0) }
                        : item
                ));
            }
        } catch (error) {
            console.error('Like failed:', error);
        }
    };

    const handleShowComments = async (postId) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/api/communities/posts/${postId}/comments`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const comments = await response.json();
                if (comments.length === 0) {
                    alert('No comments yet. Be the first to comment!');
                } else {
                    const commentsText = comments.map(c => `${c.username}: ${c.content}`).join('\n\n');
                    alert(`Comments:\n\n${commentsText}`);
                }
            }
        } catch (error) {
            console.error('Failed to fetch comments:', error);
        }
    };

    const handleSharePost = async (postId) => {
        const shareText = `Check out this post in ${community.name}!`;
        if (navigator.share) {
            try {
                await navigator.share({ title: community.name, text: shareText, url: window.location.href });
            } catch (error) {
                console.log('Share cancelled');
            }
        } else {
            alert('Share feature: Post link copied!');
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full flex flex-col relative">
            {/* Header */}
            <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-emerald-50">
                <div className="flex items-center gap-3">
                    <button onClick={onBack} className="text-gray-500 hover:text-gray-700">← Back</button>
                    <div>
                        <h2 className="text-xl font-bold text-gray-900">{community.name}</h2>
                        <p className="text-sm text-gray-600">{community.category} • {community.members_count || 0} Members</p>
                    </div>
                </div>
                <button
                    onClick={() => setShowPostModal(true)}
                    className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 text-sm font-medium"
                >
                    + New Post
                </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-200">
                <button
                    className={`flex-1 py-3 text-sm font-medium ${activeTab === 'feed' ? 'border-b-2 border-emerald-500 text-emerald-600' : 'text-gray-500'}`}
                    onClick={() => setActiveTab('feed')}
                >
                    Community Feed
                </button>
                <button
                    className={`flex-1 py-3 text-sm font-medium ${activeTab === 'products' ? 'border-b-2 border-emerald-500 text-emerald-600' : 'text-gray-500'}`}
                    onClick={() => setActiveTab('products')}
                >
                    Marketplace
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                {loading ? (
                    <div className="text-center py-8 text-gray-400">Loading...</div>
                ) : (
                    <div className="space-y-4">
                        {items.length === 0 && <p className="text-center text-gray-400">No content yet. Be the first to post!</p>}

                        {activeTab === 'feed' && items.map(post => (
                            <div key={post.id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
                                <div className="flex justify-between mb-2">
                                    <span className="font-semibold text-gray-900">{post.author}</span>
                                    <span className="text-xs text-gray-400">{post.date}</span>
                                </div>
                                <p className="text-gray-700 whitespace-pre-wrap mb-3">{post.content}</p>

                                {/* Engagement Buttons */}
                                <div className="flex items-center gap-4 pt-3 border-t border-gray-100">
                                    <button
                                        onClick={() => handleLikePost(post.id)}
                                        className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-red-600 transition-colors"
                                    >
                                        <span className={post.user_liked ? "text-red-600" : ""}>
                                            {post.user_liked ? "❤️" : "🤍"}
                                        </span>
                                        <span>{post.likes_count || 0}</span>
                                    </button>

                                    <button
                                        onClick={() => handleShowComments(post.id)}
                                        className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-blue-600 transition-colors"
                                    >
                                        <span>💬</span>
                                        <span>{post.comments_count || 0}</span>
                                    </button>

                                    <button
                                        onClick={() => handleSharePost(post.id)}
                                        className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-green-600 transition-colors"
                                    >
                                        <span>🔗</span>
                                        <span>Share</span>
                                    </button>
                                </div>
                            </div>
                        ))}

                        {activeTab === 'products' && items.map(product => (
                            <div key={product.id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex justify-between items-center">
                                <div>
                                    <h4 className="font-medium">{product.name}</h4>
                                    <p className="text-sm text-emerald-600 font-bold">₦{product.price} / {product.unit}</p>
                                </div>
                                <button className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded text-sm hover:bg-emerald-200">
                                    View
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Create Post Modal */}
            {showPostModal && (
                <div className="absolute inset-0 bg-black/50 z-50 flex items-center justify-center p-4 rounded-lg">
                    <div className="bg-white rounded-xl shadow-lg w-full max-w-lg overflow-hidden">
                        <div className="p-4 border-b border-gray-100 flex justify-between items-center">
                            <h3 className="font-bold text-gray-900">Create Post</h3>
                            <button
                                onClick={() => setShowPostModal(false)}
                                className="text-gray-400 hover:text-gray-600 text-xl"
                            >
                                &times;
                            </button>
                        </div>
                        <form onSubmit={handleCreatePost} className="p-4">
                            <textarea
                                value={newPostContent}
                                onChange={(e) => setNewPostContent(e.target.value)}
                                placeholder="Share something with the community..."
                                className="w-full h-32 p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none text-sm"
                                autoFocus
                            />
                            <div className="flex justify-end gap-2 mt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowPostModal(false)}
                                    className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm font-medium"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={!newPostContent.trim() || submitting}
                                    className={`px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium transition-colors ${(!newPostContent.trim() || submitting)
                                        ? 'opacity-50 cursor-not-allowed'
                                        : 'hover:bg-emerald-700'
                                        }`}
                                >
                                    {submitting ? 'Posting...' : 'Post'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CommunityFeed;
