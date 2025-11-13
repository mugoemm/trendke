"""
Automated trending videos updater
Runs periodically to calculate and cache trending videos
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
from .db import supabase

class TrendingScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.cache = {
            "trending_videos": [],
            "last_updated": None
        }
    
    async def calculate_trending_videos(self) -> List[Dict]:
        """
        Calculate trending videos based on:
        - Recent views (last 24 hours)
        - Like ratio
        - Comment activity
        - Share count
        """
        try:
            # Time window: last 24 hours
            time_threshold = (datetime.now() - timedelta(hours=24)).isoformat()
            
            # Fetch videos with engagement metrics from existing schema
            response = supabase.table("videos").select(
                """
                id, title, video_url, thumbnail_url, created_at, user_id,
                views_count, likes_count, comments_count, shares_count,
                users!videos_user_id_fkey (username, avatar_url)
                """
            ).gte("created_at", time_threshold).execute()
            
            videos = response.data if response.data else []
            
            # Calculate trending score for each video
            scored_videos = []
            for video in videos:
                views = video.get("views_count", 0)
                likes = video.get("likes_count", 0)
                comments = video.get("comments_count", 0)
                shares = video.get("shares_count", 0)
                
                # Trending algorithm
                # Weight: views * 1 + likes * 3 + comments * 5 + shares * 2
                score = (views * 1) + (likes * 3) + (comments * 5) + (shares * 2)
                
                video["trending_score"] = score
                scored_videos.append(video)
            
            # Sort by score and get top 50
            trending = sorted(scored_videos, key=lambda x: x["trending_score"], reverse=True)[:50]
            
            # Update in-memory cache
            self.cache["trending_videos"] = trending
            self.cache["last_updated"] = datetime.now()
            
            # Also update Redis cache if available
            try:
                from .redis_cache import cache as redis_cache
                if redis_cache.enabled:
                    # Convert to serializable format
                    from .models import VideoMetadata
                    serializable_trending = []
                    for video in trending:
                        user_data = video.get("users", {})
                        serializable_trending.append(VideoMetadata(
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
                        ).dict())
                    await redis_cache.set_trending_videos(serializable_trending, expire=900)
            except Exception as cache_error:
                print(f"⚠️  Could not update Redis cache: {cache_error}")
            
            print(f"✅ Trending videos updated: {len(trending)} videos at {datetime.now()}")
            return trending
            
        except Exception as e:
            print(f"❌ Error calculating trending videos: {e}")
            return self.cache["trending_videos"]  # Return cached data on error
    
    def get_cached_trending(self) -> List[Dict]:
        """Get cached trending videos"""
        return self.cache["trending_videos"]
    
    def start(self):
        """Start the scheduler"""
        # Run every 15 minutes
        self.scheduler.add_job(
            self.calculate_trending_videos,
            'interval',
            minutes=15,
            id='trending_update',
            replace_existing=True
        )
        
        # Also run at startup
        self.scheduler.add_job(
            self.calculate_trending_videos,
            'date',
            run_date=datetime.now() + timedelta(seconds=5)
        )
        
        self.scheduler.start()
        print("📊 Trending scheduler started (updates every 15 minutes)")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print("📊 Trending scheduler stopped")

# Global instance
trending_scheduler = TrendingScheduler()
