# security/hardening.py
import os
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from memory.memory_manager import get_memory_manager
from utils.logging_utils import log_event # Centralized logging

# --- Configuration ---
TRUST_SCORE_INITIAL = 100.0
TRUST_SCORE_THRESHOLD = 50.0 # Below this, commands are blocked
TRUST_SCORE_MAX = 100.0

RATE_LIMIT_WINDOW_SECONDS = 60 # 1 minute
RATE_LIMIT_MAX_COMMANDS = 10   # 10 commands per minute

REPLAY_PROTECTION_WINDOW_SECONDS = 10 # Prevent same critical command replay within 10 seconds
CRITICAL_COMMANDS = ["shutdown_system", "restart_system", "delete_file", "format_disk"] # List of intents to protect against replay

class UserSecurityContext:
    """Stores security-related state for each user/session."""
    def __init__(self):
        self.trust_score: float = TRUST_SCORE_INITIAL
        self.rate_limit_counter: int = 0
        self.rate_limit_window_start: float = time.time()
        self.command_history: List[Dict[str, Any]] = [] # For anomaly/replay detection
        self.last_critical_commands: Dict[str, float] = {} # {hash: timestamp} for replay protection

class SecurityHardener:
    """
    Implements advanced security features like rate limiting, trust scoring,
    anomaly detection, and integrity checks.
    """
    def __init__(self):
        self.user_contexts: Dict[str, UserSecurityContext] = {}
        self.CRITICAL_FILES = [
            "main.py",
            "core/brain.py",
            "skills/router.py",
            "security/permissions.py",
            "user/user_manager.py",
            "memory/memory_manager.py",
            "security/hardening.py",
            "nlp/router.py"
        ]
        self.TRUSTED_FILE_HASHES: Dict[str, str] = {} # Loaded from config or generated on first run
        self._load_trusted_hashes()

    def _get_user_context(self, username: str) -> UserSecurityContext:
        """Retrieves or creates a security context for a user, loading persistent data."""
        if username not in self.user_contexts:
            context = UserSecurityContext()
            
            # Load persistent trust score from user profile
            memory_manager = get_memory_manager()
            profile_security_context = memory_manager.get_memory("profile", "security_context")
            if profile_security_context and "trust_score" in profile_security_context:
                context.trust_score = profile_security_context["trust_score"]
                log_event("HARDENING", f"Loaded persistent trust score for user.", username=username, score=context.trust_score)
            else:
                context.trust_score = TRUST_SCORE_INITIAL
                log_event("HARDENING", f"Initialized new trust score for user.", username=username, score=context.trust_score)
            
            self.user_contexts[username] = context
        return self.user_contexts[username]

    def check_rate_limit(self, username: str, intent: str) -> Tuple[bool, str]:
        """
        Checks if the user is exceeding the command rate limit.
        """
        context = self._get_user_context(username)
        current_time = time.time()

        # Reset window if expired
        if current_time - context.rate_limit_window_start > RATE_LIMIT_WINDOW_SECONDS:
            context.rate_limit_window_start = current_time
            context.rate_limit_counter = 0

        context.rate_limit_counter += 1
        if context.rate_limit_counter > RATE_LIMIT_MAX_COMMANDS:
            self.update_trust_score(username, "RATE_LIMIT_EXCEEDED", intent=intent)
            log_event("HARDENING", f"RATE_LIMIT_BREACH for user.", username=username, intent=intent, score=context.trust_score)
            return False, "Command rate limit exceeded. Please wait and try again."
        return True, "Rate limit OK."

    def update_trust_score(self, username: str, event_type: str, intent: Optional[str] = None, entity: Optional[str] = None):
        """
        Adjusts the user's trust score based on the event type and persists it.
        """
        context = self._get_user_context(username)
        score_change = 0.0

        if event_type == "VALID_COMMAND":
            score_change = 0.5
        elif event_type == "LOW_CONFIDENCE":
            score_change = -0.1
        elif event_type == "PERMISSION_DENIED":
            score_change = -2.0
        elif event_type == "SECURITY_BLOCKED":
            score_change = -5.0
        elif event_type == "ANOMALY_DETECTED":
            score_change = -10.0
        elif event_type == "RATE_LIMIT_EXCEEDED":
            score_change = -3.0
        elif event_type == "REPLAY_BLOCKED":
            score_change = -5.0

        context.trust_score += score_change
        context.trust_score = max(0.0, min(TRUST_SCORE_MAX, context.trust_score)) # Keep within bounds

        log_event("HARDENING", f"TRUST_SCORE_UPDATE for user: Event '{event_type}'.", 
                  username=username, event=event_type, intent=intent, entity=entity, score=context.trust_score)

        # Persist the updated trust score
        memory_manager = get_memory_manager()
        profile_security_context = memory_manager.get_memory("profile", "security_context") or {}
        profile_security_context["trust_score"] = context.trust_score
        memory_manager.save_memory("profile", "security_context", profile_security_context)

        # Add to history for anomaly detection (simplified for this task)
        context.command_history.append({"time": time.time(), "intent": intent, "entity": entity, "event": event_type})
        context.command_history = [cmd for cmd in context.command_history if time.time() - cmd["time"] < 300] # Keep last 5 mins

    def check_trust_score(self, username: str) -> Tuple[bool, str]:
        """
        Checks if the user's trust score is above the threshold.
        """
        context = self._get_user_context(username)
        if context.trust_score < TRUST_SCORE_THRESHOLD:
            log_event("HARDENING", f"TRUST_SCORE_BLOCK for user. Score below threshold.", 
                      username=username, score=context.trust_score, threshold=TRUST_SCORE_THRESHOLD)
            return False, "Command blocked due to low trust score. Please try valid commands."
        return True, "Trust score OK."

    def check_command_replay(self, username: str, intent: str, entity: str) -> Tuple[bool, str]:
        """
        Prevents immediate replay of critical commands.
        """
        if intent not in CRITICAL_COMMANDS:
            return True, "Command not critical for replay check."

        command_hash = hashlib.sha256(f"{intent}-{entity}".encode('utf-8')).hexdigest()
        context = self._get_user_context(username)
        current_time = time.time()

        if command_hash in context.last_critical_commands:
            last_execution_time = context.last_critical_commands[command_hash]
            if current_time - last_execution_time < REPLAY_PROTECTION_WINDOW_SECONDS:
                self.update_trust_score(username, "REPLAY_BLOCKED", intent=intent, entity=entity)
                log_event("HARDENING", f"REPLAY_BLOCKED for user: Critical command repeated too quickly.", 
                          username=username, intent=intent, entity=entity)
                return False, "This critical command cannot be repeated so quickly."
        
        context.last_critical_commands[command_hash] = current_time
        return True, "Replay check OK."

    # --- Integrity Protection ---
    def _load_trusted_hashes(self):
        """Loads trusted file hashes from config."""
        from system.config_loader import load_config
        config = load_config() or {}
        self.TRUSTED_FILE_HASHES = config.get("core_hashes", {})
        if not self.TRUSTED_FILE_HASHES:
            log_event("INTEGRITY", "No trusted file hashes found in config. Please run generate_initial_hashes.")

    def _save_trusted_hashes(self, hashes: Dict[str, str]):
        """Saves trusted file hashes to config."""
        from system.config_loader import load_config, save_config
        config = load_config() or {}
        config["core_hashes"] = hashes
        save_config(config)
        log_event("INTEGRITY", "Trusted file hashes saved to config/user_config.json.")

    @staticmethod
    def _calculate_file_hash(filepath: str) -> Optional[str]:
        """Calculates SHA256 hash of a file."""
        if not os.path.exists(filepath):
            return None
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            log_event("INTEGRITY", f"ERROR calculating hash for file: {e}", file=filepath)
            return None

    def generate_initial_hashes(self):
        """
        Calculates and saves the initial trusted hashes for critical files.
        This should be run once by an administrator during setup.
        """
        calculated_hashes = {}
        log_event("INTEGRITY", "Generating initial trusted file hashes...")
        for filepath in self.CRITICAL_FILES:
            full_path = filepath # Assuming files are in project root relative to where this runs
            file_hash = self._calculate_file_hash(full_path)
            if file_hash:
                calculated_hashes[filepath] = file_hash
                log_event("INTEGRITY", f"Hash generated for file.", file=filepath, file_hash=file_hash)
            else:
                log_event("INTEGRITY", f"WARNING: Could not hash file. File not found or accessible.", file=filepath)
        self.TRUSTED_FILE_HASHES = calculated_hashes
        self._save_trusted_hashes(calculated_hashes)
        log_event("INTEGRITY", "Initial trusted file hashes generation complete.")

    def check_integrity(self) -> bool:
        """
        Verifies the integrity of critical files against trusted hashes.
        Should be called at application startup.
        """
        if not self.TRUSTED_FILE_HASHES:
            log_event("INTEGRITY", "INTEGRITY CHECK SKIPPED: No trusted file hashes loaded. Run generate_initial_hashes first.")
            print("[CRITICAL SECURITY ALERT] Core integrity check skipped. System may be compromised. Please run SecurityHardener.get_instance().generate_initial_hashes() to initialize.")
            return False

        all_ok = True
        log_event("INTEGRITY", "Performing core file integrity check...")
        for filepath, trusted_hash in self.TRUSTED_FILE_HASHES.items():
            current_hash = self._calculate_file_hash(filepath)
            if current_hash is None:
                log_event("INTEGRITY", f"INTEGRITY FAILED: Critical file is missing or inaccessible.", file=filepath)
                print(f"[CRITICAL SECURITY ALERT] Critical file missing: {filepath}. System may be compromised.")
                all_ok = False
            elif current_hash != trusted_hash:
                log_event("INTEGRITY", f"INTEGRITY FAILED: File hash mismatch.", file=filepath, trusted_hash=trusted_hash, current_hash=current_hash)
                print(f"[CRITICAL SECURITY ALERT] Core file integrity breach detected: {filepath}. System may be compromised.")
                all_ok = False
        
        
        if all_ok:
            log_event("INTEGRITY", "Core file integrity check PASSED.")
            print("[SecurityHardener] Core file integrity check passed.")
        else:
            log_event("INTEGRITY", "System integrity check FAILED. Investigate logs/security.log immediately.", level="CRITICAL")
            print("[CRITICAL SECURITY ALERT] System integrity check FAILED. Investigate logs/security.log immediately.")
        
        return all_ok

# Singleton instance
_hardener_instance: Optional[SecurityHardener] = None

def get_security_hardener() -> SecurityHardener:
    """Provides access to the singleton SecurityHardener instance."""
    global _hardener_instance
    if _hardener_instance is None:
        _hardener_instance = SecurityHardener()
    return _hardener_instance
