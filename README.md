# textual-tui-starter

Two professional Textual (Textualize) TUI apps demonstrating shared authentication and data management:

- **`task_app.py`** — Simple task manager with CRUD operations
- **`budget_app.py`** — Full-featured expense tracker with budget monitoring

Both apps share a common bcrypt-based authentication layer with support for optional data encryption.

## Quickstart

```bash
git clone https://github.com/scholarsmate/textual-examples.git
cd textual-examples
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# (Optional) keep packaging tools current
python -m pip install --upgrade pip
pip install -r requirements.txt

# Launch in the terminal
python ./src/task_app/main.py
python ./src/budget_app/main.py

# Optional: run either app in the browser (Textual web mode)
python -m textual run --web --port 8000 ./src/task_app/main.py
python -m textual run --web --port 8000 ./src/budget_app/main.py
```

### Hatch one-liners

Hatch is integrated for development and QA. Install Hatch and use these scripts:

```powershell
# Windows PowerShell
hatch run task         # runs task-app
hatch run budget       # runs budget-app
hatch run task-web     # task app in browser
hatch run budget-web   # budget app in browser

# QA helpers
hatch run test         # pytest
hatch run cov          # pytest with coverage
hatch run lint         # ruff
hatch run format       # black
```

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
- **Current Version:** `1.0.2`
- **Version Location:** The `VERSION` file at the project root
- **Display:** Version is shown in the window title bar and header (e.g., "Task App v1.0.2")

### Version Components

- **MAJOR**: Incremented for incompatible API changes or breaking changes
- **MINOR**: Incremented for new features added in a backwards-compatible manner
- **PATCH**: Incremented for backwards-compatible bug fixes

### Updating the Version

To release a new version:

Using Hatch version management (recommended):

```powershell
# Bump the version stored in VERSION (choose one):
hatch version patch   # X.Y.(Z+1)
hatch version minor   # X.(Y+1).0
hatch version major   # (X+1).0.0

# Then commit and tag in git
git add VERSION
git commit -m "Bump version to $(Get-Content VERSION)"
git tag v$(Get-Content VERSION)
git push origin main
git push origin v$(Get-Content VERSION)
```

Manual approach (still works):

1. Update the `VERSION` file with the new version number
2. Commit the changes: `git commit -m "Bump version to X.Y.Z"`
3. Tag the release: `git tag vX.Y.Z`
4. Push with tags: `git push origin main && git push origin vX.Y.Z`

**CI/CD Integration**: When you push a version tag (e.g., `v1.0.2`), GitHub Actions automatically:

- Builds both packages with Hatch from `packages/task-app` and `packages/budget-app`
- Creates a GitHub Release with wheel and source distribution files
- Uploads artifacts for both Task App and Budget App

See [CI-CD-SETUP.md](CI-CD-SETUP.md) for detailed information on automated builds and releases.

The version is automatically read from the `VERSION` file at runtime using the `get_version()` function from `tui_common`. The VERSION file is packaged with each app for runtime access.

## Installation

The apps are packaged separately, so you can install just the one you need!

### Option 1: Install from Wheel Files (Recommended)

