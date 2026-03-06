# nlp/normalization.py
import re
from typing import Dict, List, Any
from nlp.data import get_nlp_data

class TextNormalizer:
    """
    Normalizes mixed Bangla-English text for intent matching.
    Includes lowercasing, punctuation removal, whitespace trimming,
    and basic synonym replacement.
    """
    def __init__(self):
        self.nlp_data = get_nlp_data()
        self.unified_synonym_map: Dict[str, str] = {}
        self._build_unified_synonym_map()

    def _build_unified_synonym_map(self):
        """Builds a flat map of all synonyms from all registered language packs to their canonical keywords."""
        s_map = {}
        for intent_data in self.nlp_data.intent_definitions.values():
            for lang_code, lang_synonyms in intent_data.get("synonyms", {}).items():
                for synonym, canonical in lang_synonyms.items():
                    s_map[synonym.lower()] = canonical.lower()
        self.unified_synonym_map = s_map

    def normalize(self, text: str, detected_langs: List[Dict[str, Any]]) -> str:
        """
        Normalizes text by lowercasing, removing punctuation, trimming whitespace,
        and replacing known synonyms with canonical forms.
        """
        if not text:
            return ""
        
        # 1. Convert to lowercase
        normalized_text = text.lower()
        
        # 2. Basic synonym replacement (before removing punctuation for phrases)
        for synonym, canonical in self.unified_synonym_map.items():
            normalized_text = normalized_text.replace(synonym, canonical)

        # 3. Remove punctuation (keeps letters, numbers, and spaces from all scripts)
        # Combine unicode ranges from all registered language packs
        all_script_chars_pattern = ""
        for pack in self.nlp_data._language_registry.get_all_packs():
            for start, end in pack.script_unicode_ranges:
                all_script_chars_pattern += f"\\u{start:04x}-\\u{end:04x}"
        
        # Keep letters, numbers, spaces, and all script characters
        normalized_text = re.sub(f'[^\w\\s{all_script_chars_pattern}]', '', normalized_text)
        
        # 4. Replace multiple spaces with a single space and trim
        normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
        
        # 5. Remove language-specific stop words to help entity extraction
        # Combine stop words from all detected languages
        combined_stop_words = set()
        for lang_info in detected_langs:
            lang_code = lang_info["lang"]
            if lang_code != "unknown" and lang_code in self.nlp_data.stop_words:
                combined_stop_words.update(self.nlp_data.stop_words[lang_code])
        
        words = normalized_text.split()
        words = [word for word in words if word not in combined_stop_words]
        
        normalized_text = " ".join(words)

        return normalized_text

# Singleton instance
_normalizer_instance = None

def get_text_normalizer() -> TextNormalizer:
    """Provides access to the singleton TextNormalizer instance."""
    global _normalizer_instance
    if _normalizer_instance is None:
        _normalizer_instance = TextNormalizer()
    return _normalizer_instance
