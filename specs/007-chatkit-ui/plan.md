# Implementation Plan: ChatKit UI

**Branch**: `007-chatkit-ui` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Phase III - Part 3: ChatKit UI - Chat Interface for Todo Assistant (Lumina Theme)

## Summary

Build a modern chat interface that connects users with the OpenRouter-powered todo assistant. The UI follows the Lumina Deep Purple Royal theme from Phase II, integrates with existing authentication, and provides real-time conversation with the AI agent via polling.

## Technical Context

**Language/Version**: TypeScript 5.x (strict mode)
**Primary Dependencies**: React 18+, Next.js 16+, Tailwind CSS, framer-motion, react-markdown
**Storage**: Backend (Part 2 agent manages via SQLModel)
**Testing**: Jest + React Testing Library
**Target Platform**: Web (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (frontend-only for this feature)
**Performance Goals**: Message send <500ms perceived, history load <1s
**Constraints**: Lumina theme exact match, 80%+ test coverage
**Scale/Scope**: Single user chat, 50 messages displayed, 3s polling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Spec-Driven Development | PASS | spec.md, plan.md, research.md complete |
| Professional Quality | PASS | TypeScript strict, tests required |
| Visual Excellence | PASS | Lumina theme, animations, responsive |
| Task-Driven Implementation | PASS | tasks.md will define atomic tasks |
| Checkpoint Control | PASS | 4 checkpoints defined |
| AI-First Engineering | PASS | Claude Code generates all code |
| Cloud-Native Mindset | N/A | Frontend only, no infrastructure |

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Port 3000)                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Next.js App Router                    │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │    │
│  │  │ (dashboard) │  │   /tasks    │  │     /chat       │  │    │
│  │  │   layout    │  │    page     │  │      page       │  │    │
│  │  └─────────────┘  └─────────────┘  └────────┬────────┘  │    │
│  │                                              │           │    │
│  │  ┌───────────────────────────────────────────▼────────┐  │    │
│  │  │                  Chat Components                    │  │    │
│  │  │  ChatContainer │ MessageList │ MessageInput │ ...  │  │    │
│  │  └───────────────────────────────────────────┬────────┘  │    │
│  │                                              │           │    │
│  │  ┌───────────────────────────────────────────▼────────┐  │    │
│  │  │                    useChat Hook                     │  │    │
│  │  │   messages │ sendMessage │ loadHistory │ polling   │  │    │
│  │  └───────────────────────────────────────────┬────────┘  │    │
│  │                                              │           │    │
│  │  ┌───────────────────────────────────────────▼────────┐  │    │
│  │  │                   chat.ts API                       │  │    │
│  │  │   sendMessage() │ getHistory() │ getConversations()│  │    │
│  │  └───────────────────────────────────────────┬────────┘  │    │
│  └──────────────────────────────────────────────┼──────────┘    │
└─────────────────────────────────────────────────┼───────────────┘
                                                  │ HTTP (fetch)
                                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Part 2 OpenRouter Agent (Port 8001)             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  POST /chat        │ GET /conversations │ GET /messages │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           OpenRouter API (gpt-4o-mini)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           Part 1 MCP Tools (task operations)             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
ChatPage
└── ChatContainer
    ├── MessageList
    │   ├── MessageBubble (user)
    │   │   └── Timestamp
    │   ├── MessageBubble (assistant)
    │   │   ├── Markdown
    │   │   └── Timestamp
    │   └── TypingIndicator
    ├── EmptyState (when no messages)
    │   └── SuggestedPrompts
    └── MessageInput
        ├── Textarea
        └── SendButton
```

## Project Structure

### Documentation (this feature)

```text
specs/007-chatkit-ui/
├── plan.md              # This file
├── research.md          # Technical decisions
├── data-model.md        # Data types and entities
├── quickstart.md        # Test scenarios
├── contracts/
│   └── frontend-api.yaml # API contract
└── tasks.md             # Implementation tasks (Phase 2)
```

### Source Code (repository root)

```text
frontend/src/
├── app/
│   └── (dashboard)/
│       └── chat/
│           └── page.tsx           # Chat page route
├── components/
│   ├── Chat/
│   │   ├── index.ts               # Barrel export
│   │   ├── ChatContainer.tsx      # Main layout
│   │   ├── MessageList.tsx        # Scrollable message area
│   │   ├── MessageBubble.tsx      # Individual message
│   │   ├── MessageInput.tsx       # Input + send button
│   │   ├── TypingIndicator.tsx    # AI typing animation
│   │   └── EmptyState.tsx         # Welcome + prompts
│   └── layout/
│       └── sidebar.tsx            # Add chat link (modify)
├── lib/
│   └── api/
│       ├── chat.ts                # Chat API functions
│       └── endpoints.ts           # Add chat exports (modify)
├── hooks/
│   └── useChat.ts                 # Chat state management
└── types/
    └── chat.ts                    # TypeScript interfaces

