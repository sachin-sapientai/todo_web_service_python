from __future__ import annotations

import datetime

from rest_framework import serializers

from .models import Priority, ToDoItem

_DUE_DATE_FORMATS = (
    "%Y-%m-%dT%H:%M:%SZ",   # 2025-03-18T12:00:00Z  (UTC ISO 8601)
    "%Y-%m-%dT%H:%M:%S",    # 2025-03-18T12:00:00   (no timezone suffix)
    "%Y-%m-%d",              # 2025-03-18             (plain date, DRF default)
)


def _parse_due_date(value: object) -> datetime.date:
    """
    Accept either a plain date string ("YYYY-MM-DD"), a full UTC datetime
    string ("YYYY-MM-DDTHH:MM:SSZ"), or an already-resolved date/datetime
    object (passed through by DRF after its own parsing stage).
    Always returns a datetime.date.
    """
    if isinstance(value, datetime.datetime):
        return value.date()

    if isinstance(value, datetime.date):
        return value

    raw = str(value).strip()
    for fmt in _DUE_DATE_FORMATS:
        try:
            return datetime.datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    raise serializers.ValidationError(
        f"Invalid date format '{raw}'. "
        "Use 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'."
    )


class DueDateField(serializers.CharField):
    """
    Accepts both plain date strings ("YYYY-MM-DD") and full ISO 8601
    datetime strings ("YYYY-MM-DDTHH:MM:SSZ"), always serialising back
    as "YYYY-MM-DD". Passes through None / empty string as None.
    """

    def to_internal_value(self, data: object) -> datetime.date | None:
        if data is None or data == "":
            return None
        return _parse_due_date(data)

    def to_representation(self, value: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, (datetime.date, datetime.datetime)):
            return str(value.date() if isinstance(value, datetime.datetime) else value)
        return str(value)


class ToDoItemSerializer(serializers.ModelSerializer):
    priority_label = serializers.CharField(source="get_priority_display", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    due_date = DueDateField(required=False, allow_null=True, default=None)

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
        if value is None:
            return None
        if value < datetime.date.today():
            raise serializers.ValidationError("due_date cannot be in the past.")
        return value
