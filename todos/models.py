from __future__ import annotations

from django.db import models
from django.utils import timezone


class Priority(models.IntegerChoices):
    LOW = 1, "Low"
    MEDIUM = 2, "Medium"
    HIGH = 3, "High"


class ToDoItem(models.Model):
    name = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "created_at"]

    def __str__(self) -> str:
        return f"[{self.get_priority_display()}] {self.name} (completed={self.completed})"

    def mark_complete(self) -> None:
        self.completed = True
        self.save(update_fields=["completed", "updated_at"])

    def mark_incomplete(self) -> None:
        self.completed = False
        self.save(update_fields=["completed", "updated_at"])

    def is_overdue(self) -> bool:
        if self.due_date is None or self.completed:
            return False
        return self.due_date < timezone.localdate()
