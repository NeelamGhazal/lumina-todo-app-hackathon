# Implementation Plan: In-App Notifications

**Branch**: `009-notifications` | **Date**: 2026-02-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-notifications/spec.md`

## Summary

Implement an in-app notification system for task deadline alerts. Users see a notification bell icon with unread count badge in the navbar. Clicking opens a dropdown showing up to 20 recent notifications. System auto-generates notifications for tasks due soon (day before) and overdue tasks via hourly cron job. Frontend polls every 30 seconds for updates.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, SQLModel, APScheduler (Backend); Next.js 16, React 18 (Frontend)
**Storage**: SQLite via SQLModel (existing)
**Testing**: pytest (Backend), manual testing (Frontend)
**Target Platform**: Web application (Vercel frontend, HF Spaces backend)
**Project Type**: Web (frontend + backend)
**Performance Goals**: Dropdown opens <500ms, unread count loads <1s
**Constraints**: Polling every 30s, hourly cron, 30-day retention
**Scale/Scope**: Single user context, ~100s notifications per user

## Architecture Decisions

### ADR-001: Polling over WebSocket

**Decision**: Use HTTP polling (30-second interval) instead of WebSocket for real-time updates.

**Context**: Need to update notification badge without page refresh.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| WebSocket | True real-time, less server load | Complex setup, connection management, HF Spaces limitations |
| Polling | Simple implementation, works everywhere | Slight delay (30s max), more HTTP requests |
| Server-Sent Events | One-way real-time, simpler than WS | Browser support, connection management |

**Decision**: Polling - simpler implementation aligns with 4-5 hour timeline, 30s delay is acceptable per spec.

---

### ADR-002: APScheduler for Backend Cron

**Decision**: Use APScheduler library for Python cron jobs instead of external cron or Celery.

**Context**: Need hourly background jobs for notification generation and cleanup.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| APScheduler | In-process, simple setup, async support | Tied to app process, no distributed locking |
| Celery + Redis | Distributed, robust, retries | Complex setup, requires Redis, overkill for scope |
| External cron (OS/Vercel) | Decoupled | Requires HTTP endpoint exposure, auth complexity |

**Decision**: APScheduler - runs in FastAPI lifespan, simple for single-instance deployment, sufficient for current scale.

---

### ADR-003: Duplicate Prevention via Database Constraint

**Decision**: Prevent duplicate notifications using unique constraint on (task_id, notification_type) for due-soon/overdue notifications.

**Context**: FR-013 requires no duplicate notifications for the same event.

**Implementation**:
- Before creating notification, check if one exists with same task_id + type
- For TASK_COMPLETED, allow multiple (user may complete/uncomplete repeatedly) - use task_id + type + created_at date
- Query: `SELECT 1 FROM notifications WHERE task_id = ? AND type = ?`

---

## Project Structure

### Documentation (this feature)

```text
specs/009-notifications/
├── spec.md              # Feature specification
├── plan.md              # This file
├── data-model.md        # Notification model definition
├── quickstart.md        # Testing guide
├── contracts/           # API contracts
│   └── notifications-api.yaml
└── tasks.md             # Implementation tasks (from /sp.tasks)
```

### Source Code (repository root)

```text
api/
├── app/
│   ├── models/
│   │   └── notification.py      # NEW: Notification model
│   ├── schemas/
│   │   └── notification.py      # NEW: Request/response schemas
│   ├── routers/
│   │   └── notifications.py     # NEW: Notification endpoints
│   ├── services/
│   │   └── notification_service.py  # NEW: Notification generation logic
│   ├── jobs/
│   │   └── scheduler.py         # NEW: APScheduler setup and jobs
│   └── main.py                  # Modified: Add scheduler to lifespan
└── tests/
    └── test_notifications.py    # NEW: Notification tests

