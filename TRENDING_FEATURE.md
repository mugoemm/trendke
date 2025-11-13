# Automated Trending Videos Feature

## Overview
Your app now automatically fetches and ranks trending videos every 15 minutes, even after deployment!

## How It Works

### 1. **Trending Algorithm**
Videos are scored based on:
- **Views**: 1 point per view (last 24 hours)
- **Likes**: 3 points per like
- **Comments**: 5 points per comment
- **Recency**: Only videos from last 24 hours

Formula: `score = (views × 1) + (likes × 3) + (comments × 5)`

### 2. **Background Scheduler**
- Runs automatically every **15 minutes**
- Calculates top 50 trending videos
- Caches results for fast API response
- Runs even after deployment (no manual intervention needed)

### 3. **API Endpoint**
```
GET /videos/trending/videos?limit=50
```

Returns cached trending videos sorted by score.

## Installation

### Step 1: Install APScheduler
```bash
cd backend
pip install apscheduler
```

### Step 2: Restart Backend
The scheduler starts automatically on server startup.

### Step 3: Test It
```bash
# Call the trending endpoint
curl http://127.0.0.1:8000/videos/trending/videos
```

## Frontend Integration

### Update API Service
```javascript
// src/api/videoApi.js
export const getTrendingVideos = async (limit = 50) => {
  const response = await api.get(`/videos/trending/videos?limit=${limit}`);
  return response.data;
};
```

### Use in Explore Page
```javascript
// src/pages/Explore.jsx
import { getTrendingVideos } from '../api/videoApi';

function Explore() {
  const [trendingVideos, setTrendingVideos] = useState([]);

  useEffect(() => {
    const fetchTrending = async () => {
      const videos = await getTrendingVideos(20);
      setTrendingVideos(videos);
    };
    fetchTrending();
    
    // Refresh every 15 minutes
    const interval = setInterval(fetchTrending, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>🔥 Trending Now</h2>
      {trendingVideos.map(video => (
        <VideoCard key={video.id} video={video} />
      ))}
    </div>
  );
}
```

## Deployment Considerations

### For Production

1. **Adjust Update Frequency**
   - Edit `trending_scheduler.py` line 78
   - Change from 15 minutes to your preferred interval
   ```python
   self.scheduler.add_job(
       self.calculate_trending_videos,
       'interval',
       minutes=30,  # Change to 30, 60, etc.
       id='trending_update',
       replace_existing=True
   )
   ```

2. **Database Optimization**
   - Add indexes to `videos` table for faster queries:
   ```sql
   CREATE INDEX idx_videos_created_at ON videos(created_at DESC);
   CREATE INDEX idx_videos_views ON videos(views_count DESC);
   ```

3. **Caching Strategy**
   - Current: In-memory cache (resets on server restart)
   - Production: Use Redis for persistent cache
   ```python
   import redis
   r = redis.Redis(host='localhost', port=6379, db=0)
   r.set('trending_videos', json.dumps(videos))
   ```

4. **Monitor Performance**
   - Check logs for scheduler activity
   - Look for: "✅ Trending videos updated: X videos at..."
   - If slow, reduce calculation frequency or optimize query

## Benefits After Deployment

✅ **No Manual Work**: Trending updates automatically  
✅ **Fast Response**: Cached results = instant API response  
✅ **Real-time Rankings**: Videos trend based on actual engagement  
✅ **Scalable**: Works on any hosting platform (Heroku, AWS, DigitalOcean)  
✅ **Resilient**: Falls back to regular feed if scheduler fails  

## Testing Locally

1. Upload 5-10 test videos
2. Like/comment on some videos
3. Wait 15 minutes (or restart backend to trigger immediate calculation)
4. Call `/videos/trending/videos` endpoint
5. Check logs for: "📊 Trending scheduler started"

## Example Response
```json
[
  {
    "id": "vid_123",
    "title": "Amazing Dance Video",
    "trending_score": 87,
    "views_count": 25,
    "likes_count": 12,
    "comments_count": 8,
    "video_url": "https://...",
    "user": { "username": "dancer123" }
  }
]
```

## Customization Options

### Change Trending Time Window
Edit `trending_scheduler.py` line 32:
```python
# From 24 hours to 48 hours
time_threshold = (datetime.now() - timedelta(hours=48)).isoformat()
```

### Adjust Score Weights
Edit `trending_scheduler.py` line 52:
```python
# Give more weight to comments
score = (views * 1) + (likes * 5) + (comments * 10)
```

### Change Top Videos Count
Edit `trending_scheduler.py` line 60:
```python
# Get top 100 instead of 50
trending = sorted(scored_videos, key=lambda x: x["trending_score"], reverse=True)[:100]
```

## Troubleshooting

**Scheduler not starting?**
- Check logs for "📊 Trending scheduler started"
- Verify APScheduler installed: `pip list | grep APScheduler`

**Empty trending results?**
- Upload at least 1 video with engagement (views/likes/comments)
- Wait 5 seconds after server starts (initial calculation delay)

**Slow calculation?**
- Add database indexes (see Deployment section)
- Reduce trending time window (24h → 12h)
- Decrease top videos count (50 → 20)

