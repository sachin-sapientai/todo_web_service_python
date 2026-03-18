from __future__ import annotations

import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .exceptions import TodoNotFoundError, TodoValidationError
from .models import Priority, ToDoItem
from .serializers import _parse_due_date
from .services import (
    create_todo_item,
    delete_todo_item,
    get_todo_item,
    list_todo_items,
    update_todo_item,
)


class ToDoItemModelTest(TestCase):
    def setUp(self) -> None:
        self.item = ToDoItem.objects.create(name="Write tests", priority=Priority.HIGH)

    def test_str_representation(self) -> None:
        self.assertIn("Write tests", str(self.item))
        self.assertIn("High", str(self.item))

    def test_mark_complete(self) -> None:
        self.item.mark_complete()
        self.item.refresh_from_db()
        self.assertTrue(self.item.completed)

    def test_mark_incomplete(self) -> None:
        self.item.completed = True
        self.item.save()
        self.item.mark_incomplete()
        self.item.refresh_from_db()
        self.assertFalse(self.item.completed)

    def test_is_overdue_with_past_due_date(self) -> None:
        self.item.due_date = datetime.date.today() - datetime.timedelta(days=1)
        self.item.save()
        self.assertTrue(self.item.is_overdue())

    def test_is_overdue_completed_item_is_never_overdue(self) -> None:
        self.item.due_date = datetime.date.today() - datetime.timedelta(days=1)
        self.item.completed = True
        self.item.save()
        self.assertFalse(self.item.is_overdue())

    def test_is_overdue_no_due_date(self) -> None:
        self.assertFalse(self.item.is_overdue())


class TodoServiceTest(TestCase):
    def test_create_and_retrieve(self) -> None:
        item = create_todo_item({"name": "Buy milk", "completed": False})
        fetched = get_todo_item(item.pk)
        self.assertEqual(fetched.name, "Buy milk")

    def test_create_missing_name_raises(self) -> None:
        with self.assertRaises(TodoValidationError):
            create_todo_item({"name": ""})

    def test_get_nonexistent_raises(self) -> None:
        with self.assertRaises(TodoNotFoundError):
            get_todo_item(99999)

    def test_update_item(self) -> None:
        item = create_todo_item({"name": "Old name"})
        updated = update_todo_item(item.pk, {"name": "New name", "completed": True})
        self.assertEqual(updated.name, "New name")
        self.assertTrue(updated.completed)

    def test_update_with_blank_name_raises(self) -> None:
        item = create_todo_item({"name": "Valid"})
        with self.assertRaises(TodoValidationError):
            update_todo_item(item.pk, {"name": "  "})

    def test_update_invalid_priority_raises(self) -> None:
        item = create_todo_item({"name": "Valid"})
        with self.assertRaises(TodoValidationError):
            update_todo_item(item.pk, {"priority": 99})

    def test_delete_item(self) -> None:
        item = create_todo_item({"name": "To delete"})
        pk = item.pk
        delete_todo_item(pk)
        with self.assertRaises(TodoNotFoundError):
            get_todo_item(pk)

    def test_list_filter_by_completed(self) -> None:
        create_todo_item({"name": "Done", "completed": True})
        create_todo_item({"name": "Not done", "completed": False})
        done = list_todo_items(completed=True)
        self.assertTrue(all(i.completed for i in done))

    def test_list_filter_by_priority(self) -> None:
        create_todo_item({"name": "High priority", "priority": Priority.HIGH})
        create_todo_item({"name": "Low priority", "priority": Priority.LOW})
        high = list_todo_items(priority=Priority.HIGH)
        self.assertTrue(all(i.priority == Priority.HIGH for i in high))

    def test_list_invalid_priority_raises(self) -> None:
        with self.assertRaises(TodoValidationError):
            list_todo_items(priority=99)


