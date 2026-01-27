# PostgreSQL Schema Design Skill

> Design production-ready PostgreSQL schemas with SQLModel, optimized for performance and maintainability

## Metadata

| Field | Value |
|-------|-------|
| **Skill Name** | postgres-schema-design |
| **Version** | 1.0.0 |
| **Agent** | db-schema-designer |
| **Category** | Database Architecture |
| **Target Platform** | Neon PostgreSQL (serverless) |

## Description

A systematic process for designing production-ready PostgreSQL schemas using SQLModel ORM. This skill covers entity analysis, relationship mapping, type selection, constraint design, index strategy, and migration generation with a focus on performance and data integrity.

## When to Use

| Scenario | Applicable |
|----------|------------|
| Creating new database models | Yes |
| Migrating from in-memory to database | Yes |
| Adding relationships between entities | Yes |
| Optimizing existing schemas | Yes |
| Generating Alembic migration scripts | Yes |
| Query optimization | Partial (index-focused) |
| Data migration strategies | Escalate |

## Prerequisites

Before executing this skill:

- [ ] Domain entities are identified (from spec or data-model.md)
- [ ] Query patterns are understood (list, filter, search)
- [ ] Relationship cardinality is known (1:1, 1:N, N:M)
- [ ] Tech stack confirmed (SQLModel, Alembic, asyncpg)

## Process Steps

### Step 1: Entity Analysis

**Goal**: Identify all domain entities and their attributes

**Actions**:
1. List all entities from domain model
2. Document each attribute with business meaning
3. Identify required vs optional fields
4. Note any computed/derived fields
5. Determine data lifecycle (create, update, soft-delete?)

**Output**: Entity attribute inventory

```markdown
## Entity: Task

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string(6) | Yes | Unique identifier |
| title | string | Yes | Task name, 1-200 chars |
| description | string | No | Detailed description |
| priority | enum | Yes | high/medium/low |
| category | enum | Yes | work/personal/shopping/health/other |
| tags | array | No | User-defined labels |
| due_date | date | No | Target completion date |
| due_time | time | No | Target completion time |
| is_completed | boolean | Yes | Completion status |
| created_at | datetime | Yes | Creation timestamp |

### Business Rules
- Title must be 1-200 characters
- Description max 2000 characters
- ID is 6-character lowercase alphanumeric
- created_at set automatically on creation
```

---

### Step 2: Relationship Mapping

**Goal**: Define relationships between entities

**Actions**:
1. Identify all entity relationships
2. Determine cardinality (1:1, 1:N, N:M)
3. Define referential actions (CASCADE, SET NULL, RESTRICT)
4. Create junction tables for N:M relationships
5. Document relationship constraints

**Output**: Relationship diagram and definitions

```markdown
## Relationships

### Entity Relationship Diagram
```
┌──────────┐       ┌────────────┐       ┌────────────┐
│  users   │──────<│   tasks    │>──────│    tags    │
└──────────┘  1:N  └────────────┘  N:M  └────────────┘
     │                   │
     │ 1:N               │ N:1
     ▼                   ▼
┌──────────┐       ┌────────────┐
│ sessions │       │ categories │
└──────────┘       └────────────┘
```

### Relationship Definitions

| From | To | Cardinality | On Delete | Description |
|------|----|-------------|-----------|-------------|
| users | tasks | 1:N | CASCADE | User owns tasks |
| tasks | categories | N:1 | RESTRICT | Task has category |
| tasks | tags | N:M | CASCADE | Tasks can have many tags |

### Junction Tables (for N:M)
- task_tags (task_id, tag_id) - Links tasks to tags
```

---

### Step 3: Type Selection

**Goal**: Choose optimal PostgreSQL types for each field

**Actions**:
1. Map each attribute to PostgreSQL type
2. Consider storage efficiency
3. Account for query patterns
4. Use appropriate precision for numbers
5. Choose between JSONB and normalized tables

**Output**: Type mapping table

```markdown
## PostgreSQL Type Mapping

| Field | Python Type | PostgreSQL Type | Justification |
|-------|-------------|-----------------|---------------|
| id | str | VARCHAR(6) | Fixed-length identifier |
| title | str | VARCHAR(200) | Known max length |
| description | str | TEXT | Variable long text |
| priority | Enum | priority_enum | Type safety, validation |
| category | str | VARCHAR(20) | Simple lookup |
| tags | list[str] | JSONB | Flexible, queryable |
| due_date | date | DATE | Date-only storage |
| due_time | time | TIME | Time-only storage |
| is_completed | bool | BOOLEAN | Simple flag |
| created_at | datetime | TIMESTAMPTZ | Timezone-aware |

### Type Decision Notes
- **JSONB for tags**: Allows flexible tag queries (`@>`, `?`, `?|`)
  without junction table overhead for simple use case
- **ENUM for priority**: Prevents invalid values at database level,
  self-documenting schema
- **TIMESTAMPTZ**: Always store with timezone for consistency
- **VARCHAR(N)**: Use when max length is known and enforced
```

