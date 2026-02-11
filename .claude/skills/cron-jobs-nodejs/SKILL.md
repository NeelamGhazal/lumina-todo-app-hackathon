# Cron Jobs in Node.js

Production-ready background job scheduling with node-cron.

## Quick Setup

### Install

```bash
npm install node-cron
npm install -D @types/node-cron
```

### Basic Usage

```typescript
// src/lib/cron.ts
import cron from "node-cron";

// Run every minute
cron.schedule("* * * * *", () => {
  console.log("Running every minute");
});

// Run every hour at minute 0
cron.schedule("0 * * * *", () => {
  console.log("Running every hour");
});

// Run daily at midnight
cron.schedule("0 0 * * *", () => {
  console.log("Running at midnight");
});

// Run every Monday at 9 AM
cron.schedule("0 9 * * 1", () => {
  console.log("Running Monday 9 AM");
});
```

## Cron Expression Reference

```
┌──────────── minute (0-59)
│ ┌────────── hour (0-23)
│ │ ┌──────── day of month (1-31)
│ │ │ ┌────── month (1-12)
│ │ │ │ ┌──── day of week (0-7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * *
```

### Common Patterns

| Expression | Description |
|------------|-------------|
| `* * * * *` | Every minute |
| `*/5 * * * *` | Every 5 minutes |
| `0 * * * *` | Every hour |
| `0 */2 * * *` | Every 2 hours |
| `0 0 * * *` | Daily at midnight |
| `0 9 * * *` | Daily at 9 AM |
| `0 0 * * 0` | Weekly on Sunday |
| `0 0 1 * *` | Monthly on 1st |
| `0 9 * * 1-5` | Weekdays at 9 AM |

---

## Production Architecture

### Job Registry Pattern

```typescript
// src/jobs/index.ts
import cron, { ScheduledTask } from "node-cron";

interface Job {
  name: string;
  schedule: string;
  handler: () => Promise<void>;
  enabled: boolean;
}

const jobs: Job[] = [
  {
    name: "cleanup-expired-sessions",
    schedule: "0 */6 * * *", // Every 6 hours
    handler: cleanupExpiredSessions,
    enabled: true,
  },
  {
    name: "send-daily-digest",
    schedule: "0 9 * * *", // Daily 9 AM
    handler: sendDailyDigest,
    enabled: process.env.ENABLE_DIGEST === "true",
  },
  {
    name: "sync-external-data",
    schedule: "*/15 * * * *", // Every 15 minutes
    handler: syncExternalData,
    enabled: true,
  },
];

const scheduledTasks: Map<string, ScheduledTask> = new Map();

export function startAllJobs() {
  for (const job of jobs) {
    if (!job.enabled) {
      console.log(`Job "${job.name}" is disabled`);
      continue;
    }

    const task = cron.schedule(job.schedule, async () => {
      await runJob(job);
    });

    scheduledTasks.set(job.name, task);
    console.log(`Scheduled job "${job.name}" with pattern "${job.schedule}"`);
  }
}

export function stopAllJobs() {
  for (const [name, task] of scheduledTasks) {
    task.stop();
    console.log(`Stopped job "${name}"`);
  }
  scheduledTasks.clear();
}
```

### Async Job Execution with Error Handling

```typescript
// src/jobs/runner.ts
async function runJob(job: Job) {
  const startTime = Date.now();
  const jobId = `${job.name}-${Date.now()}`;

  console.log(`[${jobId}] Starting job "${job.name}"`);

  try {
    await job.handler();

    const duration = Date.now() - startTime;
    console.log(`[${jobId}] Completed in ${duration}ms`);

    // Log to monitoring
    await logJobSuccess(job.name, duration);
  } catch (error) {
    const duration = Date.now() - startTime;
    console.error(`[${jobId}] Failed after ${duration}ms:`, error);

    // Log to error tracking (Sentry, etc.)
    await logJobFailure(job.name, error, duration);
  }
}
```

---

## Preventing Duplicate Executions

### Lock-based Approach

```typescript
// src/jobs/lock.ts
const runningJobs = new Set<string>();

export async function withJobLock<T>(
  jobName: string,
  fn: () => Promise<T>
): Promise<T | null> {
  if (runningJobs.has(jobName)) {
    console.log(`Job "${jobName}" is already running, skipping`);
    return null;
  }

  runningJobs.add(jobName);

  try {
    return await fn();
  } finally {
    runningJobs.delete(jobName);
  }
}

// Usage
cron.schedule("* * * * *", async () => {
  await withJobLock("my-job", async () => {
    // Long-running task that shouldn't overlap
    await processLargeDataset();
  });
});
```

### Redis-based Distributed Lock (Multi-instance)

```typescript
// src/jobs/distributed-lock.ts
import Redis from "ioredis";

const redis = new Redis(process.env.REDIS_URL);

export async function withDistributedLock<T>(
  lockKey: string,
  ttlSeconds: number,
  fn: () => Promise<T>
): Promise<T | null> {
  const lockValue = `${process.pid}-${Date.now()}`;

  // Try to acquire lock
  const acquired = await redis.set(
    `lock:${lockKey}`,
    lockValue,
    "EX",
    ttlSeconds,
    "NX"
  );

  if (!acquired) {
    console.log(`Could not acquire lock for "${lockKey}"`);
    return null;
  }

  try {
    return await fn();
  } finally {
    // Release lock only if we still own it
    const currentValue = await redis.get(`lock:${lockKey}`);
    if (currentValue === lockValue) {
      await redis.del(`lock:${lockKey}`);
    }
  }
}
```

