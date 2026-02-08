---
id: 001
title: OpenAI Agent with MCP Integration Specification
stage: spec
date: 2026-02-08
surface: agent
model: claude-opus-4-5-20251101
feature: 006-openai-agent-mcp
branch: 006-openai-agent-mcp
user: neela
command: /sp.specify
labels: ["openai-agent", "mcp-integration", "phase3-part2", "specification"]
links:
  spec: specs/006-openai-agent-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-openai-agent-mcp/spec.md
  - specs/006-openai-agent-mcp/checklists/requirements.md
  - .claude/agents/openai_agent_builder.md
  - .claude/skills/openai_agents_sdk/openai_agents_sdk.md
tests:
  - null
---

## Prompt

/sp.specify

Project: Phase III - Part 2: OpenAI Agent with MCP Integration

## CONTEXT
Building conversational AI agent using OpenAI Agents SDK that uses MCP tools (from Part 1) to manage todo tasks through natural language.

LLM PROVIDER CLARIFICATION (COST CONSTRAINT)
- The project MUST use the official OpenAI Python SDK
- However, API requests MUST be routed via OpenRouter
- OpenRouter provides an OpenAI-compatible API surface
- Direct usage of OpenAI's paid API is NOT allowed due to cost constraints

### LLM Configuration Requirements
- API Base URL: `https://openrouter.ai/api/v1`
- API Key: `OPENROUTER_API_KEY` (environment variable)
- No dependency on `OPENAI_API_KEY`
- All agent and tool calls must function via OpenRouter

## Response snapshot

Created comprehensive feature specification for Phase III Part 2: OpenAI Agent with MCP Integration.

**Key Deliverables:**
- Feature branch: `006-openai-agent-mcp`
- Specification: `specs/006-openai-agent-mcp/spec.md`
- Quality checklist: `specs/006-openai-agent-mcp/checklists/requirements.md`

**Specification Contents:**
- 6 user stories (P1: add task, list tasks; P2: complete, delete; P3: update, multi-turn)
- 18 acceptance scenarios
- 5 edge cases identified
- 25 functional requirements across 5 categories (Agent Config, NLU, MCP Integration, Response Generation, Conversation Management)
- 8 measurable success criteria
- Clear dependencies on Part 1 MCP server and OpenRouter

**Key Design Decisions:**
- OpenRouter for LLM routing (cost constraint)
- OpenAI Python SDK with custom base_url
- 30-minute conversation timeout for session management
- User isolation via user_id in all tool calls

## Outcome

- Impact: Created complete specification for conversational AI agent with MCP tool integration
- Tests: N/A (specification phase)
- Files: 4 files created (spec, checklist, agent definition, skill definition)
- Next prompts: /sp.clarify or /sp.plan
- Reflection: Spec is comprehensive with clear boundaries between Part 1 (MCP server), Part 2 (agent), and Part 3 (UI)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Quality checklist PASSED all items
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
