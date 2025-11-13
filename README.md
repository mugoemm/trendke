# TrendKe - Social Media Platform with Live Streaming & Gifting

A TikTok-style social media platform built with React and FastAPI, featuring video feeds, live streaming (voice/camera/studio modes), and a creator monetization system through virtual gifts.

## 🚀 Features

### Core Features
- 📹 **Vertical Video Feed** - TikTok-style scrolling video feed
- 🎥 **Video Upload** - Upload videos with titles, descriptions, and hashtags
- ❤️ **Engagement** - Like, comment, and share videos
- 👤 **User Profiles** - Personal profiles with video grids

### Live Streaming
- 🎤 **Voice Only** - Audio-only live sessions
- 📷 **Camera Mode** - Video live streaming
- 🎬 **Studio Mode** - Multi-guest live sessions
- 💬 **Live Chat** - Real-time chat during streams

### Monetization
- 🎁 **Virtual Gifts** - Send gifts to creators during videos or live streams
- 💰 **Coin System** - Purchase coins to send gifts
- 📊 **Creator Dashboard** - Track earnings and analytics
- 💳 **Payment Integration** - PesaPal & Stripe for coin purchases
- **Revenue Split:** 80% to creators, 20% platform fee

## 🏗️ Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Authentication:** JWT tokens
- **Payments:** PesaPal (Kenya) & Stripe
- **Storage:** Google Drive (MVP) / CDN (Production)

### Frontend
- **Framework:** React 18
- **Routing:** React Router v6
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **HTTP Client:** Axios
- **UI Components:** React Icons, React Hot Toast

### Live Streaming
- **WebRTC:** LiveKit (recommended)
- **Alternatives:** Janus Gateway, Jitsi Meet
- **Real-time:** Supabase Realtime for chat & notifications

## 📁 Project Structure

```
trendke/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── models.py            # Pydantic models
│   │   ├── db.py                # Supabase helpers
│   │   ├── auth.py              # Authentication
│   │   ├── video.py             # Video endpoints
│   │   ├── live.py              # Live streaming
│   │   ├── gifts.py             # Gifts & coins
│   │   ├── notifications.py     # Push notifications
│   │   └── payments.py          # Payment processing
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client modules
│   │   ├── components/          # React components
│   │   │   ├── VideoFeed.jsx
│   │   │   ├── VideoPlayer.jsx
│   │   │   ├── LiveRoom.jsx
│   │   │   ├── GiftButton.jsx
│   │   │   ├── UploadVideo.jsx
│   │   │   └── Navbar.jsx
│   │   ├── pages/               # Page components
│   │   │   ├── Home.jsx
│   │   │   ├── Profile.jsx
│   │   │   ├── CreatorDashboard.jsx
│   │   │   └── Login.jsx
│   │   ├── styles/
│   │   │   └── tailwind.css
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json
│   └── .env.example
│
├── live-server/                 # WebRTC server config
│   ├── README.md
│   └── config/
│
├── README.md
└── .gitignore
```

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Supabase account
- LiveKit account (or alternative WebRTC server)

### 1. Database Setup (Supabase)

Create a new Supabase project and run the following SQL:

