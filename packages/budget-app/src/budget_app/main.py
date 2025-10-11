"""Budget tracking TUI application using Textual."""

from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.suggester import SuggestFromList
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

APP_NAME = "budget"
FIELDS = ["serial", "date", "category", "amount", "description"]
VERSION = get_version()

# Common expense categories
COMMON_CATEGORIES = [
    "Food",
    "Groceries",
    "Dining",
    "Transportation",
    "Gas",
    "Parking",
    "Utilities",
    "Electricity",
    "Water",
    "Internet",
    "Rent",
    "Mortgage",
    "Healthcare",
    "Medical",
    "Pharmacy",
    "Entertainment",
    "Movies",
    "Shopping",
    "Clothing",
    "Electronics",
    "Travel",
    "Hotels",
    "Education",
    "Books",
    "Fitness",
    "Subscriptions",
    "Insurance",
    "Personal Care",
    "Gifts",
    "Charity",
    "Other",
]


class AddExpenseScreen(Screen[None]):
    def __init__(
        self,
        on_saved: Callable[[dict[str, str]], None],
        expense: dict[str, str] | None = None,
        categories: list[str] | None = None,
    ):
        super().__init__()
        self._on_saved = on_saved
        self._expense = expense  # If provided, we're in edit mode
        self._is_edit = expense is not None
        self._categories = categories or COMMON_CATEGORIES

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="edit"):
            title = "Edit Expense" if self._is_edit else "Add Expense"
            yield Label(title, id="title")

            # Pre-populate fields if editing
            if self._is_edit and self._expense is not None:
                date_val = self._expense.get("date", "")
                cat_val = self._expense.get("category", "")
                amt_val = self._expense.get("amount", "")
                desc_val = self._expense.get("description", "")
            else:
                date_val = date.today().strftime("%Y-%m-%d")
                cat_val = ""
                amt_val = ""
                desc_val = ""

            yield Input(value=date_val, placeholder="YYYY-MM-DD", id="date_in")
            yield Input(
                value=cat_val,
                placeholder="Category (e.g., Food, Rent)",
                id="cat_in",
                suggester=SuggestFromList(self._categories, case_sensitive=False),
            )
            yield Input(value=amt_val, placeholder="Amount (e.g., 12.34)", id="amt_in")
            yield Input(value=desc_val, placeholder="Description", id="desc_in")
            with Horizontal():
                yield Button("Save", id="save", variant="success")
                yield Button("Cancel", id="cancel")
        yield Footer()

    @on(Button.Pressed, "#cancel")
    def _cancel(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#save")
    def _save(self) -> None:
        d = self.query_one("#date_in", Input).value.strip()
        c = self.query_one("#cat_in", Input).value.strip()
        a = self.query_one("#amt_in", Input).value.strip()
        desc = self.query_one("#desc_in", Input).value.strip()

        # Validate date
        if not d:
            self.app.notify("Date is required", severity="warning")
            return
        try:
            parsed_date = datetime.strptime(d, "%Y-%m-%d")
            if parsed_date.date() > date.today():
                self.app.notify("Date cannot be in the future", severity="warning")
                return
        except ValueError:
            self.app.notify(
                "Invalid date format. Use YYYY-MM-DD (e.g., 2025-10-05)", severity="warning"
            )
            return

        # Validate amount
        if not a:
            self.app.notify("Amount is required", severity="warning")
            return
        try:
            amt = float(a)
            if amt <= 0:
                self.app.notify("Amount must be greater than 0", severity="warning")
                return
        except ValueError:
            self.app.notify("Invalid amount. Enter a number (e.g., 12.34)", severity="warning")
            return

        # Validate category
        if not c:
            self.app.notify("Category is required", severity="warning")
            return

        expense = {"date": d, "category": c, "amount": f"{amt:.2f}", "description": desc}

        if self._is_edit and self._expense is not None:
            expense["serial"] = self._expense.get("serial", "")

        self._on_saved(expense)
        self.app.pop_screen()


class BudgetPrompt(Screen[None]):
    def __init__(self, current: float, on_set: Callable[[float], None]):
        super().__init__()
        self.current = current
        self._on_set = on_set

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="edit"):
            yield Label("Set Monthly Budget", id="title")
            yield Input(
                value=(f"{self.current:.2f}" if self.current > 0 else "2000.00"),
                placeholder="e.g., 2000.00",
                id="budget_in",
            )
            with Horizontal():
                yield Button("Save", id="save", variant="success")
                yield Button("Cancel", id="cancel")
        yield Footer()

    @on(Button.Pressed, "#cancel")
    def _cancel(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#save")
    def _save(self) -> None:
        s = self.query_one("#budget_in", Input).value.strip()
        try:
            val = float(s)
        except Exception:
            self.app.notify("Enter a number", severity="warning")
            return
        self._on_set(val)
        self.app.pop_screen()


class MonthPrompt(Screen[None]):
    def __init__(
        self, default_year: int, default_month: int, on_chosen: Callable[[int, int], None]
    ):
        super().__init__()
        self.default_year = default_year
        self.default_month = default_month
        self._on_chosen = on_chosen

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="edit"):
            yield Label("Pick Month to Track", id="title")
            yield Input(value=str(self.default_year), placeholder="YYYY", id="year_in")
            yield Input(value=str(self.default_month), placeholder="MM", id="month_in")
            with Horizontal():
                yield Button("Compute", id="compute", variant="success")
                yield Button("Cancel", id="cancel")
        yield Footer()

    @on(Button.Pressed, "#cancel")
    def _cancel(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#compute")
    def _compute(self) -> None:
        y = self.query_one("#year_in", Input).value.strip()
        m = self.query_one("#month_in", Input).value.strip()
        try:
            y_i, m_i = int(y), int(m)
            if not (1 <= m_i <= 12):
                raise ValueError
        except Exception:
            self.app.notify("Invalid year/month", severity="warning")
            return
        self._on_chosen(y_i, m_i)
        self.app.pop_screen()


class ConfirmDeleteScreen(Screen[None]):
    def __init__(self, expense: dict[str, str], on_confirm: Callable[[], None]):
        super().__init__()
        self._expense = expense
        self._on_confirm = on_confirm

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="edit"):
            yield Label("Confirm Delete", id="title")
            yield Label(f"Delete expense #{self._expense.get('serial', '')}?")
            yield Label(f"Date: {self._expense.get('date', '')}")
            yield Label(f"Category: {self._expense.get('category', '')}")
            yield Label(f"Amount: ${self._expense.get('amount', '')}")
            yield Label(f"Description: {self._expense.get('description', '')}")
            with Horizontal():
                yield Button("Delete", id="delete", variant="error")
                yield Button("Cancel", id="cancel")
        yield Footer()

    @on(Button.Pressed, "#cancel")
    def _cancel(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#delete")
    def _delete(self) -> None:
        self._on_confirm()
        self.app.pop_screen()


class MainScreen(Screen[None]):
    BINDINGS = [
        Binding("a", "add_expense", "Add"),
        Binding("e", "edit_expense", "Edit"),
        Binding("d", "delete_expense", "Delete"),
        Binding("t", "track_budget", "Track"),
        Binding("b", "set_budget", "Set Budget"),
        Binding("s", "toggle_sort", "Sort"),
        Binding("q", "logout", "Logout"),
    ]

    CSS = """
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
        min-width: 18;         /* grows to fit label */
        padding: 0 3;          /* horizontal padding */
        margin: 0 1;           /* <-- spacing between buttons */
    }

    /* Table fills remaining space and scrolls properly */
    #table {
        height: 1fr;
        width: 100%;
    }

    Button.-primary { background: $accent; color: $text; }
    """

    def __init__(self, username: str, password: str | None = None):
        super().__init__()
        self.username = username
        self.password = password  # None = plaintext, value = encrypted

        encrypted = password is not None

        self.csv_path: Path = user_data_path(APP_NAME, username, "expenses.csv", encrypted)
        self.cfg_path: Path = user_config_path(APP_NAME, username, encrypted)

        defaults = {"monthly_budget": 0.0, "next_serial": 1}
        self.config = load_config(self.cfg_path, defaults, password)
        self.monthly_budget: float = float(self.config.get("monthly_budget", 0.0))
        self.next_serial: int = int(self.config.get("next_serial", 1))
        self.expenses: list[dict[str, str]] = sort_data(load_csv_data(self.csv_path, password))
        self.selected_row_index: int | None = None
        self.sort_order: bool = True

    def _get_all_categories(self) -> list[str]:
        used_categories = {e.get("category", "") for e in self.expenses if e.get("category")}
        all_categories = sorted(set(COMMON_CATEGORIES) | used_categories)
        return all_categories

    def _get_monthly_summary(self) -> str:
        today = date.today()
        month_str = f"{today.year:04d}-{today.month:02d}"
        month_expenses = [e for e in self.expenses if e["date"].startswith(month_str)]
        total_spent = sum(float(e["amount"]) for e in month_expenses)
        category_totals: dict[str, float] = {}
        for e in month_expenses:
            cat = e.get("category", "Other")
            category_totals[cat] = category_totals.get(cat, 0.0) + float(e["amount"])
        if self.monthly_budget > 0:
            remaining = self.monthly_budget - total_spent
            percent = (total_spent / self.monthly_budget) * 100 if self.monthly_budget > 0 else 0
            if remaining < 0:
                status = f"⚠ OVER BUDGET by ${-remaining:.2f}"
            elif percent >= 80:
                status = f"⚠ {percent:.1f}% used (${remaining:.2f} left)"
            else:
                status = f"✓ ${remaining:.2f} remaining ({100 - percent:.1f}% left)"
            summary = f"📅 {month_str}: ${total_spent:.2f} / ${self.monthly_budget:.2f} - {status}"
        else:
            summary = f"📅 {month_str}: ${total_spent:.2f} spent (No budget set)"
        if category_totals:
            top_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]
            cat_summary = ", ".join([f"{cat}: ${amt:.2f}" for cat, amt in top_cats])
            summary += f" | Top: {cat_summary}"
        return summary

    def _update_summary(self) -> None:
        summary_label = self.query_one("#summary", Label)
        summary_label.update(self._get_monthly_summary())

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="panel"):
            yield Label(f"Logged in as: {self.username}")
            yield Label("", id="summary")
            with Horizontal(id="toolbar"):
                yield Button("Add", id="btn-add")
                yield Button("Edit", id="btn-edit")
                yield Button("Delete", id="btn-delete")
                yield Button("Track", id="btn-track")
                yield Button("Set Budget", id="btn-set")
                yield Button("Sort", id="btn-sort")
                yield Button("Logout", id="btn-logout")
            dt: DataTable[object] = DataTable(id="table", cursor_type="row")
            dt.add_columns("Serial", "Date", "Category", "Amount", "Description")
            for e in self.expenses:
                dt.add_row(
                    e.get("serial", ""), e["date"], e["category"], e["amount"], e["description"]
                )
            yield dt
        yield Footer()

    def on_mount(self) -> None:
        self._update_summary()

    def _refresh_table(self) -> None:
        dt: DataTable[object] = self.query_one("#table", DataTable)
        dt.clear()
        for e in self.expenses:
            dt.add_row(e.get("serial", ""), e["date"], e["category"], e["amount"], e["description"])

    def _on_expense_saved(self, expense: dict[str, str]) -> None:
        if "serial" in expense and expense["serial"]:
            serial = expense["serial"]
            for i, e in enumerate(self.expenses):
                if e.get("serial") == serial:
                    self.expenses[i] = expense
                    break
        else:
            expense["serial"] = str(self.next_serial)
            self.next_serial += 1
            self.config["next_serial"] = self.next_serial
            save_config(self.cfg_path, self.config)
            self.expenses.insert(0, expense)
        self.expenses = sort_data(self.expenses, reverse=self.sort_order)
        self._refresh_table()
        self._update_summary()
        save_csv_data(self.csv_path, self.expenses, FIELDS, self.password)
        if self.monthly_budget > 0:
            expense_date = expense["date"]
            month_str = expense_date[:7]
            spent = sum(
                float(e["amount"]) for e in self.expenses if e["date"].startswith(month_str)
            )
            if spent > self.monthly_budget:
                excess = spent - self.monthly_budget
                self.app.notify(
                    f"⚠ Monthly budget exceeded for {month_str} by ${excess:.2f}", severity="error"
                )
            else:
                remaining = self.monthly_budget - spent
                self.app.notify(f"✓ Budget for {month_str}: ${remaining:.2f} remaining")

    def _on_budget_set(self, value: float) -> None:
        self.monthly_budget = value
        self.config["monthly_budget"] = self.monthly_budget
        save_config(self.cfg_path, self.config)
        self._update_summary()
        self.app.notify(f"Monthly budget set to ${self.monthly_budget:.2f}")

    def _on_month_chosen(self, year: int, month: int) -> None:
        month_str = f"{year:04d}-{month:02d}"
        spent = sum(float(e["amount"]) for e in self.expenses if e["date"].startswith(month_str))
        if self.monthly_budget <= 0:
            self.app.notify(f"{month_str}: spent ${spent:.2f}. No budget set.", severity="warning")
        else:
            delta = self.monthly_budget - spent
            if delta < 0:
                self.app.notify(f"⚠ Over budget in {month_str} by ${-delta:.2f}", severity="error")
            else:
                self.app.notify(f"✓ Under budget in {month_str}: ${delta:.2f} remaining")

    def _on_expense_deleted(self, row_index: int) -> None:
        if row_index < len(self.expenses):
            deleted_expense = self.expenses.pop(row_index)
            self._refresh_table()
            self._update_summary()
            save_csv_data(self.csv_path, self.expenses, FIELDS, self.password)
            self.app.notify(f"Deleted expense #{deleted_expense.get('serial', '')}")

    @on(DataTable.RowSelected)
    def _row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_row_index = event.cursor_row

    @on(Button.Pressed, "#btn-add")
    def _btn_add(self) -> None:
        self.action_add_expense()

    @on(Button.Pressed, "#btn-edit")
    def _btn_edit(self) -> None:
        self.action_edit_expense()

    @on(Button.Pressed, "#btn-delete")
    def _btn_delete(self) -> None:
        self.action_delete_expense()

    @on(Button.Pressed, "#btn-sort")
    def _btn_sort(self) -> None:
        self.action_toggle_sort()

    @on(Button.Pressed, "#btn-track")
    def _btn_track(self) -> None:
        self.action_track_budget()

    @on(Button.Pressed, "#btn-set")
    def _btn_set(self) -> None:
        self.action_set_budget()

    @on(Button.Pressed, "#btn-logout")
    def _btn_logout(self) -> None:
        self.action_logout()

    def action_add_expense(self) -> None:
        categories = self._get_all_categories()
        self.app.push_screen(AddExpenseScreen(self._on_expense_saved, categories=categories))

    def action_edit_expense(self) -> None:
        dt: DataTable[object] = self.query_one("#table", DataTable)
        cursor_row = dt.cursor_row
        row_index = cursor_row if cursor_row >= 0 else self.selected_row_index
        if row_index is None or row_index >= len(self.expenses):
            self.app.notify("Please navigate to a row to edit (use arrow keys)", severity="warning")
            return
        expense_to_edit = self.expenses[row_index].copy()
        categories = self._get_all_categories()
        self.app.push_screen(AddExpenseScreen(self._on_expense_saved, expense_to_edit, categories))

    def action_delete_expense(self) -> None:
        dt: DataTable[object] = self.query_one("#table", DataTable)
        cursor_row = dt.cursor_row
        row_index = cursor_row if cursor_row >= 0 else self.selected_row_index
        if row_index is None or row_index >= len(self.expenses):
            self.app.notify(
                "Please navigate to a row to delete (use arrow keys)", severity="warning"
            )
            return
        expense_to_delete = self.expenses[row_index].copy()
        self.app.push_screen(
            ConfirmDeleteScreen(expense_to_delete, lambda: self._on_expense_deleted(row_index))
        )

    def action_track_budget(self) -> None:
        today = date.today()
        self.app.push_screen(MonthPrompt(today.year, today.month, self._on_month_chosen))

    def action_set_budget(self) -> None:
        self.app.push_screen(BudgetPrompt(self.monthly_budget, self._on_budget_set))

    def action_toggle_sort(self) -> None:
        self.sort_order = not self.sort_order
        self.expenses = sort_data(self.expenses, reverse=self.sort_order)
        self._refresh_table()
        order = "descending" if self.sort_order else "ascending"
        self.app.notify(f"Expenses sorted in {order} order")

    def action_logout(self) -> None:
        save_csv_data(self.csv_path, self.expenses, FIELDS, self.password)
        self.config["monthly_budget"] = self.monthly_budget if self.monthly_budget > 0 else 0.0
        self.config["next_serial"] = self.next_serial
        save_config(self.cfg_path, self.config, self.password)
        self.app.pop_screen()


class BudgetApp(App[None]):
    TITLE = f"Budget App v{VERSION}"
    CSS = MainScreen.CSS

    def on_mount(self) -> None:
        auth = BcryptAuth(APP_NAME)

        def create_main_screen(user: str, pwd: str) -> MainScreen:
            encrypted = user_wants_encryption(APP_NAME, user)
            password = pwd if encrypted else None
            return MainScreen(user, password)

        self.push_screen(LoginScreen("Budget App — Login", auth, create_main_screen))


def main() -> None:
    """Entry point for the budget-app command."""
    BudgetApp().run()


if __name__ == "__main__":
    main()
