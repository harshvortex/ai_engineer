import random
import time
import logging

class BehaviorController:
    def __init__(self, config: dict):
        self.config = config
        self.min_delay = self.config.get('min_delay_minutes', 5)
        self.max_delay = self.config.get('max_delay_minutes', 60)
        self.skip_prob = self.config.get('skip_probability', 0.15)
        self.cooldown_hours = self.config.get('commit_cooldown_hours', 12)

    def should_skip_today(self) -> bool:
        """Introduce randomness by occasionally skipping execution to simulate human behavior."""
        skip = random.random() < self.skip_prob
        if skip:
            logging.info("Behavior: Randomly decided to skip execution today.")
        return skip

    def apply_random_delay(self, disable_delay: bool = False):
        """Random delay execution between min_delay and max_delay minutes.
        Supports disable_delay for local debugging.
        """
        if disable_delay:
            return
            
        delay_minutes = random.randint(self.min_delay, self.max_delay)
        delay_seconds = delay_minutes * 60
        logging.info(f"Behavior: Sleeping for {delay_minutes} minutes to simulate human timing.")
        time.sleep(delay_seconds)

    def generate_commit_message(self, action_type: str) -> str:
        """Randomized human-like commit messages."""
        messages = {
            "docs": [
                "Update documentation",
                "docs: minor improvements",
                "Refine README structure",
                "Update docs",
                "docs: refresh changelog"
            ],
            "maintenance": [
                "chore: routine maintenance",
                "maintenance: update logs",
                "Routine checks and updates",
                "chore: minor repository maintenance",
                "Update maintenance tracker"
            ],
            "issues": [
                "chore: housekeeping",
                "Tracking potential improvements",
                "Add notes on dependency updates"
            ]
        }
        return random.choice(messages.get(action_type, ["Update codebase"]))
