
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
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Find Communities</h3>
            <form onSubmit={handleSearch} className="mb-6">
                <div className="flex gap-2">
                    <input
                        type="text"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        placeholder="Search by name, location, or crop..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <button
                        type="submit"
                        className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"
                        disabled={loading}
                    >
                        {loading ? 'Searching...' : 'Search'}
                    </button>
                </div>
            </form>

            <div className="space-y-4">
                {results.length === 0 && !loading && searchTerm && (
                    <p className="text-gray-500 text-center">No communities found. Try a different term.</p>
                )}
                {results.map(community => (
                    <div key={community.id} className="flex justify-between items-center p-4 border border-gray-100 rounded-lg hover:bg-gray-50">
                        <div>
                            <h4 className="font-medium text-gray-900">{community.name}</h4>
                            <p className="text-sm text-gray-500">{community.description}</p>
                            <div className="flex gap-2 mt-1">
                                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">{community.category}</span>
                                <span className="text-xs text-gray-400">{community.members_count || 0} members</span>
                            </div>
                        </div>
                        <button
                            onClick={() => onJoin(community.id)}
                            className="px-4 py-1.5 bg-emerald-100 text-emerald-700 rounded-md hover:bg-emerald-200 text-sm font-medium"
                        >
                            Join
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CommunitySearch;
