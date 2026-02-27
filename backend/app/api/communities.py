

from fastapi import APIRouter, HTTPException, Depends, Query
from app.api.deps import get_db, get_current_user
from typing import List, Optional
from app.models.community import Community, CommunityProduct
from datetime import datetime
from pydantic import BaseModel, Field
import html

router = APIRouter()

# SECURITY: Input validation models
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommunityCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=500)
    category: str = Field(..., max_length=50)
    is_private: bool = False

class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)

class SharePostRequest(BaseModel):
    target_community_id: str
    message: str = Field(default="", max_length=500)

class CommunityMemberRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(admin|member|moderator)$")

# SECURITY: XSS protection
def sanitize_content(content: str) -> str:
    """Sanitize user input to prevent XSS attacks"""
    return html.escape(content.strip())

@router.get("/search")
async def search_communities(
    q: Optional[str] = Query(None, min_length=1),
    type: str = "all"  # all, community, product
):
    """Search communities and products. If q is empty, returns popular communities."""
    db = get_db()
    results = {
        "communities": [],
        "products": []
    }
    
    try:
        if type in ["all", "community"]:
            # Search communities
            query = {}
            if q:
                query = {
                    "$or": [
                        {"name": {"$regex": q, "$options": "i"}},
                        {"description": {"$regex": q, "$options": "i"}},
                        {"category": {"$regex": q, "$options": "i"}}
                    ]
                }
            
            # Sort by member count descending (popular first)
            communities_cursor = db.communities.find(query).sort("members_count", -1).limit(20)
            
            communities = list(communities_cursor)
            for comm in communities:
                comm.pop('_id', None)
            results["communities"] = communities
        
        if type in ["all", "product"]:
            # Search products within communities (assuming collection community_products)
            # Note: Verify if community products are in 'products' collection or separate 'community_products'
            # Based on models, it seems separate but typically they might be mixed. 
            # Let's assume 'community_products' collection based on likely pattern or check server.py
            
            # Checking if 'community_products' exists in DB initialization. 
            # If not, we search generic products with 'community' platform or similar.
            # Safe bet: Search 'products' collection where platform='community' OR 'community_products' if it exists.
            
            # Let's try searching the 'products' collection
            products_cursor = db.products.find({
                "$or": [
                    {"title": {"$regex": q, "$options": "i"}},
                    {"description": {"$regex": q, "$options": "i"}},
                    {"category": {"$regex": q, "$options": "i"}}
                ]
            }).limit(10)
            
            products = list(products_cursor)
            for prod in products:
                prod.pop('_id', None)
            results["products"] = products
            
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommended")
async def get_recommended_communities(limit: int = 5, current_user: dict = Depends(get_current_user)):
    """Get recommended communities and posts"""
    db = get_db()
    
    # 1. Random/Popular Communities the user hasn't joined
    # Get user's communities
    user_memberships = list(db.community_members.find({"user_id": current_user['id']}))
    joined_ids = [m['community_id'] for m in user_memberships]
    
    # Find popular communities not in joined_ids
    pipeline = [
        {"$match": {"id": {"$nin": joined_ids}}},
        {"$sample": {"size": limit}}  # Random selection
    ]
    
    communities = list(db.communities.aggregate(pipeline))
    for c in communities:
        c.pop('_id', None)
        
    # 2. Random/High engagement posts from any public community
    # (Optional, for now just communities)
    
    return communities

@router.get("/my-communities")
async def get_my_communities(current_user: dict = Depends(get_current_user)):
    """List communities the user has joined"""
    db = get_db()
    # Assuming 'community_members' collection or embed in user/community
    # Let's assume 'community_members' collection: {community_id, user_id, role}
    
    cursor = db.community_members.find({"user_id": current_user['id']})
    memberships = list(cursor)
    
    community_ids = [m['community_id'] for m in memberships]
    
    communities = list(db.communities.find({"id": {"$in": community_ids}}))
    for c in communities:
        c.pop('_id', None)
        
    return communities

