# memory/memory_engine.py

from memory.memory_manager import get_memory_manager

class MemoryEngine:
    def __init__(self):
        self.memory_manager = get_memory_manager()

    def analyze_and_memorize(self, text: str, intent_data: dict):
        """
        Analyzes an interaction to see if anything is worth remembering automatically.
        This is a placeholder for a more advanced future implementation.
        """
        # For now, we only perform explicit memorization via commands.
        # A future version could detect patterns like "my favorite color is blue"
        # and automatically save that as a preference.
        print(f"[MemEngine] Analyzing text for passive memorization: '{text}' (Not implemented yet)")
        pass

    def save_explicit_fact(self, fact_to_remember: str):
        """Saves a fact explicitly told by the user."""
        if not fact_to_remember:
            return False, "There was nothing to remember."
        
        # Use a portion of the fact as the key
        key = " ".join(fact_to_remember.split()[:4])
        self.memory_manager.save_memory("facts", key, fact_to_remember)
        return True, "Okay, I'll remember that."

    def get_memory_summary(self):
        """Retrieves and summarizes all known facts and profile info for the user."""
        profile_mem = self.memory_manager._load_memory("profile") or {}
        facts_mem = self.memory_manager.list_memory("facts") or []
        
        summary = []
        # Get profile info like name
        user_name = profile_mem.get("user_name", {}).get("value")
        if user_name:
            summary.append(f"Your name is {user_name}.")
            
        if facts_mem:
            summary.append("I also remember these facts:")
            summary.extend(facts_mem)
            
        return " ".join(summary) if summary else "I don't remember anything about you yet."

    def forget_last_fact(self):
        """Forgets the most recently added fact."""
        all_facts = self.memory_manager._load_memory("facts")
        if not all_facts:
            return False, "There are no facts to forget."
            
        # Find the key of the memory item with the latest timestamp
        last_item_key = max(all_facts, key=lambda k: all_facts[k].get('timestamp', 0))
        
        if last_item_key:
            self.memory_manager.delete_memory("facts", last_item_key)
            return True, "Okay, I have forgotten the last fact."
        
        return False, "I couldn't find the last fact to forget."

    def clear_all_memory(self, memory_type='facts'):
        """Deletes all memories of a specific type for the current user."""
        # A bit dangerous, so we'll scope it to 'facts' by default for safety
        username = self.memory_manager.user_manager.current_user
        empty_data = {}
        
        if memory_type == 'all':
            for mem_type in self.memory_manager.memory_types:
                self.memory_manager._save_memory(mem_type, empty_data)
            return True, f"I have cleared all memories for {username}."
        
        elif memory_type in self.memory_manager.memory_types:
            self.memory_manager._save_memory(memory_type, empty_data)
            return True, f"I have cleared all {memory_type}."
            
        return False, "Invalid memory type."

# Global instance
S1_MEMORY_ENGINE = MemoryEngine()

def get_memory_engine():
    return S1_MEMORY_ENGINE
