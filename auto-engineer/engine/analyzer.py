import os
import datetime
from dateutil.parser import parse
from github import Repository

class RepositoryAnalyzer:
    def __init__(self, repo: Repository.Repository):
        self.repo = repo

    def get_inactivity_days(self) -> int:
        try:
            commits = list(self.repo.get_commits()[:1])
            if not commits:
                return 999
            last_commit = commits[0]
            last_commit_date = last_commit.commit.author.date
            now = datetime.datetime.now(last_commit_date.tzinfo)
            delta = now - last_commit_date
            return delta.days
        except Exception:
            return 999

    def has_dependency_updates(self) -> bool:
        # Placeholder for dependency analysis
        return False

    def check_readme_quality(self) -> int:
        try:
            readme = self.repo.get_readme()
            size = readme.size
            if size < 500:
                return 0 # poor
            elif size < 2000:
                return 1 # average
            else:
                return 2 # good
        except Exception:
            return 0

    def analyze(self) -> dict:
        return {
            "name": self.repo.full_name,
            "inactivity_days": self.get_inactivity_days(),
            "readme_quality": self.check_readme_quality(),
            "language": self.repo.language
        }
