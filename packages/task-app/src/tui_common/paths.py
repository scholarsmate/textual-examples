"""Path utilities for TUI apps."""

from pathlib import Path

from platformdirs import user_data_dir


def app_data_dir(app_name: str) -> Path:
    """Get the OS-standard data directory for an app, creating it if needed."""
    app_dir = Path(user_data_dir(app_name, "textual-apps", roaming=False))
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def user_data_path(app_name: str, username: str, filename: str, encrypted: bool = False) -> Path:
    base_path = app_data_dir(app_name) / f"{username}_{filename}"
    if encrypted:
        return base_path.with_suffix(f".enc{base_path.suffix}")
    return base_path


def user_config_path(app_name: str, username: str, encrypted: bool = False) -> Path:
    return user_data_path(app_name, username, "config.json", encrypted)


def is_encrypted_file(path: Path) -> bool:
    return ".enc." in str(path)
