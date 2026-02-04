# Tasks: Phase II Frontend - Todo Web Application

**Input**: Design documents from `/specs/002-phase2-todo-frontend/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api-types.ts, quickstart.md

**Tests**: No automated tests requested for this phase (manual testing via Lighthouse and browser inspection).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` at repository root
- Components: `frontend/src/components/`
- App routes: `frontend/src/app/`
- Utilities: `frontend/src/lib/`
- Types: `frontend/src/types/`

---

## Phase 1: Setup (Shared Infrastructure) - ~90 minutes

**Purpose**: Project initialization, dependencies, and core configuration

- [x] T001 Initialize Next.js 16 project with TypeScript, Tailwind, App Router in `frontend/`
- [x] T002 Install production dependencies (framer-motion, react-hook-form, zod, lucide-react, sonner, date-fns, clsx, tailwind-merge)
- [x] T003 Install Better Auth packages (better-auth, @better-auth/nextjs)
- [x] T004 [P] Initialize Shadcn/ui and install components (button, input, card, dialog, checkbox, select, calendar, badge, skeleton)
- [x] T005 [P] Configure TypeScript strict mode in `frontend/tsconfig.json`
- [x] T006 [P] Configure Tailwind with custom theme (colors, fonts, animations) in `frontend/tailwind.config.ts`
- [x] T007 [P] Create environment files (`frontend/.env.local`, `frontend/.env.example`)
- [x] T008 Create utility functions (cn helper) in `frontend/src/lib/utils.ts`

**Checkpoint**: Next.js project builds successfully with `pnpm dev`

---

## Phase 2: Foundational (Blocking Prerequisites) - ~60 minutes

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create TypeScript types for API contracts in `frontend/src/types/api.ts`
- [x] T010 Create Task and User entity types in `frontend/src/types/entities.ts`
- [x] T011 [P] Create Zod validation schemas in `frontend/src/lib/validations.ts`
- [x] T012 [P] Create API client with JWT attachment and error handling in `frontend/src/lib/api/client.ts`
- [x] T013 Create API endpoint functions (tasks, auth) in `frontend/src/lib/api/endpoints.ts`
- [x] T014 [P] Configure Better Auth client in `frontend/src/lib/auth.ts`
- [x] T015 [P] Create root layout with providers (Toaster, theme) in `frontend/src/app/layout.tsx`
- [x] T016 Create auth middleware for protected routes in `frontend/middleware.ts`

**Checkpoint**: Foundation ready - API client configured, types defined, auth middleware active

---

## Phase 3: User Story 6 - User Authentication (Priority: P1)

**Goal**: Users can create accounts, log in, log out, and access protected routes

**Independent Test**: Visit as unauthenticated user (redirects to login), create account, get redirected to tasks, logout, login again

### Implementation for User Story 6

- [x] T017 [P] [US6] Create auth route group layout in `frontend/src/app/(auth)/layout.tsx`
- [x] T018 [P] [US6] Create LoginForm component with email/password fields in `frontend/src/components/auth/login-form.tsx`
- [x] T019 [P] [US6] Create SignupForm component with validation in `frontend/src/components/auth/signup-form.tsx`
- [x] T020 [US6] Create login page with gradient background in `frontend/src/app/(auth)/login/page.tsx`
- [x] T021 [US6] Create signup page with animated form in `frontend/src/app/(auth)/signup/page.tsx`
- [x] T022 [US6] Create useAuth hook for session management in `frontend/src/hooks/use-auth.ts`
- [x] T023 [US6] Create logout confirmation modal in `frontend/src/components/auth/logout-modal.tsx`
- [x] T024 [US6] Add auth state display and logout button to header

**Checkpoint**: Authentication flow complete - signup, login, logout, protected routes all working

---

## Phase 4: User Story 1 - View and Manage Tasks (Priority: P1)

**Goal**: Users see their tasks displayed as beautiful cards in a responsive grid with filtering

