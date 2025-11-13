# TrendKe Deployment Preparation Script (PowerShell)
# Run this with: .\check_deployment_ready.ps1

Write-Host "🚀 TrendKe Deployment Preparation" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ Error: Please run this script from the trendke root directory" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Directory structure verified" -ForegroundColor Green
Write-Host ""

# Check backend files
Write-Host "📦 Checking backend files..." -ForegroundColor Yellow
if (Test-Path "backend/requirements.txt") {
    Write-Host "  ✅ requirements.txt found" -ForegroundColor Green
} else {
    Write-Host "  ❌ requirements.txt missing" -ForegroundColor Red
}

if (Test-Path "backend/render.yaml") {
    Write-Host "  ✅ render.yaml found" -ForegroundColor Green
} else {
    Write-Host "  ❌ render.yaml missing" -ForegroundColor Red
}

Write-Host ""

# Check frontend files
Write-Host "📦 Checking frontend files..." -ForegroundColor Yellow
if (Test-Path "frontend/vercel.json") {
    Write-Host "  ✅ vercel.json found" -ForegroundColor Green
} else {
    Write-Host "  ❌ vercel.json missing" -ForegroundColor Red
}

if (Test-Path "frontend/package.json") {
    Write-Host "  ✅ package.json found" -ForegroundColor Green
} else {
    Write-Host "  ❌ package.json missing" -ForegroundColor Red
}

Write-Host ""

# Check documentation
Write-Host "📚 Checking documentation..." -ForegroundColor Yellow
if (Test-Path "DEPLOYMENT.md") {
    Write-Host "  ✅ DEPLOYMENT.md found" -ForegroundColor Green
} else {
    Write-Host "  ❌ DEPLOYMENT.md missing" -ForegroundColor Red
}

if (Test-Path "ENV_SETUP.md") {
    Write-Host "  ✅ ENV_SETUP.md found" -ForegroundColor Green
} else {
    Write-Host "  ❌ ENV_SETUP.md missing" -ForegroundColor Red
}

if (Test-Path "PRE_DEPLOYMENT_CHECKLIST.md") {
    Write-Host "  ✅ PRE_DEPLOYMENT_CHECKLIST.md found" -ForegroundColor Green
} else {
    Write-Host "  ❌ PRE_DEPLOYMENT_CHECKLIST.md missing" -ForegroundColor Red
}

Write-Host ""

# Check git status
Write-Host "📝 Checking git status..." -ForegroundColor Yellow
try {
    $null = git rev-parse --git-dir 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Git repository initialized" -ForegroundColor Green
        
        # Check if there are uncommitted changes
        $changes = git status -s
        if ([string]::IsNullOrWhiteSpace($changes)) {
            Write-Host "  ✅ No uncommitted changes" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  You have uncommitted changes" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "  Uncommitted files:" -ForegroundColor Yellow
            git status -s
            Write-Host ""
            Write-Host "  Run: git add . ; git commit -m 'Prepare for deployment'" -ForegroundColor Yellow
        }
        
        # Check if remote is set
        $remotes = git remote -v
        if ($remotes -match "origin") {
            Write-Host "  ✅ Git remote 'origin' configured" -ForegroundColor Green
            git remote -v | Select-String "origin"
        } else {
            Write-Host "  ⚠️  No git remote configured" -ForegroundColor Yellow
            Write-Host "  Run: git remote add origin https://github.com/YOUR_USERNAME/trendke.git" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ❌ Not a git repository" -ForegroundColor Red
    Write-Host "  Run: git init" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Review PRE_DEPLOYMENT_CHECKLIST.md"
Write-Host "2. Ensure all environment variables are ready - see ENV_SETUP.md"
Write-Host "3. Push code to GitHub: git push origin main"
Write-Host "4. Follow DEPLOYMENT.md for deployment instructions"
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "  - DEPLOYMENT.md - Full deployment guide"
Write-Host "  - ENV_SETUP.md - Environment variables"
Write-Host "  - PRE_DEPLOYMENT_CHECKLIST.md - Pre-flight checklist"
Write-Host ""
Write-Host "✨ Good luck with your deployment!" -ForegroundColor Green
