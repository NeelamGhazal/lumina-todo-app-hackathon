# Tasks: In-App Notifications

**Input**: Design documents from `/specs/009-notifications/`
**Prerequisites**: plan.md ✓, spec.md ✓, data-model.md ✓, contracts/notifications-api.yaml ✓, quickstart.md ✓

**Branch**: `009-notifications`
**Date**: 2026-02-12

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- Exact file paths included in descriptions

## Path Conventions

- **Backend**: `api/app/` (FastAPI + SQLModel)
- **Frontend**: `frontend/src/` (Next.js + TypeScript)
- **Tests**: `api/tests/` (pytest)

---

## Phase 1: Database Model (Notification Table)

**Purpose**: Create Notification SQLModel with required fields and indexes

- [x] T001 [P] Create NotificationType enum and Notification model in `api/app/models/notification.py`
  - NotificationType: TASK_DUE_SOON, TASK_OVERDUE, TASK_COMPLETED
  - Notification fields: id (UUID PK), user_id (FK), task_id (FK nullable), type, message (500 char), is_read (bool), created_at
  - Indexes: user_id, (task_id, type), created_at
- [x] T002 Export Notification model in `api/app/models/__init__.py`
- [x] T003 Verify table creation by starting the API server (SQLModel auto-creates)

**Verification**: Run `sqlite3 api/evolution_todo.db ".schema notifications"` to confirm table exists

---

## Phase 2: API Endpoints (Notification CRUD)

**Purpose**: REST endpoints for notification management

### Schemas

- [x] T004 [P] Create notification schemas in `api/app/schemas/notification.py`
  - NotificationResponse: id, userId, taskId, type, message, isRead, createdAt
  - NotificationListResponse: notifications[], total, unreadCount
  - UnreadCountResponse: count

### Router

- [x] T005 Create notifications router in `api/app/routers/notifications.py`
  - GET `/api/notifications` - List notifications (limit param, unread_only param)
  - GET `/api/notifications/unread-count` - Get unread count only
  - PATCH `/api/notifications/{notification_id}/read` - Mark single as read
  - DELETE `/api/notifications` - Clear all notifications
- [x] T006 Register router in `api/app/main.py`

### Verification Tests

- [x] T007 [P] Create `api/tests/test_notifications.py` with tests:
  - test_get_notifications_empty - Returns empty list for new user
  - test_get_notifications_with_data - Returns notifications sorted by created_at DESC
  - test_get_unread_count - Returns correct count
  - test_mark_notification_read - Updates is_read to True
  - test_clear_all_notifications - Deletes all user notifications
  - test_notification_not_found - Returns 404 for invalid ID
  - test_notification_belongs_to_user - Cannot access other user's notifications

**Verification**: Run `uv run pytest api/tests/test_notifications.py -v`

---

## 🚩 CHECKPOINT 1: Database + API Endpoints Ready

**Verify before continuing**:
```bash
# 1. Table exists
sqlite3 api/evolution_todo.db ".schema notifications"

# 2. API endpoints work (with valid JWT)
curl -X GET http://localhost:8000/api/notifications -H "Authorization: Bearer <token>"
curl -X GET http://localhost:8000/api/notifications/unread-count -H "Authorization: Bearer <token>"

# 3. Tests pass
uv run pytest api/tests/test_notifications.py -v
```

---

## Phase 3: Notification Service (Generation Logic)

**Purpose**: Business logic for creating notifications with duplicate prevention

- [ ] T008 Create notification service in `api/app/services/notification_service.py`
  ```python
  async def create_notification(session, user_id, type, message, task_id=None) -> Notification | None
  async def check_duplicate_exists(session, task_id, type) -> bool
  async def generate_due_soon_notifications(session) -> int
  async def generate_overdue_notifications(session) -> int
  async def cleanup_old_notifications(session, days=30) -> int
  ```
- [ ] T009 Add service tests in `api/tests/test_notification_service.py`
  - test_create_notification_success
  - test_create_notification_prevents_duplicates
  - test_generate_due_soon_finds_tasks_due_tomorrow
  - test_generate_overdue_finds_past_due_incomplete
  - test_cleanup_removes_old_notifications

**Verification**: Run `uv run pytest api/tests/test_notification_service.py -v`

---

## Phase 4: Background Jobs (APScheduler Cron)

**Purpose**: Hourly cron for notification generation, daily cleanup

- [ ] T010 Add APScheduler dependency to `api/pyproject.toml`
  - `apscheduler>=3.10.0` (async compatible)
- [ ] T011 Create scheduler module in `api/app/jobs/scheduler.py`
  - Initialize AsyncIOScheduler
  - Job: `generate_task_notifications` - runs hourly (`0 * * * *`)
    - Calls generate_due_soon_notifications()
    - Calls generate_overdue_notifications()
    - Logs count of notifications created
  - Job: `cleanup_old_notifications` - runs daily at midnight (`0 0 * * *`)
    - Calls cleanup_old_notifications(days=30)
    - Logs count of notifications deleted
