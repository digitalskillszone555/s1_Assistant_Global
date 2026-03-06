from typing import List, Dict
from utils.logging_utils import log_event # Centralized logging

# --- User Roles ---
ADMIN_ROLE = "admin"
USER_ROLE = "user"
GUEST_ROLE = "guest" # Currently not used, but defined for future expansion

# --- Skill Permissions Mapping ---
# Maps skill 'intent' names to a list of roles that are allowed to execute them.
# IMPORTANT: This system now uses a DEFAULT-DENY model. If a skill is not listed
# here, or if a role is not explicitly allowed for a listed skill, access will be denied.
SKILL_PERMISSIONS: Dict[str, List[str]] = {
    "app_control": [ADMIN_ROLE, USER_ROLE], # Example: open/close apps
    "file_delete": [ADMIN_ROLE],             # Example: deleting files (Specific file delete)
    "file_control": [ADMIN_ROLE, USER_ROLE], # Example: creating/reading files (delete is more sensitive)
    "system_control": [ADMIN_ROLE],          # Example: shutdown, restart (Generic system control)
    "web_control": [ADMIN_ROLE, USER_ROLE],  # Example: open websites
    "set_ai_mode": [ADMIN_ROLE, USER_ROLE], # Example: change AI mode
    "save_fact": [ADMIN_ROLE, USER_ROLE],
    "get_memory_summary": [ADMIN_ROLE, USER_ROLE],
    "forget_last": [ADMIN_ROLE, USER_ROLE],
    "clear_memory": [ADMIN_ROLE],
    # --- New Skill Permissions (Admin only) ---
    "shutdown_system": [ADMIN_ROLE],
    "restart_system": [ADMIN_ROLE], # Adding for completeness, as it's a SystemControl skill
    "sleep_system": [ADMIN_ROLE],   # Adding for completeness
    "lock_system": [ADMIN_ROLE],    # Adding for completeness
    "open_file": [ADMIN_ROLE],
    "delete_file": [ADMIN_ROLE],    # This will be specifically for the new FileControlSkill's delete_file
    "move_file": [ADMIN_ROLE],
    "list_directory": [ADMIN_ROLE]  # Listing is sensitive for security audit
}

def can_execute(skill_intent: str, user_role: str) -> bool:
    """
    Checks if a given user role has permission to execute a specific skill intent.
    This function now implements a strict DEFAULT-DENY model.

    :param skill_intent: The intent string associated with the skill (e.g., "open_app", "delete_file").
    :param user_role: The role of the current user (e.g., "admin", "user", "guest").
    :return: True if the user has permission, False otherwise.
    """
    if user_role not in [ADMIN_ROLE, USER_ROLE, GUEST_ROLE]: # Ensure valid role
        log_event("PERMISSION", "PERMISSION DENIED: Invalid role attempting to execute skill.", 
                  user_role=user_role, intent=skill_intent)
        return False

    allowed_roles = SKILL_PERMISSIONS.get(skill_intent)

    if allowed_roles is None:
        log_event("PERMISSION", "PERMISSION DENIED: Skill not explicitly defined in SKILL_PERMISSIONS.", 
                  user_role=user_role, intent=skill_intent)
        return False
    
    if user_role not in allowed_roles:
        log_event("PERMISSION", "PERMISSION DENIED: Role not allowed to execute skill.", 
                  user_role=user_role, intent=skill_intent)
        return False
    
    return True

def get_allowed_skills_for_role(user_role: str) -> List[str]:
    """
    Returns a list of skill intents that a given user role is explicitly allowed to execute
    under the new DEFAULT-DENY model.
    """
    allowed_skills = []
    if user_role not in [ADMIN_ROLE, USER_ROLE, GUEST_ROLE]:
        log_event("PERMISSION", "SKILL LIST RETRIEVAL DENIED: Invalid role requesting allowed skills.", 
                  user_role=user_role)
        return [] # Invalid role has no allowed skills

    for skill_intent, roles in SKILL_PERMISSIONS.items():
        if user_role in roles:
            allowed_skills.append(skill_intent)
            
    return sorted(list(set(allowed_skills))) # Remove duplicates and sort for consistency



