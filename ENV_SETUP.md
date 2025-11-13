# Environment Variables Setup Guide

## Backend (Render)

When deploying to Render, set these environment variables in the Render dashboard:

### Required Variables:

```bash
# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here-use-strong-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Cloudinary (Media Storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Redis Cache (Upstash or other)
REDIS_URL=rediss://default:password@your-redis-host:6379

# Stripe (Optional - for payments)
STRIPE_SECRET_KEY=sk_test_or_live_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Frontend URL (Your Vercel deployment)
FRONTEND_URL=https://your-app.vercel.app
```

### How to Get These Values:

#### Supabase:
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to Settings > API
4. Copy `URL` and `anon public` key

#### Cloudinary:
1. Go to https://cloudinary.com/console
2. Dashboard shows your Cloud Name
3. Go to Settings > Access Keys for API credentials

#### Redis (Upstash):
1. Go to https://console.upstash.com
2. Create a Redis database
3. Copy the connection string (REDIS_URL)

#### JWT Secret:
Generate a strong random string:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Frontend (Vercel)

Set this in Vercel dashboard under Settings > Environment Variables:

```bash
# Backend API URL (Your Render deployment)
VITE_API_URL=https://your-backend-app.onrender.com
```

### Important Notes:

1. **Remove trailing slashes** from URLs
2. **Use HTTPS** for production URLs
3. **Keep secrets secure** - never commit them to Git
4. **Update FRONTEND_URL** in Render after deploying to Vercel
5. **Redeploy backend** after updating FRONTEND_URL to apply CORS changes

---

## Local Development

For local development, keep your existing `.env` files:

### Backend `.env`:
```bash
SUPABASE_URL=your-url
SUPABASE_KEY=your-key
JWT_SECRET_KEY=dev-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
REDIS_URL=your-redis-url
STRIPE_SECRET_KEY=sk_test_key
STRIPE_WEBHOOK_SECRET=whsec_test
```

### Frontend `.env`:
```bash
VITE_API_URL=http://localhost:8000
```
