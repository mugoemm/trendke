-- =====================================================
-- ENHANCED LIVE STREAMING WITH MULTI-GUEST SUPPORT
-- Better than TikTok Live - Multiple co-hosts, guest management, etc.
-- =====================================================

-- 1. LIVE PARTICIPANTS TABLE (Guests/Co-hosts)
-- =====================================================
CREATE TABLE IF NOT EXISTS live_participants (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES live_sessions(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(20) DEFAULT 'viewer' CHECK (role IN ('host', 'cohost', 'guest', 'viewer')),
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'muted', 'kicked', 'left')),
  audio_enabled BOOLEAN DEFAULT true,
  video_enabled BOOLEAN DEFAULT true,
  screen_sharing BOOLEAN DEFAULT false,
  joined_at TIMESTAMP DEFAULT NOW(),
  left_at TIMESTAMP,
  UNIQUE(session_id, user_id)
);

CREATE INDEX idx_live_participants_session ON live_participants(session_id);
CREATE INDEX idx_live_participants_user ON live_participants(user_id);
CREATE INDEX idx_live_participants_role ON live_participants(role);

-- 2. LIVE GUEST REQUESTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS live_guest_requests (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES live_sessions(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  request_type VARCHAR(20) DEFAULT 'guest' CHECK (request_type IN ('guest', 'cohost')),
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
  message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  responded_at TIMESTAMP,
  responded_by UUID REFERENCES users(id),
  UNIQUE(session_id, user_id, request_type)
);

CREATE INDEX idx_guest_requests_session ON live_guest_requests(session_id);
CREATE INDEX idx_guest_requests_status ON live_guest_requests(status);

-- 3. LIVE CHAT MESSAGES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS live_chat_messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES live_sessions(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  message TEXT NOT NULL,
  message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'gift', 'system', 'sticker')),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_live_chat_session ON live_chat_messages(session_id);
CREATE INDEX idx_live_chat_created ON live_chat_messages(created_at DESC);

