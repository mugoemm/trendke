# TrendKe Backend - Quick Start Guide

## Prerequisites
- Python 3.9 or higher
- PostgreSQL database (via Supabase)
- Node.js 18+ (for frontend)

## Backend Setup

### 1. Install Python Dependencies
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and update with your credentials:
```bash
cp .env.example .env
```

**Required Configuration:**
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `JWT_SECRET_KEY`: Random secret key for JWT tokens

### 3. Setup Database
Run the database schema in your Supabase SQL editor:
```bash
# Copy contents of database_schema.sql to Supabase SQL Editor
```

### 4. Start Backend Server
```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

---

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
The `.env` file is already created with:
```
VITE_API_URL=http://localhost:8000
```

### 3. Start Frontend
```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## Quick Test

1. **Start Backend**: `cd backend && uvicorn app.main:app --reload`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Open Browser**: Navigate to `http://localhost:5173`
4. **Create Account**: Click "Sign Up" and register
5. **Upload Video**: Navigate to "Upload" in the menu

---

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user
- `GET /auth/user/{user_id}` - Get user profile

### Videos
- `POST /videos/upload` - Upload video
- `GET /videos/feed` - Get video feed (paginated)
- `GET /videos/{video_id}` - Get video details
- `POST /videos/{video_id}/like` - Like/unlike video
- `GET /videos/{video_id}/comments` - Get comments
- `POST /videos/{video_id}/comment` - Add comment

### Live Streaming
- `POST /live/start` - Start live session
- `POST /live/join` - Join live session
- `POST /live/{session_id}/end` - End live session
- `GET /live/list` - Get active sessions
- `GET /live/{session_id}` - Get session details

### Gifts
- `GET /gifts/types` - Get available gift types
- `POST /gifts/send` - Send gift to user
- `GET /gifts/balance` - Get user coin balance
- `GET /gifts/leaderboard` - Get top gifters
- `GET /gifts/history` - Get gift history

### Payments
- `GET /payments/packages` - Get coin packages
- `POST /payments/purchase/initiate` - Initiate purchase
- `GET /payments/history` - Get payment history

---

## Project Structure

```
trendke/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── auth.py           # Authentication routes
│   │   ├── video.py          # Video routes
│   │   ├── live.py           # Live streaming routes
│   │   ├── gifts.py          # Gifting routes
│   │   ├── payments.py       # Payment routes
│   │   ├── notifications.py  # Notifications routes
│   │   ├── models.py         # Pydantic models
│   │   └── db.py             # Database helper
│   ├── .env                  # Environment variables
│   ├── requirements.txt      # Python dependencies
│   └── database_schema.sql   # Database schema
│
└── frontend/
    ├── src/
    │   ├── api/              # API client modules
    │   ├── components/       # React components
    │   ├── pages/            # Page components
    │   ├── App.jsx           # Main app with routing
    │   └── main.jsx          # Entry point
    ├── .env                  # Frontend environment
    └── package.json          # Node dependencies
```

---

## Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
# Ensure virtual environment is activated
cd backend
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Database connection errors:**
- Verify Supabase URL and key in `.env`
- Check database schema is imported
- Ensure tables exist in Supabase

### Frontend Issues

**"Cannot find module" errors:**
```bash
cd frontend
npm install
```

**API connection errors:**
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in frontend `.env`
- Verify CORS is enabled in backend

**Port already in use:**
```bash
# Use different port
npm run dev -- --port 3000
```

---

## Development Workflow

1. **Backend changes**: Server auto-reloads with `--reload` flag
2. **Frontend changes**: Vite HMR updates instantly
3. **Database changes**: Update `database_schema.sql` and re-run in Supabase
4. **API testing**: Use Swagger docs at `http://localhost:8000/docs`

---

## Next Steps

1. **Setup Supabase**:
   - Create account at supabase.com
   - Create new project
   - Copy project URL and anon key
   - Run database schema

2. **Configure Payments** (Optional):
   - PesaPal sandbox account
   - Stripe test account

3. **Setup LiveKit** (Optional):
   - Create LiveKit Cloud account
   - Get API credentials
   - Update `.env` with LiveKit config

---

## Support

For issues or questions:
- Check API docs: `http://localhost:8000/docs`
- Review console logs in browser DevTools
- Check backend terminal for error messages