@router.post("/{community_id}/join")
async def join_community(community_id: str, current_user: dict = Depends(get_current_user)):
    """Join a community"""
    db = get_db()
    
    community = db.communities.find_one({"id": community_id})
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
        
    # Check if already member
    existing = db.community_members.find_one({
        "community_id": community_id, 
        "user_id": current_user['id']
    })
    
    if existing:
        return {"message": "Already a member"}
        
    db.community_members.insert_one({
        "community_id": community_id,
        "user_id": current_user['id'],
        "joined_at": datetime.utcnow(),
        "role": "member"
    })
    
    # Update member count
    db.communities.update_one({"id": community_id}, {"$inc": {"members_count": 1}})
    
    return {"message": "Joined successfully", "community_id": community_id}

@router.post("/{community_id}/leave")
async def leave_community(community_id: str, current_user: dict = Depends(get_current_user)):
    """Leave a community"""
    db = get_db()
    
    result = db.community_members.delete_one({
        "community_id": community_id, 
        "user_id": current_user['id']
    })
    
    if result.deleted_count > 0:
        db.communities.update_one({"id": community_id}, {"$inc": {"members_count": -1}})
        return {"message": "Left community"}
        
    return {"message": "Not a member"}

@router.get("/{community_id}/posts")
async def get_community_posts(community_id: str, limit: int = 20):
    """Get community posts"""
    db = get_db()
    cursor = db.community_posts.find({"community_id": community_id}).sort("created_at", -1).limit(limit)
    posts = list(cursor)
    
    # Enrich with author info
    for p in posts:
        p.pop('_id', None)
        user = db.users.find_one({"id": p.get("user_id")})
        p["author"] = f"{user.get('first_name', '')} {user.get('last_name', '')}" if user else "Unknown"
        # Format date for frontend
        if isinstance(p.get("created_at"), datetime):
            p["date"] = p.get("created_at").strftime("%Y-%m-%d %H:%M")
        else:
            p["date"] = str(p.get("created_at", ""))

    return posts

@router.post("/{community_id}/posts")
async def create_community_post(community_id: str, post: dict, current_user: dict = Depends(get_current_user)):
    """Create a new post in a community"""
    db = get_db()
    
    # Check membership
    member = db.community_members.find_one({
        "community_id": community_id, 
        "user_id": current_user['id']
    })
    
    if not member:
        raise HTTPException(status_code=403, detail="Must be a member to post")
        
    # Restrict to Admins/Moderators only (Creators are usually Admins)
    if member.get('role') not in ['admin', 'moderator', 'creator']:
         raise HTTPException(status_code=403, detail="Only community admins can create posts")
        
    new_post = {
        "id": f"post_{datetime.utcnow().timestamp()}",
        "community_id": community_id,
        "user_id": current_user['id'],
        "content": post.get("content"),
        "created_at": datetime.utcnow(),
        "type": "text"
    }
    
    db.community_posts.insert_one(new_post)
    new_post.pop('_id', None)
    
    return new_post

@router.get("/{community_id}/products")
async def get_community_products(community_id: str, limit: int = 50):
    """Get products listed in a community"""
    db = get_db()
    # Query both generic products with community tag AND specific community_products
    cursor = db.products.find({
        "$or": [
            {"community_id": community_id},
            {"platform": "community", "related_community_id": community_id}
        ]
    }).limit(limit)
    
    products = list(cursor)
    for p in products:
        p.pop('_id', None)
        # Ensure name field exists for frontend consistency
        if 'name' not in p and 'title' in p:
            p['name'] = p['title']
            
    return products

# --- Community Creation ---

@router.post("/")
async def create_community(
    community_data: CommunityCreate,  # SECURITY: Validated input
    current_user: dict = Depends(get_current_user)
):
    """Create a new community"""
    db = get_db()
    
    community = {
        "id": f"comm_{datetime.utcnow().timestamp()}",
        "name": sanitize_content(community_data.name),  # SECURITY: XSS protection
        "description": sanitize_content(community_data.description),  # SECURITY: XSS protection
        "category": sanitize_content(community_data.category),
        "creator_id": current_user["id"],
        "created_at": datetime.utcnow(),
        "members_count": 1,
        "is_private": community_data.is_private
    }
    
    db.communities.insert_one(community)
    
    # Add creator as admin member
    db.community_members.insert_one({
        "community_id": community["id"],
        "user_id": current_user["id"],
        "joined_at": datetime.utcnow(),
        "role": "admin"
    })
    
    community.pop("_id", None)
    return community

# --- Post Engagement (Like, Comment, Share) ---

