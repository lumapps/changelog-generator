import re
from functools import lru_cache
from typing import List, Optional, Sequence

from git import Repo

from .commit import Commit
from .tag_manager import PrefixedTagManager, SimpleTagManager

remote_re = re.compile(
    r"^(https://github\.com/|git@github\.com:)"
    r"(?P<organization>[^/]+)/(?P<repository>[^.]+)(\.git)?$"
)


class RepositoryManager:
    repository: Repo
    organization: str = ""
    name: str = ""

    def __init__(self, uri: str, prefix: str = "") -> None:
        self.repository = Repo(uri)
        self.tag_names: List[str] = []
        if self.repository.bare:
            raise ValueError(f"Repository {self.repository.git_dir} is bare")

        res = remote_re.match(self.repository.remotes["origin"].url)
        if res:
            self.organization = res.group("organization")
            self.name = res.group("repository")

        self.tag_manager = (
            PrefixedTagManager(self.repository, prefix)
            if prefix
            else SimpleTagManager(self.repository)
        )

    @property
    @lru_cache()
    def tags(self) -> Sequence[str]:
        return self.tag_manager.get_release_tags()

    @property
    @lru_cache()
    def current_tag(self) -> str:
        return str(self.repository.tags[self.tags[0]]) if self.tags else "HEAD"

    @property
    @lru_cache()
    def previous_tag(self) -> str:
        return str(self.tags[1]) if self.current_tag and len(self.tags) > 1 else ""

    @property
    @lru_cache()
    def commits_since_last_tag(self) -> Sequence[Commit]:
        if self.previous_tag:
            revision = f"{self.previous_tag}..{self.current_tag}"
        else:
            revision = self.current_tag

        return tuple(
            Commit(hexsha=commit.hexsha, summary=commit.summary, message=commit.message)
            for commit in self.repository.iter_commits(revision, no_merges=True)
        )

    @lru_cache()
    def get_commits_since_tag(self, tag: str) -> Sequence[Commit]:
        revision = f"{tag}..{self.current_tag}"

        return tuple(
            Commit(hexsha=commit.hexsha, summary=commit.summary, message=commit.message)
            for commit in self.repository.iter_commits(revision, no_merges=True)
        )

    @lru_cache()
    def get_github_link_for_commits_since_last_tag(self) -> Optional[str]:
        if not self.previous_tag:
            return None
        return self.get_github_link_for_commits_since_tag(self.previous_tag)

    @lru_cache()
    def get_github_link_for_commits_since_tag(self, tag: str) -> str:
        return f"https://github.com/{self.organization}/{self.name}/compare/{tag}...{self.current_tag}"
