import re
from abc import ABC
from functools import lru_cache
from typing import Iterable, List, Pattern, Sequence, Tuple

from git import Repo

from changelog_generator.commit import Commit


class BaseTagManager(ABC):
    def __init__(self, regex: Pattern[str]):
        self.regex = regex

    def get_tag_as_tuple(self, tag: str) -> Tuple[int, ...]:
        """
        Splits a tag in a tuple of ints (major,minor,bug,rc).

        Args:
            regex: the regex that matches the major,minor,bug,rc values
            tag: the tag to parse

        Notes:
            This makes it straightforward to compare two tags.
        """
        res = self.regex.match(tag)
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

    def is_tag_version(self, tag: str) -> bool:
        res = self.regex.match(tag)
        return res and not res.group("rc")

    def filter(self, tags: Iterable[str]) -> Sequence[str]:
        return tuple(
            sorted(
                filter(self.is_tag_version, tags),
                key=self.get_tag_as_tuple,
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

    def __init__(self):
        super().__init__(self.PATTERN)


class MultiServiceTagManager(BaseTagManager):
    """
    Matches tags of the kind:
        - toto/1.2.3
        - toto/1.2.3rc1
    """

    def __init__(self, service: str):
        super().__init__(
            re.compile(
                f"^{service}/"
                r"(?P<major>\d+)\.(?P<minor>\d+)\.((?P<bug>\d+)|rc(?P<rc>\d+))?$"
            )
        )


remote_re = re.compile(
    r"^(https://github\.com/|git@github\.com:)"
    r"(?P<organization>[^/]+)/(?P<repository>[^.]+)(\.git)?$"
)


class RepositoryManager:
    repository: Repo
    organization: str = ""
    name: str = ""

    def __init__(self, uri: str, service: str = "") -> None:
        self.is_multi_service = bool(service)
        self.service = service
        self.repository = Repo(uri)
        self.tag_names: List[str] = []
        if self.repository.bare:
            raise ValueError(f"Repository {self.repository.git_dir} is bare")

        res = remote_re.match(self.repository.remotes["origin"].url)
        if res:
            self.organization = res.group("organization")
            self.name = res.group("repository")

    @property
    @lru_cache()
    def tags(self) -> Sequence[str]:
        tags: List[str] = self.repository.git.tag("--merged").split("\n")

        tag_manager = (
            MultiServiceTagManager(self.service)
            if self.is_multi_service
            else SimpleTagManager()
        )

        return tag_manager.filter(tags)

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
