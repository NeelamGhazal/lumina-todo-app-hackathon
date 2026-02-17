# Quickstart: Password Reset Feature

**Feature**: 008-password-reset | **Date**: 2026-02-12

## Prerequisites

1. Evolution-Todo project running locally
2. API server at `http://localhost:8000`
3. Frontend at `http://localhost:3000`
4. Resend account with API key

## Environment Setup

Add to `api/.env`:

```bash
# Resend Email Service
RESEND_API_KEY=re_xxxxxxxxxxxx
PASSWORD_RESET_FROM_EMAIL=noreply@yourdomain.com

# Token Configuration
PASSWORD_RESET_TOKEN_EXPIRY_MINUTES=15
PASSWORD_RESET_MAX_REQUESTS_PER_HOUR=3

# Frontend URL (for reset links)
FRONTEND_URL=http://localhost:3000
```

## Quick Test Flow

### 1. Request Password Reset

```bash
curl -X POST http://localhost:8000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

Expected response (always same to prevent enumeration):
```json
{
  "message": "If an account exists with this email, you will receive a reset link shortly"
}
```

### 2. Verify Token (from email link)

```bash
curl http://localhost:8000/api/auth/verify-reset-token/{token}
```

Valid token response:
```json
{
  "valid": true,
  "email": "user@example.com"
}
```

Invalid/expired token response:
```json
{
  "valid": false,
  "email": null,
  "error": "Invalid reset link"
}
```

### 3. Reset Password

```bash
curl -X POST http://localhost:8000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123xyz789...",
    "password": "NewPassword123",
    "password_confirm": "NewPassword123"
  }'
```

Success response:
```json
{
  "success": true,
  "message": "Password has been reset successfully"
}
```

## Frontend Pages

| URL | Purpose |
|-----|---------|
| `/forgot-password` | Email input form |
| `/reset-password?token=xxx` | New password form |

## Development Tips

### Testing Rate Limiting

Make 4 requests in quick succession - the 4th should return 429:

```bash
for i in {1..4}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST http://localhost:8000/api/auth/forgot-password \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com"}'
done
```

Expected output: `200`, `200`, `200`, `429`

### Testing Token Expiry

1. Request reset token
2. Wait 15+ minutes
3. Try to verify/use token - should fail with "expired"

### Checking Token Hash in Database

```sql
SELECT email, reset_token_hash, reset_token_expiry
FROM users
WHERE email = 'user@example.com';
```

Note: Only the hash is stored, never the plain token.

## Password Requirements

When resetting password, these rules apply:
- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 number (0-9)

Invalid passwords return 422 with details:
```json
{
  "error": "INVALID_PASSWORD",
  "message": "Password does not meet requirements",
  "details": [
    "Password must be at least 8 characters",
    "Password must contain at least 1 uppercase letter"
  ]
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Email not received | Check RESEND_API_KEY is valid |
| Token invalid immediately | Verify FRONTEND_URL matches actual frontend |
| Rate limit hit during testing | Wait 1 hour or reset `reset_request_count` in database |
| Password validation fails | Ensure 8+ chars, 1 uppercase, 1 number |
