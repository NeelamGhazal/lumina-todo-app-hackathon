<!--
  Sync Impact Report
  ==================
  Version change: 0.0.0 → 1.0.0 (Initial)

  Added Principles:
  - I. Spec-Driven Development
  - II. Professional Quality
  - III. Visual Excellence
  - IV. Task-Driven Implementation
  - V. Checkpoint Control
  - VI. AI-First Engineering
  - VII. Cloud-Native Mindset

  Added Sections:
  - Technology Stack Constraints
  - Phase-Specific Standards (I-V)
  - Task Execution Rules
  - Checkpoint Protocol
  - Security Standards
  - Documentation Standards
  - Quality Gates
  - Failure Prevention & Recovery

  Templates Status:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md: ✅ Compatible (user stories and acceptance criteria align)
  - .specify/templates/tasks-template.md: ✅ Compatible (checkpoint structure aligns)
  - .specify/templates/phr-template.prompt.md: ✅ Compatible (no changes needed)

  Deferred TODOs: None
-->

# Evolution of Todo - Complete Hackathon II Constitution

## Core Principles

### I. Spec-Driven Development

**STRICT RULE**: No manual coding. Only Claude Code generates implementation.

- Every feature MUST follow the workflow: specification → plan → tasks → implement
- NO shortcuts: specifications must be complete before any code generation
- Iterate specifications until Claude produces correct output (NOT iterate code)
- If implementation is wrong, fix the spec/tasks, not the code directly
- All features MUST have clear, testable acceptance criteria before implementation

**Rationale**: Spec-driven development ensures reproducibility, traceability, and quality. When AI generates code from specifications, the process is auditable and repeatable.

### II. Professional Quality

Enterprise-grade code from Phase I onwards. This is NOT a toy project.

- All Python code: Type hints MANDATORY, Pydantic models for validation, async where beneficial
- All TypeScript code: Strict mode, proper interfaces, NO 'any' types
- Error handling: Comprehensive, user-friendly messages, graceful failures
- Testing: Unit tests for business logic, integration tests for APIs
- Documentation: README.md, CLAUDE.md, AGENTS.md, inline docstrings
- API responses MUST be under 200ms
- Chatbot responses MUST be under 2s

**Rationale**: Professional quality differentiates hackathon winners from participants. Judges evaluate code quality, architecture, and polish.

### III. Visual Excellence

Even CLI applications MUST be visually impressive with rich formatting, colors, and professional UX.

- **Phase I CLI Requirements** (rich library MANDATORY):
  - Menu-driven interface + command parser for power users
  - Color-coded priorities (red=high, yellow=medium, green=low, blue=info)
  - Beautiful tables with borders and formatting
  - Progress indicators, animated spinners for loading states
  - Interactive prompts with validation
  - Panel-based layouts, status badges, and icons
  - Professional welcome banner, help system with formatted output

- **Phase II+ Web Requirements**:
  - Modern, responsive, accessible, delightful UX
  - Loading states, skeleton screens, optimistic UI updates
  - Toast notifications, dark mode support
  - Accessibility (ARIA labels, keyboard navigation)

**Rationale**: Visual polish creates first impressions. Professional interfaces demonstrate attention to detail and user experience thinking.

### IV. Task-Driven Implementation

Claude MUST follow tasks.md exactly. No freestyle coding allowed.

- Claude MUST read tasks.md before implementing
- Claude MUST follow task sequence (Task 1.1 → 1.2 → 1.3...)
- Claude CANNOT skip tasks or combine tasks without approval
- Claude MUST complete ONE task at a time
- Claude MUST reference task IDs in generated code comments
- Claude MUST validate output against acceptance criteria
- Claude MUST ask for clarification if any task is ambiguous
- Claude CANNOT invent features not explicitly defined in specifications

**Rationale**: Task-driven implementation prevents scope creep, ensures traceability, and allows precise progress tracking and debugging.

### V. Checkpoint Control

Human reviews and approves each phase before proceeding.

