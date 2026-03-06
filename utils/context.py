# =========================
# S1 CONTEXT MEMORY
# =========================

class Context:
    def __init__(self):
        self.last_opened_app = None
        self.last_command = None
        self.last_reply = None
        self.last_action = None

    def update(self, command=None, reply=None, app=None, action=None):
        if command:
            self.last_command = command
        if reply:
            self.last_reply = reply
        if app:
            self.last_opened_app = app
        if action:
            self.last_action = action
    
    def get_last_app(self):
        return self.last_opened_app

# Global context object
S1_CONTEXT = Context()

def get_context():
    return S1_CONTEXT
