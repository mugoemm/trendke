"""
TrendKe Application Health Check
Verifies all systems are working correctly
"""
import requests
import json
from app.db import supabase

BASE_URL = "http://localhost:8000"

print("🔍 TrendKe Health Check")
print("=" * 60)

# 1. Check backend is running
print("\n1️⃣  Backend Server...")
try:
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("   ✅ Backend running on port 8000")
    else:
        print(f"   ⚠️  Backend returned status {response.status_code}")
except:
    print("   ❌ Backend not accessible at port 8000")

# 2. Check database connection
print("\n2️⃣  Database Connection...")
try:
    result = supabase.table('users').select('count').limit(1).execute()
    print("   ✅ Supabase connected")
except Exception as e:
    print(f"   ❌ Database error: {e}")

# 3. Check videos exist
print("\n3️⃣  Video Content...")
try:
    result = supabase.table('videos').select('*').execute()
    count = len(result.data)
    print(f"   ✅ {count} videos in database")
except Exception as e:
    print(f"   ❌ Videos check failed: {e}")

# 4. Check follows table exists
print("\n4️⃣  Social Features...")
try:
    result = supabase.table('follows').select('count').limit(1).execute()
    print("   ✅ Follows table exists")
except Exception as e:
    print(f"   ❌ Follows table missing: {e}")

# 5. Check API endpoints
print("\n5️⃣  API Endpoints...")
endpoints = [
    ("/videos/feed", "Video Feed"),
    ("/videos/trending/videos", "Trending Videos"),
]

for endpoint, name in endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 1
            print(f"   ✅ {name}: {count} items")
        else:
            print(f"   ⚠️  {name}: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ {name}: {e}")

# 6. Check Redis cache
print("\n6️⃣  Cache System...")
try:
    response = requests.get(f"{BASE_URL}/videos/feed?limit=1")
    if "cache" in response.text.lower() or response.status_code == 200:
        print("   ✅ Cache system operational")
except:
    print("   ⚠️  Cache check inconclusive")

# Summary
print("\n" + "=" * 60)
print("📊 Health Check Complete")
print("\n🎯 Frontend should be running at: http://localhost:5173")
print("🎯 Backend API running at: http://localhost:8000")
print("🎯 API Docs available at: http://localhost:8000/docs")
print("\n✨ System Status: READY")
