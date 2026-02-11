# Feature Specification: ChatKit UI - Chat Interface for Todo Assistant

**Feature Branch**: `007-chatkit-ui`
**Created**: 2026-02-08
**Status**: Draft
**Input**: Phase III - Part 3: ChatKit UI - Chat Interface for Todo Assistant (Lumina Theme)

## Overview

Build a modern chat interface in the frontend that connects users with the OpenRouter-powered todo assistant (from Part 2). Users type natural language requests and see AI responses in a beautiful, real-time chat UI following the **Lumina Deep Purple Royal** theme from Phase II.

### Implementation Note (Hackathon Phase III Compliance)

**Actual Implementation**: The chat interface is delivered as a **floating chat widget** in the bottom-right corner of the Tasks page, rather than a separate `/chat` route. This design:
- Provides contextual access to the AI assistant while viewing tasks
- Uses a collapsible panel that opens/closes via a floating action button
- Automatically refreshes the task list when task-related actions are performed via chat
- Follows modern chat assistant UX patterns (similar to customer support widgets)

## User Scenarios & Testing

### User Story 1 - Send Message and Receive AI Response (Priority: P1)

As a user, I want to type a natural language message and receive an AI response so that I can manage my tasks conversationally.

**Why this priority**: Core chat functionality - without this, there is no chat feature. This is the minimal viable product.

**Independent Test**: Can be fully tested by opening chat, typing "Hello", and receiving an AI response. Delivers immediate value by enabling conversation with the AI assistant.

**Acceptance Scenarios**:

1. **Given** the chat page is open and user is authenticated, **When** user types "Add a task to buy groceries" and clicks send, **Then** user message appears immediately (optimistic UI) and AI response appears within 5 seconds confirming task creation.

2. **Given** user has sent a message, **When** AI is processing, **Then** typing indicator displays "AI is typing..." with animation.

3. **Given** network error occurs, **When** message send fails, **Then** error message displays with retry button, user message shows error state.

---

### User Story 2 - View Conversation History (Priority: P2)

As a user, I want to see my previous conversation when I return to chat so that I can continue where I left off.

**Why this priority**: Essential for continuity - users expect chat history to persist. Without this, each session starts fresh which breaks UX expectations.

**Independent Test**: Can be tested by sending messages, refreshing page, and verifying messages are still visible. Delivers value by maintaining conversation context.

**Acceptance Scenarios**:

1. **Given** user has previous chat messages, **When** user opens chat page, **Then** last 50 messages load and display in chronological order.

2. **Given** messages are loaded, **When** page renders, **Then** chat auto-scrolls to the most recent message.

3. **Given** user scrolls up to read history, **When** new message arrives, **Then** chat does NOT auto-scroll (preserves user position).

---

### User Story 3 - Dark/Light Mode Chat UI (Priority: P2)

As a user, I want the chat interface to match my theme preference (dark/light mode) so that the experience is consistent with the rest of the Phase II app.

**Why this priority**: Visual consistency is critical for professional feel. Lumina theme integration is mandatory per Phase II design system.

**Independent Test**: Can be tested by toggling theme and verifying all chat elements use correct Lumina color values for each mode.

**Acceptance Scenarios**:

1. **Given** user is in dark mode, **When** chat renders, **Then** user messages use gradient `#ce93d8 → #e1bee7`, AI messages use `rgba(255,255,255,0.05)` with backdrop blur.

2. **Given** user is in light mode, **When** chat renders, **Then** user messages use gradient `#5e35b1 → #4a148c`, AI messages use white background with `#d1c4e9` border.

3. **Given** user toggles theme, **When** mode changes, **Then** all chat elements transition smoothly to new theme colors.

---

### User Story 4 - Mobile Responsive Chat (Priority: P3)

As a mobile user, I want to use the chat interface on my phone so that I can manage tasks on the go.

**Why this priority**: Mobile is important but not blocking - desktop experience comes first. Many users will use mobile secondarily.

**Independent Test**: Can be tested on mobile viewport (375px width) by sending messages and verifying full functionality and proper layout.

**Acceptance Scenarios**:

1. **Given** user opens chat on mobile device, **When** page renders, **Then** chat takes full viewport height, input is sticky at bottom, messages are readable.

2. **Given** user is on mobile, **When** typing in input field, **Then** keyboard appears and input remains visible above keyboard.

3. **Given** user is on mobile, **When** scrolling messages, **Then** touch scrolling is smooth with momentum.

---

### User Story 5 - Empty State with Suggested Prompts (Priority: P3)

As a new user, I want to see helpful suggestions when I first open chat so that I know what I can ask the AI.

**Why this priority**: Onboarding improves discoverability but is not blocking for core functionality.

**Independent Test**: Can be tested by opening chat as new user (no history) and verifying welcome message and clickable suggestions appear.

**Acceptance Scenarios**:

1. **Given** user has no chat history, **When** chat page loads, **Then** welcome message displays with AI avatar and 3 suggested prompts.

2. **Given** suggested prompts are visible, **When** user clicks "Add task...", **Then** text is inserted into input field ready for completion.

3. **Given** user sends first message, **When** response arrives, **Then** empty state disappears and normal message list displays.

---

### User Story 6 - Markdown Rendering in AI Responses (Priority: P3)

As a user, I want AI responses to display formatted text (bold, lists, code) so that task lists and information are easy to read.

**Why this priority**: Enhances readability significantly but plain text is functional. Nice-to-have polish.

**Independent Test**: Can be tested by asking AI to "list my tasks" and verifying response renders with proper bullet points and formatting.

**Acceptance Scenarios**:

1. **Given** AI responds with markdown list, **When** message renders, **Then** bullet points display as proper list with correct indentation.

