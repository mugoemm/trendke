"""Quick script to check database contents"""
from app.db import supabase

print("\n🔍 Checking database contents...\n")

# Check users
try:
    users = supabase.table("users").select("id, email, username").limit(5).execute()
    print(f"✅ Users found: {len(users.data)}")
    for user in users.data:
        print(f"   - {user['username']} ({user['email']})")
except Exception as e:
    print(f"❌ Error fetching users: {e}")

# Check videos
try:
    videos = supabase.table("videos").select("id, title, user_id").limit(5).execute()
    print(f"\n✅ Videos found: {len(videos.data)}")
    for video in videos.data:
        print(f"   - {video['title']}")
except Exception as e:
    print(f"❌ Error fetching videos: {e}")

print("\n")
