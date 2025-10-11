"""Common utilities for TUI apps.

This package provides shared functionality for building terminal user interface applications
including authentication, data management, encryption, and common UI components.
"""

# Public API exports
from .auth import (
	BcryptAuth,
	create_user,
	load_users,
	save_users,
	user_wants_encryption,
	users_db_path,
	verify_user,
)
from .crypto import decrypt_data, derive_key, encrypt_data
from .data import (
	load_config,
	load_csv_data,
	load_json_data,
	save_config,
	save_csv_data,
	save_json_data,
	sort_data,
)
from .paths import app_data_dir, is_encrypted_file, user_config_path, user_data_path
from .screens import AuthProvider, LoginScreen
from .version import get_version

__all__ = [
	# Auth
	"BcryptAuth",
	"create_user",
	"verify_user",
	"user_wants_encryption",
	"load_users",
	"save_users",
	"users_db_path",
	"AuthProvider",
	# Crypto
	"derive_key",
	"encrypt_data",
	"decrypt_data",
	# Data
	"load_config",
	"save_config",
	"load_csv_data",
	"save_csv_data",
	"load_json_data",
	"save_json_data",
	"sort_data",
	# Paths
	"app_data_dir",
	"user_data_path",
	"user_config_path",
	"is_encrypted_file",
	# Screens
	"LoginScreen",
	# Version
	"get_version",
]
# Placeholder to include tui_common in package build context.
