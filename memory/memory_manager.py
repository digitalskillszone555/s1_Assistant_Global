# memory/memory_manager.py

import os
import json
import time
import base64
from user.user_manager import get_user_manager
from system.config_loader import load_config, save_config
from utils.logging_utils import log_event # Centralized logging

# --- Cryptography Imports ---
try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    print("[WARN] Cryptography package not found. Memory encryption is DISABLED.")

# --- Encryption Engine ---

def _get_encryption_key():
    if not CRYPTOGRAPHY_AVAILABLE: return None
    config = load_config() or {}
    secret = config.get("encryption_secret")
    salt = config.get("encryption_salt")
    config_updated = False
    if not secret:
        log_event("ENCRYPTION", "Master encryption secret not found. Generating a new one.")
        secret = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
        config["encryption_secret"] = secret
        config_updated = True
    if not salt:
        log_event("ENCRYPTION", "Encryption salt not found. Generating a new one.")
        salt = base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8')
        config["encryption_salt"] = salt
        config_updated = True
    if config_updated: save_config(config)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=base64.urlsafe_b64decode(salt.encode('utf-8')),
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode('utf-8')))

class EncryptionEngine:
    def __init__(self, key):
        self.key = key
        if self.key: self.fernet = Fernet(self.key)

    def encrypt(self, data: bytes) -> bytes:
        if not self.key: return data
        return self.fernet.encrypt(data)

    def decrypt(self, token: bytes) -> bytes | None:
        if not self.key: return token
        try:
            return self.fernet.decrypt(token)
        except InvalidToken:
            log_event("ENCRYPTION", "DECRYPTION FAILED: Invalid token or key.")
            return None
        except Exception as e:
            log_event("ENCRYPTION", f"DECRYPTION FAILED: An unexpected error occurred: {e}")
            return None

class MemoryManager:
    def __init__(self):
        self.user_manager = get_user_manager()
        self.memory_types = ["profile", "habits", "facts"]
        self.encryption_engine = EncryptionEngine(_get_encryption_key())
        
        # Granular limits per memory type for different user plans.
        self.limits = {
            "free": {"facts": 200, "habits": 50, "profile": 50},
            "pro":  {"facts": 5000, "habits": 1000, "profile": 1000}
        }
        
        if not CRYPTOGRAPHY_AVAILABLE:
            log_event("MEMORY_MANAGER", "Cryptography package not installed. All memory operations will be in plaintext.", level="WARNING")
            print("[CRITICAL SECURITY WARNING] MEMORY IS NOT ENCRYPTED.") # Keep print for critical visibility
        else:
            log_event("MEMORY_MANAGER", "Memory encryption is ENABLED.")
            log_event("MEMORY_MANAGER", "Quota management is active.")


    def _get_user_memory_file(self, type: str):
        if type not in self.memory_types: return None
        user_memory_path = self.user_manager.get_current_user_memory_path()
        file_path = os.path.join(user_memory_path, f"{type}.json")
        if not os.path.exists(file_path):
            if not os.path.exists(user_memory_path): os.makedirs(user_memory_path)
            with open(file_path, 'wb') as f: f.write(self.encryption_engine.encrypt(b'{}'))
        return file_path

    def _load_memory(self, type: str):
        file_path = self._get_user_memory_file(type)
        if not file_path: return {}
        try:
            with open(file_path, 'rb') as f: encrypted_data = f.read()
            if not encrypted_data: return {}
            decrypted_data_bytes = self.encryption_engine.decrypt(encrypted_data)
            if decrypted_data_bytes is not None:
                return json.loads(decrypted_data_bytes)
            _log_event("MIGRATION", f"Attempting migration for '{file_path}'.")
            try:
                plaintext_data = json.loads(encrypted_data.decode('utf-8'))
                _log_event("MIGRATION", f"Successfully loaded '{file_path}' as plaintext. Migrating to encrypted format.")
                self._save_memory(type, plaintext_data)
                return plaintext_data
            except (json.JSONDecodeError, UnicodeDecodeError):
                _log_event("CRITICAL", f"Failed to load '{file_path}'. File is corrupt.")
                return {}
        except (IOError, FileNotFoundError) as e:
            _log_event("ERROR", f"Failed to read memory file '{file_path}': {e}")
            return {}

    def _save_memory(self, type: str, data: dict):
        file_path = self._get_user_memory_file(type)
        if not file_path: return False
        json_data_bytes = json.dumps(data, indent=4).encode('utf-8')
        encrypted_data = self.encryption_engine.encrypt(json_data_bytes)
        with open(file_path, 'wb') as f: f.write(encrypted_data)
        return True

    # --- Public API (Quota Logic is Here) ---

    def save_memory(self, type: str, key: str, value: any):
        """Saves a key-value pair, enforcing per-user and per-type memory quotas."""
        if type not in self.memory_types: return False
        
        data = self._load_memory(type)
        if data is None: return False
        
        data[key] = {"value": value, "timestamp": time.time()}
        
        user_info = self.user_manager.get_current_user_info()
        current_plan = user_info.get("plan", "free") if user_info else "free"
        
        # Get the specific limit for this memory type and plan
        plan_limits = self.limits.get(current_plan, self.limits["free"])
        limit = plan_limits.get(type, 0)

        # Enforce the limit for all plans to prevent unbounded growth
        if len(data) > limit:
            # Pruning strategy: remove the oldest entry
            oldest_key = min(data, key=lambda k: data[k].get('timestamp', 0))
            del data[oldest_key]
            
            # Log the pruning event
            current_user = self.user_manager.current_user
            _log_event("QUOTA", f"Limit of {limit} reached for user '{current_user}' (Plan: {current_plan}) in memory type '{type}'. Pruned oldest entry '{oldest_key}'.")
        
        return self._save_memory(type, data)

    def get_memory(self, type: str, key: str):
        data = self._load_memory(type)
        if data and key in data:
            return data[key].get("value")
        return None

    def delete_memory(self, type: str, key: str):
        data = self._load_memory(type)
        if data and key in data:
            del data[key]
            return self._save_memory(type, data)
        return False
        
    def list_memory(self, type: str):
        data = self._load_memory(type)
        if not data: return []
        # Ensure compatibility with older data that might not have 'value' key
        return [item.get('value') for item in data.values() if 'value' in item]

# Global memory manager instance
S1_MEMORY = MemoryManager()

def get_memory_manager():
    return S1_MEMORY
