# =========================
# S1 ASSISTANT VOICE OUTPUT
# Phase 2: Stable Engine
# =========================

import pyttsx3
from utils.state import get_state_manager, AssistantState
from analytics.studio_reporter import send_event

class VoiceOutput:
    def __init__(self):
        # Engine is initialized on-demand in speak()
        pass

    def speak(self, text: str):
        """
        Uses pyttsx3 to speak the given text.
        This is a fully blocking call.
        Initializes and shuts down the engine on each call for stability.
        """
        if not text:
            return
            
        state_manager = get_state_manager()
        state_manager.set_state(AssistantState.SPEAKING)
        try:
            send_event("speaking", "Speaking response")
        except Exception:
            pass # Fail silently
        
        try:
            engine = pyttsx3.init()
            engine.say(text)
            print(f"S1: {text}")
            engine.runAndWait()
            
        except Exception as e:
            print(f"[TTS ERROR] {e}")
            try:
                send_event("error", f"TTS error: {e}")
            except Exception:
                pass # Fail silently
        finally:
            # After speaking, transition to a waiting state before listening again
            state_manager.set_state(AssistantState.WAITING)