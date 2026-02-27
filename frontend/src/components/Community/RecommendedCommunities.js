import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';

const RecommendedCommunities = ({ onJoin, API_BASE_URL }) => {
    const { user } = useAuth();
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRecommendations = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`${API_BASE_URL}/api/communities/recommended`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    setRecommendations(await response.json());
                }
            } catch (error) {
                console.error("Failed to fetch recommendations", error);
            } finally {
                setLoading(false);
            }
        };

        if (user) fetchRecommendations();
    }, [user, API_BASE_URL]);

    if (loading) return <div className="p-4 text-center text-gray-400 text-xs">Loading ideas...</div>;
    if (recommendations.length === 0) return null;

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="font-bold text-gray-900 mb-4 text-sm">Recommended for You</h3>
            <div className="space-y-4">
                {recommendations.map(comm => (
                    <div key={comm.id} className="flex flex-col gap-2 border-b border-gray-100 pb-3 last:border-0 last:pb-0">
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="font-semibold text-sm text-gray-800">{comm.name}</h4>
                                <p className="text-xs text-gray-500 line-clamp-2">{comm.description}</p>
                            </div>
                        </div>
                        <div className="flex justify-between items-center mt-1">
                            <span className="text-xs text-gray-400">{comm.members_count || 0} members</span>
                            <button
                                onClick={() => onJoin(comm.id)}
                                className="text-xs bg-emerald-50 text-emerald-600 px-3 py-1 rounded-full font-medium hover:bg-emerald-100"
                            >
                                + Join
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RecommendedCommunities;