- [ ] T012 **[TESTABILITY]** Add manual trigger endpoint in `api/app/routers/notifications.py`
  - POST `/api/notifications/trigger-job` (for testing only)
  - Manually runs generate_task_notifications job
  - Returns { "due_soon_count": X, "overdue_count": Y }
- [ ] T013 Integrate scheduler in `api/app/main.py` lifespan handler
  - Start scheduler on app startup
  - Shutdown scheduler on app shutdown
- [ ] T014 Add scheduler tests in `api/tests/test_scheduler.py`
  - test_scheduler_starts_with_app
  - test_manual_trigger_creates_notifications
  - test_no_duplicate_notifications_on_repeated_trigger

**Verification - Cron Job Testability**:
```bash
# 1. Create a task due tomorrow
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "dueDate": "2026-02-13"}'

# 2. Trigger the job manually
curl -X POST http://localhost:8000/api/notifications/trigger-job \
  -H "Authorization: Bearer <token>"

# 3. Verify notification was created
curl -X GET http://localhost:8000/api/notifications \
  -H "Authorization: Bearer <token>"

# 4. Trigger again - verify NO duplicate created
curl -X POST http://localhost:8000/api/notifications/trigger-job \
  -H "Authorization: Bearer <token>"
# Response should show due_soon_count: 0 (no new notifications)
```

---

## 🚩 CHECKPOINT 2: Cron Jobs Configured and Tested

**Verify before continuing**:
```bash
# 1. Scheduler logs on startup
# Look for: "Scheduled job 'generate_task_notifications' with pattern '0 * * * *'"

# 2. Manual trigger works
curl -X POST http://localhost:8000/api/notifications/trigger-job \
  -H "Authorization: Bearer <token>"

# 3. Duplicate prevention works (run trigger twice, second returns 0)

# 4. All backend tests pass
uv run pytest api/tests/ -v
```

---

## Phase 5: Task Completion Integration

**Purpose**: Generate TASK_COMPLETED notification on task toggle

- [ ] T015 [US7] Modify task toggle endpoint in `api/app/routers/tasks.py`
  - After `task.completed = True`, call:
    ```python
    await create_notification(
        session=session,
        user_id=current_user.id,
        type=NotificationType.TASK_COMPLETED,
        message=f"You completed: {task.title}",
        task_id=task.id
    )
    ```
- [ ] T016 [US7] Add test in `api/tests/test_tasks.py`
  - test_complete_task_creates_notification

**Verification**: Complete a task via API, verify notification appears

---

## Phase 6: Frontend Types & API Functions

**Purpose**: TypeScript types and API client functions

- [ ] T017 [P] Add notification types in `frontend/src/types/api.ts`
  ```typescript
  type NotificationType = 'TASK_DUE_SOON' | 'TASK_OVERDUE' | 'TASK_COMPLETED'
  interface Notification { id, userId, taskId?, type, message, isRead, createdAt }
  interface NotificationListResponse { notifications, total, unreadCount }
  interface UnreadCountResponse { count }
  ```
- [ ] T018 [P] Add API functions in `frontend/src/lib/api/endpoints.ts`
  - getNotifications(limit?: number): Promise<NotificationListResponse>
  - getUnreadCount(): Promise<UnreadCountResponse>
  - markNotificationRead(id: string): Promise<void>
  - clearAllNotifications(): Promise<void>

---

## Phase 7: Frontend UI Components

**Purpose**: Bell icon, dropdown, and notification items

### Notification Item Component

- [ ] T019 [P] [US2,US3] Create `frontend/src/components/notifications/notification-item.tsx`
  - Props: notification, onMarkRead
  - Display: type icon, message, relative timestamp
  - Visual distinction: unread = bold/highlighted, read = muted
  - Mark-as-read button (checkmark icon)
  - Type icons: Clock (due-soon), AlertTriangle (overdue), CheckCircle (completed)

### Notification Dropdown Component

- [ ] T020 [P] [US2,US4] Create `frontend/src/components/notifications/notification-dropdown.tsx`
  - Props: notifications, unreadCount, onMarkRead, onClearAll, isLoading
  - Header with "Notifications" title and "Clear all" button
  - Scrollable list (max-height ~400px)
  - Empty state: "No notifications yet"
  - Loading state while fetching
  - Up to 20 items displayed

### Notification Bell Component

- [ ] T021 [US1,US2] Create `frontend/src/components/notifications/notification-bell.tsx`
  - Bell icon from lucide-react
  - Badge with unread count (hide if 0, show "99+" if >99)
  - Click handler: toggle dropdown open/close
  - Click outside: close dropdown
  - Absolute/fixed positioning for dropdown

### Integration

- [ ] T022 [US1] Create `frontend/src/components/notifications/index.ts` barrel export
- [ ] T023 [US1] Add NotificationBell to dashboard header in `frontend/src/components/layout/dashboard-header.tsx`
  - Position: right side of navbar, before user menu

---

## 🚩 CHECKPOINT 3: Frontend UI Complete

**Verify before continuing**:
```bash
# 1. Start frontend
cd frontend && npm run dev

# 2. Visual verification:
# - Bell icon visible in navbar
# - Click bell → dropdown opens
# - Click outside → dropdown closes
# - Notifications display with correct styling
# - Unread vs read visual distinction
# - Mark as read button works
# - Clear all button works
# - Empty state shows when no notifications
```