frontend/
├── src/
│   ├── components/
│   │   └── notifications/
│   │       ├── notification-bell.tsx      # NEW: Bell icon with badge
│   │       ├── notification-dropdown.tsx  # NEW: Dropdown container
│   │       └── notification-item.tsx      # NEW: Single notification
│   ├── hooks/
│   │   └── use-notifications.ts           # NEW: Polling hook
│   ├── lib/api/
│   │   └── endpoints.ts                   # Modified: Add notification endpoints
│   └── types/
│       └── api.ts                         # Modified: Add notification types
```

## Phase Breakdown

### Phase 1: Database Model (Notification Table)

**Goal**: Create Notification model with all required fields

**Files**:
- `api/app/models/notification.py` (NEW)
- `api/app/models/__init__.py` (MODIFY)

**Notification Model**:
```
- id: UUID (primary key)
- user_id: UUID (foreign key to users)
- task_id: UUID | None (foreign key to tasks, nullable)
- type: NotificationType enum (TASK_DUE_SOON, TASK_OVERDUE, TASK_COMPLETED)
- message: str (notification text)
- is_read: bool (default: False)
- created_at: datetime
```

**Indexes**:
- user_id (for listing user's notifications)
- (task_id, type) (for duplicate prevention queries)
- created_at (for ordering and cleanup)

---

### Phase 2: API Endpoints

**Goal**: CRUD endpoints for notifications

**Files**:
- `api/app/schemas/notification.py` (NEW)
- `api/app/routers/notifications.py` (NEW)
- `api/app/main.py` (MODIFY: add router)

**Endpoints**:

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/notifications` | List notifications (limit 20) | NotificationListResponse |
| GET | `/api/notifications/unread-count` | Get unread count only | {count: number} |
| PATCH | `/api/notifications/{id}/read` | Mark single as read | NotificationResponse |
| DELETE | `/api/notifications` | Clear all notifications | {success: true} |

**Query Parameters for GET /notifications**:
- `limit` (default: 20, max: 50)
- `unread_only` (boolean, default: false)

---

### Phase 3: Notification Generation Service

**Goal**: Business logic for creating notifications

**Files**:
- `api/app/services/notification_service.py` (NEW)

**Functions**:
```python
async def create_notification(
    session: AsyncSession,
    user_id: UUID,
    type: NotificationType,
    message: str,
    task_id: UUID | None = None
) -> Notification | None:
    """Create notification if not duplicate. Returns None if duplicate."""

async def generate_due_soon_notifications(session: AsyncSession) -> int:
    """Find tasks due tomorrow, create notifications. Returns count created."""

async def generate_overdue_notifications(session: AsyncSession) -> int:
    """Find overdue tasks without notification, create them. Returns count."""

async def cleanup_old_notifications(session: AsyncSession, days: int = 30) -> int:
    """Delete notifications older than X days. Returns count deleted."""
```

**Duplicate Prevention Logic**:
- For TASK_DUE_SOON/TASK_OVERDUE: Check `EXISTS (SELECT 1 FROM notifications WHERE task_id = ? AND type = ?)`
- For TASK_COMPLETED: Created inline when task is marked complete (in tasks router)

---

### Phase 4: Background Jobs (APScheduler)

**Goal**: Hourly cron jobs for notification generation and cleanup

**Files**:
- `api/app/jobs/scheduler.py` (NEW)
- `api/app/main.py` (MODIFY: integrate scheduler)

**Jobs**:
| Job | Schedule | Description |
|-----|----------|-------------|
| `generate_task_notifications` | `0 * * * *` (hourly) | Due-soon + overdue checks |
| `cleanup_old_notifications` | `0 0 * * *` (daily midnight) | Delete >30 day old |

**Scheduler Integration**:
```python
# In lifespan handler
async with lifespan(app):
    scheduler.start()
    yield
    scheduler.shutdown()
```

---

### Phase 5: Frontend UI Components

**Goal**: Notification bell, dropdown, and items

**Files**:
- `frontend/src/components/notifications/notification-bell.tsx` (NEW)
- `frontend/src/components/notifications/notification-dropdown.tsx` (NEW)
- `frontend/src/components/notifications/notification-item.tsx` (NEW)
- `frontend/src/components/layout/dashboard-header.tsx` (MODIFY)