**Independent Test**: Load tasks page, verify responsive card grid displays correctly, filters work, animations smooth

### Implementation for User Story 1

- [x] T025 [P] [US1] Create dashboard route group layout in `frontend/src/app/(dashboard)/layout.tsx`
- [x] T026 [P] [US1] Create Header component with nav and theme toggle in `frontend/src/components/layout/header.tsx`
- [x] T027 [P] [US1] Create TaskCard component with hover effects in `frontend/src/components/tasks/task-card.tsx`
- [x] T028 [P] [US1] Create SkeletonCard component for loading state in `frontend/src/components/tasks/skeleton-card.tsx`
- [x] T029 [P] [US1] Create EmptyState component with illustration in `frontend/src/components/tasks/empty-state.tsx`
- [x] T030 [US1] Create TaskList component with stagger animation in `frontend/src/components/tasks/task-list.tsx`
- [x] T031 [US1] Create FilterTabs component (All/Pending/Completed) in `frontend/src/components/tasks/filter-tabs.tsx`
- [x] T032 [US1] Create useTasks hook for data fetching in `frontend/src/hooks/use-tasks.ts`
- [x] T033 [US1] Create tasks page with responsive grid in `frontend/src/app/(dashboard)/tasks/page.tsx`
- [x] T034 [US1] Add task count badges to filter tabs

**Checkpoint**: Task list displays with cards, skeleton loading, empty state, and filtering all working

---

## Phase 5: User Story 2 - Add New Task (Priority: P1)

**Goal**: Users can create new tasks via a beautiful modal form with optimistic updates

**Independent Test**: Click Add Task, fill all fields, submit, verify task appears instantly with success toast

### Implementation for User Story 2

- [x] T035 [P] [US2] Create AdaptiveDialog component (center/bottom sheet) in `frontend/src/components/ui/adaptive-dialog.tsx`
- [x] T036 [P] [US2] Create PrioritySelector component with colored badges in `frontend/src/components/tasks/priority-selector.tsx`
- [x] T037 [P] [US2] Create CategorySelect component with icons in `frontend/src/components/tasks/category-select.tsx`
- [x] T038 [P] [US2] Create TagInput component for comma-separated tags in `frontend/src/components/tasks/tag-input.tsx`
- [x] T039 [US2] Create TaskForm component with all fields in `frontend/src/components/tasks/task-form.tsx`
- [x] T040 [US2] Create useOptimistic hook for optimistic mutations in `frontend/src/hooks/use-optimistic.ts`
- [x] T041 [US2] Create AddTaskModal with spring animation in `frontend/src/components/tasks/add-task-modal.tsx`
- [x] T042 [US2] Integrate AddTaskModal with tasks page and useTasks hook
- [x] T043 [US2] Add success toast notification on task creation

**Checkpoint**: Task creation working with modal, form validation, optimistic update, and toast

---

## Phase 6: User Story 3 - Mark Task Complete (Priority: P1)

**Goal**: Users can toggle task completion with beautiful animations and automatic reordering

**Independent Test**: Click checkbox on task, verify animation, styling change, reorder, and toast

### Implementation for User Story 3

- [x] T044 [P] [US3] Create AnimatedCheckbox component with draw effect in `frontend/src/components/ui/animated-checkbox.tsx`
- [x] T045 [US3] Add completion toggle to TaskCard with optimistic update
- [x] T046 [US3] Add completed task styling (strike-through, reduced opacity, green accent)
- [x] T047 [US3] Implement task reordering (completed to bottom) with Framer Motion layout
- [x] T048 [US3] Add completion celebration toast with emoji

**Checkpoint**: Task completion toggle working with animation, styling, reorder, and toast

---

## Phase 7: User Story 4 - Update Existing Task (Priority: P2)

**Goal**: Users can edit tasks via the same beautiful modal with pre-filled values

**Independent Test**: Click task, edit fields, save, verify task updates with appropriate feedback

