from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import os
import uuid
import httpx
from dotenv import load_dotenv

from .models import CoinPurchaseRequest, CoinPackage, PaymentCallback
from .db import db, supabase
from .auth import get_current_user

load_dotenv()

router = APIRouter(prefix="/payments", tags=["Payments"])

# PesaPal Configuration (Sandbox)
PESAPAL_CONSUMER_KEY = os.getenv("PESAPAL_CONSUMER_KEY", "")
PESAPAL_CONSUMER_SECRET = os.getenv("PESAPAL_CONSUMER_SECRET", "")
PESAPAL_API_URL = os.getenv("PESAPAL_API_URL", "https://cybqa.pesapal.com/pesapalv3")

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

# Predefined coin packages
COIN_PACKAGES = [
    {
        "id": "package_1",
        "name": "Starter Pack",
        "coin_amount": 100,
        "price_usd": 0.99,
        "price_kes": 100,
        "bonus_coins": 0
    },
    {
        "id": "package_2",
        "name": "Popular Pack",
        "coin_amount": 500,
        "price_usd": 4.99,
        "price_kes": 500,
        "bonus_coins": 50
    },
    {
        "id": "package_3",
        "name": "Value Pack",
        "coin_amount": 1000,
        "price_usd": 9.99,
        "price_kes": 1000,
        "bonus_coins": 150
    },
    {
        "id": "package_4",
        "name": "Premium Pack",
        "coin_amount": 5000,
        "price_usd": 49.99,
        "price_kes": 5000,
        "bonus_coins": 1000
    }
]


@router.get("/packages", response_model=List[CoinPackage])
async def get_coin_packages():
    """Get available coin packages for purchase"""
    return [CoinPackage(**package) for package in COIN_PACKAGES]


@router.post("/purchase/initiate")
async def initiate_coin_purchase(
    purchase_request: CoinPurchaseRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Initiate coin purchase via PesaPal or Stripe
    Returns payment URL for user to complete transaction
    """
    try:
        # Find coin package
        package = next(
            (p for p in COIN_PACKAGES if p["id"] == purchase_request.coin_package_id),
            None
        )
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coin package not found"
            )
        
        transaction_id = str(uuid.uuid4())
        
        if purchase_request.payment_method == "pesapal":
            # PesaPal Integration
            payment_url = await initiate_pesapal_payment(
                transaction_id=transaction_id,
                amount=package["price_kes"],
                currency="KES",
                user_email=current_user["email"],
                description=f"Purchase {package['name']} - {package['coin_amount']} coins"
            )
            
            # Store pending transaction
            supabase.table("payment_transactions").insert({
                "id": transaction_id,
                "user_id": current_user["id"],
                "coin_package_id": package["id"],
                "amount": package["price_kes"],
                "currency": "KES",
                "payment_method": "pesapal",
                "status": "pending"
            }).execute()
            
            return {
                "transaction_id": transaction_id,
                "payment_url": payment_url,
                "payment_method": "pesapal"
            }
        
        elif purchase_request.payment_method == "stripe":
            # Stripe Integration
            payment_url = await initiate_stripe_payment(
                transaction_id=transaction_id,
                amount=package["price_usd"],
                currency="USD",
                description=f"Purchase {package['name']} - {package['coin_amount']} coins"
            )
            
            # Store pending transaction
            supabase.table("payment_transactions").insert({
                "id": transaction_id,
                "user_id": current_user["id"],
                "coin_package_id": package["id"],
                "amount": package["price_usd"],
                "currency": "USD",
                "payment_method": "stripe",
                "status": "pending"
            }).execute()
            
            return {
                "transaction_id": transaction_id,
                "payment_url": payment_url,
                "payment_method": "stripe"
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment method"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate payment: {str(e)}"
        )


async def initiate_pesapal_payment(
    transaction_id: str,
    amount: float,
    currency: str,
    user_email: str,
    description: str
) -> str:
    """
    Initiate PesaPal payment
    TODO: Implement actual PesaPal API integration
    """
    # This is a placeholder. Actual implementation would use PesaPal API
    # Reference: https://developer.pesapal.com/
    
    return f"https://pesapal-sandbox.example.com/payment/{transaction_id}"


async def initiate_stripe_payment(
    transaction_id: str,
    amount: float,
    currency: str,
    description: str
) -> str:
    """
    Initiate Stripe payment
    TODO: Implement actual Stripe API integration
    """
    # This is a placeholder. Actual implementation would use Stripe API
    # import stripe
    # stripe.api_key = STRIPE_SECRET_KEY
    # session = stripe.checkout.Session.create(...)
    
    return f"https://stripe-checkout.example.com/payment/{transaction_id}"


@router.post("/callback/pesapal")
async def pesapal_callback(callback_data: PaymentCallback):
    """
    PesaPal payment callback endpoint
    Called by PesaPal when payment is completed
    """
    try:
        # Verify transaction exists
        transaction = supabase.table("payment_transactions").select("*").eq(
            "id", callback_data.transaction_id
        ).single().execute()
        
        if not transaction.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        if callback_data.status == "COMPLETED":
            # Find coin package
            package = next(
                (p for p in COIN_PACKAGES if p["id"] == callback_data.coin_package_id),
                None
            )
            
            if package:
                total_coins = package["coin_amount"] + package["bonus_coins"]
                
                # Update user balance
                db.update_user_balance(callback_data.user_id, total_coins, 0)
                
                # Update transaction status
                supabase.table("payment_transactions").update({
                    "status": "completed"
                }).eq("id", callback_data.transaction_id).execute()
                
                return {"message": "Payment processed successfully", "coins_added": total_coins}
        
        else:
            # Update transaction as failed
            supabase.table("payment_transactions").update({
                "status": "failed"
            }).eq("id", callback_data.transaction_id).execute()
            
            return {"message": "Payment failed"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process payment callback: {str(e)}"
        )


@router.post("/callback/stripe")
async def stripe_callback(callback_data: PaymentCallback):
    """
    Stripe payment callback endpoint
    Called by Stripe webhook when payment is completed
    """
    # Similar implementation to PesaPal callback
    return await pesapal_callback(callback_data)


@router.get("/history")
async def get_payment_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get user's payment transaction history"""
    try:
        response = supabase.table("payment_transactions").select("*").eq(
            "user_id", current_user["id"]
        ).order("created_at", desc=True).limit(limit).execute()
        
        return response.data
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment history: {str(e)}"
        )
