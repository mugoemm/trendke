-- =====================================================
-- TRENDKE DATABASE SCHEMA FOR SUPABASE
-- =====================================================
-- Copy this entire file and paste it into Supabase SQL Editor
-- Then click "Run" to create all tables and functions
-- =====================================================

-- =====================================================
-- 1. USERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
  full_name VARCHAR(255),
  password_hash VARCHAR(255) NOT NULL,
  avatar_url TEXT,
  bio TEXT,
  role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'creator', 'admin')),
  coin_balance INTEGER DEFAULT 0 CHECK (coin_balance >= 0),
  total_earnings DECIMAL(10,2) DEFAULT 0 CHECK (total_earnings >= 0),
  followers_count INTEGER DEFAULT 0 CHECK (followers_count >= 0),
  following_count INTEGER DEFAULT 0 CHECK (following_count >= 0),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- =====================================================
-- 2. VIDEOS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS videos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  video_url TEXT NOT NULL,
  thumbnail_url TEXT,
  hashtags TEXT[],
  views_count INTEGER DEFAULT 0 CHECK (views_count >= 0),
  likes_count INTEGER DEFAULT 0 CHECK (likes_count >= 0),
  comments_count INTEGER DEFAULT 0 CHECK (comments_count >= 0),
  shares_count INTEGER DEFAULT 0 CHECK (shares_count >= 0),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_hashtags ON videos USING GIN(hashtags);

-- =====================================================
-- 3. VIDEO LIKES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS video_likes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(video_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_video_likes_video_id ON video_likes(video_id);
CREATE INDEX IF NOT EXISTS idx_video_likes_user_id ON video_likes(user_id);

-- =====================================================
-- 4. VIDEO COMMENTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS video_comments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  comment TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_video_comments_video_id ON video_comments(video_id);
CREATE INDEX IF NOT EXISTS idx_video_comments_created_at ON video_comments(created_at DESC);

-- =====================================================
-- 5. LIVE SESSIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS live_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  host_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  session_type VARCHAR(20) NOT NULL CHECK (session_type IN ('voice', 'camera', 'studio')),
  status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'active', 'ended')),
  thumbnail_url TEXT,
  access_token TEXT,
  viewer_count INTEGER DEFAULT 0 CHECK (viewer_count >= 0),
  max_participants INTEGER DEFAULT 50 CHECK (max_participants > 0),
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_sessions_host_id ON live_sessions(host_id);
CREATE INDEX IF NOT EXISTS idx_live_sessions_status ON live_sessions(status);
CREATE INDEX IF NOT EXISTS idx_live_sessions_started_at ON live_sessions(started_at DESC);

-- =====================================================
-- 6. GIFT TYPES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS gift_types (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  emoji VARCHAR(10),
  coin_cost INTEGER NOT NULL CHECK (coin_cost > 0),
  animation_url TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default gifts with emojis
INSERT INTO gift_types (name, emoji, coin_cost) VALUES
  ('Rose', '🌹', 10),
  ('Heart', '❤️', 50),
  ('Star', '⭐', 100),
  ('Fire', '🔥', 200),
  ('Crown', '👑', 500),
  ('Diamond', '💎', 1000),
  ('Rocket', '🚀', 2000)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- 7. GIFT TRANSACTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS gift_transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
  recipient_id UUID REFERENCES users(id) ON DELETE SET NULL,
  gift_type_id UUID REFERENCES gift_types(id),
  video_id UUID REFERENCES videos(id) ON DELETE SET NULL,
  live_session_id UUID REFERENCES live_sessions(id) ON DELETE SET NULL,
  coin_amount INTEGER NOT NULL CHECK (coin_amount > 0),
  creator_earnings DECIMAL(10,2) NOT NULL CHECK (creator_earnings >= 0),
  platform_fee DECIMAL(10,2) NOT NULL CHECK (platform_fee >= 0),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gift_transactions_sender_id ON gift_transactions(sender_id);
CREATE INDEX IF NOT EXISTS idx_gift_transactions_recipient_id ON gift_transactions(recipient_id);
CREATE INDEX IF NOT EXISTS idx_gift_transactions_created_at ON gift_transactions(created_at DESC);

-- =====================================================
-- 8. COIN PACKAGES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS coin_packages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  coin_amount INTEGER NOT NULL CHECK (coin_amount > 0),
  price_usd DECIMAL(10,2) NOT NULL CHECK (price_usd > 0),
  bonus_percentage INTEGER DEFAULT 0 CHECK (bonus_percentage >= 0),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default coin packages
INSERT INTO coin_packages (name, coin_amount, price_usd, bonus_percentage) VALUES
  ('Starter Pack', 100, 0.99, 0),
  ('Popular Pack', 500, 4.99, 10),
  ('Value Pack', 1200, 9.99, 20),
  ('Premium Pack', 2500, 19.99, 25),
  ('Ultimate Pack', 6500, 49.99, 30)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 9. PAYMENT TRANSACTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS payment_transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  package_id UUID REFERENCES coin_packages(id),
  amount_usd DECIMAL(10,2) NOT NULL,
  coins_purchased INTEGER NOT NULL,
  payment_provider VARCHAR(50),
  transaction_id VARCHAR(255),
  status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_id ON payment_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status);

