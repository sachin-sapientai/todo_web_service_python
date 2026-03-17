from django.contrib import admin

from .models import ToDoItem


@admin.register(ToDoItem)
class ToDoItemAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "priority", "completed", "due_date", "is_overdue", "created_at"]
    list_filter = ["completed", "priority"]
    search_fields = ["name"]
    ordering = ["priority", "created_at"]
    readonly_fields = ["created_at", "updated_at"]