### Implementation for User Story 4

- [x] T049 [US4] Create EditTaskModal using TaskForm with pre-filled values in `frontend/src/components/tasks/edit-task-modal.tsx`
- [x] T050 [US4] Add unsaved changes detection with warning dialog
- [x] T051 [US4] Integrate EditTaskModal with task card click handler
- [x] T052 [US4] Add update success toast notification

**Checkpoint**: Task editing working with pre-filled form, unsaved changes warning, and optimistic update

---

## Phase 8: User Story 5 - Delete Task (Priority: P2)

**Goal**: Users can delete tasks with confirmation, exit animation, and undo capability

**Independent Test**: Click delete, confirm, watch exit animation, click undo to recover

### Implementation for User Story 5

- [x] T053 [P] [US5] Create DeleteConfirmModal with danger styling in `frontend/src/components/tasks/delete-confirm-modal.tsx`
- [x] T054 [US5] Add AnimatePresence exit animation to TaskCard
- [x] T055 [US5] Implement delete with undo functionality (5 second window)
- [x] T056 [US5] Add undo toast with action button
- [x] T057 [US5] Integrate delete button and modal with task card

**Checkpoint**: Task deletion working with confirmation, exit animation, and undo toast

---

## Phase 9: User Story 7 - Dark Mode Toggle (Priority: P2)

**Goal**: Users can toggle dark mode with smooth transition and persisted preference

**Independent Test**: Click theme toggle, watch transition, refresh page, verify preference persisted

### Implementation for User Story 7

- [x] T058 [P] [US7] Create useTheme hook with system preference detection in `frontend/src/hooks/use-theme.ts`
- [x] T059 [P] [US7] Create ThemeToggle component in `frontend/src/components/layout/theme-toggle.tsx`
- [x] T060 [US7] Add dark mode CSS variables and transitions to global styles in `frontend/src/app/globals.css`
- [x] T061 [US7] Add glow effects to task cards in dark mode
- [x] T062 [US7] Integrate ThemeToggle into Header component

**Checkpoint**: Dark mode toggle working with smooth transition, system preference, and persistence

---

## Phase 10: User Story 8 - Responsive Mobile Experience (Priority: P1)

**Goal**: Application works perfectly on all device sizes with appropriate touch targets

**Independent Test**: View on mobile device/emulator, interact with all features, verify layout adapts

### Implementation for User Story 8

- [x] T063 [US8] Verify and adjust responsive grid breakpoints in task list
- [x] T064 [US8] Ensure all touch targets are minimum 44px x 44px
- [x] T065 [US8] Optimize modal behavior (bottom sheet) on mobile
- [x] T066 [US8] Test and adjust typography and spacing for mobile viewports

**Checkpoint**: All features work correctly on mobile (320px) through desktop (4K)

---

## Phase 11: Polish & Cross-Cutting Concerns - ~60 minutes

**Purpose**: Improvements that affect multiple user stories

- [x] T067 [P] Add ARIA labels to all interactive elements
- [x] T068 [P] Add visible focus indicators for keyboard navigation
- [x] T069 [P] Add skip-to-main-content link in layout
- [x] T070 Verify color contrast meets WCAG 2.1 AA requirements
- [x] T071 Add loading.tsx and error.tsx files for App Router
- [x] T072 [P] Add SEO meta tags and Open Graph configuration
- [ ] T073 Run Lighthouse audit and fix any issues below 90 *(Requires browser: run `npm run dev`, open Chrome DevTools > Lighthouse)*
- [ ] T074 Verify all animations run at 60fps (no jank) *(Requires browser: use Chrome DevTools > Performance profiler)*
- [ ] T075 Final review of bundle size (target < 500KB First Load JS) *(Requires browser: check Network tab on page load)*

**Checkpoint**: Lighthouse scores 90+, all accessibility requirements met, production-ready

