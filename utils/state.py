# =========================
# S1 STATE MANAGER
# =========================

from enum import Enum
import time
from system.state_guard import get_state_guard

class AssistantState(Enum):
    """
    Defines the possible states of the assistant.
    """
    IDLE = 1         # Waiting for wake word
    LISTENING = 2    # Actively listening for a command
    THINKING = 3     # Processing a command
    SPEAKING = 4     # Generating a voice response
    WAITING = 5      # Paused after speaking, before listening again

class StateManager:
    def __init__(self):
        self.current_state = AssistantState.IDLE
        self.last_state_change = time.time()
        self.state_guard = get_state_guard()

    def set_state(self, state: AssistantState):
        if self.current_state == state:
            return # No change, do nothing.

        # Consult the StateGuard before proceeding
        if self.state_guard.is_safe_transition(self.current_state, state):
            old_state = self.current_state
            self.current_state = state
            self.last_state_change = time.time()
            self.state_guard.record_transition(old_state, self.current_state)
            print(f"[STATE] Changing from {old_state.name} to {self.current_state.name}")
        else:
            # If the transition is deemed unsafe, block it and fallback to IDLE
            print(f"[STATE_GUARD] Unsafe transition from {self.current_state.name} to {state.name} blocked.")
            print("[STATE_GUARD] Forcing state to IDLE as a fallback.")
            if self.current_state != AssistantState.IDLE:
                self.set_state(AssistantState.IDLE) # Recursive call, should be safe

    def get_state(self) -> AssistantState:
        return self.current_state

    def is_state(self, state: AssistantState) -> bool:
        return self.current_state == state

# Global state manager instance
S1_STATE = StateManager()

def get_state_manager():
    return S1_STATE
