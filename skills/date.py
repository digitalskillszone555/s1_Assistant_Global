# skills/date.py
import datetime

def run():
    """Returns the current date."""
    return f"Today's date is {datetime.datetime.now().strftime('%d %B, %Y')}."
