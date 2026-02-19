import { NextRequest, NextResponse } from "next/server";
import nodemailer from "nodemailer";

/**
 * Email sending API route using Gmail SMTP
 * This runs on Vercel which allows outbound SMTP connections
 * (HuggingFace blocks SMTP, so we proxy through Vercel)
 */

const SMTP_USER = process.env.SMTP_USER;
const SMTP_PASS = process.env.SMTP_PASS;

// Simple API key for backend authentication
const EMAIL_API_KEY = process.env.EMAIL_API_KEY || "lumina-email-secret-key";

// Email template for password reset
function renderResetEmailTemplate(resetLink: string, expiryMinutes: number = 15): string {
  return `
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
                                        <a href="${resetLink}" style="display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; border-radius: 8px; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);">
                                            Reset Password
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- Expiry Warning -->
                            <p style="margin: 20px 0 0; padding: 16px; background-color: #fef3c7; border-radius: 8px; color: #92400e; font-size: 14px; line-height: 1.5;">
                                <strong>Note:</strong> This link will expire in ${expiryMinutes} minutes for security reasons.
                            </p>

                            <!-- Alternative Link -->
                            <p style="margin: 20px 0 0; color: #71717a; font-size: 14px; line-height: 1.5;">
                                If the button doesn't work, copy and paste this link into your browser:
                            </p>
                            <p style="margin: 10px 0 0; word-break: break-all; color: #6366f1; font-size: 14px;">
                                ${resetLink}
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
`;
}

export async function POST(request: NextRequest) {
  try {
    // Verify API key
    const authHeader = request.headers.get("authorization");
    const providedKey = authHeader?.replace("Bearer ", "");

    if (providedKey !== EMAIL_API_KEY) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    // Parse request body
    const body = await request.json();
    const { to, resetLink, expiryMinutes = 15 } = body;

    if (!to || !resetLink) {
      return NextResponse.json(
        { error: "Missing required fields: to, resetLink" },
        { status: 400 }
      );
    }

    // Check SMTP credentials
    if (!SMTP_USER || !SMTP_PASS) {
      console.error("SMTP credentials not configured");
      return NextResponse.json(
        { error: "Email service not configured" },
        { status: 500 }
      );
    }

    // Create transporter
    const transporter = nodemailer.createTransport({
      host: "smtp.gmail.com",
      port: 587,
      secure: false,
      auth: {
        user: SMTP_USER,
        pass: SMTP_PASS,
      },
    });

    // Send email
    const htmlContent = renderResetEmailTemplate(resetLink, expiryMinutes);

    await transporter.sendMail({
      from: `Lumina Todo <${SMTP_USER}>`,
      to: to,
      subject: "Reset your Lumina Todo password",
      html: htmlContent,
    });

    console.log(`Password reset email sent to ${to}`);

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Failed to send email:", error);
    return NextResponse.json(
      { error: "Failed to send email", details: String(error) },
      { status: 500 }
    );
  }
}

// Debug endpoint to check configuration
export async function GET() {
  return NextResponse.json({
    smtp_user: SMTP_USER ? "SET" : "NOT SET",
    smtp_pass: SMTP_PASS ? "SET" : "NOT SET",
    email_api_key: EMAIL_API_KEY ? "SET" : "NOT SET",
  });
}