@router.post("/posts/{post_id}/like")
async def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Like or unlike a post"""
    db = get_db()
    
    # Check if already liked
    existing = db.post_likes.find_one({
        "post_id": post_id,
        "user_id": current_user["id"]
    })
    
    if existing:
        # Unlike
        db.post_likes.delete_one({"_id": existing["_id"]})
        db.community_posts.update_one(
            {"id": post_id},
            {"$inc": {"likes_count": -1}}
        )
        return {"message": "Unliked", "liked": False}
    else:
        # Like
        db.post_likes.insert_one({
            "post_id": post_id,
            "user_id": current_user["id"],
            "created_at": datetime.utcnow()
        })
        db.community_posts.update_one(
            {"id": post_id},
            {"$inc": {"likes_count": 1}}
        )
        return {"message": "Liked", "liked": True}

@router.post("/posts/{post_id}/comments")
async def comment_on_post(
    post_id: str,
    comment_data: CommentCreate,  # SECURITY: Validated input
    current_user: dict = Depends(get_current_user)
):
    """Comment on a post"""
    db = get_db()
    
    comment = {
        "id": f"comment_{datetime.utcnow().timestamp()}",
        "post_id": post_id,
        "user_id": current_user["id"],
        "username": current_user["username"],
        "content": sanitize_content(comment_data.content),  # SECURITY: XSS protection
        "created_at": datetime.utcnow()
    }
    
    db.post_comments.insert_one(comment)
    db.community_posts.update_one(
        {"id": post_id},
        {"$inc": {"comments_count": 1}}
    )
    
    comment.pop("_id", None)
    return comment

@router.get("/posts/{post_id}/comments")
async def get_post_comments(post_id: str, limit: int = 20):
    """Get comments for a post"""
    db = get_db()
    comments = list(db.post_comments.find({"post_id": post_id})
                   .sort("created_at", -1)
                   .limit(limit))
    
    for c in comments:
        c.pop("_id", None)
    return comments

@router.post("/posts/{post_id}/share")
async def share_post(
    post_id: str,
    share_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Share a post to another community or create new post"""
    db = get_db()
    
    original_post = db.community_posts.find_one({"id": post_id})
    if not original_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Create shared post
    shared_post = {
        "id": f"post_{datetime.utcnow().timestamp()}",
        "community_id": share_data.get("target_community_id"),
        "user_id": current_user["id"],
        "content": share_data.get("message", ""),
        "shared_post_id": post_id,
        "shared_post": {
            "id": original_post.get("id"),
            "content": original_post.get("content"),
            "author": original_post.get("user_id")
        },
        "created_at": datetime.utcnow(),
        "type": "shared"
    }
    
    db.community_posts.insert_one(shared_post)
    shared_post.pop("_id", None)
    
    return shared_post

