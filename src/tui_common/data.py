"""Data loading and saving utilities for CSV and JSON files."""

import csv
import io
import json
from pathlib import Path
from typing import Any, cast

from .crypto import decrypt_data, encrypt_data
from .paths import is_encrypted_file


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
