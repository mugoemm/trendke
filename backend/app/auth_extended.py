"""
Extended authentication routes with email verification, password reset, and 2FA
"""
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import secrets

from .auth import get_current_user, get_password_hash, verify_password, create_access_token
from .email_service import EmailService, generate_verification_token, generate_2fa_code
from .db import db, supabase

router = APIRouter(prefix="/auth", tags=["Authentication Extended"])
email_service = EmailService()


# Models
class EmailVerifyRequest(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class Enable2FARequest(BaseModel):
    enable: bool


class Verify2FARequest(BaseModel):
    email: EmailStr
    code: str


# Email Verification Endpoints
@router.post("/resend-verification")
async def resend_verification_email(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Resend email verification link"""
    if current_user.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new token
    token = generate_verification_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    # Store token in database
    try:
        if supabase:
            supabase.table("email_verifications").upsert({
                "user_id": current_user["id"],
                "token": token,
                "expires_at": expires_at.isoformat()
            }).execute()
    except Exception as e:
        print(f"Token storage error: {e}")
    
    # Send email in background
    background_tasks.add_task(
        email_service.send_verification_email,
        current_user["email"],
        current_user["username"],
        token
    )
    
    return {"message": "Verification email sent"}


@router.post("/verify-email")
async def verify_email(request: EmailVerifyRequest):
    """Verify email with token"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not configured"
        )
    
    try:
        # Find token
        result = supabase.table("email_verifications").select(
            "user_id, expires_at"
        ).eq("token", request.token).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        verification = result.data[0]
        
        # Check expiration
        expires_at = datetime.fromisoformat(verification["expires_at"].replace("Z", "+00:00"))
        if datetime.utcnow() > expires_at.replace(tzinfo=None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expired"
            )
        
        # Update user
        supabase.table("users").update({
            "email_verified": True
        }).eq("id", verification["user_id"]).execute()
        
        # Delete token
        supabase.table("email_verifications").delete().eq(
            "token", request.token
        ).execute()
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed"
        )


# Password Reset Endpoints
@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks
):
    """Request password reset"""
    user = db.get_user_by_email(request.email)
    
    # Don't reveal if email exists (security)
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate token
    token = generate_verification_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # Store token
    try:
        if supabase:
            supabase.table("password_resets").upsert({
                "user_id": user["id"],
                "token": token,
                "expires_at": expires_at.isoformat()
            }).execute()
    except Exception as e:
        print(f"Token storage error: {e}")
    
    # Send email
    background_tasks.add_task(
        email_service.send_password_reset_email,
        user["email"],
        user["username"],
        token
    )
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """Reset password with token"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not configured"
        )
    
    try:
        # Find token
        result = supabase.table("password_resets").select(
            "user_id, expires_at"
        ).eq("token", request.token).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        reset = result.data[0]
        
        # Check expiration
        expires_at = datetime.fromisoformat(reset["expires_at"].replace("Z", "+00:00"))
        if datetime.utcnow() > expires_at.replace(tzinfo=None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expired"
            )
        
        # Hash new password
        new_hash = get_password_hash(request.new_password)
        
        # Update password
        supabase.table("users").update({
            "password_hash": new_hash
        }).eq("id", reset["user_id"]).execute()
        
        # Delete token
        supabase.table("password_resets").delete().eq(
            "token", request.token
        ).execute()
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reset failed"
        )


# 2FA Endpoints
@router.post("/2fa/enable")
async def toggle_2fa(
    request: Enable2FARequest,
    current_user: dict = Depends(get_current_user)
):
    """Enable or disable 2FA"""
    try:
        db.update_user(current_user["id"], {
            "two_factor_enabled": request.enable
        })
        
        return {
            "message": f"2FA {'enabled' if request.enable else 'disabled'}",
            "two_factor_enabled": request.enable
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update 2FA: {str(e)}"
        )


@router.post("/2fa/send-code")
async def send_2fa_code(
    background_tasks: BackgroundTasks,
    email: EmailStr
):
    """Send 2FA code to email"""
    user = db.get_user_by_email(email)
    
    if not user or not user.get("two_factor_enabled"):
        # Don't reveal if 2FA is enabled (security)
        return {"message": "If 2FA is enabled, code has been sent"}
    
    # Generate code
    code = generate_2fa_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Store code
    try:
        if supabase:
            supabase.table("two_factor_codes").upsert({
                "user_id": user["id"],
                "code": code,
                "expires_at": expires_at.isoformat()
            }).execute()
    except Exception as e:
        print(f"2FA code storage error: {e}")
    
    # Send email
    background_tasks.add_task(
        email_service.send_2fa_code,
        user["email"],
        user["username"],
        code
    )
    
    return {"message": "If 2FA is enabled, code has been sent"}


@router.post("/2fa/verify")
async def verify_2fa(request: Verify2FARequest):
    """Verify 2FA code and login"""
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not configured"
        )
    
    user = db.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    try:
        # Find code
        result = supabase.table("two_factor_codes").select(
            "code, expires_at"
        ).eq("user_id", user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid code"
            )
        
        stored = result.data[0]
        
        # Check expiration
        expires_at = datetime.fromisoformat(stored["expires_at"].replace("Z", "+00:00"))
        if datetime.utcnow() > expires_at.replace(tzinfo=None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code expired"
            )
        
        # Verify code
        if stored["code"] != request.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid code"
            )
        
        # Delete code
        supabase.table("two_factor_codes").delete().eq(
            "user_id", user["id"]
        ).execute()
        
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
        print(f"2FA verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed"
        )