---

### Step 4: Constraint Design

**Goal**: Add validation, uniqueness, and referential integrity

**Actions**:
1. Define PRIMARY KEY for each table
2. Add FOREIGN KEY constraints
3. Create UNIQUE constraints
4. Add CHECK constraints for business rules
5. Set NOT NULL appropriately
6. Define DEFAULT values

**Output**: Constraint specification

```markdown
## Constraints

### Primary Keys
| Table | Column(s) | Type |
|-------|-----------|------|
| tasks | id | VARCHAR(6) |
| users | id | SERIAL |
| tags | id | SERIAL |

### Foreign Keys
| Table | Column | References | On Delete |
|-------|--------|------------|-----------|
| tasks | user_id | users.id | CASCADE |
| task_tags | task_id | tasks.id | CASCADE |
| task_tags | tag_id | tags.id | CASCADE |

### Unique Constraints
| Table | Column(s) | Name |
|-------|-----------|------|
| users | email | uq_users_email |
| tags | user_id, name | uq_tags_user_name |

### Check Constraints
| Table | Constraint | Expression |
|-------|------------|------------|
| tasks | chk_title_length | LENGTH(title) BETWEEN 1 AND 200 |
| tasks | chk_desc_length | LENGTH(description) <= 2000 |
| tasks | chk_priority | priority IN ('high', 'medium', 'low') |

### Not Null
| Table | Columns |
|-------|---------|
| tasks | id, title, priority, is_completed, created_at |
| users | id, email, created_at |

### Defaults
| Table | Column | Default |
|-------|--------|---------|
| tasks | priority | 'medium' |
| tasks | category | 'other' |
| tasks | is_completed | false |
| tasks | tags | '[]'::jsonb |
| tasks | created_at | CURRENT_TIMESTAMP |
```

---

### Step 5: Index Strategy

**Goal**: Identify query patterns and create optimal indexes

**Actions**:
1. List all expected queries
2. Identify filter columns
3. Identify sort columns
4. Create composite indexes for multi-column queries
5. Consider partial indexes for common filters
6. Add GIN indexes for JSONB/array columns

**Output**: Index specification with justification

