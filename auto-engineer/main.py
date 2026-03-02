import os
import json
import yaml
import random
import logging
import argparse
from github import Github
from engine.analyzer import RepositoryAnalyzer
from engine.behavior import BehaviorController
from engine.planner import ActionPlanner
from engine.executor import RepositoryExecutor
from engine.reporter import Reporter

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    with open('config/repos.json', 'r') as f:
        repos = json.load(f)
    with open('config/rules.yaml', 'r') as f:
        rules = yaml.safe_load(f)
    return repos, rules

def run(disable_delay=False, multi_repo=False):
    token = os.getenv("GH_TOKEN")
    if not token:
        logging.error("GH_TOKEN is missing! Please expose it as an environment variable.")
        return
        
    repos_list, rules = load_config()
    
    behavior = BehaviorController(rules.get('behavior', {}))
    reporter = Reporter('memory/history.json')
    
    # Apply random delay only in non-CI environments
    behavior.apply_random_delay(disable_delay)
    
    # Authentication
    g = Github(token)
    
    # Analyze Repositories
    analyzed_states = []
    repo_objs = {}
    
    for repo_name in repos_list:
        logging.info(f"Analyzing {repo_name}...")
        try:
            repo = g.get_repo(repo_name)
            repo_objs[repo_name] = repo
            analyzer = RepositoryAnalyzer(repo)
            state = analyzer.analyze()
            analyzed_states.append(state)
        except Exception as e:
            logging.error(f"Failed to analyze {repo_name}: {e}")
            
    # Plan Actions
    planner = ActionPlanner(behavior, reporter, rules.get('weights', {}))
    prioritized = planner.prioritize_repos(analyzed_states)
    
    if not prioritized:
        logging.info("No repositories require actions (cooldown active or empty list).")
        # Even if cooldown blocks everything, force at least ONE action on a random repo
        if analyzed_states:
            logging.info("Forcing action on a random repository to ensure activity...")
            random_state = random.choice(analyzed_states)
            prioritized = [random_state['name']]
        else:
            return

    # Determine how many repos to process this run
    if multi_repo:
        # Process 2-4 repos per run for natural-looking varied activity
        max_repos = min(random.randint(2, 4), len(prioritized))
    else:
        max_repos = 1

    targets = prioritized[:max_repos]
    actions_taken = 0
    
    for target_repo_name in targets:
        target_state = next((s for s in analyzed_states if s['name'] == target_repo_name), None)
        if not target_state:
            continue
            
        action_to_take = planner.select_action(target_state)
        
        logging.info(f"Selected repository: {target_repo_name} for action: {action_to_take}")
        
        try:
            executor = RepositoryExecutor(repo_objs[target_repo_name], behavior)
            executor.execute_action(action_to_take)
            logging.info(f"Action {action_to_take} executed successfully on {target_repo_name}")
            
            reporter.record_action(target_repo_name, action_to_take)
            actions_taken += 1
        except Exception as e:
            logging.error(f"Failed to execute action on {target_repo_name}: {e}")

    logging.info(f"Run complete. Actions taken: {actions_taken}/{len(targets)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-delay", action="store_true", help="Disable random delays for CI/testing.")
    parser.add_argument("--multi", action="store_true", help="Process multiple repos per run.")
    args = parser.parse_args()
    
    run(disable_delay=args.no_delay, multi_repo=args.multi)
