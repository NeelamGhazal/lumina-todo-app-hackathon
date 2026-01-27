# Phase I to Phase II Migration Skill

> Systematic process for migrating console applications to full-stack web applications

## Metadata

| Field | Value |
|-------|-------|
| **Skill Name** | phase1-to-phase2-migration |
| **Version** | 1.0.0 |
| **Agent** | migration-expert |
| **Category** | Architecture Migration |

## Description

A systematic process for migrating Phase I console applications to Phase II full-stack web applications while preserving all functionality, business logic, and user experience. This skill ensures zero feature loss and maintains consistency between CLI and API implementations.

## When to Use

| Scenario | Applicable |
|----------|------------|
| Converting CLI commands to API endpoints | Yes |
| Migrating in-memory storage to database | Yes |
| Preserving business logic during platform change | Yes |
| Ensuring feature parity across implementations | Yes |
| Adding new features not in Phase I | No |
| Refactoring Phase I without migration | No |

## Prerequisites

Before executing this skill:

- [ ] Phase I application is complete and tested
- [ ] All Phase I features are documented
- [ ] Phase II tech stack is defined (framework, database, etc.)
- [ ] Migration timeline and scope are approved

## Process Steps

### Step 1: Inventory Phase I

**Goal**: Create comprehensive list of all features, commands, and data models

**Actions**:
1. List all CLI commands with their arguments
2. Document each command's functionality
3. Identify input validation rules
4. Map error handling behaviors
5. Document data models and fields
6. Note any business logic or calculations

**Output**: Feature inventory document

```markdown
## Phase I Feature Inventory

### Commands
| Command | Arguments | Description | Validation |
|---------|-----------|-------------|------------|
| /add | [text] | Create task | title: 1-200 chars |
| /list | none | Show all tasks | N/A |
| ... | ... | ... | ... |

### Data Models
| Model | Fields | Constraints |
|-------|--------|-------------|
| Task | id, title, ... | id: 6-char alphanumeric |

### Business Logic
- ID generation: 6-char lowercase alphanumeric
- Search: case-insensitive, matches title/description/tags
- ...
```

---

### Step 2: Map to REST

**Goal**: Design API endpoints for each CLI command

**Actions**:
1. Identify resources (nouns) from commands
2. Map commands to HTTP methods
3. Define URL structure and parameters
4. Specify request/response payloads
5. Document status codes and errors

**Output**: API endpoint mapping table

```markdown
## API Endpoint Mapping

| CLI Command | HTTP Method | Endpoint | Request Body | Response |
|-------------|-------------|----------|--------------|----------|
| /add | POST | /api/tasks | TaskCreate | Task |
| /list | GET | /api/tasks | - | Task[] |
| /show <id> | GET | /api/tasks/{id} | - | Task |
| /update <id> | PUT | /api/tasks/{id} | TaskUpdate | Task |
| /delete <id> | DELETE | /api/tasks/{id} | - | 204 |
| /complete <id> | PATCH | /api/tasks/{id}/complete | - | Task |
| /search <q> | GET | /api/tasks/search?q= | - | Task[] |
| /stats | GET | /api/stats | - | Stats |

### Request/Response Schemas

#### TaskCreate
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 2000 chars)",
  "priority": "high|medium|low (default: medium)",
  "category": "work|personal|shopping|health|other",
  "tags": ["string"],
  "due_date": "YYYY-MM-DD (optional)",
  "due_time": "HH:MM (optional)"
}
```
```

---

### Step 3: Extract Logic

**Goal**: Separate business logic from CLI presentation layer

**Actions**:
1. Identify pure business logic functions
2. Create service layer abstraction
3. Define interfaces for storage operations
4. Extract validation logic
5. Isolate calculation/aggregation logic

**Output**: Service layer design

```markdown
## Service Layer Design

### TaskService
- create(data: TaskCreate) -> Task
- get(id: str) -> Task | None
- list() -> list[Task]
- update(id: str, data: TaskUpdate) -> Task | None
- delete(id: str) -> bool
- toggle_complete(id: str) -> Task | None
- search(query: str) -> list[Task]

### StatsService
- get_stats() -> Stats
  - total_tasks: int
  - completed: int
  - pending: int
  - by_priority: dict
  - by_category: dict

### Validation Rules (preserved from Phase I)
- Title: 1-200 characters, required
- Description: max 2000 characters
- ID: 6-character lowercase alphanumeric
- Priority: enum (high, medium, low)
- Category: enum (work, personal, shopping, health, other)
```

---

### Step 4: Database Design

**Goal**: Convert in-memory models to database schemas

**Actions**:
1. Map Pydantic models to ORM models
2. Define table structure and types
3. Add indexes for common queries
4. Define constraints and defaults
5. Create migration scripts

**Output**: Database schema

```markdown
## Database Schema

### tasks table
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(6) | PRIMARY KEY |
| title | VARCHAR(200) | NOT NULL |
| description | TEXT | DEFAULT '' |
| priority | VARCHAR(10) | DEFAULT 'medium' |
| category | VARCHAR(10) | DEFAULT 'other' |
| tags | JSON | DEFAULT '[]' |
| due_date | DATE | NULLABLE |
| due_time | TIME | NULLABLE |
| is_completed | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMP | DEFAULT NOW() |

### Indexes
- idx_tasks_priority ON tasks(priority)
- idx_tasks_category ON tasks(category)
- idx_tasks_is_completed ON tasks(is_completed)
- idx_tasks_due_date ON tasks(due_date)

### Migration Script
```sql
CREATE TABLE tasks (
    id VARCHAR(6) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    priority VARCHAR(10) DEFAULT 'medium',
    category VARCHAR(10) DEFAULT 'other',
    tags JSON DEFAULT '[]',
    due_date DATE,
    due_time TIME,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
```

