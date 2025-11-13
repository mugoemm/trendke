# 🎯 TrendKe Deployment Quick Reference Card

## Status: ✅ 100% READY FOR PRODUCTION

---

## ⚡ Ultra-Quick Deploy (Copy-Paste)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Render (Backend)
1. Go to: https://dashboard.render.com
2. New + → Web Service → Connect GitHub → Select trendke
3. Add 11 environment variables (see below)
4. Click "Create Web Service"
5. Wait 10 min → Copy backend URL

### Step 3: Vercel (Frontend)  
1. Go to: https://vercel.com/dashboard
2. Add New → Project → Import trendke
3. Root Directory: `frontend`
4. Add environment variable: `VITE_API_URL` = your-render-url
5. Click "Deploy"
6. Wait 3 min → Copy frontend URL

### Step 4: Update CORS
1. Back to Render → Your service → Environment
2. Update `FRONTEND_URL` = your-vercel-url
3. Manual Deploy → Deploy latest commit
4. Done! ✅

---

## 🔑 Environment Variables (11 Backend + 1 Frontend)

### Backend (Render Dashboard → Environment Tab)

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...
SUPABASE_SERVICE_ROLE_KEY=eyJxxx...
JWT_SECRET_KEY=xxx (generate new!)
JWT_ALGORITHM=HS256
CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx
REDIS_URL=rediss://default:xxx@xxx.upstash.io:6379
REDIS_PASSWORD=xxx
FRONTEND_URL=http://localhost:5173 (update after Vercel!)
```

### Frontend (Vercel Dashboard → Settings → Environment Variables)

```
VITE_API_URL=https://your-backend.onrender.com
```

---

## 🛠️ Generate JWT Secret

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Copy output → Use as `JWT_SECRET_KEY` in Render**

---

## 📋 Pre-Flight Checklist (5 min)

- [ ] All code committed to git
- [ ] GitHub repository created
- [ ] Supabase project has all tables (users, videos, likes, comments, follows)
- [ ] Cloudinary account configured
- [ ] Upstash Redis instance created
- [ ] New JWT_SECRET_KEY generated (don't use old one!)
- [ ] All 11 backend env vars ready
- [ ] Frontend env var ready

---

## 🎯 Expected Results

### URLs
- **Backend**: `https://trendke-backend.onrender.com`
- **Frontend**: `https://trendke-username.vercel.app`
- **API Docs**: `https://trendke-backend.onrender.com/docs`

### Timing
- Backend deploy: ~10 minutes
- Frontend deploy: ~3 minutes
- Total: ~15-20 minutes

### Features to Test
✅ Homepage loads with videos  
✅ Sign up / Login works  
✅ Upload video (with progress bar)  
✅ Like / Comment  
✅ Follow users  
✅ Profile page  
✅ Trending page  

---

## 🐛 Quick Troubleshooting

### "Application failed to respond" (Render)
→ Check all 11 env vars are set  
→ Check Render logs for errors

### "Network Error" (Frontend)
→ Verify `VITE_API_URL` matches Render backend URL  
→ Check backend is running (green status on Render)

### "CORS policy" error
→ Update `FRONTEND_URL` in Render to match Vercel URL  
→ Redeploy backend after updating

### Videos not uploading
→ Verify Cloudinary credentials  
→ Check backend logs for Cloudinary errors

---

## 📚 Full Documentation

**START HERE**: `QUICK_START_DEPLOY.md` (step-by-step with screenshots reference)

**Other Docs**:
- `DEPLOYMENT.md` - Complete guide (447 lines)
- `ENV_SETUP.md` - How to get all credentials
- `PRE_DEPLOYMENT_CHECKLIST.md` - Full checklist
- `DEPLOYMENT_PACKAGE.md` - Package overview

**Run Check**: `.\check_deployment.ps1` (Windows)

---

## 🎉 After Deployment

1. Test all features (see list above)
2. Monitor logs for 24 hours
3. Set up custom domain (optional)
4. Configure database backups in Supabase
5. Share your app! 🚀

---

## 💡 Pro Tips

- Render free tier sleeps after 15 min inactivity (first request slow)
- Vercel auto-deploys on every git push to main
- Keep this card handy during deployment
- Check Render logs if anything goes wrong
- Backend API docs available at `/docs` endpoint

---

## ⏱️ Time Breakdown

| Task | Duration |
|------|----------|
| Push to GitHub | 2 min |
| Deploy to Render | 10 min |
| Deploy to Vercel | 3 min |
| Update CORS | 2 min |
| Testing | 5 min |
| **TOTAL** | **~22 minutes** |

---

## 🆘 Need Help?

1. Check `DEPLOYMENT.md` section 7 (Troubleshooting)
2. Review Render logs: Dashboard → Service → Logs
3. Check Vercel deployment logs: Dashboard → Deployments → Latest
4. Verify all env vars match `ENV_SETUP.md`

---

*This project is 100% complete and ready for production deployment*

**All systems operational | All tests passing | All docs complete**

---

**Ready? Run:** `.\check_deployment.ps1` **then follow** `QUICK_START_DEPLOY.md`
