"""Version utilities."""

from pathlib import Path


def get_version() -> str:
    """Get application version from VERSION file."""
    version_file_dev = Path(__file__).parent.parent.parent / "VERSION"
    version_file_installed = Path(__file__).parent / "VERSION"
    if version_file_installed.exists():
        return version_file_installed.read_text(encoding="utf-8").strip()
    elif version_file_dev.exists():
        return version_file_dev.read_text(encoding="utf-8").strip()
    return "unknown"
