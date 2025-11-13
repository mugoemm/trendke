"""
Seed database with demo videos after deployment
Run once: python seed_videos.py
"""
import os
from dotenv import load_dotenv
from supabase import create_client
import uuid
from datetime import datetime, timedelta
import random

load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Demo videos (publicly available sample videos)
DEMO_VIDEOS = [
    {
        "title": "Amazing Dance Performance",
        "description": "Check out this incredible dance routine! 💃🕺",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerBlazes.jpg",
        "hashtags": ["dance", "performance", "trending"]
    },
    {
        "title": "Skateboarding Tricks",
        "description": "Epic skateboarding skills 🛹",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerEscapes.jpg",
        "hashtags": ["skateboarding", "sports", "extreme"]
    },
    {
        "title": "Cute Animals Compilation",
        "description": "The cutest animals you'll see today! 🐶🐱",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
        "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerFun.jpg",
        "hashtags": ["animals", "cute", "pets"]
    },
    {
        "title": "Cooking Tutorial",
        "description": "Learn to make the perfect dish! 👨‍🍳",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
        "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerJoyrides.jpg",
        "hashtags": ["cooking", "food", "tutorial"]
    },
    {
        "title": "Travel Vlog - Nairobi",
        "description": "Exploring the beautiful city of Nairobi 🌍",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
        "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerMeltdowns.jpg",
        "hashtags": ["travel", "nairobi", "kenya"]
    },
    {
        "title": "Comedy Skit",
        "description": "This will make your day! 😂",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
        "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/Sintel.jpg",
        "hashtags": ["comedy", "funny", "entertainment"]
    },
    {
        "title": "Fitness Workout",
        "description": "Get fit with this 10-minute workout! 💪",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg",
        "hashtags": ["fitness", "workout", "health"]
    },
    {
        "title": "Music Cover",
        "description": "My cover of a popular song 🎵",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ElephantsDream.jpg",
        "hashtags": ["music", "cover", "singing"]
    },
    {
        "title": "Gaming Highlights",
        "description": "Best gaming moments of the week! 🎮",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/TearsOfSteel.jpg",
        "hashtags": ["gaming", "highlights", "esports"]
    },
    {
        "title": "Fashion Lookbook",
        "description": "My outfit ideas for this season 👗",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4",
        "thumbnail_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/VolkswagenGTIReview.jpg",
        "hashtags": ["fashion", "style", "outfit"]
    }
]

def seed_videos():
    """Seed database with demo videos"""
    try:
        # Get first user or create demo user
        users_response = supabase.table("users").select("*").limit(1).execute()
        
        if not users_response.data:
            print("❌ No users found. Please create at least one user first.")
            print("   Run: python -c \"from app.db import supabase; supabase.auth.sign_up({'email': 'demo@example.com', 'password': 'demo123456'})\"")
            return
        
        demo_user = users_response.data[0]
        print(f"📦 Using user: {demo_user['username']} ({demo_user['id']})")
        
        # Insert demo videos
        videos_created = 0
        for video_data in DEMO_VIDEOS:
            # Random engagement metrics
            views_count = random.randint(50, 5000)
            likes_count = random.randint(10, int(views_count * 0.3))
            comments_count = random.randint(0, int(views_count * 0.1))
            shares_count = random.randint(0, int(views_count * 0.05))
            
            # Random created_at (within last 7 days)
            days_ago = random.randint(0, 7)
            created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            video_record = {
                "id": str(uuid.uuid4()),
                "user_id": demo_user["id"],
                "title": video_data["title"],
                "description": video_data["description"],
                "video_url": video_data["video_url"],
                "thumbnail_url": video_data["thumbnail_url"],
                "hashtags": video_data["hashtags"],
                "views_count": views_count,
                "likes_count": likes_count,
                "comments_count": comments_count,
                "shares_count": shares_count,
                "created_at": created_at
            }
            
            try:
                supabase.table("videos").insert(video_record).execute()
                videos_created += 1
                print(f"✅ Created: {video_data['title']} ({views_count} views, {likes_count} likes)")
            except Exception as e:
                print(f"⚠️  Failed to create {video_data['title']}: {e}")
        
        print(f"\n🎉 Successfully seeded {videos_created} demo videos!")
        print(f"🔥 Trending scheduler will rank them automatically every 15 minutes")
        
    except Exception as e:
        print(f"❌ Error seeding videos: {e}")

if __name__ == "__main__":
    print("🌱 Seeding database with demo videos...\n")
    seed_videos()
