"""Task management TUI application using Textual."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from tui_common import (
    BcryptAuth,
    LoginScreen,
    get_version,
    load_config,
    load_csv_data,
    save_config,
    save_csv_data,
    sort_data,
    user_config_path,
    user_data_path,
    user_wants_encryption,
)

APP_NAME = "tasks"
FIELDS = ["serial", "title", "notes", "done"]
VERSION = get_version()


@dataclass
class Task:
    """Data class representing a single task.

    Attributes:
        serial: Unique serial number (auto-assigned)
        title: Task title (required)
        notes: Additional notes or description
        done: Completion status (default False)
    """

    title: str
    notes: str
    done: bool = False
    serial: str = ""


class TaskEditor(Screen[None]):
    """Modal screen for adding or editing a task.

    Provides form inputs for task title and notes.
    If existing task is provided, operates in edit mode.
    """

    def __init__(
        self,
        on_saved: Callable[[Task, int | None], None],
        existing: Task | None = None,
        idx: int | None = None,
    ):
        """Initialize task editor.

        Args:
            on_saved: Callback function to call when task is saved
            existing: Task to edit (None for new task)
            idx: Index of task in list (None for new task)
        """
        super().__init__()
        self._on_saved = on_saved
        self.existing = existing
        self.idx = idx

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="edit"):
            yield Label("Edit Task" if self.existing else "Add Task", id="title")
            yield Input(
                value=(self.existing.title if self.existing else ""),
                placeholder="Title",
                id="title_in",
            )
            yield Input(
                value=(self.existing.notes if self.existing else ""),
                placeholder="Notes",
                id="notes_in",
            )
            with Horizontal():
                yield Button("Save", id="save", variant="success")
                yield Button("Cancel", id="cancel")
        yield Footer()

    @on(Button.Pressed, "#cancel")
    def _cancel(self) -> None:
        """Close editor without saving."""
        self.app.pop_screen()

    @on(Button.Pressed, "#save")
    def _save(self) -> None:
        """Validate and save task changes.

        Calls the on_saved callback with the task data.
        """
        title = self.query_one("#title_in", Input).value.strip()
        notes = self.query_one("#notes_in", Input).value.strip()
        if not title:
            self.app.notify("Title required", severity="warning")
            return
        task = Task(title=title, notes=notes)
        self._on_saved(task, self.idx)
        self.app.pop_screen()


class ConfirmDeleteScreen(Screen[None]):
    """Modal screen for confirming task deletion.

    Displays task details and asks for confirmation before deleting.
    """

    def __init__(self, task_dict: dict[str, str], on_confirm: Callable[[], None]):
        """Initialize delete confirmation dialog.

        Args:
            task_dict: Task dictionary to be deleted
            on_confirm: Callback function to call if deletion is confirmed
        """
        super().__init__()
        self._task_dict = task_dict
        self._on_confirm = on_confirm

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="edit"):
            yield Label("Confirm Delete", id="title")
            yield Label(f"Delete task #{self._task_dict.get('serial', '')}?")
            yield Label(f"Title: {self._task_dict.get('title', '')}")
            yield Label(f"Notes: {self._task_dict.get('notes', '')}")
            done_status = (
                "✓ Done" if self._task_dict.get("done", "false") == "true" else "☐ Not Done"
            )
            yield Label(f"Status: {done_status}")
            with Horizontal():
                yield Button("Delete", id="delete", variant="error")
                yield Button("Cancel", id="cancel")
        yield Footer()

    @on(Button.Pressed, "#cancel")
    def _cancel(self) -> None:
        """Close dialog without deleting."""
        self.app.pop_screen()

    @on(Button.Pressed, "#delete")
    def _delete(self) -> None:
        """Confirm deletion and close dialog."""
        self._on_confirm()
        self.app.pop_screen()


class MainScreen(Screen[None]):
    """Main screen for task management application.

    Displays:
    - User info
    - Action buttons in toolbar (Add, Edit, Toggle, Delete, Save, Logout)
    - DataTable with all tasks sorted by serial number (newest first)

    Features:
    - Add/Edit/Delete tasks with serial numbers
    - Toggle task completion status
    - Keyboard shortcuts with footer display
    - Persistent CSV storage
    """

    BINDINGS = [
        Binding("a", "add_task", "Add"),
        Binding("e", "edit_task", "Edit"),
        Binding("t", "toggle_task", "Toggle"),
        Binding("d", "delete_task", "Delete"),
        Binding("s", "toggle_sort", "Sort"),
        Binding("q", "logout", "Logout"),
    ]

    CSS = """
    #edit { width: 60%; margin: 2 20; }
    #title { margin-bottom: 1; }
    #panel { height: 1fr; }

    /* Toolbar pinned above the table: roomy, won't squash */
    #toolbar {
        width: 100%;
        height: auto;          /* let buttons set height */
        padding: 1 0;          /* breathing room above/below */
        content-align: center middle;
    }

    /* Make buttons tall and readable; add spacing with margins */
    #toolbar Button {
        height: 3;             /* vertical space */
        min-width: 16;         /* grows to fit label */
        padding: 0 3;          /* horizontal padding */
        margin: 0 1;           /* spacing between buttons */
    }

    /* DataTable fills remaining space below toolbar */
    #table {
        height: 1fr;
        width: 100%;
    }

    Button.-primary { background: $accent; color: $text; }
    """

    def __init__(self, username: str, password: str | None = None):
        """Initialize main screen with user's task data."""
        super().__init__()
        self.username = username
        self.password = password  # None = plaintext, value = encrypted

        # Password itself indicates encryption: None = plaintext, value = encrypted
        encrypted = password is not None

        # Use appropriate file extensions based on encryption
        self.path: Path = user_data_path(APP_NAME, username, "tasks.csv", encrypted)
        self.cfg_path: Path = user_config_path(APP_NAME, username, encrypted)

        # Load config and data (password already None for plaintext, value for encrypted)
        self.config = load_config(self.cfg_path, {"next_serial": 1}, password)
        self.next_serial: int = int(self.config.get("next_serial", 1))

        # Load and sort tasks (newest first)
        self.tasks: list[dict[str, str]] = sort_data(load_csv_data(self.path, password))
        self.selected_row_index: int | None = None  # Track selected row
        self.sort_order: bool = True  # True = descending (newest first), False = ascending

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="panel"):
            yield Label(f"Logged in as: {self.username}")

            # --- Buttons pinned at the top (single row) ---
            with Horizontal(id="toolbar"):
                yield Button("Add", id="btn-add")
                yield Button("Edit", id="btn-edit")
                yield Button("Toggle", id="btn-toggle")
                yield Button("Delete", id="btn-delete")
                yield Button("Sort", id="btn-sort")
                yield Button("Logout", id="btn-logout")

            # --- DataTable fills remaining space below ---
            dt: DataTable[object] = DataTable(id="table", cursor_type="row")
            dt.add_columns("Serial", "Status", "Title", "Notes")
            for t in self.tasks:
                done_str = t.get("done", "false")
                status = "✅ Completed" if done_str == "true" else "⬜ Pending"
                dt.add_row(t.get("serial", ""), status, t.get("title", ""), t.get("notes", ""))
            yield dt
        yield Footer()

    def _refresh_table(self) -> None:
        """Refresh the DataTable with current task data."""
        dt: DataTable[object] = self.query_one("#table", DataTable)
        dt.clear()
        for t in self.tasks:
            done_str = t.get("done", "false")
            status = "✅ Completed" if done_str == "true" else "⬜ Pending"
            dt.add_row(t.get("serial", ""), status, t.get("title", ""), t.get("notes", ""))

    # ----- Row selection handler -----

    @on(DataTable.RowSelected)
    def _row_selected(self, event: DataTable.RowSelected) -> None:
        """Track which row is selected in the DataTable."""
        self.selected_row_index = event.cursor_row

    # ----- Button click handlers (map to key binding actions) -----

    @on(Button.Pressed, "#btn-add")
    def _btn_add(self) -> None:
        """Handle Add button click."""
        self.action_add_task()

    @on(Button.Pressed, "#btn-edit")
    def _btn_edit(self) -> None:
        """Handle Edit button click."""
        self.action_edit_task()

    @on(Button.Pressed, "#btn-toggle")
    def _btn_toggle(self) -> None:
        """Handle Toggle button click."""
        self.action_toggle_task()

    @on(Button.Pressed, "#btn-delete")
    def _btn_delete(self) -> None:
        """Handle Delete button click."""
        self.action_delete_task()

    @on(Button.Pressed, "#btn-sort")
    def _btn_sort(self) -> None:
        """Handle Sort button click."""
        self.action_toggle_sort()

    @on(Button.Pressed, "#btn-logout")
    def _btn_logout(self) -> None:
        """Handle Logout button click."""
        self.action_logout()

    # ----- Key binding actions (also called by button handlers) -----

    def action_add_task(self) -> None:
        """Show modal to add a new task. Bound to 'a' key."""
        self.app.push_screen(TaskEditor(self._task_saved_callback))

    def action_edit_task(self) -> None:
        """Show modal to edit selected task. Bound to 'e' key."""
        dt: DataTable[object] = self.query_one("#table", DataTable)
        cursor_row = dt.cursor_row
        row_index = cursor_row if cursor_row >= 0 else self.selected_row_index

        if row_index is None or row_index >= len(self.tasks):
            self.app.notify("Please navigate to a row to edit (use arrow keys)", severity="warning")
            return

        # Convert task dict to Task object for editor
        task_dict = self.tasks[row_index]
        task_obj = Task(
            title=task_dict.get("title", ""),
            notes=task_dict.get("notes", ""),
            done=task_dict.get("done", "false") == "true",
            serial=task_dict.get("serial", ""),
        )
        self.app.push_screen(TaskEditor(self._task_saved_callback, task_obj, idx=row_index))

    def action_toggle_task(self) -> None:
        """Toggle completion status of selected task. Bound to 't' key."""
        dt: DataTable[object] = self.query_one("#table", DataTable)
        cursor_row = dt.cursor_row
        row_index = cursor_row if cursor_row >= 0 else self.selected_row_index

        if row_index is None or row_index >= len(self.tasks):
            self.app.notify("Select a task (use arrow keys)", severity="warning")
            return

        # Toggle done status
        current_done = self.tasks[row_index].get("done", "false") == "true"
        self.tasks[row_index]["done"] = "false" if current_done else "true"
        self._refresh_table()
        # Auto-save after toggle
        save_csv_data(self.path, self.tasks, FIELDS, self.password)
        status = "completed" if not current_done else "incomplete"
        self.app.notify(f"Task marked as {status}")

    def action_delete_task(self) -> None:
        """Delete selected task with confirmation. Bound to 'd' key."""
        dt: DataTable[object] = self.query_one("#table", DataTable)
        cursor_row = dt.cursor_row
        row_index = cursor_row if cursor_row >= 0 else self.selected_row_index

        if row_index is None or row_index >= len(self.tasks):
            self.app.notify("Select a task (use arrow keys)", severity="warning")
            return

        # Get the task at the row and show confirmation dialog
        task_to_delete = self.tasks[row_index].copy()
        self.app.push_screen(
            ConfirmDeleteScreen(task_to_delete, lambda: self._on_task_deleted(row_index))
        )

    def action_logout(self) -> None:
        """Save tasks and config, return to login screen. Bound to 'q' key."""
        # Save tasks and config
        save_csv_data(self.path, self.tasks, FIELDS, self.password)
        self.config["next_serial"] = self.next_serial
        save_config(self.cfg_path, self.config, self.password)
        self.app.pop_screen()

    def action_toggle_sort(self) -> None:
        """Toggle sort order of tasks. Bound to 's' key."""
        # Toggle the sort order
        self.sort_order = not self.sort_order
        # Sort tasks using the shared sort_data function
        self.tasks = sort_data(self.tasks, reverse=self.sort_order)
        self._refresh_table()
        order = "descending" if self.sort_order else "ascending"
        self.app.notify(f"Tasks sorted in {order} order")

    def _task_saved_callback(self, task: Task, idx: int | None) -> None:
        """Callback function to handle task saved event from TaskEditor.

        Args:
            task: The saved task data
            idx: Index of edited task (None for new task)
        """
        if idx is None:
            # Adding new task - assign serial number
            task_dict = {
                "serial": str(self.next_serial),
                "title": task.title,
                "notes": task.notes,
                "done": "true" if task.done else "false",
            }
            self.next_serial += 1
            self.tasks.insert(0, task_dict)  # Add at beginning
            # Re-sort to ensure proper ordering
            self.tasks = sort_data(self.tasks, reverse=self.sort_order)
            self.app.notify(f"Added task #{task_dict['serial']}: {task.title}")
        else:
            # Editing existing task - preserve serial
            task_dict = self.tasks[idx]
            task_dict["title"] = task.title
            task_dict["notes"] = task.notes
            # Preserve existing done status and serial when editing
            self.app.notify(f"Updated task #{task_dict.get('serial', '')}: {task.title}")

        self._refresh_table()
        # Auto-save after adding or editing
        save_csv_data(self.path, self.tasks, FIELDS, self.password)
        # Save config with updated serial counter
        self.config["next_serial"] = self.next_serial
        save_config(self.cfg_path, self.config, self.password)

    def _on_task_deleted(self, row_index: int) -> None:
        """Callback function to handle task deletion after confirmation.

        Args:
            row_index: Index of task to delete in the tasks list
        """
        deleted_task = self.tasks.pop(row_index)
        self._refresh_table()
        # Auto-save after delete
        save_csv_data(self.path, self.tasks, FIELDS, self.password)
        self.app.notify(f"Deleted task: {deleted_task.get('title', '')}")


class TaskApp(App[None]):
    """Main Textual application for task management.

    Starts with login screen, then shows main task interface.
    """

    TITLE = f"Task App v{VERSION}"
    CSS = MainScreen.CSS

    def on_mount(self) -> None:
        """Show login screen on app startup."""
        auth = BcryptAuth(APP_NAME)
        # LoginScreen provides both username and password to callback
        # Check encryption status and pass password only if encryption is enabled

        def create_main_screen(user: str, password: str) -> MainScreen:
            # Only pass password if user has encryption enabled
            return MainScreen(user, password if user_wants_encryption(APP_NAME, user) else None)

        self.push_screen(LoginScreen("Task App — Login", auth, create_main_screen))


def main() -> None:
    """Entry point for the task-app command."""
    TaskApp().run()


if __name__ == "__main__":
    main()
