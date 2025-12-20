import React from 'react';
import { X, Star, MapPin, Phone, Mail, Award, Calendar } from 'lucide-react';

const SellerDetailsModal = ({ seller, onClose }) => {
    if (!seller) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto relative">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 p-2 bg-white rounded-full shadow-sm hover:bg-gray-100 z-10"
                >
                    <X size={20} />
                </button>

                {/* Header / Cover */}
                <div className="h-32 bg-gradient-to-r from-emerald-600 to-emerald-800 relative">
                    <div className="absolute -bottom-10 left-6">
                        <div className="w-24 h-24 bg-white rounded-full p-1 shadow-md">
                            <div className="w-full h-full bg-gray-200 rounded-full flex items-center justify-center overflow-hidden">
                                {seller.profile_picture ? (
                                    <img src={seller.profile_picture} alt={seller.username} className="w-full h-full object-cover" />
                                ) : (
                                    <span className="text-2xl font-bold text-gray-400">{seller.username?.[0]?.toUpperCase()}</span>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="pt-12 px-6 pb-6">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900">{seller.business_name || seller.username}</h2>
                            <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                                <span className="capitalize px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">
                                    {seller.partner_type || 'Seller'}
                                </span>
                                {seller.is_verified && (
                                    <span className="flex items-center gap-1 text-blue-600">
                                        <Award size={14} /> Verified
                                    </span>
                                )}
                            </div>
                        </div>
                        <div className="flex items-center gap-1 bg-yellow-50 px-3 py-1 rounded-lg">
                            <Star className="text-yellow-400 fill-current" size={20} />
                            <span className="font-bold text-gray-900">{seller.rating || 'New'}</span>
                        </div>
                    </div>

                    <p className="text-gray-600 mb-6">{seller.bio || "No bio available."}</p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                        <div className="space-y-3">
                            <h3 className="font-semibold text-gray-900">Contact Information</h3>
                            <div className="flex items-center gap-3 text-gray-600">
                                <MapPin size={18} />
                                <span>{seller.business_address || "Location hidden"}</span>
                            </div>
                            {seller.phone && (
                                <div className="flex items-center gap-3 text-gray-600">
                                    <Phone size={18} />
                                    <span>{seller.phone}</span>
                                </div>
                            )}
                            {seller.email && (
                                <div className="flex items-center gap-3 text-gray-600">
                                    <Mail size={18} />
                                    <span>{seller.email}</span>
                                </div>
                            )}
                        </div>

                        <div className="space-y-3">
                            <h3 className="font-semibold text-gray-900">Performance</h3>
                            <div className="flex items-center gap-3 text-gray-600">
                                <Award size={18} />
                                <span>{seller.total_sales || 0} Successful Sales</span>
                            </div>
                            <div className="flex items-center gap-3 text-gray-600">
                                <Calendar size={18} />
                                <span>Joined {new Date(seller.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>
                    </div>

                    <div className="border-t pt-6">
                        <h3 className="font-semibold text-gray-900 mb-4">Listings</h3>
                        <p className="text-gray-500 italic">No active listings displayed here.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SellerDetailsModal;
