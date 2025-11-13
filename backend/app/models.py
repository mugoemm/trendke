from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    CREATOR = "creator"
    ADMIN = "admin"


class LiveSessionType(str, Enum):
    VOICE = "voice"
    CAMERA = "camera"
    STUDIO = "studio"


class LiveSessionStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"
    SCHEDULED = "scheduled"


# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72, description="Password must be 6-72 characters")
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")
    full_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: UserRole = UserRole.USER
    coin_balance: int = 0
    total_earnings: float = 0.0
    followers_count: int = 0
    following_count: int = 0
    created_at: datetime


class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


# Video Models
class VideoUpload(BaseModel):
    title: str
    description: Optional[str] = None
    hashtags: Optional[List[str]] = []
    thumbnail_url: Optional[str] = None


class VideoMetadata(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    video_url: str
    thumbnail_url: Optional[str] = None
    hashtags: List[str] = []
    views_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    created_at: datetime
    
    # User info
    username: Optional[str] = None
    avatar_url: Optional[str] = None


class VideoComment(BaseModel):
    content: str


class VideoCommentResponse(BaseModel):
    id: str
    video_id: str
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    content: str
    created_at: datetime


# Live Session Models
class LiveSessionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    session_type: LiveSessionType
    thumbnail_url: Optional[str] = None
    max_participants: int = 50


class LiveSession(BaseModel):
    id: str
    host_id: str
    host_username: str
    host_avatar_url: Optional[str] = None
    title: str
    description: Optional[str] = None
    session_type: LiveSessionType
    status: LiveSessionStatus
    thumbnail_url: Optional[str] = None
    access_token: Optional[str] = None
    viewer_count: int = 0
    max_participants: int = 50
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime


class LiveJoinRequest(BaseModel):
    session_id: str


class LiveJoinResponse(BaseModel):
    session: LiveSession
    access_token: str
    webrtc_config: dict


# Gift Models
class GiftType(BaseModel):
    id: str
    name: str
    icon_url: str
    coin_cost: int
    animation_url: Optional[str] = None


class SendGiftRequest(BaseModel):
    recipient_id: str
    gift_type_id: str
    amount: int = 1
    video_id: Optional[str] = None
    live_session_id: Optional[str] = None


class GiftTransaction(BaseModel):
    id: str
    sender_id: str
    sender_username: str
    recipient_id: str
    recipient_username: str
    gift_type_id: str
    gift_name: str
    amount: int
    total_coins: int
    creator_earnings: float
    platform_fee: float
    video_id: Optional[str] = None
    live_session_id: Optional[str] = None
    created_at: datetime


class UserBalance(BaseModel):
    user_id: str
    coin_balance: int
    total_earnings: float


class LeaderboardEntry(BaseModel):
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    total_earnings: float
    gifts_received: int
    rank: int


# Payment Models
class CoinPurchaseRequest(BaseModel):
    coin_package_id: str
    payment_method: str = "pesapal"  # or "stripe"


class CoinPackage(BaseModel):
    id: str
    name: str
    coin_amount: int
    price_usd: float
    price_kes: float
    bonus_coins: int = 0


class PaymentCallback(BaseModel):
    transaction_id: str
    status: str
    amount: float
    currency: str
    user_id: str
    coin_package_id: str


# Notification Models
class NotificationType(str, Enum):
    NEW_FOLLOWER = "new_follower"
    NEW_LIKE = "new_like"
    NEW_COMMENT = "new_comment"
    GIFT_RECEIVED = "gift_received"
    LIVE_STARTED = "live_started"
    MENTION = "mention"


class Notification(BaseModel):
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None
    read: bool = False
    created_at: datetime


# =====================================================
# ENHANCED LIVE SESSION MODELS (Multi-Guest Support)
# =====================================================

class ParticipantRole(str, Enum):
    HOST = "host"
    COHOST = "cohost"
    GUEST = "guest"
    VIEWER = "viewer"


class ParticipantStatus(str, Enum):
    ACTIVE = "active"
    MUTED = "muted"
    KICKED = "kicked"
    LEFT = "left"


class LiveSessionCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    session_type: LiveSessionType
    thumbnail_url: Optional[str] = None
    max_participants: int = Field(default=50, ge=10, le=1000)
    allow_guests: bool = True
    require_approval: bool = True
    max_guests: int = Field(default=8, ge=1, le=20)
    enable_chat: bool = True
    enable_gifts: bool = True
    guest_audio_default: bool = True
    guest_video_default: bool = True


class LiveSessionResponse(BaseModel):
    id: str
    host_id: str
    host_username: str
    host_avatar_url: Optional[str] = None
    title: str
    description: Optional[str] = None
    session_type: LiveSessionType
    status: LiveSessionStatus
    thumbnail_url: Optional[str] = None
    room_name: str
    access_token: str
    viewer_count: int = 0
    guest_count: int = 0
    max_participants: int
    started_at: Optional[str] = None
    settings: Optional[LiveSessionCreateRequest] = None


# =====================================================
# ENHANCED LIVE STREAMING MODELS (Multi-Guest)
# =====================================================

class ParticipantRole(str):
    """Participant roles in live session"""
    HOST = "host"
    COHOST = "cohost"
    GUEST = "guest"
    VIEWER = "viewer"


class ParticipantStatus(str):
    """Participant status"""
    ACTIVE = "active"
    MUTED = "muted"
    KICKED = "kicked"
    LEFT = "left"


class LiveSessionCreateRequest(BaseModel):
    """Enhanced request to create a live session with guest settings"""
    title: str
    description: Optional[str] = None
    session_type: str = "camera"  # voice, camera, studio
    max_participants: int = 100
    # Guest management settings
    allow_guests: bool = True
    require_approval: bool = True
    max_guests: int = 10
    enable_chat: bool = True
    enable_gifts: bool = True
    chat_slow_mode: int = 0  # seconds between messages
    guest_audio_default: bool = True
    guest_video_default: bool = True


class LiveSessionResponse(BaseModel):
    """Enhanced live session response"""
    id: str
    room_name: str
    access_token: str
    host_username: str
    title: str
    description: Optional[str] = None
    viewer_count: int = 0
    guest_count: int = 0
    max_guests: int = 10
    allow_guests: bool = True


class EnhancedLiveJoinResponse(BaseModel):
    """Response when joining a live session (ENHANCED VERSION)"""
    session_id: str
    room_name: str
    access_token: str
    webrtc_config: dict
    role: str = "viewer"
    can_request_guest: bool = True


class GuestRequest(BaseModel):
    session_id: str
    request_type: str = Field(default="guest", pattern="^(guest|cohost)$")
    message: Optional[str] = None


class GuestRequestResponse(BaseModel):
    id: str
    session_id: str
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    request_type: str
    status: str
    message: Optional[str] = None
    created_at: str
    responded_at: Optional[str] = None


class GuestRequestResponseAction(BaseModel):
    request_id: str
    action: str = Field(..., pattern="^(approved|rejected)$")


class ParticipantAction(BaseModel):
    session_id: str
    user_id: str
    action: str = Field(..., pattern="^(mute_audio|unmute_audio|mute_video|unmute_video|kick|promote_cohost|demote)$")


class ParticipantInfo(BaseModel):
    id: str
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    role: str
    status: str
    audio_enabled: bool
    video_enabled: bool
    screen_sharing: bool
    joined_at: str


class ChatMessage(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=500)
    message_type: Optional[str] = "text"
    metadata: Optional[dict] = None


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    message: str
    message_type: str
    metadata: Optional[dict] = None
    created_at: str


class LiveSessionSummary(BaseModel):
    id: str
    host_id: str
    host_username: str
    host_avatar_url: Optional[str] = None
    title: str
    description: Optional[str] = None
    session_type: LiveSessionType
    thumbnail_url: Optional[str] = None
    viewer_count: int
    guest_count: int
    max_guests: int
    allow_guests: bool
    started_at: str


class LiveSessionDetail(BaseModel):
    id: str
    host_id: str
    host_username: str
    host_avatar_url: Optional[str] = None
    title: str
    description: Optional[str] = None
    session_type: LiveSessionType
    status: LiveSessionStatus
    thumbnail_url: Optional[str] = None
    room_name: Optional[str] = None
    viewer_count: int
    guest_count: int
    peak_viewers: int
    total_gifts_received: int
    allow_guests: bool
    max_guests: int
    enable_chat: bool
    enable_gifts: bool
    started_at: str
    ended_at: Optional[str] = None


class ReactionData(BaseModel):
    session_id: str
    reaction_type: str = Field(..., pattern="^(heart|like|fire|clap|wow|sad)$")
