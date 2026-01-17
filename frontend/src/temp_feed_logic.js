
// Fetch Community Feed (Aggregated from user communities)
const fetchCommunityFeed = async () => {
    if (!user || userCommunities.length === 0) return;
    setFeedLoading(true);
    try {
        // Fetch posts from each community the user has joined
        // Limit to 3 posts per community for the initial feed to keep it fast
        const promises = userCommunities.map(comm =>
            fetch(`${API_BASE_URL}/api/communities/${comm.id}/posts?limit=3`)
                .then(res => res.json())
                .then(posts => posts.map(p => ({ ...p, community_name: comm.name, community_id: comm.id })))
                .catch(err => [])
        );

        const results = await Promise.all(promises);
        const allPosts = results.flat();

        // Sort by newest first
        allPosts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        setCommunityFeed(allPosts);
    } catch (error) {
        console.error("Error fetching feed:", error);
    } finally {
        setFeedLoading(false);
    }
};

useEffect(() => {
    if (currentPlatform === 'communities' && user) {
        fetchCommunityFeed();
    }
}, [currentPlatform, userCommunities]);
