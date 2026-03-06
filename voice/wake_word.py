# =========================
# S1 WAKE WORD LISTENER
# Phase 2: Stable Engine (FINAL)
# =========================

import speech_recognition as sr
import time
from utils.state import get_state_manager, AssistantState

class WakeWordListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()

        # Tuned thresholds for Indian mic environments
        self.recognizer.energy_threshold = 280
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.6
        self.recognizer.phrase_threshold = 0.3

        self.microphone = None
        self.state_manager = get_state_manager()

        # Multilingual Wake Words
        self.wake_words = [
            "s1", "hey s1", "oi s1", "hello s1",
            "assistant", "hey assistant",
            "হেই এস ওয়ান", "এই এস ওয়ান", "ওই এস ওয়ান"
        ]

        self.last_detection_time = 0
        self.cooldown = 2.5  # seconds

        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
            print("[WAKE] Wake word engine ready.")
        except OSError:
            print("[WAKE] No microphone found. Using text-only mode.")
        except Exception as e:
            print(f"[WAKE ERROR] {e}")

    def listen_for_wake_word(self):
        # Only detect wake word when system is idle
        if not self.state_manager.is_state(AssistantState.IDLE):
            return False

        # Text mode fallback
        if not self.microphone:
            self.state_manager.set_state(AssistantState.LISTENING)
            return True

        # Cooldown protection
        if time.time() - self.last_detection_time < self.cooldown:
            return False

        with self.microphone as source:
            print("[WAKE] Waiting for wake word...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=None,
                    phrase_time_limit=3
                )

                text = self.recognizer.recognize_google(audio, language="en-IN").lower()
                print(f"[WAKE HEARD] {text}")

                # Reject long phrases (not wake words)
                if len(text.split()) > 4:
                    return False

                # Wake word match
                if any(w in text for w in self.wake_words):
                    print(f"[WAKE DETECTED] '{text}'")
                    self.last_detection_time = time.time()
                    self.state_manager.set_state(AssistantState.LISTENING)
                    return True

            except sr.UnknownValueError:
                pass
            except sr.WaitTimeoutError:
                pass
            except sr.RequestError as e:
                print(f"[WAKE ERROR] Google STT error: {e}")
            except Exception as e:
                print(f"[WAKE ERROR] Unexpected: {e}")

        return False