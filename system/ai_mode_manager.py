# system/ai_mode_manager.py

import os
import json

class AIModeManager:
    """Manages the AI processing mode (online, offline, smart)."""
    def __init__(self, config_path="memory/ai_mode.json"):
        self.config_path = config_path
        self.valid_modes = ["online", "offline", "smart"]
        self.ai_mode = self._load_mode()
        print(f"[AIModeManager] AI Mode initialized to: '{self.ai_mode}'")

    def _load_mode(self):
        """Loads the AI mode from a config file, defaulting to 'smart'."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    mode = data.get("ai_mode", "smart")
                    if mode in self.valid_modes:
                        return mode
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return "smart" # Default value

    def _save_mode(self):
        """Saves the current AI mode to the config file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({"ai_mode": self.ai_mode}, f, indent=4)

    def set_ai_mode(self, mode: str):
        """
        Sets the AI processing mode.
        Returns a tuple (success: bool, message: str).
        """
        mode = mode.lower()
        if mode in self.valid_modes:
            self.ai_mode = mode
            self._save_mode()
            print(f"[AIModeManager] AI mode switched to '{self.ai_mode}'")
            return True, f"AI mode switched to {self.ai_mode}."
        else:
            return False, f"Invalid AI mode '{mode}'. Valid modes are: {', '.join(self.valid_modes)}."

    def get_ai_mode(self):
        """Returns the current AI mode."""
        return self.ai_mode

# Singleton instance
_ai_mode_manager_instance = None

def get_ai_mode_manager():
    """Provides access to the singleton AIModeManager instance."""
    global _ai_mode_manager_instance
    if _ai_mode_manager_instance is None:
        _ai_mode_manager_instance = AIModeManager()
    return _ai_mode_manager_instance
