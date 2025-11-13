"""
Social features: Follow/Unfollow, Follower Feed
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from .auth import get_current_user
from .db import supabase
from .models import UserProfile
from .websocket_manager import notify_new_follower

router = APIRouter(prefix="/social", tags=["Social"])


@router.post("/follow/{user_id}")
async def follow_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Follow a user"""
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself"
        )
    
    try:
        # Check if already following
        existing = supabase.table("follows").select("*").eq(
            "follower_id", current_user["id"]
        ).eq("following_id", user_id).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already following this user"
            )
        
        # Create follow relationship
        supabase.table("follows").insert({
            "follower_id": current_user["id"],
            "following_id": user_id,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        # Update follower/following counts
        # Increment target user's followers_count
        supabase.rpc("increment_followers", {"user_id": user_id}).execute()
        
        # Increment current user's following_count
        supabase.rpc("increment_following", {"user_id": current_user["id"]}).execute()
        
        # Send WebSocket notification to followed user
        await notify_new_follower(
            user_id=user_id,
            follower_username=current_user["username"],
            follower_avatar=current_user.get("avatar_url")
        )
        
        return {
            "message": "Successfully followed user",
            "following": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error following user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to follow user"
        )


@router.delete("/unfollow/{user_id}")
async def unfollow_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Unfollow a user"""
    try:
        # Delete follow relationship
        result = supabase.table("follows").delete().eq(
            "follower_id", current_user["id"]
        ).eq("following_id", user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not following this user"
            )
        
        # Decrement counts
        supabase.rpc("decrement_followers", {"user_id": user_id}).execute()
        supabase.rpc("decrement_following", {"user_id": current_user["id"]}).execute()
        
        return {
            "message": "Successfully unfollowed user",
            "following": False
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error unfollowing user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unfollow user"
        )


@router.get("/is-following/{user_id}")
async def check_following(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Check if current user is following another user"""
    try:
        result = supabase.table("follows").select("*").eq(
            "follower_id", current_user["id"]
        ).eq("following_id", user_id).execute()
        
        return {
            "following": len(result.data) > 0
        }
    
    except Exception as e:
        print(f"Error checking follow status: {e}")
        return {"following": False}


@router.get("/followers/{user_id}")
async def get_followers(
    user_id: str,
    limit: int = 50,
    offset: int = 0
):
    """Get list of users following this user"""
    try:
        result = supabase.table("follows").select("""
            follower_id,
            users!follows_follower_id_fkey (
                id, username, avatar_url, full_name
            )
        """).eq("following_id", user_id).range(offset, offset + limit - 1).execute()
        
        followers = []
        for item in result.data:
            user = item.get("users", {})
            followers.append({
                "id": user.get("id"),
                "username": user.get("username"),
                "avatar_url": user.get("avatar_url"),
                "full_name": user.get("full_name")
            })
        
        return followers
    
    except Exception as e:
        print(f"Error fetching followers: {e}")
        return []


@router.get("/following/{user_id}")
async def get_following(
    user_id: str,
    limit: int = 50,
    offset: int = 0
):
    """Get list of users this user is following"""
    try:
        result = supabase.table("follows").select("""
            following_id,
            users!follows_following_id_fkey (
                id, username, avatar_url, full_name
            )
        """).eq("follower_id", user_id).range(offset, offset + limit - 1).execute()
        
        following = []
        for item in result.data:
            user = item.get("users", {})
            following.append({
                "id": user.get("id"),
                "username": user.get("username"),
                "avatar_url": user.get("avatar_url"),
                "full_name": user.get("full_name")
            })
        
        return following
    
    except Exception as e:
        print(f"Error fetching following: {e}")
        return []


@router.get("/feed/following")
async def get_following_feed(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get video feed from users you follow"""
    try:
        # Get list of users current user follows
        following_result = supabase.table("follows").select(
            "following_id"
        ).eq("follower_id", current_user["id"]).execute()
        
        following_ids = [f["following_id"] for f in following_result.data]
        
        if not following_ids:
            return []
        
        # Get videos from followed users
        videos_result = supabase.table("videos").select("""
            *,
            users!videos_user_id_fkey (username, avatar_url)
        """).in_("user_id", following_ids).order(
            "created_at", desc=True
        ).range(offset, offset + limit - 1).execute()
        
        return videos_result.data
    
    except Exception as e:
        print(f"Error fetching following feed: {e}")
        return []
