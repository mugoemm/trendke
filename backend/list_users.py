from app.db import supabase

users = supabase.table('users').select('email, username').execute()
print('\n📧 Available accounts:')
for u in users.data:
    print(f'  Email: {u["email"]} | Username: {u["username"]}')
print()
