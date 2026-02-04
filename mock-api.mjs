/**
 * Mock API Server for Evolution Todo Frontend Development
 * Implements all endpoints expected by the frontend at localhost:8000/api
 * No external dependencies - uses Node.js built-in http module.
 *
 * Usage: node mock-api.mjs
 */

import { createServer } from "node:http";
import { randomUUID } from "node:crypto";

const PORT = 8000;
const FRONTEND_ORIGIN = "http://localhost:3000";

// =============================================================================
// In-Memory Data Store
// =============================================================================

const users = new Map();
const sessions = new Map(); // sessionToken -> userId
const tasks = new Map();

// Seed some demo data
const demoUserId = randomUUID();
users.set(demoUserId, {
  id: demoUserId,
  email: "demo@example.com",
  password: "password123",
  name: "Demo User",
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
});

const demoSessionToken = randomUUID();
sessions.set(demoSessionToken, demoUserId);

const seedTasks = [
  {
    title: "Design landing page mockups",
    description: "Create high-fidelity mockups for the new landing page using Figma. Include desktop and mobile variants.",
    priority: "high",
    category: "work",
    tags: ["design", "figma"],
    dueDate: "2026-02-05",
    dueTime: "17:00",
    completed: false,
  },
  {
    title: "Buy groceries",
    description: "Milk, eggs, bread, vegetables, and fruits for the week.",
    priority: "medium",
    category: "shopping",
    tags: ["weekly"],
    completed: false,
  },
  {
    title: "Morning run - 5K",
    description: "Run at the park. Track with fitness app.",
    priority: "low",
    category: "health",
    tags: ["exercise", "routine"],
    dueDate: "2026-01-29",
    dueTime: "07:00",
    completed: false,
  },
  {
    title: "Read chapter 5 of Clean Code",
    description: "Focus on formatting and code structure principles.",
    priority: "low",
    category: "personal",
    tags: ["reading", "learning"],
    completed: true,
    completedAt: new Date().toISOString(),
  },
  {
    title: "Fix authentication bug",
    description: "Users are getting logged out unexpectedly after 30 minutes. Investigate token refresh logic.",
    priority: "high",
    category: "work",
    tags: ["bug", "auth", "urgent"],
    dueDate: "2026-01-30",
    completed: false,
  },
  {
    title: "Schedule dentist appointment",
    priority: "medium",
    category: "health",
    tags: ["appointment"],
    completed: false,
  },
  {
    title: "Review pull request #142",
    description: "Code review for the new dashboard feature. Check for performance issues and test coverage.",
    priority: "medium",
    category: "work",
    tags: ["code-review"],
    dueDate: "2026-01-29",
    dueTime: "12:00",
    completed: true,
    completedAt: new Date().toISOString(),
  },
];

for (const seed of seedTasks) {
  const id = randomUUID();
  tasks.set(id, {
    id,
    userId: demoUserId,
    title: seed.title,
    description: seed.description,
    priority: seed.priority,
    category: seed.category,
    tags: seed.tags ?? [],
    dueDate: seed.dueDate,
    dueTime: seed.dueTime,
    completed: seed.completed,
    completedAt: seed.completedAt,
    createdAt: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString(),
    updatedAt: new Date().toISOString(),
  });
}

// =============================================================================
// Helpers
// =============================================================================

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch {
        reject(new Error("Invalid JSON"));
      }
    });
    req.on("error", reject);
  });
}

function json(res, status, data) {
  res.writeHead(status, {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": FRONTEND_ORIGIN,
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  });
  res.end(JSON.stringify(data));
}

function setCorsHeaders(res) {
  res.setHeader("Access-Control-Allow-Origin", FRONTEND_ORIGIN);
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
}

function parseCookies(req) {
  const cookies = {};
  const header = req.headers.cookie;
  if (header) {
    header.split(";").forEach((cookie) => {
      const [name, ...rest] = cookie.split("=");
      cookies[name.trim()] = rest.join("=").trim();
    });
  }
  return cookies;
}