> **Note**: T073-T075 require manual browser verification and cannot be automated via code review.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ─── BLOCKS ALL USER STORIES
    ↓
┌───┴───────────────────────────────────────────┐
│ User Stories can proceed after Phase 2:        │
│                                                │
│ US6 (Auth) → Required for all other stories   │
│    ↓                                           │
│ US1 (View) → US2 (Add) → US3 (Complete)       │
│         ↘        ↓                             │
│          US4 (Update)                          │
│          US5 (Delete)                          │
│          US7 (Dark Mode) - Independent         │
│          US8 (Responsive) - Independent        │
└───────────────────────────────────────────────┘
    ↓
Phase 11 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US6 (Auth) | Phase 2 | Phase 2 completion |
| US1 (View) | US6 | US6 T024 (header with auth) |
| US2 (Add) | US1 | US1 T033 (tasks page) |
| US3 (Complete) | US1 | US1 T027 (TaskCard) |
| US4 (Update) | US2 | US2 T039 (TaskForm) |
| US5 (Delete) | US1 | US1 T027 (TaskCard) |
| US7 (Dark Mode) | Phase 2 | Phase 2 completion |
| US8 (Responsive) | US1-US5 | After core features |

### Within Each User Story

1. Reusable components ([P] marked) can run in parallel
2. Page/integration tasks depend on their component tasks
3. Toast/feedback tasks depend on core functionality

### Parallel Opportunities

**Phase 1 (Setup):**
```
T001 → T002 → T003 (sequential - dependencies)
     ↘ T004, T005, T006, T007, T008 (parallel after T001)
```

**Phase 2 (Foundational):**
```
T009 → T010 (types first)
     ↘ T011, T012, T014, T015 (parallel after types)
T012 → T013 (endpoints need client)
All → T016 (middleware after all)
```

**Phase 4 (US1 - View Tasks):**
```
T025, T026, T027, T028, T029 (parallel - different files)
     ↓
T030, T031 (depend on components)
     ↓
T032 → T033 → T034 (sequential)
```

**Phase 5 (US2 - Add Task):**
```
T035, T036, T037, T038 (parallel - different files)
     ↓
T039 (depends on all above)
     ↓
T040 → T041 → T042 → T043 (sequential)
```

---

## Parallel Example: Phase 4 - View Tasks

```bash
# Launch all component tasks together:
Task T025: "Create dashboard route group layout"
Task T026: "Create Header component"
Task T027: "Create TaskCard component"
Task T028: "Create SkeletonCard component"
Task T029: "Create EmptyState component"

# Then launch integration tasks:
Task T030: "Create TaskList component" (needs T027, T028, T029)
Task T031: "Create FilterTabs component"

# Then launch page tasks:
Task T032: "Create useTasks hook"
Task T033: "Create tasks page" (needs T030, T031, T032)
Task T034: "Add task count badges"
```

---

## Implementation Strategy

### MVP First (Authentication + View + Add + Complete)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US6 Authentication
4. Complete Phase 4: US1 View Tasks
5. Complete Phase 5: US2 Add Task
6. Complete Phase 6: US3 Mark Complete
7. **STOP and VALIDATE**: Test core CRUD independently
8. Deploy MVP if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US6 (Auth) → Test independently → Can now log in
3. Add US1 (View) → Test independently → Can see tasks
4. Add US2 (Add) → Test independently → Can create tasks (MVP!)
5. Add US3 (Complete) → Test independently → Can complete tasks
6. Add US4 (Update) → Test independently → Full CRUD
7. Add US5 (Delete) → Test independently → Full functionality
8. Add US7 (Dark Mode) → Test independently → Polish feature
9. Add US8 (Responsive) → Test independently → Mobile ready
10. Complete Polish → Lighthouse 90+, production-ready

