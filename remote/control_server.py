# remote/control_server.py
import http.server
import socketserver
import threading
import secrets
from remote.control_api import ControlAPIHandler
from system.config_loader import load_config, save_config
from utils.logging_utils import log_event # Centralized logging

PORT = 8080

def _get_auth_token():
    """
    Loads the remote control auth token from config, generates one if not present.
    """
    config = load_config() or {}
    token = config.get("remote_control_token")
    
    if not token:
        log_event("REMOTE_SERVER", "Remote control token not found. Generating a new one.")
        token = secrets.token_hex(32)
        config["remote_control_token"] = token
        save_config(config)
        log_event("REMOTE_SERVER", "New token generated and saved.", file="config/user_config.json")
        log_event("REMOTE_SERVER", "IMPORTANT: Use this token for API authentication in the 'Authorization' header.", level="WARNING")
    
    return token

def handler_factory(token):
    """
    Factory to create a handler class with the auth token.
    This avoids using global variables.
    """
    class AuthControlAPIHandler(ControlAPIHandler):
        def __init__(self, *args, **kwargs):
            self.auth_token = token
            super().__init__(*args, **kwargs)
    return AuthControlAPIHandler

def start_server(shutdown_event: threading.Event):
    """
    Loads the auth token and starts the remote control HTTP server,
    listening for a shutdown event.
    """
    try:
        auth_token = _get_auth_token()
        handler = handler_factory(auth_token)
        
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            httpd.timeout = 0.5 # Check for shutdown_event every 0.5 seconds
            log_event("REMOTE_SERVER", f"Secure server starting on http://localhost:{PORT}")
            log_event("REMOTE_SERVER", "All requests must include a 'Authorization: Bearer <token>' header.", level="WARNING")
            
            # Loop until shutdown event is set
            while not shutdown_event.is_set():
                httpd.handle_request() # Handle one request or timeout

            log_event("REMOTE_SERVER", "Shutdown event received. Stopping API server gracefully.")
            httpd.shutdown() # Gracefully shut down the server
            log_event("REMOTE_SERVER", "API server stopped.")

    except Exception as e:
        log_event("REMOTE_SERVER", f"Failed to start: {e}", level="ERROR")

def run_in_background(shutdown_event: threading.Event = None):
    """Runs the API server in a separate daemon thread."""
    if shutdown_event is None:
        log_event("REMOTE_SERVER", "run_in_background called without shutdown_event. Server will not shut down gracefully.", level="WARNING")
        
    server_thread = threading.Thread(
        target=start_server, 
        args=(shutdown_event,), 
        daemon=True
    )
    server_thread.start()
    log_event("REMOTE_SERVER", "Remote control server thread started.")
    return server_thread

