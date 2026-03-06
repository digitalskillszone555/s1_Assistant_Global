# config/secure_config.py
import os
import json
import base64
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from utils.logging_utils import log_event

SECURE_CONFIG_PATH = os.path.join("config", "secure_config.json.enc")
SECURE_CONFIG_SALT_PATH = os.path.join("config", "secure_config.salt") # Stored in plaintext for key derivation

class SecureConfigLoader:
    def __init__(self, passphrase: Optional[str] = None):
        self.passphrase = passphrase
        self.key: Optional[bytes] = None
        self.fernet: Optional[Fernet] = None
        self.salt: Optional[bytes] = None
        self.secure_data: Dict[str, Any] = {}

        if self.passphrase:
            self._derive_key()
            if self.key:
                self.fernet = Fernet(self.key)
            self.secure_data = self._load_secure_data()

    def _get_salt(self) -> bytes:
        """Loads or generates a salt for key derivation."""
        if os.path.exists(SECURE_CONFIG_SALT_PATH):
            try:
                with open(SECURE_CONFIG_SALT_PATH, 'rb') as f:
                    self.salt = f.read()
                log_event("SECURE_CONFIG", "Loaded secure config salt.")
            except IOError as e:
                log_event("SECURE_CONFIG", f"Error loading secure config salt: {e}", level="ERROR")
                raise
        else:
            self.salt = os.urandom(16)
            try:
                with open(SECURE_CONFIG_SALT_PATH, 'wb') as f:
                    f.write(self.salt)
                log_event("SECURE_CONFIG", "Generated and saved new secure config salt.")
            except IOError as e:
                log_event("SECURE_CONFIG", f"Error saving secure config salt: {e}", level="ERROR")
                raise
        return self.salt

    def _derive_key(self):
        """Derives the encryption key from the passphrase and salt."""
        if not self.passphrase:
            log_event("SECURE_CONFIG", "No passphrase provided for secure config.", level="ERROR")
            self.key = None
            return

        salt = self._get_salt()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(self.passphrase.encode('utf-8')))
        log_event("SECURE_CONFIG", "Encryption key derived.")

    def _encrypt(self, data: Dict[str, Any]) -> bytes:
        """Encrypts data using Fernet."""
        if not self.fernet:
            log_event("SECURE_CONFIG", "Encryption engine not initialized.", level="ERROR")
            raise ValueError("Encryption engine not initialized. Passphrase required.")
        return self.fernet.encrypt(json.dumps(data, indent=4).encode('utf-8'))

    def _decrypt(self, token: bytes) -> Dict[str, Any]:
        """Decrypts data using Fernet."""
        if not self.fernet:
            log_event("SECURE_CONFIG", "Decryption engine not initialized.", level="ERROR")
            raise ValueError("Decryption engine not initialized. Passphrase required.")
        
        try:
            decrypted_bytes = self.fernet.decrypt(token)
            return json.loads(decrypted_bytes)
        except InvalidToken:
            log_event("SECURE_CONFIG", "DECRYPTION FAILED: Invalid token or wrong passphrase.", level="ERROR")
            raise ValueError("Decryption failed. Incorrect passphrase or corrupted secure config.")
        except json.JSONDecodeError as e:
            log_event("SECURE_CONFIG", f"JSONDecodeError after decrypting secure config: {e}", level="ERROR")
            raise ValueError("Corrupted secure config file.")
        except Exception as e:
            log_event("SECURE_CONFIG", f"Unexpected error during decryption: {e}", level="ERROR")
            raise

    def _load_secure_data(self) -> Dict[str, Any]:
        """Loads and decrypts the secure config file."""
        if not os.path.exists(SECURE_CONFIG_PATH):
            log_event("SECURE_CONFIG", "secure_config.json.enc not found. Returning empty config.", level="WARNING")
            return {}
        
        try:
            with open(SECURE_CONFIG_PATH, 'rb') as f:
                encrypted_data = f.read()
            return self._decrypt(encrypted_data)
        except Exception as e:
            log_event("SECURE_CONFIG", f"Failed to load/decrypt secure config: {e}", level="CRITICAL")
            raise # Re-raise to halt startup

    def save_secure_data(self):
        """Encrypts and saves the current secure data to file."""
        if not self.fernet:
            log_event("SECURE_CONFIG", "Cannot save secure config: Encryption engine not initialized.", level="ERROR")
            raise ValueError("Encryption engine not initialized. Passphrase required.")
        
        try:
            encrypted_data = self._encrypt(self.secure_data)
            with open(SECURE_CONFIG_PATH, 'wb') as f:
                f.write(encrypted_data)
            log_event("SECURE_CONFIG", "Secure config saved successfully.")
        except Exception as e:
            log_event("SECURE_CONFIG", f"Failed to save secure config: {e}", level="CRITICAL")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a value from the secure config."""
        return self.secure_data.get(key, default)

    def set(self, key: str, value: Any):
        """Sets a value in the secure config and saves it."""
        self.secure_data[key] = value
        self.save_secure_data()

# Global singleton instance, initialized with a passphrase
_secure_config_loader_instance: Optional[SecureConfigLoader] = None

def get_secure_config_loader(passphrase: Optional[str] = None) -> SecureConfigLoader:
    """
    Provides access to the singleton SecureConfigLoader instance.
    The passphrase MUST be provided on the first call if secure config is expected to load.
    """
    global _secure_config_loader_instance
    if _secure_config_loader_instance is None:
        if passphrase is None:
            log_event("SECURE_CONFIG", "Attempted to get SecureConfigLoader without passphrase. Secure config will not be accessible.", level="ERROR")
            raise ValueError("Passphrase required to initialize SecureConfigLoader.")
        _secure_config_loader_instance = SecureConfigLoader(passphrase)
    elif passphrase is not None and _secure_config_loader_instance.passphrase is None:
        # If already initialized but without passphrase, and now one is provided
        _secure_config_loader_instance = SecureConfigLoader(passphrase) # Re-initialize to load with passphrase
        log_event("SECURE_CONFIG", "SecureConfigLoader re-initialized with passphrase.")
    return _secure_config_loader_instance

def secure_config_exists() -> bool:
    """Checks if the encrypted secure config file exists."""
    return os.path.exists(SECURE_CONFIG_PATH)

def secure_config_salt_exists() -> bool:
    """Checks if the secure config salt file exists."""
    return os.path.exists(SECURE_CONFIG_SALT_PATH)
