# ui/skill_categories.py
from typing import Dict, List

# --- Skill Categories ---
CATEGORY_APP = "App"
CATEGORY_FILE = "File"
CATEGORY_SYSTEM = "System"
CATEGORY_WEB = "Web"
CATEGORY_MEMORY = "Memory"
CATEGORY_AI = "AI"
CATEGORY_UTILITY = "Utility"
CATEGORY_UNCATEGORIZED = "Uncategorized"

# --- Skill Intent to Category Mapping ---
# Maps each known skill intent to its primary category.
# Intents not listed here will fall into CATEGORY_UNCATEGORIZED by default.
SKILL_CATEGORY_MAP: Dict[str, str] = {
    # App Control Skills (inferred from skills/app_control.py)
    "open_app": CATEGORY_APP,
    "close_app": CATEGORY_APP,

    # File Control Skills (inferred from skills/file_control.py)
    "create_file": CATEGORY_FILE,
    "delete_file": CATEGORY_FILE,
    "read_file": CATEGORY_FILE,
    "write_file": CATEGORY_FILE,

    # System Control Skills (inferred from skills/system_control.py)
    "shutdown": CATEGORY_SYSTEM,
    "restart": CATEGORY_SYSTEM,
    "sleep": CATEGORY_SYSTEM,
    "lock_screen": CATEGORY_SYSTEM, # Assuming this might exist

    # Web Control Skills (inferred from skills/web_control.py)
    "open_website": CATEGORY_WEB,
    "search_web": CATEGORY_WEB,

    # Core Memory Commands (from core/brain.py)
    "save_fact": CATEGORY_MEMORY,
    "get_memory_summary": CATEGORY_MEMORY,
    "forget_last": CATEGORY_MEMORY,
    "clear_memory": CATEGORY_MEMORY,

    # AI Mode Commands (from core/brain.py)
    "set_ai_mode": CATEGORY_AI,

    # Legacy/Utility Skills (from skills/router.py)
    "time": CATEGORY_UTILITY,
    "date": CATEGORY_UTILITY,
    "weather": CATEGORY_UTILITY,
    "system_info": CATEGORY_UTILITY,
}

def get_category(skill_intent: str) -> str:
    """
    Returns the category for a given skill intent.
    If the intent is not mapped, it returns CATEGORY_UNCATEGORIZED.
    """
    return SKILL_CATEGORY_MAP.get(skill_intent, CATEGORY_UNCATEGORIZED)

def get_skills_by_category() -> Dict[str, List[str]]:
    """
    Returns a dictionary mapping category names to lists of skill intents within that category.
    """
    categories_to_skills: Dict[str, List[str]] = {}
    
    # Initialize all defined categories
    for cat in [CATEGORY_APP, CATEGORY_FILE, CATEGORY_SYSTEM, CATEGORY_WEB, 
                 CATEGORY_MEMORY, CATEGORY_AI, CATEGORY_UTILITY, CATEGORY_UNCATEGORIZED]:
        categories_to_skills[cat] = []

    for intent, category in SKILL_CATEGORY_MAP.items():
        categories_to_skills[category].append(intent)
    
    # Handle uncategorized skills if any are dynamically discovered later
    # (though with a comprehensive map, this list should ideally be empty)
    # For now, we rely on the default CATEGORY_UNCATEGORIZED from get_category
    
    return categories_to_skills