**NotificationBell Component**:
- Bell icon from lucide-react (already imported)
- Badge with unread count (hide if 0, show "99+" if >99)
- Click toggles dropdown open/close
- Close on click outside

**NotificationDropdown Component**:
- Positioned below bell (absolute/fixed positioning)
- Scrollable list of NotificationItems (max-height with overflow)
- "Clear all" button in header
- Empty state when no notifications

**NotificationItem Component**:
- Type icon (clock for due-soon, alert for overdue, check for completed)
- Message text
- Relative timestamp ("2 hours ago")
- Mark as read button (checkmark icon)
- Visual distinction for unread (background highlight, bold)

---

### Phase 6: Frontend Polling Logic

**Goal**: Hook for fetching notifications and polling

**Files**:
- `frontend/src/hooks/use-notifications.ts` (NEW)
- `frontend/src/lib/api/endpoints.ts` (MODIFY)
- `frontend/src/types/api.ts` (MODIFY)

**useNotifications Hook**:
```typescript
function useNotifications() {
  // State: notifications[], unreadCount, isLoading, error
  // Poll unread count every 30 seconds
  // Fetch full list when dropdown opens
  // Mutations: markAsRead(id), clearAll()
  // Stop polling when user logged out
}
```

**API Functions**:
- `getNotifications(limit?: number): Promise<NotificationListResponse>`
- `getUnreadCount(): Promise<{count: number}>`
- `markNotificationRead(id: string): Promise<void>`
- `clearAllNotifications(): Promise<void>`

---

### Phase 7: Task Completion Integration

**Goal**: Generate TASK_COMPLETED notification when task is completed

**Files**:
- `api/app/routers/tasks.py` (MODIFY: toggle_complete endpoint)

**Integration Point**:
```python
# In toggle_complete endpoint, after task.completed = True:
if task.completed:
    await create_notification(
        session=session,
        user_id=current_user.id,
        type=NotificationType.TASK_COMPLETED,
        message=f"You completed: {task.title}",
        task_id=task.id
    )
```

---

### Phase 8: Testing & Polish

**Goal**: Verify all functionality works end-to-end

**Tests**:
1. Manual: Create task due tomorrow → run cron → verify notification appears
2. Manual: Create overdue task → run cron → verify single notification
3. Manual: Click bell → dropdown opens → mark as read → badge updates
4. Manual: Clear all → notifications removed
5. Automated: pytest for notification service functions

**Polish**:
- Loading states in dropdown
- Error handling for failed API calls
- Optimistic UI updates for mark-as-read

---

## API Contract Summary

### GET /api/notifications

```yaml
responses:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            notifications:
              type: array
              items:
                $ref: '#/components/schemas/Notification'
            total:
              type: integer
```

### Notification Schema

```yaml
Notification:
  type: object
  properties:
    id:
      type: string
      format: uuid
    userId:
      type: string
      format: uuid
    taskId:
      type: string
      format: uuid
      nullable: true
    type:
      type: string
      enum: [TASK_DUE_SOON, TASK_OVERDUE, TASK_COMPLETED]
    message:
      type: string
    isRead:
      type: boolean
    createdAt:
      type: string
      format: date-time
```

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scheduler doesn't start on HF Spaces | High | Test in deployment, fallback to manual endpoint trigger |
| Duplicate notifications | Medium | Database query before insert, unique constraint |
| Polling causes performance issues | Low | Lightweight unread-count endpoint, 30s interval |
| Time zone issues | Medium | Use UTC throughout, document in spec |

---

## Complexity Tracking

No constitution violations. Architecture follows existing patterns:
- New model extends SQLModel (same as User, Task)
- New router follows existing auth/tasks patterns
- Frontend components follow existing UI patterns

---

## Ready for /sp.tasks

This plan is ready for task breakdown. Key implementation order:
1. Backend model + migrations
2. Backend endpoints (testable independently)
3. Backend cron jobs
4. Frontend components
5. Frontend polling integration
6. Task completion integration
7. End-to-end testing
