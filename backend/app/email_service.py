"""
Email Service for verification and notifications
Using SendGrid (recommended) or SMTP
"""
import os
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import secrets
from datetime import datetime, timedelta

load_dotenv()


class EmailService:
    """Email service for sending verification and notification emails"""
    
    def __init__(self):
        self.sendgrid_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@trendke.com")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5175")
        
        if self.sendgrid_key:
            self.client = SendGridAPIClient(self.sendgrid_key)
        else:
            print("⚠️  SendGrid API key not configured. Email features disabled.")
            self.client = None
    
    def send_verification_email(self, email: str, username: str, verification_token: str) -> bool:
        """Send email verification link"""
        if not self.client:
            print(f"📧 Email verification would be sent to: {email}")
            print(f"🔗 Verification link: {self.frontend_url}/verify-email?token={verification_token}")
            return True
        
        try:
            verification_url = f"{self.frontend_url}/verify-email?token={verification_token}"
            
            message = Mail(
                from_email=self.from_email,
                to_emails=email,
                subject='Verify your TrendKe account',
                html_content=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to TrendKe!</h1>
                    </div>
                    
                    <div style="padding: 40px; background: #f9fafb; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                            Hi <strong>{username}</strong>,
                        </p>
                        
                        <p style="font-size: 16px; color: #374151; margin-bottom: 30px;">
                            Thanks for signing up! Please verify your email address to start sharing amazing content.
                        </p>
                        
                        <div style="text-align: center; margin: 40px 0;">
                            <a href="{verification_url}" 
                               style="background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); 
                                      color: white; 
                                      padding: 15px 40px; 
                                      text-decoration: none; 
                                      border-radius: 8px; 
                                      font-weight: bold;
                                      display: inline-block;
                                      font-size: 16px;">
                                Verify Email Address
                            </a>
                        </div>
                        
                        <p style="font-size: 14px; color: #6b7280; margin-top: 30px;">
                            Or copy and paste this link into your browser:<br>
                            <a href="{verification_url}" style="color: #8b5cf6; word-break: break-all;">
                                {verification_url}
                            </a>
                        </p>
                        
                        <p style="font-size: 14px; color: #6b7280; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                            This link will expire in 24 hours. If you didn't create an account, please ignore this email.
                        </p>
                    </div>
                </div>
                """
            )
            
            response = self.client.send(message)
            return response.status_code == 202
            
        except Exception as e:
            print(f"Email sending error: {e}")
            return False
    
    def send_password_reset_email(self, email: str, username: str, reset_token: str) -> bool:
        """Send password reset link"""
        if not self.client:
            print(f"📧 Password reset would be sent to: {email}")
            print(f"🔗 Reset link: {self.frontend_url}/reset-password?token={reset_token}")
            return True
        
        try:
            reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
            
            message = Mail(
                from_email=self.from_email,
                to_emails=email,
                subject='Reset your TrendKe password',
                html_content=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">Password Reset</h1>
                    </div>
                    
                    <div style="padding: 40px; background: #f9fafb; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                            Hi <strong>{username}</strong>,
                        </p>
                        
                        <p style="font-size: 16px; color: #374151; margin-bottom: 30px;">
                            We received a request to reset your password. Click the button below to create a new password.
                        </p>
                        
                        <div style="text-align: center; margin: 40px 0;">
                            <a href="{reset_url}" 
                               style="background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); 
                                      color: white; 
                                      padding: 15px 40px; 
                                      text-decoration: none; 
                                      border-radius: 8px; 
                                      font-weight: bold;
                                      display: inline-block;
                                      font-size: 16px;">
                                Reset Password
                            </a>
                        </div>
                        
                        <p style="font-size: 14px; color: #6b7280; margin-top: 30px;">
                            Or copy and paste this link into your browser:<br>
                            <a href="{reset_url}" style="color: #8b5cf6; word-break: break-all;">
                                {reset_url}
                            </a>
                        </p>
                        
                        <p style="font-size: 14px; color: #dc2626; margin-top: 30px; padding: 15px; background: #fee2e2; border-radius: 8px;">
                            ⚠️ If you didn't request a password reset, please ignore this email and your password will remain unchanged.
                        </p>
                        
                        <p style="font-size: 14px; color: #6b7280; margin-top: 20px;">
                            This link will expire in 1 hour.
                        </p>
                    </div>
                </div>
                """
            )
            
            response = self.client.send(message)
            return response.status_code == 202
            
        except Exception as e:
            print(f"Email sending error: {e}")
            return False
    
    def send_2fa_code(self, email: str, username: str, code: str) -> bool:
        """Send 2FA verification code"""
        if not self.client:
            print(f"📧 2FA code would be sent to: {email}")
            print(f"🔐 Code: {code}")
            return True
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=email,
                subject='Your TrendKe verification code',
                html_content=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">Verification Code</h1>
                    </div>
                    
                    <div style="padding: 40px; background: #f9fafb; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                            Hi <strong>{username}</strong>,
                        </p>
                        
                        <p style="font-size: 16px; color: #374151; margin-bottom: 30px;">
                            Your verification code is:
                        </p>
                        
                        <div style="text-align: center; margin: 40px 0;">
                            <div style="background: white; 
                                        padding: 20px 40px; 
                                        border-radius: 10px; 
                                        display: inline-block;
                                        border: 2px dashed #8b5cf6;">
                                <span style="font-size: 32px; 
                                             font-weight: bold; 
                                             color: #8b5cf6; 
                                             letter-spacing: 8px;">
                                    {code}
                                </span>
                            </div>
                        </div>
                        
                        <p style="font-size: 14px; color: #6b7280; margin-top: 30px;">
                            This code will expire in 10 minutes. If you didn't request this code, please secure your account immediately.
                        </p>
                    </div>
                </div>
                """
            )
            
            response = self.client.send(message)
            return response.status_code == 202
            
        except Exception as e:
            print(f"Email sending error: {e}")
            return False


# Helper functions for token generation
def generate_verification_token() -> str:
    """Generate secure verification token"""
    return secrets.token_urlsafe(32)


def generate_2fa_code() -> str:
    """Generate 6-digit 2FA code"""
    return str(secrets.randbelow(1000000)).zfill(6)
