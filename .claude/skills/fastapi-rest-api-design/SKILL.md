# FastAPI REST API Design Skill

> Design production-ready RESTful APIs with FastAPI, following industry best practices

## Metadata

| Field | Value |
|-------|-------|
| **Skill Name** | fastapi-rest-api-design |
| **Version** | 1.0.0 |
| **Agent** | api-architect |
| **Category** | API Design |
| **Framework** | FastAPI with Pydantic v2 |

## Description

A systematic process for designing production-ready RESTful APIs using FastAPI. This skill covers resource identification, endpoint design, model creation, authentication, error handling, and OpenAPI documentation generation following industry best practices.

## When to Use

| Scenario | Applicable |
|----------|------------|
| Creating new API endpoints | Yes |
| Structuring route organization | Yes |
| Defining request/response models | Yes |
| Implementing JWT authentication | Yes |
| Adding error handling patterns | Yes |
| Generating OpenAPI documentation | Yes |
| Database schema design | No (use postgres-schema-design) |
| Frontend development | No |

## Prerequisites

Before executing this skill:

- [ ] Domain entities are defined (from data-model or Phase I)
- [ ] Operations are identified (CRUD + special actions)
- [ ] Authentication requirements are known
- [ ] Tech stack confirmed (FastAPI, Pydantic v2)

## Process Steps

### Step 1: Resource Identification

**Goal**: List all resources (nouns) and their operations

**Actions**:
1. Extract domain entities from spec/data model
2. Identify CRUD operations for each entity
3. Identify special actions (complete, archive, etc.)
4. Note relationships between resources
5. Determine access control requirements

**Output**: Resource operation matrix

```markdown
## Resources and Operations

| Resource | Create | Read | Update | Delete | Special Actions |
|----------|--------|------|--------|--------|-----------------|
| tasks | POST | GET | PUT | DELETE | complete, search |
| users | POST | GET | PUT | DELETE | - |
| stats | - | GET | - | - | - |

### Access Control
| Resource | Public | Authenticated | Owner Only |
|----------|--------|---------------|------------|
| tasks | - | list | CRUD |
| users | register | profile | update self |
| stats | - | own stats | - |

### Relationships
- User has many Tasks (1:N)
- Task belongs to User (ownership)
```

---

### Step 2: Endpoint Design

**Goal**: Map CRUD operations to HTTP methods and URLs

**Actions**:
1. Define URL structure for each resource
2. Select appropriate HTTP methods
3. Determine query parameters for filtering
4. Design action endpoints for non-CRUD
5. Document expected status codes

**Output**: Endpoint specification table

```markdown
## Endpoint Specification

### Authentication Endpoints
| Method | Endpoint | Description | Request | Response | Codes |
|--------|----------|-------------|---------|----------|-------|
| POST | /api/auth/register | Create account | UserCreate | UserRead | 201, 409 |
| POST | /api/auth/login | Get tokens | OAuth2Form | Token | 200, 401 |
| POST | /api/auth/refresh | Refresh token | RefreshToken | Token | 200, 401 |

### Task Endpoints (Protected)
| Method | Endpoint | Description | Request | Response | Codes |
|--------|----------|-------------|---------|----------|-------|
| GET | /api/tasks | List user's tasks | Query params | TaskList | 200 |
| POST | /api/tasks | Create task | TaskCreate | TaskRead | 201 |
| GET | /api/tasks/{id} | Get task by ID | - | TaskRead | 200, 404 |
| PUT | /api/tasks/{id} | Update task | TaskUpdate | TaskRead | 200, 404 |
| DELETE | /api/tasks/{id} | Delete task | - | - | 204, 404 |
| PATCH | /api/tasks/{id}/complete | Toggle status | - | TaskRead | 200, 404 |
| GET | /api/tasks/search | Search tasks | ?q=query | TaskList | 200 |

### Stats Endpoints (Protected)
| Method | Endpoint | Description | Request | Response | Codes |
|--------|----------|-------------|---------|----------|-------|
| GET | /api/stats | Get statistics | - | StatsRead | 200 |

### Query Parameters
| Endpoint | Parameter | Type | Description |
|----------|-----------|------|-------------|
| GET /tasks | status | string | Filter: pending/completed |
| GET /tasks | priority | string | Filter: high/medium/low |
| GET /tasks | category | string | Filter by category |
| GET /tasks | limit | int | Pagination limit (1-100) |
| GET /tasks | offset | int | Pagination offset |
| GET /tasks | sort | string | Sort field (-created_at) |
| GET /tasks/search | q | string | Search query (required) |
```

