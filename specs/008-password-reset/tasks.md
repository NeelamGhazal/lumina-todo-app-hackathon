# Tasks: Password Reset

**Input**: Design documents from `/specs/008-password-reset/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/password-reset-api.yaml

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment configuration and dependency installation

- [x] T001 Add Resend dependency to backend in api/pyproject.toml (`uv add resend`)
- [x] T002 [P] Add password reset environment variables to api/.env.example (RESEND_API_KEY, PASSWORD_RESET_FROM_EMAIL, PASSWORD_RESET_TOKEN_EXPIRY_MINUTES, PASSWORD_RESET_MAX_REQUESTS_PER_HOUR, FRONTEND_URL)
- [x] T003 [P] Update Settings class with password reset config in api/app/core/config.py

**Checkpoint**: Dependencies installed, environment configured

---

## Phase 2: Foundational (Backend Infrastructure)

**Purpose**: Core utilities and database schema that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

### Database Schema

- [x] T004 Add reset token fields to User model in api/app/models/user.py (reset_token_hash, reset_token_expiry, reset_request_count, reset_request_window_start)

### Security Utilities

- [x] T005 [P] Add token generation function using secrets.token_urlsafe(32) in api/app/core/security.py
- [x] T006 [P] Add token hashing function using hashlib.sha256 in api/app/core/security.py
- [x] T007 [P] Add password validation function (8+ chars, 1 uppercase, 1 number) in api/app/core/security.py

### Email Service

- [x] T008 Create email service module with Resend integration in api/app/core/email.py
- [x] T009 Create HTML email template for password reset in api/app/core/email.py (render_reset_email_template function)

### Request/Response Schemas

- [x] T010 [P] Add ForgotPasswordRequest schema in api/app/schemas/auth.py
- [x] T011 [P] Add ForgotPasswordResponse schema in api/app/schemas/auth.py
- [x] T012 [P] Add VerifyTokenResponse schema in api/app/schemas/auth.py
- [x] T013 [P] Add ResetPasswordRequest schema in api/app/schemas/auth.py
- [x] T014 [P] Add ResetPasswordResponse schema in api/app/schemas/auth.py
- [x] T015 [P] Add PasswordValidationErrorResponse schema in api/app/schemas/auth.py

**Checkpoint**: Foundation ready - All schemas, utilities, and email service complete. User story implementation can now begin.

---

## Phase 3: User Story 1 - Request Password Reset (Priority: P1) MVP

**Goal**: Registered users can request a password reset email via the forgot password form

**Independent Test**: Submit a valid email address, verify generic success message displayed, verify email sent within 30 seconds

**Acceptance Criteria**:
1. "Forgot Password" link on login page navigates to reset request form
2. Generic message shown for both existing and non-existing emails (FR-008)
3. Rate limiting blocks 4th request within 1 hour (FR-007)

### Backend Implementation (US1)

- [x] T016 [US1] Implement rate limiting logic helper function in api/app/routers/auth.py (check_rate_limit, update_rate_limit)
- [x] T017 [US1] Implement POST /auth/forgot-password endpoint in api/app/routers/auth.py
- [x] T018 [US1] Add email sending call in forgot-password endpoint with error logging in api/app/routers/auth.py

### Frontend Implementation (US1)

- [x] T019 [P] [US1] Add forgotPassword API function in frontend/src/lib/api/endpoints.ts
- [x] T020 [US1] Create ForgotPasswordForm component in frontend/src/components/auth/forgot-password-form.tsx
- [x] T021 [US1] Create forgot-password page with GlassCard styling in frontend/src/app/(auth)/forgot-password/page.tsx
- [x] T022 [US1] Add "Forgot Password?" link to login page in frontend/src/app/(auth)/login/page.tsx

**Checkpoint US1**: Users can request password reset. Email sent, generic message shown, rate limiting works.

---

## Phase 4: User Story 2 - Reset Password via Link (Priority: P1)

**Goal**: Users can click the email link and set a new password meeting security requirements

**Independent Test**: Click valid reset link, enter new password meeting all requirements, verify password updated and redirected to login

**Acceptance Criteria**:
1. Valid token shows password reset form (FR-009)
2. Password validation enforces 8+ chars, 1 uppercase, 1 number (FR-010)
3. Password confirmation must match (FR-011)
4. Token invalidated after successful reset (FR-012)
5. Redirect to login with success message (FR-013)

### Backend Implementation (US2)

- [x] T023 [US2] Implement GET /auth/verify-reset-token/{token} endpoint in api/app/routers/auth.py
- [x] T024 [US2] Implement POST /auth/reset-password endpoint in api/app/routers/auth.py
- [x] T025 [US2] Add token validation logic (hash comparison, expiry check) in reset-password endpoint
- [x] T026 [US2] Add password validation using validate_password function in reset-password endpoint
- [x] T027 [US2] Add token invalidation (clear reset_token_hash, reset_token_expiry) after successful reset

### Frontend Implementation (US2)

- [x] T028 [P] [US2] Add verifyResetToken API function in frontend/src/lib/api/endpoints.ts
- [x] T029 [P] [US2] Add resetPassword API function in frontend/src/lib/api/endpoints.ts
- [x] T030 [US2] Create ResetPasswordForm component with validation in frontend/src/components/auth/reset-password-form.tsx
- [x] T031 [US2] Create reset-password page extracting token from URL in frontend/src/app/(auth)/reset-password/page.tsx
- [x] T032 [US2] Add client-side password validation display (requirements checklist) in ResetPasswordForm
- [x] T033 [US2] Handle success redirect to login with toast message in reset-password page

**Checkpoint US2**: Full password reset flow works. User can reset password and login with new credentials.

---

## Phase 5: User Story 3 - Handle Expired/Invalid Links (Priority: P2)

**Goal**: Users with expired or invalid tokens see clear error messages and can request a new link

**Independent Test**: Access reset page with expired/invalid token, verify appropriate error message, verify link to request new reset

**Acceptance Criteria**:
1. Expired token shows "This reset link has expired" with link to forgot password (FR-014)
2. Already-used token shows "This reset link has already been used"
3. Invalid/malformed token shows "Invalid reset link"

### Backend Implementation (US3)

- [x] T034 [US3] Add distinct error responses for expired vs invalid vs used tokens in verify-reset-token endpoint
- [x] T035 [US3] Add distinct error responses in reset-password endpoint for all token states

### Frontend Implementation (US3)

- [x] T036 [US3] Handle expired token state in reset-password page with "Request new link" button
- [x] T037 [US3] Handle invalid token state in reset-password page with error message
- [x] T038 [US3] Handle already-used token state in reset-password page (treated as invalid per ADR-002)
- [x] T039 [US3] Add loading state while verifying token on page load

**Checkpoint US3**: All error states handled gracefully with clear user guidance.

---

## Phase 6: Integration Testing & Security Verification

**Purpose**: End-to-end validation and security hardening

### Manual Testing

- [x] T040 Test full flow: request reset email → click link → set new password → login with new password
- [x] T041 Test rate limiting: make 4 requests in 1 hour, verify 4th is blocked with 429 response
- [x] T042 Test expired token: wait 15+ minutes, verify token rejected with appropriate message
- [x] T043 Test invalid token: use malformed token, verify rejection
- [x] T044 Test password validation: submit passwords missing requirements, verify validation errors
- [x] T045 Test enumeration prevention: request reset for non-existent email, verify same response as existing

### Security Verification

- [x] T046 Verify token hash stored in database (not plain token) by inspecting users table
- [x] T047 Verify plain token never appears in logs (check api logs)
- [x] T048 Verify token cleared from database after successful password reset

### Backend Tests (pytest)

- [x] T049 [P] Create test file api/app/tests/test_password_reset.py
- [x] T050 [P] Add test for forgot-password endpoint (success case)
- [x] T051 [P] Add test for forgot-password rate limiting
- [x] T052 [P] Add test for verify-reset-token endpoint (valid/invalid/expired)
- [x] T053 [P] Add test for reset-password endpoint (success case)
- [x] T054 [P] Add test for reset-password password validation errors

**Checkpoint**: All tests pass, security verified, full flow working end-to-end.

---

## Phase 7: Polish & Documentation

**Purpose**: Final cleanup and documentation

- [x] T055 [P] Update API documentation if swagger/redoc enabled
- [x] T056 [P] Add password reset section to project README if exists
- [x] T057 Run quickstart.md validation - verify all curl commands work
- [x] T058 Code review: verify no sensitive data in logs, proper error handling

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational) ─── BLOCKS ALL USER STORIES
    │
    ├──────────────────────────────────┐
    ▼                                  ▼
Phase 3 (US1: Request Reset)    Phase 4 (US2: Reset Password)
    │                                  │
    └──────────────┬───────────────────┘
                   ▼
           Phase 5 (US3: Error Handling)
                   │
                   ▼
           Phase 6 (Testing)
                   │
                   ▼
           Phase 7 (Polish)
```

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - Independent
- **User Story 2 (P1)**: Can start after Phase 2 - Independent, but benefits from US1 completion for full flow testing
- **User Story 3 (P2)**: Depends on US1 and US2 for full error handling context

