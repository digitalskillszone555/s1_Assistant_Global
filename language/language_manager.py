# language/language_manager.py

import os
import json
import difflib
from user.user_manager import get_user_manager
from memory.memory_manager import get_memory_manager
from nlp.intent_mapper import map_intent_from_text # New import for Banglish NLP

class LanguageManager:
    def __init__(self):
        self.user_manager = get_user_manager()
        self.memory_manager = get_memory_manager()
        self.packs_dir = "language/packs"
        self.language_pack = None
        self.default_lang = "en"
        self.load_user_language()

    def load_user_language(self):
        """Loads the current user's preferred language, or defaults to English."""
        lang_code = self.memory_manager.get_memory("profile", "language")
        if not lang_code:
            lang_code = self.default_lang
            self.memory_manager.save_memory("profile", "language", lang_code)
        
        self.load_language(lang_code)

    def load_language(self, lang_code: str):
        """Loads a language pack from a JSON file."""
        file_path = os.path.join(self.packs_dir, f"{lang_code}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.language_pack = json.load(f)
            print(f"[LangM] Language pack '{self.language_pack['name']}' loaded.")
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"[LangM ERROR] Could not load language pack for '{lang_code}'. Falling back to default.")
            if lang_code != self.default_lang:
                self.load_language(self.default_lang)

    def get_reply(self, key: str, **kwargs):
        """Gets a formatted reply from the current language pack."""
        if not self.language_pack:
            return "Language pack not loaded."
        
        reply_templates = self.language_pack.get("replies", {}).get(key)
        if not reply_templates:
            return ""

        import random
        template = random.choice(reply_templates)
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"[LangM Reply Error] Missing formatting key {e} in template for '{key}'")
            return template

    def map_intent(self, text: str):
        """
        Processes text to find the best intent and entity.
        It now includes a special path for Banglish NLP.
        """
        if not self.language_pack:
            return None

        # --- Banglish NLP Layer ---
        # If the current language is Bangla, try the new rule-based NLP first.
        if self.language_pack.get("code") == "bn":
            banglish_intent = map_intent_from_text(text)
            if banglish_intent:
                return banglish_intent

        # --- Fallback to existing JSON-based logic ---
        print("[LangM] Falling back to JSON-based intent mapping.")
        text_lower = text.lower().strip()
        
        for phrase, intent in self.language_pack.get("keywords", {}).items():
            if phrase in text_lower:
                entity = text_lower.split(phrase, 1)[-1].strip()
                return {"intent": intent, "entity": entity or None}

        words = text_lower.split()
        for word in words:
            for intent, patterns in self.language_pack.get("intents", {}).items():
                if word in patterns:
                    entity_data = self.language_pack.get("entities", {}).get("app", {})
                    best_entity, score = self._find_best_entity(text_lower, entity_data)
                    return {"intent": intent, "entity": best_entity}
        
        return None

    def _find_best_entity(self, text: str, entity_data: dict, cutoff=0.6):
        """Finds the best entity match from the text."""
        best_match, highest_score = None, 0.0
        text_words = text.split()

        for entity_name, synonyms in entity_data.items():
            all_patterns = [entity_name] + synonyms
            for pattern in all_patterns:
                for word in text_words:
                    score = difflib.SequenceMatcher(None, pattern, word).ratio()
                    if score > highest_score and score >= cutoff:
                        highest_score = score
                        best_match = entity_name
        
        return best_match, highest_score

# Global instance
S1_LANGUAGE_MANAGER = LanguageManager()

def get_language_manager():
    return S1_LANGUAGE_MANAGER
