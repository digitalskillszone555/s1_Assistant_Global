# speech/offline_stt.py

import os
import json
from vosk import Model, KaldiRecognizer

class OfflineSTT:
    def __init__(self, model_base_path="speech/models"):
        self.model_base_path = model_base_path
        self.models = {}
        self.is_ready = False
        self._load_models()

    def _load_models(self):
        """
        Loads the Vosk models for supported languages if they exist.
        
        IMPORTANT: You must download the Vosk models and place them in the
        'speech/models' directory. For example:
        - speech/models/vosk-model-small-en-us-0.15 -> for English
        - speech/models/vosk-model-small-bn-0.22 -> for Bengali
        - speech/models/vosk-model-small-hi-0.22 -> for Hindi
        
        Download links: https://alphacephei.com/vosk/models
        """
        supported_languages = {
            "en": "vosk-model-small-en-us-0.15",
            "bn": "vosk-model-small-bn-0.22",
            "hi": "vosk-model-small-hi-0.22"
        }
        
        print("[OfflineSTT] Checking for local speech recognition models...")
        for lang_code, model_name in supported_languages.items():
            model_path = os.path.join(self.model_base_path, model_name)
            if os.path.exists(model_path):
                try:
                    self.models[lang_code] = Model(model_path)
                    print(f"[OfflineSTT] Successfully loaded '{lang_code}' model: {model_name}")
                    self.is_ready = True
                except Exception as e:
                    print(f"[OfflineSTT ERROR] Failed to load model from '{model_path}': {e}")
            else:
                print(f"[OfflineSTT WARN] Model for '{lang_code}' not found at '{model_path}'")
        
        if not self.is_ready:
            print("[OfflineSTT WARN] No offline models loaded. Offline STT is disabled.")

    def recognize_speech(self, audio_data, language_code: str):
        """
        Performs offline speech recognition using the loaded Vosk model.
        """
        if not self.is_ready or language_code not in self.models:
            return None

        model = self.models[language_code]
        recognizer = KaldiRecognizer(model, audio_data.sample_rate)
        
        # The VOSK recognizer processes audio in chunks
        # The recognizer.AcceptWaveform() method is for complete audio data
        if recognizer.AcceptWaveform(audio_data.get_raw_data()):
            result_json = recognizer.Result()
            result_dict = json.loads(result_json)
            return result_dict.get("text")
        else:
            # For partial results, which can be useful in streaming scenarios
            partial_result_json = recognizer.PartialResult()
            # For this implementation, we only care about the final, complete result.
            return None

# Global instance
S1_OFFLINE_STT = OfflineSTT()

def get_offline_stt():
    return S1_OFFLINE_STT
