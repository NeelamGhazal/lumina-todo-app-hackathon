---
id: "0004"
title: Generate Notifications Tasks
stage: tasks
date: 2026-02-12
surface: agent
model: claude-opus-4-5-20251101
feature: 009-notifications
branch: 009-notifications
user: neela
command: /sp.tasks
labels: ["notifications", "tasks", "checkpoints", "cron", "testability"]
links:
  spec: specs/009-notifications/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-notifications/tasks.md
tests:
  - null
---

## Prompt

/sp.tasks

Generate task breakdown for notifications.

Checkpoint structure:
- CHECKPOINT 1: After database + API endpoints ready
- CHECKPOINT 2: After cron jobs configured and tested
- CHECKPOINT 3: After frontend UI complete
- CHECKPOINT 4: After polling + testing complete

Focus on testability (can I verify cron jobs trigger correctly?).

## Response snapshot

Created comprehensive tasks.md with 36 tasks organized in 9 phases:

**Phase Structure**:
1. Database Model (T001-T003) - Notification table with indexes
2. API Endpoints (T004-T007) - CRUD endpoints with tests
3. **CHECKPOINT 1**: Database + API ready
4. Notification Service (T008-T009) - Generation logic, duplicate prevention
5. Background Jobs (T010-T014) - APScheduler cron with **manual trigger endpoint for testability**
6. **CHECKPOINT 2**: Cron jobs tested
7. Task Completion Integration (T015-T016) - TASK_COMPLETED on toggle
8. Frontend Types & API (T017-T018) - TypeScript types
9. Frontend UI Components (T019-T023) - Bell, dropdown, item components
10. **CHECKPOINT 3**: Frontend UI complete
11. Frontend Polling (T024-T026) - useNotifications hook with 30s interval
12. Testing & Polish (T027-T036) - E2E tests, edge cases
13. **CHECKPOINT 4**: Feature complete

**Testability Solution for Cron Jobs**:
- T012: POST `/api/notifications/trigger-job` endpoint
- Returns `{ due_soon_count, overdue_count }` for verification
- Can test duplicate prevention by triggering twice

**User Story Mapping**:
All 7 user stories (US1-US7) mapped to specific tasks with priority alignment.

## Outcome

- ✅ Impact: Task breakdown ready for implementation
- 🧪 Tests: Defined in T007, T009, T014, T027-T029
- 📁 Files: 1 file created (tasks.md)
- 🔁 Next prompts: /sp.implement or manual task execution
- 🧠 Reflection: Manual trigger endpoint is key for cron testability; checkpoints align with user request

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Tasks complete with checkpoints - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
