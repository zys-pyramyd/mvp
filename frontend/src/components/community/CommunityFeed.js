
import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import CommunityProductModal from './CommunityProductModal';
import ProductCommentsModal from '../product/ProductCommentsModal';

const CommunityFeed = ({ community, onBack, onOpenProduct }) => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('feed'); // 'feed' | 'products'
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showPostModal, setShowPostModal] = useState(false);
    const [showProductModal, setShowProductModal] = useState(false);
    const [newPostContent, setNewPostContent] = useState('');
    const [activeCommentProduct, setActiveCommentProduct] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    // Mention States
    const [mentionQuery, setMentionQuery] = useState(null);
    const [mentionResults, setMentionResults] = useState([]);

    // Handle @ input
    const handleMentionSearch = async (text) => {
        const lastWord = text.split(' ').pop();
        if (lastWord.startsWith('@') && lastWord.length > 1) {
            const query = lastWord.substring(1);
            setMentionQuery(query);
            // Search logic (could be local members filter or API)
            // Ideally filter from fetched members if available, or call search API
            // For now, let's call the search API
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`${API_BASE_URL}/api/users/search?q=${query}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    setMentionResults(await response.json());
                }
            } catch (err) { console.error(err); }
        } else {
            setMentionQuery(null);
            setMentionResults([]);
        }
    };

    const insertMention = (username) => {
        const words = newPostContent.split(' ');
        words.pop(); // Remove the partial @mention
        words.push(`@${username} `);
        setNewPostContent(words.join(' '));
        setMentionQuery(null);
        setMentionResults([]);
    };

    const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

    const fetchItems = async () => {
        setLoading(true);
        try {
            const endpoint = activeTab === 'feed'
                ? `${API_BASE_URL}/api/communities/${community.id}/posts`
                : activeTab === 'products'
                    ? `${API_BASE_URL}/api/communities/${community.id}/products`
                    : `${API_BASE_URL}/api/communities/${community.id}/members`;

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

    const handleLeaveCommunity = async () => {
        if (!window.confirm("Are you sure you want to leave this community?")) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/api/communities/${community.id}/leave`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                alert("You have left the community.");
                onBack(); // Go back to my communities
            } else {
                alert("Failed to leave community.");
            }
        } catch (error) {
            console.error(error);
        }
    };

    const handleDeleteCommunity = async () => {
        if (!window.confirm("ARE YOU SURE? This will permanently delete the community and all its content.")) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/api/communities/${community.id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                alert("Community deleted.");
                onBack(); // Go back to my communities
            } else {
                alert("Failed to delete community.");
            }
        } catch (error) {
            console.error(error);
            alert("Error deleting community");
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
                <div className="flex gap-2 items-center">
                    {/* Only Admins/Creators can see the Sell Item button */}
                    {activeTab === 'products' && (community.creator_id === user?.id || community.user_role === 'admin') && (
                        <button
                            onClick={() => setShowProductModal(true)}
                            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 text-sm font-medium"
                        >
                            + Sell Item
                        </button>
                    )}
                    {/* Only Admins/Creators can see the New Post button */}
                    {activeTab === 'feed' && (community.creator_id === user?.id || community.user_role === 'admin') && (
                        <button
                            onClick={() => setShowPostModal(true)}
                            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 text-sm font-medium"
                        >
                            + New Post
                        </button>
                    )}

                    {/* Settings / Actions Dropdown could be better, but simple buttons for now */}
                    <button onClick={handleLeaveCommunity} className="text-red-600 hover:text-red-800 text-sm font-medium px-2">
                        Leave
                    </button>
                    {community.creator_id === user?.id && (
                        <button onClick={handleDeleteCommunity} className="text-red-600 hover:text-red-800 text-sm font-medium px-2 border-l border-gray-300">
                            Delete
                        </button>
                    )}
                </div>
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
                <button
                    className={`flex-1 py-3 text-sm font-medium ${activeTab === 'members' ? 'border-b-2 border-emerald-500 text-emerald-600' : 'text-gray-500'}`}
                    onClick={() => setActiveTab('members')}
                >
                    Members
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                {loading ? (
                    <div className="text-center py-8 text-gray-400">Loading...</div>
                ) : (
                    <div className="space-y-4">
                        {items.length === 0 && <p className="text-center text-gray-400">No content found.</p>}

                        {/* FEED TAB */}
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

                        {/* PRODUCTS TAB */}
                        {activeTab === 'products' && items.map(product => (
                            <div key={product.id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex justify-between items-center cursor-pointer hover:bg-gray-50" onClick={() => onOpenProduct && onOpenProduct(product)}>
                                <div>
                                    <h4 className="font-medium">{product.name || product.title}</h4>
                                    <p className="text-sm text-emerald-600 font-bold">₦{product.price || product.price_per_unit} / {product.unit || product.unit_of_measure}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            if (onOpenProduct) onOpenProduct(product);
                                        }}
                                        className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded text-sm hover:bg-emerald-200"
                                    >
                                        View
                                    </button>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setActiveCommentProduct(product);
                                        }}
                                        className="ml-2 px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200"
                                    >
                                        💬 {product.comments_count || 0}
                                    </button>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            const shareData = { title: product.name, text: `Check out ${product.name} in ${community.name}`, url: window.location.href };
                                            if (navigator.share) navigator.share(shareData);
                                            else { navigator.clipboard.writeText(window.location.href); alert('Link copied!'); }
                                        }}
                                        className="ml-2 px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        ))}

                        {/* MEMBERS TAB */}
                        {activeTab === 'members' && (
                            <MembersTab
                                community={community}
                                items={items}
                                onRefresh={fetchItems}
                                user={user}
                                API_BASE_URL={API_BASE_URL}
                            />
                        )}
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
                        <form onSubmit={handleCreatePost} className="p-4 relative">
                            <textarea
                                value={newPostContent}
                                onChange={(e) => {
                                    setNewPostContent(e.target.value);
                                    handleMentionSearch(e.target.value);
                                }}
                                placeholder="Share something with the community... Use @ to mention members."
                                className="w-full h-32 p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none text-sm"
                                autoFocus
                            />

                            {/* Suggestion Dropdown */}
                            {mentionQuery && mentionResults.length > 0 && (
                                <div className="absolute left-4 top-20 bg-white border border-gray-200 shadow-lg rounded-lg max-h-40 overflow-y-auto w-64 z-50">
                                    {mentionResults.map(user => (
                                        <button
                                            key={user.id}
                                            type="button"
                                            onClick={() => insertMention(user.username)}
                                            className="w-full text-left px-3 py-2 hover:bg-gray-50 flex items-center gap-2 text-sm"
                                        >
                                            <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-xs overflow-hidden">
                                                {user.profile_picture ? <img src={user.profile_picture} alt="" className="w-full h-full object-cover" /> : user.username[0].toUpperCase()}
                                            </div>
                                            <span>@{user.username}</span>
                                        </button>
                                    ))}
                                </div>
                            )}

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

            {/* Create Product Modal */}
            {showProductModal && (
                <CommunityProductModal
                    community={community}
                    onClose={() => setShowProductModal(false)}
                    onSuccess={() => {
                        setShowProductModal(false);
                        fetchItems(); // Refresh list
                    }}
                />
            )}
            {/* Product Comments Modal */}
            {activeCommentProduct && (
                <ProductCommentsModal
                    product={activeCommentProduct}
                    onClose={() => setActiveCommentProduct(null)}
                />
            )}
        </div>
    );
};

