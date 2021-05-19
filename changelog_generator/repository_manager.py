import re
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import ClassVar, Iterable, List, Pattern, Sequence, Tuple

from git import Repo

from changelog_generator.commit import Commit


class BaseTagManager(ABC):
    PATTERN: ClassVar[Pattern[str]]

    def get_semver_from_tag(self, tag: str) -> Tuple[int, ...]:
        """
        Splits a tag in a semver tuple of ints (major,minor,bug,rc).
        """
        res = self.PATTERN.match(tag)
        if not res:
            raise ValueError(f"Not a valid tag: {tag}")
        return tuple(
            map(
                int,
                [
                    res.group("major"),
                    res.group("minor"),
                    res.group("bug") or 0,
                    res.group("rc") or 0,
                ],
            )
        )

    @abstractmethod
    def is_release_tag(self, tag: str) -> bool:
        """validates a tag"""

    @abstractmethod
    def get_tags(self):
        """list the tags"""

    def get_release_tags(self) -> Sequence[str]:
        """Lists only the release tags"""
        return tuple(
            sorted(
                filter(self.is_release_tag, self.get_tags()),
                key=self.get_semver_from_tag,
                reverse=True,
            )
        )


class SimpleTagManager(BaseTagManager):
    """
    Matches tags of the kind:
        - 1.2.3
        - 1-2-3
        - v1.2.3
        - 1.2.3rc1
    """

    PATTERN = re.compile(
        r"^v?(?P<major>\d+)[-.](?P<minor>\d+)[-.]((?P<bug>\d+)|rc(?P<rc>\d+))?$"
    )

    def __init__(self, repository: Repo) -> None:
        self.repository = repository

    def is_release_tag(self, tag: str) -> bool:
        res = self.PATTERN.match(tag)
        return res and not res.group("rc")

    def get_tags(self):
        return self.repository.git.tag(f"--merged").split("\n")


class PrefixedTagManager(BaseTagManager):
    """
    Matches tags of the kind:
        - toto/1.2.3
        - toto/1.2.3rc1
    """

    PATTERN = re.compile(
        r"^(?P<prefix>\w+)/(?P<major>\d+)\.(?P<minor>\d+)\.((?P<bug>\d+)|rc(?P<rc>\d+))?$"
    )

    def __init__(self, repository: Repo, prefix: str):
        self.repository = repository
        self.prefix = prefix

    def is_release_tag(self, tag: str) -> bool:
        """making sure that only the tags with the prefix are listed"""
        res = self.PATTERN.match(tag)
        return res and res.group("prefix") == self.prefix and not res.group("rc")

    def get_tags(self):
        return self.repository.git.tag(f"--merged", "HEAD", f"{self.prefix}/*").split(
            "\n"
        )


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
