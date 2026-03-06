import requests
import threading

STUDIO_URL = "http://localhost:8000/api/assistant/event"
TIMEOUT = 0.5

def send_event(event_type: str, message: str):
    """
    Sends an event to the S1 Studio backend in a non-blocking way.
    """
    payload = {
        "type": event_type,
        "message": message
    }

    def task():
        try:
            requests.post(STUDIO_URL, json=payload, timeout=TIMEOUT)
        except requests.exceptions.RequestException:
            # Fail silently
            pass

    thread = threading.Thread(target=task)
    thread.start()
