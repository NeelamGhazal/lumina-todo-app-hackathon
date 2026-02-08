---
id: 003
title: OpenAI Agent Implementation Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-opus-4-5-20251101
feature: 006-openai-agent-mcp
branch: 006-openai-agent-mcp
user: neela
command: /sp.plan
labels: ["openai-agent", "implementation-plan", "phase3-part2", "openrouter"]
links:
  spec: specs/006-openai-agent-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-openai-agent-mcp/plan.md
  - specs/006-openai-agent-mcp/research.md
  - specs/006-openai-agent-mcp/data-model.md
  - specs/006-openai-agent-mcp/quickstart.md
  - specs/006-openai-agent-mcp/contracts/agent-api.yaml
tests:
  - null
---

## Prompt

/sp.plan

Generate implementation plan for OpenAI Agent Setup (Phase III - Part 2) using OpenRouter API instead of direct OpenAI.

Planning requirements included:
- ADR-005: OpenAI Tool Calling Pattern (Manual execution)
- ADR-006: Thread Management Strategy (Database-only context)
- ADR-007: MCP Tool Schema Sync (Startup fetch)
- ADR-008: Intent Extraction (LLM-based)

Implementation phases: 2A (Client Setup), 2B (Tool Integration), 2C (Conversation Management), 2D (Testing)

## Response snapshot

Created comprehensive implementation plan for Phase III Part 2 with:

**Phase 0 Output (research.md):**
- R1: OpenRouter API compatibility with OpenAI SDK
- R2: Chat Completions API (not Assistants) for OpenRouter
- R3: MCP tool to OpenAI function conversion
- R4: Manual tool execution pattern
- R5: Agent instructions design
- R6: Message history context window (10 messages)
- R7: Conversation session management (30-min timeout)
- R8: Error handling strategy (immediate, no retry)
- R9: OpenRouter model selection (gpt-4o-mini default)

**Phase 1 Output:**
- data-model.md: Runtime data structures (ChatRequest, ChatResponse, etc.)
- contracts/agent-api.yaml: OpenAPI spec for /chat, /conversations endpoints
- quickstart.md: Setup and usage guide

**ADRs Documented:**
- ADR-005: Manual Tool Execution Pattern
- ADR-006: Database-Only Context Storage
- ADR-007: Startup Tool Schema Loading
- ADR-008: LLM-Based Intent Extraction
- ADR-009: Immediate Error Response (No Retry)

**Implementation Phases:**
- Phase 2A: OpenRouter Client Setup (45-60 mins)
- Phase 2B: MCP Tool Integration (1-1.5 hours)
- Phase 2C: Conversation Management (1-1.5 hours)
- Phase 2D: Response Formatting & Testing (1.5-2 hours)

**Component Architecture:**
- chatbot/agent/config.py - Configuration
- chatbot/agent/client.py - OpenRouter wrapper
- chatbot/agent/tools.py - MCP integration
- chatbot/agent/conversation.py - Session management
- chatbot/agent/chat.py - Orchestration
- chatbot/agent/schemas.py - Pydantic models

## Outcome

- Impact: Complete implementation plan with 4 phases, 5 ADRs, and detailed component architecture
- Tests: Testing strategy defined (80%+ coverage target)
- Files: 5 files created (plan, research, data-model, quickstart, contracts)
- Next prompts: /sp.tasks
- Reflection: Plan aligns with clarifications (manual execution, DB context, 10 messages, startup loading, no retry)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASSED all gates
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
