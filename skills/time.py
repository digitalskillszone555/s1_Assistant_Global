# skills/time.py
import datetime

def run():
    """Returns the current time."""
    return f"The time is {datetime.datetime.now().strftime('%I:%M %p')}."
