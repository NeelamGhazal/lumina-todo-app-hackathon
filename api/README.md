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
- SQLite database (development) / PostgreSQL (production)
- CORS configured for Vercel frontend

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

## Environment Variables

Set these in HF Spaces Settings → Variables:

- `DATABASE_URL` - Database connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `FRONTEND_URL` - Vercel frontend URL for CORS
- `ENVIRONMENT` - Set to `production`

## Local Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
