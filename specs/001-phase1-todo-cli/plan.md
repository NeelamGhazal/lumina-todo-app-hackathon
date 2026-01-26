# Implementation Plan: Phase I - Professional Todo Console Application

**Branch**: `001-phase1-todo-cli` | **Date**: 2026-01-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase1-todo-cli/spec.md`

## Summary

Build an enterprise-grade command-line Todo application in Python using the `rich` library for professional visual output. The application supports task CRUD operations with two input modes (interactive wizard and natural language), beautiful table displays with color-coded priorities, and comprehensive statistics. All data is stored in-memory (Phase I scope).

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: rich (CLI rendering), pydantic (data validation), python-dateutil (date parsing)
**Package Manager**: UV
**Storage**: In-memory (dict-based, resets on exit)
**Testing**: pytest
**Target Platform**: Cross-platform CLI (Linux/macOS/Windows with ANSI support)
**Project Type**: Single project (backend-only for Phase I)
**Performance Goals**: All operations < 1 second, startup < 2 seconds
**Constraints**: In-memory only, no persistence, single-user session
**Scale/Scope**: Support 1000+ tasks in memory without degradation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | ✅ PASS | Spec complete with 25 FRs, 9 user stories, clarifications resolved |
| II. Professional Quality | ✅ PASS | Type hints mandatory, Pydantic models, pytest testing defined |
| III. Visual Excellence | ✅ PASS | rich library mandatory, color scheme defined, panel/table requirements |
| IV. Task-Driven Implementation | ✅ PASS | Plan leads to tasks.md, checkpoint protocol defined |
| V. Checkpoint Control | ✅ PASS | 4 checkpoints defined in this plan |
| VI. AI-First Engineering | ✅ PASS | Claude Code generates all implementation |
| VII. Cloud-Native Mindset | ⚪ N/A | Phase I is CLI-only, cloud-native applies Phase IV+ |

**Gate Result**: ✅ PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-phase1-todo-cli/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output (ADRs, tech decisions)
├── data-model.md        # Phase 1 output (Pydantic models)
├── quickstart.md        # Phase 1 output (setup & usage guide)
├── contracts/           # Phase 1 output (CLI command specs)
│   └── commands.md      # Command interface definitions
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml       # UV project configuration
├── src/
│   ├── __init__.py
│   ├── main.py          # Application entry point, main loop
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py      # Pydantic Task model
│   ├── storage/
│   │   ├── __init__.py
│   │   └── memory.py    # In-memory storage layer
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── base.py      # Base command interface
│   │   ├── add.py       # /add (wizard + NLP)
│   │   ├── list.py      # /list
│   │   ├── show.py      # /show <id>
│   │   ├── update.py    # /update <id>
│   │   ├── complete.py  # /complete <id>
│   │   ├── delete.py    # /delete <id>
│   │   ├── search.py    # /search <query>
│   │   ├── stats.py     # /stats
│   │   ├── help.py      # /help
│   │   └── exit.py      # /exit
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── console.py   # Rich Console singleton
│   │   ├── theme.py     # Colors, styles, icons
│   │   ├── tables.py    # Task table renderer
│   │   ├── panels.py    # Detail panels, empty states
│   │   ├── prompts.py   # Interactive input prompts
│   │   └── banner.py    # Welcome banner
│   └── parsers/
│       ├── __init__.py
│       ├── commands.py  # Command parser (slash-based)
│       └── nlp.py       # Natural language parser
└── tests/
    ├── __init__.py
    ├── conftest.py      # Pytest fixtures
    ├── unit/
    │   ├── __init__.py
    │   ├── test_models.py
    │   ├── test_storage.py
    │   ├── test_parsers.py
    │   └── test_commands.py
    └── integration/
        ├── __init__.py
        └── test_cli_flows.py
```

**Structure Decision**: Backend-only structure with clear separation of concerns:
- `models/` - Data validation (Pydantic)
- `storage/` - Data access layer (in-memory)
- `commands/` - Business logic per command
- `ui/` - Rich rendering components
- `parsers/` - Input processing

---

## Architecture Decision Records (ADRs)

### ADR-001: Task ID Generation Strategy

**Status**: Accepted

**Context**: Tasks need unique identifiers that are easy for users to type in commands.

**Decision**: Use 6-character lowercase alphanumeric IDs (e.g., "a1b2c3")

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Sequential int (1, 2, 3) | Simple, predictable | Reveals task count, collisions on reset |
| UUID | Globally unique | 36 chars, impossible to type |
| **6-char alphanumeric** | Typeable, 2.1B combinations | Requires collision check |
| Nanoid | Industry standard | External dependency |

