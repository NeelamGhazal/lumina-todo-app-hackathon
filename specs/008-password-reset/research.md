# Research: Password Reset Implementation

**Feature**: 008-password-reset | **Date**: 2026-02-12

## Research Tasks Completed

### 1. Token Generation Best Practices

**Decision**: Use `secrets.token_urlsafe(32)` for 256-bit entropy

**Rationale**:
- Python's `secrets` module is designed for cryptographic use
- `token_urlsafe(32)` generates 256 bits of randomness (32 bytes)
- URL-safe encoding avoids issues in email links
- Industry standard for password reset tokens

**Alternatives Considered**:
- UUID4: Only 122 bits of randomness, less secure
- JWT: Overkill for single-use tokens, harder to invalidate
- Custom implementation: Security risk, use standard library

### 2. Token Hashing Approach

**Decision**: SHA-256 hash with `hashlib.sha256()`

**Rationale**:
- Fast enough for single-use tokens
- Sufficient security for short-lived tokens (15 minutes)
- No salt needed (token has high entropy already)
- Consistent with existing password hashing approach (bcrypt for passwords)

**Implementation**:
```python
import hashlib

def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
```

**Alternatives Considered**:
- bcrypt: Too slow for token lookup, designed for passwords
- Argon2: Overkill for high-entropy tokens

### 3. Resend Email Service Integration

**Decision**: Use Resend Python SDK with HTML templates

**Rationale**:
- Simple API with Python SDK
- Free tier: 100 emails/day (sufficient for development)
- Good deliverability
- HTML template support built-in

**Implementation Pattern**:
```python
import resend

resend.api_key = settings.resend_api_key

def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    try:
        resend.Emails.send({
            "from": settings.password_reset_from_email,
            "to": to_email,
            "subject": "Reset your Lumina password",
            "html": render_reset_email_template(reset_link)
        })
        return True
    except Exception as e:
        logger.error(f"Failed to send reset email: {e}")
        return False
```

### 4. Rate Limiting Strategy

**Decision**: In-database per-email tracking

**Rationale**:
- No external dependencies (Redis not needed)
- Simple implementation
- Works for single-instance deployment
- Matches existing SQLModel patterns

**Implementation**:
- Store `reset_request_count` and `reset_request_window_start` on User
- On each request:
  1. Check if window has expired (> 1 hour since window_start)
  2. If expired: reset count to 1, update window_start
  3. If not expired: increment count, reject if count > 3
- For non-existent emails: still respect rate limit to prevent enumeration

### 5. Password Validation Rules

**Decision**: Server-side validation with clear error messages

**Requirements** (from spec):
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 number

**Implementation**:
```python
import re

def validate_password(password: str) -> list[str]:
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least 1 uppercase letter")
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least 1 number")
    return errors
```

### 6. Frontend Page Structure

**Decision**: Follow existing auth page patterns

**Existing Patterns Found**:
- `/frontend/src/app/(auth)/login/page.tsx` - Uses GlassCard, GradientText
- `/frontend/src/components/auth/login-form.tsx` - Form pattern
- Motion animations with `fadeUpVariants`
- Consistent error handling with toast notifications

**New Pages Will Follow**:
- Same GlassCard wrapper
- Same form validation patterns
- Same animation variants
- Same styling (Tailwind + Lumina theme)

### 7. API Endpoint Design

**Decision**: RESTful endpoints under /auth prefix

**Endpoints**:
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /auth/forgot-password | Request reset email |
| GET | /auth/verify-reset-token/{token} | Check token validity |
| POST | /auth/reset-password | Set new password |

**Request/Response Schemas**:
```python
# Request: forgot-password
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# Response: forgot-password (always same to prevent enumeration)
class ForgotPasswordResponse(BaseModel):
    message: str  # "If an account exists..."

# Request: reset-password
class ResetPasswordRequest(BaseModel):
    token: str
    password: str
    password_confirm: str

# Response: reset-password
class ResetPasswordResponse(BaseModel):
    success: bool
    message: str

# Response: verify-reset-token
class VerifyTokenResponse(BaseModel):
    valid: bool
    email: str | None  # Only if valid
```

## Dependencies to Install

### Backend (api/)
```bash
uv add resend
```

### Frontend (frontend/)
No new dependencies needed - using existing form/validation patterns.

## Environment Variables Required

```bash
# api/.env
RESEND_API_KEY=re_xxxxxxxxxxxx
PASSWORD_RESET_FROM_EMAIL=noreply@lumina-todo.com
PASSWORD_RESET_TOKEN_EXPIRY_MINUTES=15
PASSWORD_RESET_MAX_REQUESTS_PER_HOUR=3
FRONTEND_URL=http://localhost:3000  # For reset link generation
```

## Security Considerations Verified

1. **Token Entropy**: 256 bits via `secrets.token_urlsafe(32)` ✅
2. **Token Storage**: SHA-256 hash only, never plain ✅
3. **Enumeration Prevention**: Same response for existing/non-existing emails ✅
4. **Rate Limiting**: 3 requests/email/hour ✅
5. **Token Expiry**: 15 minutes enforced server-side ✅
6. **Token Invalidation**: Cleared after successful use ✅
7. **HTTPS**: Assumed for production ✅