-- =====================================================
-- 10. NOTIFICATIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS notifications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT,
  data JSONB,
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

-- =====================================================
-- 11. FOLLOWS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS follows (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  follower_id UUID REFERENCES users(id) ON DELETE CASCADE,
  following_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(follower_id, following_id),
  CHECK (follower_id != following_id)
);

CREATE INDEX IF NOT EXISTS idx_follows_follower_id ON follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_follows_following_id ON follows(following_id);

-- =====================================================
-- 12. DATABASE FUNCTIONS
-- =====================================================

-- Function to increment video views
CREATE OR REPLACE FUNCTION increment_views(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos 
  SET views_count = views_count + 1 
  WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;

-- Function to update video likes count
CREATE OR REPLACE FUNCTION update_video_likes_count()
RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE videos SET likes_count = likes_count + 1 WHERE id = NEW.video_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE videos SET likes_count = likes_count - 1 WHERE id = OLD.video_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger for video likes
DROP TRIGGER IF EXISTS video_likes_count_trigger ON video_likes;
CREATE TRIGGER video_likes_count_trigger
AFTER INSERT OR DELETE ON video_likes
FOR EACH ROW EXECUTE FUNCTION update_video_likes_count();

-- Function to update comments count
CREATE OR REPLACE FUNCTION update_video_comments_count()
RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE videos SET comments_count = comments_count + 1 WHERE id = NEW.video_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE videos SET comments_count = comments_count - 1 WHERE id = OLD.video_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger for comments count
DROP TRIGGER IF EXISTS video_comments_count_trigger ON video_comments;
CREATE TRIGGER video_comments_count_trigger
AFTER INSERT OR DELETE ON video_comments
FOR EACH ROW EXECUTE FUNCTION update_video_comments_count();

-- Function to update follower/following counts
CREATE OR REPLACE FUNCTION update_follow_counts()
RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE users SET followers_count = followers_count + 1 WHERE id = NEW.following_id;
    UPDATE users SET following_count = following_count + 1 WHERE id = NEW.follower_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE users SET followers_count = followers_count - 1 WHERE id = OLD.following_id;
    UPDATE users SET following_count = following_count - 1 WHERE id = OLD.follower_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger for follow counts
DROP TRIGGER IF EXISTS follow_counts_trigger ON follows;
CREATE TRIGGER follow_counts_trigger
AFTER INSERT OR DELETE ON follows
FOR EACH ROW EXECUTE FUNCTION update_follow_counts();

-- =====================================================
-- 13. ROW LEVEL SECURITY (RLS) - Optional but Recommended
-- =====================================================
-- Uncomment these if you want to enable RLS for additional security

-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE video_likes ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE video_comments ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- SETUP COMPLETE!
-- =====================================================
-- All tables, indexes, and functions have been created.
-- You can now use the TrendKe backend with this database.
-- =====================================================
