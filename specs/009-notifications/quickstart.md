# Quickstart: In-App Notifications

**Feature**: 009-notifications | **Date**: 2026-02-12

## Prerequisites

1. Evolution-Todo project running locally
2. API server at `http://localhost:8000`
3. Frontend at `http://localhost:3000`
4. User account created and logged in

## API Testing

### 1. Get Notifications

```bash
# Get notifications (requires auth token)
curl -X GET http://localhost:8000/api/notifications \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json"
```

Expected response:
```json
{
  "notifications": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "userId": "123e4567-e89b-12d3-a456-426614174000",
      "taskId": "789e0123-e45b-67d8-a901-234567890abc",
      "type": "TASK_DUE_SOON",
      "message": "Task 'Finish report' is due tomorrow",
      "isRead": false,
      "createdAt": "2026-02-12T10:30:00Z"
    }
  ],
  "total": 1,
  "unreadCount": 1
}
```

### 2. Get Unread Count (Polling Endpoint)

```bash
curl -X GET http://localhost:8000/api/notifications/unread-count \
  -H "Authorization: Bearer <your-jwt-token>"
```

Expected response:
```json
{
  "count": 5
}
```

### 3. Mark Notification as Read

```bash
curl -X PATCH http://localhost:8000/api/notifications/{notification_id}/read \
  -H "Authorization: Bearer <your-jwt-token>"
```

Expected response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "type": "TASK_DUE_SOON",
  "message": "Task 'Finish report' is due tomorrow",
  "isRead": true,
  "createdAt": "2026-02-12T10:30:00Z"
}
```

### 4. Clear All Notifications

```bash
curl -X DELETE http://localhost:8000/api/notifications \
  -H "Authorization: Bearer <your-jwt-token>"
```

Expected response:
```json
{
  "success": true,
  "deleted_count": 15
}
```

## Testing Notification Generation

### Test Due-Soon Notifications

1. Create a task with due date = tomorrow:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test due-soon task",
    "dueDate": "2026-02-13"
  }'
```

2. Manually trigger the notification job (if endpoint exists):
```bash
curl -X POST http://localhost:8000/api/notifications/trigger-job \
  -H "Authorization: Bearer <your-jwt-token>"
```

3. Check notifications - should see "Task due soon" notification

### Test Overdue Notifications

1. Create a task with due date = yesterday:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test overdue task",
    "dueDate": "2026-02-11"
  }'
```

2. Trigger notification job
3. Check notifications - should see "Task overdue" notification

### Test Task Completed Notifications

1. Mark any task as complete:
```bash
curl -X PATCH http://localhost:8000/api/tasks/{task_id}/complete \
  -H "Authorization: Bearer <your-jwt-token>"
```

2. Check notifications - should see "Task completed" notification immediately

## Frontend Testing

### Bell Icon & Badge

1. Log in to the application
2. Verify bell icon appears in navbar header
3. If you have unread notifications, verify badge shows count
4. If count > 99, verify badge shows "99+"

### Notification Dropdown

1. Click the bell icon
2. Verify dropdown opens showing up to 20 notifications
3. Verify notifications are sorted newest first
4. Verify each notification shows:
   - Type indicator icon
   - Message text
   - Relative timestamp
   - Mark as read button (for unread)
5. Click outside dropdown - verify it closes

### Mark as Read

1. Open notification dropdown
2. Click mark-as-read on an unread notification
3. Verify notification styling changes (less bold)
4. Verify badge count decreases by 1

### Clear All

1. Open notification dropdown
2. Click "Clear all" button
3. Verify all notifications are removed
4. Verify empty state message appears
5. Verify badge disappears or shows 0

### Polling Verification

1. Keep the app open
2. In another terminal, manually create a notification via API
3. Wait up to 30 seconds
4. Verify badge count updates without page refresh

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No notifications appearing | Check cron job is running, verify task has due_date |
| Badge not updating | Check browser console for polling errors |
| Duplicate notifications | This is a bug - check duplicate prevention logic |
| Notifications not clearing | Check API response for errors |
| Polling too frequent | Verify 30-second interval in useNotifications hook |

## Development Tips

### View Scheduled Jobs

Check API logs for scheduler output:
```
Scheduled job "generate_task_notifications" with pattern "0 * * * *"
Scheduled job "cleanup_old_notifications" with pattern "0 0 * * *"
```

### Force Notification Generation

During development, you can reduce the cron interval or add a manual trigger endpoint.

### Check Database

```sql
-- View all notifications
SELECT * FROM notifications ORDER BY created_at DESC;

-- View unread count by user
SELECT user_id, COUNT(*) FROM notifications WHERE is_read = false GROUP BY user_id;

-- Check for duplicates
SELECT task_id, type, COUNT(*) FROM notifications
GROUP BY task_id, type HAVING COUNT(*) > 1;
```
