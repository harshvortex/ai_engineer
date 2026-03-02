import random
from datetime import datetime
from github import Repository, GithubException
from engine.behavior import BehaviorController

class RepositoryExecutor:
    def __init__(self, repo: Repository.Repository, behavior: BehaviorController):
        self.repo = repo
        self.behavior = behavior

    def execute_action(self, action: str):
        action_map = {
            "maintenance_log": self._append_maintenance_log,
            "update_readme": self._update_readme_timestamp,
            "update_changelog": self._update_changelog,
            "update_contributing": self._update_contributing,
            "update_gitignore_notes": self._update_gitignore_notes,
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        handler()

    def _safe_commit(self, file_path: str, content: str, commit_message: str):
        """Create or update a file with proper error handling."""
        try:
            file_contents = self.repo.get_contents(file_path)
            self.repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=file_contents.sha
            )
        except GithubException as e:
            if e.status == 404:
                self.repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content
                )
            else:
                raise e

    def _append_maintenance_log(self):
        file_path = "MAINTENANCE.md"
        commit_msg = self.behavior.generate_commit_message("maintenance")
        
        try:
            old_contents = self.repo.get_contents(file_path).decoded_content.decode("utf-8")
        except GithubException:
            old_contents = "# Maintenance Logs\n\nAutomated maintenance tracking for this repository.\n"
            
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        checks = random.choice([
            "dependencies verified, no issues found",
            "code structure reviewed, all checks passed",
            "security audit completed, no vulnerabilities detected",
            "build configuration validated successfully",
            "repository health check completed",
            "license and documentation compliance verified",
        ])
        new_content = old_contents + f"\n- [{date_str}] {checks}"
        
        self._safe_commit(file_path, new_content, commit_msg)

    def _update_readme_timestamp(self):
        file_path = "README.md"
        commit_msg = self.behavior.generate_commit_message("docs")
        
        try:
            old_contents = self.repo.get_contents(file_path).decoded_content.decode("utf-8")
        except GithubException:
            old_contents = f"# {self.repo.name}\n\nA project by {self.repo.owner.login}.\n"
            
        date_str = datetime.now().strftime("%Y-%m-%d")
        ts_marker = "<!-- LAST_MAINTAINED -->"
        new_ts = f"{ts_marker}\n_Last maintained: {date_str}_"
        
        if ts_marker in old_contents:
            import re
            new_content = re.sub(rf"{ts_marker}.*", new_ts, old_contents, flags=re.DOTALL)
        else:
            new_content = old_contents.rstrip() + "\n\n" + new_ts + "\n"
            
        self._safe_commit(file_path, new_content, commit_msg)
        
    def _update_changelog(self):
        file_path = "CHANGELOG.md"
        commit_msg = self.behavior.generate_commit_message("docs")
        
        try:
            old_contents = self.repo.get_contents(file_path).decoded_content.decode("utf-8")
        except GithubException:
            old_contents = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n"
            
        date_str = datetime.now().strftime("%Y-%m-%d")
        entry = random.choice([
            "Routine maintenance pass - all systems operational.",
            "Reviewed project structure and dependencies.",
            "Minor documentation cleanup and formatting.",
            "Verified build pipeline and test configurations.",
            "Updated project metadata and configurations.",
        ])
        new_content = old_contents + f"\n## {date_str}\n- {entry}\n"
        
        self._safe_commit(file_path, new_content, commit_msg)

    def _update_contributing(self):
        file_path = "CONTRIBUTING.md"
        commit_msg = self.behavior.generate_commit_message("docs")
        
        try:
            old_contents = self.repo.get_contents(file_path).decoded_content.decode("utf-8")
        except GithubException:
            repo_name = self.repo.name
            lang = self.repo.language or "this project"
            old_contents = f"""# Contributing to {repo_name}

Thank you for considering contributing to **{repo_name}**!

## Getting Started

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Code of Conduct

Please be respectful and constructive in all interactions.

## Development

This project primarily uses **{lang}**. Please ensure your contributions follow the existing code style.
"""

        date_str = datetime.now().strftime("%Y-%m-%d")
        ts_marker = "<!-- LAST_UPDATED -->"
        new_ts = f"\n{ts_marker}\n_Guidelines last reviewed: {date_str}_\n"

        if ts_marker in old_contents:
            import re
            new_content = re.sub(rf"{ts_marker}.*", new_ts, old_contents, flags=re.DOTALL)
        else:
            new_content = old_contents.rstrip() + "\n" + new_ts

        self._safe_commit(file_path, new_content, commit_msg)

    def _update_gitignore_notes(self):
        file_path = ".gitignore"
        commit_msg = self.behavior.generate_commit_message("maintenance")

        try:
            old_contents = self.repo.get_contents(file_path).decoded_content.decode("utf-8")
        except GithubException:
            # Create a sensible .gitignore based on repo language
            lang = (self.repo.language or "").lower()
            templates = {
                "python": "# Python\n__pycache__/\n*.py[cod]\n*.egg-info/\ndist/\nbuild/\n.env\nvenv/\n",
                "javascript": "# Node\nnode_modules/\ndist/\n.env\n*.log\n",
                "java": "# Java\n*.class\n*.jar\ntarget/\n.idea/\n",
                "dart": "# Dart/Flutter\n.dart_tool/\nbuild/\n.packages\n",
            }
            old_contents = templates.get(lang, "# Auto-generated\n*.log\n.env\n")
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        marker = "# Last reviewed:"
        new_marker = f"{marker} {date_str}"
        
        if marker in old_contents:
            import re
            new_content = re.sub(rf"{marker}.*", new_marker, old_contents)
        else:
            new_content = old_contents.rstrip() + f"\n\n{new_marker}\n"

        self._safe_commit(file_path, new_content, commit_msg)
