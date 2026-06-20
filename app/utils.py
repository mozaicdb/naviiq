import httpx
from app.core.config import settings

async def send_reset_email(email: str, full_name: str, token: str):
    reset_url = f"http://localhost:5173/reset-password?token={token}"

    payload = {
        "sender": {
            "name": "Naviiq",
            "email": settings.BREVO_SENDER_EMAIL
        },
        "to": [{"email": email, "name": full_name}],
        "subject": "Reset your Naviiq password",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563EB;">Password Reset Request</h2>
            <p>Hi {full_name}, click the button below to reset your password.</p>
            <a href="{reset_url}" 
               style="display: inline-block; padding: 12px 24px; background-color: #2563EB; 
                      color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                Reset My Password
            </a>
            <p style="color: #64748B; margin-top: 16px;">
                This link expires in 30 minutes. If you did not request this, ignore this email.
            </p>
        </div>
        """
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={
                "api-key": settings.BREVO_API_KEY,
                "Content-Type": "application/json"
            }
        )
        return response.status_code


async def send_verification_email(email: str, full_name: str, token: str):
    verification_url = f"http://localhost:5173/verify-email?token={token}"
    
    payload = {
        "sender": {
            "name": "Naviiq",
            "email": settings.BREVO_SENDER_EMAIL
        },
        "to": [{"email": email, "name": full_name}],
        "subject": "Verify your Naviiq account",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563EB;">Welcome to Naviiq, {full_name}!</h2>
            <p>Click the button below to verify your email address.</p>
            <a href="{verification_url}" 
               style="display: inline-block; padding: 12px 24px; background-color: #2563EB; 
                      color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                Verify My Email
            </a>
            <p style="color: #64748B; margin-top: 16px;">
                This link expires in 30 minutes.
            </p>
        </div>
        """
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={
                "api-key": settings.BREVO_API_KEY,
                "Content-Type": "application/json"
            }
        )
        return response.status_code