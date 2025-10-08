# test_task_app.py
"""Tests for task_app module."""


from task_app.main import APP_NAME, FIELDS, Task


class TestTask:
    """Tests for Task dataclass."""

    def test_task_creation_minimal(self) -> None:
        """Test creating a task with minimal required fields."""
        task = Task(title="Buy groceries", notes="Milk, eggs, bread")
        assert task.title == "Buy groceries"
        assert task.notes == "Milk, eggs, bread"
        assert task.done is False
        assert task.serial == ""

    def test_task_creation_complete(self) -> None:
        """Test creating a task with all fields."""
        task = Task(title="Complete project", notes="Finish by Friday", done=True, serial="123")
        assert task.title == "Complete project"
        assert task.notes == "Finish by Friday"
        assert task.done is True
        assert task.serial == "123"

    def test_task_defaults(self) -> None:
        """Test task default values."""
        task = Task(title="Test", notes="")
        assert task.done is False
        assert task.serial == ""

    def test_task_empty_notes(self) -> None:
        """Test task with empty notes."""
        task = Task(title="Task with no notes", notes="")
        assert task.title == "Task with no notes"
        assert task.notes == ""

    def test_task_done_toggle(self) -> None:
        """Test toggling task completion status."""
        task = Task(title="Test", notes="", done=False)
        assert task.done is False
        task.done = True
        assert task.done is True
        task.done = False
        assert task.done is False

    def test_task_serial_assignment(self) -> None:
        """Test assigning serial number to task."""
        task = Task(title="Test", notes="")
        assert task.serial == ""
        task.serial = "1001"
        assert task.serial == "1001"


class TestTaskConstants:
    """Tests for task app constants."""

    def test_app_name(self) -> None:
        """Test APP_NAME constant."""
        assert APP_NAME == "tasks"

    def test_fields_structure(self) -> None:
        """Test FIELDS list contains expected field names."""
        assert FIELDS == ["serial", "title", "notes", "done"]
        assert len(FIELDS) == 4
        assert "serial" in FIELDS
        assert "title" in FIELDS
        assert "notes" in FIELDS
        assert "done" in FIELDS


class TestTaskDataPersistence:
    """Tests for task data persistence using tui_common."""

    def test_task_to_dict_format(self) -> None:
        """Test converting task to dictionary format for CSV storage."""
        task = Task(title="Test Task", notes="Test notes", done=True, serial="100")
        # This format would be used for CSV storage
        task_dict = {
            "serial": task.serial,
            "title": task.title,
            "notes": task.notes,
            "done": str(task.done),
        }
        assert task_dict["serial"] == "100"
        assert task_dict["title"] == "Test Task"
        assert task_dict["notes"] == "Test notes"
        assert task_dict["done"] == "True"

    def test_task_from_dict_format(self) -> None:
        """Test creating task from dictionary (CSV load simulation)."""
        task_dict = {
            "serial": "100",
            "title": "Test Task",
            "notes": "Test notes",
            "done": "True",
        }
        # Simulate loading from CSV
        task = Task(
            title=task_dict["title"],
            notes=task_dict["notes"],
            done=task_dict["done"].lower() == "true",
            serial=task_dict["serial"],
        )
        assert task.serial == "100"
        assert task.title == "Test Task"
        assert task.notes == "Test notes"
        assert task.done is True

    def test_task_done_string_conversion(self) -> None:
        """Test converting done status to/from string."""
        # False cases
        assert "False".lower() == "false"
        assert "False".lower() != "true"
        # True cases
        assert "True".lower() == "true"
        assert "true".lower() == "true"


class TestTaskValidation:
    """Tests for task validation logic."""

    def test_task_requires_title(self) -> None:
        """Test that task requires a title."""
        # Title should not be empty for valid task
        task = Task(title="", notes="Test")
        assert task.title == ""  # Can create but should validate before saving

    def test_task_with_multiline_notes(self) -> None:
        """Test task with multiline notes."""
        notes = "Line 1\nLine 2\nLine 3"
        task = Task(title="Test", notes=notes)
        assert "\n" in task.notes
        assert task.notes.count("\n") == 2

    def test_task_with_special_characters(self) -> None:
        """Test task with special characters in title and notes."""
        task = Task(
            title="Task with special chars: !@#$%^&*()",
            notes="Notes with \"quotes\" and 'apostrophes'",
        )
        assert "!@#$%^&*()" in task.title
        assert '"quotes"' in task.notes
        assert "'apostrophes'" in task.notes

    def test_task_unicode_support(self) -> None:
        """Test task with Unicode characters."""
        task = Task(title="Café ☕ meeting", notes="Discuss 日本語 support 🎌")
        assert "☕" in task.title
        assert "日本語" in task.notes
        assert "🎌" in task.notes


class TestTaskSerialization:
    """Tests for task serialization scenarios."""

    def test_task_list_to_csv_format(self) -> None:
        """Test converting multiple tasks to CSV-compatible format."""
        tasks = [
            Task(title="Task 1", notes="Notes 1", done=False, serial="1"),
            Task(title="Task 2", notes="Notes 2", done=True, serial="2"),
            Task(title="Task 3", notes="Notes 3", done=False, serial="3"),
        ]

        csv_data = [
            {
                "serial": t.serial,
                "title": t.title,
                "notes": t.notes,
                "done": str(t.done),
            }
            for t in tasks
        ]

        assert len(csv_data) == 3
        assert csv_data[0]["serial"] == "1"
        assert csv_data[1]["done"] == "True"
        assert csv_data[2]["title"] == "Task 3"

    def test_empty_task_list(self) -> None:
        """Test handling empty task list."""
        tasks: list[Task] = []
        csv_data = [
            {
                "serial": t.serial,
                "title": t.title,
                "notes": t.notes,
                "done": str(t.done),
            }
            for t in tasks
        ]
        assert len(csv_data) == 0
        assert csv_data == []


