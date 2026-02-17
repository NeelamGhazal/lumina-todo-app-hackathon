# Feature Specification: Password Reset

**Feature Branch**: `008-password-reset`
**Created**: 2026-02-12
**Status**: Clarified
**Input**: User description: "Implement forgot password and password reset functionality for Evolution-Todo app. Target users: Registered users who forgot their login password. Focus: Secure password reset via email with time-limited tokens."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Request Password Reset (Priority: P1)

A registered user who has forgotten their password visits the login page and clicks "Forgot Password". They enter their registered email address and submit the request. The system sends a password reset email containing a secure, time-limited link.

**Why this priority**: This is the entry point for the entire password reset flow. Without this, users cannot initiate the reset process.

**Independent Test**: Can be fully tested by submitting a valid email address and verifying that an email is sent within 30 seconds. Delivers immediate value by providing users a way to recover their account.

**Acceptance Scenarios**:

1. **Given** a registered user is on the login page, **When** they click "Forgot Password" and enter their registered email, **Then** they see a confirmation message "If an account exists with this email, you will receive a reset link shortly"
2. **Given** a user enters an unregistered email, **When** they submit the reset request, **Then** they see the same confirmation message (to prevent email enumeration attacks)
3. **Given** a user has made 3 reset requests in the last hour, **When** they attempt another request, **Then** they see an error message indicating they must wait before trying again

---

### User Story 2 - Reset Password via Link (Priority: P1)

A user receives the password reset email, clicks the link, and is taken to a secure page where they can set a new password. The new password must meet security requirements.

**Why this priority**: This completes the core reset flow. Users must be able to actually reset their password after receiving the link.

**Independent Test**: Can be tested by clicking a valid reset link and successfully setting a new password that meets all requirements.

**Acceptance Scenarios**:

1. **Given** a user clicks a valid, non-expired reset link, **When** the page loads, **Then** they see a form to enter and confirm their new password
2. **Given** a user enters a password that meets all requirements (min 8 characters, at least 1 uppercase letter, at least 1 number), **When** they submit the form, **Then** their password is updated and they are redirected to the login page with a success message
3. **Given** a user enters a password that doesn't meet requirements, **When** they submit the form, **Then** they see specific validation errors indicating what's missing
4. **Given** a user enters mismatched passwords in the password and confirm fields, **When** they submit, **Then** they see an error message "Passwords do not match"

---

### User Story 3 - Handle Expired/Invalid Links (Priority: P2)

Users who click expired or invalid reset links receive clear feedback and guidance on how to proceed.

**Why this priority**: Important for user experience and security, but secondary to the core happy path.

**Independent Test**: Can be tested by attempting to use an expired or invalid token and verifying appropriate error handling.

**Acceptance Scenarios**:

1. **Given** a user clicks a reset link that has expired (older than 15 minutes), **When** the page loads, **Then** they see a message "This reset link has expired. Please request a new one." with a link to the forgot password page
2. **Given** a user clicks a reset link that has already been used, **When** the page loads, **Then** they see a message "This reset link has already been used. Please request a new one if needed."
3. **Given** a user accesses the reset page with an invalid/malformed token, **When** the page loads, **Then** they see a message "Invalid reset link. Please request a new one."

---

### Edge Cases

- What happens when a user requests a reset while a previous valid token exists? New token replaces the old one, invalidating the previous link.
- How does the system handle concurrent reset requests from the same email? Rate limiting prevents abuse; only the most recent token is valid.
- What happens if the email service fails to send? User sees success message anyway to prevent enumeration; system logs the error for monitoring.
- What happens if user tries to reset to their current password? Allow it - no restriction on reusing current password per requirements.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a "Forgot Password" link on the login page that navigates to the password reset request form
- **FR-002**: System MUST accept an email address input and validate it is properly formatted before processing
- **FR-003**: System MUST generate a cryptographically secure, unique reset token when a valid reset is requested
- **FR-004**: System MUST hash the reset token before storing it (plain token must never be stored)
- **FR-005**: System MUST set token expiry to 15 minutes from generation time
- **FR-006**: System MUST send password reset emails via the configured email service within 30 seconds of request
- **FR-007**: System MUST limit password reset requests to maximum 3 per email address per hour
- **FR-008**: System MUST display a generic success message regardless of whether the email exists (prevent enumeration)
- **FR-009**: System MUST validate reset tokens by comparing hashed values and checking expiry before allowing password change
- **FR-010**: System MUST enforce password requirements: minimum 8 characters, at least 1 uppercase letter, at least 1 number
- **FR-011**: System MUST require password confirmation field that matches the new password
- **FR-012**: System MUST invalidate the reset token immediately after successful password change
- **FR-013**: System MUST redirect users to the login page with a success message after password reset
- **FR-014**: System MUST display clear, user-friendly error messages for expired, invalid, or already-used tokens

### Key Entities

- **User**: Existing entity - extended with reset token (hashed), token expiry timestamp, and reset request tracking for rate limiting
- **PasswordResetAttempt**: Tracks reset attempts for rate limiting - includes email, request timestamp for counting within the rate limit window

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the entire password reset flow (request to new password set) in under 3 minutes
- **SC-002**: 95% of password reset emails are delivered within 30 seconds of request
- **SC-003**: Zero password reset tokens are stored in plain text (all hashed)
- **SC-004**: Rate limiting successfully blocks more than 3 requests per email per hour with 100% accuracy
- **SC-005**: Invalid/expired tokens are rejected 100% of the time with appropriate user feedback
- **SC-006**: Users can successfully log in with their new password immediately after reset

## Assumptions

- Email addresses are unique identifiers for user accounts (one account per email)
- The existing User model can be extended with new fields for reset functionality
- The email service is already configured or can be configured with API credentials
- Users have access to the email address associated with their account
- The frontend login page already exists and can be extended with a "Forgot Password" link
- HTTPS is used for all password reset pages to ensure secure transmission

## Design Decisions (from /sp.clarify)

- **Post-reset notification**: No confirmation email sent after successful password reset - user sees success message on screen only (reset link already validates email ownership)
- **Password strength indicator**: No real-time strength meter - validation errors shown on form submit only (simpler implementation, clear error messages sufficient)

## Out of Scope

- SMS-based password reset
- Security questions
- Multi-factor authentication for reset
- Password history tracking (preventing reuse of previous passwords)
- Account lockout after failed reset attempts
- Admin-initiated password resets
