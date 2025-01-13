import re
from abc import ABC, abstractmethod
from typing import ClassVar, Pattern, Sequence, Tuple

from git import Repo


class BaseTagManager(ABC):
    PATTERN: ClassVar[Pattern[str]]

    def get_semver_from_tag(self, tag: str) -> Tuple[int, ...]:
        """
        Splits a tag in a semantic versioning tuple of integers (major,minor,bug,patch).
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
        return self.repository.git.tag("--merged").split("\n")


class PrefixedTagManager(BaseTagManager):
    """
    Matches tags of the kind:
        - toto/1.2.3
        - toto/1.2.3rc1
    """

    PATTERN = re.compile(
        r"^(?P<prefix>[\w-]+)/(?P<major>\d+)\.(?P<minor>\d+)\.((?P<bug>\d+)|rc(?P<rc>\d+))?$"
    )

    def __init__(self, repository: Repo, prefix: str):
        self.repository = repository
        self.prefix = prefix

    def is_release_tag(self, tag: str) -> bool:
        """making sure that only the tags with the prefix are listed"""
        res = self.PATTERN.match(tag)
        return res and res.group("prefix") == self.prefix and not res.group("rc")

    def get_tags(self):
        return self.repository.git.tag(
            "--merged", "origin/master", f"{self.prefix}/*"
        ).split("\n")