---

### Step 5: Create Adapters

**Goal**: Build abstraction layer for storage to enable testing and flexibility

**Actions**:
1. Define repository interface
2. Implement database repository
3. Create in-memory repository for testing
4. Add dependency injection support
5. Ensure interface matches Phase I operations

**Output**: Repository pattern implementation

```markdown
## Repository Pattern

### Interface
```python
class TaskRepository(ABC):
    @abstractmethod
    def add(self, task: Task) -> Task: ...

    @abstractmethod
    def get(self, task_id: str) -> Task | None: ...

    @abstractmethod
    def update(self, task_id: str, **updates) -> Task | None: ...

    @abstractmethod
    def delete(self, task_id: str) -> bool: ...

    @abstractmethod
    def list_all(self) -> list[Task]: ...

    @abstractmethod
    def search(self, query: str) -> list[Task]: ...
```

### Implementations
- `SQLAlchemyTaskRepository` - Production database
- `InMemoryTaskRepository` - Testing (reuse Phase I)
```

---

### Step 6: Test Parity

**Goal**: Verify all Phase I features work identically in Phase II

**Actions**:
1. Create feature parity test matrix
2. Port Phase I test cases to API tests
3. Verify validation behavior matches
4. Test error responses match expectations
5. Performance comparison testing

**Output**: Feature parity checklist

```markdown
## Feature Parity Checklist

### Task CRUD
- [ ] Create task with all fields
- [ ] Create task with minimum fields (title only)
- [ ] Create task validates title length (1-200)
- [ ] Create task validates description length (max 2000)
- [ ] Get task by valid ID returns task
- [ ] Get task by invalid ID returns 404
- [ ] Update task changes specified fields
- [ ] Update task keeps unspecified fields
- [ ] Delete task removes from storage
- [ ] Delete non-existent task returns 404

### Task Completion
- [ ] Toggle pending -> completed
- [ ] Toggle completed -> pending
- [ ] Toggle non-existent returns 404

### Search
- [ ] Search matches title (case-insensitive)
- [ ] Search matches description
- [ ] Search matches tags
- [ ] Search matches category
- [ ] Search no results returns empty array

### Statistics
- [ ] Stats returns total count
- [ ] Stats returns completed count
- [ ] Stats returns pending count
- [ ] Stats returns priority breakdown
- [ ] Stats returns category breakdown
- [ ] Stats with no tasks returns zeros

### Validation (all must match Phase I)
- [ ] Title required
- [ ] Title max 200 chars
- [ ] Description max 2000 chars
- [ ] Priority must be valid enum
- [ ] Category must be valid enum
- [ ] ID format: 6-char alphanumeric
```

---

### Step 7: Document Changes

**Goal**: Create comprehensive migration documentation

**Actions**:
1. Write API documentation (OpenAPI/Swagger)
2. Create migration guide for developers
3. Document breaking changes (if any)
4. Provide rollback procedures
5. Update project README

**Output**: Migration documentation package

```markdown
## Migration Documentation

### API Documentation
- OpenAPI spec at /api/docs
- Swagger UI at /api/swagger

### Migration Guide
1. Database setup and migrations
2. Environment configuration
3. Running the API server
4. Testing endpoints
5. Deploying to production

### Rollback Procedures
1. Stop Phase II API server
2. Restore database from backup (if needed)
3. Restart Phase I CLI application
4. Verify functionality

### Breaking Changes
- None (feature parity maintained)
```

---

## Output Artifacts

| Artifact | Format | Location |
|----------|--------|----------|
| Migration plan | Markdown | `specs/{feature}/migration-plan.md` |
| API endpoint mapping | Table | Included in plan |
| Database schema | SQL + Markdown | `backend/migrations/` |
| Feature parity checklist | Markdown | `specs/{feature}/parity-checklist.md` |
| Testing scenarios | Pytest | `backend/tests/integration/` |
| Rollback procedures | Markdown | Included in plan |
| API specification | OpenAPI 3.0 | `backend/openapi.yaml` |

## Quality Criteria

All migrations must meet these criteria:

| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Zero feature loss | 100% Phase I features in Phase II | Parity checklist |
| CLI command mapping | All commands have API endpoints | Mapping table |
| Business logic unchanged | Same behavior, different interface | Test comparison |
| Error handling preserved | Same errors, HTTP status codes | Error matrix |
| Performance | Equal or better response times | Load testing |
| Database normalized | 3NF minimum, proper indexes | Schema review |

## Example Migration

### Input: Phase I Todo CLI

```
Commands: /add, /list, /show, /update, /delete, /complete, /search, /stats
Storage: In-memory dict
Model: Task (Pydantic)
```

### Output: Phase II REST API

```
Endpoints:
  POST   /api/tasks           <- /add
  GET    /api/tasks           <- /list
  GET    /api/tasks/{id}      <- /show
  PUT    /api/tasks/{id}      <- /update
  DELETE /api/tasks/{id}      <- /delete
  PATCH  /api/tasks/{id}/complete <- /complete
  GET    /api/tasks/search    <- /search
  GET    /api/stats           <- /stats

Storage: PostgreSQL with SQLAlchemy
Model: Task (SQLAlchemy + Pydantic schemas)

Feature Parity: 100%
All validation rules preserved
All error handling preserved
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Validation mismatch | Compare Phase I validators with API schemas |
| Missing feature | Re-check inventory, add endpoint |
| Performance regression | Add database indexes, optimize queries |
| Error format different | Update error handlers to match Phase I messages |

## Related Skills

- `api-design` - RESTful API design patterns
- `database-migration` - Database schema evolution
- `test-migration` - Converting test suites
