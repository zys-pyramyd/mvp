
import React, { useEffect, useState } from 'react';

const MyCommunities = ({ onSelect, refreshTrigger, onCreate }) => {
    const [communities, setCommunities] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCommunities = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/communities/my-communities`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    setCommunities(data);
                }
            } catch (error) {
                console.error("Failed to fetch my communities", error);
            } finally {
                setLoading(false);
            }
        };

        if (localStorage.getItem('token')) {
            fetchCommunities();
        }
    }, [refreshTrigger]);

    if (loading) return <div className="p-4 text-center text-gray-500">Loading your communities...</div>;

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 bg-emerald-50 border-b border-emerald-100 flex justify-between items-center">
                <h3 className="font-semibold text-emerald-900">My Communities</h3>
                <button
                    onClick={onCreate}
                    className="text-xs bg-emerald-600 text-white px-2 py-1 rounded hover:bg-emerald-700 transition-colors"
                >
                    + Create
                </button>
            </div>

            {communities.length === 0 ? (
                <div className="p-8 text-center">
                    <p className="text-gray-500 mb-2">You haven't joined any communities yet.</p>
                    <p className="text-xs text-gray-400">Use the search to find groups!</p>
                </div>
            ) : (
                <div className="divide-y divide-gray-100">
                    {communities.map(comm => (
                        <button
                            key={comm.id}
                            onClick={() => onSelect(comm)}
                            className="w-full text-left p-4 hover:bg-gray-50 transition-colors flex items-center justify-between group"
                        >
                            <div>
                                <h4 className="font-medium text-gray-900 group-hover:text-emerald-700">{comm.name}</h4>
                                <p className="text-xs text-gray-500">{comm.members_count || 0} members</p>
                            </div>
                            <span className="text-gray-300 group-hover:text-emerald-500">→</span>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};

export default MyCommunities;
