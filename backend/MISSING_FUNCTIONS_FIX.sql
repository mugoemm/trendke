-- ============================================
-- TrendKe: Missing Database Functions Fix
-- Run this in Supabase SQL Editor
-- ============================================

-- Function: Increment video likes count
CREATE OR REPLACE FUNCTION increment_likes(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos 
  SET likes_count = likes_count + 1 
  WHERE id = video_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Decrement video likes count
CREATE OR REPLACE FUNCTION decrement_likes(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos 
  SET likes_count = GREATEST(likes_count - 1, 0) 
  WHERE id = video_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Increment video comments count
CREATE OR REPLACE FUNCTION increment_comments(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos 
  SET comments_count = comments_count + 1 
  WHERE id = video_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Increment video views count
CREATE OR REPLACE FUNCTION increment_views(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos 
  SET views_count = views_count + 1 
  WHERE id = video_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Increment video shares count
CREATE OR REPLACE FUNCTION increment_shares(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos 
  SET shares_count = shares_count + 1 
  WHERE id = video_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Verify functions were created
SELECT 
  routine_name,
  routine_type
FROM information_schema.routines
WHERE routine_schema = 'public' 
  AND routine_name LIKE '%increment%' OR routine_name LIKE '%decrement%'
ORDER BY routine_name;
