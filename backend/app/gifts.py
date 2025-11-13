from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
import uuid

from .models import (
    SendGiftRequest, GiftTransaction, GiftType, UserBalance, LeaderboardEntry
)
from .db import db, supabase
from .auth import get_current_user
from .notifications import send_notification

router = APIRouter(prefix="/gifts", tags=["Gifts & Coins"])

# Platform fee: 20% to platform, 80% to creator
PLATFORM_FEE_PERCENTAGE = 0.20
CREATOR_EARNINGS_PERCENTAGE = 0.80


@router.get("/types", response_model=List[GiftType])
async def get_gift_types():
    """Get all available gift types"""
    gift_types = db.get_gift_types()
    
    result = []
    for gift in gift_types:
        result.append(GiftType(
            id=gift["id"],
            name=gift["name"],
            icon_url=gift["icon_url"],
            coin_cost=gift["coin_cost"],
            animation_url=gift.get("animation_url")
        ))
    
    return result


@router.post("/send", response_model=GiftTransaction)
async def send_gift(
    gift_request: SendGiftRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a gift to a creator (in video or live session)"""
    try:
        # Validate recipient exists
        recipient = db.get_user_by_id(gift_request.recipient_id)
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient not found"
            )
        
        # Get gift type
        gift_type_response = supabase.table("gift_types").select("*").eq(
            "id", gift_request.gift_type_id
        ).single().execute()
        
        if not gift_type_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gift type not found"
            )
        
        gift_type = gift_type_response.data
        total_coins = gift_type["coin_cost"] * gift_request.amount
        
        # Check sender balance
        if current_user.get("coin_balance", 0) < total_coins:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient coin balance"
            )
        
        # Calculate earnings
        creator_earnings = total_coins * CREATOR_EARNINGS_PERCENTAGE
        platform_fee = total_coins * PLATFORM_FEE_PERCENTAGE
        
        # Create transaction
        transaction_data = {
            "id": str(uuid.uuid4()),
            "sender_id": current_user["id"],
            "recipient_id": gift_request.recipient_id,
            "gift_type_id": gift_request.gift_type_id,
            "amount": gift_request.amount,
            "total_coins": total_coins,
            "creator_earnings": creator_earnings,
            "platform_fee": platform_fee,
            "video_id": gift_request.video_id,
            "live_session_id": gift_request.live_session_id
        }
        
        transaction = db.create_gift_transaction(transaction_data)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process gift"
            )
        
        # Update balances
        db.update_user_balance(current_user["id"], -total_coins, 0)
        db.update_user_balance(gift_request.recipient_id, 0, creator_earnings)
        
        # Send notification to recipient
        await send_notification(
            user_id=gift_request.recipient_id,
            notification_type="gift_received",
            title="Gift Received!",
            message=f"{current_user['username']} sent you {gift_request.amount}x {gift_type['name']}",
            data={
                "gift_type": gift_type["name"],
                "amount": gift_request.amount,
                "sender_username": current_user["username"]
            }
        )
        
        return GiftTransaction(
            id=transaction["id"],
            sender_id=transaction["sender_id"],
            sender_username=current_user["username"],
            recipient_id=transaction["recipient_id"],
            recipient_username=recipient["username"],
            gift_type_id=transaction["gift_type_id"],
            gift_name=gift_type["name"],
            amount=transaction["amount"],
            total_coins=transaction["total_coins"],
            creator_earnings=transaction["creator_earnings"],
            platform_fee=transaction["platform_fee"],
            video_id=transaction.get("video_id"),
            live_session_id=transaction.get("live_session_id"),
            created_at=transaction["created_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send gift: {str(e)}"
        )


@router.get("/balance/{user_id}", response_model=UserBalance)
async def get_user_balance(user_id: str):
    """Get user's coin balance and earnings"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserBalance(
        user_id=user["id"],
        coin_balance=user.get("coin_balance", 0),
        total_earnings=user.get("total_earnings", 0.0)
    )


@router.get("/balance", response_model=UserBalance)
async def get_my_balance(current_user: dict = Depends(get_current_user)):
    """Get current user's balance"""
    return UserBalance(
        user_id=current_user["id"],
        coin_balance=current_user.get("coin_balance", 0),
        total_earnings=current_user.get("total_earnings", 0.0)
    )


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 50):
    """Get top creators by earnings"""
    creators = db.get_leaderboard(limit=limit)
    
    result = []
    for idx, creator in enumerate(creators, start=1):
        # Count gifts received
        gifts_response = supabase.table("gift_transactions").select(
            "amount", count="exact"
        ).eq("recipient_id", creator["id"]).execute()
        
        total_gifts = sum(gift.get("amount", 0) for gift in gifts_response.data) if gifts_response.data else 0
        
        result.append(LeaderboardEntry(
            user_id=creator["id"],
            username=creator["username"],
            avatar_url=creator.get("avatar_url"),
            total_earnings=creator.get("total_earnings", 0.0),
            gifts_received=total_gifts,
            rank=idx
        ))
    
    return result


@router.get("/history", response_model=List[GiftTransaction])
async def get_gift_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get current user's gift transaction history"""
    try:
        response = supabase.table("gift_transactions").select("""
            *,
            sender:users!gift_transactions_sender_id_fkey (username),
            recipient:users!gift_transactions_recipient_id_fkey (username),
            gift_types (name)
        """).or_(
            f"sender_id.eq.{current_user['id']},recipient_id.eq.{current_user['id']}"
        ).order("created_at", desc=True).limit(limit).execute()
        
        transactions = []
        for txn in response.data:
            transactions.append(GiftTransaction(
                id=txn["id"],
                sender_id=txn["sender_id"],
                sender_username=txn["sender"]["username"],
                recipient_id=txn["recipient_id"],
                recipient_username=txn["recipient"]["username"],
                gift_type_id=txn["gift_type_id"],
                gift_name=txn["gift_types"]["name"],
                amount=txn["amount"],
                total_coins=txn["total_coins"],
                creator_earnings=txn["creator_earnings"],
                platform_fee=txn["platform_fee"],
                video_id=txn.get("video_id"),
                live_session_id=txn.get("live_session_id"),
                created_at=txn["created_at"]
            ))
        
        return transactions
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch gift history: {str(e)}"
        )
