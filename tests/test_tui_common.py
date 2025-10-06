# test_tui_common.py
"""Comprehensive tests for tui_common module."""

import json
from pathlib import Path
from typing import Any

import pytest

import tui_common


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test data."""
    return tmp_path


@pytest.fixture
def app_name() -> str:
    """Return a test app name."""
    return "test_app"


@pytest.fixture
def test_user() -> dict[str, str]:
    """Return test user credentials."""
    return {"username": "testuser", "password": "testpass123"}


class TestGetVersion:
    """Tests for get_version function."""

    def test_get_version_returns_string(self) -> None:
        """Test that get_version returns a string."""
        version = tui_common.get_version()
        assert isinstance(version, str)
        assert len(version) > 0

    def test_get_version_format(self) -> None:
        """Test that version follows semantic versioning format."""
        version = tui_common.get_version()
        # Should be in format X.Y.Z or "unknown"
        if version != "unknown":
            parts = version.split(".")
            assert len(parts) >= 2  # At least major.minor


class TestAppDataDir:
    """Tests for app_data_dir function."""

    def test_creates_directory(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that app_data_dir creates the directory structure."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        result = tui_common.app_data_dir("test_app")
        assert result.exists()
        assert result.is_dir()
        assert result.name == "test_app"

    def test_returns_existing_directory(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that app_data_dir works with existing directory."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        result1 = tui_common.app_data_dir("test_app")
        result2 = tui_common.app_data_dir("test_app")
        assert result1 == result2


class TestUsersDbPath:
    """Tests for users_db_path function."""

    def test_returns_users_json_path(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that users_db_path returns correct path."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        result = tui_common.users_db_path("test_app")
        assert result.name == "users.json"
        assert "test_app" in str(result)


class TestLoadSaveUsers:
    """Tests for load_users and save_users functions."""

    def test_load_users_empty_file(self, temp_dir: Path) -> None:
        """Test loading users from non-existent file returns empty dict."""
        path = temp_dir / "users.json"
        result = tui_common.load_users(path)
        assert result == {}

    def test_save_and_load_users(self, temp_dir: Path) -> None:
        """Test saving and loading users."""
        path = temp_dir / "users.json"
        users = {
            "user1": {"password": "hash1", "encrypt_data": False},
            "user2": {"password": "hash2", "encrypt_data": True},
        }
        tui_common.save_users(path, users)
        assert path.exists()

        loaded = tui_common.load_users(path)
        assert loaded == users

    def test_load_users_migrates_old_format(self, temp_dir: Path) -> None:
        """Test that old format (username -> hash string) is migrated."""
        path = temp_dir / "users.json"
        # Create old format file
        old_format = {"user1": "oldhash123", "user2": "oldhash456"}
        with path.open("w", encoding="utf-8") as f:
            json.dump(old_format, f)

        loaded = tui_common.load_users(path)
        assert loaded["user1"] == {"password": "oldhash123", "encrypt_data": False}
        assert loaded["user2"] == {"password": "oldhash456", "encrypt_data": False}

    def test_load_users_mixed_format(self, temp_dir: Path) -> None:
        """Test loading users with mixed old and new format."""
        path = temp_dir / "users.json"
        mixed_format = {
            "olduser": "oldhash",
            "newuser": {"password": "newhash", "encrypt_data": True},
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(mixed_format, f)

        loaded = tui_common.load_users(path)
        assert loaded["olduser"] == {"password": "oldhash", "encrypt_data": False}
        assert loaded["newuser"] == {"password": "newhash", "encrypt_data": True}


class TestCreateUser:
    """Tests for create_user function."""

    def test_create_user_success(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test creating a new user."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        tui_common.create_user("test_app", "newuser", "password123")

        path = tui_common.users_db_path("test_app")
        users = tui_common.load_users(path)
        assert "newuser" in users
        assert "password" in users["newuser"]
        assert users["newuser"]["encrypt_data"] is False

    def test_create_user_with_encryption(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test creating a user with encryption enabled."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        tui_common.create_user("test_app", "encuser", "password123", encrypt_data=True)

        path = tui_common.users_db_path("test_app")
        users = tui_common.load_users(path)
        assert users["encuser"]["encrypt_data"] is True

    def test_create_user_empty_username(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that empty username raises ValueError."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        with pytest.raises(ValueError, match="username/password required"):
            tui_common.create_user("test_app", "", "password123")

    def test_create_user_empty_password(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that empty password raises ValueError."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        with pytest.raises(ValueError, match="username/password required"):
            tui_common.create_user("test_app", "user", "")

    def test_create_user_duplicate(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that creating duplicate user raises ValueError."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        tui_common.create_user("test_app", "user", "password123")
        with pytest.raises(ValueError, match="user exists"):
            tui_common.create_user("test_app", "user", "password456")


class TestVerifyUser:
    """Tests for verify_user function."""

    def test_verify_user_success(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test verifying correct credentials."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        tui_common.create_user("test_app", "user", "password123")
        assert tui_common.verify_user("test_app", "user", "password123") is True

    def test_verify_user_wrong_password(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test verifying with wrong password."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        tui_common.create_user("test_app", "user", "password123")
        assert tui_common.verify_user("test_app", "user", "wrongpassword") is False

    def test_verify_user_nonexistent(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test verifying non-existent user."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        assert tui_common.verify_user("test_app", "nonexistent", "password") is False


class TestUserWantsEncryption:
    """Tests for user_wants_encryption function."""

    def test_user_wants_encryption_true(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test user with encryption enabled."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        tui_common.create_user("test_app", "user", "password", encrypt_data=True)
        assert tui_common.user_wants_encryption("test_app", "user") is True

    def test_user_wants_encryption_false(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test user with encryption disabled."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        tui_common.create_user("test_app", "user", "password", encrypt_data=False)
        assert tui_common.user_wants_encryption("test_app", "user") is False

    def test_user_wants_encryption_nonexistent(
        self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test non-existent user returns False."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        assert tui_common.user_wants_encryption("test_app", "nonexistent") is False


class TestEncryption:
    """Tests for encryption utilities."""

    def test_derive_key_deterministic(self) -> None:
        """Test that same password and salt produce same key."""
        salt = b"1234567890123456"
        key1 = tui_common.derive_key("password", salt)
        key2 = tui_common.derive_key("password", salt)
        assert key1 == key2

    def test_derive_key_different_passwords(self) -> None:
        """Test that different passwords produce different keys."""
        salt = b"1234567890123456"
        key1 = tui_common.derive_key("password1", salt)
        key2 = tui_common.derive_key("password2", salt)
        assert key1 != key2

    def test_derive_key_different_salts(self) -> None:
        """Test that different salts produce different keys."""
        key1 = tui_common.derive_key("password", b"1234567890123456")
        key2 = tui_common.derive_key("password", b"6543210987654321")
        assert key1 != key2

    def test_encrypt_decrypt_roundtrip(self) -> None:
        """Test encrypting and decrypting data."""
        original = "Hello, World! 🔐"
        password = "secret123"

        encrypted = tui_common.encrypt_data(original, password)
        assert isinstance(encrypted, bytes)
        assert len(encrypted) > len(original)

        decrypted = tui_common.decrypt_data(encrypted, password)
        assert decrypted == original

    def test_encrypt_produces_different_output(self) -> None:
        """Test that encrypting same data twice produces different output (different salts)."""
        data = "test data"
        password = "password"

        encrypted1 = tui_common.encrypt_data(data, password)
        encrypted2 = tui_common.encrypt_data(data, password)
        assert encrypted1 != encrypted2

    def test_decrypt_wrong_password_raises(self) -> None:
        """Test that decrypting with wrong password raises exception."""
        from cryptography.fernet import InvalidToken

        data = "secret data"
        encrypted = tui_common.encrypt_data(data, "correct")

        with pytest.raises(InvalidToken):
            tui_common.decrypt_data(encrypted, "wrong")

    def test_encrypt_decrypt_empty_string(self) -> None:
        """Test encrypting and decrypting empty string."""
        original = ""
        password = "password"

        encrypted = tui_common.encrypt_data(original, password)
        decrypted = tui_common.decrypt_data(encrypted, password)
        assert decrypted == original

    def test_encrypt_decrypt_unicode(self) -> None:
        """Test encrypting and decrypting Unicode text."""
        original = "Hello 世界 🌍 café"
        password = "password"

        encrypted = tui_common.encrypt_data(original, password)
        decrypted = tui_common.decrypt_data(encrypted, password)
        assert decrypted == original


class TestBcryptAuth:
    """Tests for BcryptAuth class."""

    def test_init(self) -> None:
        """Test BcryptAuth initialization."""
        auth = tui_common.BcryptAuth("test_app")
        assert auth.app_name == "test_app"

    def test_create_user(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test creating user through BcryptAuth."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        auth = tui_common.BcryptAuth("test_app")
        auth.create_user("user", "password")

        path = tui_common.users_db_path("test_app")
        users = tui_common.load_users(path)
        assert "user" in users

    def test_verify_user(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test verifying user through BcryptAuth."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        auth = tui_common.BcryptAuth("test_app")
        auth.create_user("user", "password123")

        assert auth.verify_user("user", "password123") is True
        assert auth.verify_user("user", "wrong") is False

    def test_user_exists(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test checking if user exists through BcryptAuth."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        auth = tui_common.BcryptAuth("test_app")

        assert auth.user_exists("user") is False
        auth.create_user("user", "password")
        assert auth.user_exists("user") is True


class TestUserDataPath:
    """Tests for user_data_path function."""

    def test_plaintext_path(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test generating plaintext file path."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        result = tui_common.user_data_path("test_app", "user", "tasks.csv", encrypted=False)
        assert result.name == "user_tasks.csv"
        assert ".enc." not in str(result)

    def test_encrypted_path(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test generating encrypted file path."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        result = tui_common.user_data_path("test_app", "user", "tasks.csv", encrypted=True)
        assert result.name == "user_tasks.enc.csv"
        assert ".enc." in str(result)

    def test_json_encrypted_path(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test generating encrypted JSON file path."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        result = tui_common.user_data_path("test_app", "user", "config.json", encrypted=True)
        assert result.name == "user_config.enc.json"


class TestUserConfigPath:
    """Tests for user_config_path function."""

    def test_plaintext_config(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test generating plaintext config path."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        result = tui_common.user_config_path("test_app", "user", encrypted=False)
        assert result.name == "user_config.json"

    def test_encrypted_config(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test generating encrypted config path."""
        monkeypatch.setattr("sys.argv", [str(temp_dir / "app.py")])
        result = tui_common.user_config_path("test_app", "user", encrypted=True)
        assert result.name == "user_config.enc.json"


