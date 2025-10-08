# conftest.py
"""Shared pytest configuration and fixtures."""

import sys
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

# Add the src directory to the path so tests can import the modules
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Isolate each test to use a temporary data directory.

    This prevents tests from interfering with each other and with
    the user's actual application data.
    """
    test_data_dir = tmp_path / "test_data"
    test_data_dir.mkdir(parents=True, exist_ok=True)

    # Mock platformdirs.user_data_dir where it's imported in tui_common.paths
    def mock_user_data_dir(
        appname: str,
        appauthor: str | None = None,
        version: str | None = None,
        roaming: bool = False,
        ensure_exists: bool = True,
    ) -> str:
        app_dir = test_data_dir / appname
        if ensure_exists:
            app_dir.mkdir(parents=True, exist_ok=True)
        return str(app_dir)

    # Patch it in the tui_common.paths module where it's actually used
    monkeypatch.setattr("tui_common.paths.user_data_dir", mock_user_data_dir)