function getSessionUser(req) {
  const cookies = parseCookies(req);
  const token = cookies["session_token"];
  if (!token) return null;
  const userId = sessions.get(token);
  if (!userId) return null;
  const user = users.get(userId);
  if (!user) return null;
  const { password: _, ...safeUser } = user;
  return safeUser;
}

function getUserTasks(userId) {
  return Array.from(tasks.values()).filter((t) => t.userId === userId);
}

function getTaskCounts(userId) {
  const userTasks = getUserTasks(userId);
  return {
    all: userTasks.length,
    pending: userTasks.filter((t) => !t.completed).length,
    completed: userTasks.filter((t) => t.completed).length,
  };
}

function matchRoute(pathname, pattern) {
  const patternParts = pattern.split("/");
  const pathParts = pathname.split("/");
  if (patternParts.length !== pathParts.length) return null;
  const params = {};
  for (let i = 0; i < patternParts.length; i++) {
    if (patternParts[i].startsWith(":")) {
      params[patternParts[i].slice(1)] = pathParts[i];
    } else if (patternParts[i] !== pathParts[i]) {
      return null;
    }
  }
  return params;
}

// =============================================================================
// Route Handlers
// =============================================================================

async function handleAuth(req, res, pathname, method) {
  // POST /api/auth/register
  if (pathname === "/api/auth/register" && method === "POST") {
    const body = await parseBody(req);
    const { email, password, name } = body;

    if (!email || !password) {
      return json(res, 422, { error: "VALIDATION_ERROR", message: "Email and password are required" });
    }

    const existing = Array.from(users.values()).find((u) => u.email === email);
    if (existing) {
      return json(res, 409, { error: "EMAIL_ALREADY_EXISTS", message: "Email already registered" });
    }

    const id = randomUUID();
    const user = { id, email, password, name, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
    users.set(id, user);

    const token = randomUUID();
    sessions.set(token, id);

    res.setHeader("Set-Cookie", `session_token=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400`);
    const { password: _, ...safeUser } = user;
    return json(res, 201, { user: safeUser, token });
  }

  // POST /api/auth/login
  if (pathname === "/api/auth/login" && method === "POST") {
    const body = await parseBody(req);
    const { email, password } = body;

    const user = Array.from(users.values()).find((u) => u.email === email && u.password === password);
    if (!user) {
      return json(res, 401, { error: "INVALID_CREDENTIALS", message: "Invalid email or password" });
    }

    const token = randomUUID();
    sessions.set(token, user.id);

    res.setHeader("Set-Cookie", `session_token=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400`);
    const { password: _, ...safeUser } = user;
    return json(res, 200, { user: safeUser, token });
  }

  // POST /api/auth/logout
  if (pathname === "/api/auth/logout" && method === "POST") {
    const cookies = parseCookies(req);
    const token = cookies["session_token"];
    if (token) sessions.delete(token);
    res.setHeader("Set-Cookie", "session_token=; Path=/; HttpOnly; Max-Age=0");
    return json(res, 200, { success: true });
  }

  // GET /api/auth/session
  if (pathname === "/api/auth/session" && method === "GET") {
    const user = getSessionUser(req);
    if (!user) {
      return json(res, 401, { error: "UNAUTHORIZED", message: "Not authenticated" });
    }
    return json(res, 200, { user, expiresAt: new Date(Date.now() + 86400000).toISOString() });
  }

  return null; // not handled
}

async function handleTasks(req, res, pathname, method) {
  const user = getSessionUser(req);
  if (!user) {
    return json(res, 401, { error: "UNAUTHORIZED", message: "Not authenticated" });
  }

  // GET /api/tasks
  if (pathname === "/api/tasks" && method === "GET") {
    const userTasks = getUserTasks(user.id);
    return json(res, 200, { tasks: userTasks, counts: getTaskCounts(user.id) });
  }

  // POST /api/tasks
  if (pathname === "/api/tasks" && method === "POST") {
    const body = await parseBody(req);
    const id = randomUUID();
    const now = new Date().toISOString();
    const task = {
      id,
      userId: user.id,
      title: body.title,
      description: body.description,
      priority: body.priority || "medium",
      category: body.category || "personal",
      tags: body.tags || [],
      dueDate: body.dueDate,
      dueTime: body.dueTime,
      completed: false,
      createdAt: now,
      updatedAt: now,
    };
    tasks.set(id, task);
    return json(res, 201, { task });
  }

  // GET /api/tasks/:id
  let params = matchRoute(pathname, "/api/tasks/:id");
  if (params && method === "GET" && !pathname.endsWith("/complete")) {
    const task = tasks.get(params.id);
    if (!task || task.userId !== user.id) {
      return json(res, 404, { error: "TASK_NOT_FOUND", message: "Task not found" });
    }
    return json(res, 200, { task });
  }

  // PUT /api/tasks/:id
  params = matchRoute(pathname, "/api/tasks/:id");
  if (params && method === "PUT") {
    const task = tasks.get(params.id);
    if (!task || task.userId !== user.id) {
      return json(res, 404, { error: "TASK_NOT_FOUND", message: "Task not found" });
    }
    const body = await parseBody(req);
    const updated = {
      ...task,
      ...body,
      // Convert null to undefined
      dueDate: body.dueDate === null ? undefined : (body.dueDate ?? task.dueDate),
      dueTime: body.dueTime === null ? undefined : (body.dueTime ?? task.dueTime),
      updatedAt: new Date().toISOString(),
    };
    tasks.set(params.id, updated);
    return json(res, 200, { task: updated });
  }

  // DELETE /api/tasks/:id
  params = matchRoute(pathname, "/api/tasks/:id");
  if (params && method === "DELETE") {
    const task = tasks.get(params.id);
    if (!task || task.userId !== user.id) {
      return json(res, 404, { error: "TASK_NOT_FOUND", message: "Task not found" });
    }
    tasks.delete(params.id);
    return json(res, 200, { success: true, taskId: params.id });
  }

  // PATCH /api/tasks/:id/complete
  params = matchRoute(pathname, "/api/tasks/:id/complete");
  if (params && method === "PATCH") {
    const task = tasks.get(params.id);
    if (!task || task.userId !== user.id) {
      return json(res, 404, { error: "TASK_NOT_FOUND", message: "Task not found" });
    }
    task.completed = !task.completed;
    task.completedAt = task.completed ? new Date().toISOString() : undefined;
    task.updatedAt = new Date().toISOString();
    tasks.set(params.id, task);
    return json(res, 200, { task });
  }

  return null;
}

// =============================================================================
// Server
// =============================================================================

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const pathname = url.pathname;
  const method = req.method;

  // CORS preflight
  if (method === "OPTIONS") {
    setCorsHeaders(res);
    res.writeHead(204);
    return res.end();
  }

  try {
    // Auth routes
    if (pathname.startsWith("/api/auth")) {
      const handled = await handleAuth(req, res, pathname, method);
      if (handled !== null) return;
    }

    // Task routes
    if (pathname.startsWith("/api/tasks")) {
      const handled = await handleTasks(req, res, pathname, method);
      if (handled !== null) return;
    }

    // Health check
    if (pathname === "/api/health") {
      return json(res, 200, { status: "ok", timestamp: new Date().toISOString() });
    }

    // 404
    json(res, 404, { error: "NOT_FOUND", message: `Route ${method} ${pathname} not found` });
  } catch (err) {
    console.error("Server error:", err);
    json(res, 500, { error: "INTERNAL_ERROR", message: "Internal server error" });
  }
});

server.listen(PORT, () => {
  console.log(`\n  Mock API Server running at http://localhost:${PORT}/api`);
  console.log(`  Health check: http://localhost:${PORT}/api/health\n`);
  console.log(`  Demo account: demo@example.com / password123`);
  console.log(`  ${seedTasks.length} seed tasks loaded\n`);
  console.log(`  Auto-authenticated session cookie set for demo user.`);
  console.log(`  To use: login via the frontend, or include the session cookie.\n`);
});
