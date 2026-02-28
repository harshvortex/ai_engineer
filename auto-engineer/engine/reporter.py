import json
import os
from datetime import datetime

class Reporter:
    def __init__(self, history_file: str):
        self.history_file = history_file
        self.history = self.load_history()

    def load_history(self) -> dict:
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                try:
                    return json.load(f)
                except Exception:
                    return {}
        return {}

    def save_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def record_action(self, repo_name: str, action: str):
        if repo_name not in self.history:
            self.history[repo_name] = []
        
        self.history[repo_name].append({
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.save_history()

    def get_last_action_time(self, repo_name: str):
        if repo_name in self.history and self.history[repo_name]:
            latest = self.history[repo_name][-1]["timestamp"]
            return datetime.fromisoformat(latest)
        return None
