import random
import time
import logging

class BehaviorController:
    def __init__(self, config: dict):
        self.config = config
        self.min_delay = self.config.get('min_delay_minutes', 1)
        self.max_delay = self.config.get('max_delay_minutes', 10)
        self.skip_prob = self.config.get('skip_probability', 0.0)
        self.cooldown_hours = self.config.get('commit_cooldown_hours', 4)

    def should_skip_today(self) -> bool:
        """Introduce randomness by occasionally skipping execution."""
        skip = random.random() < self.skip_prob
        if skip:
            logging.info("Behavior: Randomly decided to skip execution today.")
        return skip

    def apply_random_delay(self, disable_delay: bool = False):
        """Random delay to simulate human timing. Disabled in CI."""
        if disable_delay:
            return
            
        delay_minutes = random.randint(self.min_delay, self.max_delay)
        delay_seconds = delay_minutes * 60
        logging.info(f"Behavior: Sleeping for {delay_minutes} minutes to simulate human timing.")
        time.sleep(delay_seconds)

    def generate_commit_message(self, action_type: str) -> str:
        """Randomized human-like commit messages with more variety."""
        messages = {
            "docs": [
                "Update documentation",
                "docs: minor improvements",
                "Refine README structure",
                "Update docs",
                "docs: refresh changelog",
                "docs: improve project documentation",
                "Update project guidelines",
                "docs: formatting and clarity improvements",
                "Improve contributing guidelines",
                "docs: update project info",
                "Enhance documentation readability",
                "docs: add missing sections",
            ],
            "maintenance": [
                "chore: routine maintenance",
                "maintenance: update logs",
                "Routine checks and updates",
                "chore: minor repository maintenance",
                "Update maintenance tracker",
                "chore: project health check",
                "maintenance: verify configurations",
                "chore: review and update configs",
                "Update project files",
                "chore: routine cleanup",
                "maintenance: regular upkeep",
                "chore: verify project structure",
            ],
            "issues": [
                "chore: housekeeping",
                "Tracking potential improvements",
                "Add notes on dependency updates",
                "Review open items",
                "chore: organize project tracking",
            ]
        }
        return random.choice(messages.get(action_type, ["Update codebase"]))
