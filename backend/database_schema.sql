# Supabase Database Schema SQL

Run this SQL in your Supabase SQL Editor to create all required tables and functions.

## Tables

### Users
```sql
CREATE TABLE users (
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

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

### Videos
```sql
CREATE TABLE videos (
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

CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_created_at ON videos(created_at DESC);
CREATE INDEX idx_videos_hashtags ON videos USING GIN(hashtags);
```

### Live Sessions
```sql
CREATE TABLE live_sessions (
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

CREATE INDEX idx_live_sessions_host_id ON live_sessions(host_id);
CREATE INDEX idx_live_sessions_status ON live_sessions(status);
CREATE INDEX idx_live_sessions_started_at ON live_sessions(started_at DESC);
```

### Gift Types
```sql
CREATE TABLE gift_types (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  icon_url TEXT,
  coin_cost INTEGER NOT NULL CHECK (coin_cost > 0),
  animation_url TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default gifts
INSERT INTO gift_types (name, coin_cost) VALUES
  ('Rose', 10),
  ('Heart', 50),
  ('Star', 100),
  ('Crown', 500),
  ('Diamond', 1000),
  ('Rocket', 2000);
```

### Gift Transactions
```sql
CREATE TABLE gift_transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  sender_id UUID REFERENCES users(id),
  recipient_id UUID REFERENCES users(id),
  gift_type_id UUID REFERENCES gift_types(id),
  amount INTEGER DEFAULT 1 CHECK (amount > 0),
  total_coins INTEGER NOT NULL CHECK (total_coins > 0),
  creator_earnings DECIMAL(10,2) NOT NULL CHECK (creator_earnings >= 0),
  platform_fee DECIMAL(10,2) NOT NULL CHECK (platform_fee >= 0),
  video_id UUID REFERENCES videos(id),
  live_session_id UUID REFERENCES live_sessions(id),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_gift_transactions_sender ON gift_transactions(sender_id);
CREATE INDEX idx_gift_transactions_recipient ON gift_transactions(recipient_id);
CREATE INDEX idx_gift_transactions_created_at ON gift_transactions(created_at DESC);
```

### Video Likes
```sql
CREATE TABLE video_likes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, video_id)
);

CREATE INDEX idx_video_likes_user_id ON video_likes(user_id);
CREATE INDEX idx_video_likes_video_id ON video_likes(video_id);
```

### Video Comments
```sql
CREATE TABLE video_comments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_video_comments_video_id ON video_comments(video_id);
CREATE INDEX idx_video_comments_created_at ON video_comments(created_at DESC);
```

### Notifications
```sql
CREATE TABLE notifications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  data JSONB,
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(user_id, read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
```

### Payment Transactions
```sql
CREATE TABLE payment_transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  coin_package_id VARCHAR(50) NOT NULL,
  amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
  currency VARCHAR(10) NOT NULL,
  payment_method VARCHAR(20) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payment_transactions_user_id ON payment_transactions(user_id);
CREATE INDEX idx_payment_transactions_status ON payment_transactions(status);
```

## Database Functions

### Increment Video Views
```sql
CREATE OR REPLACE FUNCTION increment_views(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos SET views_count = views_count + 1 WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;
```

### Increment Video Likes
```sql
CREATE OR REPLACE FUNCTION increment_likes(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos SET likes_count = likes_count + 1 WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;
```

### Decrement Video Likes
```sql
CREATE OR REPLACE FUNCTION decrement_likes(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos SET likes_count = GREATEST(likes_count - 1, 0) WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;
```

### Increment Comments
```sql
CREATE OR REPLACE FUNCTION increment_comments(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos SET comments_count = comments_count + 1 WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;
```

## Row Level Security (Optional for Production)

Enable RLS and create policies for secure multi-tenant access:

```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_comments ENABLE ROW LEVEL SECURITY;

-- Users can read all profiles
CREATE POLICY "Users can view all profiles"
  ON users FOR SELECT
  USING (true);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id);

-- Videos are publicly readable
CREATE POLICY "Videos are publicly readable"
  ON videos FOR SELECT
  USING (true);

-- Users can insert their own videos
CREATE POLICY "Users can insert own videos"
  ON videos FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Similar policies for other tables...
```

## Verification

After running the SQL, verify the schema:

```sql
-- Check tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check functions
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_type = 'FUNCTION';

-- Count records in gift_types
SELECT COUNT(*) FROM gift_types;
```
