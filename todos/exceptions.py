from __future__ import annotations


class TodoNotFoundError(Exception):
    def __init__(self, pk: int) -> None:
        super().__init__(f"ToDoItem with id={pk} does not exist.")
        self.pk = pk


class TodoValidationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
