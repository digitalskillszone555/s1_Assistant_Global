# =========================
# S1 ASSISTANT VOICE INPUT
# Phase 14: Hybrid STT Engine
# =========================

import speech_recognition as sr
from utils.state import get_state_manager, AssistantState
from speech.offline_stt import get_offline_stt
from language.language_manager import get_language_manager
from analytics.studio_reporter import send_event

class VoiceInput:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.microphone = None
        self.state_manager = get_state_manager()
        self.offline_stt = get_offline_stt() # Get the offline engine instance
        self.lang_manager = get_language_manager()

        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                print("Calibrating microphone...")
                self.recognizer.dynamic_energy_threshold = True
            print("Microphone ready.")
        except Exception as e:
            print(f"Microphone not found or error: {e}. Falling back to text input.")
            self.microphone = None

    def listen(self):
        if self.state_manager.is_state(AssistantState.SPEAKING):
            return None # Do not listen while assistant is speaking

        self.state_manager.set_state(AssistantState.LISTENING)
        try:
            send_event("listening", "Assistant started listening")
        except Exception:
            pass # Fail silently

        # --- Fallback to text input if no microphone ---
        if not self.microphone:
            try:
                text = input("You: ")
                self.state_manager.set_state(AssistantState.THINKING)
                return text.lower() if text else None
            except EOFError:
                self.state_manager.set_state(AssistantState.IDLE)
                return None
        
        # --- Voice input logic ---
        with self.microphone as source:
            print("Listening for command...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                self.state_manager.set_state(AssistantState.THINKING)
                
                text = None
                current_lang = self.lang_manager.language_pack.get("code", "en")
                
                # 1. Try Offline STT first
                if self.offline_stt.is_ready:
                    print("[STT] Attempting offline recognition...")
                    text = self.offline_stt.recognize_speech(audio, language_code=current_lang)
                    if text:
                        print(f"[Offline STT] You said: {text}")

                # 2. Fallback to Online STT if offline fails
                if not text:
                    print("[STT] Offline failed, falling back to online recognition...")
                    # The online recognizer needs a BCP-47 tag, e.g., 'en-US', 'bn-IN'
                    lang_tag = f"{current_lang}-IN" 
                    text = self.recognizer.recognize_google(audio, language=lang_tag)
                    print(f"[Online STT] You said: {text}")

                return text.lower() if text else None

            except sr.UnknownValueError:
                print("[STT] Could not understand audio.")
                self.state_manager.set_state(AssistantState.WAITING)
                return None
            except sr.WaitTimeoutError:
                print("[STT] Listening timed out.")
                self.state_manager.set_state(AssistantState.IDLE)
                return None
            except sr.RequestError as e:
                print(f"[STT] Online recognition error; {e}")
                self.state_manager.set_state(AssistantState.IDLE)
                return None
            except Exception as e:
                print(f"[STT] An unexpected error occurred: {e}")
                try:
                    send_event("error", f"STT error: {e}")
                except Exception:
                    pass # Fail silently
                self.state_manager.set_state(AssistantState.IDLE)
                return None