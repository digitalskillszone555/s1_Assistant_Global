# ai/ai_router.py

import socket
from ai.ai_engine import get_ai_engine
from user.user_manager import get_user_manager
from system.ai_mode_manager import get_ai_mode_manager

def _is_internet_available():
    """Checks for a live internet connection."""
    try:
        # Connect to a reliable server (Google's DNS) to check for internet
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

from core.online_command_router import is_online_command # New import

def _is_internet_available():
    """Checks for a live internet connection."""
    try:
        # Connect to a reliable server (Google's DNS) to check for internet
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def get_ai_response(prompt: str):
    """
    Routes a prompt to an AI engine based on the user-configured AI mode
    and the new online command router.
    - online: Forces usage of the online AI (Gemini).
    - offline: Forces usage of the offline AI (Ollama).
    - smart: Automatically chooses the best engine based on connectivity and command type.
    """
    ai_mode_manager = get_ai_mode_manager()
    ai_mode = ai_mode_manager.get_ai_mode()

    ai_engine = get_ai_engine()
    user_manager = get_user_manager()
    user_info = user_manager.get_current_user_info()

    # --- Mode-Based Routing ---
    
    # 1. Online-Only Mode
    if ai_mode == "online":
        print("[AI Router] Mode is 'online'. Forcing online AI.")
        return ai_engine.generate_online_response(prompt, user_info)

    # 2. Offline-Only Mode
    elif ai_mode == "offline":
        print("[AI Router] Mode is 'offline'. Forcing offline AI.")
        return ai_engine.generate_offline_response(prompt)

    # 3. Smart Mode (Default Hybrid Logic with new Online Command Router)
    elif ai_mode == "smart":
        print("[AI Router] Mode is 'smart'. Using hybrid routing.")
        has_internet = _is_internet_available()

        if has_internet:
            # If the command is explicitly an online command, send it directly to the online engine.
            if is_online_command(prompt):
                print("[AI Router] Smart: Command identified as online-only. Routing to online AI.")
                return ai_engine.generate_online_response(prompt, user_info)
            
            # Otherwise, maintain the offline-first approach.
            else:
                print("[AI Router] Smart: Command is offline-capable. Trying offline AI first.")
                offline_response = ai_engine.generate_offline_response(prompt)
                if offline_response:
                    return offline_response
                
                # Fallback for general queries if offline fails.
                print("[AI Router] Smart: Offline AI failed or returned no response. Falling back to online AI.")
                return ai_engine.generate_online_response(prompt, user_info)
        
        # Offline-only if no internet is available.
        else:
            print("[AI Router] Smart: No internet connection. Using offline AI only.")
            return ai_engine.generate_offline_response(prompt)

    return None # Should not be reached, but as a safeguard