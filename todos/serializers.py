from __future__ import annotations

import datetime

from rest_framework import serializers

from .models import Priority, ToDoItem


class ToDoItemSerializer(serializers.ModelSerializer):
    priority_label = serializers.CharField(source="get_priority_display", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = ToDoItem
        fields = [
            "id",
            "name",
            "completed",
            "priority",
            "priority_label",
            "due_date",
            "is_overdue",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name must not be blank.")
        if len(value) > 255:
            raise serializers.ValidationError("Name must be 255 characters or fewer.")
        return value

    def validate_priority(self, value: int) -> int:
        valid = {choice.value for choice in Priority}
        if value not in valid:
            raise serializers.ValidationError(
                f"Priority must be one of {sorted(valid)} (1=Low, 2=Medium, 3=High)."
            )
        return value

    def validate_due_date(self, value: datetime.date | None) -> datetime.date | None:
        if value is not None and value < datetime.date.today():
            raise serializers.ValidationError("due_date cannot be in the past.")
        return value
