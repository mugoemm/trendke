"""Reset password for a user"""
from app.db import supabase
from app.auth import get_password_hash

# Reset password for newuser@test.com
email = "newuser@test.com"
new_password = "password123"

# Get user
result = supabase.table("users").select("*").eq("email", email).execute()

if result.data:
    user = result.data[0]
    hashed = get_password_hash(new_password)
    
    # Update password
    update = supabase.table("users").update({
        "password_hash": hashed
    }).eq("id", user["id"]).execute()
    
    print(f"✅ Password reset successful!")
    print(f"Email: {email}")
    print(f"New Password: {new_password}")
else:
    print(f"❌ User not found: {email}")