**Checkpoint Protocol**:
1. Claude completes Phase X tasks
2. Claude reports: "Phase X complete: [list outputs]"
3. Human reviews all outputs against specifications
4. Human validates acceptance criteria are met
5. If PASS: Human says "Approved, proceed to Phase Y"
6. If FAIL: Human identifies gap, Claude iterates on THAT specific task only
7. Git commit ONLY after checkpoint approval
8. NEVER proceed autonomously past checkpoints

**Rationale**: Human-in-the-loop ensures quality gates are enforced and prevents cascading errors from undetected issues.

### VI. AI-First Engineering

Use AI agents (Claude Code, OpenAI Agents SDK, MCP) as primary developers.

- Claude Code generates ALL code - zero manual typing by developer
- OpenAI Agents SDK for backend chatbot logic
- Official MCP SDK for tool exposure
- Use AI DevOps tools: kubectl-ai, kagent, Gordon (Docker AI)
- Conversation history persistence for multi-turn context
- Tool call transparency (show what agent did)

**Rationale**: AI-first engineering maximizes productivity and demonstrates mastery of modern AI-assisted development workflows.

### VII. Cloud-Native Mindset

Design for scalability, containerization, and distributed systems from Day 1.

- Multi-stage Docker builds for optimization
- Health checks (liveness/readiness) for all services
- Resource limits and requests defined
- Helm charts with proper templating
- Event-driven architecture via Kafka (Phase V)
- Dapr sidecars for microservices communication
- Horizontal Pod Autoscaler configurations
- Distributed tracing, metrics collection (Prometheus compatible)
- 99.9% uptime target (Phase V)

**Rationale**: Cloud-native architecture ensures the application can scale and demonstrates production-ready engineering practices.

## Technology Stack Constraints

All downstream work MUST use these technologies:

| Layer | Technology |
|-------|------------|
| Backend | Python 3.13+, FastAPI, SQLModel, UV, Pydantic, rich (CLI) |
| Frontend | Next.js 16+, TypeScript, Tailwind, Shadcn/ui, Zod |
| Database | Neon Serverless PostgreSQL |
| Auth | Better Auth with JWT |
| AI Backend | OpenAI Agents SDK, Official MCP SDK |
| Chat UI | OpenAI ChatKit |
| Containers | Docker (multi-stage builds) |
| Orchestration | Kubernetes (Minikube → Cloud) |
| Packages | Helm Charts |
| Event Streaming | Kafka (Strimzi/Redpanda) |
| Runtime | Dapr for microservices |
| DevOps AI | kubectl-ai, kagent, Gordon |
| Spec Workflow | Spec-Kit Plus, Claude Code |
| Platform | WSL 2 required (Windows) |

## Phase-Specific Standards

### Phase I: Console Application

- rich library MANDATORY for professional CLI
- Menu-driven interface + command parser
- Color-coded priorities: red=high, yellow=medium, green=low, blue=info
- Beautiful tables, progress indicators, animated spinners
- Interactive prompts with validation
- Panel-based layouts, status badges (check, cross, clock, star icons)
- Professional welcome banner and formatted help system

### Phase II: Full-Stack Web Application

- Next.js 16+ App Router with server components default
- Shadcn/ui components for consistent design system
- Tailwind CSS for styling (no inline styles)
- Loading states, skeleton screens, optimistic UI updates
- Form validation with Zod
- Toast notifications, responsive design (mobile-first)
- Dark mode support, accessibility compliance
- Better Auth JWT tokens for stateless authentication
- Environment variables for ALL secrets

### Phase III: AI Chatbot Integration

- Natural language understanding for ALL operations
- OpenAI ChatKit for frontend
- OpenAI Agents SDK for backend logic
- Official MCP SDK for tool exposure
- Stateless architecture (all state in database)
- Conversation history persistence
- Multi-turn context awareness
- Friendly, helpful agent personality
- Streaming responses, Markdown rendering, code syntax highlighting

### Phase IV: Local Kubernetes Deployment

