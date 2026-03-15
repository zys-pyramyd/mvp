import React, { useState } from 'react';
import { Star, X } from 'lucide-react';

const RatingModal = ({ onClose, onSubmit, orderItem }) => {
    const [rating, setRating] = useState(0);
    const [hoveredRating, setHoveredRating] = useState(0);
    const [comment, setComment] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (rating === 0) {
            alert('Please select a rating');
            return;
        }

        setIsSubmitting(true);
        try {
            await onSubmit({
                order_id: orderItem.id, // Assuming orderItem has the order ID or we pass it separately
                product_id: orderItem.product_id,
                rating,
                comment
            });
            onClose();
        } catch (error) {
            console.error('Error submitting rating:', error);
            alert('Failed to submit rating. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl max-w-md w-full overflow-hidden">
                <div className="p-4 border-b flex justify-between items-center">
                    <h3 className="font-bold text-lg">Rate Product</h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                        <X size={20} />
                    </button>
                </div>

                <div className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                            {orderItem?.image ? (
                                <img src={orderItem.image} alt={orderItem.product_name} className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">IMG</div>
                            )}
                        </div>
                        <div>
                            <h4 className="font-semibold text-gray-900 line-clamp-1">{orderItem?.product_name || 'Product'}</h4>
                            <p className="text-sm text-gray-500">How was your experience?</p>
                        </div>
                    </div>

                    <form onSubmit={handleSubmit}>
                        {/* Star Rating */}
                        <div className="flex justify-center gap-2 mb-6">
                            {[1, 2, 3, 4, 5].map((star) => (
                                <button
                                    key={star}
                                    type="button"
                                    onMouseEnter={() => setHoveredRating(star)}
                                    onMouseLeave={() => setHoveredRating(0)}
                                    onClick={() => setRating(star)}
                                    className="focus:outline-none transition-transform hover:scale-110"
                                >
                                    <Star
                                        size={32}
                                        className={`${star <= (hoveredRating || rating)
                                                ? 'fill-yellow-400 text-yellow-400'
                                                : 'text-gray-300'
                                            } transition-colors`}
                                    />
                                </button>
                            ))}
                        </div>

                        <div className="text-center mb-6 text-sm font-medium text-emerald-600">
                            {rating === 1 && 'Poor 😞'}
                            {rating === 2 && 'Fair 😐'}
                            {rating === 3 && 'Good 🙂'}
                            {rating === 4 && 'Very Good 😄'}
                            {rating === 5 && 'Excellent! 🤩'}
                            {rating === 0 && 'Select stars'}
                        </div>

                        {/* Comment */}
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Write a review (Optional)
                            </label>
                            <textarea
                                value={comment}
                                onChange={(e) => setComment(e.target.value)}
                                placeholder="Share more details about your experience..."
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 min-h-[100px]"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full bg-emerald-600 text-white py-3 rounded-lg font-bold hover:bg-emerald-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isSubmitting ? 'Submitting...' : 'Submit Review'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default RatingModal;
