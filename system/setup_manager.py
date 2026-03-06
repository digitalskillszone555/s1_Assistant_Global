# system/setup_manager.py
from system.config_loader import load_config, save_config, validate_config
from memory.memory_manager import get_memory_manager
from system.ai_mode_manager import get_ai_mode_manager

def is_setup_needed():
    """
    Checks if the initial setup is required by validating the config file.
    """
    config = load_config()
    if not config or not validate_config(config):
        return True
    return False

def run_setup():
    """
    Runs the interactive first-time setup process for the user.
    """
    print("="*30)
    print("S1 Assistant - First-Time Setup")
    print("="*30)
    print("Please configure your preferences.")

    # --- Collect User Preferences ---
    language = _get_user_choice("Choose your language", ["en", "bn", "hi"])
    ai_mode = _get_user_choice("Choose AI Mode", ["smart", "online", "offline"])
    voice_enabled_str = _get_user_choice("Enable voice interaction? (requires microphone)", ["true", "false"])
    voice_enabled = voice_enabled_str == "true"
    api_key = input("Enter your Gemini API Key (optional, press Enter to skip): ").strip()

    # --- Prepare Config Data ---
    config_data = {
        "language": language,
        "ai_mode": ai_mode,
        "voice_enabled": voice_enabled,
        "api_key": api_key
    }

    # --- Save to user_config.json ---
    if save_config(config_data):
        print("\nConfiguration saved successfully!")
    else:
        print("\nError: Could not save configuration file.")
        return # Exit if we can't save

    # --- Apply settings to relevant systems ---
    # This ensures other modules don't need to be rewritten immediately
    print("Applying initial settings...")
    try:
        # 1. Save language to user's profile memory
        memory_manager = get_memory_manager()
        memory_manager.save_memory("profile", "language", language)
        print("- Language preference applied.")

        # 2. Set the AI mode
        ai_mode_manager = get_ai_mode_manager()
        ai_mode_manager.set_ai_mode(ai_mode)
        print("- AI mode set.")
        
        # NOTE: voice_enabled will be checked in main.py before starting voice services.
        # NOTE: The API key will be loaded where needed, e.g., in the online_ai_engine.

    except Exception as e:
        print(f"An error occurred while applying settings: {e}")

    print("="*30)
    print("Setup complete. The assistant will now start.")
    print("="*30)


def _get_user_choice(prompt: str, options: list):
    """
    Prompts the user to select from a list of options and validates the input.
    """
    print(f"\n{prompt}")
    options_str = " / ".join(options)
    while True:
        choice = input(f"({options_str}): ").lower().strip()
        if choice in options:
            return choice
        print(f"Invalid selection. Please choose one of: {options_str}")

def perform_setup_if_needed():
    """
    Main function to be called from main.py. Checks if setup is needed
    and runs it.
    """
    if is_setup_needed():
        run_setup()
