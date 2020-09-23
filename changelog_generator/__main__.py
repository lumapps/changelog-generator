import os
from typing import List, NamedTuple

from jinja2 import Environment, FileSystemLoader

from changelog_generator.commit import Commit
from changelog_generator.repository_manager import RepositoryManager


class CommitTree(NamedTuple):
    commit_type: str
    commits: List[Commit]


def render_changelog(
    organization: str,
    repository: str,
    previous_tag: str,
    current_tag: str,
    commit_trees: List[CommitTree],
) -> str:
    template_loader = FileSystemLoader(searchpath=os.path.dirname(__file__))
    template_environment = Environment(loader=template_loader)
    template = template_environment.get_template("changelog_template.jinja")

    return template.render(
        organization=organization,
        repository=repository,
        previous_tag=previous_tag,
        current_tag=current_tag,
        commit_trees=commit_trees,
    )


def get_commit_from_type(commits: List["Commit"], commit_type: str) -> List["Commit"]:
    return sorted(
        filter(lambda commit: commit.commit_type == commit_type, commits),
        key=lambda commit: commit.scope,
    )


def get_commit_but_types(
    commits: List["Commit"], commit_types: List[str]
) -> List["Commit"]:
    return sorted(
        filter(
            lambda commit: commit.commit_type
            and commit.commit_type not in commit_types,
            commits,
        ),
        key=lambda commit: commit.scope,
    )


def main() -> None:
    repository = RepositoryManager("./")

    commits = list(repository.get_commits_since_last_tag())
    trees: List["CommitTree"] = []

    documentations = CommitTree(
        commit_type=":notebook_with_decorative_cover: Documentation",
        commits=get_commit_from_type(commits, "docs"),
    )
    if documentations.commits:
        trees.append(documentations)

    features = CommitTree(
        commit_type=":rocket: Features", commits=get_commit_from_type(commits, "feat")
    )
    if features.commits:
        trees.append(features)

    fixes = CommitTree(
        commit_type=":bug: Fixes", commits=get_commit_from_type(commits, "fix")
    )
    if fixes.commits:
        trees.append(fixes)

    reverts = CommitTree(
        commit_type=":scream: Revert", commits=get_commit_from_type(commits, "revert")
    )
    if reverts.commits:
        trees.append(reverts)

    others = CommitTree(
        commit_type=":nut_and_bolt: Others",
        commits=get_commit_but_types(
            commits, ["documentations", "feat", "fix", "revert"]
        ),
    )
    if others.commits:
        trees.append(others)

    print(
        render_changelog(
            organization=repository.get_organization(),
            repository=repository.get_name(),
            previous_tag=repository.get_previous_tag() or "",
            current_tag=repository.get_current_tag() or "HEAD",
            commit_trees=trees,
        )
    )


if __name__ == "__main__":
    main()
