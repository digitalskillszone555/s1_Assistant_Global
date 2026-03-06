# =========================
# S1 COMMAND CLEANER
# PRODUCTION FINAL VERSION
# =========================

import re

# Words / phrases that add no meaning
FILLER_WORDS = [
    "please", "plz", "kindly", "sir", "dada", "bro", "buddy",
    "can you", "could you", "would you", "will you",
    "hey", "hi", "hello", "ok", "okay", "assistant", "s1"
]

# These must NEVER be rejected even if short
CRITICAL_COMMANDS = [
    "exit", "quit", "stop", "close", "shutdown", "turn off"
]

# Known junk phrases from STT
JUNK_PHRASES = [
    "is on", "always on", "yes on", "hey is on",
    "hello is on", "hi is on", "is oven", "essay on"
]


def clean_command(text: str) -> str:
    """
    Cleans & normalizes user voice commands safely.
    Protects real commands, rejects noise.
    """

    if not text:
        return ""

    original = text.lower().strip()
    text = original

    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # Reject known STT junk
    for junk in JUNK_PHRASES:
        if junk in text:
            print("[CLEANER] Rejected junk:", junk)
            return ""

    # Protect critical commands even if short
    for cmd in CRITICAL_COMMANDS:
        if cmd in text:
            print(f"[CLEANER] Critical allowed: {cmd}")
            return text.strip()

    # Remove filler words
    for filler in FILLER_WORDS:
        text = text.replace(filler, "")

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Final length check (after cleaning)
    if len(text.split()) < 2:
        print("[CLEANER] Rejected: too short")
        return ""

    print(f"[CLEANER] Cleaned: {text}")
    return text