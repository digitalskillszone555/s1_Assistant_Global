# system/reminder_manager.py

import os
import json
import uuid
import time
import parsedatetime as pdt
from datetime import datetime
from user.user_manager import get_user_manager
from collections import deque

class ReminderManager:
    def __init__(self):
        self.user_manager = get_user_manager()
        self.reminders_dir = "reminders"
        if not os.path.exists(self.reminders_dir):
            os.makedirs(self.reminders_dir)
        
        self.time_parser = pdt.Calendar()
        self.notification_queue = deque()

    def _get_user_reminders_file(self, username: str):
        return os.path.join(self.reminders_dir, f"{username}.json")

    def _load_reminders(self, username: str):
        file_path = self._get_user_reminders_file(username)
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_reminders(self, username: str, reminders: list):
        file_path = self._get_user_reminders_file(username)
        with open(file_path, 'w') as f:
            json.dump(reminders, f, indent=4)

    def add_reminder(self, time_str: str, message: str, repeat: str = None):
        """Adds a reminder for the current user."""
        username = self.user_manager.current_user
        reminders = self._load_reminders(username)
        
        time_struct, parse_status = self.time_parser.parse(time_str)
        if parse_status == 0:
            return False, "Sorry, I could not understand the time."

        due_time = datetime.fromtimestamp(time.mktime(time_struct))
        
        reminder = {
            "id": str(uuid.uuid4()),
            "due_time": due_time.isoformat(),
            "message": message,
            "repeat": repeat, # e.g., "daily", "weekly"
            "created_at": datetime.now().isoformat()
        }
        reminders.append(reminder)
        self._save_reminders(username, reminders)
        
        return True, f"Okay, I will remind you to '{message}' at {due_time.strftime('%I:%M %p on %A, %B %d')}."

    def get_reminders(self):
        """Gets all reminders for the current user."""
        username = self.user_manager.current_user
        return self._load_reminders(username)

    def delete_reminder(self, reminder_id: str):
        """Deletes a reminder by its ID for the current user."""
        username = self.user_manager.current_user
        reminders = self._load_reminders(username)
        
        initial_count = len(reminders)
        reminders = [r for r in reminders if r.get('id') != reminder_id]
        
        if len(reminders) < initial_count:
            self._save_reminders(username, reminders)
            return True
        return False

    def check_due_reminders(self):
        """
        Checks for due reminders for ALL users and adds them to a notification queue.
        This should be run periodically in a background thread.
        """
        all_users = self.user_manager.list_users()
        now = datetime.now()
        
        for username in all_users:
            reminders_to_keep = []
            reminders = self._load_reminders(username)
            updated = False
            
            for reminder in reminders:
                due_time = datetime.fromisoformat(reminder["due_time"])
                
                if now >= due_time:
                    # Reminder is due! Add to queue for notification.
                    notification = f"Hey {username}, this is a reminder to {reminder['message']}"
                    self.notification_queue.append(notification)
                    print(f"[REMINDER] Due for {username}: {reminder['message']}")
                    updated = True
                    
                    # Handle repeating reminders
                    if reminder.get("repeat") == "daily":
                        reminder["due_time"] = (due_time + timedelta(days=1)).isoformat()
                        reminders_to_keep.append(reminder)
                    elif reminder.get("repeat") == "weekly":
                        reminder["due_time"] = (due_time + timedelta(weeks=1)).isoformat()
                        reminders_to_keep.append(reminder)
                    # One-time reminders are not added back
                else:
                    reminders_to_keep.append(reminder)
            
            if updated:
                self._save_reminders(username, reminders_to_keep)

    def get_notification(self):
        """Pops a notification from the queue if one exists."""
        if self.notification_queue:
            return self.notification_queue.popleft()
        return None

# Global instance
S1_REMINDER_MANAGER = ReminderManager()

def get_reminder_manager():
    return S1_REMINDER_MANAGER
