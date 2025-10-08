"""Version utilities."""

from pathlib import Path


def get_version() -> str:
    """Get application version from VERSION file."""
    # In development: Look for VERSION file in project root (2 levels up from this file)
    # In installed package: Look for VERSION file next to this module (packaged with tui_common)
    version_file_dev = Path(__file__).parent.parent.parent / "VERSION"
    version_file_installed = Path(__file__).parent / "VERSION"

    if version_file_installed.exists():
        return version_file_installed.read_text(encoding="utf-8").strip()
    elif version_file_dev.exists():
        return version_file_dev.read_text(encoding="utf-8").strip()
    return "unknown"
