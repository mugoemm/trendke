# TrendKe Frontend

React + Vite frontend for TrendKe - A TikTok-style social media platform.

## 🚀 Quick Start (Local Development)

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Environment Setup

Create `.env` file with:

```bash
VITE_API_URL=http://localhost:8000
```

### Run Dev Server

```bash
npm run dev
```

Access at: http://localhost:5173

## 📦 Production Deployment

See [DEPLOYMENT.md](../DEPLOYMENT.md) for complete deployment instructions to Vercel.

### Key Files for Deployment:

- `vercel.json` - Vercel configuration
- `package.json` - Dependencies and build scripts
- `.env.production.example` - Production env template

### Build for Production

```bash
npm run build
```

Output in `dist/` directory.

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── authApi.js       # Authentication API
│   │   ├── videoApi.js      # Video API
│   │   ├── socialApi.js     # Social features API
│   │   └── giftsApi.js      # Gifts API
│   ├── components/
│   │   ├── Navbar.jsx       # Bottom navigation
│   │   ├── VideoPlayer.jsx  # Video player with controls
│   │   ├── VideoFeed.jsx    # Infinite scroll feed
│   │   └── UploadVideo.jsx  # Upload with progress
│   ├── pages/
│   │   ├── Home.jsx         # Video feed page
│   │   ├── Profile.jsx      # User profile
│   │   ├── Explore.jsx      # Trending videos
│   │   ├── Following.jsx    # Following feed
│   │   ├── Login.jsx        # Login page
│   │   └── Signup.jsx       # Signup page
│   ├── App.jsx              # Routes & layout
│   └── main.jsx             # Entry point
├── vercel.json              # Vercel config
└── package.json             # Dependencies
```

## 🎨 Features

- ✅ TikTok-style vertical scrolling
- ✅ Video player with mute/unmute
- ✅ Double-tap to like
- ✅ Upload with progress indicator
- ✅ Profile with clickable video grid
- ✅ Trending/Explore page
- ✅ Follow/unfollow system
- ✅ Comments & likes
- ✅ Virtual gifts
- ✅ Responsive design

## 🛠️ Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client
- **React Hot Toast** - Notifications
- **React Icons** - Icon library
- **Tailwind CSS** - Styling (via index.css)

## 📱 Pages

### Public Routes
- `/` - Home (video feed)
- `/login` - Login
- `/signup` - Signup

### Protected Routes
- `/profile/:userId?` - User profile
- `/dashboard` - Creator dashboard
- `/following` - Following feed
- `/explore` - Trending videos
- `/upload` - Upload video
- `/live/:sessionId` - Live streaming

## 🔧 Development

### Available Scripts

```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Lint code
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## 🚀 Deployment to Vercel

1. Push code to GitHub
2. Import project in Vercel
3. Set `VITE_API_URL` environment variable
4. Deploy!

Vercel will auto-detect Vite and configure everything.

## 🎨 Customization

### Styling

- Main styles in `src/index.css`
- Tailwind utility classes used throughout
- Dark theme by default

### API Configuration

- API base URL from `VITE_API_URL`
- Axios interceptors handle auth tokens
- Automatic redirect on 401 (unauthorized)

## 📝 License

MIT
