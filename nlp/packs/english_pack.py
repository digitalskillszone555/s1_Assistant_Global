# nlp/packs/english_pack.py
from nlp.languages import BaseLanguagePack
from typing import Dict, List, Tuple, Set

class EnglishPack(BaseLanguagePack):
    lang_code: str = "en"
    
    script_unicode_ranges: List[Tuple[int, int]] = [
        (0x0041, 0x005A), # Uppercase Latin (A-Z)
        (0x0061, 0x007A)  # Lowercase Latin (a-z)
    ]

    stop_words: Set[str] = {
        "a", "an", "the", "in", "on", "for", "is", "are", "it", "please", "can", "you",
        "what", "where", "when", "why", "how", "tell", "me", "show"
    }

    # Maps synonyms to canonical keywords
    synonym_map: Dict[str, str] = {
        "start": "open",
        "launch": "open",
        "terminate": "close",
        "shut down": "shutdown",
        "reboot": "restart",
        "lock computer": "lock",
        "find": "search",
        "what time is it": "time",
        "what is today's date": "date",
        "go to": "open website",
        "show files": "list directory"
    }

    # Intent keywords specific to English
    intent_keywords: Dict[str, List[str]] = {
        "open_app": ["open", "launch"],
        "close_app": ["close", "exit", "quit"],
        "time": ["time"],
        "date": ["date"],
        "weather": ["weather", "temperature"],
        "system_info": ["system info", "computer details"],
        "search_web": ["search", "google"],
        "open_website": ["open website", "go to"],
        "shutdown_system": ["shutdown", "shut down"],
        "restart_system": ["restart"],
        "sleep_system": ["sleep"],
        "lock_system": ["lock", "lock computer"],
        "open_file": ["open file"],
        "delete_file": ["delete file"],
        "move_file": ["move file"],
        "list_directory": ["list directory", "list files"],
    }
