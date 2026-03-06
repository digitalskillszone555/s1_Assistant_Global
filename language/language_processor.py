# language/language_processor.py
# This module is now deprecated. All logic has been moved to LanguageManager.

def process_language(text: str) -> str:
    """
    This function is now a pass-through. The core logic is in LanguageManager.
    It simply returns the text as-is, because the new system handles normalization
    during the intent mapping phase.
    """
    print("[WARN] language_processor.process_language is deprecated.")
    return text
