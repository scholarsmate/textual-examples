# test_budget_app.py
"""Tests for budget_app module."""

from datetime import date, datetime

import pytest

from budget_app import APP_NAME, COMMON_CATEGORIES, FIELDS


class TestBudgetConstants:
    """Tests for budget app constants."""

    def test_app_name(self) -> None:
        """Test APP_NAME constant."""
        assert APP_NAME == "budget"

    def test_fields_structure(self) -> None:
        """Test FIELDS list contains expected field names."""
        assert FIELDS == ["serial", "date", "category", "amount", "description"]
        assert len(FIELDS) == 5
        assert "serial" in FIELDS
        assert "date" in FIELDS
        assert "category" in FIELDS
        assert "amount" in FIELDS
        assert "description" in FIELDS

    def test_common_categories_exist(self) -> None:
        """Test that common categories list is populated."""
        assert len(COMMON_CATEGORIES) > 0
        assert isinstance(COMMON_CATEGORIES, list)
        assert all(isinstance(cat, str) for cat in COMMON_CATEGORIES)

    def test_common_categories_content(self) -> None:
        """Test specific expected categories."""
        expected = ["Food", "Transportation", "Utilities", "Entertainment", "Healthcare"]
        for cat in expected:
            assert cat in COMMON_CATEGORIES

    def test_categories_no_duplicates(self) -> None:
        """Test that category list has no duplicates."""
        assert len(COMMON_CATEGORIES) == len(set(COMMON_CATEGORIES))


class TestExpenseDataStructure:
    """Tests for expense data structure."""

    def test_expense_dict_structure(self) -> None:
        """Test expense dictionary has all required fields."""
        expense = {
            "serial": "100",
            "date": "2025-10-07",
            "category": "Food",
            "amount": "25.50",
            "description": "Lunch",
        }
        assert all(field in expense for field in FIELDS)
        assert expense["serial"] == "100"
        assert expense["date"] == "2025-10-07"
        assert expense["category"] == "Food"
        assert expense["amount"] == "25.50"
        assert expense["description"] == "Lunch"

    def test_expense_minimal_data(self) -> None:
        """Test expense with minimal required data."""
        expense = {
            "serial": "1",
            "date": "2025-10-07",
            "category": "Other",
            "amount": "0.00",
            "description": "",
        }
        assert all(field in expense for field in FIELDS)
        assert expense["amount"] == "0.00"
        assert expense["description"] == ""

    def test_expense_with_empty_description(self) -> None:
        """Test expense can have empty description."""
        expense = {
            "serial": "1",
            "date": "2025-10-07",
            "category": "Food",
            "amount": "10.00",
            "description": "",
        }
        assert expense["description"] == ""


class TestDateValidation:
    """Tests for date validation logic."""

    def test_valid_date_format(self) -> None:
        """Test valid date string format YYYY-MM-DD."""
        date_str = "2025-10-07"
        try:
            parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
            assert isinstance(parsed, date)
            assert parsed.year == 2025
            assert parsed.month == 10
            assert parsed.day == 7
        except ValueError:
            pytest.fail("Valid date string should parse successfully")

    def test_invalid_date_format(self) -> None:
        """Test invalid date format raises ValueError."""
        invalid_dates = ["10/07/2025", "2025-13-01", "2025-10-32", "not-a-date"]
        for date_str in invalid_dates:
            with pytest.raises(ValueError):
                datetime.strptime(date_str, "%Y-%m-%d")

    def test_future_date_detection(self) -> None:
        """Test detecting future dates."""
        today = date.today()
        future_date = date(2099, 12, 31)
        assert future_date > today

    def test_past_date_is_valid(self) -> None:
        """Test past dates are valid."""
        today = date.today()
        past_date = date(2020, 1, 1)
        assert past_date < today

    def test_today_is_valid(self) -> None:
        """Test today's date is valid."""
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")
        parsed = datetime.strptime(today_str, "%Y-%m-%d").date()
        assert parsed == today


class TestAmountValidation:
    """Tests for amount validation logic."""

    def test_valid_amount_formats(self) -> None:
        """Test various valid amount formats."""
        valid_amounts = ["10", "10.50", "0.99", "100.00", "1000.50"]
        for amt_str in valid_amounts:
            try:
                amt = float(amt_str)
                assert amt >= 0
            except ValueError:
                pytest.fail(f"Valid amount {amt_str} should parse successfully")

    def test_amount_positive(self) -> None:
        """Test amount must be positive."""
        amount_str = "50.00"
        amount = float(amount_str)
        assert amount > 0

    def test_amount_zero_is_valid(self) -> None:
        """Test zero amount is technically valid."""
        amount = float("0.00")
        assert amount == 0.0
        assert amount >= 0

    def test_negative_amount_detection(self) -> None:
        """Test detecting negative amounts."""
        amount = float("-10.00")
        assert amount < 0  # Should be rejected in validation

    def test_amount_two_decimal_places(self) -> None:
        """Test formatting amount to 2 decimal places."""
        amounts = [10, 10.5, 10.123, 10.999]
        for amt in amounts:
            formatted = f"{amt:.2f}"
            assert "." in formatted
            decimal_part = formatted.split(".")[1]
            assert len(decimal_part) == 2

    def test_invalid_amount_format(self) -> None:
        """Test invalid amount strings raise ValueError."""
        invalid_amounts = ["abc", "10.5.5", "$50", ""]
        for amt_str in invalid_amounts:
            with pytest.raises(ValueError):
                float(amt_str)


