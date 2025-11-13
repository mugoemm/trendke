# TrendKe Backend API

FastAPI backend for TrendKe - A TikTok-style social media platform.

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- Redis (local or Upstash)
- Supabase account
- Cloudinary account

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Environment Setup

Create `.env` file with:

```bash
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
REDIS_URL=your-redis-url
STRIPE_SECRET_KEY=your-stripe-key
STRIPE_WEBHOOK_SECRET=your-webhook-secret
```

### Run Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Access at: http://localhost:8000
API Docs: http://localhost:8000/docs

## 📦 Production Deployment

See [DEPLOYMENT.md](../DEPLOYMENT.md) for complete deployment instructions to Render.

### Key Files for Deployment:

- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `app/main.py` - Main application with CORS setup

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app & CORS config
│   ├── auth.py              # Authentication & JWT
│   ├── video.py             # Video endpoints
│   ├── social.py            # Follow/like/comment
│   ├── gifts.py             # Virtual gifts system
│   ├── live.py              # Live streaming
│   ├── db.py                # Supabase client
│   ├── redis_cache.py       # Redis caching
│   └── trending_scheduler.py # Trending algorithm
├── migrations/              # Database migrations
├── requirements.txt         # Dependencies
└── render.yaml             # Render deployment config
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user

### Videos
- `GET /videos/feed` - Get video feed (public)
- `GET /videos/trending/videos` - Get trending videos
- `POST /videos/upload` - Upload video (auth required)
- `POST /videos/{id}/like` - Like video
- `GET /videos/{id}/comments` - Get comments
- `POST /videos/{id}/comment` - Add comment

### Social
- `POST /social/follow/{user_id}` - Follow user
- `POST /social/unfollow/{user_id}` - Unfollow user
- `GET /social/is-following/{user_id}` - Check if following
- `GET /social/following-feed` - Get following feed

### Gifts
- `GET /gifts/balance` - Get coin balance
- `POST /gifts/send` - Send virtual gift

## 🔧 Utilities

### Health Check
```bash
python health_check.py
```

### List Users
```bash
python list_users.py
```

### Reset Password
```bash
python reset_password.py
```

### Seed Demo Videos
```bash
python seed_videos.py
```

## 📊 Features

- ✅ JWT Authentication
- ✅ Video Upload (Cloudinary)
- ✅ Redis Caching
- ✅ Trending Algorithm (APScheduler)
- ✅ WebSocket Support
- ✅ Social Features (Follow, Like, Comment)
- ✅ Virtual Gifts System
- ✅ Live Streaming Support

## 🔐 Security

- Password hashing with bcrypt
- JWT tokens with expiration
- Protected routes with dependencies
- CORS configuration for production
- Environment-based configuration

## 📝 License

MIT
