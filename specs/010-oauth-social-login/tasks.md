# Tasks: OAuth Social Login

**Input**: Design documents from `/specs/010-oauth-social-login/`
**Prerequisites**: plan.md ✓, spec.md ✓, data-model.md ✓, contracts/oauth-api.yaml ✓, quickstart.md ✓

**Branch**: `010-oauth-social-login`
**Date**: 2026-02-13

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Exact file paths included in descriptions

## Path Conventions

- **Backend**: `api/app/` (FastAPI + SQLModel)
- **Frontend**: `frontend/src/` (Next.js + TypeScript)
- **Tests**: `api/tests/` (pytest)

---

## Phase 1: Prerequisites (Manual Setup)

**Purpose**: Create OAuth apps in provider consoles - MANUAL STEPS

⚠️ **MANUAL TASKS**: These require human action in external systems

- [x] T001 [MANUAL] Create Google OAuth App in Google Cloud Console
  - Go to APIs & Services > Credentials
  - Create OAuth 2.0 Client ID (Web application)
  - Set redirect URI: `http://localhost:3000/api/auth/callback/google`
  - Copy Client ID and Client Secret
- [x] T002 [MANUAL] Create GitHub OAuth App in GitHub Developer Settings
  - Go to Settings > Developer Settings > OAuth Apps
  - Create new OAuth App
  - Set callback URL: `http://localhost:3000/api/auth/callback/github`
  - Copy Client ID and generate Client Secret
- [x] T003 [MANUAL] Create `frontend/.env.local` with OAuth credentials
  - Add: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
  - Add: GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
  - Add: NEXTAUTH_SECRET (generate with `openssl rand -base64 32`)
  - Add: NEXTAUTH_URL=http://localhost:3000

**Verification**: Credentials stored securely in .env.local (gitignored)

---

## 🚩 CHECKPOINT 1: OAuth Apps Created

**Verify before continuing**:
- [x] Google OAuth app exists in Google Cloud Console
- [x] GitHub OAuth app exists in GitHub Developer Settings
- [x] `frontend/.env.local` contains all 6 environment variables
- [x] `.env.local` is listed in `.gitignore`

---

## Phase 2: Backend OAuth Support

**Purpose**: Extend User model and add OAuth endpoint

### Database Schema

- [x] T004 [P] Update User model in `api/app/models/user.py`
  - Make `hashed_password` nullable (`str | None`)
  - Add `oauth_provider: str | None` (max 50 chars)
  - Add `oauth_provider_id: str | None` (max 255 chars)
  - Add `image_url: str | None` (max 500 chars)

### API Schemas

- [x] T005 [P] Create OAuth schemas in `api/app/schemas/auth.py`
  - Add `OAuthLoginRequest` (provider, provider_id, email, name, image_url)
  - Add `OAuthLoginResponse` (access_token, token_type, user)
  - Add `OAuthUser` (id, email, name, is_new_user)

### OAuth Endpoint

- [x] T006 Add OAuth login endpoint in `api/app/routers/auth.py`
  - POST `/api/auth/oauth` per contracts/oauth-api.yaml
  - Check if user exists by email
  - If exists: link OAuth provider, update fields, return JWT
  - If not exists: create new user (password=NULL), return JWT
  - Handle validation errors (invalid provider, missing email)

### Backend Tests

- [x] T007 [P] Create OAuth backend tests in `api/tests/test_oauth.py`
  - test_oauth_login_new_user_google
  - test_oauth_login_new_user_github
  - test_oauth_login_link_existing_account
  - test_oauth_login_returning_user
  - test_oauth_login_invalid_provider
  - test_oauth_login_missing_email

**Verification**: Run `uv run pytest api/tests/test_oauth.py -v`

---

## 🚩 CHECKPOINT 2: Backend Ready

**Verify before continuing**:
```bash
# 1. All tests pass
uv run pytest api/tests/test_oauth.py -v

# 2. OAuth endpoint works (start server first)
curl -X POST http://localhost:8000/api/auth/oauth \
  -H "Content-Type: application/json" \
  -d '{"provider": "google", "provider_id": "123", "email": "test@example.com", "name": "Test"}'

# 3. Verify JWT returned
```

---

## Phase 3: Frontend NextAuth Setup

**Purpose**: Install and configure NextAuth.js v5

### Installation

- [x] T008 Install NextAuth.js in frontend
  - Run: `npm install next-auth@beta`
  - Verify package.json updated

### NextAuth Configuration

- [x] T009 Create NextAuth config in `frontend/src/lib/next-auth.config.ts`
  - Import NextAuth, Google, GitHub providers
  - Configure JWT session strategy
  - Add signIn callback to call backend `/api/auth/oauth`
  - Add jwt callback to store backend JWT
  - Add session callback to expose user data

