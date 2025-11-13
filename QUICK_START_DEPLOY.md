# 🚀 Quick Deployment Guide

> **TL;DR**: Push to GitHub → Deploy to Render (backend) → Deploy to Vercel (frontend) → Update CORS

---

## Prerequisites Checklist

- [ ] GitHub account
- [ ] Render account (https://render.com)
- [ ] Vercel account (https://vercel.com)
- [ ] All environment variables ready (see ENV_SETUP.md)

---

## 3-Step Deployment

### Step 1: Push to GitHub (5 minutes)

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - ready for deployment"

# Add remote (replace YOUR_USERNAME/trendke with your repo)
git remote add origin https://github.com/YOUR_USERNAME/trendke.git

# Push
git push -u origin main
```

---

### Step 2: Deploy Backend to Render (10 minutes)

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your `trendke` repository

3. **Render Auto-Detects Settings** (from render.yaml):
   - Name: `trendke-backend`
   - Environment: `Python 3`
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables** (click "Environment" tab):
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   JWT_SECRET_KEY=generate_with_python_secrets
   JWT_ALGORITHM=HS256
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   REDIS_URL=your_upstash_redis_url
   REDIS_PASSWORD=your_redis_password
   STRIPE_SECRET_KEY=your_stripe_secret
   STRIPE_WEBHOOK_SECRET=your_webhook_secret
   FRONTEND_URL=http://localhost:5173
   ```
   
   **Note**: Generate JWT_SECRET_KEY with:
   ```python
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Deploy**: Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Your backend URL will be: `https://trendke-backend.onrender.com`

---

### Step 3: Deploy Frontend to Vercel (5 minutes)

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard

2. **Import Project**:
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Select `trendke`

3. **Configure Project**:
   - **Framework Preset**: Vite (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)

4. **Add Environment Variable**:
   ```
   VITE_API_URL=https://trendke-backend.onrender.com
   ```
   (Use your actual Render backend URL from Step 2)

5. **Deploy**: Click "Deploy"
   - Wait 2-3 minutes
   - Your frontend URL will be: `https://trendke-username.vercel.app`

---

### Step 4: Update Backend CORS (2 minutes)

1. **Go back to Render Dashboard**

2. **Update Environment Variable**:
   - Find your `trendke-backend` service
   - Go to "Environment" tab
   - Update `FRONTEND_URL` from `http://localhost:5173` to your Vercel URL:
     ```
     FRONTEND_URL=https://trendke-username.vercel.app
     ```

3. **Redeploy**:
   - Click "Manual Deploy" → "Deploy latest commit"
   - Wait 2-3 minutes

---

## ✅ Verify Deployment

Visit your frontend URL: `https://trendke-username.vercel.app`

**Test these features**:
- [ ] Homepage loads with videos
- [ ] Can sign up/login
- [ ] Can upload a video
- [ ] Videos play correctly
- [ ] Can like/comment on videos
- [ ] Can follow other users
- [ ] Profile page shows user videos
- [ ] Explore/trending page works

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: "Application failed to respond"
- **Solution**: Check Render logs, verify all environment variables are set

**Problem**: "Database connection error"
- **Solution**: Verify SUPABASE_URL and SUPABASE_KEY are correct

**Problem**: "Redis connection failed"
- **Solution**: Check REDIS_URL and REDIS_PASSWORD from Upstash

### Frontend Issues

**Problem**: "Network Error" or "Failed to fetch"
- **Solution**: Verify VITE_API_URL points to correct Render backend URL
- **Solution**: Ensure FRONTEND_URL is updated in Render backend

**Problem**: "Videos not loading"
- **Solution**: Check browser console for CORS errors
- **Solution**: Verify backend CORS allows your Vercel domain

**Problem**: "Images not showing"
- **Solution**: Verify CLOUDINARY credentials in backend

### CORS Issues

**Problem**: "Access-Control-Allow-Origin error"
- **Solution**: Update backend `FRONTEND_URL` to match Vercel URL
- **Solution**: Redeploy backend after updating

---

## 📊 Monitoring

### Render Dashboard
- **Logs**: https://dashboard.render.com/web/YOUR_SERVICE/logs
- **Metrics**: Monitor memory, CPU usage
- **Health**: Check if service is running

### Vercel Dashboard
- **Deployments**: See all deployment history
- **Analytics**: View page views, performance
- **Logs**: Runtime and build logs

---

## 🔄 Redeployment

### Update Code

```bash
# Make your changes
git add .
git commit -m "Update: description of changes"
git push origin main
```

**Vercel** automatically redeploys on every push to `main`

**Render** auto-redeploys if you enabled "Auto-Deploy" (recommended)

### Manual Redeploy

**Render**: Dashboard → Service → "Manual Deploy" → "Deploy latest commit"

**Vercel**: Dashboard → Project → Deployments → "Redeploy"

---

## 🎯 Post-Deployment Tasks

- [ ] Set up custom domain (optional)
- [ ] Configure analytics (Vercel Analytics)
- [ ] Set up error tracking (Sentry)
- [ ] Enable Stripe webhooks for production
- [ ] Test all features in production
- [ ] Monitor logs for errors
- [ ] Set up database backups (Supabase)

---

## 📚 Additional Resources

- **Full Deployment Guide**: `DEPLOYMENT.md`
- **Environment Variables**: `ENV_SETUP.md`
- **Pre-Deployment Checklist**: `PRE_DEPLOYMENT_CHECKLIST.md`
- **Backend Documentation**: `backend/README.md`
- **Frontend Documentation**: `frontend/README.md`

---

## 🆘 Need Help?

1. Check `DEPLOYMENT.md` for detailed troubleshooting
2. Review Render logs: `https://dashboard.render.com/web/YOUR_SERVICE/logs`
3. Check Vercel deployment logs
4. Verify all environment variables are set correctly
5. Ensure database has proper tables and data

---

## 🎉 Success!

Your TrendKe app is now live!

- **Frontend**: `https://trendke-username.vercel.app`
- **Backend**: `https://trendke-backend.onrender.com`
- **API Docs**: `https://trendke-backend.onrender.com/docs`

Share your app with the world! 🚀
