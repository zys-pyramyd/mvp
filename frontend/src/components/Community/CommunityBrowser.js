import React from 'react';
import { X } from 'lucide-react';

const CommunityBrowser = ({ onClose, communities, onJoin, user }) => {
    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl max-w-4xl w-full h-[80vh] flex flex-col relative">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 p-2 bg-gray-100 rounded-full hover:bg-gray-200"
                >
                    <X size={20} />
                </button>
                <div className="p-6 border-b">
                    <h2 className="text-2xl font-bold">Communities</h2>
                    <p className="text-gray-600">Join communities to connect with others.</p>
                </div>
                <div className="flex-1 overflow-y-auto p-6">
                    {communities && communities.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {communities.map((community) => (
                                <div key={community.id} className="border p-4 rounded-lg">
                                    <h3 className="font-bold">{community.name}</h3>
                                    <button
                                        onClick={() => onJoin(community.id)}
                                        className="mt-2 bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm"
                                    >
                                        Join
                                    </button>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center text-gray-500 mt-10">No communities found.</div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CommunityBrowser;