---

### Step 3: Model Creation

**Goal**: Define Pydantic models for validation and serialization

**Actions**:
1. Create Base model with shared fields
2. Create Create model for POST requests
3. Create Update model with optional fields
4. Create Read model for responses
5. Create List model for collections
6. Add field constraints and examples

**Output**: Pydantic model definitions

```python
## Pydantic Models

### Task Models

from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    SHOPPING = "shopping"
    HEALTH = "health"
    OTHER = "other"


class TaskBase(BaseModel):
    """Shared fields for task schemas."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title",
        json_schema_extra={"examples": ["Buy groceries"]}
    )
    description: str = Field(
        default="",
        max_length=2000,
        description="Detailed task description"
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Task priority level"
    )
    category: Category = Field(
        default=Category.OTHER,
        description="Task category"
    )
    tags: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Custom tags"
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Due date (YYYY-MM-DD)"
    )
    due_time: Optional[time] = Field(
        default=None,
        description="Due time (HH:MM)"
    )


class TaskCreate(TaskBase):
    """Request body for creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Request body for updating a task.
    All fields optional - only provided fields are updated.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[Priority] = None
    category: Optional[Category] = None
    tags: Optional[list[str]] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    is_completed: Optional[bool] = None


class TaskRead(TaskBase):
    """Response model for a single task."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Unique task identifier")
    is_completed: bool = Field(description="Completion status")
    created_at: datetime = Field(description="Creation timestamp")
    user_id: int = Field(description="Owner user ID")


class TaskList(BaseModel):
    """Paginated list of tasks."""
    tasks: list[TaskRead] = Field(description="List of tasks")
    total: int = Field(description="Total matching tasks")
    limit: int = Field(description="Page size")
    offset: int = Field(description="Current offset")


### User Models

class UserBase(BaseModel):
    """Shared user fields."""
    email: str = Field(
        ...,
        description="User email address",
        json_schema_extra={"examples": ["user@example.com"]}
    )


class UserCreate(UserBase):
    """Request body for user registration."""
    password: str = Field(
        ...,
        min_length=8,
        description="Password (min 8 characters)"
    )


class UserRead(UserBase):
    """Response model for user."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


### Token Models

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token payload."""
    user_id: Optional[int] = None


### Stats Models

class StatsRead(BaseModel):
    """Statistics dashboard response."""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float
    by_priority: dict[str, int]
    by_category: dict[str, int]
```

---

### Step 4: Route Organization

**Goal**: Group related endpoints in logical routers

**Actions**:
1. Create router per resource domain
2. Apply path prefixes and tags
3. Define shared dependencies
4. Configure route order (specific before generic)
5. Register routers with app

**Output**: Router structure

