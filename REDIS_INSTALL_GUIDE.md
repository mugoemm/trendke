# Redis Installation and Setup Guide for Windows

## Current Status
❌ Redis is NOT installed on your system

## Option 1: Use Docker Redis (Recommended - Already Running!)

You already have Redis running in Docker. Just use it:

```powershell
# Check if Redis Docker container is running
docker ps | Select-String redis

# If not running, start it:
docker start redis-trendke

# Your Python backend is already configured to use localhost:6379
# So this will work automatically!
```

## Option 2: Install Redis on Windows (WSL)

1. **Install WSL** (if not already installed):
```powershell
wsl --install
```

2. **Install Redis in WSL**:
```powershell
wsl
sudo apt update
sudo apt install redis-server -y
```

3. **Start Redis**:
```powershell
wsl redis-server --daemonize yes
```

4. **Test Redis**:
```powershell
wsl redis-cli ping
# Should return: PONG
```

## Option 3: Install Redis Native Windows Build

1. Download from: https://github.com/microsoftarchive/redis/releases
2. Download: `Redis-x64-3.0.504.msi`
3. Install and start Redis service

## Quick Start (Use Existing Docker Redis)

Since you already have Redis in Docker, just run:

```powershell
# 1. Start Redis container
docker start redis-trendke

# 2. Verify it's running
docker ps | Select-String redis

# 3. Test connection
docker exec redis-trendke redis-cli ping

# 4. Start your backend (it will connect automatically)
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

## Using the Startup Scripts

Once Redis is running, use these scripts to start everything:

### Windows Command Prompt:
```cmd
start-all.bat
```

### PowerShell:
```powershell
.\start-all.ps1
```

## Manual Start (If Scripts Don't Work)

**Terminal 1 - Start Redis:**
```powershell
docker start redis-trendke
```

**Terminal 2 - Start Backend:**
```powershell
cd "D:\My projects\trendke\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

**Terminal 3 - Start Frontend:**
```powershell
cd "D:\My projects\trendke\frontend"
npm run dev
```

## Troubleshooting

### Redis connection refused
```powershell
# Check if Redis is running
docker ps | Select-String redis

# Check port 6379
Test-NetConnection -ComputerName localhost -Port 6379

# Restart Redis
docker restart redis-trendke
```

### Backend can't connect to Redis
- Make sure Redis is running first
- Check backend/.env has: `REDIS_HOST=localhost` and `REDIS_PORT=6379`
- Redis Docker container should map port 6379:6379

---

**Recommended:** Use your existing Docker Redis container. It's already configured and working!