```sql
-- Users table
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
  full_name VARCHAR(255),
  password_hash VARCHAR(255) NOT NULL,
  avatar_url TEXT,
  bio TEXT,
  role VARCHAR(20) DEFAULT 'user',
  coin_balance INTEGER DEFAULT 0,
  total_earnings DECIMAL(10,2) DEFAULT 0,
  followers_count INTEGER DEFAULT 0,
  following_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Videos table
CREATE TABLE videos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  video_url TEXT NOT NULL,
  thumbnail_url TEXT,
  hashtags TEXT[],
  views_count INTEGER DEFAULT 0,
  likes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,
  shares_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Live sessions table
CREATE TABLE live_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  host_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  session_type VARCHAR(20) NOT NULL,
  status VARCHAR(20) DEFAULT 'scheduled',
  thumbnail_url TEXT,
  access_token TEXT,
  viewer_count INTEGER DEFAULT 0,
  max_participants INTEGER DEFAULT 50,
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Gift types table
CREATE TABLE gift_types (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  icon_url TEXT,
  coin_cost INTEGER NOT NULL,
  animation_url TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Gift transactions table
CREATE TABLE gift_transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  sender_id UUID REFERENCES users(id),
  recipient_id UUID REFERENCES users(id),
  gift_type_id UUID REFERENCES gift_types(id),
  amount INTEGER DEFAULT 1,
  total_coins INTEGER NOT NULL,
  creator_earnings DECIMAL(10,2) NOT NULL,
  platform_fee DECIMAL(10,2) NOT NULL,
  video_id UUID REFERENCES videos(id),
  live_session_id UUID REFERENCES live_sessions(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Video likes table
CREATE TABLE video_likes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, video_id)
);

-- Video comments table
CREATE TABLE video_comments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Notifications table
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

-- Payment transactions table
CREATE TABLE payment_transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  coin_package_id VARCHAR(50) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(10) NOT NULL,
  payment_method VARCHAR(20) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default gift types
INSERT INTO gift_types (name, icon_url, coin_cost) VALUES
  ('Rose', '🌹', 10),
  ('Heart', '❤️', 50),
  ('Star', '⭐', 100),
  ('Crown', '👑', 500),
  ('Diamond', '💎', 1000);

-- Create database functions
CREATE OR REPLACE FUNCTION increment_views(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos SET views_count = views_count + 1 WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION increment_likes(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos SET likes_count = likes_count + 1 WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrement_likes(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos SET likes_count = likes_count - 1 WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION increment_comments(video_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE videos SET comments_count = comments_count + 1 WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env
# Edit .env with your API URL

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 4. LiveKit Setup (Recommended)

1. Sign up at [LiveKit Cloud](https://livekit.io/)
2. Create a new project
3. Get API key and secret
4. Update backend `.env`:
   ```
   LIVEKIT_API_KEY=your_key
   LIVEKIT_API_SECRET=your_secret
   LIVEKIT_WS_URL=wss://your-project.livekit.cloud
   ```

See `live-server/README.md` for alternative WebRTC servers.

## 📱 API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user
- `GET /auth/user/{user_id}` - Get user profile

### Videos
- `GET /videos/feed` - Get video feed
- `GET /videos/{video_id}` - Get video details
- `POST /videos/upload` - Upload video
- `POST /videos/{video_id}/like` - Like/unlike video
- `GET /videos/{video_id}/comments` - Get comments
- `POST /videos/{video_id}/comment` - Add comment

### Live Streaming
- `POST /live/start` - Start live session
- `POST /live/join` - Join live session
- `POST /live/{session_id}/end` - End session
- `GET /live/list` - Get active sessions

### Gifts & Coins
- `GET /gifts/types` - Get gift types
- `POST /gifts/send` - Send gift
- `GET /gifts/balance` - Get coin balance
- `GET /gifts/leaderboard` - Get top creators

### Payments
- `GET /payments/packages` - Get coin packages
- `POST /payments/purchase/initiate` - Start purchase
- `POST /payments/callback/pesapal` - PesaPal callback
- `POST /payments/callback/stripe` - Stripe callback

## 🚀 Deployment

### Free-Tier Hosting Strategy

| Component | Platform | Cost |
|-----------|----------|------|
| Frontend | Vercel | Free |
| Backend | Railway/Render | Free tier |
| Database | Supabase | Free tier |
| Live Streaming | LiveKit Cloud | Free tier (10k mins/mo) |
| Video Storage | Google Drive | Free (15 GB) |

### Backend Deployment (Railway)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Frontend Deployment (Vercel)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel
```

### Environment Variables

