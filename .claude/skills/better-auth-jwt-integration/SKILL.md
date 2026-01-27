# Better Auth + JWT Integration Skill

> Implement secure authentication with Better Auth (frontend) and JWT (backend) for stateless auth

## Metadata

| Field | Value |
|-------|-------|
| **Skill Name** | better-auth-jwt-integration |
| **Version** | 1.0.0 |
| **Agent** | auth-integration-expert |
| **Category** | Security / Authentication |
| **Stack** | Better Auth + FastAPI JWT |

## Description

A comprehensive process for implementing secure authentication using Better Auth for Next.js frontend session management and JWT tokens for FastAPI backend API authentication. This skill ensures stateless, secure authentication with proper token handling, cookie security, and protected route patterns.

## When to Use

| Scenario | Applicable |
|----------|------------|
| Setting up user authentication | Yes |
| Implementing login/signup flows | Yes |
| Creating protected API routes | Yes |
| Adding JWT verification middleware | Yes |
| Handling token refresh | Yes |
| OAuth/Social login | Partial (escalate) |
| Multi-factor authentication | No (escalate) |

## Prerequisites

Before executing this skill:

- [ ] Next.js 16+ app with App Router configured
- [ ] FastAPI backend with SQLModel/PostgreSQL
- [ ] User model defined in database schema
- [ ] Environment variables strategy defined
- [ ] HTTPS available (production)

## Process Steps

### Step 1: Better Auth Setup

**Goal**: Install and configure Better Auth in Next.js

**Actions**:
1. Install Better Auth package
2. Create auth configuration file
3. Set up API route handler
4. Create auth context provider
5. Configure session management

**Output**: Better Auth configuration

```bash
# Installation
npm install better-auth
```

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";

export const auth = betterAuth({
  // Base URL for auth callbacks
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",

  // Secret for signing sessions
  secret: process.env.BETTER_AUTH_SECRET!,

  // Email/password authentication
  emailAndPassword: {
    enabled: true,

    // Delegate to FastAPI backend
    async signIn({ email, password }) {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            username: email,
            password: password,
          }),
          credentials: "include", // Include cookies
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Invalid credentials");
      }

      const data = await response.json();
      return {
        user: {
          id: data.user_id,
          email: email,
        },
        token: data.access_token,
      };
    },

    async signUp({ email, password, name }) {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            password,
            name,
          }),
          credentials: "include",
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Registration failed");
      }

      const user = await response.json();
      return {
        user: {
          id: user.id,
          email: user.email,
        },
      };
    },
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // Cache for 5 minutes
    },
  },

  // Advanced configuration
  advanced: {
    cookiePrefix: "todo_auth",
    generateId: () => crypto.randomUUID(),
  },

  // Plugins
  plugins: [nextCookies()],
});

// Export typed client functions
export const { signIn, signUp, signOut, useSession, getSession } = auth;
```

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth.handler);
```

