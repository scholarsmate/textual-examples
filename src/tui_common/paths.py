"""Path utilities for TUI apps."""

from pathlib import Path

from platformdirs import user_data_dir


def app_data_dir(app_name: str) -> Path:
    """Get the OS-standard data directory for an app, creating it if needed.

    Uses platformdirs to determine the correct location:
    - Windows: %LOCALAPPDATA%\\textual-apps\\{app_name}
    - macOS: ~/Library/Application Support/textual-apps/{app_name}
    - Linux: ~/.local/share/textual-apps/{app_name}

    Args:
        app_name: Name of the application

    Returns:
        Path to the application's data directory
    """
    app_dir = Path(user_data_dir(app_name, "textual-apps", roaming=False))
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def user_data_path(app_name: str, username: str, filename: str, encrypted: bool = False) -> Path:
    """Return the path to a user's data file with appropriate extension.

    Args:
        app_name: Name of the application
        username: Username
        filename: Base filename (e.g., "expenses.csv", "tasks.csv")
        encrypted: If True, adds .enc before the extension

    Returns:
        Full path with .enc inserted before extension if encrypted
    """
    base_path = app_data_dir(app_name) / f"{username}_{filename}"
    if encrypted:
        # Insert .enc before the file extension
        # "user_expenses.csv" -> "user_expenses.enc.csv"
        return base_path.with_suffix(f".enc{base_path.suffix}")
    return base_path


def user_config_path(app_name: str, username: str, encrypted: bool = False) -> Path:
    """Return the path to a user's configuration JSON file.

    Args:
        app_name: Name of the application
        username: Username
        encrypted: If True, uses .enc.json extension

    Returns:
        Full path to config file
    """
    return user_data_path(app_name, username, "config.json", encrypted)


def is_encrypted_file(path: Path) -> bool:
    """Check if a file path indicates an encrypted file.

    Args:
        path: File path to check

    Returns:
        True if path contains .enc. extension pattern
    """
    return ".enc." in str(path)
