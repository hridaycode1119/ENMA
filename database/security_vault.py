"""
ENMA Enterprise Database Security Vault & Cryptographic Field-Level Encryption Engine.
Provides envelope encryption, blind indexing for encrypted searches, and PII masking.
"""

from __future__ import annotations
import base64
import hashlib
import hmac
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Union

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class DatabaseSecurityVault:
    """
    Enterprise-grade Cryptographic Vault for field-level encryption, blind indexing,
    and credential protection across database repositories.
    """

    CIPHER_PREFIX = "enc::v1::"
    BLIND_INDEX_PREFIX = "bidx::v1::"

    _instance: Optional["DatabaseSecurityVault"] = None

    def __new__(cls, *args, **kwargs) -> "DatabaseSecurityVault":
        if cls._instance is None:
            cls._instance = super(DatabaseSecurityVault, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        master_key: Optional[str] = None,
        salt: Optional[bytes] = None,
        blind_index_salt: Optional[bytes] = None,
    ) -> None:
        if getattr(self, "_initialized", False):
            return

        # 1. Resolve Master Encryption Key
        raw_key = master_key or os.getenv("ENMA_MASTER_ENCRYPTION_KEY", "enma-secure-enterprise-master-key-2026")
        raw_salt = salt or os.getenv("ENMA_VAULT_SALT", "enma-cryptographic-salt-byte-secure").encode("utf-8")
        
        # 2. Derive 256-bit Key via PBKDF2-HMAC-SHA256 (100,000 iterations)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=raw_salt,
            iterations=100_000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(raw_key.encode("utf-8")))
        self._fernet = Fernet(derived_key)

        # 3. Blind Index HMAC Salt for Searchable Encryption
        self._blind_index_salt = blind_index_salt or os.getenv(
            "ENMA_BLIND_INDEX_SALT", "enma-blind-index-search-salt-secure"
        ).encode("utf-8")

        self._initialized = True

    # ----------------------------------------------------------------------
    # Field-Level Symmetric Encryption / Decryption
    # ----------------------------------------------------------------------

    def is_encrypted(self, value: Any) -> bool:
        """Checks if a string value is an armored ciphertext."""
        if not isinstance(value, str):
            return False
        return value.startswith(self.CIPHER_PREFIX)

    def encrypt_field(self, plaintext: Optional[str]) -> str:
        """
        Encrypts a plaintext string using AES-128-CBC with HMAC-SHA256 authentication (Fernet).
        Returns an armored ciphertext string with version prefix.
        """
        if plaintext is None:
            return ""
        if not isinstance(plaintext, str):
            plaintext = str(plaintext)
        if not plaintext:
            return ""

        # Avoid double encryption
        if self.is_encrypted(plaintext):
            return plaintext

        encrypted_bytes = self._fernet.encrypt(plaintext.encode("utf-8"))
        armored = self.CIPHER_PREFIX + encrypted_bytes.decode("utf-8")
        return armored

    def decrypt_field(self, ciphertext: Optional[str]) -> str:
        """
        Decrypts an armored ciphertext string back into original plaintext.
        If the value is not encrypted, returns it cleanly as plaintext.
        """
        if not ciphertext:
            return ""
        if not isinstance(ciphertext, str):
            return str(ciphertext)

        if not self.is_encrypted(ciphertext):
            return ciphertext

        raw_token = ciphertext[len(self.CIPHER_PREFIX):]
        try:
            decrypted_bytes = self._fernet.decrypt(raw_token.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except (InvalidToken, Exception):
            return "[DECRYPTION_ERROR_INTEGRITY_COMPROMISED]"

    # ----------------------------------------------------------------------
    # Blind Indexing for Searchable Encrypted Fields
    # ----------------------------------------------------------------------

    def generate_blind_index(self, plaintext: Optional[str]) -> str:
        """
        Generates a deterministic HMAC-SHA256 blind index hash for exact-match searching
        on encrypted database columns without decrypting entire tables.
        """
        if not plaintext:
            return ""
        normalized = str(plaintext).strip().lower()
        h = hmac.new(self._blind_index_salt, normalized.encode("utf-8"), hashlib.sha256)
        return self.BLIND_INDEX_PREFIX + h.hexdigest()

    # ----------------------------------------------------------------------
    # Structured Dictionary & JSON Envelope Encryption
    # ----------------------------------------------------------------------

    def encrypt_dict(
        self,
        data: Dict[str, Any],
        sensitive_keys: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        """
        Recursively encrypts specified sensitive keys within a dictionary payload.
        """
        if not isinstance(data, dict):
            return data

        target_keys = set(sensitive_keys or [
            "password", "secret", "token", "api_key", "oauth_token",
            "body", "content", "phone", "private_notes", "credentials"
        ])

        encrypted_data: Dict[str, Any] = {}
        for k, v in data.items():
            if k in target_keys and isinstance(v, (str, int, float)):
                encrypted_data[k] = self.encrypt_field(str(v))
            elif isinstance(v, dict):
                encrypted_data[k] = self.encrypt_dict(v, target_keys)
            elif isinstance(v, list):
                encrypted_data[k] = [
                    self.encrypt_dict(item, target_keys) if isinstance(item, dict) else item
                    for item in v
                ]
            else:
                encrypted_data[k] = v

        return encrypted_data

    def decrypt_dict(
        self,
        data: Dict[str, Any],
        sensitive_keys: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        """
        Recursively decrypts sensitive armored ciphertext fields in a dictionary payload.
        """
        if not isinstance(data, dict):
            return data

        target_keys = set(sensitive_keys or [
            "password", "secret", "token", "api_key", "oauth_token",
            "body", "content", "phone", "private_notes", "credentials"
        ])

        decrypted_data: Dict[str, Any] = {}
        for k, v in data.items():
            if isinstance(v, str) and self.is_encrypted(v):
                decrypted_data[k] = self.decrypt_field(v)
            elif isinstance(v, dict):
                decrypted_data[k] = self.decrypt_dict(v, target_keys)
            elif isinstance(v, list):
                decrypted_data[k] = [
                    self.decrypt_dict(item, target_keys) if isinstance(item, dict) else item
                    for item in v
                ]
            else:
                decrypted_data[k] = v

        return decrypted_data

    # ----------------------------------------------------------------------
    # PII Masking Utilities
    # ----------------------------------------------------------------------

    @staticmethod
    def mask_email(email: Optional[str]) -> str:
        """Masks an email address for safe display: h****9@gmail.com"""
        if not email or "@" not in email:
            return email or ""
        user, domain = email.split("@", 1)
        if len(user) <= 2:
            masked_user = user[0] + "*"
        else:
            masked_user = user[0] + "*" * (len(user) - 2) + user[-1]
        return f"{masked_user}@{domain}"

    @staticmethod
    def mask_phone(phone: Optional[str]) -> str:
        """Masks a phone number: +91 ******3210"""
        if not phone:
            return ""
        clean = re.sub(r"[^\d+]", "", str(phone))
        if len(clean) <= 4:
            return "****"
        return clean[:3] + "*" * (len(clean) - 7) + clean[-4:]

    @staticmethod
    def mask_secret_token(token: Optional[str]) -> str:
        """Masks sensitive API tokens: sk_live_****...****3a8f"""
        if not token:
            return ""
        if len(token) <= 8:
            return "*" * len(token)
        return token[:6] + "*" * 8 + token[-4:]


# Singleton instance for direct import
vault = DatabaseSecurityVault()
