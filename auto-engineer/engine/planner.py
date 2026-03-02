import random
from engine.reporter import Reporter
from engine.behavior import BehaviorController
from datetime import datetime

class ActionPlanner:
    def __init__(self, behavior: BehaviorController, reporter: Reporter, weights: dict):
        self.behavior = behavior
        self.reporter = reporter
        self.weights = weights

    def prioritize_repos(self, analyzed_repos: list) -> list:
        """Score repos based on inactivity and lack of recent actions."""
        scored_repos = []
        for state in analyzed_repos:
            repo_name = state['name']
            
            # Check cooldown
            last_action = self.reporter.get_last_action_time(repo_name)
            if last_action:
                delta = datetime.utcnow() - last_action
                if delta.total_seconds() < self.behavior.cooldown_hours * 3600:
                    continue  # Skip, recently updated
            
            # Weighted score: higher inactivity = higher priority
            inactivity = state['inactivity_days']
            readme_score = state['readme_quality']  # 0 is poor, 2 is good
            
            score = (inactivity * self.weights.get("inactivity", 0.5)) + \
                    ((2 - readme_score) * 20 * self.weights.get("readme_quality", 0.2))
            
            # Add slight randomness to avoid always picking same repo
            score += random.uniform(0, 10)
                    
            scored_repos.append({"name": repo_name, "score": score, "state": state})
            
        scored_repos.sort(key=lambda x: x['score'], reverse=True)
        return [r['name'] for r in scored_repos]

    def select_action(self, repo_state: dict) -> str:
        """Determine the best action for the selected repository with more variety."""
        # Check what the last action was for this repo to avoid repetition
        last_actions = self._get_recent_actions(repo_state['name'])
        
        possible_actions = []
        
        if repo_state['inactivity_days'] > 30:
            possible_actions.append("maintenance_log")
        
        if repo_state['readme_quality'] < 2:
            possible_actions.append("update_readme")
        
        possible_actions.append("update_changelog")
        possible_actions.append("update_contributing")
        possible_actions.append("update_gitignore_notes")
        
        # Remove the last used action to ensure variety
        if last_actions and len(possible_actions) > 1:
            last = last_actions[-1]
            possible_actions = [a for a in possible_actions if a != last] or possible_actions
        
        return random.choice(possible_actions)

    def _get_recent_actions(self, repo_name: str) -> list:
        """Get list of recent action types for a repo."""
        if repo_name in self.reporter.history and self.reporter.history[repo_name]:
            return [entry['action'] for entry in self.reporter.history[repo_name][-3:]]
        return []
