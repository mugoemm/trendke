# TrendKe Deployment Readiness Check (PowerShell)
# Run this with: .\check_deployment.ps1

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "TrendKe Deployment Preparation Check" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "[ERROR] Please run this script from the trendke root directory" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Directory structure verified" -ForegroundColor Green
Write-Host ""

# Check backend files
Write-Host "Checking backend files..." -ForegroundColor Yellow
$backendOK = $true

if (Test-Path "backend/requirements.txt") {
    Write-Host "  [OK] requirements.txt found" -ForegroundColor Green
} else {
    Write-Host "  [MISSING] requirements.txt" -ForegroundColor Red
    $backendOK = $false
}

if (Test-Path "backend/render.yaml") {
    Write-Host "  [OK] render.yaml found" -ForegroundColor Green
} else {
    Write-Host "  [MISSING] render.yaml" -ForegroundColor Red
    $backendOK = $false
}

Write-Host ""

# Check frontend files
Write-Host "Checking frontend files..." -ForegroundColor Yellow
$frontendOK = $true

if (Test-Path "frontend/vercel.json") {
    Write-Host "  [OK] vercel.json found" -ForegroundColor Green
} else {
    Write-Host "  [MISSING] vercel.json" -ForegroundColor Red
    $frontendOK = $false
}

if (Test-Path "frontend/package.json") {
    Write-Host "  [OK] package.json found" -ForegroundColor Green
} else {
    Write-Host "  [MISSING] package.json" -ForegroundColor Red
    $frontendOK = $false
}

Write-Host ""

# Check documentation
Write-Host "Checking documentation..." -ForegroundColor Yellow
$docsOK = $true

$docFiles = @(
    "DEPLOYMENT.md",
    "ENV_SETUP.md",
    "PRE_DEPLOYMENT_CHECKLIST.md",
    "QUICK_START_DEPLOY.md",
    "DEPLOYMENT_PACKAGE.md"
)

foreach ($doc in $docFiles) {
    if (Test-Path $doc) {
        Write-Host "  [OK] $doc found" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $doc" -ForegroundColor Red
        $docsOK = $false
    }
}

Write-Host ""

# Check git status
Write-Host "Checking git status..." -ForegroundColor Yellow
try {
    $null = git rev-parse --git-dir 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Git repository initialized" -ForegroundColor Green
        
        # Check if there are uncommitted changes
        $changes = git status -s
        if ([string]::IsNullOrWhiteSpace($changes)) {
            Write-Host "  [OK] No uncommitted changes" -ForegroundColor Green
        } else {
            Write-Host "  [WARNING] You have uncommitted changes" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "  Uncommitted files:" -ForegroundColor Yellow
            git status -s
            Write-Host ""
            Write-Host "  Run: git add . ; git commit -m 'Prepare for deployment'" -ForegroundColor Yellow
        }
        
        # Check if remote is set
        $remotes = git remote -v 2>&1
        if ($remotes -match "origin") {
            Write-Host "  [OK] Git remote 'origin' configured" -ForegroundColor Green
        } else {
            Write-Host "  [WARNING] No git remote configured" -ForegroundColor Yellow
            Write-Host "  Run: git remote add origin https://github.com/YOUR_USERNAME/trendke.git" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  [ERROR] Not a git repository" -ForegroundColor Red
    Write-Host "  Run: git init" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

if ($backendOK) {
    Write-Host "[OK] Backend files ready" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Backend files incomplete" -ForegroundColor Red
}

if ($frontendOK) {
    Write-Host "[OK] Frontend files ready" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Frontend files incomplete" -ForegroundColor Red
}

if ($docsOK) {
    Write-Host "[OK] Documentation complete" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Documentation incomplete" -ForegroundColor Red
}

Write-Host ""

if ($backendOK -and $frontendOK -and $docsOK) {
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "READY FOR DEPLOYMENT!" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
} else {
    Write-Host "====================================" -ForegroundColor Red
    Write-Host "NOT READY - Please fix issues above" -ForegroundColor Red
    Write-Host "====================================" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review PRE_DEPLOYMENT_CHECKLIST.md"
Write-Host "  2. Ensure all environment variables are ready (see ENV_SETUP.md)"
Write-Host "  3. Push code to GitHub: git push origin main"
Write-Host "  4. Follow QUICK_START_DEPLOY.md for deployment"
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  - QUICK_START_DEPLOY.md - Quick deployment guide (START HERE)"
Write-Host "  - DEPLOYMENT.md - Full deployment guide"
Write-Host "  - ENV_SETUP.md - Environment variables"
Write-Host "  - PRE_DEPLOYMENT_CHECKLIST.md - Pre-flight checklist"
Write-Host "  - DEPLOYMENT_PACKAGE.md - Complete package overview"
Write-Host ""
