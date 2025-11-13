# 🚀 Implementation Guide: Advanced Features

## Table of Contents
1. [Video Upload (Cloudinary)](#1-video-upload-cloudinary)
2. [Email Service (SendGrid)](#2-email-service-sendgrid)
3. [Password Reset](#3-password-reset)
4. [Two-Factor Authentication](#4-two-factor-authentication)
5. [Testing](#5-testing)

---

## 1. Video Upload (Cloudinary)

### Step 1: Create Cloudinary Account
1. Go to https://cloudinary.com/users/register/free
2. Sign up for free account (25GB storage + 25GB bandwidth/month)
3. Go to Dashboard → Account Details
4. Copy: Cloud Name, API Key, API Secret

### Step 2: Install Dependencies
```bash
cd backend
pip install cloudinary
```

### Step 3: Configure Environment
Add to `backend/.env`:
```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Step 4: Update Video Upload Endpoint
In `backend/app/video.py`, replace the upload function:

```python
from .video_upload import VideoUploadService

@router.post("/upload", response_model=VideoMetadata)
async def upload_video(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    hashtags: Optional[str] = Form(None),
    video_file: UploadFile = File(...),
    thumbnail: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload video with Cloudinary"""
    video_id = str(uuid.uuid4())
    
    # Upload to Cloudinary
    upload_result = await VideoUploadService.upload_video(
        video_file=video_file,
        user_id=current_user["id"],
        title=title,
        public_id=video_id
    )
    
    # Save to database
    video_data = {
        "id": video_id,
        "user_id": current_user["id"],
        "title": title,
        "description": description,
        "video_url": upload_result["video_url"],
        "thumbnail_url": upload_result["thumbnail_url"],
        "hashtags": [tag.strip() for tag in hashtags.split(",")] if hashtags else [],
        "views_count": 0,
        "likes_count": 0,
        "comments_count": 0,
        "shares_count": 0
    }
    
    created_video = db.create_video(video_data)
    # ... rest of the code
```

### Alternative: AWS S3 (If you prefer)
```bash
pip install boto3
```

Use `S3VideoUploadService` from `video_upload.py` instead.

---

## 2. Email Service (SendGrid)

### Step 1: Create SendGrid Account
1. Go to https://signup.sendgrid.com/
2. Sign up for free (100 emails/day)
3. Verify your email
4. Go to Settings → API Keys → Create API Key
5. Choose "Restricted Access" → Mail Send (Full Access)
6. Copy the API key (only shown once!)

### Step 2: Verify Sender Email
1. Go to Settings → Sender Authentication
2. Click "Verify a Single Sender"
3. Fill in your email details
4. Check your email and verify

### Step 3: Install Dependencies
```bash
pip install sendgrid
```

### Step 4: Configure Environment
Add to `backend/.env`:
```env
SENDGRID_API_KEY=SG.your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com  # Must match verified sender
FRONTEND_URL=http://localhost:5175
```

### Step 5: Register Extended Auth Routes
In `backend/app/main.py`:
```python
from .auth_extended import router as auth_extended_router

app.include_router(auth_extended_router)
```

### Step 6: Run Database Schema
1. Open Supabase SQL Editor
2. Run `EXTENDED_SCHEMA.sql`
3. Verify tables created: `email_verifications`, `password_resets`, `two_factor_codes`

---

## 3. Password Reset

### Backend is Ready! Now Create Frontend Pages:

#### Create `frontend/src/pages/ForgotPassword.jsx`:
```jsx
import React, { useState } from 'react';
import { forgotPassword } from '../api/authApi';
import toast from 'react-hot-toast';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await forgotPassword(email);
      setSent(true);
      toast.success('Reset link sent! Check your email.');
    } catch (error) {
      toast.error('Failed to send reset link');
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-center">
          <div className="text-6xl mb-4">📧</div>
          <h2 className="text-2xl font-bold text-white mb-2">Check Your Email</h2>
          <p className="text-gray-400">We've sent a password reset link to {email}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 px-4">
      <div className="max-w-md w-full bg-gray-900 rounded-2xl p-8">
        <h2 className="text-3xl font-bold text-white mb-2">Forgot Password?</h2>
        <p className="text-gray-400 mb-6">Enter your email to receive a reset link</p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-pink-500"
            required
          />
          
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-lg hover:shadow-xl transition-all disabled:opacity-50"
          >
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>
        
        <div className="mt-4 text-center">
          <a href="/login" className="text-pink-500 hover:underline">
            Back to Login
          </a>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
```

#### Create `frontend/src/pages/ResetPassword.jsx`:
```jsx
import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { resetPassword } from '../api/authApi';
import toast from 'react-hot-toast';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      toast.error('Invalid reset link');
      navigate('/login');
    }
  }, [token, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    
    if (password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }
    
    setLoading(true);
    
    try {
      await resetPassword(token, password);
      toast.success('Password reset successfully!');
      navigate('/login');
    } catch (error) {
      toast.error('Failed to reset password. Link may be expired.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 px-4">
      <div className="max-w-md w-full bg-gray-900 rounded-2xl p-8">
        <h2 className="text-3xl font-bold text-white mb-2">Reset Password</h2>
        <p className="text-gray-400 mb-6">Enter your new password</p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="New password"
            className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-pink-500"
            required
          />
          
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm password"
            className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-pink-500"
            required
          />
          
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-lg hover:shadow-xl transition-all disabled:opacity-50"
          >
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
```

#### Add API functions to `frontend/src/api/authApi.js`:
```javascript
export const forgotPassword = async (email) => {
  const response = await fetch(`${API_URL}/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  if (!response.ok) throw new Error('Failed');
  return response.json();
};

export const resetPassword = async (token, new_password) => {
  const response = await fetch(`${API_URL}/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password })
  });
  if (!response.ok) throw new Error('Failed');
  return response.json();
};
```

---

## 4. Two-Factor Authentication (2FA)

### Frontend Implementation:

#### Add to `frontend/src/pages/Profile.jsx`:
```jsx
import { toggle2FA } from '../api/authApi';

const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);

const handle2FAToggle = async () => {
  try {
    await toggle2FA(!twoFactorEnabled);
    setTwoFactorEnabled(!twoFactorEnabled);
    toast.success(`2FA ${!twoFactorEnabled ? 'enabled' : 'disabled'}`);
  } catch (error) {
    toast.error('Failed to update 2FA');
  }
};

// In your JSX:
<div className="flex items-center justify-between p-4 bg-gray-900 rounded-lg">
  <div>
    <h3 className="font-semibold text-white">Two-Factor Authentication</h3>
    <p className="text-sm text-gray-400">Extra security for your account</p>
  </div>
  <button
    onClick={handle2FAToggle}
    className={`px-4 py-2 rounded-lg font-semibold ${
      twoFactorEnabled
        ? 'bg-green-500 text-white'
        : 'bg-gray-700 text-gray-300'
    }`}
  >
    {twoFactorEnabled ? 'Enabled' : 'Disabled'}
  </button>
</div>
```

---

## 5. Testing

### Test Video Upload:
```bash
# In terminal
cd backend
python -c "
from app.video_upload import VideoUploadService
print('Cloudinary configured:', VideoUploadService is not None)
"
```

### Test Email Service:
```bash
cd backend
python -c "
from app.email_service import EmailService
service = EmailService()
print('SendGrid configured:', service.client is not None)
"
```

### Manual Testing:
1. **Sign up** → Check email for verification link
2. **Forgot Password** → Check email for reset link
3. **Upload Video** → Should upload to Cloudinary
4. **Enable 2FA** → Try logging in with code

---

## 📋 Quick Checklist

### Video Upload:
- [ ] Cloudinary account created
- [ ] Environment variables added
- [ ] `pip install cloudinary`
- [ ] Updated video.py upload function

### Email Service:
- [ ] SendGrid account created
- [ ] Sender email verified
- [ ] Environment variables added
- [ ] `pip install sendgrid`
- [ ] Extended schema run in Supabase
- [ ] Auth extended routes registered

### Frontend:
- [ ] ForgotPassword page created
- [ ] ResetPassword page created
- [ ] Routes added to App.jsx
- [ ] API functions added
- [ ] 2FA toggle in Profile

---

## 🚨 Common Issues

**Emails not sending?**
- Check SendGrid API key is correct
- Verify sender email in SendGrid
- Check `FROM_EMAIL` matches verified sender
- Look for errors in terminal

**Video upload failing?**
- Verify Cloudinary credentials
- Check file size (Cloudinary free tier: 100MB max)
- Ensure video format is supported (mp4, mov, avi)

**Database errors?**
- Run `EXTENDED_SCHEMA.sql` in Supabase
- Check Supabase is configured
- Verify tables exist in Supabase dashboard

---

## 💰 Cost Estimates (Free Tiers)

| Service | Free Tier | Upgrade Cost |
|---------|-----------|--------------|
| Cloudinary | 25GB storage, 25GB bandwidth/month | $99/month for 275GB |
| SendGrid | 100 emails/day | $19.95/month for 50k emails |
| Supabase | 500MB database, 2GB bandwidth | $25/month for 8GB |

All services have generous free tiers perfect for MVP and early growth!
