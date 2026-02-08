# Quickstart: ChatKit UI

**Feature**: 007-chatkit-ui
**Date**: 2026-02-08

## Prerequisites

Before testing ChatKit UI, ensure:

1. **Part 2 OpenRouter Agent is running** (port 8001)
   ```bash
   cd chatbot
   uv run uvicorn mcp_server.main:app --port 8001 --reload
   ```

2. **Frontend is running** (port 3000)
   ```bash
   cd frontend
   npm run dev
   ```

3. **User is authenticated** (login via Phase II)

---

## Test Scenarios

### Scenario 1: Send First Message

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Observe empty state with welcome message and suggested prompts
3. Type "Hello" in the input field
4. Press Enter or click Send button

**Expected**:
- User message appears immediately (right-aligned, purple gradient)
- Typing indicator shows "AI is typing..."
- AI response appears within 5 seconds (left-aligned, glass effect)
- Both messages have timestamps

---

### Scenario 2: Add Task via Chat

**Steps**:
1. Type: "Add a task to buy groceries"
2. Send message

**Expected**:
- AI responds with confirmation: "I've added 'buy groceries' to your tasks"
- May show tool_calls info in response

**Verification**:
```bash
# Check task was created
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "list_tasks",
    "parameters": {
      "user_id": "YOUR_USER_ID"
    }
  }'
```

---

### Scenario 3: List Tasks via Chat

**Steps**:
1. Type: "Show my tasks"
2. Send message

**Expected**:
- AI responds with formatted list of tasks
- Markdown rendering shows bullet points or numbered list
- Task titles are visible

---

### Scenario 4: Multi-Turn Conversation

**Steps**:
1. Type: "Add task: call mom"
2. Wait for response
3. Type: "What tasks do I have?"
4. Wait for response
5. Type: "Complete the first one"
6. Wait for response

**Expected**:
- Each message gets response
- Context maintained across turns
- AI correctly references previous tasks

---

### Scenario 5: Dark/Light Mode Toggle

**Steps**:
1. Ensure chat has messages
2. Click theme toggle in header
3. Observe color changes

**Expected (Dark Mode)**:
- User messages: Purple gradient (#ce93d8 → #e1bee7)
- AI messages: Glass effect (white/5% + blur)
- Background: Deep purple gradient
- Input: Glass effect with purple border

**Expected (Light Mode)**:
- User messages: Deep purple gradient (#5e35b1 → #4a148c)
- AI messages: White with light purple border
- Background: Light purple gradient
- Input: White with light purple border

---

### Scenario 6: Error Recovery

**Steps**:
1. Stop Part 2 agent (Ctrl+C)
2. Try sending a message
3. Observe error state
4. Restart Part 2 agent
5. Click retry button

**Expected**:
- Error message displays when agent unavailable
- Retry button visible
- After restart, retry works and gets response

---

### Scenario 7: Mobile Responsiveness

**Steps**:
1. Open browser DevTools
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select iPhone 12 Pro (390px width)
4. Navigate to /chat
5. Send a message

**Expected**:
- Chat takes full viewport height
- Input stays at bottom
- Messages are readable
- Touch scrolling works
- Keyboard doesn't obscure input

---

### Scenario 8: Keyboard Navigation

**Steps**:
1. Focus on input field
2. Type a message
3. Press Shift+Enter (should add newline)
4. Press Enter (should send)
5. Tab through interface

**Expected**:
- Shift+Enter inserts newline, doesn't send
- Enter sends message
- Tab focuses on interactive elements
- Focus visible on all elements

---

### Scenario 9: Empty State Prompts

**Steps**:
1. Open chat with no history (new user or cleared)
2. Click "Add task..." suggestion

**Expected**:
- Text "Add task: " inserted into input
- Cursor placed after text
- Ready for user to complete

---

### Scenario 10: Page Refresh Persistence

**Steps**:
1. Send a few messages
2. Refresh page (F5)
3. Observe loaded messages

**Expected**:
- Previous messages load from history
- Chat scrolls to bottom
- Conversation continues seamlessly

---

## API Verification Commands

### Health Check
```bash
curl http://localhost:8001/health
# Should include: "agent_status": "ready"
```

### Send Message (Direct API)
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### Get Conversation History
```bash
curl "http://localhost:8001/conversations?user_id=550e8400-e29b-41d4-a716-446655440000"
```

### Get Messages
```bash
curl "http://localhost:8001/conversations/{CONVERSATION_ID}/messages?user_id=550e8400-e29b-41d4-a716-446655440000"
```

---

## Troubleshooting

### "Agent unavailable" error
- Ensure Part 2 agent is running on port 8001
- Check OPENROUTER_API_KEY is set in chatbot/.env

### CORS errors
- Verify Part 2 CORS includes `http://localhost:3000`
- Check browser console for specific origin issues

### Messages not loading
- Check conversation_id is being passed correctly
- Verify user_id matches authenticated user

### Theme colors wrong
- Clear browser cache
- Verify Tailwind config includes Lumina colors
- Check dark mode class on html element

---

## Demo Checklist

For the 90-second demo video:

- [ ] Open chat from Phase II app (5s)
- [ ] Show dark mode chat UI (5s)
- [ ] Type: "Add task to buy groceries" (5s)
- [ ] AI responds with confirmation (5s)
- [ ] Type: "Show my tasks" (5s)
- [ ] AI lists tasks (10s)
- [ ] Type: "Complete task 1" (5s)
- [ ] AI confirms completion (5s)
- [ ] Show typing indicator (5s)
- [ ] Show error handling (10s)
- [ ] Toggle to light mode (10s)
- [ ] Mobile view demo (10s)
- [ ] Glassmorphism showcase (10s)
- [ ] Code structure glimpse (5s)
