import os
from typing import List, NamedTuple, Sequence

from jinja2 import Environment, FileSystemLoader

from changelog_generator.commit import Commit
from changelog_generator.repository_manager import RepositoryManager


class CommitTree(NamedTuple):
    commit_type: str
    commits: Sequence[Commit]


def render_changelog(
    organization: str,
    repository: str,
    previous_tag: str,
    current_tag: str,
    commit_trees: Sequence[CommitTree],
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


def main() -> None:
    repository = RepositoryManager("./", os.environ.get("SERVICE"))

    commits = repository.commits_since_last_tag
    trees: List[CommitTree] = []

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
            organization=repository.organization,
            repository=repository.name,
            previous_tag=repository.previous_tag,
            current_tag=repository.current_tag,
            commit_trees=trees,
        )
    )


if __name__ == "__main__":
    main()
