---
id: "0003"
title: oauth-social-login-implementation-plan
stage: plan
date: 2026-02-13
surface: agent
model: claude-opus-4-5-20251101
feature: 010-oauth-social-login
branch: 010-oauth-social-login
user: neela
command: /sp.plan
labels: [oauth, nextauth, implementation-plan, architecture]
links:
  spec: specs/010-oauth-social-login/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/010-oauth-social-login/plan.md
  - specs/010-oauth-social-login/research.md
  - specs/010-oauth-social-login/data-model.md
  - specs/010-oauth-social-login/contracts/oauth-api.yaml
  - specs/010-oauth-social-login/quickstart.md
  - CLAUDE.md
tests:
  - null
---

## Prompt

Create implementation plan for OAuth login.

Architecture decisions:
- NextAuth adapter: Prisma vs None? (Recommend: Prisma for user sync)
- Session strategy: JWT vs Database? (Recommend: JWT for simplicity)
- Account linking: Automatic (by email) vs Manual? (Recommend: Automatic)

Phases:
1. OAuth App Setup (Google Cloud Console + GitHub Settings)
2. NextAuth Configuration (providers, callbacks, adapters)
3. Database Schema (Account, Session models)
4. Frontend Components (OAuth buttons, loading states)
5. Testing (login flow, account linking, errors)

Use skill: /mnt/skills/oauth-nextauth/SKILL.md for best practices

## Response snapshot

Created comprehensive implementation plan with:
- 4 Architecture Decisions (AD-001 to AD-004)
- Technical context aligned with existing FastAPI + Next.js stack
- Hybrid auth strategy: NextAuth.js handles OAuth, backend issues JWTs
- 5 implementation phases defined
- Phase 0 research.md with NextAuth.js v5 configuration patterns
- Phase 1 artifacts: data-model.md, contracts/oauth-api.yaml, quickstart.md
- Constitution check passed with documented deviation (NextAuth.js vs Better Auth)

## Outcome

- Impact: Complete implementation plan with all Phase 0/1 artifacts ready
- Tests: N/A (plan phase)
- Files: plan.md, research.md, data-model.md, oauth-api.yaml, quickstart.md, CLAUDE.md
- Next prompts: /sp.tasks to generate implementation tasks
- Reflection: Hybrid auth approach preserves existing system while adding OAuth

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASS (with documented deviation)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
