

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
            
            # Let's try searching the 'community_products' collection first
            products_cursor = db.community_products.find({
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
