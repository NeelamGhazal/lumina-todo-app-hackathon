# Tasks: Phase I - Professional Todo Console Application

**Input**: Design documents from `/specs/001-phase1-todo-cli/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/commands.md (complete)

**Tests**: Unit tests are REQUIRED per spec TR-001 through TR-006 (models, storage, command handlers)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project type**: Web app (backend-only for Phase I)
- **Source**: `backend/src/`
- **Tests**: `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md (backend/src/, backend/tests/)
- [x] T002 Initialize UV project with pyproject.toml in backend/ (python 3.13+, rich, pydantic, python-dateutil, pytest, pytest-cov)
- [x] T003 [P] Create package __init__.py files (backend/src/__init__.py, backend/src/models/__init__.py, backend/src/storage/__init__.py, backend/src/commands/__init__.py, backend/src/ui/__init__.py, backend/src/parsers/__init__.py)
- [x] T004 [P] Create test package __init__.py files (backend/tests/__init__.py, backend/tests/unit/__init__.py, backend/tests/integration/__init__.py)
- [x] T005 [P] Configure pytest in pyproject.toml (testpaths, coverage settings per research.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Data Models

- [x] T006 Implement Priority enum in backend/src/models/task.py (HIGH, MEDIUM, LOW with string values)
- [x] T007 Implement Category enum in backend/src/models/task.py (WORK, PERSONAL, SHOPPING, HEALTH, OTHER)
- [x] T008 Implement Task Pydantic model in backend/src/models/task.py (all fields per data-model.md: id, title, description, priority, category, tags, due_date, due_time, is_completed, created_at)
- [x] T009 Implement generate_id function in backend/src/models/task.py (6-char lowercase alphanumeric per ADR-001)

### Storage Layer

- [x] T010 Implement TaskStorage class in backend/src/storage/memory.py (dict-based per ADR-003)
- [x] T011 Implement add() method in TaskStorage (backend/src/storage/memory.py)
- [x] T012 Implement get() method in TaskStorage (backend/src/storage/memory.py)
- [x] T013 Implement update() method in TaskStorage (backend/src/storage/memory.py)
- [x] T014 Implement delete() method in TaskStorage (backend/src/storage/memory.py)
- [x] T015 Implement list_all() method in TaskStorage (backend/src/storage/memory.py)
- [x] T016 Implement search() method in TaskStorage (backend/src/storage/memory.py)
- [x] T017 Implement get_storage() singleton function in backend/src/storage/memory.py

### Parsers

- [x] T018 Implement parse_date() in backend/src/parsers/nlp.py (today, tomorrow, next monday, weekdays, YYYY-MM-DD using python-dateutil per ADR-005)
- [x] T019 Implement parse_time() in backend/src/parsers/nlp.py (morning=09:00, afternoon=14:00, evening=18:00, night=21:00, HH:MM)
- [x] T020 Implement extract_priority() in backend/src/parsers/nlp.py (urgent/high/medium/low keywords)
- [x] T021 Implement extract_category() in backend/src/parsers/nlp.py (#work, #personal, #shopping, #health, #other hashtags)
- [x] T022 Implement parse_natural_language() in backend/src/parsers/nlp.py (combine all extractors, return parsed components)

### Command Parser

- [x] T023 Implement parse_command() in backend/src/parsers/commands.py (extract command name and args from /command input, case-insensitive per FR-021a)

### UI Foundation (Rich Console)

- [x] T024 Implement get_console() singleton in backend/src/ui/console.py (per ADR-004)
- [x] T025 Implement set_console() for testing in backend/src/ui/console.py
- [x] T026 Define COLORS dict in backend/src/ui/theme.py (priority colors: high=red, medium=yellow, low=green; status colors per research.md)
- [x] T027 Define STATUS_ICONS dict in backend/src/ui/theme.py (completed=✓, pending=✗)
- [x] T028 Define CATEGORY_ICONS dict in backend/src/ui/theme.py (work=💼, personal=🏠, shopping=🛒, health=❤️, other=📌)
- [x] T029 Define PRIORITY_ICONS dict in backend/src/ui/theme.py (high=🔴, medium=🟡, low=🟢)

### Base Command Interface

- [x] T030 Implement Command ABC in backend/src/commands/base.py (name, description, usage properties; execute() abstract method)
- [x] T031 Implement CommandRegistry class in backend/src/commands/base.py (register, get_command, list_commands methods)
- [x] T032 Create get_registry() singleton in backend/src/commands/base.py

### Unit Tests for Foundation

- [x] T033 [P] Create pytest fixtures in backend/tests/conftest.py (sample tasks, mock storage, mock console)
- [x] T034 [P] Write tests for Task model validation in backend/tests/unit/test_models.py (title constraints, priority/category enums, defaults)
- [x] T035 [P] Write tests for generate_id() in backend/tests/unit/test_models.py (format, uniqueness, collision handling)
- [x] T036 [P] Write tests for TaskStorage CRUD in backend/tests/unit/test_storage.py (add, get, update, delete, list_all)
- [x] T037 [P] Write tests for TaskStorage search in backend/tests/unit/test_storage.py (match title, description, tags, category)
- [x] T038 [P] Write tests for parse_date() in backend/tests/unit/test_parsers.py (today, tomorrow, weekdays, ISO format)
- [x] T039 [P] Write tests for parse_time() in backend/tests/unit/test_parsers.py (keywords, HH:MM format)
- [x] T040 [P] Write tests for extract_priority() in backend/tests/unit/test_parsers.py (all keywords)
- [x] T041 [P] Write tests for extract_category() in backend/tests/unit/test_parsers.py (all hashtags)
- [x] T042 [P] Write tests for parse_command() in backend/tests/unit/test_parsers.py (case-insensitivity, arg extraction)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View and Navigate Tasks (Priority: P1) 🎯 MVP

**Goal**: Launch app with welcome banner, view tasks in beautiful table with colors/icons

**Independent Test**: Launch app, run `/list` - see professional welcome and formatted task table

### UI Components for US1

- [x] T043 [US1] Implement render_banner() in backend/src/ui/banner.py (ASCII art TODO logo with rich Panel per quickstart.md)
- [x] T044 [US1] Implement render_task_table() in backend/src/ui/tables.py (columns: ID, Title, Status, Priority, Category, Due Date with colors/icons per FR-015, FR-016, FR-017)
- [x] T045 [US1] Implement render_empty_state() in backend/src/ui/panels.py (friendly panel with example commands per contracts/commands.md /list empty state)

### Command Implementation for US1

- [x] T046 [US1] Implement ListCommand class in backend/src/commands/list.py (fetch all tasks from storage, render table or empty state)
- [x] T047 [US1] Register ListCommand with registry in backend/src/commands/__init__.py

### Unit Tests for US1

- [x] T048 [P] [US1] Write tests for ListCommand in backend/tests/unit/test_commands.py (list with tasks, list empty, output format)

**Checkpoint**: User Story 1 complete - app launches with banner, /list shows formatted table

---

## Phase 4: User Story 2 - Add Tasks via Interactive Wizard (Priority: P1) 🎯 MVP

**Goal**: Create tasks through step-by-step wizard with validation and styled prompts

**Independent Test**: Run `/add` with no args, follow prompts, see confirmation panel

### UI Components for US2

- [x] T049 [US2] Implement prompt_text() in backend/src/ui/prompts.py (styled input with validation message, min/max length)
- [x] T050 [US2] Implement prompt_choice() in backend/src/ui/prompts.py (color-coded options for priority/category selection)
- [x] T051 [US2] Implement prompt_optional() in backend/src/ui/prompts.py (optional field with "press Enter to skip")
- [x] T052 [US2] Implement render_task_created() in backend/src/ui/panels.py (success panel showing task details per contracts/commands.md /add output)
- [x] T053 [US2] Implement render_error() in backend/src/ui/panels.py (red panel with error message and suggestion)

### Command Implementation for US2

- [x] T054 [US2] Implement AddCommand class in backend/src/commands/add.py (detect wizard vs NLP mode based on args)
- [x] T055 [US2] Implement _run_wizard() method in AddCommand (prompt for each field: title, description, priority, category, tags, due_date, due_time)
- [x] T056 [US2] Implement field validation in _run_wizard() (title 1-200 chars, show error and retry on failure)
- [x] T057 [US2] Register AddCommand with registry in backend/src/commands/__init__.py

### Unit Tests for US2

- [x] T058 [P] [US2] Write tests for AddCommand wizard mode in backend/tests/unit/test_commands.py (task creation, validation errors, defaults)

**Checkpoint**: User Story 2 complete - wizard creates tasks with validation

---

## Phase 5: User Story 3 - Add Tasks via Natural Language (Priority: P2)

**Goal**: Quick task creation with `/add Buy milk tomorrow #shopping urgent`

**Independent Test**: Run `/add Buy groceries tomorrow #shopping high` - see task created with correct fields

### Command Implementation for US3

- [x] T059 [US3] Implement _run_nlp() method in AddCommand (backend/src/commands/add.py) - call parse_natural_language(), create task
- [x] T060 [US3] Implement NLP result display in _run_nlp() (show interpreted values: title, due date, priority, category)

### Unit Tests for US3

- [x] T061 [P] [US3] Write tests for AddCommand NLP mode in backend/tests/unit/test_commands.py (date extraction, priority extraction, category extraction, combined parsing)

**Checkpoint**: User Story 3 complete - NLP task creation works

---

## Phase 6: User Story 4 - View Task Details (Priority: P2)

**Goal**: View complete task details in formatted panel with `/show <id>`

**Independent Test**: Create task, run `/show <id>` - see all fields beautifully formatted

### UI Components for US4

- [x] T062 [US4] Implement render_task_detail() in backend/src/ui/panels.py (panel with all task fields per contracts/commands.md /show output)

### Command Implementation for US4

- [x] T063 [US4] Implement ShowCommand class in backend/src/commands/show.py (get task by ID, render detail panel or error)
- [x] T064 [US4] Implement ID validation in ShowCommand (check ID provided, check task exists, friendly error messages per contracts)
- [x] T065 [US4] Register ShowCommand with registry in backend/src/commands/__init__.py

### Unit Tests for US4

- [x] T066 [P] [US4] Write tests for ShowCommand in backend/tests/unit/test_commands.py (valid ID, missing ID, invalid ID)

**Checkpoint**: User Story 4 complete - /show displays task details

---

## Phase 7: User Story 5 - Update Tasks (Priority: P2)

**Goal**: Update task fields while seeing current values

**Independent Test**: Create task, run `/update <id>` - modify fields, see before/after comparison

### UI Components for US5

- [x] T067 [US5] Implement render_update_comparison() in backend/src/ui/panels.py (before/after panel showing changed fields per contracts/commands.md /update output)

### Command Implementation for US5

- [x] T068 [US5] Implement UpdateCommand class in backend/src/commands/update.py (get task, show current values, prompt for changes)
- [x] T069 [US5] Implement _prompt_with_default() in UpdateCommand (show current value, keep on Enter)
- [x] T070 [US5] Implement change tracking in UpdateCommand (track which fields changed for comparison display)
- [x] T071 [US5] Register UpdateCommand with registry in backend/src/commands/__init__.py

### Unit Tests for US5

- [x] T072 [P] [US5] Write tests for UpdateCommand in backend/tests/unit/test_commands.py (update fields, keep current, task not found)

**Checkpoint**: User Story 5 complete - /update modifies tasks

---

## Phase 8: User Story 6 - Complete and Delete Tasks (Priority: P2)

**Goal**: Toggle completion status and delete tasks with confirmation

**Independent Test**: Create task, run `/complete <id>` - see toggle; run `/delete <id>` - confirm and delete

### UI Components for US6

- [x] T073 [US6] Implement render_completion_toggle() in backend/src/ui/panels.py (message with checkmark/cross per contracts)
- [x] T074 [US6] Implement confirm_delete() in backend/src/ui/prompts.py (confirmation prompt [y/N])
- [x] T075 [US6] Implement render_delete_result() in backend/src/ui/panels.py (deleted/cancelled message)

### Command Implementation for US6

- [x] T076 [US6] Implement CompleteCommand class in backend/src/commands/complete.py (toggle is_completed, show result)
- [x] T077 [US6] Register CompleteCommand with registry in backend/src/commands/__init__.py
- [x] T078 [US6] Implement DeleteCommand class in backend/src/commands/delete.py (confirm, delete, show result)
- [x] T079 [US6] Register DeleteCommand with registry in backend/src/commands/__init__.py

### Unit Tests for US6

- [x] T080 [P] [US6] Write tests for CompleteCommand in backend/tests/unit/test_commands.py (toggle pending→complete, toggle complete→pending, not found)
- [x] T081 [P] [US6] Write tests for DeleteCommand in backend/tests/unit/test_commands.py (confirm delete, cancel delete, not found)

**Checkpoint**: User Story 6 complete - /complete and /delete work

---

## Phase 9: User Story 7 - Search Tasks (Priority: P3)

**Goal**: Search tasks by keyword across all fields

**Independent Test**: Create tasks, run `/search groceries` - see filtered results with highlighting

### UI Components for US7

- [x] T082 [US7] Implement render_search_results() in backend/src/ui/tables.py (filtered table with match highlighting per contracts)
- [x] T083 [US7] Implement render_no_results() in backend/src/ui/panels.py (friendly message with suggestions per contracts)

### Command Implementation for US7

- [x] T084 [US7] Implement SearchCommand class in backend/src/commands/search.py (call storage.search(), render results or no-results)
- [x] T085 [US7] Implement query validation in SearchCommand (require query, friendly error if missing)
- [x] T086 [US7] Register SearchCommand with registry in backend/src/commands/__init__.py

### Unit Tests for US7

- [x] T087 [P] [US7] Write tests for SearchCommand in backend/tests/unit/test_commands.py (matches found, no matches, missing query)

**Checkpoint**: User Story 7 complete - /search finds tasks

---

## Phase 10: User Story 8 - View Statistics (Priority: P3)

**Goal**: View visual statistics dashboard with progress bars and breakdowns

**Independent Test**: Create tasks, run `/stats` - see dashboard with metrics and progress bar

### UI Components for US8

- [x] T088 [US8] Implement render_stats_dashboard() in backend/src/ui/panels.py (overview panel with total/completed/pending counts, progress bar, priority breakdown, category breakdown per contracts)
- [x] T089 [US8] Implement render_progress_bar() in backend/src/ui/panels.py (completion percentage visual bar per FR-019)
- [x] T090 [US8] Implement render_no_stats() in backend/src/ui/panels.py (empty state encouraging task creation)

### Command Implementation for US8

- [x] T091 [US8] Implement StatsCommand class in backend/src/commands/stats.py (calculate stats from storage, render dashboard or empty)
- [x] T092 [US8] Implement _calculate_stats() in StatsCommand (total, completed, pending, by priority, by category)
- [x] T093 [US8] Register StatsCommand with registry in backend/src/commands/__init__.py

### Unit Tests for US8

- [x] T094 [P] [US8] Write tests for StatsCommand in backend/tests/unit/test_commands.py (stats with tasks, stats empty, stat calculations)

**Checkpoint**: User Story 8 complete - /stats shows dashboard

---

## Phase 11: User Story 9 - Help and Exit (Priority: P3)

**Goal**: Display comprehensive help and exit gracefully

**Independent Test**: Run `/help` - see all commands; run `/exit` - see goodbye message

### UI Components for US9

- [x] T095 [US9] Implement render_help() in backend/src/ui/panels.py (formatted help screen with grouped commands per contracts/commands.md /help output)
- [x] T096 [US9] Implement render_goodbye() in backend/src/ui/panels.py (farewell message per contracts)
- [x] T097 [US9] Implement render_unknown_command() in backend/src/ui/panels.py (error with /help suggestion per contracts)
- [x] T098 [US9] Implement render_invalid_input() in backend/src/ui/panels.py (commands must start with / per contracts)

### Command Implementation for US9

- [x] T099 [US9] Implement HelpCommand class in backend/src/commands/help.py (render help screen)
- [x] T100 [US9] Register HelpCommand with registry in backend/src/commands/__init__.py
- [x] T101 [US9] Implement ExitCommand class in backend/src/commands/exit.py (render goodbye, signal exit)
- [x] T102 [US9] Register ExitCommand with registry in backend/src/commands/__init__.py

### Unit Tests for US9

- [x] T103 [P] [US9] Write tests for HelpCommand in backend/tests/unit/test_commands.py (output contains all commands)
- [x] T104 [P] [US9] Write tests for ExitCommand in backend/tests/unit/test_commands.py (exit signal)

**Checkpoint**: User Story 9 complete - /help and /exit work

---

## Phase 12: Main Application Loop

**Purpose**: Wire everything together into the running application

- [x] T105 Implement main() function in backend/src/main.py (render banner, start REPL loop)
- [x] T106 Implement REPL loop in main() (read input, parse command, execute, handle errors)
- [x] T107 Implement unknown command handling in main() (show unknown command panel per US9)
- [x] T108 Implement invalid input handling in main() (no / prefix, show error per US9)
- [x] T109 Register all commands on startup in backend/src/commands/__init__.py (import and register all 10 commands)
- [x] T110 Create __main__.py entry point in backend/src/__main__.py (allow `python -m src.main`)

### Integration Tests

- [x] T111 [P] Write integration test for add-list-show flow in backend/tests/integration/test_cli_flows.py
- [x] T112 [P] Write integration test for add-complete-stats flow in backend/tests/integration/test_cli_flows.py
- [x] T113 [P] Write integration test for search flow in backend/tests/integration/test_cli_flows.py

**Checkpoint**: Application runs end-to-end

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Final quality pass and documentation

- [x] T114 [P] Add docstrings to all public functions and classes
- [x] T115 [P] Verify all type hints are present (run mypy if configured)
- [x] T116 [P] Run pytest --cov and verify 80%+ coverage on models/storage/commands
- [x] T117 [P] Create backend/README.md with installation, usage, command reference
- [x] T118 Run quickstart.md validation (follow steps, verify app works as documented)
- [x] T119 Manual QA pass on all 9 user stories (verify acceptance scenarios)
- [x] T120 Code review for raw print statements (ensure all output via rich)

**Checkpoint**: Production-ready, documented, tested

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-11)**: All depend on Foundational phase completion
  - US1 (P1) and US2 (P1) can proceed in parallel after Foundational
  - US3-US9 (P2/P3) can proceed after respective P1 stories if needed
- **Main Loop (Phase 12)**: Depends on all user story commands being complete
- **Polish (Phase 13)**: Depends on Main Loop completion

### User Story Dependencies

| Story | Priority | Depends On | Can Parallel With |
|-------|----------|------------|-------------------|
| US1: View/Navigate | P1 | Foundational | US2 |
| US2: Add Wizard | P1 | Foundational | US1 |
| US3: Add NLP | P2 | US2 (AddCommand exists) | US4, US5, US6 |
| US4: Show Details | P2 | Foundational | US3, US5, US6 |
| US5: Update | P2 | Foundational | US3, US4, US6 |
| US6: Complete/Delete | P2 | Foundational | US3, US4, US5 |
| US7: Search | P3 | Foundational | US8, US9 |
| US8: Stats | P3 | Foundational | US7, US9 |
| US9: Help/Exit | P3 | Foundational | US7, US8 |

### Within Each User Story

- UI components before commands (commands use UI)
- Commands before tests (tests verify commands)
- All [P] tasks within a phase can run in parallel

### Parallel Opportunities

```bash
# Setup parallel tasks:
T003, T004, T005 can all run in parallel

# Foundational models in sequence (same file):
T006 → T007 → T008 → T009 (all in task.py)

# Foundational storage in sequence (same file):
T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017 (all in memory.py)

# Foundation tests all parallel (different files):
T033, T034, T035, T036, T037, T038, T039, T040, T041, T042

# User stories can parallel after Foundational:
US1 || US2  (both P1, different commands)
US4 || US5 || US6  (all P2, different commands)
US7 || US8 || US9  (all P3, different commands)
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (View/Navigate)
4. Complete Phase 4: User Story 2 (Add Wizard)
5. **STOP and VALIDATE**: Test US1 + US2 independently - app can launch, list, and add tasks
6. This is a working MVP!

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 + US2 → MVP ready (can demo!)
3. Add US3 → NLP quick-add
4. Add US4 + US5 + US6 → Full CRUD
5. Add US7 + US8 + US9 → Complete feature set
6. Main Loop + Polish → Production ready

### Task Count Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| 1: Setup | 5 | T003, T004, T005 |
| 2: Foundational | 37 | T033-T042 (tests) |
| 3: US1 View/Navigate | 6 | T048 |
| 4: US2 Add Wizard | 10 | T058 |
| 5: US3 Add NLP | 3 | T061 |
| 6: US4 Show Details | 5 | T066 |
| 7: US5 Update | 6 | T072 |
| 8: US6 Complete/Delete | 10 | T080, T081 |
| 9: US7 Search | 6 | T087 |
| 10: US8 Stats | 7 | T094 |
| 11: US9 Help/Exit | 10 | T103, T104 |
| 12: Main Loop | 9 | T111, T112, T113 |
| 13: Polish | 7 | T114, T115, T116, T117 |
| **TOTAL** | **120** | |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks in same phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are REQUIRED per spec (TR-001 through TR-006)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All output must use rich library (no raw print statements per FR-020)
