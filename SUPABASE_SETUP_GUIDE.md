# 🚨 Login/Registration Not Working?

## The Issue

You're seeing login/registration errors because **Supabase is not configured yet**. The backend needs a PostgreSQL database to store users, and we're using Supabase for that.

## Quick Fix (5 minutes)

### Step 1: Create Supabase Account
1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up (free)

### Step 2: Create New Project
1. Click "New Project"
2. Name it: `trendke`
3. Create a strong database password (save it!)
4. Choose a region close to you
5. Wait 2-3 minutes for setup

### Step 3: Get Your Credentials
1. In your Supabase project dashboard
2. Click "Project Settings" (gear icon)
3. Click "API" in the sidebar
4. Copy these two values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

### Step 4: Update Backend .env
Open `backend/.env` and replace:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

With your actual values:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGci...your-actual-key...
```

### Step 5: Create Database Tables
1. In Supabase dashboard, click "SQL Editor"
2. Click "New query"
3. Open `backend/database_schema.sql` in your code editor
4. Copy ALL the contents
5. Paste into Supabase SQL Editor
6. Click "Run"
7. You should see "Success. No rows returned"

### Step 6: Restart Backend
In your terminal where backend is running:
1. Press `Ctrl+C` to stop
2. Run: `cd backend; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

### Step 7: Test!
1. Go to http://localhost:5174
2. Click "Sign Up"
3. Create an account
4. It should work now! 🎉

---

## Still Having Issues?

### Check Backend Terminal
You should see:
```
INFO:     Application startup complete.
```

NOT:
```
⚠️  WARNING: SUPABASE NOT CONFIGURED!
```

### Test Database Connection
1. Go to http://127.0.0.1:8000/docs
2. Try the `/auth/signup` endpoint
3. Click "Try it out"
4. Fill in the form
5. Click "Execute"

If you see "Failed to create user", double-check:
- ✅ SUPABASE_URL is correct (no `your-project-id` placeholders)
- ✅ SUPABASE_KEY is the **anon public** key
- ✅ Database schema was run successfully
- ✅ Backend was restarted after updating .env

---

## Alternative: Use Local Development Database

If you don't want to use Supabase right now, you can temporarily modify the backend to use an in-memory database, but this means data won't persist. Let me know if you want this option!

---

## What Each Error Means

**"Failed to create user. Please check if Supabase is configured correctly"**
→ Backend can't connect to database. Check .env file.

**"Incorrect email or password. If this is a new setup, please configure Supabase first."**
→ Database has no users yet, or Supabase not configured.

**"Signup failed. Please ensure Supabase is configured"**
→ .env file has placeholder values, not real credentials.

---

## Need Help?

Show me:
1. Your backend terminal output (does it show the Supabase warning?)
2. The error message you're seeing in the browser
3. Whether you've created a Supabase project

And I'll help you troubleshoot!
