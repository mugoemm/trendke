# 🚀 SUPABASE SETUP - COMPLETE GUIDE

## ⏱️ Time Required: 5-7 minutes

Follow these steps **exactly** to get your database running.

---

## 📋 STEP 1: Create Supabase Account (2 minutes)

1. **Browser is already open** at https://supabase.com
2. Click **"Start your project"** button
3. Sign up with:
   - ✅ GitHub account (recommended - instant)
   - ✅ Email (you'll need to verify)
4. Complete signup

---

## 📋 STEP 2: Create New Project (2 minutes)

1. After login, click **"New Project"**
2. Choose your organization (or create one)
3. Fill in project details:
   ```
   Name: trendke
   Database Password: [Create a STRONG password - SAVE THIS!]
   Region: [Choose closest to you - e.g., "West US" or "Europe West"]
   Pricing Plan: Free (perfect for development)
   ```
4. Click **"Create new project"**
5. **WAIT 2-3 minutes** for project setup (grab a coffee! ☕)

---

## 📋 STEP 3: Get Your Credentials (1 minute)

Once your project is ready:

1. In Supabase dashboard, look for **"Project Settings"** icon (⚙️ gear) in sidebar
2. Click **"API"** in the settings menu
3. You'll see two important values:

   **Copy these:**
   ```
   Project URL: https://xxxxxxxxxxxxx.supabase.co
   anon public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey...
   ```

4. **IMPORTANT:** Copy the **anon** key, NOT the service_role key!

---

## 📋 STEP 4: Update Backend Configuration (30 seconds)

1. Open file: **`backend/.env`** in VS Code
2. Find these lines:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   ```

3. Replace with your ACTUAL values:
   ```env
   SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey...
   ```

4. **Save the file** (Ctrl+S / Cmd+S)

---

## 📋 STEP 5: Create Database Tables (2 minutes)

1. In Supabase dashboard, click **"SQL Editor"** in sidebar (or find it in the left menu)
2. Click **"New query"** button
3. Open this file in VS Code: **`backend/SUPABASE_SCHEMA.sql`**
4. **Select ALL** content (Ctrl+A / Cmd+A)
5. **Copy** (Ctrl+C / Cmd+C)
6. Go back to Supabase SQL Editor
7. **Paste** the entire SQL (Ctrl+V / Cmd+V)
8. Click **"Run"** button (or press F5)
9. You should see: **"Success. No rows returned"** ✅

**Expected output in Supabase:**
```
Success. No rows returned
```

If you see errors, **tell me immediately** - but you shouldn't if you followed steps correctly!

---

## 📋 STEP 6: Verify Database Setup (30 seconds)

In Supabase dashboard:

1. Click **"Table Editor"** in sidebar
2. You should see these tables:
   - ✅ users
   - ✅ videos
   - ✅ video_likes
   - ✅ video_comments
   - ✅ live_sessions
   - ✅ gift_types
   - ✅ gift_transactions
   - ✅ coin_packages
   - ✅ payment_transactions
   - ✅ notifications
   - ✅ follows

3. Click on **"gift_types"** table - you should see 7 gifts (Rose, Heart, Star, Fire, Crown, Diamond, Rocket) 🎁

---

## 📋 STEP 7: Restart Backend Server (30 seconds)

1. Go to VS Code
2. Find the terminal running the backend
3. Press **Ctrl+C** to stop the server
4. Run this command:
   ```bash
   cd "d:\My projects\trendke\backend"
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

5. Look for this output (NO WARNING!):
   ```
   INFO:     Application startup complete.
   ```

   **NOT THIS:**
   ```
   ⚠️  WARNING: SUPABASE NOT CONFIGURED!
   ```

---

## 🎉 STEP 8: TEST EVERYTHING! (1 minute)

### Test 1: Backend Health Check
Open browser: http://127.0.0.1:8000/health

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Test 2: Create Your First Account!
1. Go to: http://localhost:5174
2. Click **"Sign Up"**
3. Fill in the form:
   ```
   Email: test@example.com
   Username: testuser
   Full Name: Test User
   Password: testpassword123
   ```
4. Click **"Sign up"**
5. **IT SHOULD WORK!** 🎉

### Test 3: Login
1. Use the same credentials
2. You should see the home page (even if no videos yet)

---

## ✅ SUCCESS CHECKLIST

- [ ] Supabase project created
- [ ] Project URL and anon key copied
- [ ] `backend/.env` updated with real credentials
- [ ] SQL schema executed successfully in Supabase
- [ ] All 11 tables visible in Supabase Table Editor
- [ ] Backend restarted (NO Supabase warning)
- [ ] Signup works without errors
- [ ] Login works without errors

---

## 🆘 TROUBLESHOOTING

### Problem: "Failed to create user" error

**Solution:**
1. Check `backend/.env` - make sure NO placeholder text remains
2. Verify anon key is complete (starts with `eyJ` and is very long)
3. Make sure SQL schema ran successfully
4. Restart backend server

### Problem: Backend still shows Supabase warning

**Solution:**
1. Double-check `.env` file was saved
2. Make sure you're editing `backend/.env` not `backend/.env.example`
3. Restart the backend server completely

### Problem: SQL Editor shows errors

**Solution:**
1. Make sure you copied the ENTIRE `SUPABASE_SCHEMA.sql` file
2. Try running the SQL again
3. Check if tables already exist (might just be duplicate warnings)

### Problem: Can't find SQL Editor in Supabase

**Solution:**
- Look for "SQL Editor" icon in the left sidebar
- Or go to: https://supabase.com/dashboard/project/YOUR-PROJECT-ID/sql

---

## 🎊 WHAT'S NEXT?

Once everything works:

1. **Upload a video** (use the Upload button)
2. **Test live streaming** (go to Dashboard)
3. **Send gifts** (when viewing videos)
4. **Explore the API** at http://127.0.0.1:8000/docs

---

## 📝 IMPORTANT NOTES

**Your Database Password:**
- You set this when creating the project
- You DON'T need it in `.env` file
- But SAVE IT somewhere - you need it to connect via other tools

**Supabase Free Tier Limits:**
- ✅ 500 MB database storage
- ✅ 2 GB bandwidth per month
- ✅ 50,000 monthly active users
- ✅ Perfect for development & MVP!

**Security:**
- Never commit your `.env` file to GitHub
- The `.env.example` is for reference only
- Your anon key is meant to be used in frontend/backend

---

Need help? Tell me:
1. Which step you're on
2. What error you're seeing
3. Screenshot if possible

Let's get this working! 🚀
