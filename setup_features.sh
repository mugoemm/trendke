#!/bin/bash
# Quick setup script for advanced features

echo "🚀 TrendKe Advanced Features Setup"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📦 Installing Python dependencies..."
cd backend

pip install cloudinary sendgrid || {
    echo "❌ Failed to install dependencies"
    exit 1
}

echo "✅ Dependencies installed"
echo ""

echo "📝 Next steps:"
echo ""
echo "1. CREATE ACCOUNTS:"
echo "   - Cloudinary: https://cloudinary.com/users/register/free"
echo "   - SendGrid: https://signup.sendgrid.com/"
echo ""
echo "2. UPDATE backend/.env WITH:"
echo "   CLOUDINARY_CLOUD_NAME=your-cloud-name"
echo "   CLOUDINARY_API_KEY=your-api-key"
echo "   CLOUDINARY_API_SECRET=your-api-secret"
echo "   SENDGRID_API_KEY=your-sendgrid-api-key"
echo "   FROM_EMAIL=your-verified-email"
echo "   FRONTEND_URL=http://localhost:5175"
echo ""
echo "3. RUN EXTENDED_SCHEMA.sql IN SUPABASE"
echo "   - Open Supabase SQL Editor"
echo "   - Copy contents of backend/EXTENDED_SCHEMA.sql"
echo "   - Execute the SQL"
echo ""
echo "4. UPDATE backend/app/main.py:"
echo "   from .auth_extended import router as auth_extended_router"
echo "   app.include_router(auth_extended_router)"
echo ""
echo "5. RESTART SERVERS"
echo ""
echo "📖 Full guide: IMPLEMENTATION_GUIDE.md"
echo ""
echo "✨ Setup script completed!"
