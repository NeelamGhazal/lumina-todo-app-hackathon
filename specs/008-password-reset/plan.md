# Implementation Plan: Password Reset

**Branch**: `008-password-reset` | **Date**: 2026-02-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-password-reset/spec.md`

## Summary

Implement secure forgot password and password reset functionality for Evolution-Todo app. Users can request a password reset via email, receive a time-limited token (15 minutes), and set a new password meeting security requirements (8+ chars, 1 uppercase, 1 number). Includes rate limiting (3 requests/email/hour) and security measures (token hashing, enumeration prevention).

## Technical Context

**Language/Version**: Python 3.13+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, SQLModel, Resend (email), Next.js 16+, Tailwind CSS
**Storage**: SQLite (existing, via SQLModel) - extend User model
**Testing**: pytest (backend), manual testing (frontend)
**Target Platform**: Web application (Linux server + browser)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Email sent within 30 seconds, full reset flow under 3 minutes
**Constraints**: 15-minute token expiry, max 3 requests/email/hour, token hashing required
**Scale/Scope**: Single-user password reset, existing user base

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Spec complete and clarified before planning |
| II. Professional Quality | ✅ PASS | Type hints, Pydantic models, error handling planned |
| III. Visual Excellence | ✅ PASS | GlassCard components, consistent with login page design |
| IV. Task-Driven Implementation | ✅ PASS | Tasks will be generated in /sp.tasks phase |
| V. Checkpoint Control | ✅ PASS | Phased approach with review points |
| VI. AI-First Engineering | ✅ PASS | Claude Code generates all implementation |
| VII. Cloud-Native Mindset | ✅ PASS | Stateless design, env vars for secrets |

**Technology Stack Compliance**:
- ✅ Python 3.13+, FastAPI, SQLModel, Pydantic
- ✅ Next.js 16+, TypeScript, Tailwind, Shadcn/ui
- ✅ Environment variables for RESEND_API_KEY

## Project Structure

### Documentation (this feature)

```text
specs/008-password-reset/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
│   └── password-reset-api.yaml
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
api/
├── app/
│   ├── core/
│   │   ├── security.py      # MODIFY: Add token generation/hashing
│   │   ├── config.py        # MODIFY: Add RESEND_API_KEY setting
│   │   └── email.py         # NEW: Resend email service
│   ├── models/
│   │   └── user.py          # MODIFY: Add reset token fields
│   ├── routers/
│   │   └── auth.py          # MODIFY: Add password reset endpoints
│   ├── schemas/
│   │   └── auth.py          # MODIFY: Add reset request/response schemas
│   └── tests/
│       └── test_password_reset.py  # NEW: Password reset tests

