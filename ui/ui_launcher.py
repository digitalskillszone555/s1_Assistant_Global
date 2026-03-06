# ui/ui_launcher.py
import threading
from interface_layer.device_detector import detect_device_type
from ui.mobile.mobile_app import launch_mobile_ui # New import
from ui.web.web_app import launch_web_ui       # New import

def get_platform():
    """Detects the current platform (e.g., 'desktop')."""
    return detect_device_type()

def launch_desktop_ui():
    """
    Launches the main desktop window.
    This function was moved from main.py during refactoring.
    """
    try:
        from ui.desktop_app import S1DesktopApp
        print("[UI Launcher] Launching Desktop UI...")
        app = S1DesktopApp()
        app.mainloop() # This is a blocking call
    except ImportError as e:
        print(f"[UI Launcher ERROR] UI launch failed. Is 'customtkinter' installed? Error: {e}")
    except Exception as e:
        print(f"[UI Launcher ERROR] An unexpected error occurred: {e}")

def launch_tray_mode(ui_launcher_func):
    """
    Launches the system tray icon in a separate thread.
    This function was moved from main.py during refactoring.
    """
    try:
        from ui.tray_manager import TrayManager
        print("[UI Launcher] Initiating System Tray icon...")
        tray_manager = TrayManager(ui_launcher=ui_launcher_func)
        tray_manager.run_in_thread()
    except Exception as e:
        print(f"[UI Launcher TRAY ERROR] {e}")

def launch_interface(ui_type: str):
    """
    Acts as a UI router, launching the appropriate interface based on the
    startup arguments and platform detection.
    
    :param ui_type: The type of UI to launch ('desktop', 'tray', or 'auto').
    """
    platform = get_platform()
    print(f"[UI Launcher] Detected platform: {platform}. Requested UI: {ui_type}")

    if platform == "desktop":
        if ui_type == 'desktop':
            launch_desktop_ui()
        elif ui_type == 'tray':
            launch_tray_mode(ui_launcher_func=launch_desktop_ui)
    
    elif platform == "mobile":
        # Launch placeholder mobile UI
        launch_mobile_ui()

    elif platform == "web":
        # Launch placeholder web UI
        launch_web_ui()
        
    else:
        print(f"[UI Launcher] No UI implementation available for platform: {platform}")
