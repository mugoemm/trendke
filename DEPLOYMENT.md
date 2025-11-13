# 🚀 TrendKe Deployment Guide

Complete guide to deploy TrendKe to production using Render (backend) and Vercel (frontend).

---

## 📋 Prerequisites

Before deploying, ensure you have:

- [x] GitHub account
- [x] Render account (https://render.com)
- [x] Vercel account (https://vercel.com)
- [x] Supabase project set up
- [x] Cloudinary account set up
- [x] Redis database (Upstash recommended)
- [x] All environment variables ready (see ENV_SETUP.md)

---

## 🔧 Part 1: Prepare Your Repository

### 1. Push to GitHub

If you haven't already, push your code to GitHub:

```bash
cd "d:\My projects\trendke"
git init
git add .
git commit -m "Initial commit - ready for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/trendke.git
git push -u origin main
```

### 2. Verify Files

Ensure these files exist in your repository:

**Backend:**
- ✅ `backend/requirements.txt`
- ✅ `backend/render.yaml`
- ✅ `backend/app/main.py` (with updated CORS)

**Frontend:**
- ✅ `frontend/vercel.json`
- ✅ `frontend/package.json`
- ✅ `frontend/.env.production.example`

---

## 🖥️ Part 2: Deploy Backend to Render

### Step 1: Create New Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the `trendke` repository

### Step 2: Configure Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `trendke-backend` |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` (or paid for better performance) |

### Step 3: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add all variables from `ENV_SETUP.md`:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key
JWT_SECRET_KEY=your-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
REDIS_URL=rediss://...
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=https://your-app.vercel.app (will add after Vercel deploy)
```

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for the build to complete (5-10 minutes)
3. Note your backend URL: `https://trendke-backend.onrender.com`

### Step 5: Test Backend

Visit: `https://your-backend-app.onrender.com/docs`

You should see the FastAPI Swagger documentation.

---

## 🌐 Part 3: Deploy Frontend to Vercel

### Step 1: Import Project

1. Go to https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select your `trendke` repository
4. Vercel will auto-detect it as a Vite project

### Step 2: Configure Project

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Vite` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |

### Step 3: Add Environment Variable

Click **"Environment Variables"** and add:

```
VITE_API_URL=https://your-backend-app.onrender.com
```

**Important:** Replace with your actual Render backend URL (no trailing slash!)

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait for build to complete (2-5 minutes)
3. Note your frontend URL: `https://your-app.vercel.app`

### Step 5: Test Frontend

1. Visit your Vercel URL
2. You should see the TrendKe home page
3. Try creating an account or logging in

---

## 🔄 Part 4: Update Backend with Frontend URL

### Important: Update CORS Settings

1. Go back to Render dashboard
2. Open your backend service
3. Go to **"Environment"** tab
4. Update `FRONTEND_URL` with your Vercel URL:
   ```
   FRONTEND_URL=https://your-app.vercel.app
   ```
5. Click **"Save Changes"**
6. Render will automatically redeploy

**Why?** This updates CORS to allow requests from your production frontend.

---

## ✅ Part 5: Verify Deployment

### Backend Checks:

- [ ] API docs accessible: `https://your-backend.onrender.com/docs`
- [ ] Health check works: `https://your-backend.onrender.com/health`
- [ ] Video feed endpoint: `https://your-backend.onrender.com/videos/feed`

### Frontend Checks:

- [ ] Home page loads
- [ ] Can create account / login
- [ ] Videos display correctly
- [ ] Can upload videos
- [ ] Profile page works
- [ ] Trending/Explore page works

### Integration Checks:

- [ ] Login/signup works
- [ ] Videos upload successfully
- [ ] Like/comment features work
- [ ] Follow/unfollow works
- [ ] No CORS errors in browser console

---

## 🔧 Troubleshooting

### Common Issues:

#### 1. CORS Errors

**Problem:** "Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy"

**Solution:**
- Ensure `FRONTEND_URL` in Render matches your Vercel URL exactly
- Redeploy backend after updating `FRONTEND_URL`
- Clear browser cache and try again

#### 2. API Connection Failed

**Problem:** Frontend can't connect to backend

**Solution:**
- Check `VITE_API_URL` in Vercel environment variables
- Ensure backend URL has no trailing slash
- Verify backend is running (check Render logs)

#### 3. Videos Not Uploading

**Problem:** Video upload fails

**Solution:**
- Verify Cloudinary credentials in Render
- Check backend logs for errors
- Ensure file size is under 100MB

#### 4. Database Connection Errors

**Problem:** "Database connection failed"

**Solution:**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in Render
- Check Supabase project is active
- Verify database tables exist (run migrations)

#### 5. Redis/Cache Errors

**Problem:** "Redis connection failed"

**Solution:**
- Verify `REDIS_URL` is correct
- Check Redis database is active in Upstash
- Ensure Redis URL uses `rediss://` (with SSL)

---

## 📊 Monitoring

### Render Dashboard:

- View logs: Click service → **"Logs"**
- Check metrics: **"Metrics"** tab
- Monitor deploys: **"Events"** tab

### Vercel Dashboard:

- View deployments: Project → **"Deployments"**
- Check analytics: **"Analytics"** tab
- View logs: Select deployment → **"Functions"** tab

---

## 🔄 Redeploying

### Backend (Render):

**Automatic:** Push to main branch on GitHub
```bash
git add .
git commit -m "Update backend"
git push origin main
```

**Manual:** Render dashboard → Click **"Manual Deploy"**

### Frontend (Vercel):

**Automatic:** Push to main branch on GitHub
```bash
git add .
git commit -m "Update frontend"
git push origin main
```

**Manual:** Vercel dashboard → Click **"Redeploy"**

---

## 🎯 Performance Tips

### Backend Optimization:

1. **Upgrade Render plan** for better performance (free tier spins down after inactivity)
2. **Enable caching** - Redis is already configured
3. **Add CDN** for static files (Cloudinary handles this)

### Frontend Optimization:

1. **Enable Vercel Analytics** - Built-in performance monitoring
2. **Use Edge Network** - Automatically enabled on Vercel
3. **Image optimization** - Cloudinary handles this

---

## 🔐 Security Checklist

Before going live:

- [ ] Change `JWT_SECRET_KEY` to a strong random string
- [ ] Use production Stripe keys (not test keys)
- [ ] Enable Supabase Row Level Security (RLS)
- [ ] Review API rate limits
- [ ] Set up monitoring alerts
- [ ] Configure backup strategy for database

---

## 📞 Support

If you encounter issues:

1. Check Render logs: Service → Logs tab
2. Check Vercel logs: Deployment → Functions tab
3. Check browser console for frontend errors
4. Review ENV_SETUP.md for correct environment variables

---

## ✨ You're Done!

Your TrendKe application is now live in production! 🎉

- **Frontend:** https://your-app.vercel.app
- **Backend:** https://your-backend.onrender.com
- **API Docs:** https://your-backend.onrender.com/docs

Share your app with the world! 🚀
