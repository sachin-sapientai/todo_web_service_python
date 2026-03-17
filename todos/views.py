from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ToDoItem
from .serializers import ToDoItemSerializer


@api_view(["GET", "POST"])
def todos_collection(request):
    if request.method == "GET":
        items = ToDoItem.objects.all()
        serializer = ToDoItemSerializer(items, many=True)
        return Response(serializer.data)

    serializer = ToDoItemSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    item = serializer.save()

    location = request.build_absolute_uri(
        reverse("todos_item", kwargs={"pk": item.pk})
    )
    headers = {"Location": location}

    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@api_view(["GET", "PUT", "DELETE"])
def todos_item(request, pk: int):
    item = get_object_or_404(ToDoItem, pk=pk)

    if request.method == "GET":
        serializer = ToDoItemSerializer(item)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = ToDoItemSerializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if request.method == "DELETE":
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

