# nlp/packs/bangla_pack.py
from nlp.languages import BaseLanguagePack
from typing import Dict, List, Tuple, Set

class BanglaPack(BaseLanguagePack):
    lang_code: str = "bn"

    # Unicode range for Bengali script
    script_unicode_ranges: List[Tuple[int, int]] = [
        (0x0980, 0x09FF) 
    ]

    stop_words: Set[str] = {
        "একটি", "এবং", "এর", "জন্য", "হয়", "হচ্ছে", "এটা", "দয়া করে", "পারবে", "তুমি", "আপনি", 
        "খুলে", "খুলো", "খোল", "বন্ধ", "কর", "করো", "দাও", "কি", "কোথায়", "কখন", "কেন", "কিভাবে", "বলুন"
    }

    synonym_map: Dict[str, str] = {
        "খোল": "খুলো",
        "চালু কর": "খুলো",
        "বন্ধ কর": "বন্ধ করো",
        "কয়টা বাজে": "সময়",
        "সময় কত": "সময়",
        "আজকের তারিখ": "তারিখ",
        "আজ কি বার": "তারিখ",
        "অনুসন্ধান কর": "সার্চ",
        "ওয়েবসাইট খুলুন": "ওয়েবসাইট খুলো",
        "রিস্টার্ট": "পুনরায় চালু করুন",
        "বন্ধ করুন": "shutdown", # Special case for shutdown
        "লক করুন": "লক কর",
        "ফাইল খোল": "ফাইল খুলুন",
        "ফাইল মুছে ফেলুন": "ফাইল ডিলিট করুন",
        "ফাইল মুভ করুন": "ফাইল সরান",
        "ডিরেক্টরি দেখান": "ফাইল দেখান",
        "ফাইল লিস্ট": "ফাইল দেখান"
    }

    intent_keywords: Dict[str, List[str]] = {
        "open_app": ["খুলো"],
        "close_app": ["বন্ধ করো"],
        "time": ["সময়"],
        "date": ["তারিখ"],
        "weather": ["আবহাওয়া", "তাপমাত্রা"],
        "system_info": ["সিস্টেম ইনফো"],
        "search_web": ["সার্চ"],
        "open_website": ["ওয়েবসাইট খুলো"],
        "shutdown_system": ["বন্ধ করুন", "shutdown"], # using special case shutdown for consistency with en
        "restart_system": ["পুনরায় চালু করুন"],
        "sleep_system": ["ঘুম পাড়াও"],
        "lock_system": ["লক কর"],
        "open_file": ["ফাইল খুলুন"],
        "delete_file": ["ফাইল ডিলিট করুন"],
        "move_file": ["ফাইল সরান"],
        "list_directory": ["ফাইল দেখান"],
    }
