"""
Encryption module for secure ID storage.

Uses AES-256 encryption with the fingerprint hash as the key.
This ensures that only someone with the correct fingerprint hash
can decrypt and access the stored ID data.
"""
import base64
import hashlib
import json
import os
from typing import Dict, Any, Optional

# Use cryptography library for AES encryption
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


# Valid ID types that can be stored
VALID_ID_TYPES = ['PASSPORT', 'BCID']


def _derive_key(fingerprint_hash: str, salt: bytes = None) -> tuple:
    """
    Derive a 256-bit AES key from the fingerprint hash.
    
    Args:
        fingerprint_hash: The user's fingerprint hash
        salt: Optional salt bytes (generated if not provided)
    
    Returns:
        Tuple of (key_bytes, salt_bytes)
    """
    if salt is None:
        salt = os.urandom(16)
    
    # Use PBKDF2-like derivation with SHA-256
    # Multiple rounds to make brute-force harder
    key_material = fingerprint_hash.encode() + salt
    for _ in range(10000):
        key_material = hashlib.sha256(key_material).digest()
    
    return key_material[:32], salt


def encrypt_ids(id_data: Dict[str, Any], fingerprint_hash: str) -> str:
    """
    Encrypt ID data using the fingerprint hash as the key.
    
    Args:
        id_data: Dictionary with ID types as keys (PASSPORT, BCID)
        fingerprint_hash: The user's fingerprint hash (used as encryption key)
    
    Returns:
        Base64-encoded encrypted string containing salt + iv + ciphertext
    """
    if not CRYPTO_AVAILABLE:
        # Fallback: simple XOR-based obfuscation (less secure but works without dependencies)
        return _encrypt_fallback(id_data, fingerprint_hash)
    
    # Convert data to JSON string
    plaintext = json.dumps(id_data).encode('utf-8')
    
    # Derive key from fingerprint hash
    key, salt = _derive_key(fingerprint_hash)
    
    # Generate random IV
    iv = os.urandom(16)
    
    # Pad plaintext to multiple of 16 bytes (AES block size)
    padding_length = 16 - (len(plaintext) % 16)
    padded_plaintext = plaintext + bytes([padding_length] * padding_length)
    
    # Encrypt using AES-256-CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    
    # Combine salt + iv + ciphertext and base64 encode
    encrypted_data = salt + iv + ciphertext
    return base64.b64encode(encrypted_data).decode('utf-8')


def decrypt_ids(encrypted_data: str, fingerprint_hash: str) -> Optional[Dict[str, Any]]:
    """
    Decrypt ID data using the fingerprint hash as the key.
    
    Args:
        encrypted_data: Base64-encoded encrypted string
        fingerprint_hash: The user's fingerprint hash (used as decryption key)
    
    Returns:
        Decrypted ID dictionary, or None if decryption fails
    """
    if not CRYPTO_AVAILABLE:
        return _decrypt_fallback(encrypted_data, fingerprint_hash)
    
    try:
        # Decode base64
        raw_data = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # Extract salt, iv, and ciphertext
        salt = raw_data[:16]
        iv = raw_data[16:32]
        ciphertext = raw_data[32:]
        
        # Derive key from fingerprint hash with the same salt
        key, _ = _derive_key(fingerprint_hash, salt)
        
        # Decrypt using AES-256-CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        padding_length = padded_plaintext[-1]
        plaintext = padded_plaintext[:-padding_length]
        
        # Parse JSON
        return json.loads(plaintext.decode('utf-8'))
        
    except Exception as e:
        # Decryption failed - wrong key or corrupted data
        return None


