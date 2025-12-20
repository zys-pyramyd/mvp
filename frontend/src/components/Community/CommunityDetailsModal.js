import React, { useState, useEffect } from 'react';
import { X, Heart, MessageCircle, Share2, Image as ImageIcon, ShoppingCart, Tag, MoreVertical, Trash2, Edit2, Check, AlertCircle } from 'lucide-react';

const CommunityDetailsModal = ({ community, onClose, user, token, API_BASE_URL, onUpload }) => {
    const [activeTab, setActiveTab] = useState('feed'); // 'feed' or 'marketplace'
    const [posts, setPosts] = useState([]);
    const [newPostContent, setNewPostContent] = useState('');
    const [selectedImages, setSelectedImages] = useState([]);
    const [previewUrls, setPreviewUrls] = useState([]);

    // Product Creation State
    const [isProductPost, setIsProductPost] = useState(false);
    const [productPrice, setProductPrice] = useState('');
    const [productName, setProductName] = useState('');

    // Edit State
    const [editingPost, setEditingPost] = useState(null); // The post object being edited
    const [editContent, setEditContent] = useState('');
    const [editPrice, setEditPrice] = useState('');
    const [editStatus, setEditStatus] = useState('available');

    const [loading, setLoading] = useState(false);
    const [expandedPostId, setExpandedPostId] = useState(null); // For comments section
    const [lightboxImage, setLightboxImage] = useState(null);

    // Comment State
    const [newComment, setNewComment] = useState('');
    const [editingCommentId, setEditingCommentId] = useState(null);
    const [editCommentContent, setEditCommentContent] = useState('');

    useEffect(() => {
        fetchPosts();
    }, [community, activeTab]);

    const fetchPosts = async () => {
        if (!community?.id) return;
        try {
            const typeParam = activeTab === 'marketplace' ? '?type=product' : '';
            const response = await fetch(`${API_BASE_URL}/api/communities/${community.id}/posts${typeParam}`);
            if (response.ok) {
                setPosts(await response.json());
            }
        } catch (error) {
            console.error("Failed to fetch posts", error);
        }
    };

    const handleCreatePost = async () => {
        if (!newPostContent && selectedImages.length === 0) return;
        setLoading(true);
        try {
            // Upload Images to R2
            const imageUrls = [];
            if (selectedImages.length > 0 && onUpload) {
                // Upload concurrently
                const uploadPromises = selectedImages.map(file => onUpload(file, 'social', 'public'));
                const results = await Promise.all(uploadPromises);
                results.forEach(url => {
                    if (url) imageUrls.push(url);
                });
            } else if (selectedImages.length > 0) {
                console.warn("Upload handler missing, skipping image upload");
            }

            const postData = {
                content: newPostContent,
                type: isProductPost ? 'product' : 'regular',
                images: imageUrls,
                product_name: isProductPost ? productName : null,
                product_price: isProductPost ? parseFloat(productPrice) : null,
                is_available: true
            };

            const response = await fetch(`${API_BASE_URL}/api/communities/${community.id}/posts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(postData)
            });

            if (response.ok) {
                setNewPostContent('');
                setSelectedImages([]);
                setPreviewUrls([]);
                setIsProductPost(false);
                setProductName('');
                setProductPrice('');
                fetchPosts();
            }
        } catch (error) {
            console.error("Error creating post", error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdatePost = async () => {
        if (!editingPost) return;
        try {
            const updateData = {
                content: editContent,
                ...(editingPost.type === 'product' && {
                    product_price: parseFloat(editPrice),
                    is_available: editStatus === 'available',
                    status: editStatus // Optional if backend supports specific string
                })
            };

            const response = await fetch(`${API_BASE_URL}/api/communities/posts/${editingPost.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(updateData)
            });

            if (response.ok) {
                setEditingPost(null);
                fetchPosts();
            }
        } catch (error) {
            console.error("Update failed", error);
        }
    };

    const handleDeletePost = async (postId) => {
        if (!window.confirm("Are you sure you want to delete this?")) return;
        try {
            await fetch(`${API_BASE_URL}/api/communities/posts/${postId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            fetchPosts();
        } catch (error) {
            console.error("Delete failed", error);
        }
    };

    const handleAddComment = async (postId) => {
        if (!newComment.trim()) return;
        try {
            const response = await fetch(`${API_BASE_URL}/api/communities/posts/${postId}/comments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ content: newComment })
            });
            if (response.ok) {
                setNewComment('');
                fetchPosts(); // Refresh to show new comment
            }
        } catch (error) {
            console.error("Comment failed", error);
        }
    };

    const handleEditComment = async (postId, commentId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/communities/comments/${postId}/${commentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ content: editCommentContent })
            });
            if (response.ok) {
                setEditingCommentId(null);
                fetchPosts();
            }
        } catch (error) {
            console.error("Edit comment failed", error);
        }
    };

    const getUserRole = () => user?.role || 'member';

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            {/* Lightbox */}
            {lightboxImage && (
                <div
                    className="fixed inset-0 z-[60] bg-black bg-opacity-90 flex items-center justify-center p-4 cursor-pointer"
                    onClick={() => setLightboxImage(null)}
                >
                    <img src={lightboxImage} alt="Fullscreen" className="max-w-full max-h-screen object-contain" />
                    <button className="absolute top-4 right-4 text-white hover:text-gray-300"><X size={32} /></button>
                </div>
            )}

            <div className="bg-white rounded-xl max-w-4xl w-full h-[90vh] flex flex-col relative shadow-2xl overflow-hidden">
                {/* Header */}
                <div className="p-4 border-b flex justify-between items-center bg-white z-10">
                    <div>
                        <h2 className="text-xl font-bold">{community.name}</h2>
                        <p className="text-sm text-gray-500">{community.members?.length || 0} members</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full"><X size={20} /></button>
                </div>

                {/* Tabs */}
                <div className="flex border-b bg-gray-50">
                    <button
                        className={`flex-1 py-3 font-medium text-sm ${activeTab === 'feed' ? 'border-b-2 border-emerald-600 text-emerald-700 bg-white' : 'text-gray-500'}`}
                        onClick={() => setActiveTab('feed')}
                    >
                        Feed
                    </button>
                    <button
                        className={`flex-1 py-3 font-medium text-sm flex items-center justify-center gap-2 ${activeTab === 'marketplace' ? 'border-b-2 border-emerald-600 text-emerald-700 bg-white' : 'text-gray-500'}`}
                        onClick={() => setActiveTab('marketplace')}
                    >
                        <ShoppingCart size={16} /> Marketplace
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto bg-gray-50">
                    <div className="max-w-2xl mx-auto py-6 space-y-6">

                        {/* Create Post (Only show if not editing) */}
                        {!editingPost && (
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                <textarea
                                    className="w-full p-3 bg-gray-50 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500 resize-none"
                                    rows="3"
                                    placeholder={activeTab === 'marketplace' ? "What are you selling?" : "Share something..."}
                                    value={newPostContent}
                                    onChange={(e) => setNewPostContent(e.target.value)}
                                />

                                {/* Product Fields */}
                                {(isProductPost || activeTab === 'marketplace') && (
                                    <div className="mt-3 grid grid-cols-2 gap-3 bg-emerald-50 p-3 rounded-lg">
                                        <input
                                            type="text"
                                            placeholder="Product Name"
                                            className="p-2 border rounded text-sm"
                                            value={productName}
                                            onChange={(e) => setProductName(e.target.value)}
                                        />
                                        <input
                                            type="number"
                                            placeholder="Price (₦)"
                                            className="p-2 border rounded text-sm"
                                            value={productPrice}
                                            onChange={(e) => setProductPrice(e.target.value)}
                                        />
                                    </div>
                                )}

                                <div className="flex justify-between items-center mt-3 pt-3 border-t">
                                    <button
                                        onClick={() => setIsProductPost(!isProductPost)}
                                        className={`p-2 rounded flex items-center gap-1 text-xs font-medium ${isProductPost || activeTab === 'marketplace' ? 'text-emerald-600 bg-emerald-50' : 'text-gray-500'}`}
                                    >
                                        <Tag size={16} /> Sell Product
                                    </button>
                                    <button
                                        onClick={handleCreatePost}
                                        disabled={loading || !newPostContent}
                                        className="bg-emerald-600 text-white px-6 py-2 rounded-full text-sm font-semibold"
                                    >
                                        Post
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* Posts Feed */}
                        {posts.map((post) => (
                            <div key={post.id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                                {editingPost?.id === post.id ? (
                                    // EDIT MODE
                                    <div className="p-4 space-y-3">
                                        <div className="flex justify-between items-center mb-2">
                                            <h3 className="font-bold text-gray-700">Edit Post</h3>
                                            <button onClick={() => setEditingPost(null)}><X size={18} /></button>
                                        </div>
                                        <textarea
                                            className="w-full p-2 border rounded"
                                            value={editContent}
                                            onChange={(e) => setEditContent(e.target.value)}
                                        />
                                        {post.type === 'product' && (
                                            <div className="grid grid-cols-2 gap-3">
                                                <input
                                                    type="number"
                                                    className="p-2 border rounded"
                                                    value={editPrice}
                                                    onChange={(e) => setEditPrice(e.target.value)}
                                                    placeholder="Price"
                                                />
                                                <select
                                                    className="p-2 border rounded"
                                                    value={editStatus}
                                                    onChange={(e) => setEditStatus(e.target.value)}
                                                >
                                                    <option value="available">Available</option>
                                                    <option value="preorder">Pre-order</option>
                                                    <option value="unavailable">Unavailable</option>
                                                </select>
                                            </div>
                                        )}
                                        <div className="flex justify-end gap-2">
                                            <button onClick={handleUpdatePost} className="bg-emerald-600 text-white px-4 py-2 rounded">Save</button>
                                        </div>
                                    </div>
                                ) : (
                                    // VIEW MODE
                                    <>
                                        <div className="p-4 flex justify-between items-start">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 bg-gray-200 rounded-full overflow-hidden">
                                                    {post.user_avatar ? <img src={post.user_avatar} className="w-full h-full object-cover" /> : <div className="w-full h-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold">{post.username?.[0]}</div>}
                                                </div>
                                                <div>
                                                    <h3 className="font-semibold text-gray-900">{post.username}</h3>
                                                    <p className="text-xs text-gray-500">{new Date(post.created_at).toLocaleDateString()}</p>
                                                </div>
                                            </div>

                                            {(user?.role === 'admin' || user?.id === post.user_id) && (
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={() => {
                                                            setEditingPost(post);
                                                            setEditContent(post.content);
                                                            setEditPrice(post.product_price || '');
                                                            setEditStatus(post.is_available ? 'available' : 'unavailable');
                                                        }}
                                                        className="text-gray-400 hover:text-blue-500"
                                                    >
                                                        <Edit2 size={16} />
                                                    </button>
                                                    <button onClick={() => handleDeletePost(post.id)} className="text-gray-400 hover:text-red-500">
                                                        <Trash2 size={16} />
                                                    </button>
                                                </div>
                                            )}
                                        </div>

                                        <div className="px-4 pb-2">
                                            {post.type === 'product' && (
                                                <div className="mb-2">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${post.is_available ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                                                            {post.is_available ? 'In Stock' : 'Unavailable'}
                                                        </span>
                                                    </div>
                                                    <h4 className="font-bold text-lg">{post.product_name}</h4>
                                                    <p className="text-emerald-700 font-bold text-xl">₦{post.product_price?.toLocaleString()}</p>
                                                </div>
                                            )}
                                            <p className="text-gray-800 whitespace-pre-wrap">{post.content}</p>
                                        </div>

                                        {/* Images */}
                                        {post.images && post.images.length > 0 && (
                                            <div className={`mt-2 ${post.images.length === 1 ? '' : 'grid grid-cols-2 gap-1'} max-h-96 overflow-hidden`}>
                                                {post.images.slice(0, 4).map((img, idx) => (
                                                    <img
                                                        key={idx}
                                                        src={img}
                                                        className="w-full h-full object-cover cursor-pointer hover:opacity-90"
                                                        onClick={() => setLightboxImage(img)}
                                                    />
                                                ))}
                                            </div>
                                        )}

                                        {/* Actions */}
                                        <div className="px-4 py-3 border-t flex items-center justify-between text-gray-500 text-sm">
                                            <div className="flex gap-4">
                                                <button className="flex items-center gap-1 hover:text-red-500"><Heart size={18} /> Like</button>
                                                <button
                                                    className="flex items-center gap-1 hover:text-blue-500"
                                                    onClick={() => setExpandedPostId(expandedPostId === post.id ? null : post.id)}
                                                >
                                                    <MessageCircle size={18} /> {post.comments?.length || 0}
                                                </button>
                                            </div>
                                            {post.type === 'product' && post.is_available && (
                                                <button className="bg-emerald-600 text-white px-4 py-1.5 rounded-lg text-xs font-bold">
                                                    Add to Cart
                                                </button>
                                            )}
                                        </div>

                                        {/* Comments Section */}
                                        {expandedPostId === post.id && (
                                            <div className="bg-gray-50 p-4 border-t space-y-3">
                                                {post.comments?.map((comment) => (
                                                    <div key={comment.id} className="flex gap-2 text-sm">
                                                        <div className="w-8 h-8 bg-gray-200 rounded-full flex-shrink-0 overflow-hidden">
                                                            {comment.user_avatar && <img src={comment.user_avatar} className="w-full h-full object-cover" />}
                                                        </div>
                                                        <div className="flex-1">
                                                            {editingCommentId === comment.id ? (
                                                                <div className="flex gap-2">
                                                                    <input
                                                                        className="flex-1 p-1 border rounded"
                                                                        value={editCommentContent}
                                                                        onChange={(e) => setEditCommentContent(e.target.value)}
                                                                    />
                                                                    <button onClick={() => handleEditComment(post.id, comment.id)} className="text-emerald-600"><Check size={16} /></button>
                                                                    <button onClick={() => setEditingCommentId(null)} className="text-gray-500"><X size={16} /></button>
                                                                </div>
                                                            ) : (
                                                                <div className="bg-white p-2 rounded-lg border shadow-sm relative group">
                                                                    <p className="font-bold text-xs">{comment.username}</p>
                                                                    <p className="text-gray-700">{comment.content}</p>
                                                                    {user?.id === comment.user_id && (
                                                                        <button
                                                                            onClick={() => {
                                                                                setEditingCommentId(comment.id);
                                                                                setEditCommentContent(comment.content);
                                                                            }}
                                                                            className="absolute top-2 right-2 text-gray-400 opacity-0 group-hover:opacity-100 hover:text-blue-500"
                                                                        >
                                                                            <Edit2 size={12} />
                                                                        </button>
                                                                    )}
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                                <div className="flex gap-2">
                                                    <input
                                                        className="flex-1 p-2 border rounded-full text-sm"
                                                        placeholder="Write a comment..."
                                                        value={newComment}
                                                        onChange={(e) => setNewComment(e.target.value)}
                                                        onKeyPress={(e) => e.key === 'Enter' && handleAddComment(post.id)}
                                                    />
                                                    <button onClick={() => handleAddComment(post.id)} className="text-emerald-600 font-bold text-sm">Post</button>
                                                </div>
                                            </div>
                                        )}
                                    </>
                                )}
                            </div>
                        ))}

                        {posts.length === 0 && <div className="text-center py-10 text-gray-500">No posts yet.</div>}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CommunityDetailsModal;
