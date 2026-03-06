# analytics/skill_tracker.py
import json
import os
import datetime
from typing import List, Dict

LOGS_DIR = "logs"
LOG_FILE_PATH = os.path.join(LOGS_DIR, "skill_logs.json")
MAX_LOG_ENTRIES = 1000  # Max number of log entries to keep

# --- Log Status Enums ---
SUCCESS = "SUCCESS"
PERMISSION_DENIED = "PERMISSION_DENIED"
SECURITY_BLOCKED = "SECURITY_BLOCKED"
NOT_FOUND = "NOT_FOUND"
EXECUTION_ERROR = "EXECUTION_ERROR"

def _read_logs() -> List[Dict]:
    """Reads and returns all logs from the log file."""
    if not os.path.exists(LOG_FILE_PATH):
        return []
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError, FileNotFoundError):
        # If file is corrupt, unreadable, or not found, return an empty list
        return []

def _write_logs(logs: List[Dict]):
    """Writes a list of log entries to the log file."""
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
    except IOError as e:
        print(f"[SkillTracker ERROR] Could not write to log file: {e}")

def log_skill(skill_intent: str, user_role: str, status: str, reason: str = None):
    """
    Logs a skill usage event. This function is designed to be fail-safe
    and not interrupt the main application flow.
    """
    try:
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "skill_intent": skill_intent,
            "user_role": user_role,
            "status": status,
            "reason": reason
        }

        logs = _read_logs()
        logs.append(log_entry)

        # Simple rotation: keep only the last MAX_LOG_ENTRIES
        if len(logs) > MAX_LOG_ENTRIES:
            logs = logs[-MAX_LOG_ENTRIES:]
        
        _write_logs(logs)

    except Exception as e:
        # This broad exception ensures the logging mechanism NEVER crashes the main application
        print(f"[SkillTracker FATAL] An unexpected error occurred during logging: {e}")