**Backend (.env):**
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
JWT_SECRET_KEY=your_secret_key
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
PESAPAL_CONSUMER_KEY=your_pesapal_key
PESAPAL_CONSUMER_SECRET=your_pesapal_secret
STRIPE_SECRET_KEY=your_stripe_key
```

**Frontend (.env):**
```
VITE_API_URL=https://your-backend.railway.app
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
VITE_LIVEKIT_URL=wss://your-livekit.cloud
```

## 🌍 Production Deployment (Render & Vercel)

### Backend (FastAPI) on Render

- **Render Config:** See `backend/render.yaml` for service definition and environment variables.
- **Environment Variables:** Copy `backend/.env.example` to `.env` and fill in your secrets. Render will use these as environment variables.
- **CORS:**
  - The backend reads allowed CORS origin from the `CORS_ORIGIN` environment variable (set to your frontend URL in production, e.g., `https://your-frontend.vercel.app`).
  - For local dev, set `CORS_ORIGIN=http://localhost:3000`.
- **Health Check:**
  - Endpoint: `GET /healthz` (returns `{ "status": "ok" }`)
  - Used by Render for service health monitoring.
- **Startup:**
  - Render runs: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
  - Local dev: `uvicorn app.main:app --reload` (port from `.env` or default 8000)
- **.env Loading:**
  - In production (Render), env vars are injected by the platform.
  - In local/dev, `.env` is loaded automatically if present.

### Frontend (Vite/React) on Vercel

- **Vercel Config:**
  - Deploy the `frontend` folder to Vercel.
  - Use `.env.production` for production environment variables (see `frontend/.env.example`).
- **API URL:**
  - Set `VITE_API_URL` in `.env.production` to your deployed backend URL (e.g., `https://your-backend.onrender.com`).
  - For local dev, use `VITE_API_URL=http://localhost:8000`.
- **.env Usage:**
  - Vercel automatically loads `.env.production` for production builds.
  - For local dev, copy `.env.example` to `.env` and edit as needed.

### Example `.env` Files

**backend/.env.example**
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
JWT_SECRET_KEY=your_secret_key
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
PESAPAL_CONSUMER_KEY=your_pesapal_key
PESAPAL_CONSUMER_SECRET=your_pesapal_secret
STRIPE_SECRET_KEY=your_stripe_key
CORS_ORIGIN=http://localhost:3000
```

**frontend/.env.example**
```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
VITE_LIVEKIT_URL=wss://your-livekit.cloud
```

**frontend/.env.production**
```
VITE_API_URL=https://your-backend.onrender.com
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
VITE_LIVEKIT_URL=wss://your-livekit.cloud
```

---

## 🛡️ Notes
- **CORS:** Always set `CORS_ORIGIN` to your frontend’s deployed URL in production for security.
- **Health Endpoint:** Use `/healthz` for uptime checks and Render health monitoring.
- **.env:** Never commit real `.env` files with secrets to version control. Use `.env.example` for documentation.
- **Production URLs:** Update all URLs in `.env.production` and Render environment settings before going live.

---

## 🔐 Security Considerations

- ✅ JWT authentication with secure secret keys
- ✅ Password hashing with bcrypt
- ✅ CORS configuration for production
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (Supabase client)
- ⚠️ Implement rate limiting (production)
- ⚠️ Add HTTPS for production
- ⚠️ Secure file upload validation

## 📈 Scaling Considerations

### MVP (0-1000 users)
- Free tier services
- Single server
- Google Drive storage

### Growth (1k-10k users)
- Upgrade to paid tiers
- CDN for video delivery (CloudFlare)
- Redis for caching
- Load balancing

### Scale (10k+ users)
- Microservices architecture
- Kubernetes deployment
- Dedicated video transcoding
- Multiple CDN regions

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- FastAPI for the amazing Python web framework
- React for the frontend library
- Supabase for the backend infrastructure
- LiveKit for WebRTC streaming
- Tailwind CSS for styling

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Email: support@trendke.com (example)

---

**Built with ❤️ for creators in Kenya and beyond**