class TestIsEncryptedFile:
    """Tests for is_encrypted_file function."""

    def test_encrypted_csv(self) -> None:
        """Test identifying encrypted CSV file."""
        path = Path("data/user_tasks.enc.csv")
        assert tui_common.is_encrypted_file(path) is True

    def test_plaintext_csv(self) -> None:
        """Test identifying plaintext CSV file."""
        path = Path("data/user_tasks.csv")
        assert tui_common.is_encrypted_file(path) is False

    def test_encrypted_json(self) -> None:
        """Test identifying encrypted JSON file."""
        path = Path("data/config.enc.json")
        assert tui_common.is_encrypted_file(path) is True

    def test_plaintext_json(self) -> None:
        """Test identifying plaintext JSON file."""
        path = Path("data/config.json")
        assert tui_common.is_encrypted_file(path) is False


class TestLoadSaveCsvData:
    """Tests for load_csv_data and save_csv_data functions."""

    def test_load_csv_nonexistent(self, temp_dir: Path) -> None:
        """Test loading non-existent CSV returns empty list."""
        path = temp_dir / "test.csv"
        result = tui_common.load_csv_data(path)
        assert result == []

    def test_save_and_load_csv_plaintext(self, temp_dir: Path) -> None:
        """Test saving and loading plaintext CSV."""
        path = temp_dir / "test.csv"
        data = [
            {"id": "1", "name": "Alice", "age": "30"},
            {"id": "2", "name": "Bob", "age": "25"},
        ]
        fieldnames = ["id", "name", "age"]

        tui_common.save_csv_data(path, data, fieldnames)
        assert path.exists()

        loaded = tui_common.load_csv_data(path)
        assert loaded == data

    def test_save_and_load_csv_encrypted(self, temp_dir: Path) -> None:
        """Test saving and loading encrypted CSV."""
        path = temp_dir / "test.enc.csv"
        password = "secret123"
        data = [
            {"id": "1", "secret": "classified"},
            {"id": "2", "secret": "confidential"},
        ]
        fieldnames = ["id", "secret"]

        tui_common.save_csv_data(path, data, fieldnames, password)
        assert path.exists()

        loaded = tui_common.load_csv_data(path, password)
        assert loaded == data

    def test_load_encrypted_without_password_raises(self, temp_dir: Path) -> None:
        """Test that loading encrypted CSV without password raises ValueError."""
        path = temp_dir / "test.enc.csv"
        password = "secret"
        data = [{"id": "1"}]
        fieldnames = ["id"]

        tui_common.save_csv_data(path, data, fieldnames, password)

        with pytest.raises(ValueError, match="encrypted but no password"):
            tui_common.load_csv_data(path, password=None)

    def test_load_plaintext_with_password_raises(self, temp_dir: Path) -> None:
        """Test that loading plaintext CSV with password raises ValueError."""
        path = temp_dir / "test.csv"
        data = [{"id": "1"}]
        fieldnames = ["id"]

        tui_common.save_csv_data(path, data, fieldnames)

        with pytest.raises(ValueError, match="plaintext but password was provided"):
            tui_common.load_csv_data(path, password="secret")

    def test_save_encrypted_without_password_raises(self, temp_dir: Path) -> None:
        """Test that saving to encrypted path without password raises ValueError."""
        path = temp_dir / "test.enc.csv"
        data = [{"id": "1"}]
        fieldnames = ["id"]

        with pytest.raises(ValueError, match="has .enc extension but no password"):
            tui_common.save_csv_data(path, data, fieldnames, password=None)

    def test_save_plaintext_with_password_raises(self, temp_dir: Path) -> None:
        """Test that saving to plaintext path with password raises ValueError."""
        path = temp_dir / "test.csv"
        data = [{"id": "1"}]
        fieldnames = ["id"]

        with pytest.raises(ValueError, match="plaintext but password was provided"):
            tui_common.save_csv_data(path, data, fieldnames, password="secret")

    def test_csv_empty_data(self, temp_dir: Path) -> None:
        """Test saving and loading empty CSV."""
        path = temp_dir / "empty.csv"
        data: list[dict[str, Any]] = []
        fieldnames = ["id", "name"]

        tui_common.save_csv_data(path, data, fieldnames)
        loaded = tui_common.load_csv_data(path)
        assert loaded == []


