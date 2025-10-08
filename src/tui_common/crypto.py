"""Encryption and decryption utilities."""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


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
