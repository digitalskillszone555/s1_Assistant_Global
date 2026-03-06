# language/smart_matcher.py
# This module is now deprecated. All logic has been moved to LanguageManager.
from language.language_manager import get_language_manager

def smart_match(text: str):
    """
    This function is now a pass-through to the new LanguageManager.
    """
    print("[WARN] smart_matcher.smart_match is deprecated. Using LanguageManager.")
    lang_manager = get_language_manager()
    return lang_manager.map_intent(text)
