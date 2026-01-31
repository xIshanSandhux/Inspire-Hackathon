"""Encryption utilities for sensitive data.

Uses Fernet symmetric encryption (AES-128-CBC with HMAC-SHA256).
All encrypted values include authentication to prevent tampering.

Usage:
    from backend.core.crypto import encrypt_value, decrypt_value, encrypt_json, decrypt_json

    # String encryption
    encrypted = encrypt_value("sensitive data")
    decrypted = decrypt_value(encrypted)

    # JSON/dict encryption
    encrypted_dict = encrypt_json({"key": "value", "nested": {"data": 123}})
    decrypted_dict = decrypt_json(encrypted_dict)
"""

import hashlib
import json
from functools import lru_cache
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from backend.core.config import settings


class EncryptionError(Exception):
    """Raised when encryption fails."""
    pass


class DecryptionError(Exception):
    """Raised when decryption fails (invalid key, corrupted data, or tampered ciphertext)."""
    pass


@lru_cache
def get_fernet() -> Fernet:
    """Get cached Fernet instance for encryption/decryption."""
    return Fernet(settings.encryption_key.encode())


def encrypt_value(value: str) -> str:
    """
    Encrypt a string value and return base64-encoded ciphertext.
    
    Args:
        value: The plaintext string to encrypt.
        
    Returns:
        Base64-encoded encrypted string.
        
    Raises:
        EncryptionError: If encryption fails.
    """
    try:
        fernet = get_fernet()
        return fernet.encrypt(value.encode()).decode()
    except Exception as e:
        raise EncryptionError(f"Failed to encrypt value: {e}") from e


def decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt a base64-encoded ciphertext and return plaintext.
    
    Args:
        encrypted_value: Base64-encoded encrypted string.
        
    Returns:
        Decrypted plaintext string.
        
    Raises:
        DecryptionError: If decryption fails (wrong key, corrupted, or tampered data).
    """
    try:
        fernet = get_fernet()
        return fernet.decrypt(encrypted_value.encode()).decode()
    except InvalidToken as e:
        raise DecryptionError("Decryption failed: invalid token (wrong key or corrupted data)") from e
    except Exception as e:
        raise DecryptionError(f"Failed to decrypt value: {e}") from e


def encrypt_json(data: dict[str, Any] | list[Any] | None) -> str | None:
    """
    Encrypt a JSON-serializable object (dict, list, or None).
    
    Args:
        data: A dict, list, or None to encrypt. None returns None.
        
    Returns:
        Base64-encoded encrypted string, or None if input is None.
        
    Raises:
        EncryptionError: If encryption or JSON serialization fails.
    """
    if data is None:
        return None
    
    try:
        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        return encrypt_value(json_str)
    except (TypeError, ValueError) as e:
        raise EncryptionError(f"Failed to serialize data to JSON: {e}") from e


def decrypt_json(encrypted_value: str | None) -> dict[str, Any] | list[Any] | None:
    """
    Decrypt an encrypted JSON string back to its original structure.
    
    Args:
        encrypted_value: Base64-encoded encrypted string, or None.
        
    Returns:
        Decrypted dict/list, or None if input is None.
        
    Raises:
        DecryptionError: If decryption or JSON parsing fails.
    """
    if encrypted_value is None:
        return None
    
    try:
        json_str = decrypt_value(encrypted_value)
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise DecryptionError(f"Failed to parse decrypted JSON: {e}") from e


def hash_for_lookup(value: str) -> str:
    """
    Create a deterministic hash for database lookups.
    
    This allows searching by fingerprint without exposing the actual value.
    Uses SHA-256 for consistent 64-character hex output.
    
    Args:
        value: The value to hash.
        
    Returns:
        64-character hex string (SHA-256 hash).
    """
    return hashlib.sha256(value.encode()).hexdigest()