class TestLoadSaveJsonData:
    """Tests for load_json_data and save_json_data functions."""

    def test_load_json_nonexistent(self, temp_dir: Path) -> None:
        """Test loading non-existent JSON returns empty dict."""
        path = temp_dir / "test.json"
        result = tui_common.load_json_data(path)
        assert result == {}

    def test_save_and_load_json_plaintext(self, temp_dir: Path) -> None:
        """Test saving and loading plaintext JSON."""
        path = temp_dir / "test.json"
        data = {"name": "Alice", "age": 30, "active": True}

        tui_common.save_json_data(path, data)
        assert path.exists()

        loaded = tui_common.load_json_data(path)
        assert loaded == data

    def test_save_and_load_json_encrypted(self, temp_dir: Path) -> None:
        """Test saving and loading encrypted JSON."""
        path = temp_dir / "test.enc.json"
        password = "secret123"
        data = {"secret": "classified", "level": 5}

        tui_common.save_json_data(path, data, password)
        assert path.exists()

        loaded = tui_common.load_json_data(path, password)
        assert loaded == data

    def test_load_encrypted_json_without_password_raises(self, temp_dir: Path) -> None:
        """Test that loading encrypted JSON without password raises ValueError."""
        path = temp_dir / "test.enc.json"
        password = "secret"
        data = {"key": "value"}

        tui_common.save_json_data(path, data, password)

        with pytest.raises(ValueError, match="encrypted but no password"):
            tui_common.load_json_data(path, password=None)

    def test_load_plaintext_json_with_password_raises(self, temp_dir: Path) -> None:
        """Test that loading plaintext JSON with password raises ValueError."""
        path = temp_dir / "test.json"
        data = {"key": "value"}

        tui_common.save_json_data(path, data)

        with pytest.raises(ValueError, match="plaintext but password was provided"):
            tui_common.load_json_data(path, password="secret")

    def test_save_encrypted_json_without_password_raises(self, temp_dir: Path) -> None:
        """Test that saving to encrypted path without password raises ValueError."""
        path = temp_dir / "test.enc.json"
        data = {"key": "value"}

        with pytest.raises(ValueError, match="has .enc extension but no password"):
            tui_common.save_json_data(path, data, password=None)

    def test_save_plaintext_json_with_password_raises(self, temp_dir: Path) -> None:
        """Test that saving to plaintext path with password raises ValueError."""
        path = temp_dir / "test.json"
        data = {"key": "value"}

        with pytest.raises(ValueError, match="plaintext but password was provided"):
            tui_common.save_json_data(path, data, password="secret")

    def test_json_nested_data(self, temp_dir: Path) -> None:
        """Test saving and loading nested JSON data."""
        path = temp_dir / "nested.json"
        data = {
            "user": {
                "name": "Alice",
                "preferences": {"theme": "dark", "notifications": True},
            },
            "items": [1, 2, 3],
        }

        tui_common.save_json_data(path, data)
        loaded = tui_common.load_json_data(path)
        assert loaded == data


