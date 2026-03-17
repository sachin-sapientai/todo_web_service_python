from django.urls import path

from . import views

urlpatterns = [
    path("todos", views.todos_collection, name="todos_collection"),
    path("todos/<int:pk>", views.todos_item, name="todos_item"),
]

