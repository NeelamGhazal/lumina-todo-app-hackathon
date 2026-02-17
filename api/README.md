---
title: Lumina Todo API
emoji: ✅
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

# Lumina Todo API

FastAPI backend for the Lumina Todo application.

## Features

- RESTful API for task management
- JWT-based authentication
- Password reset via email (Resend)
- SQLite database (development) / PostgreSQL (production)
- CORS configured for Vercel frontend

## API Endpoints

### Health
- `GET /api/health` - Health check

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Password Reset
- `POST /api/auth/forgot-password` - Request password reset email
- `GET /api/auth/verify-reset-token/{token}` - Verify reset token validity
- `POST /api/auth/reset-password` - Reset password with valid token

### Tasks
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

## Environment Variables

Set these in HF Spaces Settings → Variables:

### Required
- `DATABASE_URL` - Database connection string (default: `sqlite+aiosqlite:///./data/evolution_todo.db`)
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `FRONTEND_URL` - Vercel frontend URL for CORS
- `ENVIRONMENT` - Set to `production`

### Password Reset (Optional)
- `RESEND_API_KEY` - Resend API key for sending emails
- `PASSWORD_RESET_FROM_EMAIL` - Sender email address (default: `noreply@lumina-todo.com`)
- `PASSWORD_RESET_TOKEN_EXPIRY_MINUTES` - Token expiry time (default: `15`)
- `PASSWORD_RESET_MAX_REQUESTS_PER_HOUR` - Rate limit (default: `3`)

## Local Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
