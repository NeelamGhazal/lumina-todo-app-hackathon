---
title: Lumina Chatbot
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# Lumina Chatbot API

AI-powered todo assistant chatbot using OpenRouter (GPT-4o-mini) with MCP tool integration.

## This is an API-only backend

- **API Base URL**: `https://neelumghazal-lumina-chatbot.hf.space`
- **Docs/Swagger**: `https://neelumghazal-lumina-chatbot.hf.space/docs`
- **Health Check**: `https://neelumghazal-lumina-chatbot.hf.space/health`

⚠️ Visiting the root URL (`/`) returns API status info.
This is NORMAL for API-only backends.

The frontend is deployed separately on Vercel: https://lumina-todo.vercel.app

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/docs` | GET | OpenAPI documentation |
| `/api/chat` | POST | Send chat message |
| `/mcp/tools` | GET | List available MCP tools |

## Environment Variables

Set in HF Space Settings:
- `OPENROUTER_API_KEY` - OpenRouter API key (required)
- `AGENT_MODEL` - Model to use (default: gpt-4o-mini)
- `CORS_ORIGINS` - Allowed CORS origins

## Features

- Natural language task management
- Automatic date/time parsing ("tomorrow", "9 AM")
- Category detection (shopping, work, health)
- Duplicate task prevention
- Smart defaults for missing fields