### Time Estimates by Phase

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Setup | T001-T008 | 90 minutes |
| Phase 2: Foundational | T009-T016 | 60 minutes |
| Phase 3: US6 Auth | T017-T024 | 60 minutes |
| Phase 4: US1 View | T025-T034 | 75 minutes |
| Phase 5: US2 Add | T035-T043 | 75 minutes |
| Phase 6: US3 Complete | T044-T048 | 45 minutes |
| Phase 7: US4 Update | T049-T052 | 30 minutes |
| Phase 8: US5 Delete | T053-T057 | 45 minutes |
| Phase 9: US7 Dark Mode | T058-T062 | 30 minutes |
| Phase 10: US8 Responsive | T063-T066 | 30 minutes |
| Phase 11: Polish | T067-T075 | 60 minutes |
| Phase 12: Backend API | T076-T083 | 120 minutes |
| Phase 13: Auth Fix | T084-T092 | 30 minutes |
| **TOTAL** | **92 tasks** | **~12.5 hours** |

---

---

## Phase 12: Backend API Implementation - ~120 minutes

**Purpose**: Create FastAPI backend with REST endpoints to replace mock-api.mjs

**Note**: This phase was added during Phase II implementation to provide a real backend for the frontend.

### Implementation for Backend API

- [x] T076 [Backend] Initialize FastAPI project with uv in `api/` directory
- [x] T077 [Backend] Create SQLModel database models (User, Task) in `api/app/models/`
- [x] T078 [Backend] Create Pydantic schemas matching frontend API contracts in `api/app/schemas/`
- [x] T079 [Backend] Implement JWT authentication with bcrypt password hashing in `api/app/core/security.py`
- [x] T080 [Backend] Create authentication routes (register, login, logout, session) in `api/app/routers/auth.py`
- [x] T081 [Backend] Create task CRUD routes (list, create, get, update, delete, toggle) in `api/app/routers/tasks.py`
- [x] T082 [Backend] Configure CORS middleware for frontend integration
- [x] T083 [Backend] Test all API endpoints with curl

**Checkpoint**: Backend API running on localhost:8000 with full CRUD operations verified

---

## Phase 13: Auth Integration Fix - ~30 minutes

**Purpose**: Fix JWT authentication to work properly between frontend and backend

**Note**: This phase was added to fix 401 Unauthorized errors during Phase II verification.

### Implementation for Auth Fix

- [x] T084 [Backend] Update deps.py to accept both Authorization header AND session_token cookie
- [x] T085 [Frontend] Add token storage functions (getAuthToken, setAuthToken, clearAuthToken) in client.ts
- [x] T086 [Frontend] Modify API client to include Authorization: Bearer <token> header
- [x] T087 [Frontend] Update auth endpoints to store token on login/register and clear on logout
- [x] T088 [Frontend] Update useAuth hook to check token before making session requests
- [x] T089 [Frontend] Fix middleware.ts to check `auth_token` cookie instead of `better-auth.session_token`
- [x] T090 [Frontend] Switch token storage from localStorage to cookie for middleware compatibility
- [x] T091 [Integration] Verify full CRUD operations work with JWT token authentication
- [x] T092 [Integration] Verify 401 Unauthorized returned without token

**Checkpoint**: Auth flow working end-to-end with JWT tokens

### API Path Design Decision

The spec suggests `/api/{user_id}/tasks` paths, but the implementation uses `/api/tasks` with JWT-based user identification. This is a **security improvement**:

- User ID is extracted from the verified JWT token, not from URL
- Prevents URL manipulation attacks
- Simpler API surface
- Same security guarantees (user isolation, ownership verification)

---

## Starting the Application

### Backend (FastAPI)
```bash
cd api
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Next.js)
```bash
cd frontend
pnpm install
pnpm dev
```

### Demo Credentials
After starting the backend, register a new account or use the mock-api demo credentials:
- Email: `demo@example.com`
- Password: `password123`

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks target 15-30 minute completion time
- Priority order: US6 → US1 → US2 → US3 → US4 → US5 → US7 → US8
