# tui_common.py
"""Common utilities for TUI apps."""

import base64
import csv
import io
import json
import os
import sys
from pathlib import Path
from typing import Any, cast

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from tui_screens import AuthProvider


def get_version() -> str:
    """Get application version from VERSION file."""
    version_file = Path(__file__).parent / "VERSION"
    return version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unknown"


def app_data_dir(app_name: str) -> Path:
    base = Path(sys.argv[0]).resolve().parent / "data" / app_name
    base.mkdir(parents=True, exist_ok=True)
    return base


def users_db_path(app_name: str) -> Path:
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


# Encryption utilities
def derive_key(password: str, salt: bytes) -> bytes:
    """Derive an encryption key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)


def encrypt_data(data: str, password: str) -> bytes:
    """Encrypt string data using password. Returns salt + encrypted data."""
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(data.encode("utf-8"))
    # Prefix with salt so we can decrypt later
    return salt + encrypted


def decrypt_data(encrypted_data: bytes, password: str) -> str:
    """Decrypt data using password. First 16 bytes are the salt."""
    salt = encrypted_data[:16]
    encrypted = encrypted_data[16:]
    key = derive_key(password, salt)
    f = Fernet(key)
    decrypted = f.decrypt(encrypted)
    return decrypted.decode("utf-8")


class BcryptAuth(AuthProvider):
    """Authentication provider using bcrypt for password hashing.

    Delegates to tui_common for actual user creation and verification.
    """

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


def load_csv_data(path: Path, password: str | None = None) -> list[dict[str, str]]:
    """Load CSV data from file, auto-detecting encryption from extension.

    Args:
        path: Path to CSV file (.csv for plaintext, .enc.csv for encrypted)
        password: Password for decryption (required if file is encrypted)

    Returns:
        List of dictionaries representing CSV rows

    Raises:
        ValueError: If encrypted file is accessed without password or vice versa
    """
    if not path.exists():
        return []

    encrypted = is_encrypted_file(path)

    # Validate password matches file type
    if encrypted and password is None:
        raise ValueError(f"File {path} is encrypted but no password provided")
    if not encrypted and password is not None:
        raise ValueError(f"File {path} is plaintext but password was provided")

    if encrypted:
        # Encrypted file - read binary, decrypt, parse CSV
        with path.open("rb") as f:
            encrypted_data = f.read()
        # Type checker: we've already validated password is not None above
        assert password is not None
        csv_text = decrypt_data(encrypted_data, password)
        reader = csv.DictReader(csv_text.splitlines())
        return list(reader)
    else:
        # Plain text file
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))


def save_csv_data(
    path: Path, rows: list[dict[str, Any]], fieldnames: list[str], password: str | None = None
) -> None:
    """Save CSV data to file with appropriate extension based on encryption.

    Args:
        path: Path to CSV file (.csv for plaintext, .enc.csv for encrypted)
        rows: List of dictionaries to save
        fieldnames: CSV field names
        password: Password for encryption (triggers .enc.csv if provided)

    Raises:
        ValueError: If password/extension mismatch detected
    """
    encrypted = is_encrypted_file(path)

    # Validate password matches file type
    if encrypted and password is None:
        raise ValueError(f"File {path} has .enc extension but no password provided")
    if not encrypted and password is not None:
        raise ValueError(f"File {path} is plaintext but password was provided")

    path.parent.mkdir(parents=True, exist_ok=True)

    # First generate CSV text
    output = io.StringIO()
    w = csv.DictWriter(output, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    csv_text = output.getvalue()

    if encrypted:
        # Encrypt and write binary
        assert password is not None  # Type checker: validated above
        encrypted_data = encrypt_data(csv_text, password)
        with path.open("wb") as f:
            f.write(encrypted_data)
    else:
        # Plain text
        with path.open("w", newline="", encoding="utf-8") as f:
            f.write(csv_text)


def load_json_data(path: Path, password: str | None = None) -> dict[str, Any]:
    """Load JSON data from file, auto-detecting encryption from extension.

    Args:
        path: Path to JSON file (.json for plaintext, .enc.json for encrypted)
        password: Password for decryption (required if file is encrypted)

    Returns:
        Dictionary containing JSON data

    Raises:
        ValueError: If encrypted file is accessed without password or vice versa
    """
    if not path.exists():
        return {}

    encrypted = is_encrypted_file(path)

    # Validate password matches file type
    if encrypted and password is None:
        raise ValueError(f"File {path} is encrypted but no password provided")
    if not encrypted and password is not None:
        raise ValueError(f"File {path} is plaintext but password was provided")

    if encrypted:
        # Encrypted file - read binary, decrypt, parse JSON
        with path.open("rb") as f:
            encrypted_data = f.read()
        # Type checker: we've already validated password is not None above
        assert password is not None
        json_text = decrypt_data(encrypted_data, password)
        return cast(dict[str, Any], json.loads(json_text))
    # Plain text file
    with path.open(encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def save_json_data(path: Path, data: dict[str, Any], password: str | None = None) -> None:
    """Save JSON data to file with appropriate extension based on encryption.

    Args:
        path: Path to JSON file (.json for plaintext, .enc.json for encrypted)
        data: Dictionary to save as JSON
        password: Password for encryption (triggers .enc.json if provided)

    Raises:
        ValueError: If password/extension mismatch detected
    """
    encrypted = is_encrypted_file(path)

    # Validate password matches file type
    if encrypted and password is None:
        raise ValueError(f"File {path} has .enc extension but no password provided")
    if not encrypted and password is not None:
        raise ValueError(f"File {path} is plaintext but password was provided")

    path.parent.mkdir(parents=True, exist_ok=True)

    # Generate JSON text
    json_text = json.dumps(data, indent=2)

    if encrypted:
        # Encrypt and write binary
        assert password is not None  # Type checker: validated above
        encrypted_data = encrypt_data(json_text, password)
        with path.open("wb") as f:
            f.write(encrypted_data)
    else:
        # Plain text
        with path.open("w", encoding="utf-8") as f:
            f.write(json_text)


def sort_data(
    data: list[dict[str, str]], serial_field: str = "serial", reverse: bool = True
) -> list[dict[str, str]]:
    """Return data sorted by serial number.

    Args:
        data: List of dictionaries to sort
        serial_field: Field name containing the serial number (default: "serial")
        reverse: If True, sort descending (newest first). If False, sort ascending (oldest first).
    """

    def key(item: dict[str, str]) -> int:
        try:
            return int(item.get(serial_field, 0))
        except Exception:
            return 0

    return sorted(data, key=key, reverse=reverse)


def load_config(
    cfg_path: Path, defaults: dict[str, Any] | None = None, password: str | None = None
) -> dict[str, Any]:
    """Load configuration from JSON file with optional defaults and encryption.

    Args:
        cfg_path: Path to the JSON config file (.json or .enc.json)
        defaults: Default configuration values if file doesn't exist
        password: Password for decryption (required if file is .enc.json)

    Returns:
        Configuration dictionary
    """
    if defaults is None:
        defaults = {}

    if cfg_path.exists():
        return load_json_data(cfg_path, password)
    return defaults.copy()


def save_config(cfg_path: Path, config: dict[str, Any], password: str | None = None) -> None:
    """Save configuration to JSON file with optional encryption.

    Args:
        cfg_path: Path to the JSON config file (.json or .enc.json)
        config: Configuration dictionary to save
        password: Password for encryption (required if file is .enc.json)
    """
    save_json_data(cfg_path, config, password)
