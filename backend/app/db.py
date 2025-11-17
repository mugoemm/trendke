import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Check if Supabase is configured with real values
if not SUPABASE_URL or not SUPABASE_KEY or \
   "your-project-id" in SUPABASE_URL or "your-supabase" in SUPABASE_KEY:
    print("=" * 80)
    print("⚠️  WARNING: SUPABASE NOT CONFIGURED!")
    print("=" * 80)
    print("Database operations will fail until you configure Supabase.")
    print("\nTo fix this:")
    print("1. Go to https://supabase.com and create a project")
    print("2. Copy your project URL and anon key")
    print("3. Update backend/.env with:")
    print("   SUPABASE_URL=https://your-actual-project.supabase.co")
    print("   SUPABASE_KEY=your-actual-anon-key")
    print("4. Run the database_schema.sql in Supabase SQL Editor")
    print("5. Restart the backend server")
    print("=" * 80)
    # Use placeholder that won't crash immediately but will fail on actual use
    SUPABASE_URL = "https://placeholder.supabase.co"
    SUPABASE_KEY = "placeholder-key"

try:
    # Create client with minimal options to avoid proxy parameter issues
    from supabase.lib.client_options import ClientOptions
    options = ClientOptions(
        schema="public",
        auto_refresh_token=True,
        persist_session=True
    )
    supabase: Client = create_client(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY,
        options=options
    )
except Exception as e:
    print(f"⚠️  Failed to initialize Supabase client: {e}")
    print("Attempting fallback initialization...")
    try:
        # Fallback: simple initialization
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e2:
        print(f"⚠️  Fallback also failed: {e2}")
        print("Using placeholder - database operations will fail.")
        supabase = None


class DatabaseHelper:
    """Helper class for common database operations"""
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if not supabase:
            print("❌ Supabase not configured. Please set up your database.")
            return None
        try:
            response = supabase.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except IndexError:
            return None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        if not supabase:
            print("❌ Supabase not configured. Please set up your database.")
            return None
        try:
            response = supabase.table("users").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except IndexError:
            return None
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        if not supabase:
            print("❌ Supabase not configured. Please set up your database.")
            return None
        try:
            response = supabase.table("users").insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def update_user(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user data"""
        try:
            response = supabase.table("users").update(updates).eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
    
    @staticmethod
    def get_videos_feed(limit: int = 20, offset: int = 0, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get video feed with pagination"""
        try:
            query = supabase.table("videos").select("""
                *,
                users!videos_user_id_fkey (username, avatar_url)
            """).order("created_at", desc=True).range(offset, offset + limit - 1)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error fetching video feed: {e}")
            return []
    
    @staticmethod
    def get_video_by_id(video_id: str) -> Optional[Dict[str, Any]]:
        """Get video by ID with user info"""
        try:
            response = supabase.table("videos").select("""
                *,
                users!videos_user_id_fkey (username, avatar_url)
            """).eq("id", video_id).single().execute()
            return response.data
        except Exception as e:
            print(f"Error fetching video: {e}")
            return None
    
    @staticmethod
    def create_video(video_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create video metadata"""
        try:
            response = supabase.table("videos").insert(video_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating video: {e}")
            return None
    
    @staticmethod
    def increment_video_views(video_id: str) -> bool:
        """Increment video view count"""
        try:
            supabase.rpc("increment_views", {"video_id": video_id}).execute()
            return True
        except Exception as e:
            print(f"Error incrementing views: {e}")
            return False
    
    @staticmethod
    def get_live_sessions(status: str = "active") -> List[Dict[str, Any]]:
        """Get live sessions by status"""
        try:
            response = supabase.table("live_sessions").select("""
                *,
                users!live_sessions_host_id_fkey (username, avatar_url)
            """).eq("status", status).order("started_at", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching live sessions: {e}")
            return []
    
    @staticmethod
    def create_live_session(session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a live session"""
        try:
            response = supabase.table("live_sessions").insert(session_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating live session: {e}")
            return None
    
    @staticmethod
    def update_live_session(session_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update live session"""
        try:
            response = supabase.table("live_sessions").update(updates).eq("id", session_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating live session: {e}")
            return None
    
    @staticmethod
    def create_gift_transaction(transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create gift transaction"""
        try:
            response = supabase.table("gift_transactions").insert(transaction_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating gift transaction: {e}")
            return None
    
    @staticmethod
    def update_user_balance(user_id: str, coin_delta: int, earnings_delta: float = 0) -> bool:
        """Update user coin balance and earnings"""
        try:
            user = DatabaseHelper.get_user_by_id(user_id)
            if not user:
                return False
            
            new_balance = user.get("coin_balance", 0) + coin_delta
            new_earnings = user.get("total_earnings", 0) + earnings_delta
            
            supabase.table("users").update({
                "coin_balance": new_balance,
                "total_earnings": new_earnings
            }).eq("id", user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating user balance: {e}")
            return False
    
    @staticmethod
    def get_gift_types() -> List[Dict[str, Any]]:
        """Get all gift types"""
        try:
            response = supabase.table("gift_types").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching gift types: {e}")
            return []
    
    @staticmethod
    def get_leaderboard(limit: int = 50) -> List[Dict[str, Any]]:
        """Get creator leaderboard by earnings"""
        try:
            response = supabase.table("users").select(
                "id, username, avatar_url, total_earnings"
            ).order("total_earnings", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
            return []
    
    @staticmethod
    def create_notification(notification_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a notification"""
        try:
            response = supabase.table("notifications").insert(notification_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def get_user_notifications(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user notifications"""
        try:
            response = supabase.table("notifications").select("*").eq(
                "user_id", user_id
            ).order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching notifications: {e}")
            return []


# Export singleton instance
db = DatabaseHelper()
