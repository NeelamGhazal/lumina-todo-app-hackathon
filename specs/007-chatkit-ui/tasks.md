# Tasks: ChatKit UI - Chat Interface for Todo Assistant

**Input**: Design documents from `/specs/007-chatkit-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/frontend-api.yaml
**Branch**: `007-chatkit-ui`
**Date**: 2026-02-08

**Organization**: Tasks are grouped into 4 phases (3A-3D) matching the implementation plan. Each phase is independently testable with clear checkpoints.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- All file paths are absolute from repository root

---

## Phase 3A: Backend API Layer (~90 mins)

**Purpose**: Create Phase II backend proxy endpoints to Part 2 OpenRouter agent

**Dependencies**: Part 2 OpenRouter agent running on port 8001

### Tasks

- [x] T001 Create chat router scaffold in `api/app/routers/chat.py` with health check endpoint
- [x] T002 Implement POST `/api/chat` endpoint to proxy messages to Part 2 agent in `api/app/routers/chat.py`
- [x] T003 Implement GET `/api/chat/history` endpoint for message retrieval in `api/app/routers/chat.py`
- [x] T004 Add JWT authentication dependency to chat routes in `api/app/routers/chat.py`
- [x] T005 Add error handling and structured logging for chat endpoints in `api/app/routers/chat.py`

**Checkpoint 1**: Backend endpoints working
- [x] Backend endpoints respond to requests
- [x] Can proxy to Part 2 OpenRouter agent (port 8001)
- [x] History retrieval functional
- [x] Auth protecting routes (401 for unauthenticated)

---

## Phase 3B: Frontend Components - Lumina Theme (~150 mins)

**Purpose**: Build all UI components with Lumina Deep Purple Royal theme

**Dependencies**: Phase 3A complete

### Core Layout

- [ ] T006 [P] [US3] Create ChatContainer layout component in `frontend/src/components/Chat/ChatContainer.tsx`
  - Dark BG: `bg-gradient-to-br from-[#1a0033] via-[#2e003e] to-[#120024]`
  - Light BG: `bg-gradient-to-br from-[#ede7f6] to-[#d1c4e9]`
  - Full height flex layout, responsive max-w-4xl

- [ ] T007 [P] [US2] Create MessageList scrollable component in `frontend/src/components/Chat/MessageList.tsx`
  - Scrollable container with ref for auto-scroll
  - Map over messages array
  - Empty state check

### Message Components

- [ ] T008 [P] [US1] [US3] Create MessageBubble component in `frontend/src/components/Chat/MessageBubble.tsx`
  - User Dark: `bg-gradient-to-br from-[#ce93d8] to-[#e1bee7] text-[#1a0033]`
  - User Light: `bg-gradient-to-br from-[#5e35b1] to-[#4a148c] text-white`
  - AI Dark: `bg-white/5 backdrop-blur-[10px] text-[#f3e5f5]`
  - AI Light: `bg-white border border-[#d1c4e9]/50 text-[#1a0033]`
  - Markdown rendering with react-markdown
  - Relative timestamps with date-fns

- [ ] T009 [P] [US1] Create MessageInput component in `frontend/src/components/Chat/MessageInput.tsx`
  - Dark: `bg-white/5 border-[#7e57c2]/30 text-[#f3e5f5] placeholder-[#ce93d8]/80`
  - Light: `bg-white/80 border-[#b39ddb]/50 text-[#1a0033] placeholder-[#5e35b1]/80`
  - Focus Dark: `focus:border-[#b39ddb] focus:ring-[#b39ddb]/15`
  - Focus Light: `focus:border-[#7e57c2] focus:ring-[#7e57c2]/15`
  - Auto-resize textarea (max 4 lines)
  - Enter sends, Shift+Enter newline
  - 500 char limit with counter

- [ ] T010 [P] [US1] Create TypingIndicator component in `frontend/src/components/Chat/TypingIndicator.tsx`
  - Animated dots (Framer Motion)
  - Dark: `text-[#ce93d8]`
  - Light: `text-[#5e35b1]`
  - Fade-in animation

- [ ] T011 [P] [US5] Create EmptyState component in `frontend/src/components/Chat/EmptyState.tsx`
  - Welcome message with AI avatar icon
  - 3 suggested prompts: "Add task...", "Show my tasks", "What's pending today?"
  - Clickable prompts insert text into input
  - Lumina gradient buttons

### Page Integration

- [ ] T012 [US1] Create barrel export in `frontend/src/components/Chat/index.ts`

- [ ] T013 [US1] Create chat page route in `frontend/src/app/(dashboard)/chat/page.tsx`
  - Import and render ChatContainer
  - Protected route (require auth)

- [ ] T014 [US1] Add chat link to sidebar navigation in `frontend/src/components/layout/sidebar.tsx`
  - Chat icon with "Chat" label
  - Active state styling

**Checkpoint 2**: All UI components built
- [ ] All 6 components render without errors
- [ ] Lumina theme applied correctly (both modes)
- [ ] Static mockup with dummy data looks professional
- [ ] Responsive on 375px and 1920px viewports
- [ ] Sidebar shows "Chat" link

---

## Phase 3C: API Integration & State (~110 mins)

**Purpose**: Connect components to backend API with state management

**Dependencies**: Phase 3B complete

### API Layer

- [ ] T015 [P] [US1] Create TypeScript types in `frontend/src/types/chat.ts`
  - `interface Message` (id, role, content, created_at, status?)
  - `interface ChatResponse` (message, conversation_id, tool_calls?)
  - `type MessageRole = "user" | "assistant"`

- [ ] T016 [P] [US1] Create chat API client in `frontend/src/lib/api/chat.ts`
  - `sendMessage(message: string, conversationId?: string): Promise<ChatResponse>`
  - `getHistory(conversationId?: string): Promise<Message[]>`
  - `getConversations(): Promise<ConversationSummary[]>`
  - Use Phase II API client with auth headers
  - Error handling with user-friendly messages

### State Management

- [ ] T017 [US1] [US2] Create useChat hook in `frontend/src/hooks/useChat.ts`
  - State: messages, isLoading, error, isTyping, conversationId
  - `sendMessage(text)`: optimistic update → API call → success/error handling
  - `loadHistory()`: fetch and set messages on mount
  - useEffect to load history on mount

- [ ] T018 [US1] Integrate useChat in ChatContainer in `frontend/src/components/Chat/ChatContainer.tsx`
  - Pass messages to MessageList
  - Pass sendMessage to MessageInput
  - Pass isLoading/isTyping to components
  - Show error banner on error state

### Real-Time Updates

- [ ] T019 [US2] Implement polling for new messages in `frontend/src/hooks/useChat.ts`
  - Poll getHistory every 3 seconds when page visible
  - Use Page Visibility API: document.visibilityState
  - Deduplicate messages by ID
  - Stop polling when page hidden

- [ ] T020 [US2] Implement auto-scroll behavior in `frontend/src/components/Chat/MessageList.tsx`
  - scrollIntoView({ behavior: "smooth" }) on new message
  - Only scroll if user is near bottom (within 100px)
  - Preserve scroll position if user scrolled up manually

**Checkpoint 3**: End-to-end messaging works
- [ ] Can send message and receive AI response
- [ ] History loads on page mount
- [ ] Conversation ID persists across messages
- [ ] Real-time updates via polling (within 3s)
- [ ] Auto-scroll working
- [ ] Error states display correctly
- [ ] Retry button works for failed messages

---

## Phase 3D: Polish & Testing (~100 mins)

**Purpose**: Animations, responsiveness verification, and test coverage

**Dependencies**: Phase 3C complete

### Animations

- [ ] T021 [P] [US1] Add Framer Motion animations in `frontend/src/components/Chat/MessageBubble.tsx`
  - Fade-in animation for new messages
  - Slide-up entrance animation

- [ ] T022 [P] [US5] Add stagger animation for EmptyState prompts in `frontend/src/components/Chat/EmptyState.tsx`

### Responsiveness

- [ ] T023 [US4] Verify mobile responsiveness across all Chat components
  - Test on 375px (iPhone SE)
  - Test on 428px (iPhone Pro Max)
  - Fix input keyboard issues (iOS zoom prevention: font-size 16px)
  - Ensure send button accessible (thumb reach)

### Theme Verification

- [ ] T024 [US3] Verify Lumina Dark/Light mode in all Chat components
  - Verify all color values match spec exactly
  - Check gradients render correctly
  - Verify glassmorphism effects (dark mode)
  - Test theme toggle (instant, no flash)

### Unit Tests

- [ ] T025 [P] Write MessageBubble tests in `frontend/src/__tests__/components/Chat/MessageBubble.test.tsx`
  - Test user vs AI message rendering
  - Test markdown rendering
  - Test timestamps

- [ ] T026 [P] Write MessageInput tests in `frontend/src/__tests__/components/Chat/MessageInput.test.tsx`
  - Test validation (empty input)
  - Test character limit (500 chars)
  - Test keyboard shortcuts (Enter, Shift+Enter)

- [ ] T027 [P] Write useChat hook tests in `frontend/src/__tests__/hooks/useChat.test.ts`
  - Test sendMessage with mocked API
  - Test loadHistory
  - Test error handling
  - Test polling mechanism

- [ ] T028 [P] Write EmptyState tests in `frontend/src/__tests__/components/Chat/EmptyState.test.tsx`
  - Test prompt button clicks
  - Test text insertion into input

### Integration Tests

- [ ] T029 Write integration tests in `frontend/src/__tests__/integration/chat.test.tsx`
  - Test send message flow (MSW mock)
  - Test load history flow
  - Test error handling (network error, 401, 500)

### Final Validation

- [ ] T030 Run test suite and verify 80%+ coverage on Chat components
  - Run: `cd frontend && npm test -- --coverage`
  - Verify coverage report shows >80% on Chat components

- [ ] T031 E2E smoke test: Full conversation flow
  1. Login to Phase II app
  2. Navigate to /chat
  3. Send message "Add task to buy milk"
  4. Verify AI response
  5. Send "Show my tasks"
  6. Verify task list in response
  7. Test on mobile device (real or simulator)
  8. Test error handling (disconnect backend, verify retry)

**Checkpoint 4 (FINAL)**: Phase III Part 3 Complete
- [ ] All tests passing
- [ ] Coverage >= 80% on Chat components
- [ ] No console errors
- [ ] Dark/light mode switch seamless
- [ ] Animations smooth (60fps)
- [ ] Mobile fully responsive
- [ ] Demo video recorded (90 seconds)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 3A (Backend) → Phase 3B (Components) → Phase 3C (Integration) → Phase 3D (Polish)
```

### Task Dependency Graph

```
Phase 3A:
T001 (router) → T002 (send) → T003 (history) → T004 (auth) → T005 (errors)
                                                                    ↓
Phase 3B:                                                    [CHECKPOINT 1]
T006 [P] (container) ─┬─→ T012 (barrel) → T013 (page) → T014 (sidebar)
T007 [P] (list) ──────┤                                            ↓
T008 [P] (bubble) ────┤                                    [CHECKPOINT 2]
T009 [P] (input) ─────┤
T010 [P] (typing) ────┤
T011 [P] (empty) ─────┘

Phase 3C:
T015 [P] (types) ──┬─→ T017 (hook) → T018 (integrate) → T019 (polling) → T020 (scroll)
T016 [P] (api) ────┘                                                          ↓
                                                                      [CHECKPOINT 3]
Phase 3D:
T021 [P] (bubble anim) ──┬─→ T023 (mobile) → T024 (theme verify)
T022 [P] (empty anim) ───┘                           ↓
T025 [P] (bubble tests) ─┬─→ T029 (integration) → T030 (coverage) → T031 (e2e)
T026 [P] (input tests) ──┤                                              ↓
T027 [P] (hook tests) ───┤                                      [CHECKPOINT 4]
T028 [P] (empty tests) ──┘
```

### Parallel Opportunities

**Phase 3B (7 tasks in parallel)**:
- T006, T007, T008, T009, T010, T011 can all run in parallel (different files)

**Phase 3C (2 tasks in parallel)**:
- T015, T016 can run in parallel (types and API client)

**Phase 3D (6 tasks in parallel)**:
- T021, T022 (animations) in parallel
- T025, T026, T027, T028 (unit tests) in parallel

---

## User Story to Task Mapping

| User Story | Priority | Tasks |
|------------|----------|-------|
| US1: Send/Receive Messages | P1 | T001-T005, T008-T010, T012-T018, T021, T025-T027 |
| US2: Conversation History | P2 | T007, T017, T019, T020 |
| US3: Dark/Light Mode | P2 | T006, T008, T024 |
| US4: Mobile Responsive | P3 | T023 |
| US5: Empty State Prompts | P3 | T011, T022, T028 |
| US6: Markdown Rendering | P3 | T008 (included in MessageBubble) |

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 3A: Backend proxy
2. Complete Phase 3B: Core components only (T006, T008, T009, T012-T014)
3. Complete Phase 3C: T015-T018 only
4. **STOP and VALIDATE**: Test send/receive flow
5. Deploy/demo if ready

### Full Implementation

1. Phase 3A → Checkpoint 1 (backend ready)
2. Phase 3B → Checkpoint 2 (UI complete)
3. Phase 3C → Checkpoint 3 (integration complete)
4. Phase 3D → Checkpoint 4 (polish & tests)
5. **PHASE III COMPLETE**

---

## Notes

- All Lumina color values are documented in spec.md Design System Reference section
- Part 2 OpenRouter agent must be running on port 8001 for integration testing
- Phase II authentication (JWT) must be functional
- Test coverage target: 80%+ on Chat components
- Demo video should be 90 seconds or less

---

## Summary

| Phase | Task Count | Time Estimate | Checkpoint |
|-------|------------|---------------|------------|
| 3A: Backend | 5 tasks | ~90 mins | 1: Backend ready |
| 3B: Components | 9 tasks | ~150 mins | 2: UI complete |
| 3C: Integration | 6 tasks | ~110 mins | 3: E2E working |
| 3D: Polish | 11 tasks | ~100 mins | 4: Production ready |
| **Total** | **31 tasks** | **~450 mins** | **4 checkpoints** |
