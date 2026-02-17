# Implementation Plan: OAuth Social Login

**Branch**: `010-oauth-social-login` | **Date**: 2026-02-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-oauth-social-login/spec.md`

## Summary

Implement Google and GitHub OAuth 2.0 social login for Evolution-Todo app, enabling users to sign up/login with one click. OAuth users are auto-linked to existing accounts by email match. The implementation adds NextAuth.js v5 to the frontend for OAuth handling while maintaining compatibility with the existing FastAPI JWT backend.

## Technical Context

**Language/Version**: Python 3.13+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, SQLModel (Backend); NextAuth.js v5, Next.js 16 (Frontend)
**Storage**: SQLite via SQLModel (existing)
**Testing**: pytest (Backend), manual E2E (Frontend)
**Target Platform**: Web (Next.js App Router)
**Project Type**: Web (frontend + backend)
**Performance Goals**: OAuth sign-up < 30s, re-auth < 10s (per SC-001, SC-004)
**Constraints**: JWT sessions only, no database sessions; auto-link by email
**Scale/Scope**: Existing user base, 2 OAuth providers (Google, GitHub)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Spec-Driven Development | ✅ PASS | Full spec with acceptance criteria exists |
| Professional Quality | ✅ PASS | TypeScript strict mode, proper error handling planned |
| Visual Excellence | ✅ PASS | Loading states (FR-011), OAuth button design specified |
| Task-Driven Implementation | ✅ PASS | Will generate tasks.md after plan approval |
| Checkpoint Control | ✅ PASS | Phases defined with clear deliverables |
| AI-First Engineering | ✅ PASS | Claude Code generates all implementation |
| Cloud-Native Mindset | ✅ PASS | Stateless JWT sessions, env vars for secrets |
| Technology Constraint | ⚠️ DEVIATION | User specified NextAuth.js v5 instead of Better Auth |

**Deviation Justification**: User explicitly requested NextAuth.js v5 for OAuth providers. NextAuth.js has mature Google/GitHub provider support and is standard for Next.js App Router. The existing custom JWT auth for email/password remains unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/010-oauth-social-login/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── oauth-api.yaml   # OAuth callback endpoints
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
api/
├── app/
│   ├── models/
│   │   └── user.py           # Extended with OAuth fields
│   ├── routers/
│   │   └── auth.py           # Extended with OAuth endpoints
│   └── core/
│       └── config.py         # OAuth client credentials
└── tests/
    └── test_oauth.py         # OAuth flow tests

frontend/
├── src/
│   ├── app/
│   │   ├── api/auth/[...nextauth]/
│   │   │   └── route.ts      # NextAuth.js route handler
│   │   └── (auth)/
│   │       ├── login/page.tsx      # Add OAuth buttons
│   │       └── signup/page.tsx     # Add OAuth buttons
│   ├── components/
│   │   └── auth/
│   │       └── oauth-buttons.tsx   # Google/GitHub buttons
│   └── lib/
│       └── auth.ts           # NextAuth.js configuration
└── .env.local                # OAuth credentials (gitignored)
```

**Structure Decision**: Web application with separate frontend/backend. OAuth UI handled by NextAuth.js in frontend; backend extended to accept OAuth users and issue JWTs.

## Architecture Decisions

### AD-001: NextAuth.js for OAuth Flow

**Decision**: Use NextAuth.js v5 in frontend for Google/GitHub OAuth, syncing with FastAPI backend

**Rationale**:
- User explicitly requested NextAuth.js v5
- Mature provider support for Google and GitHub
- Handles OAuth state, CSRF, callbacks automatically
- JWT strategy aligns with existing auth architecture

**Alternatives Rejected**:
- Better Auth: Constitution default, but user specified NextAuth.js
- Direct OAuth implementation: More work, security risks

### AD-002: Hybrid Auth Strategy

**Decision**: Frontend uses NextAuth.js for OAuth; backend validates and issues its own JWTs

**Rationale**:
- Keeps existing email/password auth unchanged
- Backend remains the source of truth for user data
- Frontend NextAuth.js handles OAuth flow complexity
- After OAuth success, frontend calls backend `/auth/oauth` endpoint

**Flow**:
1. User clicks "Continue with Google/GitHub"
2. NextAuth.js handles OAuth redirect and callback
3. On success, frontend sends OAuth profile to backend `/auth/oauth`
4. Backend creates/links user, returns JWT
5. Frontend stores JWT as before

### AD-003: Automatic Account Linking by Email

**Decision**: Auto-link OAuth to existing account when emails match (per clarification)

**Rationale**:
- OAuth providers verify email ownership
- Reduces friction for existing users
- Specified in spec clarifications

### AD-004: Nullable Password for OAuth Users

**Decision**: User.hashed_password becomes nullable (per clarification)

**Rationale**:
- OAuth-only users never set a password
- NULL clearly indicates OAuth-only status
- Prevents accidental password login attempts

## Complexity Tracking

| Deviation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| NextAuth.js vs Better Auth | User requirement for OAuth | Better Auth lacks mature Google/GitHub support |
| Hybrid auth (NextAuth + FastAPI JWT) | Maintain existing email/password flow | Full migration too risky mid-project |

## Phase 0: Research Summary

See [research.md](./research.md) for detailed findings.

**Key Decisions**:
1. NextAuth.js v5 with JWT strategy (no database adapter)
2. Backend `/api/auth/oauth` endpoint for user creation/linking
3. OAuth buttons styled to match existing Lumina design system
4. Environment variables: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `NEXTAUTH_SECRET`, `NEXTAUTH_URL`

## Phase 1: Design Artifacts

- [data-model.md](./data-model.md): User model extensions
- [contracts/oauth-api.yaml](./contracts/oauth-api.yaml): OAuth endpoints
- [quickstart.md](./quickstart.md): Setup instructions

## Implementation Phases

### Phase 1: Backend OAuth Support
- Extend User model with OAuth fields (provider, provider_id nullable)
- Make hashed_password nullable
- Add `/api/auth/oauth` endpoint for OAuth user creation/linking
- Add environment variables for OAuth credentials

### Phase 2: Frontend NextAuth Setup
- Install and configure NextAuth.js v5
- Create route handler at `/api/auth/[...nextauth]`
- Configure Google and GitHub providers
- Setup JWT session strategy

### Phase 3: OAuth UI Components
- Create OAuthButtons component (Google, GitHub)
- Add loading states with spinner
- Integrate into login and signup pages
- Handle errors and cancellation

### Phase 4: Integration & Session Sync
- After OAuth success, call backend `/auth/oauth`
- Store returned JWT in existing auth storage
- Redirect to tasks dashboard
- Handle account linking flow

### Phase 5: Testing & Polish
- Test new user OAuth signup (Google, GitHub)
- Test existing user account linking
- Test returning user OAuth login
- Test error handling and cancellation
- Verify all existing features work for OAuth users
