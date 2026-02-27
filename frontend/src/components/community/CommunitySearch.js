
import React, { useState } from 'react';

const CommunitySearch = ({ onJoin }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e) => {
        if (e) e.preventDefault();

        setLoading(true);
        try {
            const queryParam = searchTerm.trim() ? `?q=${searchTerm}&type=community` : '?type=community';
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/communities/search${queryParam}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setResults(data.communities || []);
            }
        } catch (error) {
            console.error("Search failed", error);
        } finally {
            setLoading(false);
        }
    };

    // Load popular communities on mount
    React.useEffect(() => {
        handleSearch();
    }, []);

    return (
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <h3 className="font-bold text-gray-900 mb-3 text-sm">Find Communities</h3>
            <form onSubmit={handleSearch} className="mb-4">
                <div className="flex gap-2">
                    <input
                        type="text"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-emerald-500"
                        placeholder="Search..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <button
                        type="submit"
                        className="px-3 py-2 bg-emerald-600 text-white rounded text-sm hover:bg-emerald-700 disabled:opacity-50"
                        disabled={loading}
                    >
                        🔍
                    </button>
                </div>
            </form>

            <div className="space-y-3 max-h-60 overflow-y-auto">
                {results.length === 0 && !loading && searchTerm && (
                    <p className="text-gray-500 text-center text-xs">No result.</p>
                )}
                {results.map(community => (
                    <div key={community.id} className="flex flex-col gap-2 p-2 border border-gray-100 rounded hover:bg-gray-50">
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="font-semibold text-sm text-gray-900 line-clamp-1">{community.name}</h4>
                                <p className="text-xs text-gray-500 line-clamp-1">{community.category}</p>
                            </div>
                            <button
                                onClick={() => onJoin(community.id)}
                                className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded hover:bg-emerald-200"
                            >
                                Join
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CommunitySearch;
