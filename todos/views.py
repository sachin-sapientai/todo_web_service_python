from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .exceptions import TodoNotFoundError, TodoValidationError
from .serializers import ToDoItemSerializer
from .services import (
    create_todo_item,
    delete_todo_item,
    get_todo_item,
    list_todo_items,
    serialize_item,
    serialize_items,
    update_todo_item,
)


def _parse_bool_param(value: str) -> bool:
    return value.lower() in {"true", "1", "yes"}


@api_view(["GET", "POST"])
def todos_collection(request: Request) -> Response:
    if request.method == "GET":
        completed_param = request.query_params.get("completed")
        priority_param = request.query_params.get("priority")
        overdue_param = request.query_params.get("overdue")

        completed = _parse_bool_param(completed_param) if completed_param is not None else None
        priority = int(priority_param) if priority_param is not None else None
        overdue_only = _parse_bool_param(overdue_param) if overdue_param is not None else False

        try:
            items = list_todo_items(
                completed=completed,
                priority=priority,
                overdue_only=overdue_only,
            )
        except TodoValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serialize_items(items)
        return Response(serializer.data)

    serializer = ToDoItemSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        item = create_todo_item(serializer.validated_data)
    except TodoValidationError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    out = serialize_item(item)
    location = request.build_absolute_uri(reverse("todos_item", kwargs={"pk": item.pk}))
    return Response(out.data, status=status.HTTP_201_CREATED, headers={"Location": location})


@api_view(["GET", "PUT", "DELETE"])
def todos_item(request: Request, pk: int) -> Response:
    try:
        item = get_todo_item(pk)
    except TodoNotFoundError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = serialize_item(item)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = ToDoItemSerializer(item, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            update_todo_item(pk, serializer.validated_data)
        except TodoValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    try:
        delete_todo_item(pk)
    except TodoNotFoundError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_204_NO_CONTENT)
