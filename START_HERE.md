# TrendKe - Quick Start Guide (No Installation Needed)

## Your Current Setup

✅ **Backend:** Python FastAPI  
✅ **Frontend:** React + Vite  
✅ **Database:** Supabase (cloud)  
⚠️ **Redis:** Need to setup (use online service)

---

## Step 1: Setup Online Redis (5 minutes)

Choose one option:

### Option A: Upstash (Recommended - Easiest)
1. Go to: https://upstash.com
2. Sign up (free, no credit card)
3. Create database → Copy `REDIS_URL`
4. Update `backend/.env`:
   ```env
   REDIS_URL=redis://default:password@redis-xxxxx.upstash.io:6379
   ```

### Option B: Redis Cloud
1. Go to: https://redis.com/try-free/
2. Create free database
3. Copy endpoint and password
4. Update `backend/.env` with connection URL

**Full instructions:** See `REDIS_ONLINE_SETUP.md`

---

## Step 2: Start Backend

```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

✅ Look for: `✅ Redis cache connected successfully`

---

## Step 3: Start Frontend (New Terminal)

```powershell
cd frontend
npm run dev
```

✅ Opens at: http://localhost:5174

---

## That's It!

Your app is now running:
- **Frontend:** http://localhost:5174
- **Backend:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs

---

## Troubleshooting

### "Redis connection failed"
- Check `REDIS_URL` in `backend/.env`
- Make sure you copied the full URL from Upstash/Redis Cloud
- Restart backend after updating `.env`

### "Module not found"
```powershell
cd backend
pip install -r requirements.txt
```

### Frontend won't start
```powershell
cd frontend
npm install
npm run dev
```

### Port already in use
```powershell
# Backend on different port
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload

# Update frontend/.env
VITE_API_URL=http://localhost:8002
```

---

## Quick Commands Reference

```powershell
# Check if Redis URL is set
cd backend
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('REDIS_URL'))"

# Test backend manually
curl http://localhost:8001/

# View backend logs (verbose)
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload --log-level debug
```

---

## Need Help?

1. **Redis Setup:** See `REDIS_ONLINE_SETUP.md`
2. **Supabase:** See `backend/HOW_TO_USE_SUPABASE.md`
3. **Docker Removed:** See `DOCKER_REMOVAL_COMPLETE.md`

Everything is now running locally except Redis and Database (which are in the cloud).