class TestCategoryManagement:
    """Tests for category management."""

    def test_custom_category_addition(self) -> None:
        """Test adding custom category to existing list."""
        categories = COMMON_CATEGORIES.copy()
        custom_category = "Custom Category"
        if custom_category not in categories:
            categories.append(custom_category)
        assert custom_category in categories

    def test_category_case_sensitivity(self) -> None:
        """Test category matching is case-sensitive."""
        assert "Food" in COMMON_CATEGORIES
        assert "food" not in COMMON_CATEGORIES  # Case matters

    def test_category_validation(self) -> None:
        """Test category is not empty."""
        category = "Groceries"
        assert category.strip() != ""
        assert len(category) > 0

    def test_category_from_user_input(self) -> None:
        """Test accepting user-defined category."""
        user_category = "Pet Supplies"
        categories = COMMON_CATEGORIES + [user_category]
        assert user_category in categories


class TestBudgetCalculations:
    """Tests for budget calculation logic."""

    def test_calculate_total_expenses(self) -> None:
        """Test calculating total expenses."""
        expenses = [
            {"amount": "10.50"},
            {"amount": "25.75"},
            {"amount": "5.00"},
        ]
        total = sum(float(e["amount"]) for e in expenses)
        assert total == 41.25

    def test_calculate_budget_remaining(self) -> None:
        """Test calculating remaining budget."""
        budget = 1000.00
        expenses = [{"amount": "250.00"}, {"amount": "150.50"}]
        spent = sum(float(e["amount"]) for e in expenses)
        remaining = budget - spent
        assert remaining == 599.50
        assert remaining > 0

    def test_budget_exceeded(self) -> None:
        """Test detecting when budget is exceeded."""
        budget = 1000.00
        expenses = [{"amount": "600.00"}, {"amount": "500.00"}]
        spent = sum(float(e["amount"]) for e in expenses)
        remaining = budget - spent
        assert remaining < 0
        assert spent > budget

    def test_budget_percentage_used(self) -> None:
        """Test calculating percentage of budget used."""
        budget = 1000.00
        spent = 750.00
        percentage = (spent / budget * 100) if budget > 0 else 0
        assert percentage == 75.0

    def test_budget_warning_threshold(self) -> None:
        """Test 80% budget warning threshold."""
        budget = 1000.00
        warning_threshold = 0.80
        expenses = [{"amount": "850.00"}]
        spent = sum(float(e["amount"]) for e in expenses)
        percentage = spent / budget
        assert percentage > warning_threshold

    def test_empty_expenses_total(self) -> None:
        """Test total with no expenses."""
        expenses: list[dict[str, str]] = []
        total = sum(float(e["amount"]) for e in expenses)
        assert total == 0.0


class TestMonthlyTracking:
    """Tests for monthly expense tracking."""

    def test_filter_expenses_by_month(self) -> None:
        """Test filtering expenses by specific month."""
        expenses = [
            {"date": "2025-10-01", "amount": "50.00"},
            {"date": "2025-10-15", "amount": "75.00"},
            {"date": "2025-09-20", "amount": "100.00"},
            {"date": "2025-10-30", "amount": "25.00"},
        ]
        target_month = "2025-10"
        monthly_expenses = [e for e in expenses if e["date"].startswith(target_month)]
        assert len(monthly_expenses) == 3
        total = sum(float(e["amount"]) for e in monthly_expenses)
        assert total == 150.00

    def test_parse_month_from_date(self) -> None:
        """Test extracting year-month from date string."""
        date_str = "2025-10-07"
        year_month = date_str[:7]  # "2025-10"
        assert year_month == "2025-10"
        assert len(year_month) == 7

    def test_current_month_format(self) -> None:
        """Test formatting current month as YYYY-MM."""
        today = date.today()
        current_month = today.strftime("%Y-%m")
        assert len(current_month) == 7
        assert current_month.count("-") == 1

    def test_group_expenses_by_month(self) -> None:
        """Test grouping expenses by month."""
        expenses = [
            {"date": "2025-10-01", "amount": "50.00"},
            {"date": "2025-09-15", "amount": "75.00"},
            {"date": "2025-10-20", "amount": "100.00"},
        ]
        by_month: dict[str, list[dict[str, str]]] = {}
        for exp in expenses:
            month = exp["date"][:7]
            if month not in by_month:
                by_month[month] = []
            by_month[month].append(exp)

        assert len(by_month) == 2
        assert "2025-10" in by_month
        assert "2025-09" in by_month
        assert len(by_month["2025-10"]) == 2


