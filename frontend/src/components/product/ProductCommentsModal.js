import React, { useState, useEffect } from 'react';

const ProductCommentsModal = ({ product, onClose }) => {
    const [comments, setComments] = useState([]);
    const [stats, setStats] = useState({ count: 0 });
    const [loading, setLoading] = useState(true);
    const [newComment, setNewComment] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const token = localStorage.getItem('token');
    const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

    useEffect(() => {
        fetchComments();
    }, [product.id]);

    const fetchComments = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/products/${product.id}/comments`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setComments(data);
                setStats({ count: data.length });
            }
        } catch (error) {
            console.error("Failed to fetch comments", error);
        } finally {
            setLoading(false);
        }
    };

    const handlePostComment = async (e) => {
        e.preventDefault();
        if (!newComment.trim()) return;

        setSubmitting(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/products/${product.id}/comments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ content: newComment })
            });

            if (res.ok) {
                const comment = await res.json();
                setComments([comment, ...comments]);
                setNewComment('');
                setStats(prev => ({ count: prev.count + 1 }));
            } else {
                alert("Failed to post comment");
            }
        } catch (error) {
            console.error("Post error", error);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-xl max-w-lg w-full overflow-hidden flex flex-col max-h-[80vh]">
                {/* Header */}
                <div className="p-4 border-b flex justify-between items-center bg-gray-50">
                    <div>
                        <h3 className="font-bold text-gray-900">Q&A</h3>
                        <p className="text-xs text-gray-500">Ask about {product.title}</p>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 font-bold text-xl">&times;</button>
                </div>

                {/* Comments List */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {loading ? (
                        <div className="text-center py-4 text-gray-400">Loading...</div>
                    ) : comments.length === 0 ? (
                        <div className="text-center py-8 text-gray-400">
                            <p>No questions yet.</p>
                            <p className="text-sm">Be the first to ask about this product!</p>
                        </div>
                    ) : (
                        comments.map((comment, idx) => (
                            <div key={idx} className="flex gap-3">
                                <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold text-xs shrink-0">
                                    {comment.username?.[0]?.toUpperCase() || 'U'}
                                </div>
                                <div className="bg-gray-50 p-3 rounded-lg flex-1">
                                    <div className="flex justify-between items-baseline mb-1">
                                        <span className="font-semibold text-sm text-gray-900">{comment.username}</span>
                                        <span className="text-xs text-gray-400">
                                            {new Date(comment.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-700">{comment.comment}</p>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Input Area */}
                <form onSubmit={handlePostComment} className="p-4 border-t bg-white">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            className="flex-1 border rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            placeholder="Ask a question..."
                            value={newComment}
                            onChange={(e) => setNewComment(e.target.value)}
                        />
                        <button
                            type="submit"
                            disabled={!newComment.trim() || submitting}
                            className="bg-emerald-600 text-white rounded-full px-4 py-2 text-sm font-bold hover:bg-emerald-700 disabled:bg-gray-300"
                        >
                            Send
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ProductCommentsModal;
