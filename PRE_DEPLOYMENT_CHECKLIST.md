# 🚀 Pre-Deployment Checklist

Complete this checklist before deploying to production.

## ✅ Backend Preparation

### Files Ready
- [ ] `backend/requirements.txt` - All dependencies listed
- [ ] `backend/render.yaml` - Render configuration complete
- [ ] `backend/app/main.py` - CORS configured for production
- [ ] `backend/.env.example` - Example env file created

### Code Ready
- [ ] Remove all `print()` debug statements (optional)
- [ ] All imports working
- [ ] No hardcoded URLs or secrets
- [ ] Database migrations run successfully
- [ ] Health check script works

### Environment Variables Prepared
- [ ] `SUPABASE_URL` - Copied from Supabase dashboard
- [ ] `SUPABASE_KEY` - Copied from Supabase dashboard
- [ ] `JWT_SECRET_KEY` - Generated strong random string
- [ ] `CLOUDINARY_CLOUD_NAME` - From Cloudinary account
- [ ] `CLOUDINARY_API_KEY` - From Cloudinary account
- [ ] `CLOUDINARY_API_SECRET` - From Cloudinary account
- [ ] `REDIS_URL` - From Upstash console
- [ ] `STRIPE_SECRET_KEY` - From Stripe dashboard (optional)
- [ ] `STRIPE_WEBHOOK_SECRET` - From Stripe dashboard (optional)

## ✅ Frontend Preparation

### Files Ready
- [ ] `frontend/vercel.json` - Vercel configuration complete
- [ ] `frontend/package.json` - All dependencies listed
- [ ] `frontend/.env.production.example` - Example env file created

### Code Ready
- [ ] No console.log() in production code (optional)
- [ ] All API calls use `VITE_API_URL` env variable
- [ ] No hardcoded backend URLs
- [ ] Build completes without errors (`npm run build`)
- [ ] All routes work correctly

### Environment Variables Prepared
- [ ] `VITE_API_URL` - Will be set after backend deployment

## ✅ GitHub Repository

### Repository Setup
- [ ] Code pushed to GitHub
- [ ] Repository is public or accessible to deploy services
- [ ] `.gitignore` properly configured
- [ ] No `.env` files committed
- [ ] All sensitive data removed from commits

### Branch Setup
- [ ] Main branch is `main` or `master`
- [ ] Latest code is on main branch
- [ ] No uncommitted changes locally

## ✅ External Services

### Supabase
- [ ] Project created
- [ ] Database tables created (run migrations)
- [ ] API keys copied
- [ ] Row Level Security configured (optional)

### Cloudinary
- [ ] Account created
- [ ] Cloud name noted
- [ ] API credentials copied
- [ ] Upload preset configured (optional)

### Upstash Redis
- [ ] Database created
- [ ] Connection string copied
- [ ] Database accessible

### Stripe (Optional)
- [ ] Account created
- [ ] API keys copied
- [ ] Webhook configured

## ✅ Deployment Accounts

### Render
- [ ] Account created at render.com
- [ ] GitHub connected
- [ ] Payment method added (if using paid plan)

### Vercel
- [ ] Account created at vercel.com
- [ ] GitHub connected
- [ ] Ready to import project

## ✅ Testing

### Local Testing
- [ ] Backend runs without errors
- [ ] Frontend runs without errors
- [ ] Can create account
- [ ] Can login
- [ ] Can upload video
- [ ] Videos display in feed
- [ ] Like/comment works
- [ ] Follow system works

### API Testing
- [ ] Health endpoint works: `/health`
- [ ] Video feed endpoint works: `/videos/feed`
- [ ] Trending endpoint works: `/videos/trending/videos`
- [ ] Auth endpoints work: `/auth/login`, `/auth/register`

## ✅ Documentation

### Required Docs
- [ ] DEPLOYMENT.md - Deployment instructions complete
- [ ] ENV_SETUP.md - Environment variables documented
- [ ] README.md - Project overview complete
- [ ] backend/README.md - Backend docs complete
- [ ] frontend/README.md - Frontend docs complete

## 📝 Deployment Order

1. ✅ Complete this checklist
2. 🔧 Deploy backend to Render
3. 🌐 Deploy frontend to Vercel
4. 🔄 Update backend FRONTEND_URL with Vercel URL
5. ✅ Test production deployment
6. 🎉 Share with the world!

## 🚨 Important Notes

- **Don't commit `.env` files!**
- **Use strong JWT_SECRET_KEY in production**
- **Update FRONTEND_URL after deploying frontend**
- **Test thoroughly before sharing publicly**
- **Monitor logs during first deployment**

---

Once all items are checked, you're ready to deploy! 🚀

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step deployment instructions.
