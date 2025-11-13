#!/bin/bash

# TrendKe Quick Deployment Script
# This script helps you prepare for deployment

echo "🚀 TrendKe Deployment Preparation"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the trendke root directory"
    exit 1
fi

echo "✅ Directory structure verified"
echo ""

# Check backend files
echo "📦 Checking backend files..."
if [ -f "backend/requirements.txt" ]; then
    echo "  ✅ requirements.txt found"
else
    echo "  ❌ requirements.txt missing"
fi

if [ -f "backend/render.yaml" ]; then
    echo "  ✅ render.yaml found"
else
    echo "  ❌ render.yaml missing"
fi

echo ""

# Check frontend files
echo "📦 Checking frontend files..."
if [ -f "frontend/vercel.json" ]; then
    echo "  ✅ vercel.json found"
else
    echo "  ❌ vercel.json missing"
fi

if [ -f "frontend/package.json" ]; then
    echo "  ✅ package.json found"
else
    echo "  ❌ package.json missing"
fi

echo ""

# Check documentation
echo "📚 Checking documentation..."
if [ -f "DEPLOYMENT.md" ]; then
    echo "  ✅ DEPLOYMENT.md found"
else
    echo "  ❌ DEPLOYMENT.md missing"
fi

if [ -f "ENV_SETUP.md" ]; then
    echo "  ✅ ENV_SETUP.md found"
else
    echo "  ❌ ENV_SETUP.md missing"
fi

if [ -f "PRE_DEPLOYMENT_CHECKLIST.md" ]; then
    echo "  ✅ PRE_DEPLOYMENT_CHECKLIST.md found"
else
    echo "  ❌ PRE_DEPLOYMENT_CHECKLIST.md missing"
fi

echo ""

# Check git status
echo "📝 Checking git status..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "  ✅ Git repository initialized"
    
    # Check if there are uncommitted changes
    if [[ -z $(git status -s) ]]; then
        echo "  ✅ No uncommitted changes"
    else
        echo "  ⚠️  You have uncommitted changes"
        echo ""
        echo "  Uncommitted files:"
        git status -s
        echo ""
        echo "  Run: git add . && git commit -m 'Prepare for deployment'"
    fi
    
    # Check if remote is set
    if git remote -v | grep -q origin; then
        echo "  ✅ Git remote 'origin' configured"
        git remote -v | grep origin
    else
        echo "  ⚠️  No git remote configured"
        echo "  Run: git remote add origin https://github.com/YOUR_USERNAME/trendke.git"
    fi
else
    echo "  ❌ Not a git repository"
    echo "  Run: git init"
fi

echo ""
echo "=================================="
echo "📋 Next Steps:"
echo ""
echo "1. Review PRE_DEPLOYMENT_CHECKLIST.md"
echo "2. Ensure all environment variables are ready (see ENV_SETUP.md)"
echo "3. Push code to GitHub: git push origin main"
echo "4. Follow DEPLOYMENT.md for deployment instructions"
echo ""
echo "📚 Documentation:"
echo "  - DEPLOYMENT.md - Full deployment guide"
echo "  - ENV_SETUP.md - Environment variables"
echo "  - PRE_DEPLOYMENT_CHECKLIST.md - Pre-flight checklist"
echo ""
echo "✨ Good luck with your deployment!"