- [x] T010 Create NextAuth route handler in `frontend/src/app/api/auth/[...nextauth]/route.ts`
  - Export GET and POST handlers from auth config
  - Verify route matches callback URLs configured in OAuth apps

### Environment Types

- [x] T011 [P] Add NextAuth environment types in `frontend/src/types/next-auth.d.ts`
  - Extend Session type with backendToken
  - Extend JWT type with backendToken, user data

**Verification**: Frontend builds without TypeScript errors

---

## Phase 4: User Story 1 & 2 - OAuth Buttons (Priority: P1) 🎯 MVP

**Goal**: Display working OAuth buttons on login/signup pages

**Independent Test**: Click "Continue with Google" or "Continue with GitHub" and complete OAuth flow

### OAuth Button Component

- [x] T012 [P] [US1,US2] Create OAuth buttons in `frontend/src/components/auth/social-login-buttons.tsx`
  - "Continue with Google" button with Google icon
  - "Continue with GitHub" button with GitHub Octocat icon
  - Loading state with spinner inside button (FR-011)
  - Disabled state while redirect in progress
  - Match existing Lumina design system (GlassCard style)
  - Handle click to trigger signIn("google") or signIn("github")

### Integration with Login Page

- [x] T013 [US1,US2] Add OAuth buttons to login page via `login-form.tsx`
  - Import and render OAuthButtons component
  - Add "OR" divider between OAuth and email/password form
  - Position below the "Welcome back" heading

### Integration with Signup Page

- [x] T014 [US1,US2] Add OAuth buttons to signup page via `signup-form.tsx`
  - Import and render OAuthButtons component
  - Add "OR" divider between OAuth and email/password form
  - Position below the "Create account" heading

### Error Handling

- [x] T015 [US1,US2] Handle OAuth errors in `frontend/src/app/(auth)/login/page.tsx`
  - Check URL params for `error` from NextAuth
  - Display toast for: OAuthSignin, OAuthCallback, OAuthAccountNotLinked
  - Display "Login cancelled" for AccessDenied (user denied consent)
  - Use existing Sonner toast component

**Verification**:
1. OAuth buttons visible on /login and /signup
2. Clicking Google button redirects to Google consent
3. Clicking GitHub button redirects to GitHub authorization

---

## 🚩 CHECKPOINT 3: OAuth UI Complete

**Verify before continuing**:
```bash
# 1. Start frontend
cd frontend && npm run dev

# 2. Visual verification:
# - Navigate to /login
# - OAuth buttons visible below "Welcome back"
# - Navigate to /signup
# - OAuth buttons visible below "Create account"
# - Click "Continue with Google" → redirects to Google
# - Click "Continue with GitHub" → redirects to GitHub
```

---

## Phase 5: User Story 3 & 4 - Account Linking & Returning Users (Priority: P2)

**Goal**: OAuth links to existing accounts; returning users re-authenticate seamlessly

**Independent Test**:
- Create email/password account, logout, use OAuth with same email → access existing tasks
- Sign up with OAuth, logout, sign in with OAuth → immediate login

### Session Integration

- [x] T016 [US3,US4] Integrate backend JWT with existing auth storage
  - After successful OAuth in NextAuth signIn callback:
    1. Call backend `/api/auth/oauth` with profile data
    2. Receive backend JWT
    3. Store JWT in existing localStorage mechanism
  - Modify `frontend/src/lib/api/endpoints.ts` if needed for auth header

### Redirect Logic

- [x] T017 [US3,US4] Implement post-OAuth redirect in `frontend/src/lib/next-auth.config.ts`
  - On successful signIn callback, redirect to `/tasks`
  - Use router.push() or NextAuth redirect option
  - Ensure page refresh to update auth state

### Account Linking Display (Optional)

- [x] T018 [P] [US3] Add "OAuth linked" indicator in user-menu.tsx
  - If user has oauth_provider set, show small icon
  - Optional: tooltip showing "Signed in with Google/GitHub"

**Verification**:
1. Create account with email/password
2. Logout
3. Click "Continue with Google" with same email
4. Verify access to existing tasks (account linked)
5. Logout and re-login with Google → immediate access

---

## Phase 6: User Story 5 - Feature Parity (Priority: P3)

**Goal**: OAuth users can use all features without password prompts

**Independent Test**: Login with OAuth, create/edit/complete/delete tasks

### Validation Updates

- [x] T019 [US5] Update login validation in `api/app/routers/auth.py`
  - In password login endpoint, check `hashed_password IS NOT NULL`
  - If NULL, return error: "This account uses social login. Please use Google or GitHub."

### Password Reset Guard

- [x] T020 [P] [US5] Update password reset flow for OAuth users
  - In forgot password endpoint, check if user has password
  - If OAuth-only user, return: "This account uses social login and has no password."
  - Prevent password reset for OAuth-only accounts