```markdown
## Index Strategy

### Query Pattern Analysis
| Query | Filters | Sort | Frequency |
|-------|---------|------|-----------|
| List user's tasks | user_id | created_at DESC | High |
| List by due date | user_id, due_date | due_date ASC | Medium |
| Filter by priority | user_id, priority | - | Medium |
| Filter by category | user_id, category | - | Medium |
| Search by tag | tags contains | - | Low |
| Active tasks only | is_completed=false | - | High |

### Index Definitions
| Name | Table | Columns | Type | Justification |
|------|-------|---------|------|---------------|
| idx_tasks_user_id | tasks | user_id | B-tree | FK lookups, ownership filter |
| idx_tasks_user_created | tasks | user_id, created_at DESC | B-tree | Default list query |
| idx_tasks_user_due | tasks | user_id, due_date | B-tree | Due date filtering |
| idx_tasks_priority | tasks | priority | B-tree | Priority filtering |
| idx_tasks_category | tasks | category | B-tree | Category filtering |
| idx_tasks_tags_gin | tasks | tags | GIN | Tag containment queries |
| idx_tasks_active | tasks | user_id | Partial | WHERE is_completed = false |

### Index SQL
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
CREATE INDEX idx_tasks_user_due ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_category ON tasks(category);
CREATE INDEX idx_tasks_tags_gin ON tasks USING GIN(tags);
CREATE INDEX idx_tasks_active ON tasks(user_id)
    WHERE is_completed = false;
```
```

---

### Step 6: Migration Script

**Goal**: Generate Alembic migration with proper up/down

**Actions**:
1. Create migration file with revision ID
2. Implement upgrade() with all DDL
3. Implement downgrade() for rollback
4. Handle enum type creation
5. Create indexes after table
6. Test both directions

**Output**: Alembic migration file

```python
"""Create tasks table

Revision ID: 001_create_tasks
Revises: None
Create Date: 2025-01-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ENUM as PgEnum

revision = '001_create_tasks'
down_revision = None
branch_labels = None
depends_on = None

# Enum definitions
priority_enum = PgEnum('high', 'medium', 'low', name='priority_enum')
category_enum = PgEnum(
    'work', 'personal', 'shopping', 'health', 'other',
    name='category_enum'
)


def upgrade() -> None:
    # Create enum types
    priority_enum.create(op.get_bind(), checkfirst=True)
    category_enum.create(op.get_bind(), checkfirst=True)

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(6), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), server_default=''),
        sa.Column('priority', priority_enum, server_default='medium'),
        sa.Column('category', category_enum, server_default='other'),
        sa.Column('tags', JSONB, server_default='[]'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('due_time', sa.Time(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), server_default='false'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        # Check constraints
        sa.CheckConstraint(
            "LENGTH(title) BETWEEN 1 AND 200",
            name='chk_tasks_title_length'
        ),
        sa.CheckConstraint(
            "LENGTH(description) <= 2000",
            name='chk_tasks_desc_length'
        ),
    )

    # Create indexes
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_category', 'tasks', ['category'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('idx_tasks_is_completed', 'tasks', ['is_completed'])
    op.execute(
        "CREATE INDEX idx_tasks_tags_gin ON tasks USING GIN(tags)"
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_tasks_tags_gin')
    op.drop_index('idx_tasks_is_completed')
    op.drop_index('idx_tasks_due_date')
    op.drop_index('idx_tasks_category')
    op.drop_index('idx_tasks_priority')

    # Drop table
    op.drop_table('tasks')

    # Drop enum types
    category_enum.drop(op.get_bind(), checkfirst=True)
    priority_enum.drop(op.get_bind(), checkfirst=True)
```

---

### Step 7: Validation

**Goal**: Test schema with sample data and queries

**Actions**:
1. Insert sample data covering all fields
2. Test constraint violations
3. Verify index usage with EXPLAIN
4. Test relationship queries
5. Validate migration rollback

**Output**: Validation test suite

```markdown
## Schema Validation Tests

### Data Insertion Tests
```sql
-- Valid task (should succeed)
INSERT INTO tasks (id, title, priority, category, tags)
VALUES ('abc123', 'Test task', 'high', 'work', '["urgent"]');

-- Missing title (should fail - NOT NULL)
INSERT INTO tasks (id, priority) VALUES ('xyz789', 'low');
-- ERROR: null value in column "title"

-- Title too long (should fail - CHECK)
INSERT INTO tasks (id, title) VALUES ('xyz789', REPEAT('x', 201));
-- ERROR: check constraint "chk_tasks_title_length"

-- Invalid priority (should fail - ENUM)
INSERT INTO tasks (id, title, priority) VALUES ('xyz789', 'Test', 'critical');
-- ERROR: invalid input value for enum priority_enum
```

### Index Usage Verification
```sql
EXPLAIN ANALYZE SELECT * FROM tasks WHERE priority = 'high';
-- Should show: Index Scan using idx_tasks_priority

EXPLAIN ANALYZE SELECT * FROM tasks WHERE tags @> '["urgent"]';
-- Should show: Bitmap Index Scan on idx_tasks_tags_gin
```

### Migration Rollback Test
```bash
# Apply migration
alembic upgrade head

# Verify table exists
psql -c "\d tasks"

# Rollback migration
alembic downgrade -1

# Verify table dropped
psql -c "\d tasks"
-- ERROR: relation "tasks" does not exist
```
```

---

## Output Artifacts

| Artifact | Format | Location |
|----------|--------|----------|
| SQLModel models | Python | `backend/src/models/` |
| Alembic migration | Python | `backend/migrations/versions/` |
| ER diagram | Text/Mermaid | `docs/database/er-diagram.md` |
| Index justification | Markdown | `docs/database/indexes.md` |
| Sample queries | SQL | `docs/database/queries.sql` |

## Quality Criteria

All schemas must meet these criteria:

| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Primary keys | All tables have PK | Schema inspection |
| Foreign keys | Referential integrity | Constraint check |
| Index coverage | FK cols + query patterns | EXPLAIN ANALYZE |
| Type appropriateness | No VARCHAR(MAX) abuse | Schema review |
| Constraint coverage | Business rules enforced | Insert tests |
| Migration reversibility | Up and down work | Rollback test |
| Model validation | Pydantic validators | Unit tests |

## SQLModel Best Practices

### Model Structure

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class TaskBase(SQLModel):
    """Shared fields for create/read schemas."""
    title: str = Field(max_length=200)
    description: str = Field(default="")

class Task(TaskBase, table=True):
    """Database model with table=True."""
    __tablename__ = "tasks"
    id: str = Field(primary_key=True, max_length=6)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    """Schema for POST request body."""
    pass

class TaskRead(TaskBase):
    """Schema for response body."""
    id: str
    created_at: datetime

class TaskUpdate(SQLModel):
    """Schema for PATCH - all optional."""
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
```

### Relationship Patterns

```python
from sqlmodel import Relationship

class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.id")
    user: Optional["User"] = Relationship(back_populates="tasks")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Enum already exists | Use `checkfirst=True` in migration |
| Index not used | Check column order in composite index |
| Slow JSONB query | Add GIN index, use `@>` operator |
| Migration conflict | Rebase, regenerate revision ID |
| FK constraint fails | Check insert order, use CASCADE |

## Related Skills

- `migration-expert` - Phase I to Phase II migration
- `api-design` - RESTful endpoint design
- `query-optimization` - Advanced query tuning
