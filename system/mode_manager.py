# system/mode_manager.py

import os
import json
from user.user_manager import get_user_manager

class ModeManager:
    def __init__(self):
        self.user_manager = get_user_manager()
        self.modes_dir = "modes"
        if not os.path.exists(self.modes_dir):
            os.makedirs(self.modes_dir)
        
        self.default_modes = {
            "normal": {
                "reply_style": "friendly",
                "notification_volume": "speak",
                "allowed_actions": ["all"] # all actions allowed
            },
            "office": {
                "reply_style": "formal",
                "notification_volume": "silent",
                "allowed_actions": ["open", "close", "time", "date", "weather", "set_reminder", "list_reminders", "save_fact"]
            },
            "sleep": {
                "reply_style": "short",
                "notification_volume": "silent",
                "allowed_actions": ["time", "set_reminder"] # Only allow time checks and new alarms
            },
            "study": {
                "reply_style": "short",
                "notification_volume": "silent",
                "allowed_actions": ["open", "close", "time", "date", "weather"]
            },
            "gaming": {
                "reply_style": "short",
                "notification_volume": "silent",
                "allowed_actions": ["open", "close", "time"]
            }
        }
        self.active_mode = "normal" # Default active mode

    def _get_user_modes_file(self, username: str):
        return os.path.join(self.modes_dir, f"{username}.json")

    def _load_modes(self, username: str):
        file_path = self._get_user_modes_file(username)
        if not os.path.exists(file_path):
            # If user has no mode file, create one with defaults
            self._save_modes(username, {"active_mode": "normal", "modes": self.default_modes})
            return {"active_mode": "normal", "modes": self.default_modes}
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"active_mode": "normal", "modes": self.default_modes}

    def _save_modes(self, username: str, data: dict):
        file_path = self._get_user_modes_file(username)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def set_mode(self, mode_name: str):
        """Sets the active mode for the current user."""
        username = self.user_manager.current_user
        data = self._load_modes(username)
        if mode_name not in data["modes"]:
            return False, f"Mode '{mode_name}' not found."

        data["active_mode"] = mode_name
        self.active_mode = mode_name # Update runtime active mode
        self._save_modes(username, data)
        return True, f"Switched to {mode_name} mode."

    def get_current_mode_settings(self):
        """Returns the settings for the currently active mode."""
        username = self.user_manager.current_user
        data = self._load_modes(username)
        self.active_mode = data.get("active_mode", "normal")
        return data["modes"].get(self.active_mode, self.default_modes["normal"])

    def list_modes(self):
        """Lists all available modes for the current user."""
        username = self.user_manager.current_user
        data = self._load_modes(username)
        return list(data["modes"].keys())

    def add_mode(self, mode_name: str, settings: dict):
        """Adds a new custom mode for the current user."""
        username = self.user_manager.current_user
        data = self._load_modes(username)
        if mode_name in data["modes"]:
            return False, f"Mode '{mode_name}' already exists."
        
        data["modes"][mode_name] = settings
        self._save_modes(username, data)
        return True, f"Created new mode: '{mode_name}'."

    def delete_mode(self, mode_name: str):
        """Deletes a custom mode for the current user."""
        if mode_name in self.default_modes:
            return False, f"Cannot delete a default mode."

        username = self.user_manager.current_user
        data = self._load_modes(username)
        
        if mode_name in data["modes"]:
            del data["modes"][mode_name]
            # If the deleted mode was active, revert to normal
            if data["active_mode"] == mode_name:
                data["active_mode"] = "normal"
                self.active_mode = "normal"
            self._save_modes(username, data)
            return True, f"Mode '{mode_name}' deleted."
        return False, f"Mode '{mode_name}' not found."

_s1_mode_manager_instance = None

def get_mode_manager():
    global _s1_mode_manager_instance
    if _s1_mode_manager_instance is None:
        _s1_mode_manager_instance = ModeManager()
    return _s1_mode_manager_instance
