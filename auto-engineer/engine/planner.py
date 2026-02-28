from engine.analyzer import RepositoryAnalyzer
from engine.reporter import Reporter
from engine.behavior import BehaviorController
from datetime import datetime

class ActionPlanner:
    def __init__(self, behavior: BehaviorController, reporter: Reporter, weights: dict):
        self.behavior = behavior
        self.reporter = reporter
        self.weights = weights

    def prioritize_repos(self, analyzed_repos: list) -> list:
        # Score repos based on inactivity and lack of recent actions
        scored_repos = []
        for state in analyzed_repos:
            repo_name = state['name']
            
            # Check cooldown
            last_action = self.reporter.get_last_action_time(repo_name)
            if last_action:
                delta = datetime.utcnow() - last_action
                if delta.total_seconds() < self.behavior.cooldown_hours * 3600:
                    continue # Skip, recently updated
            
            # Weighted score: higher inactivity = higher priority
            inactivity = state['inactivity_days']
            readme_score = state['readme_quality'] # 0 is poor, 2 is good
            
            score = (inactivity * self.weights.get("inactivity", 0.5)) + \
                    ((2 - readme_score) * 20 * self.weights.get("readme_quality", 0.2))
                    
            scored_repos.append({"name": repo_name, "score": score, "state": state})
            
        scored_repos.sort(key=lambda x: x['score'], reverse=True)
        return [r['name'] for r in scored_repos]

    def select_action(self, repo_state: dict) -> str:
        # Determine the best action for the selected repository
        if repo_state['inactivity_days'] > 30:
            return "maintenance_log"
        elif repo_state['readme_quality'] == 0:
            return "update_readme"
        else:
            return "update_changelog"
