from dataclasses import dataclass
from typing import Optional

from git import Repo


@dataclass
class GitStatus:
    branch: str
    dirty: bool
    details: str


class GitOperations:
    def __init__(self, repo_path: str = ".") -> None:
        self.repo = Repo(repo_path, search_parent_directories=True)

    def status(self) -> GitStatus:
        branch = self.repo.active_branch.name
        dirty = self.repo.is_dirty()
        details = self.repo.git.status("-sb")
        return GitStatus(branch=branch, dirty=dirty, details=details)

    def commit(self, message: str) -> Optional[str]:
        if not self.repo.is_dirty():
            return None
        self.repo.git.add(all=True)
        commit = self.repo.index.commit(message)
        return commit.hexsha