---

## Job Examples

### Cleanup Job

```typescript
// src/jobs/handlers/cleanup.ts
export async function cleanupExpiredSessions() {
  const cutoff = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000); // 7 days ago

  const result = await db.session.deleteMany({
    where: {
      expiresAt: { lt: cutoff },
    },
  });

  console.log(`Deleted ${result.count} expired sessions`);
}
```

### Notification Job

```typescript
// src/jobs/handlers/notifications.ts
export async function sendDailyDigest() {
  const users = await db.user.findMany({
    where: { digestEnabled: true },
    include: { tasks: { where: { dueDate: { gte: new Date() } } } },
  });

  for (const user of users) {
    if (user.tasks.length === 0) continue;

    await sendEmail({
      to: user.email,
      subject: "Your Daily Task Digest",
      html: renderDigestEmail(user.tasks),
    });

    // Rate limit: 10 emails/second
    await sleep(100);
  }

  console.log(`Sent digest to ${users.length} users`);
}
```

### Data Sync Job

```typescript
// src/jobs/handlers/sync.ts
export async function syncExternalData() {
  await withJobLock("sync-external-data", async () => {
    const lastSync = await getLastSyncTimestamp();

    const updates = await fetchExternalAPI({
      since: lastSync,
    });

    for (const update of updates) {
      await db.externalData.upsert({
        where: { externalId: update.id },
        update: update,
        create: update,
      });
    }

    await setLastSyncTimestamp(new Date());
    console.log(`Synced ${updates.length} records`);
  });
}
```

---

## Integration with Next.js

### Standalone Worker Process (Recommended)

```typescript
// src/worker.ts
import { startAllJobs, stopAllJobs } from "./jobs";

console.log("Starting worker process...");
startAllJobs();

// Graceful shutdown
process.on("SIGTERM", () => {
  console.log("Received SIGTERM, stopping jobs...");
  stopAllJobs();
  process.exit(0);
});

process.on("SIGINT", () => {
  console.log("Received SIGINT, stopping jobs...");
  stopAllJobs();
  process.exit(0);
});
```

```json
// package.json
{
  "scripts": {
    "worker": "ts-node src/worker.ts",
    "worker:prod": "node dist/worker.js"
  }
}
```

### API Route Trigger (Simple)

```typescript
// src/app/api/cron/daily/route.ts
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  // Verify cron secret (Vercel Cron, GitHub Actions, etc.)
  const authHeader = request.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    await runDailyTasks();
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: "Job failed" }, { status: 500 });
  }
}
```

---

## Common Mistakes & Solutions

### 1. Jobs Running Multiple Times (Multi-instance)

**Problem:** Multiple server instances each run the same cron job.

**Fix:** Use distributed locking (Redis) or single worker process.

### 2. Long Jobs Overlapping

**Problem:** Job takes longer than interval, causing overlaps.

**Fix:** Use job locks:
```typescript
await withJobLock("my-job", async () => { /* ... */ });
```

### 3. Timezone Issues

**Problem:** Jobs run at wrong time.

**Fix:** Specify timezone:
```typescript
cron.schedule("0 9 * * *", handler, {
  timezone: "America/New_York",
});
```

### 4. Memory Leaks

**Problem:** Jobs accumulate data in memory.

**Fix:** Process in batches:
```typescript
async function processLargeDataset() {
  const BATCH_SIZE = 100;
  let offset = 0;

  while (true) {
    const batch = await db.items.findMany({
      take: BATCH_SIZE,
      skip: offset,
    });

    if (batch.length === 0) break;

    await processBatch(batch);
    offset += BATCH_SIZE;
  }
}
```

### 5. Silent Failures

**Problem:** Jobs fail without notification.

**Fix:** Implement proper error handling and alerting:
```typescript
try {
  await job.handler();
} catch (error) {
  await sendAlert(`Job ${job.name} failed: ${error.message}`);
  throw error;
}
```

---

## Production Deployment

### Docker Compose

```yaml
# docker-compose.yml
services:
  web:
    build: .
    command: npm start

  worker:
    build: .
    command: npm run worker:prod
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:alpine
```

### Vercel Cron (Serverless)

```json
// vercel.json
{
  "crons": [
    {
      "path": "/api/cron/daily",
      "schedule": "0 9 * * *"
    },
    {
      "path": "/api/cron/cleanup",
      "schedule": "0 */6 * * *"
    }
  ]
}
```

---

## Production Checklist

- [ ] Distributed locking for multi-instance deployments
- [ ] Job overlap prevention
- [ ] Error handling and alerting
- [ ] Graceful shutdown handling
- [ ] Timezone explicitly configured
- [ ] Logging with job IDs for tracing
- [ ] Batch processing for large datasets
- [ ] Health check endpoint for worker
- [ ] Monitoring/metrics for job duration
- [ ] Retry logic for transient failures
