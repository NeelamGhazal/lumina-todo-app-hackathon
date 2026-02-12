# Feature Specification: In-App Notifications

**Feature Branch**: `009-notifications`
**Created**: 2026-02-12
**Status**: Clarified
**Input**: User description: "Implement real-time notifications system for Evolution-Todo app with in-app notification center and task deadline alerts"

## Clarifications (from /sp.clarify)

| Question | Decision | Rationale |
|----------|----------|-----------|
| Due-soon trigger timing | Start of day before due_date | Simpler logic, user gets full day warning, no complex time math |
| Dropdown display limit | 20 notifications with scroll | Good balance - enough history without overwhelming UI |
| Overdue notification frequency | Single notification when first overdue | No spam - one notification is sufficient, user can see overdue tasks in task list |

**Design Principles Applied**: Simple implementation, good UX, clean code (fewer edge cases)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Notification Bell with Unread Count (Priority: P1)

A logged-in user sees a notification bell icon in the navigation bar. The bell displays a badge showing the count of unread notifications. This provides immediate visual feedback about pending notifications requiring attention.

**Why this priority**: This is the entry point for the entire notification system. Without visible notification indicators, users would not know notifications exist. This is the minimum viable notification experience.

**Independent Test**: Can be fully tested by logging in as a user with unread notifications and verifying the bell icon appears with the correct unread count badge. Delivers immediate awareness of pending notifications.

**Acceptance Scenarios**:

1. **Given** a logged-in user with 5 unread notifications, **When** they view the navbar, **Then** they see a bell icon with a badge showing "5"
2. **Given** a logged-in user with 0 unread notifications, **When** they view the navbar, **Then** they see a bell icon without a badge (or badge showing "0")
3. **Given** a logged-in user viewing the page, **When** a new notification is generated, **Then** the badge count updates within 30 seconds without page refresh
4. **Given** a logged-in user with more than 99 unread notifications, **When** they view the navbar, **Then** the badge shows "99+"

---

### User Story 2 - View Notification Dropdown (Priority: P1)

A user can click on the notification bell to open a dropdown displaying recent notifications. Each notification shows the type, message, and time. Users can quickly scan their notifications without navigating away from their current page.

**Why this priority**: Users need to see their notification content to take action. This completes the core notification viewing experience and enables the mark-as-read functionality.

**Independent Test**: Can be fully tested by clicking the bell icon and verifying the dropdown opens with notification items displaying correct content, type indicators, and timestamps.

**Acceptance Scenarios**:

1. **Given** a logged-in user with notifications, **When** they click the bell icon, **Then** a dropdown opens showing up to 20 most recent notifications (newest first) with scroll if more exist
2. **Given** an open notification dropdown, **When** the user views a notification, **Then** they see the notification type, message, related task name (if applicable), and relative timestamp
3. **Given** an open notification dropdown, **When** the user clicks outside the dropdown, **Then** the dropdown closes
4. **Given** a logged-in user with no notifications, **When** they click the bell icon, **Then** the dropdown shows an empty state message ("No notifications yet")
5. **Given** a user with more than 20 notifications, **When** they open the dropdown, **Then** they can scroll to see all 20 displayed notifications

---

### User Story 3 - Mark Notification as Read (Priority: P1)

A user can mark individual notifications as read to acknowledge them. Read notifications are visually distinct from unread ones, helping users track which items they have already reviewed.

**Why this priority**: This is essential for users to manage their notification state and reduce visual clutter. Without this, users cannot clear their unread count.

**Independent Test**: Can be fully tested by clicking a mark-as-read action on an unread notification and verifying it transitions to read state with updated visual styling and badge count.

**Acceptance Scenarios**:

1. **Given** an unread notification in the dropdown, **When** the user clicks the mark-as-read action, **Then** the notification visually changes to read state
2. **Given** a user marks a notification as read, **When** the action completes, **Then** the unread count badge decreases by 1
3. **Given** an unread notification, **When** viewing the notification list, **Then** unread notifications are visually distinct (e.g., bolder text, background highlight)

---

### User Story 4 - Clear All Notifications (Priority: P2)

A user can clear all notifications at once to quickly reset their notification center. This bulk action saves time when many notifications have accumulated.

**Why this priority**: This is a convenience feature that improves efficiency but is not required for basic notification functionality.

**Independent Test**: Can be fully tested by clicking the "Clear all" action and verifying all notifications are removed and the badge count becomes zero.

**Acceptance Scenarios**:

1. **Given** a user with multiple notifications, **When** they click "Clear all", **Then** all notifications are removed from their notification list
2. **Given** a user clears all notifications, **When** the action completes, **Then** the unread count badge shows 0 or disappears
3. **Given** a user with no notifications, **When** viewing the dropdown, **Then** the "Clear all" action is disabled or hidden

---

### User Story 5 - Receive Task Due Soon Notification (Priority: P2)

Users automatically receive notifications at the start of the day before their task's due date. This proactive alert gives users a full day's warning to complete their tasks.

**Why this priority**: This delivers the core value proposition of the notification system - proactive task deadline awareness. However, it requires the viewing system (P1 stories) to be functional first.

**Independent Test**: Can be fully tested by creating a task due tomorrow, running the cron job today, and verifying the notification appears in the user's notification list.

**Acceptance Scenarios**:

1. **Given** a task with due_date of tomorrow (e.g., Feb 15), **When** the hourly cron runs today (Feb 14), **Then** a "Task due soon" notification is created for the task owner
2. **Given** a "due soon" notification exists, **When** the user views it, **Then** it displays the task name and that it's due tomorrow
3. **Given** a task that has already triggered a "due soon" notification, **When** the cron runs again, **Then** no duplicate notification is created (tracked by task_id + TASK_DUE_SOON type)

---

