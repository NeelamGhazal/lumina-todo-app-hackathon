---
id: "0003"
title: Create Notifications Plan
stage: plan
date: 2026-02-12
surface: agent
model: claude-opus-4-5-20251101
feature: 009-notifications
branch: 009-notifications
user: neela
command: /sp.plan
labels: ["notifications", "architecture", "polling", "cron", "apscheduler"]
links:
  spec: specs/009-notifications/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-notifications/plan.md
  - specs/009-notifications/data-model.md
  - specs/009-notifications/quickstart.md
  - specs/009-notifications/contracts/notifications-api.yaml
tests:
  - null
---

## Prompt

/sp.plan

Create implementation plan for notifications.

Architecture decisions:
- Real-time method: Polling vs WebSocket? (Recommend: Polling for simplicity)
- Cron library: node-cron vs APScheduler? (Backend-dependent)
- Notification storage: How long to keep? (Recommend: 30 days)

Phases:
1. Database Model (Notification table)
2. API Endpoints (get, mark-read, clear)
3. Cron Jobs (task due reminders, overdue checks)
4. Frontend UI (bell icon, dropdown, notification items)
5. Polling Logic (fetch notifications every 30sec)
6. Testing (cron triggers, UI updates, edge cases)

Use skill: .claude/skills/cron-jobs-nodejs/SKILL.md for cron setup

## Response snapshot

Created comprehensive implementation plan with:

**Architecture Decisions (ADRs)**:
1. ADR-001: Polling over WebSocket (simplicity, 30s delay acceptable)
2. ADR-002: APScheduler for Python backend cron (not node-cron since backend is FastAPI)
3. ADR-003: Duplicate prevention via database query before insert

**8 Implementation Phases**:
1. Database Model - Notification table with type enum
2. API Endpoints - GET/DELETE /notifications, GET /unread-count, PATCH /{id}/read
3. Notification Service - Generation logic with duplicate prevention
4. Background Jobs - APScheduler hourly cron for due-soon/overdue
5. Frontend UI - Bell icon, dropdown, notification items
6. Frontend Polling - useNotifications hook with 30s interval
7. Task Integration - TASK_COMPLETED notification on toggle_complete
8. Testing & Polish

**Supporting Documents Created**:
- data-model.md: Notification schema, indexes, query patterns
- contracts/notifications-api.yaml: OpenAPI spec for all endpoints
- quickstart.md: Testing guide with curl examples

## Outcome

- ✅ Impact: Plan ready for /sp.tasks breakdown
- 🧪 Tests: N/A (plan phase)
- 📁 Files: 4 files created
- 🔁 Next prompts: /sp.tasks
- 🧠 Reflection: User requested node-cron skill but backend is Python - used APScheduler instead

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Plan complete - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