```typescript
// components/providers/auth-provider.tsx
"use client";

import { createContext, useContext, ReactNode } from "react";
import { useSession } from "@/lib/auth";

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, isPending, error } = useSession();

  const handleSignOut = async () => {
    // Clear backend cookies
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/logout`, {
      method: "POST",
      credentials: "include",
    });

    // Clear frontend session
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider
      value={{
        user: session?.user ?? null,
        isLoading: isPending,
        isAuthenticated: !!session?.user && !error,
        signOut: handleSignOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
```

```typescript
// app/layout.tsx
import { AuthProvider } from "@/components/providers/auth-provider";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
```

---

### Step 2: JWT Configuration

**Goal**: Set up FastAPI JWT utilities

**Actions**:
1. Install required packages
2. Create security configuration
3. Implement token creation functions
4. Implement token validation
5. Set up password hashing

**Output**: JWT security utilities

```bash
# Installation
pip install python-jose[cryptography] passlib[bcrypt]
```

```python
# src/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/tododb"

    # JWT Configuration
    JWT_SECRET_KEY: str  # Required, no default
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Better Auth (for CORS)
    BETTER_AUTH_URL: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

```python
# src/core/security.py
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.core.config import settings

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Secure default
)


class TokenPayload(BaseModel):
    """Decoded JWT token payload."""
    sub: str  # Subject (user_id as string)
    exp: datetime  # Expiration time
    iat: datetime  # Issued at
    type: str  # "access" or "refresh"


# =============================================================================
# Password Functions
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password for secure storage."""
    return pwd_context.hash(password)


# =============================================================================
# Token Functions
# =============================================================================

def create_token(
    subject: int | str,
    token_type: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT token.

    Args:
        subject: The user ID to encode in the token
        token_type: Either "access" or "refresh"
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    now = datetime.utcnow()

    if expires_delta:
        expire = now + expires_delta
    elif token_type == "access":
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:  # refresh
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": token_type,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(user_id: int) -> str:
    """Create an access token for a user."""
    return create_token(user_id, "access")


def create_refresh_token(user_id: int) -> str:
    """Create a refresh token for a user."""
    return create_token(user_id, "refresh")


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token string

    Returns:
        TokenPayload if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


def create_tokens(user_id: int) -> tuple[str, str]:
    """
    Create both access and refresh tokens.

    Args:
        user_id: The user's database ID

    Returns:
        Tuple of (access_token, refresh_token)
    """
    return (
        create_access_token(user_id),
        create_refresh_token(user_id),
    )
```

---

### Step 3: User Model

**Goal**: Create user table and SQLModel

**Actions**:
1. Define User SQLModel with required fields
2. Add password hash field (never expose)
3. Create user schemas for API
4. Set up database migration

**Output**: User model and schemas

```python
# src/models/user.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Index


class UserBase(SQLModel):
    """Shared user fields."""
    email: str = Field(
        sa_column=Column(String(255), unique=True, index=True, nullable=False)
    )
    name: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """User database model."""
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_email", "email"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (add when Task model exists)
    # tasks: list["Task"] = Relationship(back_populates="user")
```

```python
# src/schemas/user.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(description="User's email address")
    password: str = Field(
        min_length=8,
        description="Password (minimum 8 characters)"
    )
    name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's display name"
    )


class UserRead(BaseModel):
    """Schema for user response (never includes password)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: Optional[str] = None
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class UserInDB(UserRead):
    """User with hashed password (internal use only)."""
    hashed_password: str
```

```python
# src/schemas/token.py
from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token data."""
    user_id: Optional[int] = None
    token_type: Optional[str] = None


class RefreshRequest(BaseModel):
    """Refresh token request body (alternative to cookie)."""
    refresh_token: str
```

---

### Step 4: Registration Flow

**Goal**: Implement secure user registration

**Actions**:
1. Validate email uniqueness
2. Hash password securely
3. Create user record
4. Generate initial tokens
5. Set authentication cookies

**Output**: Registration endpoint

```python
# src/api/routes/auth.py (registration part)
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from src.api.dependencies import get_db
from src.core.security import hash_password, create_tokens
from src.core.config import settings
from src.models.user import User
from src.schemas.user import UserCreate, UserRead
from src.schemas.token import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    """Set secure authentication cookies."""
    is_production = settings.ENVIRONMENT == "production"

    # Access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    # Refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/auth",  # Only sent to auth endpoints
    )


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"},
    },
)
async def register(
    user_in: UserCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> User:
    """
    Register a new user account.

    - Validates email is not already registered
    - Hashes password securely with bcrypt
    - Creates user record in database
    - Sets authentication cookies for immediate login
    """
    # Check if email already exists
    existing_user = db.exec(
        select(User).where(User.email == user_in.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create new user with hashed password
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        name=user_in.name,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens and set cookies
    access_token, refresh_token = create_tokens(user.id)
    set_auth_cookies(response, access_token, refresh_token)

    return user
```

---

### Step 5: Login Flow

**Goal**: Authenticate user and generate JWT

**Actions**:
1. Validate credentials
2. Verify password hash
3. Generate access and refresh tokens
4. Set secure cookies
5. Return token response

**Output**: Login endpoint

```python
# src/api/routes/auth.py (login part)
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.core.security import verify_password


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    """
    Authenticate with email and password.

    - Validates credentials against database
    - Returns JWT access and refresh tokens
    - Sets httpOnly cookies for secure storage

    Note: Uses OAuth2 form format (username field contains email).
    """
    # Find user by email
    user = db.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    # Validate credentials (constant-time comparison via passlib)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
        )

    # Generate tokens
    access_token, refresh_token = create_tokens(user.id)

    # Set secure cookies
    set_auth_cookies(response, access_token, refresh_token)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
```

---

### Step 6: Middleware

**Goal**: Add JWT verification to FastAPI routes

**Actions**:
1. Create token extraction function
2. Implement user lookup dependency
3. Create optional auth dependency
4. Handle token errors gracefully
5. Export type aliases

**Output**: Authentication middleware

```python
# src/api/dependencies.py
from typing import Annotated, Generator, Optional

from fastapi import Depends, HTTPException, status, Cookie, Header
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from src.core.security import decode_token
from src.db.session import engine
from src.models.user import User

# OAuth2 scheme for Swagger UI documentation
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False,  # Don't raise exception, let us handle it
)


def get_db() -> Generator[Session, None, None]:
    """Database session dependency."""
    with Session(engine) as session:
        yield session


async def get_token(
    # Cookie (preferred, more secure)
    access_token_cookie: Optional[str] = Cookie(None, alias="access_token"),
    # Header (for API clients)
    authorization: Optional[str] = Header(None),
    # OAuth2 scheme (for Swagger UI)
    oauth2_token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[str]:
    """
    Extract JWT token from multiple sources.

    Priority:
    1. Cookie (httpOnly, most secure)
    2. Authorization header
    3. OAuth2 bearer token

    Returns:
        Token string or None
    """
    # Try cookie first (most secure)
    if access_token_cookie:
        return access_token_cookie

    # Try Authorization header
    if authorization:
        # Handle "Bearer <token>" format
        if authorization.startswith("Bearer "):
            return authorization[7:]
        return authorization

    # Try OAuth2 scheme (Swagger UI)
    if oauth2_token:
        return oauth2_token

    return None


async def get_current_user(
    token: Annotated[Optional[str], Depends(get_token)],
    db: Session = Depends(get_db),
) -> User:
    """
    Validate token and return current user.

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Check token exists
    if not token:
        raise credentials_exception

    # Decode and validate token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Verify token type
    if payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Use access token.",
        )

    # Get user from database
    try:
        user_id = int(payload.sub)
    except ValueError:
        raise credentials_exception

    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception

    # Check user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
        )

    return user


async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(get_token)],
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.

    Use for routes that work with or without authentication.
    """
    if not token:
        return None

    payload = decode_token(token)
    if payload is None or payload.type != "access":
        return None

    try:
        user_id = int(payload.sub)
    except ValueError:
        return None

    user = db.get(User, user_id)
    if user and user.is_active:
        return user

    return None


# Type aliases for cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[Optional[User], Depends(get_current_user_optional)]
DbSession = Annotated[Session, Depends(get_db)]
```

---

### Step 7: Protected Routes

**Goal**: Secure frontend and backend routes

**Actions**:
1. Use CurrentUser dependency on protected endpoints
2. Filter data by authenticated user
3. Create frontend auth guards
4. Handle unauthorized access

**Output**: Protected route examples

```python
# src/api/routes/tasks.py (protected routes)
from fastapi import APIRouter, status
from src.api.dependencies import CurrentUser, DbSession
from src.schemas.task import TaskCreate, TaskRead, TaskList

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=TaskList)
async def list_tasks(
    db: DbSession,
    user: CurrentUser,  # Requires authentication
    limit: int = 20,
    offset: int = 0,
):
    """
    List tasks for the authenticated user.

    Only returns tasks owned by the current user.
    """
    # Filter by user_id automatically
    tasks = db.exec(
        select(Task)
        .where(Task.user_id == user.id)
        .offset(offset)
        .limit(limit)
    ).all()

    total = db.exec(
        select(func.count(Task.id)).where(Task.user_id == user.id)
    ).one()

    return TaskList(tasks=tasks, total=total, limit=limit, offset=offset)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: DbSession,
    user: CurrentUser,  # Requires authentication
):
    """Create a new task for the authenticated user."""
    task = Task(
        **task_in.model_dump(),
        user_id=user.id,  # Associate with current user
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

```typescript
// middleware.ts (Next.js)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getSession } from "@/lib/auth";

// Routes that require authentication
const protectedRoutes = ["/dashboard", "/settings", "/tasks"];

// Routes that should redirect to dashboard if authenticated
const authRoutes = ["/login", "/register"];

export async function middleware(request: NextRequest) {
  const session = await getSession();
  const { pathname } = request.nextUrl;

  // Check if route is protected
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  );

  // Check if route is auth route
  const isAuthRoute = authRoutes.some((route) =>
    pathname.startsWith(route)
  );

  // Redirect unauthenticated users from protected routes
  if (isProtectedRoute && !session) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated users from auth routes
  if (isAuthRoute && session) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - api routes (handled separately)
     * - static files
     * - public assets
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
```

```typescript
// components/auth/protected-route.tsx
"use client";

import { useAuth } from "@/components/providers/auth-provider";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function ProtectedRoute({
  children,
  fallback = <div>Loading...</div>,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return fallback;
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
```

---

### Step 8: Testing

**Goal**: Verify authentication flows end-to-end

**Actions**:
1. Test registration flow
2. Test login with valid/invalid credentials
3. Test protected route access
4. Test token refresh
5. Test logout and cookie clearing

**Output**: Test suite

```python
# tests/api/test_auth.py
import pytest
from httpx import AsyncClient
from sqlmodel import Session

from src.models.user import User
from src.core.security import hash_password


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("password123"),
        name="Test User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestRegistration:
    """Test user registration."""

    async def test_register_success(self, client: AsyncClient):
        """Should register new user and set cookies."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "password": "securepassword",
                "name": "New User",
            },
        )

        assert response.status_code == 201
        assert response.json()["email"] == "new@example.com"
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user: User
    ):
        """Should reject duplicate email."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "password": "password123",
            },
        )

        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]

    async def test_register_weak_password(self, client: AsyncClient):
        """Should reject weak password."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "password": "short",  # Less than 8 chars
            },
        )

        assert response.status_code == 422


class TestLogin:
    """Test user login."""

    async def test_login_success(
        self, client: AsyncClient, test_user: User
    ):
        """Should authenticate and return tokens."""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "password123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_password(
        self, client: AsyncClient, test_user: User
    ):
        """Should reject invalid password."""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Should reject nonexistent user."""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "nobody@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401


class TestProtectedRoutes:
    """Test protected route access."""

    async def test_access_without_token(self, client: AsyncClient):
        """Should reject request without token."""
        response = await client.get("/api/tasks")

        assert response.status_code == 401

    async def test_access_with_valid_token(
        self, client: AsyncClient, test_user: User
    ):
        """Should allow request with valid token."""
        # Login first
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "password123",
            },
        )

        # Use cookies for next request
        response = await client.get("/api/tasks")

        assert response.status_code == 200

    async def test_access_with_expired_token(self, client: AsyncClient):
        """Should reject expired token."""
        # Create an expired token manually
        from src.core.security import create_token
        from datetime import timedelta

        expired_token = create_token(
            subject=1,
            token_type="access",
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        response = await client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401


class TestTokenRefresh:
    """Test token refresh flow."""

    async def test_refresh_success(
        self, client: AsyncClient, test_user: User
    ):
        """Should issue new tokens with valid refresh token."""
        # Login to get initial tokens
        await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "password123",
            },
        )

        # Refresh tokens
        response = await client.post("/api/auth/refresh")

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_without_token(self, client: AsyncClient):
        """Should reject refresh without token."""
        response = await client.post("/api/auth/refresh")

        assert response.status_code == 401
