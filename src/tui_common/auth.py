"""Authentication and user management for TUI apps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

import bcrypt

from .paths import app_data_dir


class AuthProvider(Protocol):
    """Protocol for authentication providers."""

    def create_user(self, username: str, password: str, encrypt_data: bool = False) -> None:
        """Create a new user."""
        ...

    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials."""
        ...

    def user_exists(self, username: str) -> bool:
        """Check if user exists."""
        ...


def users_db_path(app_name: str) -> Path:
    """Get path to users database for an app."""
    return app_data_dir(app_name) / "users.json"


def load_users(path: Path) -> dict[str, dict[str, Any]]:
    """Load users from JSON. Handles both old (str) and new (dict) formats."""
    if path.exists():
        with path.open(encoding="utf-8") as f:
            users: dict[str, Any] = json.load(f)
            # Migrate old format to new format
            for username, data in users.items():
                if isinstance(data, str):
                    # Old format: username -> hashed_password
                    users[username] = {"password": data, "encrypt_data": False}
            result: dict[str, dict[str, Any]] = users
            return result
    return {}


def save_users(path: Path, users: dict[str, dict[str, Any]]) -> None:
    """Save users to JSON."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def create_user(app_name: str, username: str, password: str, encrypt_data: bool = False) -> None:
    """Create a new user with optional data encryption."""
    if not username or not password:
        raise ValueError("username/password required")
    path = users_db_path(app_name)
    users = load_users(path)
    if username in users:
        raise ValueError("user exists")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
    users[username] = {"password": hashed, "encrypt_data": encrypt_data}
    save_users(path, users)


def verify_user(app_name: str, username: str, password: str) -> bool:
    """Verify user credentials."""
    path = users_db_path(app_name)
    users = load_users(path)
    user_data = users.get(username)
    if not user_data:
        return False
    hashed = user_data.get("password", "")
    return bool(hashed and bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8")))


def user_wants_encryption(app_name: str, username: str) -> bool:
    """Check if user has encryption enabled."""
    path = users_db_path(app_name)
    users = load_users(path)
    user_data = users.get(username)
    if not user_data:
        return False
    result: bool = bool(user_data.get("encrypt_data", False))
    return result


class BcryptAuth:
    """Authentication provider using bcrypt for password hashing."""

    def __init__(self, app_name: str):
        """Initialize auth provider with app name for data isolation."""
        self.app_name = app_name

    def create_user(self, username: str, password: str, encrypt_data: bool = False) -> None:
        """Create a new user with hashed password and optional data encryption."""
        create_user(self.app_name, username, password, encrypt_data)

    def verify_user(self, username: str, password: str) -> bool:
        """Verify username and password against stored bcrypt hash."""
        return verify_user(self.app_name, username, password)

    def user_exists(self, username: str) -> bool:
        """Check if a user already exists."""
        path = users_db_path(self.app_name)
        users = load_users(path)
        return username in users