def _encrypt_fallback(id_data: Dict[str, Any], fingerprint_hash: str) -> str:
    """
    Fallback encryption when cryptography library is not available.
    Uses XOR-based obfuscation with the fingerprint hash.
    
    Note: This is less secure than AES but provides basic protection.
    """
    plaintext = json.dumps(id_data).encode('utf-8')
    
    # Generate key stream from fingerprint hash
    key_stream = hashlib.sha256(fingerprint_hash.encode()).digest()
    
    # Extend key stream to match plaintext length
    extended_key = (key_stream * ((len(plaintext) // len(key_stream)) + 1))[:len(plaintext)]
    
    # XOR plaintext with key stream
    encrypted_bytes = bytes(a ^ b for a, b in zip(plaintext, extended_key))
    
    # Add marker to identify fallback encryption
    return "FALLBACK:" + base64.b64encode(encrypted_bytes).decode('utf-8')


def _decrypt_fallback(encrypted_data: str, fingerprint_hash: str) -> Optional[Dict[str, Any]]:
    """
    Fallback decryption for XOR-based obfuscation.
    """
    try:
        if not encrypted_data.startswith("FALLBACK:"):
            return None
        
        encrypted_b64 = encrypted_data[9:]  # Remove "FALLBACK:" prefix
        encrypted_bytes = base64.b64decode(encrypted_b64.encode('utf-8'))
        
        # Generate key stream from fingerprint hash
        key_stream = hashlib.sha256(fingerprint_hash.encode()).digest()
        
        # Extend key stream
        extended_key = (key_stream * ((len(encrypted_bytes) // len(key_stream)) + 1))[:len(encrypted_bytes)]
        
        # XOR to decrypt
        plaintext = bytes(a ^ b for a, b in zip(encrypted_bytes, extended_key))
        
        return json.loads(plaintext.decode('utf-8'))
        
    except Exception:
        return None


def validate_id_data(id_data: Dict[str, Any]) -> tuple:
    """
    Validate ID data structure.
    
    Expected format:
    {
        "PASSPORT": {
            "id": "123456789",
            "metadata": {...}  # optional
        },
        "BCID": {
            "id": "987654321",
            "metadata": {...}  # optional
        }
    }
    
    Args:
        id_data: Dictionary to validate
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    if not isinstance(id_data, dict):
        return False, "ID data must be a dictionary"
    
    if len(id_data) == 0:
        return False, "At least one ID type must be provided"
    
    for id_type, id_info in id_data.items():
        # Check if ID type is valid
        if id_type not in VALID_ID_TYPES:
            return False, f"Invalid ID type '{id_type}'. Valid types: {', '.join(VALID_ID_TYPES)}"
        
        # Check if id_info is a dictionary
        if not isinstance(id_info, dict):
            return False, f"ID info for '{id_type}' must be a dictionary"
        
        # Check if 'id' field exists and is not empty
        if 'id' not in id_info:
            return False, f"'{id_type}' must have an 'id' field"
        
        if not id_info['id'] or not isinstance(id_info['id'], str):
            return False, f"'{id_type}' id must be a non-empty string"
        
        # Metadata is optional, but if present must be a dict
        if 'metadata' in id_info and not isinstance(id_info['metadata'], dict):
            return False, f"'{id_type}' metadata must be a dictionary if provided"
    
    return True, None


def format_id_for_display(id_data: Dict[str, Any], mask: bool = False) -> str:
    """
    Format ID data for display.
    
    Args:
        id_data: Decrypted ID dictionary
        mask: If True, partially mask the ID values
    
    Returns:
        Formatted string for display
    """
    lines = []
    for id_type, id_info in id_data.items():
        id_value = id_info.get('id', 'N/A')
        if mask and len(id_value) > 4:
            id_value = id_value[:2] + '*' * (len(id_value) - 4) + id_value[-2:]
        
        lines.append(f"   📄 {id_type}:")
        lines.append(f"      ID: {id_value}")
        
        metadata = id_info.get('metadata', {})
        if metadata:
            for key, value in metadata.items():
                lines.append(f"      {key}: {value}")
    
    return '\n'.join(lines)


# Check and report crypto status at import
def get_crypto_status() -> str:
    """Get the current encryption status."""
    if CRYPTO_AVAILABLE:
        return "AES-256-CBC (cryptography library)"
    else:
        return "XOR Fallback (install 'cryptography' for stronger encryption)"
