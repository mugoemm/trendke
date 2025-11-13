from app.db import supabase

# Remove the Big Buck Bunny demo video
demo_video_id = '9a272039-c5d9-4726-ba0e-67765983af12'

try:
    result = supabase.table('videos').delete().eq('id', demo_video_id).execute()
    if result.data:
        print(f"✅ Successfully deleted demo video (Big Buck Bunny)")
        print(f"   Video ID: {demo_video_id}")
    else:
        print("❌ Demo video not found or already deleted")
except Exception as e:
    print(f"❌ Error deleting demo video: {e}")
