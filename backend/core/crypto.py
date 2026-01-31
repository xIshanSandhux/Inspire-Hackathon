"""Encryption utilities for sensitive data."""

import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet

from backend.core.config import settings


@lru_cache
def get_fernet() -> Fernet:
    """Get cached Fernet instance for encryption/decryption."""
    return Fernet(settings.encryption_key.encode())


def encrypt_value(value: str) -> str:
    """Encrypt a string value and return base64-encoded ciphertext."""
    fernet = get_fernet()
    return fernet.encrypt(value.encode()).decode()


def decrypt_value(encrypted_value: str) -> str:
    """Decrypt a base64-encoded ciphertext and return plaintext."""
    fernet = get_fernet()
    return fernet.decrypt(encrypted_value.encode()).decode()


def hash_for_lookup(value: str) -> str:
    """
    Create a deterministic hash for database lookups.
    This allows us to search by fingerprint without exposing the actual value.
    """
    return hashlib.sha256(value.encode()).hexdigest()