**Rationale**: 6 characters provides 36^6 = 2,176,782,336 combinations - more than sufficient for in-memory usage. Lowercase-only improves typing speed. Generation uses `random.choices()` from Python stdlib with collision retry.

**Consequences**:
- Must implement collision detection on generation
- Users can easily type IDs in commands

---

### ADR-002: Command Input Style

**Status**: Accepted

**Context**: Users need to input commands efficiently with varying complexity.

**Decision**: Hybrid approach - both interactive wizard AND inline natural language

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Interactive only | Guided, low errors | Slow for power users |
| Args only | Fast | Steep learning curve |
| **Hybrid** | Best of both | More code to maintain |

**Rationale**: `/add` with no args launches wizard for beginners. `/add <text>` parses natural language for power users. Same command, different modes based on presence of arguments.

**Consequences**:
- Must implement both wizard and NLP parser
- Must clearly document both modes in `/help`

---

### ADR-003: Storage Structure

**Status**: Accepted

**Context**: Need efficient in-memory storage for CRUD operations on tasks.

**Decision**: Dict with ID as key: `dict[str, Task]`

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| List | Simple iteration | O(n) lookup by ID |
| **Dict {id: Task}** | O(1) lookup | Slightly more complex |
| Both (list + index) | Fast everything | Sync complexity |

**Rationale**: Primary access pattern is by ID (show, update, delete, complete). Dict provides O(1) lookup. List operations (list all, search) iterate dict.values() which is still O(n) but acceptable for 1000+ items.

**Consequences**:
- All CRUD operations efficient
- Search remains O(n) - acceptable for Phase I scope

---

### ADR-004: Rich Console Architecture

**Status**: Accepted

**Context**: Need consistent Rich console usage across all UI components.

**Decision**: Global singleton Console instance

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| **Global singleton** | Consistent, simple | Harder to test |
| Passed instance | Testable | Verbose, threading issues |
| Context manager | Clean lifecycle | Overkill for CLI |

**Rationale**: Single-threaded CLI application with one output stream. Global singleton simplifies code and ensures consistent formatting. Testing uses `Console(file=StringIO())` for capture.

**Consequences**:
- All UI modules import from `ui.console`
- Tests must reset/mock console for isolation

---

### ADR-005: Natural Language Date Parsing

**Status**: Accepted

**Context**: Users should enter dates naturally ("tomorrow", "next monday") not just ISO format.

**Decision**: Use `python-dateutil` for relative date parsing with custom keyword handling

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Manual regex | No deps | Complex, error-prone |
| **python-dateutil** | Robust, tested | External dependency |
| dateparser | More languages | Heavy, slow startup |

**Rationale**: `dateutil.parser` handles "tomorrow", "next monday", weekday names. English-only is acceptable per assumptions. Adds ~100KB dependency but saves significant development time.

**Consequences**:
- Add `python-dateutil` to dependencies
- Wrap parser with fallback to ISO format

---

## Implementation Phases

### Phase 1A: Foundation (Checkpoint 1)

**Goal**: Core data layer working, no UI yet

**Tasks**:
1. Initialize UV project in `backend/`
2. Create `pyproject.toml` with dependencies
3. Implement `models/task.py` - Pydantic Task model with validation
4. Implement `storage/memory.py` - In-memory CRUD operations
5. Implement `parsers/nlp.py` - Date/time/priority/category extraction
6. Write unit tests for models, storage, parsers

**Acceptance Criteria**:
- [ ] `uv run pytest` passes all model tests
- [ ] Task creation with all field validations works
- [ ] Storage add/get/update/delete/list/search operations work
- [ ] NLP parser extracts dates, priorities, categories correctly

**Dependencies**: None (first phase)

---

### Phase 1B: Rich UI Layer (Checkpoint 2)

**Goal**: Beautiful output rendering, no commands yet

**Tasks**:
1. Implement `ui/console.py` - Console singleton
2. Implement `ui/theme.py` - Color constants (priority colors, status icons)
3. Implement `ui/banner.py` - Animated welcome banner
4. Implement `ui/tables.py` - Task list table renderer
5. Implement `ui/panels.py` - Task detail panel, empty states, errors
6. Implement `ui/prompts.py` - Interactive input with validation

**Acceptance Criteria**:
- [ ] Welcome banner displays with animation
- [ ] Task table renders with colors and icons
- [ ] Empty state shows friendly panel message
- [ ] Error messages display in red with suggestions
- [ ] Interactive prompts work with validation

**Dependencies**: Phase 1A (models for rendering)

---

