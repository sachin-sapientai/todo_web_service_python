from rest_framework import serializers

from .models import ToDoItem


class ToDoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDoItem
        fields = ["id", "name", "completed"]