```

---

## Output Artifacts

| Artifact | Format | Location |
|----------|--------|----------|
| Better Auth config | TypeScript | `lib/auth.ts` |
| Auth provider | TSX | `components/providers/` |
| JWT utilities | Python | `src/core/security.py` |
| Auth routes | Python | `src/api/routes/auth.py` |
| Auth middleware | Python | `src/api/dependencies.py` |
| User model | Python | `src/models/user.py` |
| User schemas | Python | `src/schemas/user.py` |
| Token schemas | Python | `src/schemas/token.py` |
| Auth tests | Python | `tests/api/test_auth.py` |
| Environment template | Text | `.env.example` |

## Environment Variables

```bash
# .env.example

# =============================================================================
# JWT Configuration (REQUIRED)
# =============================================================================
# Generate with: openssl rand -hex 32
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# Better Auth Configuration (REQUIRED)
# =============================================================================
# Generate with: openssl rand -hex 32
BETTER_AUTH_SECRET=another-unique-secret-for-better-auth-sessions
BETTER_AUTH_URL=http://localhost:3000

# =============================================================================
# API Configuration
# =============================================================================
NEXT_PUBLIC_API_URL=http://localhost:8000

# =============================================================================
# Environment
# =============================================================================
ENVIRONMENT=development
```

## Quality Criteria

| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Password hashing | bcrypt 12+ rounds | Code review |
| Token storage | httpOnly cookies | Browser inspection |
| Token expiry | Access: 30min max | Configuration |
| CORS | Specific origins | Network inspection |
| Rate limiting | Login attempts limited | Load test |
| Error messages | No credential hints | Manual test |
| Cookie security | Secure flag in production | Network inspection |

## Security Checklist

```markdown
## Authentication Security Checklist

### Password Security
- [ ] Passwords hashed with bcrypt (12+ rounds)
- [ ] No password stored in plain text
- [ ] Password not included in any response
- [ ] Minimum password length enforced (8 chars)

### Token Security
- [ ] JWT signed with strong secret (32+ chars)
- [ ] Access token expires in 30 minutes or less
- [ ] Refresh token expires in 7 days or less
- [ ] Tokens stored in httpOnly cookies
- [ ] Secure flag set in production
- [ ] SameSite attribute set to "lax" or "strict"

### API Security
- [ ] All protected routes verify JWT
- [ ] Invalid tokens return 401
- [ ] Expired tokens return 401
- [ ] User data filtered by authenticated user
- [ ] No sensitive data in error messages

### CORS Security
- [ ] Specific origins configured (no wildcards in production)
- [ ] Credentials allowed only for specific origins
- [ ] Preflight requests handled

### Cookie Security
- [ ] httpOnly: true (prevent XSS)
- [ ] secure: true in production (HTTPS only)
- [ ] sameSite: "lax" or "strict" (CSRF protection)
- [ ] Appropriate max_age values
```

## Related Skills

- `api-architect` - API endpoint design
- `postgres-schema-design` - User model schema
- `migration-expert` - Adding auth to existing app
