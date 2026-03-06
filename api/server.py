# api/server.py

import uvicorn
import threading
import asyncio # New import for managing server loop
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from interface_layer.ui_controller import get_ui_controller
from utils.logging_utils import log_event # Centralized logging

# --- Pydantic Models for Request Bodies ---
class CommandRequest(BaseModel):
    text: str

class ModeRequest(BaseModel):
    mode: str

class UserRequest(BaseModel):
    username: str

class LanguageRequest(BaseModel):
    language: str

# --- FastAPI Application ---
app = FastAPI()
ui_controller = get_ui_controller()

@app.post("/command")
async def send_command(request: CommandRequest):
    """Receives a text command and sends it to the S1 core."""
    reply, exit_flag = ui_controller.send_command(request.text)
    # In an API context, we don't exit, we just report the intent
    return {"status": "ok", "reply": reply, "exit_intent": exit_flag}

@app.get("/reply")
async def get_last_reply():
    """Gets the last spoken reply from the S1 core."""
    reply = ui_controller.get_last_reply()
    return {"reply": reply}

@app.post("/listen")
async def start_listening():
    """Triggers the S1 core to start listening for a voice command."""
    success = ui_controller.start_listening()
    return {"status": "listening" if success else "failed"}

@app.post("/stop")
async def stop_listening():
    """Tells the S1 core to stop the current session and go idle."""
    success = ui_controller.stop_listening()
    return {"status": "stopped" if success else "failed"}

@app.post("/mode")
async def change_mode(request: ModeRequest):
    """Changes the assistant's behavior mode."""
    reply = ui_controller.change_mode(request.mode)
    return {"status": "ok", "message": reply}

@app.post("/user")
async def switch_user(request: UserRequest):
    """Switches the active user profile."""
    reply = ui_controller.switch_user(request.username)
    return {"status": "ok", "message": reply}

@app.post("/language")
async def set_language(request: LanguageRequest):
    """Sets the user's preferred language."""
    reply = ui_controller.set_language(request.language)
    return {"status": "ok", "message": reply}

# --- Server Runner ---
def run_api_server(host: str, port: int, shutdown_event: threading.Event):
    """Function to run the Uvicorn server, listening for a shutdown event."""
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    
    # Run server in a separate asyncio task
    server_task = asyncio.ensure_future(server.serve())
    log_event("API_SERVER", f"API server starting on http://{host}:{port}")

    # Monitor shutdown event
    while not shutdown_event.is_set():
        shutdown_event.wait(0.5) # Check every 0.5 seconds

    log_event("API_SERVER", "Shutdown event received. Stopping API server gracefully.")
    server.should_exit = True # Signal uvicorn to exit
    asyncio.get_event_loop().call_soon_threadsafe(server.force_exit) # Force exit if it doesn't
    server_task.cancel() # Cancel the task
    log_event("API_SERVER", "API server stopped.")


def run_in_thread(host="127.0.0.1", port=8000, shutdown_event: threading.Event = None):
    """Runs the API server in a separate daemon thread."""
    if shutdown_event is None:
        log_event("API_SERVER", "run_in_thread called without shutdown_event. API server will not shut down gracefully.", level="WARNING")
        
    server_thread = threading.Thread(
        target=lambda: asyncio.run(run_api_server(host, port, shutdown_event)), 
        daemon=True
    )
    server_thread.start()
    log_event("API_SERVER", "API server thread started.")
    return server_thread
