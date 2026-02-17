---
id: "0001"
title: Create Notifications Spec
stage: spec
date: 2026-02-12
surface: agent
model: claude-opus-4-5-20251101
feature: 009-notifications
branch: 009-notifications
user: neela
command: /sp.specify
labels: ["notifications", "in-app", "polling", "cron"]
links:
  spec: specs/009-notifications/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-notifications/spec.md
  - specs/009-notifications/checklists/requirements.md
tests:
  - null
---

## Prompt

Implement real-time notifications system for Evolution-Todo app.

Target users: All logged-in users who need task reminders
Focus: In-app notification center with task deadline alerts

Success criteria:
- User sees notification bell icon in navbar with unread count badge
- User clicks bell → notification dropdown opens with recent notifications
- Notifications include: task due soon (24h), task overdue, task completed
- User can mark individual notification as read
- User can clear all notifications
- System auto-generates notifications via cron jobs
- Unread count updates every 30 seconds (polling)

Constraints:
- Backend: FastAPI (Python) with notification cron jobs
- Frontend: Next.js 14 with polling (no WebSocket)
- Database: Create Notification model (userId, type, message, isRead, taskId, createdAt)
- Cron schedule: Check tasks every hour for due dates
- Polling interval: 30 seconds for frontend
- Retention: Auto-delete notifications older than 30 days
- Timeline: Complete within 4-5 hours

Not building:
- Push notifications (browser/mobile)
- Email notifications for every notification
- Notification preferences/settings
- Notification sound effects

## Response snapshot

Created comprehensive feature specification for In-App Notifications system:
- 7 prioritized user stories (P1: bell icon, dropdown, mark-as-read; P2: clear all, due soon, overdue; P3: completed)
- 19 functional requirements covering display, interaction, generation, and lifecycle
- 9 measurable success criteria (all technology-agnostic)
- Key entities: Notification model with type enum
- Edge cases documented for high volume, deleted tasks, timezone handling
- Out of scope clearly defined (push, email, preferences, sounds)
- Quality checklist passed all validation items

## Outcome

- ✅ Impact: Specification complete, ready for planning phase
- 🧪 Tests: N/A (spec phase)
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: /sp.clarify (optional) or /sp.plan
- 🧠 Reflection: User provided detailed constraints which eliminated need for clarification questions

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All checklist items PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
