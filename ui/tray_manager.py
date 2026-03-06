# ui/tray_manager.py

import os
import threading
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
from interface_layer.ui_controller import get_ui_controller

class TrayManager:
    def __init__(self, ui_launcher=None):
        self.ui_controller = get_ui_controller()
        self.ui_launcher = ui_launcher # Function to launch the UI
        self.icon = None
        self.icon_thread = None

    def _create_icon_image(self):
        """Creates a simple 64x64 icon programmatically."""
        width = 64
        height = 64
        # A simple blue circle with "S1" in the middle
        image = Image.new('RGB', (width, height), color = 'black')
        draw = ImageDraw.Draw(image)
        draw.ellipse((2, 2, width-3, height-3), fill = '#1E90FF')
        # A simple font is fine, no need for specific .ttf files
        draw.text((16, 18), "S1", fill='white')
        return image

    def _build_menu(self):
        """Dynamically builds the context menu for the tray icon."""
        
        # --- Dynamic Submenus ---
        try:
            modes = self.ui_controller.mode_manager.list_modes()
            mode_submenu = Menu(*[
                MenuItem(
                    mode.capitalize(), 
                    lambda m=mode: self.ui_controller.change_mode(m),
                ) for mode in modes
            ])
        except Exception:
            modes = []
            mode_submenu = Menu(MenuItem("Error loading modes", None, enabled=False))

        try:
            users = self.ui_controller.user_manager.list_users()
            user_submenu = Menu(*[
                MenuItem(
                    user.capitalize(),
                    lambda u=user: self.on_switch_user(u),
                ) for user in users
            ])
        except Exception:
            users = []
            user_submenu = Menu(MenuItem("Error loading users", None, enabled=False))


        # --- Main Menu Structure ---
        return Menu(
            MenuItem('Open UI', self.on_open_ui, enabled=self.ui_launcher is not None),
            Menu.SEPARATOR,
            MenuItem('Start Listening', self.ui_controller.start_listening),
            MenuItem('Stop Listening', self.ui_controller.stop_listening),
            Menu.SEPARATOR,
            MenuItem('Change Mode', mode_submenu),
            MenuItem('Switch User', user_submenu),
            Menu.SEPARATOR,
            MenuItem('Exit Assistant', self.on_exit)
        )

    def on_open_ui(self):
        if self.ui_launcher:
            # To prevent creating multiple UI windows, this should ideally
            # check if a window is already open. For now, it just calls the launcher.
            print("[Tray] Requesting to open UI...")
            self.ui_launcher()

    def on_switch_user(self, user):
        print(f"[Tray] Switching to user: {user}")
        self.ui_controller.switch_user(user)
        # We need to refresh the menu to reflect the new state,
        # which pystray supports by reassigning the menu property.
        self.icon.menu = self._build_menu()

    def on_exit(self):
        print("[Tray] Exit requested. Shutting down...")
        self.icon.stop()
        # A hard exit is needed to ensure all daemon threads are killed
        os._exit(0)

    def run(self):
        """Runs the tray icon in the current thread (blocking)."""
        print("[Tray] Initializing System Tray Icon...")
        self.icon = Icon(
            'S1-Assistant',
            icon=self._create_icon_image(),
            title='S1 Assistant',
            menu=self._build_menu()
        )
        self.icon.run()
        
    def run_in_thread(self):
        """Launches the tray icon in a separate daemon thread."""
        if self.icon_thread and self.icon_thread.is_alive():
            print("[Tray] Tray icon is already running.")
            return
        
        # The thread must not be a daemon if we want KeyboardInterrupt to work in headless
        self.icon_thread = threading.Thread(target=self.run)
        self.icon_thread.daemon = True
        self.icon_thread.start()