### Phase 1C: Command System (Checkpoint 3)

**Goal**: All 10 commands functional

**Tasks**:
1. Implement `parsers/commands.py` - Slash command parser (case-insensitive)
2. Implement `commands/base.py` - Base command interface
3. Implement all command handlers:
   - `/help` - Formatted help screen
   - `/add` - Interactive wizard + NLP inline
   - `/list` - Table view
   - `/show <id>` - Detail panel
   - `/update <id>` - Edit with current values
   - `/complete <id>` - Toggle completion
   - `/delete <id>` - Delete with confirmation
   - `/search <query>` - Search with highlighting
   - `/stats` - Statistics dashboard
   - `/exit` - Graceful shutdown
4. Implement `main.py` - Main REPL loop
5. Write unit tests for command handlers

**Acceptance Criteria**:
- [ ] All 10 commands work correctly
- [ ] Commands are case-insensitive
- [ ] Unknown commands suggest `/help`
- [ ] Invalid IDs show friendly errors
- [ ] Wizard mode and NLP mode both work for `/add`

**Dependencies**: Phase 1A (storage), Phase 1B (UI)

---

### Phase 1D: Polish & Testing (Checkpoint 4)

**Goal**: Production-ready, documented, tested

**Tasks**:
1. Complete unit test coverage (80%+ on business logic)
2. Create `backend/README.md` - Setup, usage, screenshots
3. Update root `CLAUDE.md` - Add Phase I commands
4. Create `AGENTS.md` - Agent behavior rules
5. Final QA pass - all acceptance scenarios
6. Clean up code - docstrings, type hints verification

**Acceptance Criteria**:
- [ ] `uv run pytest --cov` shows 80%+ coverage on models/storage/commands
- [ ] README.md has installation, usage examples, command reference
- [ ] All 9 user stories pass manual testing
- [ ] No raw print statements (all output via rich)
- [ ] All type hints present and mypy passes

**Dependencies**: Phase 1C (all commands)

---

## Testing Strategy

### Unit Tests (Required)

| Module | Test Focus | Target Coverage |
|--------|------------|-----------------|
| `models/task.py` | Pydantic validation, defaults, constraints | 100% |
| `storage/memory.py` | CRUD operations, search, edge cases | 90% |
| `parsers/nlp.py` | Date/time/priority/category extraction | 90% |
| `parsers/commands.py` | Command parsing, case handling | 90% |
| `commands/*.py` | Business logic, validation | 80% |

### Integration Tests (Optional but recommended)

| Flow | Description |
|------|-------------|
| Add-List-Show | Create task, verify in list, view details |
| Add-Complete-Stats | Create task, complete it, verify stats update |
| Search | Create tasks, search, verify results |

### What NOT to Test

- Rich rendering output (visual verification acceptable)
- Console colors/formatting
- Banner animation timing

---

## Quality Gates (Checkpoints)

| Checkpoint | Phase | Criteria | Blocker |
|------------|-------|----------|---------|
| 1 | 1A: Foundation | Models/storage/parsers working + tests passing | Cannot proceed without data layer |
| 2 | 1B: UI Layer | All rich components render correctly | Cannot build commands without UI |
| 3 | 1C: Commands | All 10 commands functional | Cannot polish incomplete app |
| 4 | 1D: Polish | Tests passing, docs complete, QA passed | Cannot demo without polish |

---

## Dependency Flow

```
Phase 1A (Foundation)
       ↓
Phase 1B (UI Layer)
       ↓
Phase 1C (Commands)
       ↓
Phase 1D (Polish)
```

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| NLP parser complexity | Medium | High | Use python-dateutil, limit to documented keywords |
| Rich learning curve | Low | Medium | Follow rich docs, use examples from gallery |
| Test coverage gaps | Medium | Medium | Write tests alongside implementation |
| Scope creep | Medium | High | Strict adherence to spec, no unplanned features |

---

## Success Criteria Summary

From spec, validated against plan:

- ✅ SC-001: Wizard task creation < 60s
- ✅ SC-002: NLP task creation < 10s
- ✅ SC-003: All operations < 1s
- ✅ SC-004: 100% rich formatting (no raw prints)
- ✅ SC-005: Command discovery via /help < 30s
- ✅ SC-006: Priority identification via color coding
- ✅ SC-007: Stats dashboard with 4+ metrics
- ✅ SC-008: User-friendly error messages
- ✅ SC-009: Startup < 2s
- ✅ SC-010: 100% input validation

---

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Begin implementation at Phase 1A
3. Stop at each checkpoint for human review
4. Commit only after checkpoint approval