@router.put("/{community_id}/members/{user_id}/role")
async def update_member_role(
    community_id: str,
    user_id: str,
    role_data: CommunityMemberRoleUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a member's role (Admin only)"""
    db = get_db()
    
    # Check if current user is admin of the community
    requester_membership = db.community_members.find_one({
        "community_id": community_id,
        "user_id": current_user["id"],
        "role": "admin"
    })
    
    if not requester_membership:
        raise HTTPException(status_code=403, detail="Only admins can update roles")

    # Update target member
    result = db.community_members.update_one(
        {"community_id": community_id, "user_id": user_id},
        {"$set": {"role": role_data.role}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Member not found")
        
    return {"message": "Role updated successfully"}

@router.get("/{community_id}/members")
async def get_community_members(community_id: str, current_user: dict = Depends(get_current_user)):
    """Get list of community members"""
    db = get_db()
    
    # Verify membership (optional, but good for privacy if private community)
    # For now, allow checking members if you are in it
    
    cursor = db.community_members.find({"community_id": community_id})
    members = list(cursor)
    
    results = []
    for m in members:
        user = db.users.find_one({"id": m["user_id"]})
        if user:
            results.append({
                "user_id": m["user_id"],
                "username": user.get("username"),
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "profile_picture": user.get("profile_picture"),
                "role": m.get("role", "member"),
                "joined_at": m.get("joined_at")
            })
            
    return results

@router.post("/{community_id}/members")
async def add_community_member(
    community_id: str, 
    payload: dict, # {user_id: str}
    current_user: dict = Depends(get_current_user)
):
    """Add a member manually (Admin only)"""
    db = get_db()
    target_user_id = payload.get("user_id")
    
    # Check admin
    requester = db.community_members.find_one({
        "community_id": community_id, 
        "user_id": current_user['id'],
        "role": {"$in": ["admin", "creator"]}
    })
    if not requester:
        raise HTTPException(status_code=403, detail="Only admins can add members")
        
    # Check if target exists
    target = db.users.find_one({"id": target_user_id})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if already member
    exists = db.community_members.find_one({"community_id": community_id, "user_id": target_user_id})
    if exists:
        return {"message": "User is already a member"}
        
    db.community_members.insert_one({
        "community_id": community_id,
        "user_id": target_user_id,
        "joined_at": datetime.utcnow(),
        "role": "member",
        "added_by": current_user['id']
    })
    
    db.communities.update_one({"id": community_id}, {"$inc": {"members_count": 1}})
    
    return {"message": "Member added successfully"}

@router.delete("/{community_id}")
async def delete_community(community_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a community (Creator only)"""
    db = get_db()
    
    community = db.communities.find_one({"id": community_id})
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
        
    if community.get("creator_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the creator can delete the community")
        
    # Delete everything
    db.communities.delete_one({"id": community_id})
    db.community_members.delete_many({"community_id": community_id})
    db.community_posts.delete_many({"community_id": community_id})
    # Optional: Delete products or flag them? 
    # For now, let's leave products but they won't show in community feed.
    
    return {"message": "Community deleted successfully"}

@router.get("/trending-products")
async def get_trending_community_products(limit: int = 10):
    """Get trending community products across all communities"""
    db = get_db()
    
    # Query products with a community platform or community_id
    cursor = db.products.find({
        "$or": [
            {"community_id": {"$exists": True, "$ne": None}},
            {"platform": "community"}
        ]
    }).sort("quantity_available", -1).limit(limit) # Sorting by available stock as proxy for now
    
    products = list(cursor)
    for p in products:
        p.pop('_id', None)
        # Fetch community details to display
        if p.get("community_id"):
            comm = db.communities.find_one({"id": p["community_id"]})
            if comm:
                p["community_name"] = comm.get("name")
                
    return products

@router.get("/global-feed")
async def get_global_community_feed(limit: int = 20):
    """Get aggregated posts and products from public communities"""
    db = get_db()
    
    # Get public communities
    public_comms = list(db.communities.find({"is_private": False}))
    public_comm_ids = [c["id"] for c in public_comms]
    
    if not public_comm_ids:
        return []
        
    # Get recent posts from these communities
    posts_cursor = db.community_posts.find({"community_id": {"$in": public_comm_ids}}).sort("created_at", -1).limit(limit)
    posts = list(posts_cursor)
    
    # Enrich posts
    for p in posts:
        p.pop('_id', None)
        p["feed_type"] = "post"
        user = db.users.find_one({"id": p.get("user_id")})
        p["author"] = f"{user.get('first_name', '')} {user.get('last_name', '')}" if user else "Unknown"
        if isinstance(p.get("created_at"), datetime):
            p["date"] = p.get("created_at").strftime("%Y-%m-%d %H:%M")
        else:
            p["date"] = str(p.get("created_at", ""))
            
        comm = db.communities.find_one({"id": p.get("community_id")})
        if comm:
            p["community_name"] = comm.get("name")
            
    # Get recent products from these communities
    products_cursor = db.products.find({
        "community_id": {"$in": public_comm_ids}
    }).sort("created_at", -1).limit(limit)
    
    products = list(products_cursor)
    for p in products:
        p.pop('_id', None)
        p["feed_type"] = "product"
        if isinstance(p.get("created_at"), datetime):
            p["date"] = p.get("created_at").strftime("%Y-%m-%d %H:%M")
        else:
            p["date"] = str(p.get("created_at", ""))
            
        comm = db.communities.find_one({"id": p.get("community_id")})
        if comm:
            p["community_name"] = comm.get("name")
            
    # Combine and sort by date descending
    combined_feed = posts + products
    # Sort by raw created_at if possible, else rely on string date
    combined_feed.sort(key=lambda x: x.get("created_at", x.get("date", "")), reverse=True)
    
    return combined_feed[:limit]
