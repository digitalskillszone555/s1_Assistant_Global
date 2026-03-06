# system/automation_manager.py

import os
import json
import time
from datetime import datetime
from user.user_manager import get_user_manager

class AutomationManager:
    def __init__(self, action_executors=None):
        self.user_manager = get_user_manager()
        self.workflows_dir = "workflows"
        if not os.path.exists(self.workflows_dir):
            os.makedirs(self.workflows_dir)
        
        # Dependency injection for action execution to avoid circular imports
        self.action_executors = action_executors or {}

    def _get_user_workflows_file(self, username: str):
        return os.path.join(self.workflows_dir, f"{username}.json")

    def _load_workflows(self, username: str):
        file_path = self._get_user_workflows_file(username)
        if not os.path.exists(file_path):
            return {"workflows": {}}
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"workflows": {}}

    def _save_workflows(self, username: str, data: dict):
        file_path = self._get_user_workflows_file(username)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def add_workflow(self, name: str, trigger: dict, actions: list):
        """Adds a workflow for the current user."""
        username = self.user_manager.current_user
        data = self._load_workflows(username)
        
        if name in data["workflows"]:
            return False, f"A workflow named '{name}' already exists."
        
        data["workflows"][name] = {"trigger": trigger, "actions": actions}
        self._save_workflows(username, data)
        return True, f"Workflow '{name}' has been created."

    def get_workflows(self):
        """Gets all workflow names for the current user."""
        username = self.user_manager.current_user
        data = self._load_workflows(username)
        return list(data["workflows"].keys())

    def delete_workflow(self, name: str):
        """Deletes a workflow by its name for the current user."""
        username = self.user_manager.current_user
        data = self._load_workflows(username)
        
        if name in data["workflows"]:
            del data["workflows"][name]
            self._save_workflows(username, data)
            return True
        return False

    def run_workflow(self, name: str):
        """
        Finds a workflow by its voice trigger name and executes its actions.
        """
        username = self.user_manager.current_user
        data = self._load_workflows(username)
        workflow = data["workflows"].get(name)

        if not workflow or workflow["trigger"]["type"] != "voice":
            return False

        print(f"[AUTOMATION] Running workflow '{name}' for user '{username}'...")
        for action_details in workflow["actions"]:
            action_type = action_details.get("action")
            executor = self.action_executors.get(action_type)
            
            if executor:
                # Pass parameters to the executor
                params = {k: v for k, v in action_details.items() if k != 'action'}
                try:
                    executor(**params)
                    time.sleep(1) # Pause between actions
                except Exception as e:
                    print(f"[AUTOMATION ERROR] Failed to execute action {action_details}: {e}")
            else:
                print(f"[AUTOMATION WARN] No executor found for action type '{action_type}'.")
        
        return True
        
    def check_triggers(self):
        """
        Checks for time-based or event-based triggers for ALL users.
        This would be expanded in a real implementation.
        For now, we will just have a placeholder for time-based triggers.
        """
        # This is a placeholder for a more complex trigger engine.
        # A real implementation would involve a scheduler (like APScheduler).
        pass

# We will create the instance in main.py after initializing the speaker, etc.
S1_AUTOMATION_MANAGER = None

def initialize_automation_manager(action_executors):
    global S1_AUTOMATION_MANAGER
    S1_AUTOMATION_MANAGER = AutomationManager(action_executors)
    return S1_AUTOMATION_MANAGER

def get_automation_manager():
    return S1_AUTOMATION_MANAGER
