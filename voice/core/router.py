import sys
import os

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.brain import think

def route_command(text):
    reply, exit_flag = think(text)
    return reply, exit_flag