// Subcomponent for Members Tab to keep code clean
const MembersTab = ({ community, items, onRefresh, user, API_BASE_URL }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [adding, setAdding] = useState(false);

    // items passed here are members when activeTab is 'members'

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        try {
            const token = localStorage.getItem('token');
            // assuming users.py updated for search
            const response = await fetch(`${API_BASE_URL}/api/users/search?q=${searchQuery}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                setSearchResults(await response.json());
            }
        } catch (error) {
            console.error(error);
        }
    };

    const handleAddMember = async (targetUserId) => {
        setAdding(true);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/api/communities/${community.id}/members`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ user_id: targetUserId })
            });
            if (response.ok) {
                alert("Member added!");
                setSearchResults([]);
                setSearchQuery('');
                onRefresh();
            } else {
                const err = await response.json();
                alert(err.detail || "Failed to add member");
            }
        } catch (error) {
            alert("Error adding member");
        } finally {
            setAdding(false);
        }
    };

    const handleRoleToggle = async (memberUserId, currentRole) => {
        // Toggle Logic: Admin <-> Member. Only Admins can do this.
        const newRole = currentRole === 'admin' ? 'member' : 'admin';
        if (!window.confirm(`Change role to ${newRole}?`)) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/api/communities/${community.id}/members/${memberUserId}/role`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ role: newRole })
            });
            if (response.ok) {
                onRefresh();
            } else {
                alert("Failed to update role");
            }
        } catch (error) {
            console.error(error);
        }
    };

    const isAdmin = community.creator_id === user?.id || community.user_role === 'admin';

    return (
        <div className="space-y-6">
            {/* Add Member Section (Admin Only) */}
            {isAdmin && (
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <h4 className="text-sm font-bold text-gray-700 mb-2">Add New Member</h4>
                    <form onSubmit={handleSearch} className="flex gap-2 mb-2">
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search by name or username..."
                            className="flex-1 p-2 border border-gray-300 rounded text-sm"
                        />
                        <button type="submit" className="px-3 py-2 bg-emerald-600 text-white rounded text-sm">Search</button>
                    </form>

                    {searchResults.length > 0 && (
                        <div className="bg-white border border-gray-200 rounded mt-2 max-h-40 overflow-y-auto">
                            {searchResults.map(res => (
                                <div key={res.id} className="p-2 flex justify-between items-center hover:bg-gray-50 border-b border-gray-100 last:border-0">
                                    <div className="flex items-center gap-2">
                                        <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-xs overflow-hidden">
                                            {res.profile_picture ? <img src={res.profile_picture} alt="" className="w-full h-full object-cover" /> : res.username[0].toUpperCase()}
                                        </div>
                                        <span className="text-sm font-medium">{res.first_name} {res.last_name} (@{res.username})</span>
                                    </div>
                                    <button
                                        onClick={() => handleAddMember(res.id)}
                                        disabled={adding}
                                        className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded hover:bg-emerald-200"
                                    >
                                        Add
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Members List */}
            <div className="space-y-2">
                <h4 className="text-sm font-bold text-gray-700">Community Members ({items.length})</h4>
                {items.map(member => (
                    <div key={member.user_id} className="flex items-center justify-between p-3 bg-white border border-gray-100 rounded-lg shadow-sm">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center text-gray-500 font-bold text-lg overflow-hidden">
                                {member.profile_picture ? (
                                    <img src={member.profile_picture} alt={member.username} className="w-full h-full object-cover" />
                                ) : (
                                    (member.username || '?')[0].toUpperCase()
                                )}
                            </div>
                            <div>
                                <p className="font-medium text-gray-900">{member.first_name} {member.last_name}</p>
                                <p className="text-xs text-gray-500">@{member.username}</p>
                            </div>
                        </div>

                        {/* Role Badge (Clickable for Admin) */}
                        <div className="flex items-center gap-2">
                            {isAdmin && member.user_id !== user.id ? (
                                <button
                                    onClick={() => handleRoleToggle(member.user_id, member.role)}
                                    className={`px-3 py-1 rounded-full text-xs font-medium border ${member.role === 'admin'
                                        ? 'bg-purple-100 text-purple-700 border-purple-200 hover:bg-purple-200'
                                        : 'bg-gray-100 text-gray-600 border-gray-200 hover:bg-gray-200'
                                        }`}
                                    title="Click to toggle role"
                                >
                                    {member.role === 'admin' ? 'Admin 🛡️' : 'Member'}
                                </button>
                            ) : (
                                <span className={`px-3 py-1 rounded-full text-xs font-medium ${member.role === 'admin'
                                    ? 'bg-purple-100 text-purple-700'
                                    : 'bg-gray-100 text-gray-600'
                                    }`}>
                                    {member.role === 'admin' ? 'Admin 🛡️' : 'Member'}
                                </span>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CommunityFeed;