```python
## Router Organization

### File: src/api/routes/tasks.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated
from sqlmodel import Session

from src.api.dependencies import get_db, get_current_user
from src.models.user import User
from src.schemas.task import TaskCreate, TaskRead, TaskUpdate, TaskList

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses={401: {"description": "Not authenticated"}},
)

# Type aliases
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=TaskList, summary="List tasks")
async def list_tasks(
    db: DbSession,
    user: CurrentUser,
    status: str | None = Query(None, enum=["pending", "completed"]),
    priority: str | None = Query(None, enum=["high", "medium", "low"]),
    category: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("-created_at", regex="^-?(created_at|due_date|priority)$"),
):
    """
    Retrieve all tasks for the authenticated user.

    Supports filtering by status, priority, and category.
    Results are paginated with configurable limit and offset.
    """
    pass


@router.get("/search", response_model=TaskList, summary="Search tasks")
async def search_tasks(
    db: DbSession,
    user: CurrentUser,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Search tasks by keyword.

    Searches in title, description, and tags.
    """
    pass


@router.get("/{task_id}", response_model=TaskRead, summary="Get task")
async def get_task(task_id: str, db: DbSession, user: CurrentUser):
    """Retrieve a specific task by ID."""
    pass


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create task"
)
async def create_task(
    task_in: TaskCreate,
    db: DbSession,
    user: CurrentUser,
):
    """Create a new task for the authenticated user."""
    pass


@router.put("/{task_id}", response_model=TaskRead, summary="Update task")
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: DbSession,
    user: CurrentUser,
):
    """Update an existing task."""
    pass


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task"
)
async def delete_task(task_id: str, db: DbSession, user: CurrentUser):
    """Delete a task permanently."""
    pass


@router.patch(
    "/{task_id}/complete",
    response_model=TaskRead,
    summary="Toggle completion"
)
async def toggle_complete(task_id: str, db: DbSession, user: CurrentUser):
    """Toggle the completion status of a task."""
    pass


### File: src/api/routes/__init__.py

from fastapi import APIRouter
from src.api.routes import auth, tasks, stats

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(tasks.router)
api_router.include_router(stats.router)


### File: src/main.py

from fastapi import FastAPI
from src.api.routes import api_router
from src.api.errors import register_error_handlers

app = FastAPI(
    title="Todo API",
    description="RESTful API for task management",
    version="1.0.0",
)

register_error_handlers(app)
app.include_router(api_router)
```

---

### Step 5: Middleware Setup

**Goal**: Add JWT verification, CORS, and other middleware

**Actions**:
1. Configure CORS for frontend origins
2. Implement JWT token verification
3. Create authentication dependency
4. Add request logging middleware
5. Configure rate limiting (if needed)

**Output**: Middleware configuration

```python
## Middleware Setup

### File: src/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()


### File: src/core/security.py

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: int) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


### File: src/api/dependencies.py

from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from src.core.security import decode_token
from src.db.session import engine
from src.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception

    return user


### File: src/main.py (CORS setup)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.routes import api_router

app = FastAPI(title="Todo API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
```

---

### Step 6: Error Handling

**Goal**: Standardize error responses across API

**Actions**:
1. Define standard error response format
2. Create custom exception classes
3. Register global exception handlers
4. Map domain errors to HTTP status codes
5. Ensure consistent error messages

**Output**: Error handling utilities

```python
## Error Handling

### File: src/api/errors.py

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response format."""
    detail: str


class NotFoundError(Exception):
    """Resource not found."""
    def __init__(self, resource: str, id: str):
        self.resource = resource
        self.id = id
        self.message = f"{resource} with id '{id}' not found"


class ConflictError(Exception):
    """Resource already exists."""
    def __init__(self, message: str):
        self.message = message


class ForbiddenError(Exception):
    """Access denied."""
    def __init__(self, message: str = "Access denied"):
        self.message = message


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"][1:])
            errors.append(f"{field}: {error['msg']}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "; ".join(errors)},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(
        request: Request, exc: NotFoundError
    ) -> JSONResponse:
        """Handle not found errors."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(
        request: Request, exc: ConflictError
    ) -> JSONResponse:
        """Handle conflict errors."""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(
        request: Request, exc: ForbiddenError
    ) -> JSONResponse:
        """Handle forbidden errors."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def general_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected errors."""
        # Log the full exception here
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


### Usage in routes

from src.api.errors import NotFoundError, ForbiddenError

@router.get("/{task_id}")
async def get_task(task_id: str, db: DbSession, user: CurrentUser):
    task = db.get(Task, task_id)
    if not task:
        raise NotFoundError("Task", task_id)
    if task.user_id != user.id:
        raise ForbiddenError("You don't have access to this task")
    return task
```

---

### Step 7: Documentation

**Goal**: Generate comprehensive OpenAPI specifications

**Actions**:
1. Add descriptions to all endpoints
2. Include request/response examples
3. Document error responses
4. Add tags for grouping
5. Configure OpenAPI metadata

