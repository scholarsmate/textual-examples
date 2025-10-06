# textual-tui-starter

Two professional Textual (Textualize) TUI apps demonstrating shared authentication and data management:

- **`task_app.py`** — Simple task manager with CRUD operations
- **`budget_app.py`** — Full-featured expense tracker with budget monitoring

Both apps share a common bcrypt-based authentication layer with support for optional data encryption.

## Features

### Task App

- ✅ Create, edit, delete, and toggle tasks
- 📝 Tasks include serial number, title, notes, and completion status
- 💾 Per-user CSV storage with JSON config (matching budget app pattern)
- 🔢 Auto-incrementing serial numbers for unique task IDs
- 📊 DataTable display showing all task details with status indicators
- 🎯 Keyboard shortcuts and toolbar UI matching budget app
- 🔐 Secure authentication with bcrypt
- 🔒 Optional data encryption (both CSV and config files)
- ⚡ Auto-save on all operations
- 🔄 Sortable by serial number (ascending/descending)

### Budget App

- 💰 Track expenses with date, category, amount, and description
- 📊 Monthly budget setting and tracking
- ⚠️ Automatic budget warnings when limits exceeded
- 📅 Monthly spending summaries with category breakdowns
- 🔢 Auto-incrementing expense serial numbers
- 🏷️ Category autocomplete with customizable categories
- 📈 Track spending for any past month
- 💾 Per-user CSV storage for expenses
- 📊 DataTable display showing all expense details
- 🎯 Keyboard shortcuts and toolbar UI matching task app
- 🔐 Secure authentication with bcrypt
- 🔒 Optional data encryption (both CSV and config files)
- ✏️ Full CRUD operations with validation
- 🎯 Keyboard shortcuts and button UI
- ⚡ Auto-save on all operations
- 🔄 Sortable by serial number (ascending/descending)

## Versioning