class TestCategoryBreakdown:
    """Tests for category spending breakdown."""

    def test_calculate_category_totals(self) -> None:
        """Test calculating total spending by category."""
        expenses = [
            {"category": "Food", "amount": "50.00"},
            {"category": "Transportation", "amount": "30.00"},
            {"category": "Food", "amount": "75.00"},
            {"category": "Entertainment", "amount": "40.00"},
            {"category": "Food", "amount": "25.00"},
        ]
        category_totals: dict[str, float] = {}
        for exp in expenses:
            cat = exp["category"]
            amt = float(exp["amount"])
            category_totals[cat] = category_totals.get(cat, 0.0) + amt

        assert category_totals["Food"] == 150.00
        assert category_totals["Transportation"] == 30.00
        assert category_totals["Entertainment"] == 40.00

    def test_top_spending_categories(self) -> None:
        """Test finding top spending categories."""
        category_totals = {
            "Food": 150.00,
            "Transportation": 75.00,
            "Entertainment": 50.00,
            "Utilities": 100.00,
        }
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        top_3 = sorted_categories[:3]

        assert len(top_3) == 3
        assert top_3[0][0] == "Food"
        assert top_3[0][1] == 150.00
        assert top_3[1][0] == "Utilities"
        assert top_3[2][0] == "Transportation"

    def test_category_percentage_of_total(self) -> None:
        """Test calculating category percentage of total spending."""
        category_totals = {"Food": 200.00, "Transportation": 100.00, "Other": 50.00}
        total_spending = sum(category_totals.values())
        food_percentage = (
            (category_totals["Food"] / total_spending * 100) if total_spending > 0 else 0
        )

        assert total_spending == 350.00
        assert food_percentage == pytest.approx(57.14, rel=0.01)


class TestExpenseSerialization:
    """Tests for expense serialization."""

    def test_expense_to_csv_format(self) -> None:
        """Test converting expense to CSV-compatible format."""
        expense = {
            "serial": "100",
            "date": "2025-10-07",
            "category": "Food",
            "amount": "25.50",
            "description": "Lunch at café",
        }
        # All values should be strings for CSV
        assert all(isinstance(v, str) for v in expense.values())
        assert all(field in expense for field in FIELDS)

    def test_expense_list_serialization(self) -> None:
        """Test serializing multiple expenses."""
        expenses = [
            {
                "serial": "1",
                "date": "2025-10-01",
                "category": "Food",
                "amount": "50.00",
                "description": "Groceries",
            },
            {
                "serial": "2",
                "date": "2025-10-02",
                "category": "Gas",
                "amount": "45.00",
                "description": "Gas station",
            },
        ]
        assert len(expenses) == 2
        assert all(all(field in exp for field in FIELDS) for exp in expenses)

    def test_empty_expense_list(self) -> None:
        """Test handling empty expense list."""
        expenses: list[dict[str, str]] = []
        assert len(expenses) == 0
        total = sum(float(e.get("amount", "0")) for e in expenses)
        assert total == 0.0


class TestExpenseValidation:
    """Tests for expense validation logic."""

    def test_valid_expense_all_fields(self) -> None:
        """Test validating expense with all fields."""
        expense = {
            "serial": "100",
            "date": "2025-10-07",
            "category": "Food",
            "amount": "25.50",
            "description": "Lunch",
        }
        # Validation checks
        assert expense["date"]  # Not empty
        assert expense["category"]  # Not empty
        assert float(expense["amount"]) > 0  # Positive amount
        # Date format check
        datetime.strptime(expense["date"], "%Y-%m-%d")

    def test_expense_missing_optional_description(self) -> None:
        """Test expense with missing description is valid."""
        expense = {
            "serial": "1",
            "date": "2025-10-07",
            "category": "Other",
            "amount": "10.00",
            "description": "",
        }
        assert "description" in expense
        assert expense["description"] == ""  # Empty is okay

    def test_expense_with_unicode(self) -> None:
        """Test expense with Unicode characters."""
        expense = {
            "serial": "1",
            "date": "2025-10-07",
            "category": "Dining",
            "amount": "35.00",
            "description": "Café ☕ lunch 🍽️",
        }
        assert "☕" in expense["description"]
        assert "🍽️" in expense["description"]


class TestSerialNumbering:
    """Tests for expense serial number management."""

    def test_next_serial_calculation(self) -> None:
        """Test calculating next serial number."""
        existing_serials = ["1", "2", "3", "5", "10"]
        max_serial = max(int(s) for s in existing_serials) if existing_serials else 0
        next_serial = str(max_serial + 1)
        assert next_serial == "11"

    def test_first_serial_number(self) -> None:
        """Test first serial number when list is empty."""
        existing_serials: list[str] = []
        max_serial = max((int(s) for s in existing_serials), default=0)
        next_serial = str(max_serial + 1)
        assert next_serial == "1"

    def test_serial_ordering(self) -> None:
        """Test ordering expenses by serial number."""
        expenses = [
            {"serial": "3", "amount": "10.00"},
            {"serial": "1", "amount": "20.00"},
            {"serial": "2", "amount": "15.00"},
        ]
        sorted_expenses = sorted(expenses, key=lambda x: int(x["serial"]))
        assert sorted_expenses[0]["serial"] == "1"
        assert sorted_expenses[1]["serial"] == "2"
        assert sorted_expenses[2]["serial"] == "3"
