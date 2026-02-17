"""Task routes."""

from datetime import UTC, datetime, date, time
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.core.deps import CurrentUser, DbSession
from app.models.notification import Notification, NotificationType
from app.models.task import Task, TaskCategory, TaskPriority
from app.services.notification_service import create_notification
from app.schemas.task import (
    CreateTaskRequest,
    CreateTaskResponse,
    DeleteTaskResponse,
    ListTasksResponse,
    TaskCounts,
    TaskResponse,
    ToggleCompleteResponse,
    UpdateTaskRequest,
    UpdateTaskResponse,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def task_to_response(task: Task) -> TaskResponse:
    """Convert Task model to response schema."""
    return TaskResponse(
        id=str(task.id),
        userId=str(task.user_id),
        title=task.title,
        description=task.description,
        priority=task.priority,
        category=task.category,
        tags=task.tags,
        dueDate=task.due_date.isoformat() if task.due_date else None,
        dueTime=task.due_time.strftime("%H:%M") if task.due_time else None,
        completed=task.completed,
        completedAt=task.completed_at.isoformat() if task.completed_at else None,
        createdAt=task.created_at.isoformat(),
        updatedAt=task.updated_at.isoformat(),
    )


def parse_date(date_str: str | None) -> date | None:
    """Parse ISO date string to date object."""
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None


def parse_time(time_str: str | None) -> time | None:
    """Parse time string (HH:MM) to time object."""
    if not time_str:
        return None
    try:
        parts = time_str.split(":")
        return time(hour=int(parts[0]), minute=int(parts[1]))
    except (ValueError, IndexError):
        return None


@router.get("", response_model=ListTasksResponse)
async def list_tasks(
    current_user: CurrentUser,
    session: DbSession,
    task_status: str | None = Query(None, alias="status"),
    category: TaskCategory | None = None,
    priority: TaskPriority | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100, alias="pageSize"),
) -> ListTasksResponse:
    """List all tasks for the authenticated user."""
    # Build query
    query = select(Task).where(Task.user_id == current_user.id)

    # Apply filters
    if task_status == "pending":
        query = query.where(Task.completed == False)  # noqa: E712
    elif task_status == "completed":
        query = query.where(Task.completed == True)  # noqa: E712

    if category:
        query = query.where(Task.category == category)
    if priority:
        query = query.where(Task.priority == priority)

    # Order by created_at desc
    query = query.order_by(Task.created_at.desc())

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await session.execute(query)
    tasks = result.scalars().all()

    # Get counts
    all_result = await session.execute(
        select(Task).where(Task.user_id == current_user.id)
    )
    all_tasks = all_result.scalars().all()
    counts = TaskCounts(
        all=len(all_tasks),
        pending=sum(1 for t in all_tasks if not t.completed),
        completed=sum(1 for t in all_tasks if t.completed),
    )

    return ListTasksResponse(
        tasks=[task_to_response(t) for t in tasks],
        counts=counts,
    )


@router.post("", response_model=CreateTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> CreateTaskResponse:
    """Create a new task."""
    task = Task(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        category=request.category,
        tags=request.tags,
        due_date=parse_date(request.dueDate),
        due_time=parse_time(request.dueTime),
    )
    session.add(task)
    await session.flush()
    await session.refresh(task)

    return CreateTaskResponse(task=task_to_response(task))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> TaskResponse:
    """Get a single task by ID."""
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "TASK_NOT_FOUND", "message": "Task not found"},
        )

    return task_to_response(task)


@router.put("/{task_id}", response_model=UpdateTaskResponse)
async def update_task(
    task_id: UUID,
    request: UpdateTaskRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> UpdateTaskResponse:
    """Update an existing task."""
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "TASK_NOT_FOUND", "message": "Task not found"},
        )

    # Update fields that were provided
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "dueDate":
            task.due_date = parse_date(value) if value else None
        elif field == "dueTime":
            task.due_time = parse_time(value) if value else None
        else:
            setattr(task, field if field != "tags" else "tags", value)

    task.updated_at = datetime.now(UTC)
    await session.flush()
    await session.refresh(task)

    return UpdateTaskResponse(task=task_to_response(task))


@router.delete("/{task_id}", response_model=DeleteTaskResponse)
async def delete_task(
    task_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> DeleteTaskResponse:
    """Delete a task."""
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "TASK_NOT_FOUND", "message": "Task not found"},
        )

    await session.delete(task)
    return DeleteTaskResponse(success=True, taskId=str(task_id))


@router.patch("/{task_id}/complete", response_model=ToggleCompleteResponse)
async def toggle_complete(
    task_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> ToggleCompleteResponse:
    """Toggle task completion status."""
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "TASK_NOT_FOUND", "message": "Task not found"},
        )

    was_completed = task.completed
    task.completed = not task.completed
    task.completed_at = datetime.now(UTC) if task.completed else None
    task.updated_at = datetime.now(UTC)
    await session.flush()
    await session.refresh(task)

    # Create completion notification when task is marked complete
    if task.completed:
        await create_notification(
            session=session,
            user_id=current_user.id,
            notification_type=NotificationType.TASK_COMPLETED,
            message=f"You completed: {task.title}",
            task_id=task.id,
        )
    # ISSUE 3 FIX: Delete completion notification when task is uncompleted
    elif was_completed:
        # Task was completed, now uncompleted - delete the completion notification
        result = await session.execute(
            select(Notification).where(
                Notification.task_id == task_id,
                Notification.type == NotificationType.TASK_COMPLETED,
                Notification.user_id == current_user.id,
            )
        )
        completion_notification = result.scalar_one_or_none()
        if completion_notification:
            await session.delete(completion_notification)

    return ToggleCompleteResponse(task=task_to_response(task))