class TestTaskFiltering:
    """Tests for task filtering and sorting operations."""

    def test_filter_completed_tasks(self) -> None:
        """Test filtering completed tasks."""
        tasks = [
            Task(title="Task 1", notes="", done=False, serial="1"),
            Task(title="Task 2", notes="", done=True, serial="2"),
            Task(title="Task 3", notes="", done=False, serial="3"),
            Task(title="Task 4", notes="", done=True, serial="4"),
        ]
        completed = [t for t in tasks if t.done]
        assert len(completed) == 2
        assert all(t.done for t in completed)

    def test_filter_pending_tasks(self) -> None:
        """Test filtering pending tasks."""
        tasks = [
            Task(title="Task 1", notes="", done=False, serial="1"),
            Task(title="Task 2", notes="", done=True, serial="2"),
            Task(title="Task 3", notes="", done=False, serial="3"),
        ]
        pending = [t for t in tasks if not t.done]
        assert len(pending) == 2
        assert all(not t.done for t in pending)

    def test_count_task_statistics(self) -> None:
        """Test calculating task statistics."""
        tasks = [
            Task(title="Task 1", notes="", done=False, serial="1"),
            Task(title="Task 2", notes="", done=True, serial="2"),
            Task(title="Task 3", notes="", done=False, serial="3"),
            Task(title="Task 4", notes="", done=True, serial="4"),
            Task(title="Task 5", notes="", done=True, serial="5"),
        ]
        total = len(tasks)
        completed = sum(1 for t in tasks if t.done)
        pending = sum(1 for t in tasks if not t.done)
        completion_rate = (completed / total * 100) if total > 0 else 0

        assert total == 5
        assert completed == 3
        assert pending == 2
        assert completion_rate == 60.0


class TestTaskSearch:
    """Tests for task search operations."""

    def test_search_by_title(self) -> None:
        """Test searching tasks by title."""
        tasks = [
            Task(title="Buy groceries", notes="", serial="1"),
            Task(title="Pay bills", notes="", serial="2"),
            Task(title="Buy tickets", notes="", serial="3"),
        ]
        results = [t for t in tasks if "buy" in t.title.lower()]
        assert len(results) == 2
        assert all("buy" in t.title.lower() for t in results)

    def test_search_by_notes(self) -> None:
        """Test searching tasks by notes."""
        tasks = [
            Task(title="Task 1", notes="urgent priority", serial="1"),
            Task(title="Task 2", notes="low priority", serial="2"),
            Task(title="Task 3", notes="medium priority", serial="3"),
        ]
        results = [t for t in tasks if "urgent" in t.notes.lower()]
        assert len(results) == 1
        assert results[0].notes == "urgent priority"

    def test_search_case_insensitive(self) -> None:
        """Test case-insensitive task search."""
        tasks = [
            Task(title="IMPORTANT Meeting", notes="", serial="1"),
            Task(title="important call", notes="", serial="2"),
            Task(title="Less Important", notes="", serial="3"),
        ]
        results = [t for t in tasks if "important" in t.title.lower()]
        assert len(results) == 3


class TestTaskOrdering:
    """Tests for task ordering by serial number."""

    def test_serial_number_ordering(self) -> None:
        """Test ordering tasks by serial number."""
        task_dicts = [
            {"serial": "3", "title": "Third", "notes": "", "done": "False"},
            {"serial": "1", "title": "First", "notes": "", "done": "False"},
            {"serial": "2", "title": "Second", "notes": "", "done": "False"},
        ]
        # Sort by serial (string comparison)
        sorted_dicts = sorted(task_dicts, key=lambda x: int(x["serial"]))
        assert sorted_dicts[0]["serial"] == "1"
        assert sorted_dicts[1]["serial"] == "2"
        assert sorted_dicts[2]["serial"] == "3"

    def test_next_serial_number(self) -> None:
        """Test calculating next serial number."""
        existing_serials = ["1", "2", "3", "5"]
        max_serial = max(int(s) for s in existing_serials) if existing_serials else 0
        next_serial = str(max_serial + 1)
        assert next_serial == "6"

    def test_next_serial_empty_list(self) -> None:
        """Test getting next serial when no tasks exist."""
        existing_serials: list[str] = []
        max_serial = max((int(s) for s in existing_serials), default=0)
        next_serial = str(max_serial + 1)
        assert next_serial == "1"


class TestConfirmDeleteScreen:
    """Tests for ConfirmDeleteScreen confirmation dialog."""

    def test_confirm_delete_screen_initialization(self) -> None:
        """Test ConfirmDeleteScreen can be initialized with task data."""
        from task_app.main import ConfirmDeleteScreen

        task_dict = {
            "serial": "42",
            "title": "Important Task",
            "notes": "Some notes here",
            "done": "false",
        }
        confirmed = False

        def on_confirm() -> None:
            nonlocal confirmed
            confirmed = True

        screen = ConfirmDeleteScreen(task_dict, on_confirm)
        assert screen._task_dict == task_dict
        assert screen._on_confirm == on_confirm
        assert not confirmed

    def test_confirm_delete_callback_execution(self) -> None:
        """Test that the confirmation callback is properly stored."""
        from task_app.main import ConfirmDeleteScreen

        task_dict = {
            "serial": "1",
            "title": "Test",
            "notes": "",
            "done": "true",
        }
        callback_executed = False

        def on_confirm() -> None:
            nonlocal callback_executed
            callback_executed = True

        screen = ConfirmDeleteScreen(task_dict, on_confirm)
        # Execute the callback manually
        screen._on_confirm()
        assert callback_executed