Download the latest wheel files from [GitHub Releases](https://github.com/scholarsmate/textual-examples/releases):

```bash
# Task app
pip install textual-task-app-1.0.2-py3-none-any.whl

# Budget app
pip install textual-budget-app-1.0.2-py3-none-any.whl

# Run the apps
task-app
budget-app
```

### Option 2: Build and Install from Source (per-package with Hatch)

```bash
git clone https://github.com/scholarsmate/textual-examples.git
cd textual-examples

pip install -r requirements.txt

# Build both packages (one command)
hatch run build-all

# Install from built wheels (pick the version built on your machine)
pip install packages/task-app/dist/textual-task-app-*.whl
pip install packages/budget-app/dist/textual-budget-app-*.whl

# Run the apps
task-app
budget-app

### Option 2b: Editable install for development (easiest CLI)

```powershell
pip install -e .

# Then use the console scripts (works from anywhere)
task-app
budget-app
```

### Option 3: Development / Run from Source

```bash
git clone https://github.com/scholarsmate/textual-examples.git
cd textual-examples
python -m venv .venv

# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Run in the terminal
python ./src/task_app/main.py
python ./src/budget_app/main.py

# Textual web mode (in-browser)
# Launch Task app in browser
python -m textual run --web --port 8000 ./src/task_app/main.py

# Launch Budget app in browser
python -m textual run --web --port 8000 ./src/budget_app/main.py
```

## Building Distribution Packages

Use the per-package builds from Option 2 above. Artifacts will be created in each package's `dist/` directory:

- `packages/task-app/dist/textual-task-app-<version>-py3-none-any.whl`
- `packages/task-app/dist/textual-task-app-<version>.tar.gz`
- `packages/budget-app/dist/textual-budget-app-<version>-py3-none-any.whl`
- `packages/budget-app/dist/textual-budget-app-<version>.tar.gz`

See [PACKAGING.md](PACKAGING.md) for detailed information about the packaging architecture.

## Usage

### First Run

1. Launch either app: `task-app` or `budget-app` (after installing), or use `hatch run task` / `hatch run budget`
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

### Data Storage Location

Application data is stored in OS-standard locations using `platformdirs`:

- **Windows**: `%LOCALAPPDATA%\textual-apps\{app_name}` (e.g., `C:\Users\YourName\AppData\Local\textual-apps\tasks`)
- **macOS**: `~/Library/Application Support/textual-apps/{app_name}`
- **Linux**: `~/.local/share/textual-apps/{app_name}`

### Directory Structure

```raw
{OS-specific-data-dir}/textual-apps/
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

- **Location:** `{OS-data-dir}/textual-apps/budget/{username}_config.json` (or `{username}_config.enc.json` if encrypted)
- **Note:** If encryption is enabled, the config file is encrypted with your password
- The app automatically suggests categories from your existing expenses
- Common categories are built into the app for autocomplete
- **Config Example (if you need to manually edit):**

  ```json
  {
    "monthly_budget": 2112.0,
    "next_serial": 42
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

- Set a monthly budget limit (e.g., 2000.00)
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

## Hatch commands

These Hatch scripts are available:

```powershell
hatch run task         # run task app in terminal
hatch run budget       # run budget app in terminal
hatch run task-web     # run task app in browser (Textual web mode)
hatch run budget-web   # run budget app in browser (Textual web mode)

# QA
hatch run test         # run pytest
hatch run cov          # run pytest with coverage
hatch run lint         # ruff
hatch run format       # black
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

# With Hatch
hatch run test
```

#### Test Coverage Snapshot (pytest 8.4.2, Python 3.13)

- 141 total tests across three modules (`tests/test_tui_common.py`, `tests/test_task_app.py`, `tests/test_budget_app.py`)
- Critical paths (authentication, encryption, file I/O helpers) maintain 95–100% coverage
- Interactive Textual screens intentionally remain partially untested due to UI event loop constraints

### Project Structure

```text
src/
├── tui_common/          # Shared library (no duplication in git)
│   ├── __init__.py      # Public API exports
│   ├── auth.py          # User authentication (bcrypt)
│   ├── crypto.py        # Encryption utilities (Fernet)
│   ├── data.py          # CSV/JSON file operations
│   ├── paths.py         # OS-standard path management
│   ├── screens.py       # Login/registration UI
│   └── version.py       # Version reading
├── task_app/
│   ├── __init__.py
│   └── main.py          # Task management app
└── budget_app/
    ├── __init__.py
    └── main.py          # Budget tracking app

Root files:
├── VERSION              # Semantic version (packaged with apps)
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
├── packages/            # Per-app Hatch projects
│   ├── task-app/        # textual-task-app build config
│   └── budget-app/      # textual-budget-app build config
├── (no Makefile)       # Use Hatch scripts instead
└── tests/              # Comprehensive test suite
    ├── conftest.py      # Test fixtures (isolated data dirs)
    ├── test_tui_common.py
    ├── test_task_app.py
    └── test_budget_app.py
```

**Packaging Architecture:**

- Source code in `src/` has NO duplication
- Two Hatch projects under `packages/` build separate distributions
- Each package includes `tui_common` and a copy of `VERSION` for runtime
- Build artifacts (`build/`, `dist/`) are gitignored

See [PACKAGING.md](PACKAGING.md) for detailed architecture documentation.

## Application Dependencies

- **textual** >= 6.2.1 - Terminal UI framework
- **bcrypt** >= 5.0.0 - Password hashing
- **cryptography** >= 43.0.3 - Data encryption (Fernet)
- **rich** >= 14.1.0 - Rich text formatting
- **platformdirs** >= 3.0.0 - OS-standard directory locations

## Development Dependencies

- **pytest** - Testing framework
- **pytest-cov** - Code coverage reporting
- **ruff** - Fast Python linter
- **black** - Code formatter
- **mypy** - Static type checker
- **pyright** - Type checker
- **hatch** - Build and environment runner

## License

Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). See the `LICENSE` file for full terms and attribution guidelines.
