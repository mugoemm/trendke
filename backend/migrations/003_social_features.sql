-- Social Features Migration: Follow/Unfollow System
-- Run this SQL in your Supabase SQL Editor

-- Create follows table
CREATE TABLE IF NOT EXISTS follows (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  follower_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  following_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(follower_id, following_id),
  CHECK (follower_id != following_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_follows_follower ON follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_follows_following ON follows(following_id);
CREATE INDEX IF NOT EXISTS idx_follows_created ON follows(created_at DESC);

-- Function to increment followers count
CREATE OR REPLACE FUNCTION increment_followers(user_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE users 
  SET followers_count = followers_count + 1 
  WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to decrement followers count
CREATE OR REPLACE FUNCTION decrement_followers(user_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE users 
  SET followers_count = GREATEST(0, followers_count - 1)
  WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to increment following count
CREATE OR REPLACE FUNCTION increment_following(user_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE users 
  SET following_count = following_count + 1 
  WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to decrement following count
CREATE OR REPLACE FUNCTION decrement_following(user_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE users 
  SET following_count = GREATEST(0, following_count - 1)
  WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;

-- Test the setup (optional)
SELECT 'Social features migration completed successfully!' AS status;
