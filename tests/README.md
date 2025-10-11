# Tests Directory

This directory contains the test suite for the textual-examples project.

## Structure

```text
tests/
├── __init__.py           # Makes tests a package
├── conftest.py           # Shared pytest configuration and fixtures
├── test_tui_common.py    # Tests for tui_common module
├── test_task_app.py      # Tests for task_app module
└── test_budget_app.py    # Tests for budget_app module
```

## Running Tests

### All Tests

```bash
pytest
```

### Specific Test File

```bash
pytest tests/test_tui_common.py
pytest tests/test_task_app.py
pytest tests/test_budget_app.py
```

### Specific Test Class

```bash
pytest tests/test_tui_common.py::TestEncryption -v
```

### Specific Test Function

```bash
pytest tests/test_tui_common.py::TestEncryption::test_encrypt_decrypt_roundtrip -v
```

### With Coverage

```bash
pytest --cov=task_app --cov=budget_app --cov=tui_common --cov-report=html
```

### Using Hatch

```bash
hatch run test
```

## Test Coverage

- Current suite: 141 tests across 3 files
- tui_common: Core helpers and crypto fully tested
- task_app: Data models and business logic covered
- budget_app: Data models and calculations covered

## Test Organization

Tests are organized by module and functionality:

### test_tui_common.py (66 tests)

- Authentication and user management
- Encryption and cryptographic operations
- File I/O (CSV/JSON, encrypted/plaintext)
- Configuration management
- Data sorting and validation

### test_task_app.py (26 tests)

- Task dataclass creation and manipulation
- Task serialization and persistence
- Task filtering, searching, and ordering
- Validation and error handling
- Unicode and special character support

### test_budget_app.py (45 tests)

- Expense data structure and validation
- Date and amount validation
- Category management
- Budget calculations and tracking
- Monthly expense grouping
- Category spending breakdown
- Serial number management

## Fixtures

Common fixtures are defined in `conftest.py`:

- Path setup for module imports

Test-specific fixtures in `test_tui_common.py`:

- `temp_dir` - Temporary directory for test data
- `app_name` - Test application name
- `test_user` - Test user credentials

## Adding New Tests

1. Create a new test file: `test_<module_name>.py`
2. Import pytest and the module to test
3. Organize tests into classes by functionality
4. Use descriptive test names: `test_<functionality>_<scenario>`
5. Add docstrings explaining what each test validates
6. Run tests to verify they pass: `pytest tests/test_<module_name>.py`

## Continuous Integration

All checks must pass before code is merged:

- ✅ pytest (all tests passing)
- ✅ mypy (no type errors)
- ✅ ruff (no linting errors)
- ✅ coverage thresholds enforced in CI