-- 4. LIVE SESSION SETTINGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS live_session_settings (
  session_id UUID PRIMARY KEY REFERENCES live_sessions(id) ON DELETE CASCADE,
  allow_guests BOOLEAN DEFAULT true,
  require_approval BOOLEAN DEFAULT true,
  max_guests INTEGER DEFAULT 8 CHECK (max_guests > 0 AND max_guests <= 20),
  enable_chat BOOLEAN DEFAULT true,
  enable_gifts BOOLEAN DEFAULT true,
  chat_slow_mode INTEGER DEFAULT 0,
  guest_audio_default BOOLEAN DEFAULT true,
  guest_video_default BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 5. LIVE REACTIONS TABLE (Hearts, emojis during live)
-- =====================================================
CREATE TABLE IF NOT EXISTS live_reactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES live_sessions(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  reaction_type VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_live_reactions_session ON live_reactions(session_id);

-- 6. UPDATE live_sessions table with new fields
-- =====================================================
ALTER TABLE live_sessions ADD COLUMN IF NOT EXISTS room_name VARCHAR(255);
ALTER TABLE live_sessions ADD COLUMN IF NOT EXISTS webrtc_room_id VARCHAR(255);
ALTER TABLE live_sessions ADD COLUMN IF NOT EXISTS recording_enabled BOOLEAN DEFAULT false;
ALTER TABLE live_sessions ADD COLUMN IF NOT EXISTS recording_url TEXT;
ALTER TABLE live_sessions ADD COLUMN IF NOT EXISTS guest_count INTEGER DEFAULT 0;
ALTER TABLE live_sessions ADD COLUMN IF NOT EXISTS total_gifts_received INTEGER DEFAULT 0;
ALTER TABLE live_sessions ADD COLUMN IF NOT EXISTS peak_viewers INTEGER DEFAULT 0;

-- 7. FUNCTIONS FOR AUTO-UPDATING COUNTS
-- =====================================================

-- Function to update guest count
CREATE OR REPLACE FUNCTION update_guest_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.role IN ('guest', 'cohost') AND NEW.status = 'active' THEN
        UPDATE live_sessions 
        SET guest_count = guest_count + 1 
        WHERE id = NEW.session_id;
    ELSIF TG_OP = 'UPDATE' AND OLD.status = 'active' AND NEW.status != 'active' AND NEW.role IN ('guest', 'cohost') THEN
        UPDATE live_sessions 
        SET guest_count = GREATEST(guest_count - 1, 0) 
        WHERE id = NEW.session_id;
    ELSIF TG_OP = 'DELETE' AND OLD.role IN ('guest', 'cohost') AND OLD.status = 'active' THEN
        UPDATE live_sessions 
        SET guest_count = GREATEST(guest_count - 1, 0) 
        WHERE id = OLD.session_id;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger for guest count
DROP TRIGGER IF EXISTS live_participants_guest_count_trigger ON live_participants;
CREATE TRIGGER live_participants_guest_count_trigger
AFTER INSERT OR UPDATE OR DELETE ON live_participants
FOR EACH ROW EXECUTE FUNCTION update_guest_count();

-- Function to update peak viewers
CREATE OR REPLACE FUNCTION update_peak_viewers()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.viewer_count > COALESCE(NEW.peak_viewers, 0) THEN
        NEW.peak_viewers = NEW.viewer_count;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for peak viewers
DROP TRIGGER IF EXISTS live_sessions_peak_viewers_trigger ON live_sessions;
CREATE TRIGGER live_sessions_peak_viewers_trigger
BEFORE UPDATE ON live_sessions
FOR EACH ROW EXECUTE FUNCTION update_peak_viewers();

-- 8. ROW LEVEL SECURITY (RLS) - Optional but recommended
-- =====================================================
ALTER TABLE live_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_guest_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_session_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_reactions ENABLE ROW LEVEL SECURITY;

-- Allow users to read all participants
CREATE POLICY "Users can view participants" ON live_participants
FOR SELECT USING (true);

-- Allow hosts to manage participants
CREATE POLICY "Hosts can manage participants" ON live_participants
FOR ALL USING (
    EXISTS (
        SELECT 1 FROM live_sessions 
        WHERE id = session_id AND host_id = auth.uid()
    )
);

-- Allow users to request to join
CREATE POLICY "Users can create guest requests" ON live_guest_requests
FOR INSERT WITH CHECK (user_id = auth.uid());

-- Allow users to view their own requests
CREATE POLICY "Users can view their requests" ON live_guest_requests
FOR SELECT USING (user_id = auth.uid() OR EXISTS (
    SELECT 1 FROM live_sessions WHERE id = session_id AND host_id = auth.uid()
));

-- Allow hosts to respond to requests
CREATE POLICY "Hosts can respond to requests" ON live_guest_requests
FOR UPDATE USING (EXISTS (
    SELECT 1 FROM live_sessions WHERE id = session_id AND host_id = auth.uid()
));

-- Allow everyone to read chat messages
CREATE POLICY "Everyone can read chat" ON live_chat_messages
FOR SELECT USING (true);

-- Allow authenticated users to send messages
CREATE POLICY "Users can send messages" ON live_chat_messages
FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- Allow everyone to send reactions
CREATE POLICY "Everyone can react" ON live_reactions
FOR ALL USING (auth.uid() IS NOT NULL);

-- =====================================================
-- VIEWS FOR EASY QUERYING
-- =====================================================

-- View for active live sessions with guest info
CREATE OR REPLACE VIEW live_sessions_with_guests AS
SELECT 
    ls.*,
    u.username as host_username,
    u.avatar_url as host_avatar_url,
    COUNT(DISTINCT lp.id) FILTER (WHERE lp.role IN ('guest', 'cohost') AND lp.status = 'active') as active_guests,
    COUNT(DISTINCT lgr.id) FILTER (WHERE lgr.status = 'pending') as pending_requests
FROM live_sessions ls
LEFT JOIN users u ON ls.host_id = u.id
LEFT JOIN live_participants lp ON ls.id = lp.session_id
LEFT JOIN live_guest_requests lgr ON ls.id = lgr.session_id
GROUP BY ls.id, u.username, u.avatar_url;

-- =====================================================
-- SAMPLE DATA INSERTION (Optional - for testing)
-- =====================================================

-- Insert default session settings for existing sessions
INSERT INTO live_session_settings (session_id)
SELECT id FROM live_sessions 
WHERE id NOT IN (SELECT session_id FROM live_session_settings)
ON CONFLICT (session_id) DO NOTHING;
