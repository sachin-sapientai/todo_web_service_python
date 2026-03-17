from django.db import models


class ToDoItem(models.Model):
    name = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.id}: {self.name} [completed: {self.completed}]"