- Multi-stage Docker builds
- Health checks (liveness/readiness) for all services
- Resource limits and requests defined
- Helm charts with proper templating
- ConfigMaps for configuration, Secrets for sensitive data
- Service mesh ready architecture
- Horizontal Pod Autoscaler configurations
- Proper labeling and annotations

### Phase V: Cloud Deployment with Event Streaming

- Event-driven architecture via Kafka
- Dapr sidecars for all services
- Pub/Sub for async operations
- Circuit breakers and retries
- Distributed tracing enabled
- CI/CD with GitHub Actions
- Blue-green deployment strategy
- Auto-scaling policies
- Monitoring dashboards

## Task Execution Rules

These rules are NON-NEGOTIABLE:

1. Claude MUST read tasks.md before ANY implementation
2. Claude MUST follow task sequence exactly
3. Claude CANNOT skip or combine tasks without explicit approval
4. Claude MUST complete ONE task at a time
5. Claude MUST stop at checkpoints for human review
6. Claude CANNOT invent features not in specifications
7. Claude MUST reference task IDs in code comments
8. Claude MUST validate output against acceptance criteria
9. Claude MUST ask for clarification on ambiguous tasks
10. Human MUST approve each checkpoint before proceeding

## Security Standards

- NO hardcoded secrets (use environment variables)
- JWT tokens expire (7 days default)
- HTTPS in production
- Input validation on ALL endpoints
- SQL injection prevention (ORM only)
- XSS protection
- CORS whitelist only
- Secrets encrypted (K8s Secrets/Dapr)
- Rate limiting (Phase V)
- Security headers and Content Security Policy

## Documentation Standards

- **README.md**: Badges, quick start, features, architecture, deployment, contributing
- **CLAUDE.md**: Project context, spec usage instructions, command reference
- **AGENTS.md**: Agent rules, workflow, failure modes
- **API docs**: OpenAPI/Swagger with examples
- **Database schema**: ER diagrams with relationships
- **Architecture diagrams**: ASCII art or Mermaid
- **Deployment runbooks**: Step-by-step for each phase

## Quality Gates

Each phase MUST pass ALL gates before approval:

- [ ] Specification complete and clarified
- [ ] Plan generated with ADRs where applicable
- [ ] Tasks atomic (15-30 min each)
- [ ] Implementation matches tasks exactly
- [ ] All acceptance criteria met
- [ ] Tests passing
- [ ] Documentation updated
- [ ] No linting errors
- [ ] Git committed with conventional commits
- [ ] Demo video created (final phases)

## Failure Prevention Rules

STOP immediately if any of these occur:

- Claude starts coding before tasks.md exists
- Claude skips a task
- Claude invents features not in specification
- Checkpoint fails validation
- "Vibe coding" detected (unstructured implementation)

**Recovery Protocol**:
1. Don't panic
2. Check: Are specs clear? Are tasks atomic?
3. Review: Did Claude follow tasks.md?
4. Fix: Update spec/tasks, NOT code directly
5. Restart: From last successful checkpoint
6. Document: What went wrong in ADRs

## Git Standards

- Conventional commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`
- Commit after each checkpoint approval
- Feature branches for each phase
- Constitution committed first
- Specs committed before implementation
- .gitignore: secrets, node_modules, __pycache__, .env, venv/

## Success Criteria

- All specs exist in /specs with clear acceptance criteria
- Constitution file at root (this file)
- AGENTS.md with agent behavior rules
- CLAUDE.md with Claude Code instructions
- README.md comprehensive
- All 5 basic features working in each phase
- Zero manual coding (verified in commits)
- All tests passing
- No security vulnerabilities
- API responses < 200ms
- Chatbot responses < 2s
- 99.9% uptime (Phase V)

## Governance

- This constitution supersedes all other practices
- Amendments require: documentation, approval, migration plan
- All PRs/reviews MUST verify compliance with these principles
- Complexity MUST be justified and documented
- See CLAUDE.md for runtime development guidance

**Version**: 1.0.0 | **Ratified**: 2026-01-26 | **Last Amended**: 2026-01-26
