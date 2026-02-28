from datetime import datetime
from github import Repository, GithubException
from engine.behavior import BehaviorController

class RepositoryExecutor:
    def __init__(self, repo: Repository.Repository, behavior: BehaviorController):
        self.repo = repo
        self.behavior = behavior

    def execute_action(self, action: str):
        if action == "maintenance_log":
            self._append_maintenance_log()
        elif action == "update_readme":
            self._update_readme_timestamp()
        elif action == "update_changelog":
            self._update_changelog()
        else:
            raise ValueError(f"Unknown action: {action}")

    def _safe_commit(self, file_path: str, content: str, commit_message: str):
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
            old_contents = "# Maintenance Logs\n"
            
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_content = old_contents + f"\n- [Routine] System checked on {date_str} - dependencies verified."
        
        self._safe_commit(file_path, new_content, commit_msg)

    def _update_readme_timestamp(self):
        file_path = "README.md"
        commit_msg = self.behavior.generate_commit_message("docs")
        
        try:
            old_contents = self.repo.get_contents(file_path).decoded_content.decode("utf-8")
        except GithubException:
            old_contents = f"# {self.repo.name}\n"
            
        date_str = datetime.now().strftime("%Y-%m-%d")
        ts_marker = "<!-- LAST_MAINTAINED -->"
        new_ts = f"{ts_marker}\n_Last maintained: {date_str}_"
        
        if ts_marker in old_contents:
            import re
            new_content = re.sub(rf"{ts_marker}.*", new_ts, old_contents, flags=re.MULTILINE)
        else:
            new_content = old_contents + "\n\n" + new_ts
            
        self._safe_commit(file_path, new_content, commit_msg)
        
    def _update_changelog(self):
        file_path = "CHANGELOG.md"
        commit_msg = self.behavior.generate_commit_message("docs")
        
        try:
            old_contents = self.repo.get_contents(file_path).decoded_content.decode("utf-8")
        except GithubException:
            old_contents = "# Changelog\n"
            
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_content = old_contents + f"\n## {date_str}\n- Routine maintenance pass."
        
        self._safe_commit(file_path, new_content, commit_msg)
