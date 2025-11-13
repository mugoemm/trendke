# How to Use Supabase - Quick Guide

## 1. Access Supabase Dashboard

1. Go to **https://supabase.com**
2. Click **Sign In** (top right)
3. Log in with your account credentials

## 2. Select Your Project

After logging in, you'll see your projects list. Click on your **TrendKe** project.

## 3. Run SQL to Fix Likes/Comments

### Option A: SQL Editor (Recommended)
1. In the left sidebar, click **SQL Editor** (icon looks like `</>`)
2. Click **+ New query** button
3. Copy and paste this SQL:

```sql
-- Fix for likes and comments
CREATE OR REPLACE FUNCTION increment_likes(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos 
  SET likes_count = likes_count + 1 
  WHERE id = video_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION decrement_likes(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos 
  SET likes_count = GREATEST(likes_count - 1, 0) 
  WHERE id = video_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION increment_comments(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos 
  SET comments_count = comments_count + 1 
  WHERE id = video_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

4. Click **RUN** button (or press `Ctrl + Enter`)
5. You should see "Success. No rows returned" - this is good!

### Option B: Database → Functions (Alternative)
1. Click **Database** in left sidebar
2. Click **Functions** tab
3. Click **Create a new function**
4. Paste the function code

## 4. Verify Functions Were Created

Run this query to check:

```sql
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
  AND routine_name LIKE '%increment%' 
  OR routine_name LIKE '%decrement%';
```

You should see:
- `increment_likes`
- `decrement_likes`
- `increment_comments`

## 5. Other Useful Supabase Features

### View Your Tables
1. Click **Table Editor** in left sidebar
2. You'll see all your tables: `videos`, `users`, `video_likes`, `video_comments`, etc.
3. Click any table to view/edit data

### Check Database Structure
1. Click **Database** in left sidebar
2. Click **Tables** to see table schemas
3. Click **Functions** to see all SQL functions
4. Click **Extensions** to enable features like `uuid-ossp`

### View API Logs
1. Click **Logs** in left sidebar
2. See all API requests and errors

### Get Connection Info
1. Click **Settings** (bottom of left sidebar)
2. Click **Database**
3. You'll see:
   - Host
   - Database name
   - Port
   - User
   - Password
   - Connection string

### API Keys
1. Click **Settings** → **API**
2. You'll see:
   - `anon` key (for frontend)
   - `service_role` key (for backend - keep secret!)
   - API URL

## 6. Your Current Setup

Based on your `.env` file, you have:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_or_service_key
```

These are used by your Python backend to connect to Supabase.

## Common Supabase Tasks

### Add Data Manually
1. **Table Editor** → Select table → **Insert row**
2. Fill in the fields → **Save**

### Delete Data
1. **Table Editor** → Select table → Check rows → **Delete**

### Run Custom Queries
1. **SQL Editor** → Type your query → **RUN**

Example:
```sql
-- Count all videos
SELECT COUNT(*) FROM videos;

-- Get all videos by a user
SELECT * FROM videos WHERE user_id = 'user-uuid-here';

-- Check likes count
SELECT id, title, likes_count, comments_count FROM videos;
```

### Enable Row Level Security (RLS)
1. **Authentication** → **Policies**
2. Select table → **New Policy**
3. Define who can read/write

### View Realtime Subscriptions
1. **Database** → **Replication**
2. Enable tables for realtime updates

## Troubleshooting

### "Function not found" error
- Make sure you ran the SQL in the correct project
- Check **Database** → **Functions** to verify they exist
- Try refreshing the schema cache: Click **Database** → **Schema** → **Reload schema**

### "Permission denied" error
- Your API key might not have permissions
- Check if you're using `service_role` key for backend operations
- Check RLS policies aren't blocking your requests

### Connection timeout
- Check your internet connection
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check if your IP is blocked (Supabase → Settings → Database → Network restrictions)

## Quick Fix for Your Current Issue

Run this ONE command in SQL Editor:

```sql
CREATE OR REPLACE FUNCTION increment_likes(video_id UUID) RETURNS void AS $$ BEGIN UPDATE videos SET likes_count = likes_count + 1 WHERE id = video_id; END; $$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION decrement_likes(video_id UUID) RETURNS void AS $$ BEGIN UPDATE videos SET likes_count = GREATEST(likes_count - 1, 0) WHERE id = video_id; END; $$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION increment_comments(video_id UUID) RETURNS void AS $$ BEGIN UPDATE videos SET comments_count = comments_count + 1 WHERE id = video_id; END; $$ LANGUAGE plpgsql SECURITY DEFINER;
```

Click **RUN** and you're done! Your likes and comments will work immediately.

## Need Help?

- Supabase Docs: https://supabase.com/docs
- SQL Tutorial: https://supabase.com/docs/guides/database
- Functions Guide: https://supabase.com/docs/guides/database/functions
- Support: https://supabase.com/support

---

**After running the SQL, refresh your TrendKe app and try liking/commenting again!**
