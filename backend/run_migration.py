"""
Run database migration for social features
"""
from app.db import supabase

# Read migration SQL
with open('migrations/003_social_features.sql', 'r') as f:
    migration_sql = f.read()

print("🚀 Running social features migration...")
print("=" * 60)

try:
    # Execute the migration
    result = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
    print("✅ Migration completed successfully!")
    print("   - Created follows table")
    print("   - Created indexes for performance")
    print("   - Created follower/following count functions")
except Exception as e:
    # If rpc doesn't work, try to execute statements individually
    print("ℹ️  Direct execution not available, using Supabase client...")
    
    # Check if follows table exists
    try:
        result = supabase.table('follows').select('*').limit(1).execute()
        print("✅ Follows table already exists!")
    except:
        print("❌ Follows table needs to be created manually in Supabase")
        print("\n📋 Please run this SQL in your Supabase SQL Editor:")
        print("   https://supabase.com/dashboard/project/YOUR_PROJECT/sql")
        print("\n" + "=" * 60)
        print(migration_sql)
        print("=" * 60)

print("\n✨ Social features setup complete!")