class TestSortData:
    """Tests for sort_data function."""

    def test_sort_descending_default(self) -> None:
        """Test sorting data descending (default)."""
        data = [
            {"serial": "1", "name": "first"},
            {"serial": "3", "name": "third"},
            {"serial": "2", "name": "second"},
        ]
        result = tui_common.sort_data(data)
        assert result[0]["serial"] == "3"
        assert result[1]["serial"] == "2"
        assert result[2]["serial"] == "1"

    def test_sort_ascending(self) -> None:
        """Test sorting data ascending."""
        data = [
            {"serial": "3", "name": "third"},
            {"serial": "1", "name": "first"},
            {"serial": "2", "name": "second"},
        ]
        result = tui_common.sort_data(data, reverse=False)
        assert result[0]["serial"] == "1"
        assert result[1]["serial"] == "2"
        assert result[2]["serial"] == "3"

    def test_sort_custom_field(self) -> None:
        """Test sorting by custom field name."""
        data = [
            {"id": "5", "name": "item5"},
            {"id": "2", "name": "item2"},
            {"id": "8", "name": "item8"},
        ]
        result = tui_common.sort_data(data, serial_field="id", reverse=False)
        assert result[0]["id"] == "2"
        assert result[1]["id"] == "5"
        assert result[2]["id"] == "8"

    def test_sort_missing_field(self) -> None:
        """Test sorting with missing serial field defaults to 0."""
        data = [
            {"serial": "5", "name": "has_serial"},
            {"name": "no_serial"},
            {"serial": "3", "name": "has_serial2"},
        ]
        result = tui_common.sort_data(data, reverse=False)
        # Missing serial should sort as 0
        assert result[0]["name"] == "no_serial"
        assert result[1]["serial"] == "3"
        assert result[2]["serial"] == "5"

    def test_sort_invalid_number(self) -> None:
        """Test sorting with invalid number in serial field."""
        data = [
            {"serial": "5", "name": "valid"},
            {"serial": "invalid", "name": "invalid_serial"},
            {"serial": "3", "name": "valid2"},
        ]
        result = tui_common.sort_data(data, reverse=False)
        # Invalid number should sort as 0
        assert result[0]["serial"] == "invalid"
        assert result[1]["serial"] == "3"
        assert result[2]["serial"] == "5"

    def test_sort_empty_list(self) -> None:
        """Test sorting empty list."""
        data: list[dict[str, str]] = []
        result = tui_common.sort_data(data)
        assert result == []