frontend/tests/
└── components/
    └── Chat/
        ├── ChatContainer.test.tsx
        ├── MessageBubble.test.tsx
        ├── MessageInput.test.tsx
        └── useChat.test.ts
```

**Structure Decision**: Frontend-only feature added to existing Phase II Next.js app. No backend changes required.

---

## Architecture Decision Records (ADRs)

### ADR-009: Chat UI Integration Point

**Status**: Accepted

**Context**: Need to integrate chat UI into existing Phase II todo app. Options: new route, modal overlay, or persistent sidebar.

**Decision**: New route `/chat` within `(dashboard)` route group.

**Rationale**:
- Clean separation of concerns (chat is distinct from task management)
- Full-screen chat experience (not cramped in modal)
- Shares dashboard layout (sidebar, header, theme toggle)
- Easy navigation via sidebar link

**Consequences**:
- Extra navigation click to access chat
- Users see chat as separate feature (intentional)
- Full viewport for messages on mobile

### ADR-010: Real-Time Update Strategy

**Status**: Accepted

**Context**: Need to keep chat updated with new messages. WebSocket explicitly excluded from scope.

**Decision**: Poll every 3 seconds when page is visible, pause when hidden.

**Rationale**:
- Simple, reliable implementation
- Works with existing HTTP endpoints
- 3s is fast enough for responsive feel
- Saves resources when tab is hidden

**Alternatives Rejected**:
- WebSocket: Excluded from scope, overkill for this use case
- Long polling: More complex, marginal benefit
- Adaptive polling: Over-engineering for v1

**Consequences**:
- Max 3s delay for new messages
- Simple recovery on network issues (just retry poll)
- Easy to upgrade to WebSocket later if needed

### ADR-011: Direct API Connection

**Status**: Accepted

**Context**: Frontend needs to communicate with Part 2 agent. Options: direct connection or proxy through Phase II backend.

**Decision**: Frontend calls Part 2 agent directly (port 8001).

**Rationale**:
- Part 2 endpoints already exist and are fully functional
- CORS already configured for localhost:3000
- No need to duplicate proxy logic
- Simpler architecture with fewer moving parts

**Alternatives Rejected**:
- Phase II backend proxy: Would duplicate endpoints, add latency
- Environment variable toggle: Over-engineering

**Consequences**:
- Frontend needs to know Part 2 URL (env variable)
- CORS must be configured on Part 2 (already done)
- Auth token passed via header to Part 2

### ADR-012: Optimistic UI Updates

**Status**: Accepted

**Context**: Need fast, responsive UI when sending messages.

**Decision**: Show user message immediately (optimistic), then update with response.

**Rationale**:
- Instant feedback feels better
- Common pattern in chat apps
- Easy to handle errors (rollback + show error state)

**Implementation**:
```typescript
// 1. Show immediately with 'sending' status
setMessages([...messages, { ...userMsg, status: 'sending' }]);

// 2. On success, update status and add AI response
// 3. On error, mark as 'error' with retry option
```

### ADR-013: Thread Management (Delegated)

**Status**: Accepted

**Context**: How to manage conversation threads.

**Decision**: Delegate to Part 2 agent (uses 30-min session timeout).

**Rationale**:
- Part 2 already implements correct behavior
- `get_or_create_conversation()` handles lifecycle
- Frontend just passes `conversation_id` from responses
- User gets automatic session continuity

**Consequences**:
- Frontend doesn't manage thread creation
- Conversation ID comes from API responses
- New thread after 30-min inactivity (automatic)

### ADR-014: Markdown Rendering

**Status**: Accepted

**Context**: AI responses may contain formatted text.

**Decision**: Use react-markdown with remark-gfm for minimal markdown support.

**Supported**:
- Bold, italic
- Inline code, code blocks
- Unordered/ordered lists
- Links

**Not Supported**:
- Tables (too complex for chat bubbles)
- Images (would need hosting)
- Nested blockquotes

**Rationale**:
- AI responses commonly use these formats
- react-markdown is lightweight (~15KB gzipped)
- GFM support covers common patterns

### ADR-015: Lumina Theme Integration

**Status**: Accepted

**Context**: Chat UI must match Phase II Lumina Deep Purple Royal theme.

**Decision**: Use Tailwind `dark:` classes inheriting from Phase II theme.

**Rationale**:
- Automatic theme switching via existing toggle
- No additional theme context needed
- Consistent with rest of app
- Colors documented in spec.md

**Implementation**:
- All chat components use Tailwind classes
- Dark/light variants via `dark:` prefix
- Exact color values from Lumina spec

---

## Implementation Phases

### Phase 3A: Core Components (2-3 hours)

**Purpose**: Build foundational chat UI components

**Deliverables**:
- ChatContainer layout with Lumina styling
- MessageBubble with user/AI variants
- MessageInput with textarea and send button
- TypingIndicator animation
- EmptyState with suggested prompts
- Sidebar link to chat

**Dependencies**: None (uses mock data initially)

### Phase 3B: API Integration (1.5-2 hours)

**Purpose**: Connect components to Part 2 agent

**Deliverables**:
- chat.ts API client functions
- TypeScript interfaces (chat.ts types)
- useChat hook for state management
- Send message flow with optimistic updates
- Load history on mount
- Error handling and retry logic

**Dependencies**: Phase 3A components complete

### Phase 3C: Real-Time & Polish (1-1.5 hours)

**Purpose**: Add polling and UX polish

**Deliverables**:
- Polling mechanism (3s interval, visibility check)
- Auto-scroll logic (conditional on user scroll)
- Markdown rendering in AI messages
- Animations (fade-in, slide-up)
- Mobile responsiveness verification

**Dependencies**: Phase 3B integration complete

### Phase 3D: Testing & Documentation (1.5-2 hours)

**Purpose**: Ensure quality and completeness

**Deliverables**:
- Unit tests for all components
- Integration test for send/receive flow
- Dark/light mode verification
- Coverage report (80%+ target)
- Update README with chat instructions

**Dependencies**: All features complete

---

## Checkpoints

### Checkpoint 1: After Phase 3A

**Verification**:
- [ ] All 6 components render without errors
- [ ] Lumina theme applied correctly (dark/light)
- [ ] Static mockup looks professional
- [ ] Responsive on 375px and 1920px viewports
- [ ] Sidebar shows "Chat" link

**Command**:
```bash
cd frontend && npm run dev
# Navigate to /chat, verify visual appearance
```

### Checkpoint 2: After Phase 3B

**Verification**:
- [ ] Can send message and receive AI response
- [ ] History loads on page mount
- [ ] Conversation ID persists across messages
- [ ] Error states display correctly
- [ ] Retry button works for failed messages

**Command**:
```bash
# Start Part 2 agent
cd chatbot && uv run uvicorn mcp_server.main:app --port 8001

# In another terminal, start frontend
cd frontend && npm run dev

# Test: Send "Add task: test chat" and verify response
```

### Checkpoint 3: After Phase 3C

**Verification**:
- [ ] New messages appear via polling (within 3s)
- [ ] Auto-scroll works (scrolls to bottom on new message)
- [ ] Manual scroll up preserved (no auto-scroll interruption)
- [ ] Markdown renders correctly (bold, lists, code)
- [ ] Animations smooth (no jank)

**Command**:
```bash
# Send message in one tab, verify it appears in another tab within 3s
# (Note: Same user, different conversation_id expected)
```

### Checkpoint 4: After Phase 3D (FINAL)

**Verification**:
- [ ] All tests passing
- [ ] Coverage >= 80%
- [ ] No console errors
- [ ] Dark/light mode switch seamless
- [ ] Demo video recorded

**Command**:
```bash
cd frontend && npm test -- --coverage
# Verify 80%+ coverage on Chat components
```

---

## Testing Strategy

### Unit Tests

| Component | Test Coverage |
|-----------|---------------|
| MessageBubble | Render user/AI variants, timestamps, markdown |
| MessageInput | Validation, submit, keyboard shortcuts |
| TypingIndicator | Animation presence |
| EmptyState | Prompts clickable, insert text |
| useChat | Send, receive, error states, polling |

### Integration Tests

| Flow | Description |
|------|-------------|
| Send message | Type → Submit → Optimistic → Response |
| Load history | Mount → API call → Display messages |
| Error retry | Network fail → Error state → Retry → Success |

### Manual Tests

| Scenario | Steps |
|----------|-------|
| Theme toggle | Switch dark/light, verify colors |
| Mobile | Open on 375px, send message |
| Long conversation | Send 20+ messages, verify scroll |

---

## Dependencies

### New npm Packages

```json
{
  "react-markdown": "^9.0.0",
  "remark-gfm": "^4.0.0",
  "jwt-decode": "^4.0.0"
}
```

### Existing (Already in Phase II)

- framer-motion (animations)
- lucide-react (icons)
- date-fns (relative time)
- tailwindcss (styling)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Part 2 agent not running | Clear error message with instructions |
| CORS issues | Document required CORS config (already done) |
| Slow AI response | Typing indicator, timeout after 30s |
| Theme mismatch | Visual regression in Checkpoint 1 |

---

## Success Criteria

From spec.md:

- [SC-001] Message send + response < 5 seconds
- [SC-002] History load < 1 second
- [SC-003] Responsive 320px-2560px
- [SC-004] Lumina colors exact match
- [SC-005] Keyboard accessible
- [SC-006] Screen reader announcements
- [SC-007] 80%+ test coverage
- [SC-008] No console errors

---

## Next Steps

1. Run `/sp.tasks` to generate tasks.md
2. Start Phase 3A implementation
3. Complete checkpoints in sequence
4. Record demo video after Checkpoint 4
