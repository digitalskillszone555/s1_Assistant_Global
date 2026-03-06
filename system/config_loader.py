# system/config_loader.py
import json
import os
from typing import Dict, Any, Optional
from config.secure_config import get_secure_config_loader, secure_config_exists, secure_config_salt_exists # New imports
from utils.logging_utils import log_event # Centralized logging

CONFIG_PATH = os.path.join("config", "user_config.json")
REQUIRED_KEYS = {"language", "ai_mode", "voice_enabled"}

# --- Sensitive keys that MUST NOT be in user_config.json ---
SENSITIVE_KEYS = ["encryption_secret", "encryption_salt", "remote_control_token", "core_hashes"]

_secure_config_passphrase: Optional[str] = None

def set_secure_config_passphrase(passphrase: str):
    """Sets the passphrase for the SecureConfigLoader."""
    global _secure_config_passphrase
    _secure_config_passphrase = passphrase
    log_event("CONFIG_LOADER", "Secure config passphrase set.")

def load_config() -> Dict[str, Any]:
    """
    Loads the user configuration from user_config.json.
    Sensitive fields are explicitly removed if found (migration step).
    """
    user_config_data: Dict[str, Any] = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                user_config_data = json.load(f)
            log_event("CONFIG_LOADER", "user_config.json loaded.")
        except (json.JSONDecodeError, IOError) as e:
            log_event("CONFIG_LOADER", f"Error loading user_config.json: {e}", level="ERROR")
            return {}

    # --- Migration step: Ensure sensitive fields are NOT in user_config.json ---
    config_needs_save = False
    for key in SENSITIVE_KEYS:
        if key in user_config_data:
            del user_config_data[key]
            config_needs_save = True
            log_event("CONFIG_LOADER", f"Removed sensitive field '{key}' from user_config.json (migration/cleanup).")
    
    if config_needs_save:
        save_config(user_config_data) # Save cleaned non-sensitive config
        log_event("CONFIG_LOADER", "user_config.json cleaned and re-saved.")

    return user_config_data

def save_config(data: Dict[str, Any]):
    """
    Saves the provided dictionary to user_config.json.
    Ensures no sensitive fields are saved.
    """
    data_to_save = {k: v for k, v in data.items() if k not in SENSITIVE_KEYS}
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)
        log_event("CONFIG_LOADER", "user_config.json saved.")
        return True
    except IOError as e:
        log_event("CONFIG_LOADER", f"Error saving user_config.json: {e}", level="ERROR")
        return False

def get_secure_config_data(key: str, default: Any = None) -> Any:
    """
    Retrieves a value from the encrypted secure config.
    Requires the passphrase to have been set via set_secure_config_passphrase.
    """
    if _secure_config_passphrase is None:
        log_event("SECURE_CONFIG", "Attempted to access secure config without passphrase being set.", level="ERROR")
        raise ValueError("Secure config passphrase not set. Cannot access sensitive data.")
    
    loader = get_secure_config_loader(_secure_config_passphrase)
    return loader.get(key, default)

def set_secure_config_data(key: str, value: Any):
    """
    Sets a value in the encrypted secure config and saves it.
    Requires the passphrase to have been set.
    """
    if _secure_config_passphrase is None:
        log_event("SECURE_CONFIG", "Attempted to modify secure config without passphrase being set.", level="ERROR")
        raise ValueError("Secure config passphrase not set. Cannot modify sensitive data.")
    
    loader = get_secure_config_loader(_secure_config_passphrase)
    loader.set(key, value)
    log_event("SECURE_CONFIG", f"Secure config field '{key}' updated.")

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validates if the loaded config contains all necessary keys.
    """
    if not isinstance(config, dict):
        return False
    
    return REQUIRED_KEYS.issubset(config.keys())
