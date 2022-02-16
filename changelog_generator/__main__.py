import os
from typing import List, Sequence

from jinja2 import Environment, FileSystemLoader

from changelog_generator.commit import (
    CommitTree,
    check_and_cut_if_over_limit,
    construct_commit_trees,
)
from changelog_generator.repository_manager import RepositoryManager


def render_changelog(
    organization: str,
    repository: str,
    previous_tag: str,
    current_tag: str,
    commit_trees: Sequence[CommitTree],
    link_to_commits: str,
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
        link_to_commits=link_to_commits,
    )


def main() -> None:
    repository = RepositoryManager("./", os.environ.get("TAG_PREFIX"))
    max_changelog_length: int = int(os.getenv("MAX_LENGTH", 5000))

    commits = repository.commits_since_last_tag
    trees: List[CommitTree] = construct_commit_trees(commits)

    check_and_cut_if_over_limit(max_changelog_length, len(commits), trees)

    print(
        render_changelog(
            organization=repository.organization,
            repository=repository.name,
            previous_tag=repository.previous_tag,
            current_tag=repository.current_tag,
            commit_trees=trees,
            link_to_commits=repository.get_github_link_for_commits_since_last_tag(),
        )
    )


if __name__ == "__main__":
    main()
