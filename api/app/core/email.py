"""Email service using Gmail SMTP for password reset functionality."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import resend

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Initialize Resend with API key (fallback)
if settings.resend_api_key:
    resend.api_key = settings.resend_api_key


def render_reset_email_template(reset_link: str, expiry_minutes: int = 15) -> str:
    """
    Render HTML email template for password reset.

    Args:
        reset_link: The password reset URL
        expiry_minutes: Token expiry time in minutes

    Returns:
        HTML string for the email body
    """
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f5;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 100%; max-width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px; text-align: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">Lumina Todo</h1>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 20px; color: #18181b; font-size: 24px; font-weight: 600;">Reset Your Password</h2>
                            <p style="margin: 0 0 20px; color: #52525b; font-size: 16px; line-height: 1.6;">
                                We received a request to reset your password. Click the button below to create a new password.
                            </p>

                            <!-- Button -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <a href="{reset_link}" style="display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; border-radius: 8px; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);">
                                            Reset Password
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- Expiry Warning -->
                            <p style="margin: 20px 0 0; padding: 16px; background-color: #fef3c7; border-radius: 8px; color: #92400e; font-size: 14px; line-height: 1.5;">
                                <strong>Note:</strong> This link will expire in {expiry_minutes} minutes for security reasons.
                            </p>

                            <!-- Alternative Link -->
                            <p style="margin: 20px 0 0; color: #71717a; font-size: 14px; line-height: 1.5;">
                                If the button doesn't work, copy and paste this link into your browser:
                            </p>
                            <p style="margin: 10px 0 0; word-break: break-all; color: #6366f1; font-size: 14px;">
                                {reset_link}
                            </p>
                        </td>
                    </tr>

                    <!-- Security Note -->
                    <tr>
                        <td style="padding: 0 40px 40px;">
                            <p style="margin: 0; padding: 16px; background-color: #f4f4f5; border-radius: 8px; color: #71717a; font-size: 13px; line-height: 1.5;">
                                <strong>Didn't request this?</strong> If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 40px; text-align: center; border-top: 1px solid #e4e4e7;">
                            <p style="margin: 0; color: #a1a1aa; font-size: 12px;">
                                &copy; 2026 Lumina Todo. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def _send_via_smtp(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send email via Gmail SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body

    Returns:
        True if sent successfully, False otherwise
    """
    if not settings.smtp_user or not settings.smtp_pass:
        logger.debug("SMTP credentials not configured")
        return False

    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Lumina Todo <{settings.smtp_user}>"
        msg["To"] = to_email

        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        # Connect and send
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.sendmail(settings.smtp_user, to_email, msg.as_string())

        logger.info(f"Password reset email sent via SMTP to {to_email}")
        return True

    except Exception as e:
        logger.error(f"SMTP send failed: {e}")
        return False


def _send_via_resend(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send email via Resend API (fallback).

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body

    Returns:
        True if sent successfully, False otherwise
    """
    if not settings.resend_api_key:
        logger.debug("Resend API key not configured")
        return False

    try:
        resend.Emails.send(
            {
                "from": settings.password_reset_from_email,
                "to": to_email,
                "subject": subject,
                "html": html_content,
            }
        )
        logger.info(f"Password reset email sent via Resend to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Resend send failed: {e}")
        return False


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """
    Send password reset email using SMTP (primary) or Resend (fallback).

    Args:
        to_email: Recipient email address
        reset_link: Password reset URL with token

    Returns:
        True if email sent successfully, False otherwise
    """
    html_content = render_reset_email_template(
        reset_link=reset_link,
        expiry_minutes=settings.password_reset_token_expiry_minutes,
    )
    subject = "Reset your Lumina Todo password"

    # Try SMTP first (Gmail - works without domain verification)
    if _send_via_smtp(to_email, subject, html_content):
        return True

    # Fallback to Resend
    if _send_via_resend(to_email, subject, html_content):
        return True

    logger.warning("No email service configured or all services failed")
    return False