---

## Phase 8: Frontend Polling Logic

**Purpose**: Auto-refresh unread count every 30 seconds

- [ ] T024 [US1] Create `frontend/src/hooks/use-notifications.ts`
  ```typescript
  function useNotifications() {
    // State
    notifications: Notification[]
    unreadCount: number
    isLoading: boolean
    error: Error | null

    // Polling: fetch unread count every 30 seconds
    // Fetch full list only when dropdown opens

    // Mutations
    markAsRead(id: string): Promise<void>
    clearAll(): Promise<void>
    refetch(): Promise<void>

    // Cleanup: stop polling on unmount or logout
  }
  ```
- [ ] T025 [US1] Wire useNotifications hook to NotificationBell component
  - Pass notifications, unreadCount to dropdown
  - Handle loading states
  - Handle errors gracefully (silent retry)
- [ ] T026 [US1] Stop polling when user is not authenticated
  - Check auth state before polling
  - Clear notifications on logout

---

## Phase 9: Testing & Polish

**Purpose**: End-to-end verification and edge case handling

### E2E Testing

- [ ] T027 [US5] E2E Test: Due-soon notification flow
  1. Create task due tomorrow
  2. Trigger job manually
  3. Verify notification appears in dropdown within 30s
  4. Verify badge count updated

- [ ] T028 [US6] E2E Test: Overdue notification flow
  1. Create task with yesterday's due date
  2. Trigger job manually
  3. Verify overdue notification appears
  4. Trigger again - verify NO duplicate

- [ ] T029 [US7] E2E Test: Task completion notification
  1. Complete a task
  2. Verify completion notification appears immediately
  3. Verify badge updates

### Edge Cases

- [ ] T030 Handle deleted tasks: notification message shows task no longer exists
- [ ] T031 Handle 99+ notifications: badge displays "99+"
- [ ] T032 Optimistic UI updates for mark-as-read

### Final Verification

- [ ] T033 Run full test suite
  ```bash
  uv run pytest api/tests/ -v
  ```
- [ ] T034 Run quickstart.md validation
- [ ] T035 Verify polling interval is exactly 30 seconds
- [ ] T036 Verify dropdown opens within 500ms (SC-002)

---

## 🚩 CHECKPOINT 4: Polling + Testing Complete

**Final Verification Checklist**:

```bash
# Backend
uv run pytest api/tests/ -v  # All tests pass

# Frontend
npm run build  # No TypeScript errors

# E2E Manual Tests
# 1. Login → bell icon visible with correct count
# 2. Create task due tomorrow → trigger job → notification appears <30s
# 3. Create overdue task → trigger job → notification appears
# 4. Trigger job again → no duplicate notifications
# 5. Complete task → completion notification appears immediately
# 6. Mark notification read → badge decrements
# 7. Clear all → all notifications removed
# 8. Wait 30s → badge auto-updates (polling works)
# 9. Logout → polling stops
```

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Model)
    ↓
Phase 2 (API)
    ↓
[CHECKPOINT 1] ← Database + API ready
    ↓
Phase 3 (Service) + Phase 4 (Cron) ← Can run in parallel
    ↓
Phase 5 (Task Integration)
    ↓
[CHECKPOINT 2] ← Cron jobs tested
    ↓
Phase 6 (Frontend Types) + Phase 7 (Frontend UI) ← Can run in parallel
    ↓
[CHECKPOINT 3] ← Frontend UI complete
    ↓
Phase 8 (Polling)
    ↓
Phase 9 (Testing)
    ↓
[CHECKPOINT 4] ← Feature complete
```

### Parallel Opportunities

- T001-T003: Model tasks can run in parallel
- T004, T007: Schemas and tests can run in parallel
- Phase 3 + Phase 4: Service and Scheduler can run in parallel after CHECKPOINT 1
- T017, T018: Frontend types and API can run in parallel
- T019, T020, T021: UI components can run in parallel
- T027, T028, T029: E2E tests can run in parallel

---

## User Story Mapping

| Story | Tasks | Priority | Checkpoint |
|-------|-------|----------|------------|
| US1 - Bell Icon + Badge | T021, T023, T024, T025, T026 | P1 | 3, 4 |
| US2 - Dropdown | T019, T020 | P1 | 3 |
| US3 - Mark as Read | T005, T019 | P1 | 1, 3 |
| US4 - Clear All | T005, T020 | P2 | 1, 3 |
| US5 - Due Soon | T008, T011, T012, T027 | P2 | 2 |
| US6 - Overdue | T008, T011, T012, T028 | P2 | 2 |
| US7 - Completed | T015, T016, T029 | P3 | 2 |

---

## Notes

- APScheduler runs in-process with FastAPI - no external dependencies
- Manual trigger endpoint (`/trigger-job`) is critical for testing cron jobs
- Duplicate prevention uses database query, not unique constraint (allows TASK_COMPLETED duplicates)
- Polling interval (30s) is hardcoded in useNotifications hook
- Badge "99+" is a frontend display limit, not an API limit