### User Story 6 - Receive Task Overdue Notification (Priority: P2)

Users receive a single notification when their task first becomes overdue (past due date). No repeated reminders are sent for the same overdue task.

**Why this priority**: Overdue notifications are critical for task management but follow the same pattern as due-soon notifications, making them a natural extension.

**Independent Test**: Can be fully tested by having a task with yesterday's due date, running the cron job, and verifying exactly one overdue notification appears.

**Acceptance Scenarios**:

1. **Given** an incomplete task with due_date in the past (and no existing overdue notification), **When** the hourly cron runs, **Then** a single "Task overdue" notification is created for the task owner
2. **Given** an overdue notification, **When** the user views it, **Then** it displays the task name and that it's overdue
3. **Given** a task that already has an overdue notification, **When** the cron runs on subsequent days, **Then** no additional overdue notifications are created (one notification per overdue task, ever)
4. **Given** an overdue task that the user completes, **When** viewing notifications, **Then** the overdue notification remains (historical record) but no new notifications are generated

---

### User Story 7 - Receive Task Completed Notification (Priority: P3)

Users receive notifications when they complete a task. This provides positive reinforcement and a record of completed work.

**Why this priority**: This is a nice-to-have that provides positive feedback but is not essential for deadline awareness functionality.

**Independent Test**: Can be fully tested by marking a task as complete and verifying a completion notification appears in the notification list.

**Acceptance Scenarios**:

1. **Given** a user completes a task, **When** the task is marked complete, **Then** a "Task completed" notification is created
2. **Given** a completion notification, **When** the user views it, **Then** it displays the completed task name

---

### Edge Cases

- What happens when a user has hundreds of notifications? The dropdown displays the 20 most recent notifications with scrollable list; no separate "View all" page needed
- How does the system handle a task with no due date? No due-soon or overdue notifications are generated for tasks without due dates
- What happens when a task is deleted? Associated notifications for that task remain visible but indicate the task no longer exists (or are cleaned up)
- How does the system handle time zones? All due date calculations use the server's configured timezone (UTC); due_time field is ignored for notification triggers (only due_date matters)
- What happens when a user is logged out? Polling stops, no notifications are fetched until re-authentication
- What happens if polling fails? System silently retries; no error shown to user for transient failures
- What happens if a task is overdue for multiple days? Only one overdue notification is created when task first becomes overdue; no repeated reminders

## Requirements *(mandatory)*

### Functional Requirements

**Notification Display**
- **FR-001**: System MUST display a notification bell icon in the navbar for all logged-in users
- **FR-002**: System MUST display an unread count badge on the bell icon when unread notifications exist
- **FR-003**: System MUST update the unread count automatically every 30 seconds without requiring page refresh
- **FR-004**: System MUST open a notification dropdown when the user clicks the bell icon
- **FR-005**: System MUST display notifications in reverse chronological order (newest first)
- **FR-006**: System MUST visually distinguish unread notifications from read notifications

**Notification Interaction**
- **FR-007**: Users MUST be able to mark individual notifications as read
- **FR-008**: Users MUST be able to clear all notifications at once
- **FR-009**: System MUST immediately update the UI when a notification state changes

**Notification Generation**
- **FR-010**: System MUST automatically generate "due soon" notifications at the start of the day before the task's due_date (e.g., task due Feb 15 → notification created when cron runs on Feb 14)
- **FR-011**: System MUST automatically generate a single "overdue" notification when a task first becomes overdue (past due_date); no repeated reminders for the same overdue task
- **FR-012**: System MUST generate "task completed" notifications when a user completes a task
- **FR-013**: System MUST NOT create duplicate notifications for the same event (tracked via task_id + notification_type combination)
- **FR-014**: System MUST check for due dates and generate notifications hourly via cron job

**Notification Lifecycle**
- **FR-015**: System MUST automatically delete notifications older than 30 days
- **FR-016**: System MUST associate notifications with specific tasks where applicable
- **FR-017**: System MUST link notifications to their associated tasks for easy navigation

**Data Requirements**
- **FR-018**: Each notification MUST include: user reference, notification type, message content, read status, optional task reference, and creation timestamp
- **FR-019**: Notification types MUST include: TASK_DUE_SOON, TASK_OVERDUE, TASK_COMPLETED

### Key Entities

- **Notification**: Represents a single notification for a user. Contains: user reference, type (enum), message (text), read status (boolean), optional task reference, creation timestamp. Belongs to one user, optionally linked to one task.
- **NotificationType**: Enumeration of notification categories: TASK_DUE_SOON (task due within 24 hours), TASK_OVERDUE (task past due date), TASK_COMPLETED (task marked complete)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view their unread notification count within 1 second of page load
- **SC-002**: Notification dropdown opens within 500ms of clicking the bell icon
- **SC-003**: Unread count updates reflect new notifications within 30 seconds of generation
- **SC-004**: Users receive due-soon notifications at least 24 hours before task deadline
- **SC-005**: 100% of tasks with due dates trigger appropriate notifications (due soon, overdue)
- **SC-006**: Zero duplicate notifications are created for the same event
- **SC-007**: All notifications older than 30 days are automatically removed
- **SC-008**: Users can mark a notification as read with a single click
- **SC-009**: Users can clear all notifications with a single action

## Assumptions

- Users are already authenticated via the existing JWT-based authentication system
- Tasks have an optional due_date field that stores date/time information
- The existing navbar component can accommodate the notification bell icon
- Server time is configured in UTC for consistent due date calculations
- The frontend polls the backend rather than using real-time push (WebSocket)

## Out of Scope

- Push notifications (browser/mobile)
- Email notifications for in-app notification events
- User notification preferences/settings
- Notification sound effects
- Notification grouping or bundling
- Snooze/reminder functionality