2. **Given** AI responds with **bold** text, **When** message renders, **Then** bold text displays with correct font weight.

3. **Given** AI responds with `code`, **When** message renders, **Then** code displays in monospace font with background highlight.

---

### Edge Cases

- **Empty message**: Input validation prevents sending empty/whitespace-only messages
- **Very long message**: Character limit of 500 chars with counter, truncation warning
- **Rapid messages**: Debounce prevents duplicate sends, disable send button while processing
- **Session timeout**: If backend returns 401, redirect to login page
- **AI timeout**: If no response in 30 seconds, show timeout error with retry option
- **Network offline**: Detect offline state, show banner, queue message for retry
- **100+ messages**: Virtualized list prevents performance degradation

## Requirements

### Functional Requirements

#### Core Chat
- **FR-001**: System MUST display a chat interface accessible from the Phase II todo app via floating widget button
- **FR-002**: System MUST allow users to send text messages via input field
- **FR-003**: System MUST forward messages to Part 2 OpenRouter agent via Phase II backend proxy (`/api/chat`)
- **FR-004**: System MUST display AI responses in chat message bubbles
- **FR-005**: System MUST show typing/loading indicator while AI is processing
- **FR-006**: System MUST auto-refresh task list when task-related tools are executed (add_task, update_task, delete_task, complete_task)

#### Message Display
- **FR-010**: User messages MUST be right-aligned with Lumina user gradient colors
- **FR-011**: AI messages MUST be left-aligned with Lumina AI bubble colors
- **FR-012**: Messages MUST display relative timestamps ("Just now", "2m ago")
- **FR-013**: AI messages MUST render markdown (bold, lists, code blocks)
- **FR-014**: Consecutive messages from same sender MUST be grouped visually

#### History & Persistence
- **FR-020**: System MUST load conversation history on page mount (last 50 messages)
- **FR-021**: System MUST auto-scroll to latest message on load
- **FR-022**: System MUST preserve scroll position when user scrolls up manually
- **FR-023**: System MUST persist messages via backend API (database storage)

#### Input
- **FR-030**: Input field MUST auto-resize up to 4 lines
- **FR-031**: Enter key MUST send message, Shift+Enter MUST insert newline
- **FR-032**: System MUST validate message is non-empty before sending
- **FR-033**: Send button MUST be disabled while message is sending

#### Error Handling
- **FR-040**: System MUST display error banner on network failure with retry button
- **FR-041**: System MUST redirect to login on 401 authentication error
- **FR-042**: System MUST show error state on message bubble if send fails
- **FR-043**: System MUST allow retry of failed messages

#### Theme Integration
- **FR-050**: System MUST use exact Lumina Deep Purple Royal colors (see design spec)
- **FR-051**: System MUST support dark mode and light mode per Phase II theme toggle
- **FR-052**: System MUST apply glassmorphism effects per Lumina spec

### Key Entities

- **Message**: Represents a single chat message with id, role (user/assistant), content, timestamp, status
- **Conversation**: Represents a chat session with id, user_id, messages array, created/updated timestamps
- **ChatResponse**: API response containing user_message, ai_message, and thread_id

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can send a message and receive AI response in under 5 seconds (95th percentile)
- **SC-002**: Chat history loads in under 1 second for 50 messages
- **SC-003**: Chat UI renders correctly on viewports from 320px to 2560px width
- **SC-004**: All color values match Lumina spec exactly (verified by visual regression test)
- **SC-005**: Keyboard users can complete full chat flow without mouse
- **SC-006**: Screen readers can announce new messages as they arrive
- **SC-007**: Test coverage exceeds 80% for chat components
- **SC-008**: No console errors during normal chat operation

## Assumptions

- Phase II authentication (JWT) is functional and provides user context
- Part 2 OpenRouter agent is running and accessible at configured URL
- Phase II Tailwind CSS configuration includes Lumina color palette
- Users have modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Backend proxy endpoint will be created as part of this feature

## Out of Scope

- Voice input/output
- File attachments
- Group chats (single user only)
- Message editing after send
- Message deletion
- Rich text editor (plain text input only)
- Emoji picker (paste supported)
- WebSocket real-time (polling is sufficient for v1)
- Direct OpenRouter API calls from frontend (must proxy through backend)

## Design System Reference

### Lumina Deep Purple Royal - Chat Colors

#### Dark Mode
| Element | Value |
|---------|-------|
| User Message BG | `linear-gradient(135deg, #ce93d8 0%, #e1bee7 100%)` |
| User Message Text | `#1a0033` |
| AI Message BG | `rgba(255, 255, 255, 0.05)` with `backdrop-filter: blur(10px)` |
| AI Message Text | `#f3e5f5` |
| Input BG | `rgba(255, 255, 255, 0.05)` |
| Input Border | `rgba(126, 87, 194, 0.3)` |
| Input Focus | `#b39ddb` ring |
| Send Button | `linear-gradient(135deg, #ce93d8 0%, #e1bee7 100%)` |
| Typing Indicator | `#ce93d8` |

#### Light Mode
| Element | Value |
|---------|-------|
| User Message BG | `linear-gradient(135deg, #5e35b1 0%, #4a148c 100%)` |
| User Message Text | `#FFFFFF` |
| AI Message BG | `#FFFFFF` with `border: rgba(209, 196, 233, 0.5)` |
| AI Message Text | `#1a0033` |
| Input BG | `rgba(255, 255, 255, 0.8)` |
| Input Border | `rgba(179, 157, 219, 0.5)` |
| Input Focus | `#7e57c2` ring |
| Send Button | `linear-gradient(135deg, #5e35b1 0%, #4a148c 100%)` |
| Typing Indicator | `#5e35b1` |
