from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from datetime import datetime
import uuid

# Import auth helper dependencies
from auth import get_current_user

# Import models
from community.models import Community, Post, Comment

# Import DB (Assuming standard import path, might need adjustment based on server structure)
from database import db

router = APIRouter(prefix="/api/communities", tags=["Communities"])

# --- Community CRUD ---

@router.get("/", response_model=List[Community])
def get_communities():
    """List all communities"""
    communities = list(db.communities.find())
    return communities

@router.post("/", response_model=Community)
def create_community(community: Community, current_user: dict = Depends(get_current_user)):
    """Create a new community"""
    community.creator_id = current_user['id']
    community.members = [current_user['id']] # Creator is first member
    
    db.communities.insert_one(community.dict())
    return community

@router.post("/{id}/join")
def join_community(id: str, current_user: dict = Depends(get_current_user)):
    """Join a community"""
    result = db.communities.update_one(
        {"id": id},
        {"$addToSet": {"members": current_user['id']}}
    )
    if result.modified_count == 0:
        # Check if already member
        community = db.communities.find_one({"id": id})
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")
            
    return {"message": "Joined successfully", "community_id": id}

# --- Posts & Marketplace ---

@router.get("/{id}/posts", response_model=List[Post])
def get_community_posts(id: str, type: Optional[str] = None, skip: int = 0, limit: int = 20):
    """
    Get posts for a community. 
    Optional 'type' query param to filter for 'product' (Marketplace) or 'regular' (Feed).
    """
    query = {"community_id": id}
    
    # Filter by type if provided (e.g., ?type=product for Marketplace)
    if type:
        query["type"] = type
        
    # Exclude unavailable products if looking at marketplace
    if type == 'product':
        query["is_available"] = True
        
    posts = list(db.community_posts.find(query).sort("created_at", -1).skip(skip).limit(limit))
    return posts

@router.post("/{id}/posts", response_model=Post)
def create_post(id: str, post: Post, current_user: dict = Depends(get_current_user)):
    """Create a new post or product listing"""
    # Verify membership
    community = db.communities.find_one({"id": id})
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
        
    if current_user['id'] not in community['members']:
        raise HTTPException(status_code=403, detail="Must be a member to post")

    # Set Author details
    post.community_id = id
    post.user_id = current_user['id']
    post.username = current_user['username']
    post.user_role = current_user.get('role', 'member')
    post.user_avatar = current_user.get('profile_picture')
    
    # Validate Product Fields
    if post.type == 'product':
        if not post.product_price or not post.product_name:
             raise HTTPException(status_code=400, detail="Product posts must have price and name")
    
    db.community_posts.insert_one(post.dict())
    return post

@router.delete("/posts/{post_id}")
def delete_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a post or mark it unavailable (Admin/Creator only)"""
    post = db.community_posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Check permissions (Author or Admin)
    is_author = post['user_id'] == current_user['id']
    is_admin = current_user.get('role') == 'admin'
    
    if not (is_author or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        
    db.community_posts.delete_one({"id": post_id})
    return {"message": "Post deleted"}

# --- Interactions ---

@router.post("/posts/{post_id}/like")
def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Toggle like on a post"""
    user_id = current_user['id']
    post = db.community_posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if user_id in post.get('likes', []):
        # Unlike
        db.community_posts.update_one(
            {"id": post_id},
            {"$pull": {"likes": user_id}}
        )
        action = "unliked"
    else:
        # Like
        db.community_posts.update_one(
            {"id": post_id},
            {"$addToSet": {"likes": user_id}}
        )
        action = "liked"
        
    return {"message": f"Post {action}"}

@router.put("/posts/{post_id}")
def update_post(post_id: str, updates: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """
    Update a post or product listing.
    Allows updating content, price, name, and availability status.
    """
    post = db.community_posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Check permissions (Author or Admin)
    is_author = post['user_id'] == current_user['id']
    is_admin = current_user.get('role') == 'admin'
    
    if not (is_author or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
    
    # Allowed fields to update
    allowed_fields = ['content', 'product_name', 'product_price', 'is_available', 'status'] # added status for 'preorder' logic if needed
    update_data = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    # If updating to 'preorder' or changing availability, handle it here
    # 'status' field in updates could be 'available', 'unavailable', 'preorder' mapping to is_available logic or new field
    # For now, we map 'status' to is_available boolean strictly or keep it flexible.
    # Let's support an explicit 'product_status' field if provided, or fallback to is_available
    
    db.community_posts.update_one(
        {"id": post_id},
        {"$set": update_data}
    )
    
    return {"message": "Post updated", "changes": update_data}

@router.post("/posts/{post_id}/comments", response_model=Comment)
def add_comment(post_id: str, comment: Comment, current_user: dict = Depends(get_current_user)):
    """Add a comment to a post"""
    comment.user_id = current_user['id']
    comment.username = current_user['username']
    comment.user_avatar = current_user.get('profile_picture')
    
    db.community_posts.update_one(
        {"id": post_id},
        {"$push": {"comments": comment.dict()}}
    )
    return comment

@router.put("/comments/{post_id}/{comment_id}")
def edit_comment(post_id: str, comment_id: str, content: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Edit a specific comment within a post"""
    post = db.community_posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Find the comment to verify ownership
    # MongoDB array filtering is complex for "find specific item in array and check field" in one go safely without aggregation
    # We'll pull the post and check python side for simplicity in MVP, or use array filter update query
    
    # We need to ensure only the comment author can edit.
    # Using arrayFilters is the atomic way.
    
    # First, verify ownership (optional but recommended before write)
    target_comment = next((c for c in post.get('comments', []) if c['id'] == comment_id), None)
    if not target_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    if target_comment['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")

    db.community_posts.update_one(
        {"id": post_id, "comments.id": comment_id},
        {"$set": {"comments.$.content": content.get("content")}}
    )
    
    return {"message": "Comment updated"}
