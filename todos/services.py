from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from django.db.models import QuerySet

from .exceptions import TodoNotFoundError, TodoValidationError
from .models import Priority, ToDoItem
from .serializers import ToDoItemSerializer


def get_todo_item(pk: int) -> ToDoItem:
    try:
        return ToDoItem.objects.get(pk=pk)
    except ToDoItem.DoesNotExist:
        raise TodoNotFoundError(pk)


def list_todo_items(
    *,
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    overdue_only: bool = False,
) -> List[ToDoItem]:
    qs: QuerySet[ToDoItem] = ToDoItem.objects.all()

    if completed is not None:
        qs = qs.filter(completed=completed)

    if priority is not None:
        if priority not in {choice.value for choice in Priority}:
            raise TodoValidationError(
                f"Invalid priority filter value: {priority}. "
                "Must be 1 (Low), 2 (Medium), or 3 (High)."
            )
        qs = qs.filter(priority=priority)

    items = list(qs)

    if overdue_only:
        items = [item for item in items if item.is_overdue()]

    return items


def create_todo_item(payload: Dict[str, Any]) -> ToDoItem:
    name: str = str(payload.get("name", "")).strip()
    if not name:
        raise TodoValidationError("Field 'name' is required and must not be blank.")

    completed: bool = bool(payload.get("completed", False))
    priority: int = int(payload.get("priority", Priority.MEDIUM))
    due_date: Optional[datetime.date] = payload.get("due_date") or None

    return ToDoItem.objects.create(
        name=name,
        completed=completed,
        priority=priority,
        due_date=due_date,
    )


def update_todo_item(pk: int, payload: Dict[str, Any]) -> ToDoItem:
    item: ToDoItem = get_todo_item(pk)

    if "name" in payload:
        name = str(payload["name"]).strip()
        if not name:
            raise TodoValidationError("Field 'name' must not be blank.")
        item.name = name

    if "completed" in payload:
        item.completed = bool(payload["completed"])

    if "priority" in payload:
        priority = int(payload["priority"])
        if priority not in {choice.value for choice in Priority}:
            raise TodoValidationError(
                f"Invalid priority: {priority}. Must be 1 (Low), 2 (Medium), or 3 (High)."
            )
        item.priority = priority

    if "due_date" in payload:
        item.due_date = payload["due_date"] or None

    item.save()
    return item


def delete_todo_item(pk: int) -> None:
    item: ToDoItem = get_todo_item(pk)
    item.delete()


def serialize_item(item: ToDoItem) -> ToDoItemSerializer:
    serializer: ToDoItemSerializer = ToDoItemSerializer(item)
    return serializer


def serialize_items(items: List[ToDoItem]) -> ToDoItemSerializer:
    serializer: ToDoItemSerializer = ToDoItemSerializer(items, many=True)
    return serializer
