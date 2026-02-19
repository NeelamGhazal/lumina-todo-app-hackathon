"""Email service using Vercel proxy for password reset functionality.

Since HuggingFace blocks outbound SMTP connections, we proxy email
sending through a Vercel API route that handles Gmail SMTP.
"""

import logging

import httpx

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Vercel email API endpoint
VERCEL_EMAIL_API = "https://lumina-todo.vercel.app/api/send-email"
EMAIL_API_KEY = "lumina-email-secret-key"


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """
    Send password reset email via Vercel proxy.

    The actual email sending happens on Vercel (which allows SMTP),
    not on HuggingFace (which blocks SMTP).

    Args:
        to_email: Recipient email address
        reset_link: Password reset URL with token

    Returns:
        True if email sent successfully, False otherwise
    """
    logger.info(f"Sending password reset email to {to_email} via Vercel proxy")

    try:
        response = httpx.post(
            VERCEL_EMAIL_API,
            json={
                "to": to_email,
                "resetLink": reset_link,
                "expiryMinutes": settings.password_reset_token_expiry_minutes,
            },
            headers={
                "Authorization": f"Bearer {EMAIL_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        if response.status_code == 200:
            logger.info(f"Password reset email sent successfully to {to_email}")
            return True
        else:
            logger.error(
                f"Vercel email API returned {response.status_code}: {response.text}"
            )
            return False

    except httpx.TimeoutException:
        logger.error("Vercel email API timed out")
        return False
    except Exception as e:
        logger.error(f"Failed to send email via Vercel proxy: {e}")
        return False
