import re
from typing import List, Optional, Sequence
from dataclasses import dataclass

re_header_pattern = re.compile(
    r"^(?P<type>[^\(]+)\((?P<scope>[^\)]+)\): (?P<subject>.+)$"
)
re_jira_pattern = re.compile(r"([A-Z]{2,4}-[0-9]{1,6})")
re_broke_pattern = re.compile(r"^BROKEN:$")
re_revert_header_pattern = re.compile(r"^[R|r]evert:? (?P<summary>.*)$")
re_revert_commit_pattern = re.compile(r"^This reverts commit ([a-f0-9]+)")
re_temp_header_pattern = re.compile(r"^(fixup!|squash!).*$")


class Commit:
    sha1: str
    short: str
    summary: str
    message: str

    revert: Optional["Commit"]
    commit_type: Optional[str]
    scope: Optional[str]
    subject: Optional[str]
    jiras: List[str]

    def get_header_data(self) -> None:
        self.commit_type = None
        self.scope = None
        self.subject = None

        res = re_header_pattern.match(self.summary)
        if res:
            self.commit_type = res.group("type")
            self.scope = res.group("scope")
            self.subject = res.group("subject")
        else:
            self.commit_type = "unknown"
            self.scope = "any"
            self.subject = self.summary

    def get_revert_data(self) -> None:
        self.revert = None

        res = re_revert_header_pattern.match(self.summary)
        if res:
            self.commit_type = "revert"

            self.revert = Commit(
                hexsha="", summary=res.group("summary"), message=res.group("summary")
            )

            summary_res = re_header_pattern.match(res.group("summary"))
            if summary_res:
                self.scope = summary_res.group("scope")
                self.subject = "revert %s" % summary_res.group("subject")
            else:
                self.scope = "any"
                self.subject = "revert %s" % res.group("summary")

    def get_jira_data(self) -> None:
        self.jiras = []

        for line in self.message.split("\n"):
            res = re_jira_pattern.findall(line)
            if res:
                self.jiras.extend(res)

    def __init__(self, hexsha: str, summary: str, message: str) -> None:
        self.sha1 = hexsha
        self.short = hexsha[:8]
        self.message = message
        self.summary = summary

        self.get_header_data()
        self.get_revert_data()
        self.get_jira_data()


@dataclass
class CommitTree:
    id: str
    commit_type: str
    commits: Sequence[Commit]


def get_commit_from_type(
    commits: Sequence[Commit], commit_type: str
) -> Sequence[Commit]:
    return sorted(
        filter(lambda commit: commit.commit_type == commit_type, commits),
        key=lambda commit: commit.scope,
    )


def get_commit_but_types(
    commits: Sequence[Commit], commit_types: Sequence[str]
) -> Sequence[Commit]:
    return sorted(
        filter(
            lambda commit: commit.commit_type
            and commit.commit_type not in commit_types,
            commits,
        ),
        key=lambda commit: commit.scope,
    )


def construct_commit_trees(commits: Sequence[Commit]) -> List[CommitTree]:
    trees = []
    documentations = CommitTree(
        id="doc",
        commit_type=":notebook_with_decorative_cover: Documentation",
        commits=get_commit_from_type(commits, "docs"),
    )
    if documentations.commits:
        trees.append(documentations)

    features = CommitTree(
        id="features",
        commit_type=":rocket: Features",
        commits=get_commit_from_type(commits, "feat"),
    )
    if features.commits:
        trees.append(features)

    fixes = CommitTree(
        id="fixes",
        commit_type=":bug: Fixes",
        commits=get_commit_from_type(commits, "fix"),
    )
    if fixes.commits:
        trees.append(fixes)

    reverts = CommitTree(
        id="revert",
        commit_type=":scream: Revert",
        commits=get_commit_from_type(commits, "revert"),
    )
    if reverts.commits:
        trees.append(reverts)

    others = CommitTree(
        id="others",
        commit_type=":nut_and_bolt: Others",
        commits=get_commit_but_types(
            commits, ["documentations", "feat", "fix", "revert"]
        ),
    )
    if others.commits:
        trees.append(others)

    return trees


def cut_tree_commits(tree: CommitTree, n_keep: int, n_commits_after_cutted: int) -> int:

    n_tree_commits = len(tree.commits)
    if n_tree_commits > n_keep:
        tree.commits = tree.commits[:n_keep]
        n_commits_after_cutted = n_commits_after_cutted - n_tree_commits + n_keep
    return n_commits_after_cutted


def cut_trees_commits(
    trees: List[CommitTree], n_commits: int, max_total_commits: int
) -> None:
    """
    Cut trees commits if we are above the given threshold for a valid changelog
    Cut them in order according to the `cut_order` map.
    Once the number of commits in under the fixed threshold, we stop.
    When cutting we cut the section to 10 commits (`n_commits_to_keep`).
    """
    cut_order = {"others": 1, "revert": 2, "doc": 3, "fixes": 4, "features": 5}

    trees_to_cut: List[CommitTree] = list(
        sorted(trees, key=lambda tree: cut_order[tree.id])
    )
    n_commits_after_section_cutted = n_commits

    n_commits_to_keep = 10
    for tree in trees_to_cut:
        if n_commits_after_section_cutted > max_total_commits:
            n_commits_after_section_cutted = cut_tree_commits(
                tree, n_commits_to_keep, n_commits_after_section_cutted
            )
        else:
            return


def check_and_cut_if_over_limit(
    max_changelog_length: int, n_commits: int, trees: List[CommitTree]
) -> None:
    # check if we have to much commits (-200 to take count of sections titles/spaces)
    max_commits = max_changelog_length - 200
    if n_commits > max_commits:
        cut_trees_commits(trees, n_commits, max_commits)
