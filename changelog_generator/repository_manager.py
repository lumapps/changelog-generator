import re
from typing import Iterable, List, Optional

from git import Repo

from changelog_generator.commit import Commit

tag_version_re = re.compile(
    r"^v?(?P<major>\d+)[-\.]+(?P<minor>\d+)[-\.]+((?P<bug>\d+)|rc(?P<rc>\d+)){0,1}$"
)

remote_re = re.compile(
    r"^(https://github\.com/|git@github\.com:)"
    r"(?P<organization>[^/]+)/(?P<repository>[^.]+)(\.git)?$"
)


def is_tag_version(tag: str) -> bool:
    res = tag_version_re.match(tag)
    if not res:
        return False
    return not res.group("rc")


def get_tag_value(tag: str) -> int:
    res = tag_version_re.match(tag)
    assert res
    return -1 * (
        1000000 * int(res.group("major"))
        + 10000 * int(res.group("minor"))
        + 100 * int(res.group("bug") or "0")
        + int(res.group("rc") or "100")
    )


class RepositoryManager:
    repository: Repo
    organization: str = ""
    name: str = ""

    def __init__(self, uri: str) -> None:
        self.repository = Repo(uri)
        self.tag_names: List[str] = []
        assert not self.repository.bare

        res = remote_re.match(self.repository.remotes["origin"].url)
        if res:
            self.organization = res.group("organization")
            self.name = res.group("repository")

        self.tags = self.get_tags()

    def get_tags(self) -> List[str]:
        if not self.tag_names:
            tags: List[str] = self.repository.git.tag("--merged").split("\n")
            self.tag_names = list(
                sorted(filter(is_tag_version, tags), key=get_tag_value)
            )
        return self.tag_names

    def get_current_tag(self) -> Optional[str]:
        if not self.tags:
            return None

        tag = self.repository.tags[self.tags[0]]
        if tag.commit == self.repository.head.commit:
            return tag
        return None

    def get_previous_tag(self) -> Optional[str]:
        current_tag = self.get_current_tag()

        if not current_tag and self.tags:
            return self.tags[0]

        if current_tag and len(self.tags) > 1:
            return self.tags[1]

        return None

    def get_commits_since_last_tag(self) -> Iterable[Commit]:
        previous_tag = self.get_previous_tag()
        current_tag = self.get_current_tag() or "HEAD"

        if previous_tag:
            revision = "%s..%s" % (previous_tag, current_tag)
        else:
            revision = current_tag

        return map(
            lambda commit: Commit(
                hexsha=commit.hexsha, summary=commit.summary, message=commit.message
            ),
            self.repository.iter_commits(revision, no_merges=True),
        )

    def get_organization(self) -> str:
        return self.organization

    def get_name(self) -> str:
        return self.name