frontend/
├── src/
│   ├── app/
│   │   └── (auth)/
│   │       ├── forgot-password/
│   │       │   └── page.tsx         # NEW: Forgot password page
│   │       └── reset-password/
│   │           └── page.tsx         # NEW: Reset password page
│   ├── components/
│   │   └── auth/
│   │       ├── forgot-password-form.tsx  # NEW: Email input form
│   │       └── reset-password-form.tsx   # NEW: New password form
│   └── lib/
│       └── api.ts               # MODIFY: Add password reset API calls
```

**Structure Decision**: Web application structure following existing patterns. Backend extends auth.py router, frontend adds new pages under (auth) route group.

## Architecture Decisions

### ADR-001: Token Generation - UUID vs JWT

**Decision**: UUID (recommended by user)

**Rationale**:
- Simpler implementation - no JWT parsing/validation overhead
- Token is single-use and short-lived (15 minutes)
- No need for JWT claims (user lookup happens via database anyway)
- Easier to invalidate (delete from database)

**Alternatives Rejected**:
- JWT: Adds complexity, harder to invalidate before expiry

### ADR-002: Token Storage - Separate Table vs User Model Fields

**Decision**: User model fields (recommended by user)

**Rationale**:
- Simpler schema - no new table needed
- One token per user at a time (replacing old tokens)
- Easier queries - single table lookup
- Matches existing User model pattern

**Fields to add to User model**:
- `reset_token_hash: str | None` - SHA-256 hash of token
- `reset_token_expiry: datetime | None` - Expiry timestamp
- `reset_request_count: int` - Count for rate limiting (current hour)
- `reset_request_window_start: datetime | None` - Rate limit window start

**Alternatives Rejected**:
- Separate PasswordResetToken table: More complex, unnecessary for single-token-per-user

### ADR-003: Email Template - Plain Text vs HTML

**Decision**: HTML with Resend (recommended by user)

**Rationale**:
- Professional appearance matching Lumina branding
- Resend provides easy HTML email support
- Better user experience with styled button
- Consistent with modern application standards

**Template content**:
- Header with Lumina logo/branding
- Clear message explaining the reset
- Prominent "Reset Password" button
- Expiry warning (15 minutes)
- Security note if user didn't request

### ADR-004: Rate Limiting Implementation

**Decision**: In-database tracking on User model

**Rationale**:
- Simple implementation without external dependencies
- Works for single-instance deployment
- Sliding window using reset_request_window_start field
- Reset count at window boundary

**Implementation**:
- Track count per email per hour
- Reset count when window expires
- Return generic message to prevent enumeration

## Implementation Phases

### Phase 1: Backend Foundation (Priority: P1)

**Scope**: Database schema, security utilities, email service setup

**Tasks**:
1. Update User model with reset token fields
2. Add token generation/hashing to security.py
3. Create email service with Resend integration
4. Add RESEND_API_KEY to config

**Deliverables**:
- Updated User model with migration
- Token generation/validation utilities
- Email service with HTML template

### Phase 2: Backend API Endpoints (Priority: P1)

**Scope**: Three API endpoints for password reset flow

**Endpoints**:
1. `POST /auth/forgot-password` - Request reset (FR-001 to FR-008)
2. `GET /auth/verify-reset-token/{token}` - Verify token validity (FR-009)
3. `POST /auth/reset-password` - Set new password (FR-010 to FR-014)

**Tasks**:
1. Create forgot-password endpoint with rate limiting
2. Create verify-reset-token endpoint
3. Create reset-password endpoint with validation
4. Add request/response schemas

**Deliverables**:
- Three working API endpoints
- Proper error handling and responses
- Rate limiting enforcement

### Phase 3: Frontend Pages (Priority: P1)

**Scope**: Two new pages matching Lumina design

**Pages**:
1. `/forgot-password` - Email input form
2. `/reset-password?token=xxx` - New password form

**Tasks**:
1. Create ForgotPasswordForm component
2. Create ForgotPasswordPage with GlassCard styling
3. Create ResetPasswordForm component with validation
4. Create ResetPasswordPage handling token from URL
5. Add "Forgot Password?" link to login page
6. Update API client with new endpoints

**Deliverables**:
- Two styled pages matching Lumina design
- Form validation with error messages
- Success/error state handling
- Login page updated with forgot password link

### Phase 4: Integration & Testing (Priority: P2)

**Scope**: End-to-end testing and edge cases

**Tasks**:
1. Test full flow: request → email → reset → login
2. Test expired token handling
3. Test invalid token handling
4. Test rate limiting (4th request fails)
5. Test password validation rules
6. Verify token hashing (security audit)

**Deliverables**:
- All acceptance scenarios passing
- Edge cases handled correctly
- Security requirements verified

## Security Checklist

- [ ] Tokens generated with `secrets.token_urlsafe(32)` (256-bit)
- [ ] Tokens hashed with SHA-256 before storage
- [ ] Plain tokens never logged or stored
- [ ] Generic messages prevent email enumeration
- [ ] Rate limiting enforced (3/email/hour)
- [ ] Token expiry checked before allowing reset
- [ ] Token invalidated immediately after use
- [ ] Password validation enforced server-side
- [ ] HTTPS assumed for all traffic

## Environment Variables

```bash
# Add to api/.env
RESEND_API_KEY=re_xxxxxxxxxxxx
PASSWORD_RESET_FROM_EMAIL=noreply@lumina-todo.com
PASSWORD_RESET_TOKEN_EXPIRY_MINUTES=15
PASSWORD_RESET_MAX_REQUESTS_PER_HOUR=3

# Frontend needs API URL (already exists)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Complexity Tracking

> No constitution violations detected. Implementation follows existing patterns.

| Item | Complexity | Justification |
|------|------------|---------------|
| User model extension | Low | 4 new fields, no new tables |
| Email service | Low | Resend SDK is simple |
| Rate limiting | Low | In-database, no Redis needed |
| Frontend pages | Low | Follow existing auth page patterns |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Resend API rate limits | Low | Medium | Free tier supports 100 emails/day |
| Email deliverability | Medium | High | Use verified domain, proper SPF/DKIM |
| Token timing attacks | Low | Medium | Use constant-time comparison |
| Database migration issues | Low | Medium | SQLModel auto-migration |

## Definition of Done

- [ ] All 14 functional requirements implemented
- [ ] All 3 user stories pass acceptance tests
- [ ] Rate limiting blocks 4th request in 1 hour
- [ ] Tokens properly hashed (verified via database inspection)
- [ ] Password validation enforced (8+ chars, 1 upper, 1 number)
- [ ] Email sent within 30 seconds
- [ ] Full flow completes in under 3 minutes
- [ ] Login page has "Forgot Password?" link
- [ ] Reset success redirects to login with message
- [ ] No security vulnerabilities (enumeration, plain tokens)
