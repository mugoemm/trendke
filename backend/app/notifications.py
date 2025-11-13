from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import uuid

from .models import Notification, NotificationType
from .db import db, supabase
from .auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


async def send_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    data: dict = None
):
    """
    Send a notification to a user
    This function can be called from other modules
    """
    try:
        notification_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "read": False
        }
        
        notification = db.create_notification(notification_data)
        
        # TODO: Integrate with Firebase Cloud Messaging or Supabase Realtime
        # for push notifications to mobile/web clients
        
        # Publish to Supabase Realtime channel
        try:
            supabase.channel(f"notifications:{user_id}").send({
                "type": "broadcast",
                "event": "new_notification",
                "payload": notification
            })
        except Exception as e:
            print(f"Failed to send realtime notification: {e}")
        
        return notification
    
    except Exception as e:
        print(f"Error sending notification: {e}")
        return None


@router.get("/", response_model=List[Notification])
async def get_notifications(
    limit: int = 20,
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    try:
        query = supabase.table("notifications").select("*").eq(
            "user_id", current_user["id"]
        ).order("created_at", desc=True).limit(limit)
        
        if unread_only:
            query = query.eq("read", False)
        
        response = query.execute()
        
        notifications = []
        for notif in response.data:
            notifications.append(Notification(
                id=notif["id"],
                user_id=notif["user_id"],
                type=notif["type"],
                title=notif["title"],
                message=notif["message"],
                data=notif.get("data"),
                read=notif.get("read", False),
                created_at=notif["created_at"]
            ))
        
        return notifications
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        # Verify notification belongs to user
        notification = supabase.table("notifications").select("*").eq(
            "id", notification_id
        ).eq("user_id", current_user["id"]).single().execute()
        
        if not notification.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Mark as read
        supabase.table("notifications").update({
            "read": True
        }).eq("id", notification_id).execute()
        
        return {"message": "Notification marked as read"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.post("/read-all")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read"""
    try:
        supabase.table("notifications").update({
            "read": True
        }).eq("user_id", current_user["id"]).eq("read", False).execute()
        
        return {"message": "All notifications marked as read"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notifications as read: {str(e)}"
        )


@router.get("/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    """Get count of unread notifications"""
    try:
        response = supabase.table("notifications").select(
            "id", count="exact"
        ).eq("user_id", current_user["id"]).eq("read", False).execute()
        
        return {"unread_count": response.count}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )
