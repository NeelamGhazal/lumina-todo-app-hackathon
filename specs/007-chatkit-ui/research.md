# Research: ChatKit UI

**Feature**: 007-chatkit-ui
**Date**: 2026-02-08
**Purpose**: Resolve technical unknowns for ChatKit UI implementation

## Research Summary

All technical decisions have been resolved. The ChatKit UI will integrate with existing Phase II frontend and Part 2 OpenRouter agent.

---

## Decision 1: Backend Proxy Architecture

**Question**: Should frontend call Part 2 agent directly or proxy through Phase II backend?

**Research Findings**:
- Part 2 agent runs on port 8001 (chatbot/mcp_server)
- Phase II backend runs on port 8000 (api/)
- Frontend currently calls `http://localhost:8000/api` exclusively
- Part 2 agent already has CORS configured for localhost:3000
- Part 2 agent has `/chat`, `/conversations`, `/conversations/{id}/messages` endpoints

**Decision**: Frontend calls Part 2 agent directly (port 8001)

**Rationale**:
- Part 2 endpoints already exist and are fully functional
- No need to duplicate proxy logic in Phase II backend
- CORS already configured correctly
- Simpler architecture with fewer moving parts
- Auth can be passed via Authorization header to Part 2

**Alternatives Rejected**:
- Phase II backend proxy: Would require duplicating endpoints, adds latency, no benefit
- Environment variable toggle: Over-engineering for this use case

---

## Decision 2: Chat Route Integration

**Question**: How should chat UI integrate with Phase II app?

**Research Findings**:
- Phase II uses Next.js App Router with route groups: `(auth)`, `(dashboard)`
- Dashboard layout includes sidebar with navigation
- Existing sidebar has Tasks, Categories, Priority sections
- Current routes: `/login`, `/signup`, `/tasks`

**Decision**: New route `/chat` within `(dashboard)` route group

**Rationale**:
- Clean separation of concerns (chat is distinct from task management)
- Full-screen chat experience (not cramped in modal)
- Shares dashboard layout (sidebar, header, theme toggle)
- Easy navigation via sidebar link

**Implementation**:
```
frontend/src/app/(dashboard)/chat/page.tsx
```

---

## Decision 3: Real-Time Update Strategy

**Question**: How to keep chat updated with new messages?

**Research Findings**:
- WebSocket explicitly excluded from scope
- Part 2 agent is HTTP-based (no streaming)
- Page visibility API available in modern browsers
- Typical chat polling intervals: 1-5 seconds

**Decision**: Poll every 3 seconds when page is visible

**Rationale**:
- Simple, reliable, works with existing HTTP endpoints
- 3 seconds is fast enough for responsive UX
- Pausing when hidden saves resources
- No complex reconnection logic needed

**Implementation Pattern**:
```typescript
useEffect(() => {
  if (document.visibilityState !== 'visible') return;
  const interval = setInterval(fetchMessages, 3000);
  return () => clearInterval(interval);
}, [document.visibilityState]);
```

---

## Decision 4: Message Persistence Strategy

**Question**: Where to store messages and how to handle optimistic updates?

**Research Findings**:
- Part 2 agent stores messages in `messages` table via SQLModel
- Part 2 returns `conversation_id` for thread continuity
- Frontend needs optimistic updates for instant feedback

**Decision**: Backend persistence + frontend optimistic updates

**Rationale**:
- Messages persist across sessions (backend DB)
- UI feels instant (optimistic updates)
- Easy recovery from errors (reload from backend)

**Implementation Pattern**:
```typescript
// Optimistic: add pending message immediately
setMessages([...messages, { ...userMsg, status: 'sending' }]);

// On success: update with real message
const response = await sendMessage(text);
setMessages([...messages, response.user_message, response.ai_message]);
```

---

## Decision 5: Thread Management

**Question**: One thread per user or new thread per session?

**Research Findings**:
- Part 2 agent implements 30-minute session timeout
- `get_or_create_conversation()` reuses active conversation within timeout
- New conversation created automatically after timeout
- Conversation ID returned with every response

**Decision**: One thread per user (managed by Part 2 agent)

**Rationale**:
- Part 2 already handles thread lifecycle correctly
- Frontend just passes `conversation_id` from responses
- User gets continuity within 30-min window
- Natural session breaks after inactivity

---

## Decision 6: Markdown Rendering Scope

**Question**: Which markdown features to support?

**Research Findings**:
- AI responses commonly include lists, bold, code
- react-markdown is lightweight (~15KB gzipped)
- remark-gfm adds GitHub-flavored markdown

**Decision**: Minimal markdown via react-markdown

**Supported**:
- **Bold** (`**text**`)
- *Italic* (`*text*`)
- `inline code` (`` `code` ``)
- Code blocks (``` ```code``` ```)
- Unordered lists (`-` or `*`)
- Ordered lists (`1.`, `2.`)
- Links (`[text](url)`)

**Not Supported**:
- Tables (too complex for chat bubbles)
- Images (would need hosting)
- Nested blockquotes

---

## Decision 7: Authentication Integration

**Question**: How to authenticate chat requests?

**Research Findings**:
- Phase II stores JWT in cookie (`auth_token`)
- `getAuthToken()` retrieves token from cookie
- Part 2 agent expects `user_id` in request body
- Phase II backend extracts user_id from JWT

**Decision**: Extract user_id from JWT on frontend, pass to Part 2

**Rationale**:
- JWT is already stored in accessible cookie
- Frontend can decode JWT to get user_id (payload is not encrypted)
- Part 2 validates user_id format (UUID)
- Simple, no backend changes needed

**Implementation**:
```typescript
import { jwtDecode } from 'jwt-decode';

function getUserId(): string {
  const token = getAuthToken();
  if (!token) throw new Error('Not authenticated');
  const decoded = jwtDecode<{ sub: string }>(token);
  return decoded.sub; // user_id is in 'sub' claim
}
```

---

## Decision 8: Error Retry Strategy

**Question**: How to handle failed message sends?

**Research Findings**:
- Network errors are common on mobile
- Exponential backoff prevents thundering herd
- Users expect retry capability

**Decision**: 3 attempts with exponential backoff (1s, 2s, 4s)

**Implementation**:
```typescript
async function sendWithRetry(message: string, attempts = 3): Promise<ChatResponse> {
  for (let i = 0; i < attempts; i++) {
    try {
      return await sendMessage(message);
    } catch (error) {
      if (i === attempts - 1) throw error;
      await sleep(1000 * Math.pow(2, i)); // 1s, 2s, 4s
    }
  }
}
```

---

## Technology Decisions

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Markdown | react-markdown + remark-gfm | Lightweight, GFM support |
| Animations | framer-motion | Already in Phase II |
| Icons | lucide-react | Already in Phase II |
| Date formatting | date-fns | Already in Phase II |
| State management | React hooks (useState, useEffect) | Simple, no Redux needed |
| API client | Fetch API with custom wrapper | Consistent with Phase II |
| Virtualization | Not needed for v1 | <100 messages typical |

---

## Dependencies to Add

```json
{
  "dependencies": {
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "jwt-decode": "^4.0.0"
  }
}
```

---

## Open Questions (None)

All technical decisions have been resolved. Ready for Phase 1 design.
