---
name: "chatkit_ui"
description: "Build production-ready chat interfaces with modern UX patterns and real-time messaging"
version: "1.0.0"
---

# ChatKit UI Skill

## When to Use
- Creating chat interfaces
- Building conversation UIs
- Integrating real-time messaging
- Implementing chat UX patterns

## Process Steps

### 1. Component Design
- ChatContainer
- MessageList
- MessageBubble
- MessageInput
- TypingIndicator
- ErrorBoundary
- EmptyState

### 2. API Integration Layer
```typescript
interface ChatAPI {
  sendMessage(text: string, userId: string): Promise<ChatResponse>;
  getHistory(userId: string): Promise<Message[]>;
  getThread(threadId: string): Promise<Thread>;
}
```

### 3. State Management
```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
```

### 4. Real-Time Updates
- Poll every 2 seconds when active
- Optimistic UI updates
- Message deduplication
- Error recovery

### 5. UX Polish
- Auto-scroll
- Message grouping
- Time separators
- Animations
- Loading skeletons

## Output Format
- `/components/Chat/` directory
- API integration files
- TypeScript types
- Tailwind CSS
- Unit tests (React Testing Library)

## Quality Criteria
- Responsive
- Accessible
- Fast
- Error-resilient
- Polished UI

## Component Structure
```
frontend/src/components/Chat/
├── ChatContainer.tsx
├── MessageList.tsx
├── MessageBubble.tsx
├── MessageInput.tsx
├── TypingIndicator.tsx
├── EmptyState.tsx
└── index.ts
```

## Example Component: MessageBubble
```tsx
export function MessageBubble({ message, isUser }: MessageBubbleProps) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`rounded-lg p-3 max-w-[80%] ${
        isUser ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-900"
      }`}>
        <Markdown>{message.content}</Markdown>
        <span className="text-xs opacity-70">
          {formatTime(message.created_at)}
        </span>
      </div>
    </div>
  );
}
```

## API Example
```typescript
export async function sendChatMessage(message: string): Promise<ChatResponse> {
  return api.post("/api/chat", { message }).then(r => r.data);
}
```

## Testing Pattern
```tsx
it("renders user message correctly", () => {
  render(<MessageBubble message={{ content: "Hello" }} isUser />);
  expect(screen.getByText("Hello")).toBeInTheDocument();
});
```

## Integration with Part 2 Agent

### Backend Endpoints
- `POST /chat` - Send message, get AI response
- `GET /conversations` - List user conversations
- `GET /conversations/{id}/messages` - Get conversation history

### Request/Response Types
```typescript
interface ChatRequest {
  message: string;
  user_id: string;
  conversation_id?: string;
}

interface ChatResponse {
  message: string;
  conversation_id: string;
  tool_calls?: ToolCallSummary[];
}

interface ToolCallSummary {
  tool: string;
  success: boolean;
  summary: string;
}
```

## UX State Machine
```
IDLE -> SENDING -> WAITING_FOR_AI -> RECEIVED -> IDLE
                                  \-> ERROR -> IDLE (retry)
```

## Accessibility Requirements
- Keyboard navigation (Tab, Enter to send)
- Screen reader announcements for new messages
- Focus management after send
- ARIA labels on interactive elements
- High contrast mode support
