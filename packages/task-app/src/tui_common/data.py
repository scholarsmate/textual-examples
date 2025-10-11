"""Data loading and saving utilities for CSV and JSON files."""

import csv
import io
import json
from pathlib import Path
from typing import Any, cast

from .crypto import decrypt_data, encrypt_data
from .paths import is_encrypted_file


def load_csv_data(path: Path, password: str | None = None) -> list[dict[str, str]]:
    if not path.exists():
        return []
    encrypted = is_encrypted_file(path)
    if encrypted and password is None:
        raise ValueError(f"File {path} is encrypted but no password provided")
    if not encrypted and password is not None:
        raise ValueError(f"File {path} is plaintext but password was provided")
    if encrypted:
        with path.open("rb") as f:
            encrypted_data = f.read()
        assert password is not None
        csv_text = decrypt_data(encrypted_data, password)
        reader = csv.DictReader(csv_text.splitlines())
        return list(reader)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_csv_data(
    path: Path, rows: list[dict[str, Any]], fieldnames: list[str], password: str | None = None
) -> None:
    encrypted = is_encrypted_file(path)
    if encrypted and password is None:
        raise ValueError(f"File {path} has .enc extension but no password provided")
    if not encrypted and password is not None:
        raise ValueError(f"File {path} is plaintext but password was provided")
    path.parent.mkdir(parents=True, exist_ok=True)
    output = io.StringIO()
    w = csv.DictWriter(output, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    csv_text = output.getvalue()
    if encrypted:
        assert password is not None
        encrypted_data = encrypt_data(csv_text, password)
        with path.open("wb") as f:
            f.write(encrypted_data)
    else:
        with path.open("w", newline="", encoding="utf-8") as f:
            f.write(csv_text)


def load_json_data(path: Path, password: str | None = None) -> dict[str, Any]:
    if not path.exists():
        return {}
    encrypted = is_encrypted_file(path)
    if encrypted and password is None:
        raise ValueError(f"File {path} is encrypted but no password provided")
    if not encrypted and password is not None:
        raise ValueError(f"File {path} is plaintext but password was provided")
    if encrypted:
        with path.open("rb") as f:
            encrypted_data = f.read()
        assert password is not None
        json_text = decrypt_data(encrypted_data, password)
        return cast(dict[str, Any], json.loads(json_text))
    with path.open(encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def save_json_data(path: Path, data: dict[str, Any], password: str | None = None) -> None:
    encrypted = is_encrypted_file(path)
    if encrypted and password is None:
        raise ValueError(f"File {path} has .enc extension but no password provided")
    if not encrypted and password is not None:
        raise ValueError(f"File {path} is plaintext but password was provided")
    path.parent.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(data, indent=2)
    if encrypted:
        assert password is not None
        encrypted_data = encrypt_data(json_text, password)
        with path.open("wb") as f:
            f.write(encrypted_data)
    else:
        with path.open("w", encoding="utf-8") as f:
            f.write(json_text)


def sort_data(
    data: list[dict[str, str]], serial_field: str = "serial", reverse: bool = True
) -> list[dict[str, str]]:
    def key(item: dict[str, str]) -> int:
        try:
            return int(item.get(serial_field, 0))
        except Exception:
            return 0

    return sorted(data, key=key, reverse=reverse)


def load_config(
    cfg_path: Path, defaults: dict[str, Any] | None = None, password: str | None = None
) -> dict[str, Any]:
    if defaults is None:
        defaults = {}
    if cfg_path.exists():
        return load_json_data(cfg_path, password)
    return defaults.copy()


def save_config(cfg_path: Path, config: dict[str, Any], password: str | None = None) -> None:
    save_json_data(cfg_path, config, password)
