# utils/logging_utils.py
import os
from datetime import datetime
from typing import Any, Dict

LOG_DIRECTORY = "logs"
LOG_FILE_NAME = "security.log"
FULL_LOG_PATH = os.path.join(LOG_DIRECTORY, LOG_FILE_NAME)

def log_event(log_type: str, message: str, **kwargs: Any):
    """
    Centralized logging utility for the S1 Assistant.
    Logs events to a specified file with a structured format.

    :param log_type: A string categorizing the event (e.g., "SECURITY", "USER_MANAGER", "ENCRYPTION").
    :param message: The main message describing the event.
    :param kwargs: Optional additional context to include in the log entry.
                   Examples: user, intent, entity, role, score, file_path.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build a context string from kwargs
    context_parts = []
    for key, value in kwargs.items():
        if value is not None:
            context_parts.append(f"{key.capitalize()}:'{value}'")
    context_string = " ".join(context_parts)
    if context_string:
        context_string = f" ({context_string})"

    log_entry = f"[{timestamp}] [{log_type}] {message}{context_string}\n"
    
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    try:
        with open(FULL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except IOError as e:
        print(f"[ERROR] Failed to write to log file {FULL_LOG_PATH}: {e}")