This project follows [Semantic Versioning](https://semver.org/) (SemVer):

- **Version Format:** MAJOR.MINOR.PATCH (e.g., 1.0.0)
- **Current Version:** `1.0.0`
- **Version Location:** The `VERSION` file at the project root
- **Display:** Version is shown in the window title bar and header (e.g., "Task App v1.0.0")

### Version Components

- **MAJOR**: Incremented for incompatible API changes or breaking changes
- **MINOR**: Incremented for new features added in a backwards-compatible manner
- **PATCH**: Incremented for backwards-compatible bug fixes

### Updating the Version

To release a new version:

1. Update the `VERSION` file with the new version number
2. Commit the change: `git commit -m "Bump version to X.Y.Z"`
3. Tag the release: `git tag vX.Y.Z`
4. Push with tags: `git push --tags`

The version is automatically read from the `VERSION` file at runtime using the `get_version()` function in `tui_common.py`.

## Quickstart

```bash
git clone https://github.com/scholarsmate/textual-examples.git
cd textual-tui-starter
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python task_app.py     # Task app
python budget_app.py   # Budget app
```

## Usage

### First Run

1. Launch either app: `python task_app.py` or `python budget_app.py`
2. Click "Register" to create a new account
3. Enter username and password
4. Choose whether to encrypt your data (recommended for sensitive information)
5. Start using the app!

### Budget App Controls

- **Keyboard Shortcuts:**
  - `a` - Add new expense
  - `e` - Edit selected expense (use arrow keys to select)
  - `d` - Delete selected expense
  - `t` - Track budget for specific month
  - `b` - Set monthly budget
  - `s` - Toggle sort order (ascending/descending)
  - `q` - Logout (auto-saves)
- **Mouse:** Click buttons for same actions
- **Navigation:** Use arrow keys to navigate expense table

### Task App Controls

- **Keyboard Shortcuts:**
  - `a` - Add new task
  - `e` - Edit selected task (use arrow keys to select)
  - `t` - Toggle task completion status
  - `d` - Delete selected task
  - `s` - Toggle sort order (ascending/descending)
  - `q` - Logout (auto-saves)
- **Mouse:** Click buttons for same actions
- **Navigation:** Use arrow keys to navigate task list
- **Task Status:** ⬜ Pending or ✅ Completed indicators

## Data & Auth

### Directory Structure

```raw
data/
├── budget/
│   ├── users.json                    # User credentials (bcrypt hashes + encryption preference)
│   ├── {username}_expenses.csv       # User's expenses (plain text)
│   ├── {username}_expenses.enc.csv   # User's expenses (encrypted)
│   ├── {username}_config.json        # User's config (plain text)
│   └── {username}_config.enc.json    # User's config (encrypted)
└── tasks/
    ├── users.json                    # User credentials (bcrypt hashes + encryption preference)
    ├── {username}_tasks.csv          # User's tasks (plain text)
    ├── {username}_tasks.enc.csv      # User's tasks (encrypted)
    ├── {username}_config.json        # User's config (plain text)
    └── {username}_config.enc.json    # User's config (encrypted)
```

### Authentication

- Passwords are hashed with bcrypt (12 rounds, salt included in hash)
- Each app maintains separate user databases in `data/{app_name}/users.json`
- Encryption status is set during registration and stored with user profile
- User database stores: hashed password + encryption preference

### Data Encryption

Both apps support **optional data encryption** configured at registration:

- **Encryption Method:** Fernet (symmetric encryption) with PBKDF2-derived keys
- **Key Derivation:** PBKDF2-HMAC-SHA256 (100,000 iterations)
- **What Gets Encrypted:** CSV data files and JSON config files
- **File Extensions:** Encrypted files use `.enc.csv` and `.enc.json` extensions
- **Security:**
  - Each file is encrypted with a unique salt (stored with the file)
  - Password is never stored; only the bcrypt hash is saved
  - If you forget your password, encrypted data cannot be recovered
- **When to Use Encryption:**
  - ✅ Recommended for sensitive financial data (Budget App)
  - ✅ Recommended if storing personal task information (Task App)
  - ⚠️ Not needed if convenience is more important than security

### Data Storage

- **Tasks**: Stored as CSV with serial, title, notes, done status
- **Task Config**: JSON file containing:
  - `next_serial`: Auto-incrementing ID for tasks
- **Budget Expenses**: Stored as CSV with serial, date, category, amount, description
- **Budget Config**: JSON file containing:
  - `monthly_budget`: Your monthly spending limit
  - `next_serial`: Auto-incrementing ID for expenses

### Customizing Budget Categories

To customize expense categories, edit your config file:

- **Location:** `data/budget/{username}_config.json` (or `{username}_config.enc.json` if encrypted)
- **Note:** If encryption is enabled, the config file is encrypted with your password
- The app automatically suggests categories from your existing expenses
- Common categories are built into the app for autocomplete
- **Config Example (if you need to manually edit):**

  ```json
  {
    "monthly_budget": 2000.0,
    "next_serial": 14
  }
  ```

- Categories from your existing expenses are automatically included in autocomplete suggestions

## Task App Details

### Task Management

- Tasks are sorted by serial number (newest first by default, toggleable)
- Each task gets a unique serial number
- Edit any task while preserving its serial number
- Tasks show visual status indicators (⬜ Pending / ✅ Completed)
- Toggle completion status with 't' key or button
- Auto-save on every change

### Task Storage

- CSV format: serial, title, notes, done
- Config tracks next available serial number
- Optional encryption protects your task data

## Budget App Details

### Validation

- **Date:** Must be YYYY-MM-DD format and not in the future
- **Amount:** Must be a positive number (automatically formatted to 2 decimals)
- **Category:** Required field with autocomplete suggestions

### Monthly Budget Features

- Set a monthly budget limit (e.g., $2000)
- View current month's spending summary at the top of the screen
- See top 3 spending categories
- Get alerts when approaching or exceeding budget:
  - ⚠️ Warning when 80%+ of budget is used
  - 🚨 Error notification when budget is exceeded
- Track any past month to compare against budget

### Expense Management

- Expenses are sorted by serial number (newest first by default, toggleable)
- Each expense gets a unique serial number
- Edit any expense while preserving its serial number
- Confirmation dialog before deletion with expense details
- Auto-save on every change
- Budget warnings displayed when saving expenses

## Make targets (optional)

If you have `make` installed:

```bash
make venv       # create virtual environment
make install    # install dependencies into venv
make task       # run task app
make budget     # run budget app
```

## Development

### Code Quality: Ruff + Black via pre-commit

```bash
pip install -r requirements.txt
pre-commit install           # set up git hook
pre-commit run --all-files   # lint/format once
```

### Type Checking

Type hints are included throughout. Check with:

```bash
pip install mypy pyright
mypy .
pyright
```

### Testing

Comprehensive test suite with 100% code coverage in the `tests/` directory:

```bash
# Run all tests with coverage report
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_tui_common.py

# Run specific test class
pytest tests/test_tui_common.py::TestEncryption

# Run specific test
pytest tests/test_tui_common.py::TestEncryption::test_encrypt_decrypt_roundtrip

# Generate HTML coverage report
pytest --cov-report=html
# Open htmlcov/index.html in browser

# Using Makefile
make test
```

Test coverage:

- **141 total tests** across 3 test files
  - `test_tui_common.py` (68 tests) - 100% coverage of authentication, encryption & version management
  - `test_task_app.py` (28 tests) - Task data model, business logic, and confirmation dialogs
  - `test_budget_app.py` (45 tests) - Budget data model and calculations
- Tests cover authentication, encryption, file I/O, data validation, and business logic
- Fixtures for temporary directories and test data
- Both positive and negative test cases

### Project Structure

- `budget_app.py` - Budget tracking application
- `task_app.py` - Task management application  
- `tui_common.py` - Shared authentication and encryption utilities
- `tui_screens.py` - Shared login/registration screens
- `VERSION` - Semantic version number (e.g., 1.0.0)
- `tests/` - Comprehensive test suite (141 tests)
  - `test_tui_common.py` - Tests for tui_common module (100% coverage)
  - `test_task_app.py` - Tests for task app data models
  - `test_budget_app.py` - Tests for budget app data models
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Project configuration (Black, Ruff, Pytest)
- `Makefile` - Convenience commands

## Dependencies

- **textual** - Terminal UI framework
- **bcrypt** - Password hashing
- **cryptography** - Optional data encryption (Fernet)
- **pre-commit** (dev) - Git hooks for code quality
- **ruff** (dev) - Fast Python linter
- **black** (dev) - Code formatter

## License

See LICENSE file for details.
