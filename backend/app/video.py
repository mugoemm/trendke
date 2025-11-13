from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from typing import Optional, List
from datetime import datetime
import uuid
import os

from .models import VideoUpload, VideoMetadata, VideoComment, VideoCommentResponse
from .db import db, supabase
from .auth import get_current_user, get_current_user_optional

# Try to import video upload service
try:
    from .video_upload import VideoUploadService
    HAS_CLOUDINARY_MODULE = True
except ImportError:
    HAS_CLOUDINARY_MODULE = False
    print("ℹ️  Cloudinary not available. Install: pip install cloudinary")

# Try to import Redis cache
try:
    from .redis_cache import cache
    HAS_REDIS_CACHE = True
except ImportError:
    HAS_REDIS_CACHE = False

router = APIRouter(prefix="/videos", tags=["Videos"])


def is_cloudinary_configured() -> bool:
    """Check if Cloudinary is configured at runtime"""
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    api_key = os.getenv("CLOUDINARY_API_KEY", "")
    api_secret = os.getenv("CLOUDINARY_API_SECRET", "")
    return (HAS_CLOUDINARY_MODULE and 
            cloud_name and api_key and api_secret and
            "your-" not in cloud_name)


@router.post("/upload", response_model=VideoMetadata)
async def upload_video(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    hashtags: Optional[str] = Form(None),  # Comma-separated
    video_file: UploadFile = File(...),
    thumbnail: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload video with metadata
    Automatically uses Cloudinary if configured, otherwise demo URL
    """
    try:
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        
        # Parse hashtags
        hashtag_list = []
        if hashtags:
            hashtag_list = [tag.strip() for tag in hashtags.split(",")]
        
        # Try to upload to Cloudinary if configured
        if is_cloudinary_configured():
            try:
                print(f"📤 Uploading video to Cloudinary for user {current_user['username']}...")
                upload_result = await VideoUploadService.upload_video(
                    video_file=video_file,
                    user_id=current_user["id"],
                    title=title,
                    public_id=video_id
                )
                video_url = upload_result["video_url"]
                thumbnail_url = upload_result["thumbnail_url"]
                print(f"✅ Video uploaded successfully: {video_url}")
            except Exception as e:
                print(f"⚠️  Cloudinary upload failed: {e}. Using demo URL.")
                video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
                thumbnail_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg"
        else:
            # Fallback to demo URL
            print("ℹ️  Using demo video URL (Cloudinary not configured)")
            print(f"    Cloud Name: {os.getenv('CLOUDINARY_CLOUD_NAME', 'NOT SET')}")
            print(f"    API Key: {os.getenv('CLOUDINARY_API_KEY', 'NOT SET')}")
            print(f"    Module loaded: {HAS_CLOUDINARY_MODULE}")
            video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            thumbnail_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg"
        
        # Create video metadata
        video_data = {
            "id": video_id,
            "user_id": current_user["id"],
            "title": title,
            "description": description,
            "video_url": video_url,
            "thumbnail_url": thumbnail_url,
            "hashtags": hashtag_list,
            "views_count": 0,
            "likes_count": 0,
            "comments_count": 0,
            "shares_count": 0
        }
        
        created_video = db.create_video(video_data)
        if not created_video:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create video"
            )
        
        # Broadcast new video upload to all connected users
        try:
            from .websocket_manager import broadcast_new_video
            await broadcast_new_video(
                uploader_id=current_user["id"],
                uploader_username=current_user["username"],
                video_id=created_video["id"],
                video_title=created_video["title"],
                thumbnail_url=created_video.get("thumbnail_url", "")
            )
        except Exception as e:
            print(f"⚠️  Failed to broadcast new video: {e}")
        
        return VideoMetadata(
            id=created_video["id"],
            user_id=created_video["user_id"],
            title=created_video["title"],
            description=created_video.get("description"),
            video_url=created_video["video_url"],
            thumbnail_url=created_video.get("thumbnail_url"),
            hashtags=created_video.get("hashtags", []),
            views_count=created_video.get("views_count", 0),
            likes_count=created_video.get("likes_count", 0),
            comments_count=created_video.get("comments_count", 0),
            shares_count=created_video.get("shares_count", 0),
            created_at=created_video["created_at"],
            username=current_user["username"],
            avatar_url=current_user.get("avatar_url")
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/feed", response_model=List[VideoMetadata])
async def get_video_feed(
    limit: int = 20,
    offset: int = 0,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Get video feed with pagination and trending sorting"""
    user_id = current_user["id"] if current_user else None
    
    # Try to get from cache first
    if HAS_REDIS_CACHE:
        cached_feed = await cache.get_video_feed(user_id, limit, offset)
        if cached_feed:
            print(f"✅ Cache HIT: feed ({len(cached_feed)} videos)")
            return cached_feed
    
    # Cache miss - fetch from database
    print(f"⚠️  Cache MISS: feed - fetching from DB")
    videos = db.get_videos_feed(limit=limit, offset=offset, user_id=user_id)
    
    result = []
    for video in videos:
        user_data = video.get("users", {})
        result.append(VideoMetadata(
            id=video["id"],
            user_id=video["user_id"],
            title=video["title"],
            description=video.get("description"),
            video_url=video["video_url"],
            thumbnail_url=video.get("thumbnail_url"),
            hashtags=video.get("hashtags", []),
            views_count=video.get("views_count", 0),
            likes_count=video.get("likes_count", 0),
            comments_count=video.get("comments_count", 0),
            shares_count=video.get("shares_count", 0),
            created_at=video["created_at"],
            username=user_data.get("username"),
            avatar_url=user_data.get("avatar_url")
        ))
    
    # Cache the result
    if HAS_REDIS_CACHE and result:
        await cache.set_video_feed(user_id, limit, offset, [v.dict() for v in result], expire=300)
        print(f"💾 Cached feed: {len(result)} videos (5 min TTL)")
    
    return result


@router.get("/trending/videos", response_model=List[VideoMetadata])
async def get_trending_videos(
    limit: int = 50,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get trending videos from cache (updated every 15 minutes)
    Falls back to recent videos if scheduler not available
    """
    # Try Redis cache first
    if HAS_REDIS_CACHE:
        cached_trending = await cache.get_trending_videos()
        if cached_trending:
            print(f"✅ Cache HIT: trending videos ({len(cached_trending)} videos)")
            return cached_trending[:limit]
    
    try:
        # Try to get from trending scheduler cache
        from .trending_scheduler import trending_scheduler
        cached_trending = trending_scheduler.get_cached_trending()
        
        if cached_trending:
            # Format cached trending videos
            result = []
            for video in cached_trending[:limit]:
                user_data = video.get("users", {})
                result.append(VideoMetadata(
                    id=video["id"],
                    user_id=video["user_id"],
                    title=video["title"],
                    description=video.get("description"),
                    video_url=video["video_url"],
                    thumbnail_url=video.get("thumbnail_url"),
                    hashtags=video.get("hashtags", []),
                    views_count=video.get("views_count", 0),
                    likes_count=video.get("likes_count", 0),
                    comments_count=video.get("comments_count", 0),
                    shares_count=video.get("shares_count", 0),
                    created_at=video["created_at"],
                    username=user_data.get("username"),
                    avatar_url=user_data.get("avatar_url")
                ))
            return result
    except ImportError:
        pass  # Scheduler not available, fallback to regular feed
    
    # Fallback: Return recent videos sorted by engagement
    videos = db.get_videos_feed(limit=limit, offset=0, user_id=current_user["id"] if current_user else None)
    
    result = []
    for video in videos:
        user_data = video.get("users", {})
        result.append(VideoMetadata(
            id=video["id"],
            user_id=video["user_id"],
            title=video["title"],
            description=video.get("description"),
            video_url=video["video_url"],
            thumbnail_url=video.get("thumbnail_url"),
            hashtags=video.get("hashtags", []),
            views_count=video.get("views_count", 0),
            likes_count=video.get("likes_count", 0),
            comments_count=video.get("comments_count", 0),
            shares_count=video.get("shares_count", 0),
            created_at=video["created_at"],
            username=user_data.get("username"),
            avatar_url=user_data.get("avatar_url")
        ))
    
    return result


@router.get("/{video_id}", response_model=VideoMetadata)
async def get_video_details(video_id: str):
    """Get video details by ID"""
    video = db.get_video_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Increment view count
    db.increment_video_views(video_id)
    
    user_data = video.get("users", {})
    return VideoMetadata(
        id=video["id"],
        user_id=video["user_id"],
        title=video["title"],
        description=video.get("description"),
        video_url=video["video_url"],
        thumbnail_url=video.get("thumbnail_url"),
        hashtags=video.get("hashtags", []),
        views_count=video.get("views_count", 0) + 1,  # Incremented
        likes_count=video.get("likes_count", 0),
        comments_count=video.get("comments_count", 0),
        shares_count=video.get("shares_count", 0),
        created_at=video["created_at"],
        username=user_data.get("username"),
        avatar_url=user_data.get("avatar_url")
    )


@router.post("/{video_id}/like")
async def like_video(video_id: str, current_user: dict = Depends(get_current_user)):
    """Like/unlike a video"""
    try:
        print(f"🔍 Like request - video_id: {video_id}, user_id: {current_user['id']}")
        
        # Check if already liked
        existing_like = supabase.table("video_likes").select("*").eq(
            "video_id", video_id
        ).eq("user_id", current_user["id"]).execute()
        
        print(f"🔍 Existing like: {existing_like.data}")
        
        if existing_like.data:
            # Unlike
            print(f"🔓 Unliking video...")
            supabase.table("video_likes").delete().eq("video_id", video_id).eq(
                "user_id", current_user["id"]
            ).execute()
            
            # Update likes count directly (fallback if RPC function doesn't exist)
            try:
                supabase.rpc("decrement_likes", {"video_id": video_id}).execute()
            except Exception as rpc_error:
                print(f"⚠️  RPC failed, updating count directly: {rpc_error}")
                # Get current video
                video = supabase.table("videos").select("likes_count").eq("id", video_id).single().execute()
                new_count = max(0, video.data["likes_count"] - 1)
                supabase.table("videos").update({"likes_count": new_count}).eq("id", video_id).execute()
            
            print(f"✅ Video unliked successfully")
            return {"liked": False}
        else:
            # Like
            print(f"❤️  Liking video...")
            insert_result = supabase.table("video_likes").insert({
                "video_id": video_id,
                "user_id": current_user["id"]
            }).execute()
            print(f"🔍 Insert result: {insert_result.data}")
            
            # Update likes count directly (fallback if RPC function doesn't exist)
            try:
                rpc_result = supabase.rpc("increment_likes", {"video_id": video_id}).execute()
                print(f"🔍 RPC result: {rpc_result.data}")
            except Exception as rpc_error:
                print(f"⚠️  RPC failed, updating count directly: {rpc_error}")
                # Get current video
                video = supabase.table("videos").select("likes_count").eq("id", video_id).single().execute()
                new_count = video.data["likes_count"] + 1
                supabase.table("videos").update({"likes_count": new_count}).eq("id", video_id).execute()
            
            # Get video info and notify owner (optional WebSocket)
            try:
                video = db.get_video_by_id(video_id)
                if video and video["user_id"] != current_user["id"]:
                    try:
                        from .websocket_manager import notify_new_like
                        await notify_new_like(
                            user_id=video["user_id"],
                            video_id=video_id,
                            liker_username=current_user["username"],
                            video_title=video["title"]
                        )
                    except Exception as ws_error:
                        print(f"⚠️  WebSocket notification failed: {ws_error}")
            except Exception as notify_error:
                print(f"⚠️  Notification error (non-critical): {notify_error}")
            
            print(f"✅ Video liked successfully")
            return {"liked": True}
    
    except Exception as e:
        print(f"❌ Error in like_video: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to like video: {str(e)}"
        )


@router.get("/{video_id}/comments", response_model=List[VideoCommentResponse])
async def get_video_comments(video_id: str, limit: int = 50):
    """Get comments for a video"""
    try:
        response = supabase.table("video_comments").select("""
            *,
            users!video_comments_user_id_fkey (username, avatar_url)
        """).eq("video_id", video_id).order("created_at", desc=True).limit(limit).execute()
        
        print(f"🔍 Fetched {len(response.data)} comments for video {video_id}")
        
        comments = []
        for comment in response.data:
            user_data = comment.get("users", {})
            comments.append(VideoCommentResponse(
                id=comment["id"],
                video_id=comment["video_id"],
                user_id=comment["user_id"],
                username=user_data.get("username", ""),
                avatar_url=user_data.get("avatar_url"),
                content=comment["comment"],  # Database column is 'comment', not 'content'
                created_at=comment["created_at"]
            ))
        
        return comments
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch comments: {str(e)}"
        )


@router.post("/{video_id}/comment", response_model=VideoCommentResponse)
async def add_comment(
    video_id: str,
    comment: VideoComment,
    current_user: dict = Depends(get_current_user)
):
    """Add a comment to a video"""
    try:
        print(f"🔍 Comment request - video_id: {video_id}, user_id: {current_user['id']}, content: {comment.content}")
        
        comment_data = {
            "video_id": video_id,
            "user_id": current_user["id"],
            "comment": comment.content  # Database column is 'comment', not 'content'
        }
        
        print(f"🔍 Inserting comment...")
        response = supabase.table("video_comments").insert(comment_data).execute()
        created_comment = response.data[0]
        print(f"🔍 Comment inserted: {created_comment['id']}")
        
        # Increment comment count (with fallback if RPC doesn't exist)
        print(f"🔍 Incrementing comment count...")
        try:
            rpc_result = supabase.rpc("increment_comments", {"video_id": video_id}).execute()
            print(f"🔍 RPC result: {rpc_result.data}")
        except Exception as rpc_error:
            print(f"⚠️  RPC failed, updating count directly: {rpc_error}")
            # Get current video
            video = supabase.table("videos").select("comments_count").eq("id", video_id).single().execute()
            new_count = video.data["comments_count"] + 1
            supabase.table("videos").update({"comments_count": new_count}).eq("id", video_id).execute()
            print(f"✅ Updated comments count to {new_count}")
        
        # Notify video owner of new comment (optional WebSocket)
        try:
            video = db.get_video_by_id(video_id)
            if video and video["user_id"] != current_user["id"]:
                try:
                    from .websocket_manager import notify_new_comment
                    await notify_new_comment(
                        user_id=video["user_id"],
                        video_id=video_id,
                        commenter_username=current_user["username"],
                        comment=comment.content,
                        video_title=video["title"]
                    )
                except Exception as ws_error:
                    print(f"⚠️  WebSocket notification failed: {ws_error}")
        except Exception as notify_error:
            print(f"⚠️  Notification error (non-critical): {notify_error}")
        
        # Get username from database if not in token
        username = current_user.get("username")
        avatar_url = current_user.get("avatar_url")
        
        if not username:
            try:
                user_data = supabase.table("users").select("username, avatar_url").eq("id", current_user["id"]).single().execute()
                username = user_data.data.get("username", "Unknown User")
                avatar_url = user_data.data.get("avatar_url")
            except Exception as user_error:
                print(f"⚠️  Could not fetch username: {user_error}")
                username = "Unknown User"
        
        print(f"✅ Comment added successfully")
        return VideoCommentResponse(
            id=created_comment["id"],
            video_id=created_comment["video_id"],
            user_id=created_comment["user_id"],
            username=username,
            avatar_url=avatar_url,
            content=created_comment["comment"],  # Database column is 'comment', not 'content'
            created_at=created_comment["created_at"]
        )
    
    except Exception as e:
        print(f"❌ Error in add_comment: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}"
        )
        
        return VideoCommentResponse(
            id=created_comment["id"],
            video_id=created_comment["video_id"],
            user_id=created_comment["user_id"],
            username=current_user["username"],
            avatar_url=current_user.get("avatar_url"),
            content=created_comment["comment"],  # Database column is 'comment', not 'content'
            created_at=created_comment["created_at"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}"
        )