class TestLoadSaveConfig:
    """Tests for load_config and save_config functions."""

    def test_load_config_with_defaults(self, temp_dir: Path) -> None:
        """Test loading config with defaults when file doesn't exist."""
        path = temp_dir / "config.json"
        defaults = {"theme": "dark", "page_size": 10}

        result = tui_common.load_config(path, defaults)
        assert result == defaults
        # Should return copy, not same object
        assert result is not defaults

    def test_load_config_no_defaults(self, temp_dir: Path) -> None:
        """Test loading config without defaults returns empty dict."""
        path = temp_dir / "config.json"
        result = tui_common.load_config(path)
        assert result == {}

    def test_save_and_load_config_plaintext(self, temp_dir: Path) -> None:
        """Test saving and loading plaintext config."""
        path = temp_dir / "config.json"
        config = {"theme": "light", "language": "en"}

        tui_common.save_config(path, config)
        loaded = tui_common.load_config(path)
        assert loaded == config

    def test_save_and_load_config_encrypted(self, temp_dir: Path) -> None:
        """Test saving and loading encrypted config."""
        path = temp_dir / "config.enc.json"
        password = "secret123"
        config = {"api_key": "secret123456", "token": "xyz"}

        tui_common.save_config(path, config, password)
        loaded = tui_common.load_config(path, password=password)
        assert loaded == config

    def test_load_existing_config_ignores_defaults(self, temp_dir: Path) -> None:
        """Test that loading existing config ignores defaults."""
        path = temp_dir / "config.json"
        config = {"theme": "custom", "new_field": "value"}
        defaults = {"theme": "dark", "page_size": 10}

        tui_common.save_config(path, config)
        loaded = tui_common.load_config(path, defaults)
        assert loaded == config
        assert "page_size" not in loaded
