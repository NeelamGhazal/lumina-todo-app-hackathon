---
id: "0002"
title: Clarify Notification Triggers
stage: spec
date: 2026-02-12
surface: agent
model: claude-opus-4-5-20251101
feature: 009-notifications
branch: 009-notifications
user: neela
command: /sp.clarify
labels: ["notifications", "clarification", "triggers", "ui"]
links:
  spec: specs/009-notifications/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-notifications/spec.md
tests:
  - null
---

## Prompt

/sp.clarify

My notifications specification is in the previous message.
Please analyze for:
1. Notification triggers (exactly when to create due-soon vs overdue?)
2. UI/UX details (dropdown size? max notifications shown? scroll behavior?)
3. Performance concerns (polling every 30sec? cron job frequency?)
4. Edge cases (duplicate notifications? notifications for deleted tasks?)

What should I clarify before planning?

User responses:
Q1: C (Start of day before due_date)
Q2: B (20 notifications with scroll)
Q3: A (Single notification when first overdue)

Rationale: Simpler implementation, good UX, clean code (fewer edge cases)

## Response snapshot

Analyzed spec against 4 focus areas:
- Already clear: polling (30s), cron (hourly), retention (30 days), duplicate prevention, deleted task handling
- Needed clarification: 3 questions

Questions asked:
1. Due-soon trigger timing → User chose: Start of day before due_date
2. Dropdown display limit → User chose: 20 notifications with scroll
3. Overdue notification frequency → User chose: Single notification when first overdue

Updated spec with:
- FR-010: "due soon" notifications at start of day before due_date
- FR-011: Single overdue notification per task (no repeated reminders)
- US2: Dropdown shows up to 20 notifications with scroll
- Edge cases: Added overdue frequency clarification
- Status changed from Draft to Clarified

## Outcome

- ✅ Impact: Spec fully clarified, ready for /sp.plan
- 🧪 Tests: N/A (spec phase)
- 📁 Files: 1 file updated (spec.md)
- 🔁 Next prompts: /sp.plan
- 🧠 Reflection: User prioritized simplicity over complexity - good for 4-5hr timeline

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All clarifications resolved - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