**Output**: OpenAPI configuration and examples

```python
## OpenAPI Documentation

### File: src/main.py

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Todo API",
    description="""
## Task Management API

RESTful API for managing personal tasks with the following features:

- **Authentication**: JWT-based authentication with access and refresh tokens
- **Tasks**: Full CRUD operations for task management
- **Search**: Full-text search across task fields
- **Statistics**: Dashboard statistics for task completion

### Authentication

All task endpoints require authentication. Include the JWT token in the
Authorization header:

```
Authorization: Bearer <access_token>
```

### Rate Limiting

API requests are limited to 100 requests per minute per user.
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Authentication and authorization endpoints",
        },
        {
            "name": "Tasks",
            "description": "Task management operations",
        },
        {
            "name": "Stats",
            "description": "Statistics and analytics",
        },
    ],
)


### Endpoint documentation example

@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="""
Create a new task for the authenticated user.

The task will be assigned a unique 6-character ID and the creation
timestamp will be set automatically.

**Required fields:**
- `title`: Task title (1-200 characters)

**Optional fields:**
- `description`: Detailed description (max 2000 chars)
- `priority`: high, medium (default), or low
- `category`: work, personal, shopping, health, or other (default)
- `tags`: List of custom tags (max 10)
- `due_date`: Target completion date (YYYY-MM-DD)
- `due_time`: Target completion time (HH:MM)
    """,
    responses={
        201: {
            "description": "Task created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "abc123",
                        "title": "Buy groceries",
                        "description": "Milk, bread, eggs",
                        "priority": "medium",
                        "category": "shopping",
                        "tags": ["food"],
                        "due_date": "2025-01-28",
                        "due_time": "14:00",
                        "is_completed": False,
                        "created_at": "2025-01-27T10:30:00Z",
                        "user_id": 1
                    }
                }
            }
        },
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error"},
    },
)
async def create_task(task_in: TaskCreate, db: DbSession, user: CurrentUser):
    pass
```

---

## Output Artifacts

| Artifact | Format | Location |
|----------|--------|----------|
| Router files | Python | `src/api/routes/` |
| Pydantic schemas | Python | `src/schemas/` |
| Middleware config | Python | `src/core/` |
| Error handlers | Python | `src/api/errors.py` |
| OpenAPI spec | JSON/YAML | `/openapi.json` |
| API examples | Markdown | `docs/api/` |

## Quality Criteria

All APIs must meet these criteria:

| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| REST compliance | Resources + HTTP methods | Manual review |
| Consistent responses | Same format everywhere | Schema tests |
| Proper status codes | Semantically correct | Integration tests |
| Input validation | Pydantic on all inputs | Unit tests |
| JWT protection | All protected routes | Auth tests |
| Error messages | Clear and actionable | Manual review |
| OpenAPI docs | Auto-generated, complete | /docs endpoint |

## Testing Checklist

```markdown
## API Test Checklist

### Authentication
- [ ] Register with valid data → 201
- [ ] Register duplicate email → 409
- [ ] Login with valid credentials → 200 + tokens
- [ ] Login with invalid password → 401
- [ ] Access protected route without token → 401
- [ ] Access protected route with expired token → 401
- [ ] Refresh token → 200 + new tokens

### Tasks CRUD
- [ ] Create task → 201 + task object
- [ ] Create task without title → 422
- [ ] Create task with title too long → 422
- [ ] List tasks → 200 + paginated list
- [ ] List tasks with filters → filtered results
- [ ] Get task by ID → 200 + task
- [ ] Get non-existent task → 404
- [ ] Get another user's task → 403 or 404
- [ ] Update task → 200 + updated task
- [ ] Update with invalid data → 422
- [ ] Delete task → 204
- [ ] Delete non-existent task → 404

### Search & Stats
- [ ] Search with query → matching results
- [ ] Search empty query → 422
- [ ] Get stats → 200 + statistics
```

## Related Skills

- `postgres-schema-design` - Database schema for API
- `migration-expert` - CLI to API migration
- `frontend-integration` - Connecting frontend to API
