import os
import json
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(message)s')

class ContextAwareCLIAgent:
    def __init__(self, history_file: str = "cli_memory.json"):
        self.history_file = history_file
        # Maps command to a dictionary of next commands and their frequencies
        self.pattern_db = defaultdict(lambda: defaultdict(int))
        self.last_command = None
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                for k, v in data.items():
                    for next_cmd, count in v.items():
                        self.pattern_db[k][next_cmd] = count
            logging.info("🧠 Loaded existing CLI context memory.")

    def _save_memory(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.pattern_db, f, indent=4)

    def process_command(self, cmd: str):
        cmd = cmd.strip()
        if not cmd:
            return
            
        logging.info(f"\n▶️ Executing: {cmd}")
        
        # Learn pattern
        if self.last_command:
            # Strip unique args for better pattern matching (e.g., commit messages)
            base_last = self.last_command.split(" -m ")[0] if " -m " in self.last_command else self.last_command
            base_cmd = cmd.split(" -m ")[0] if " -m " in cmd else cmd
            self.pattern_db[base_last][base_cmd] += 1
            self._save_memory()
            
        self.last_command = cmd
        base_current = cmd.split(" -m ")[0] if " -m " in cmd else cmd
        
        # Predict next
        suggestions = self.pattern_db.get(base_current, {})
        if suggestions:
            # Get highest frequency next command
            best_guess = max(suggestions.items(), key=lambda x: x[1])[0]
            confidence = suggestions[best_guess]
            logging.info(f"💡 Suggestion: Based on your habits, you might want to run -> `{best_guess}` (Seen {confidence} times)")
        else:
            logging.info("💡 Suggestion: No patterns learned for this command yet.")

if __name__ == "__main__":
    agent = ContextAwareCLIAgent()
    
    # Simulating a user session
    session = [
        "git add .",
        "git commit -m 'update'",
        "git push origin main",
        "npm start",
        "git add .",
        "git commit -m 'fix bug'",
        "git push origin main",
        "ls -la",
        "git add ."
    ]
    
    print("--- Simulating CLI Agent ---")
    for command in session:
        agent.process_command(command)
