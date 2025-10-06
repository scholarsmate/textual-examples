# Tests Directory

This directory contains the test suite for the textual-examples project.

## Structure

```
tests/
├── __init__.py           # Makes tests a package
├── conftest.py           # Shared pytest configuration and fixtures
├── test_tui_common.py    # Tests for tui_common.py module (66 tests)
├── test_task_app.py      # Tests for task_app.py module (26 tests)
└── test_budget_app.py    # Tests for budget_app.py module (45 tests)
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
pytest --cov=tui_common --cov-report=html
```

### Using Makefile

```bash
make test
```

## Test Coverage

- **137 total tests** across 3 test files
- **tui_common.py**: 100% coverage (177/177 lines)
- **task_app.py**: Data models and business logic tested
- **budget_app.py**: Data models and calculations tested

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

All tests must pass before code is merged:

- ✅ pytest (all tests passing)
- ✅ mypy (no type errors)
- ✅ ruff (no linting errors)
- ✅ 100% code coverage maintained
