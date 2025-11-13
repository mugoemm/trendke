from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

from .models import UserCreate, UserLogin, UserProfile, UserRole
from .db import supabase, db

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        # bcrypt automatically handles passwords up to 72 bytes
        password_bytes = plain_password.encode('utf-8')
        # Truncate to 72 bytes if needed
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password"""
    try:
        # Convert password to bytes and truncate to 72 bytes if needed
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload (for WebSocket use)"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Validate JWT token and return current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """Validate JWT token and return current user, or None if not authenticated"""
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        user = db.get_user_by_id(user_id)
        return user
    except JWTError:
        return None


@router.post("/signup", response_model=dict)
async def signup(user_data: UserCreate):
    """Register a new user"""
    try:
        # Validate and truncate password to 72 bytes for bcrypt
        password_bytes = user_data.password.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncate at 72 bytes
            truncated = password_bytes[:72]
            # Handle potential incomplete UTF-8 sequences
            while len(truncated) > 0:
                try:
                    user_data.password = truncated.decode('utf-8')
                    break
                except UnicodeDecodeError:
                    truncated = truncated[:-1]
        
        # Check if user already exists
        existing_user = db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username is taken
        try:
            if supabase:
                username_check = supabase.table("users").select("id").eq("username", user_data.username).execute()
                if username_check.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
        except HTTPException:
            raise
        except Exception as e:
            pass
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user in database
        new_user_data = {
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "password_hash": hashed_password,
            "role": UserRole.USER,
            "coin_balance": 0,
            "total_earnings": 0.0,
            "followers_count": 0,
            "following_count": 0
        }
        
        user = db.create_user(new_user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user. Please check if Supabase is configured correctly in backend/.env"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user["id"]})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user.get("full_name"),
                "role": user["role"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed. Please ensure Supabase is configured in backend/.env. Error: {str(e)}"
        )


@router.post("/login", response_model=dict)
async def login(credentials: UserLogin):
    """Login user"""
    try:
        # Validate and truncate password to 72 bytes for bcrypt
        password_bytes = credentials.password.encode('utf-8')
        if len(password_bytes) > 72:
            truncated = password_bytes[:72]
            while len(truncated) > 0:
                try:
                    credentials.password = truncated.decode('utf-8')
                    break
                except UnicodeDecodeError:
                    truncated = truncated[:-1]
        
        # Get user by email
        user = db.get_user_by_email(credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password. If this is a new setup, please configure Supabase first."
            )
        
        # Verify password
        if not verify_password(credentials.password, user.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user["id"]})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user.get("full_name"),
                "role": user["role"],
                "coin_balance": user.get("coin_balance", 0)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed. Please ensure Supabase is configured in backend/.env. Error: {str(e)}"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        username=current_user["username"],
        full_name=current_user.get("full_name"),
        avatar_url=current_user.get("avatar_url"),
        bio=current_user.get("bio"),
        role=current_user.get("role", UserRole.USER),
        coin_balance=current_user.get("coin_balance", 0),
        total_earnings=current_user.get("total_earnings", 0.0),
        followers_count=current_user.get("followers_count", 0),
        following_count=current_user.get("following_count", 0),
        created_at=current_user["created_at"]
    )


@router.get("/user/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        full_name=user.get("full_name"),
        avatar_url=user.get("avatar_url"),
        bio=user.get("bio"),
        role=user.get("role", UserRole.USER),
        coin_balance=user.get("coin_balance", 0),
        total_earnings=user.get("total_earnings", 0.0),
        followers_count=user.get("followers_count", 0),
        following_count=user.get("following_count", 0),
        created_at=user["created_at"]
    )