class TodoAPITest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.list_url = reverse("todos_collection")

    def _detail_url(self, pk: int) -> str:
        return reverse("todos_item", kwargs={"pk": pk})

    def test_create_returns_201_with_location(self) -> None:
        response = self.client.post(
            self.list_url,
            {"name": "Buy milk", "completed": False, "priority": Priority.MEDIUM},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Location", response)
        self.assertEqual(response.data["name"], "Buy milk")

    def test_create_missing_name_returns_400(self) -> None:
        response = self.client.post(self.list_url, {"name": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_returns_all_items(self) -> None:
        ToDoItem.objects.create(name="Item A")
        ToDoItem.objects.create(name="Item B")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_filter_completed_query_param(self) -> None:
        ToDoItem.objects.create(name="Done", completed=True)
        ToDoItem.objects.create(name="Pending", completed=False)
        response = self.client.get(self.list_url, {"completed": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(i["completed"] for i in response.data))

    def test_retrieve_returns_item(self) -> None:
        item = ToDoItem.objects.create(name="Item A")
        response = self.client.get(self._detail_url(item.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Item A")

    def test_retrieve_nonexistent_returns_404(self) -> None:
        response = self.client.get(self._detail_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_returns_204(self) -> None:
        item = ToDoItem.objects.create(name="Old")
        response = self.client.put(
            self._detail_url(item.pk),
            {"name": "New", "completed": True, "priority": Priority.HIGH},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        item.refresh_from_db()
        self.assertEqual(item.name, "New")

    def test_update_nonexistent_returns_404(self) -> None:
        response = self.client.put(
            self._detail_url(99999),
            {"name": "X", "completed": False, "priority": Priority.LOW},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_returns_204(self) -> None:
        item = ToDoItem.objects.create(name="To delete")
        response = self.client.delete(self._detail_url(item.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ToDoItem.objects.filter(pk=item.pk).exists())

    def test_delete_nonexistent_returns_404(self) -> None:
        response = self.client.delete(self._detail_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DueDateParsingTest(TestCase):
    """
    Validates that due_date accepts both plain dates and ISO 8601
    datetime strings, and rejects invalid formats.
    """

    def setUp(self) -> None:
        self.client = APIClient()
        self.list_url = reverse("todos_collection")
        self.future = datetime.date.today() + datetime.timedelta(days=7)

    def _detail_url(self, pk: int) -> str:
        return reverse("todos_item", kwargs={"pk": pk})

    # --- unit tests on _parse_due_date directly ---

    def test_parse_plain_date_string(self) -> None:
        result = _parse_due_date("2099-12-31")
        self.assertEqual(result, datetime.date(2099, 12, 31))

    def test_parse_iso8601_utc_string(self) -> None:
        result = _parse_due_date("2099-06-15T12:00:00Z")
        self.assertEqual(result, datetime.date(2099, 6, 15))

    def test_parse_iso8601_no_tz_string(self) -> None:
        result = _parse_due_date("2099-06-15T08:30:00")
        self.assertEqual(result, datetime.date(2099, 6, 15))

    def test_parse_date_object_passthrough(self) -> None:
        d = datetime.date(2099, 1, 1)
        self.assertEqual(_parse_due_date(d), d)

    def test_parse_datetime_object_extracts_date(self) -> None:
        dt = datetime.datetime(2099, 4, 20, 9, 0, 0)
        self.assertEqual(_parse_due_date(dt), datetime.date(2099, 4, 20))

    def test_parse_invalid_format_raises(self) -> None:
        with self.assertRaises(Exception):
            _parse_due_date("not-a-date")

    # --- API integration tests ---

    def test_create_with_plain_date(self) -> None:
        response = self.client.post(
            self.list_url,
            {"name": "Plain date task", "priority": 2, "due_date": str(self.future)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["due_date"], str(self.future))

    def test_create_with_iso8601_utc_datetime(self) -> None:
        future_dt = f"{self.future}T12:00:00Z"
        response = self.client.post(
            self.list_url,
            {"name": "ISO datetime task", "priority": 1, "due_date": future_dt},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["due_date"], str(self.future))

    def test_create_with_iso8601_no_tz(self) -> None:
        future_dt = f"{self.future}T08:30:00"
        response = self.client.post(
            self.list_url,
            {"name": "ISO no-tz task", "priority": 3, "due_date": future_dt},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["due_date"], str(self.future))

    def test_create_with_null_due_date(self) -> None:
        response = self.client.post(
            self.list_url,
            {"name": "No due date", "priority": 2, "due_date": None},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["due_date"])

    def test_create_with_past_due_date_returns_400(self) -> None:
        past = str(datetime.date.today() - datetime.timedelta(days=1))
        response = self.client.post(
            self.list_url,
            {"name": "Past task", "priority": 2, "due_date": past},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_with_iso8601_utc_datetime(self) -> None:
        item = ToDoItem.objects.create(name="Update me", priority=2)
        future_dt = f"{self.future}T15:00:00Z"
        response = self.client.put(
            self._detail_url(item.pk),
            {"name": "Updated", "completed": False, "priority": 2, "due_date": future_dt},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        item.refresh_from_db()
        self.assertEqual(item.due_date, self.future)
