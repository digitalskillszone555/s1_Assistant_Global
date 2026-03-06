# system/state_guard.py

from collections import deque
import time

class StateGuard:
    """
    A system to monitor state transitions and prevent infinite loops
    or rapid, repetitive state changes.
    """
    def __init__(self, history_size=10, loop_threshold=3, time_threshold_ms=500):
        self.history = deque(maxlen=history_size)
        self.loop_threshold = loop_threshold # Num of repetitions to detect a loop
        self.time_threshold_ms = time_threshold_ms # Time window for rapid transitions

    def record_transition(self, old_state, new_state):
        """Records a new state transition along with a timestamp."""
        timestamp = int(time.time() * 1000)
        self.history.append(((old_state, new_state), timestamp))

    def is_safe_transition(self, old_state, new_state):
        """
        Checks if a potential state transition is safe.
        Detects two primary issues:
        1. Rapid flip-flop loops (e.g., A -> B, B -> A, A -> B, ...)
        2. Excessively fast identical transitions.
        """
        if not self.history:
            return True

        # Check for rapid flip-flop loops (e.g., IDLE -> SPEAKING -> IDLE)
        # We look for a pattern like (A, B), (B, A), (A, B)
        if len(self.history) >= 2:
            last_transition, _ = self.history[-1]
            second_last_transition, _ = self.history[-2]
            
            # If the new transition is (A, B), check if history is (B, A), (A, B)
            if second_last_transition == (new_state, old_state) and last_transition == (old_state, new_state):
                print(f"[StateGuard] Loop detected: {second_last_transition} -> {last_transition} -> {(old_state, new_state)}. Blocking.")
                return False

        # Check for too many identical transitions in a short time
        current_time = int(time.time() * 1000)
        recent_matches = 0
        for transition, timestamp in reversed(self.history):
            if (current_time - timestamp) > self.time_threshold_ms:
                break # Stop checking if outside the time window
            if transition == (old_state, new_state):
                recent_matches += 1
        
        if recent_matches >= self.loop_threshold:
            print(f"[StateGuard] Rapid transition detected: {(old_state, new_state)} repeated {recent_matches+1} times. Blocking.")
            return False

        return True

# Singleton instance
_state_guard_instance = None

def get_state_guard():
    """Provides access to the singleton StateGuard instance."""
    global _state_guard_instance
    if _state_guard_instance is None:
        _state_guard_instance = StateGuard()
    return _state_guard_instance