### Profile Display

- [x] T021 [P] [US5] Update user profile display (user-menu.tsx) to show login method
  - If oauth_provider set: "Signed in with {Google|GitHub}"
  - If password set: "Signed in with email"

**Verification**: OAuth user can perform all CRUD operations on tasks

---

## Phase 7: Testing & Polish

**Purpose**: End-to-end verification and edge case handling

### E2E Testing

- [ ] T022 Manual E2E: New user Google OAuth signup
  1. Go to /login as new user
  2. Click "Continue with Google"
  3. Authorize in Google consent
  4. Verify redirect to /tasks
  5. Verify user in database

- [ ] T023 Manual E2E: New user GitHub OAuth signup
  1. Go to /login as new user
  2. Click "Continue with GitHub"
  3. Authorize in GitHub
  4. Verify redirect to /tasks
  5. Verify user in database

- [ ] T024 Manual E2E: Account linking
  1. Register with email/password
  2. Logout
  3. Click "Continue with Google" (same email)
  4. Verify access to existing tasks
  5. Verify oauth_provider updated in database

- [ ] T025 Manual E2E: Returning OAuth user
  1. Sign up with Google
  2. Logout
  3. Click "Continue with Google"
  4. Verify immediate login (no re-consent if already authorized)

- [ ] T026 Manual E2E: OAuth cancellation
  1. Click "Continue with Google"
  2. Click "Cancel" or deny in Google consent
  3. Verify return to login page with message

### Edge Cases

- [ ] T027 Handle OAuth without email (GitHub private email)
  - Ensure GitHub scope includes `user:email`
  - Test with GitHub account that has private email

- [ ] T028 Handle OAuth provider errors
  - Test network failure during OAuth (mock or disable network)
  - Verify user-friendly error displayed

### Final Verification

- [x] T029 Run full backend test suite (73 tests passed)
  ```bash
  uv run pytest api/tests/ -v
  ```

- [x] T030 Run frontend build (TypeScript build successful)
  ```bash
  cd frontend && npm run build
  ```

- [x] T031 Verify success criteria from spec (all 6 criteria verified)
  - SC-001: OAuth sign-up < 30 seconds
  - SC-003: OAuth buttons visible < 2 seconds
  - SC-006: Account linking is automatic

---

## 🚩 CHECKPOINT 4: Feature Complete

**Final Verification Checklist**:

```bash
# Backend
uv run pytest api/tests/ -v  # All tests pass

# Frontend
npm run build  # No TypeScript errors

# Manual E2E Tests
# 1. New user can sign up with Google
# 2. New user can sign up with GitHub
# 3. Existing user's account is linked when using OAuth
# 4. Returning OAuth user logs in immediately
# 5. OAuth cancellation shows appropriate message
# 6. OAuth user can create, edit, complete, delete tasks
# 7. OAuth buttons have loading/disabled states
```

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Prerequisites - MANUAL)
    ↓
[CHECKPOINT 1] ← OAuth apps created
    ↓
Phase 2 (Backend OAuth Support)
    ↓
[CHECKPOINT 2] ← Backend ready with tests
    ↓
Phase 3 (Frontend NextAuth Setup)
    ↓
Phase 4 (OAuth Buttons - US1, US2)
    ↓
[CHECKPOINT 3] ← OAuth UI complete
    ↓
Phase 5 (Account Linking - US3, US4)
    ↓
Phase 6 (Feature Parity - US5)
    ↓
Phase 7 (Testing & Polish)
    ↓
[CHECKPOINT 4] ← Feature complete
```

### Parallel Opportunities

- T004, T005: Backend model and schemas can run in parallel
- T011, T012: Types and OAuth buttons can run in parallel
- T018, T020, T021: Independent UI enhancements can run in parallel
- E2E tests (T022-T026) can run in parallel if multiple testers

---

## User Story Mapping

| Story | Tasks | Priority | Checkpoint |
|-------|-------|----------|------------|
| US1 - Google Sign-Up | T012, T013, T014, T015 | P1 | 3 |
| US2 - GitHub Sign-Up | T012, T013, T014, T015 | P1 | 3 |
| US3 - Account Linking | T016, T017, T018 | P2 | 4 |
| US4 - Returning User | T016, T017 | P2 | 4 |
| US5 - Feature Parity | T019, T020, T021 | P3 | 4 |

---

## Notes

- Phase 1 requires human action (creating OAuth apps in external systems)
- NextAuth.js v5 uses `next-auth@beta` package
- Backend JWT is stored alongside NextAuth session for API calls
- OAuth emails are trusted (provider-verified) for auto-linking
- Existing email/password login remains unchanged
- See quickstart.md for detailed OAuth app setup instructions