### Within Each Phase

- Tasks marked [P] can run in parallel
- Backend implementation before frontend for each story
- API functions before components before pages

---

## Parallel Execution Examples

### Phase 2 Parallel Tasks (Security + Schemas)

```bash
# Run in parallel:
T005: Add token generation function
T006: Add token hashing function
T007: Add password validation function
T010-T015: All schema tasks
```

### US1 Backend + Frontend Parallel Start

```bash
# After T017 (forgot-password endpoint) complete:
# Frontend can start while backend finalizes:
T019: Add forgotPassword API function (can start immediately after T017)
```

### US2 API Functions Parallel

```bash
# Run in parallel:
T028: Add verifyResetToken API function
T029: Add resetPassword API function
```

### Phase 6 Tests Parallel

```bash
# All pytest tests can run in parallel:
T049-T054: All test tasks
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T015)
3. Complete Phase 3: User Story 1 (T016-T022)
4. **CHECKPOINT**: Test request reset flow
5. Complete Phase 4: User Story 2 (T023-T033)
6. **CHECKPOINT**: Test full reset flow
7. **MVP COMPLETE**: Users can reset passwords

### Full Feature

8. Complete Phase 5: User Story 3 (T034-T039)
9. Complete Phase 6: Testing (T040-T054)
10. Complete Phase 7: Polish (T055-T058)
11. **FEATURE COMPLETE**: All acceptance criteria met

---

## Summary

| Phase | Tasks | Parallel | Est. Time |
|-------|-------|----------|-----------|
| Phase 1: Setup | 3 | 2 | 15 min |
| Phase 2: Foundational | 12 | 9 | 45 min |
| Phase 3: US1 Request Reset | 7 | 1 | 45 min |
| Phase 4: US2 Reset Password | 11 | 2 | 60 min |
| Phase 5: US3 Error Handling | 6 | 0 | 30 min |
| Phase 6: Testing | 15 | 6 | 60 min |
| Phase 7: Polish | 4 | 2 | 20 min |
| **Total** | **58** | **22** | **~4.5 hrs** |

**MVP Scope**: Phases 1-4 (33 tasks, ~2.5 hours) delivers complete password reset functionality.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- Security-critical: Never log plain tokens, always hash before storage
