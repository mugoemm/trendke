"""
Import videos from external source (example: YouTube API, TikTok API, etc.)
Customize this based on your video source
"""
import os
import requests
from dotenv import load_dotenv
from supabase import create_client
import uuid

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def import_from_youtube_api(channel_id: str, api_key: str, user_id: str):
    """
    Example: Import videos from YouTube channel
    Requires: YouTube Data API key
    """
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=20"
    
    response = requests.get(url)
    data = response.json()
    
    for item in data.get("items", []):
        if item["id"]["kind"] == "youtube#video":
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            video_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": snippet["title"],
                "description": snippet["description"],
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail_url": snippet["thumbnails"]["high"]["url"],
                "hashtags": extract_hashtags(snippet["description"]),
                "views_count": 0,
                "likes_count": 0,
                "comments_count": 0,
                "shares_count": 0
            }
            
            supabase.table("videos").insert(video_record).execute()
            print(f"✅ Imported: {snippet['title']}")

def extract_hashtags(text: str):
    """Extract hashtags from text"""
    import re
    return re.findall(r'#(\w+)', text)

# Usage:
# import_from_youtube_api("UC_x5XG1OV2P6uZZ5FSM9Ttw", "YOUR_API_KEY", "user_id_here")
