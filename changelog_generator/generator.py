import os
from typing import List, NamedTuple, Optional, Sequence

from jinja2 import Environment, FileSystemLoader

from .commit import Commit
from .repository_manager import RepositoryManager
from .ai_generator import generate_ai_summary


class CommitTree(NamedTuple):
    commit_type: str
    commits: Sequence[Commit]


def render_changelog(
    organization: str,
    repository: str,
    previous_tag: str,
    current_tag: str,
    commit_trees: Sequence[CommitTree],
    ai_summary: str | None,
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
        ai_summary=ai_summary,
    )


def get_commit_trees(commits: Sequence[Commit]) -> List[CommitTree]:
    types = {"docs", "feat", "fix", "revert"}
    titles = {
        "docs": ":notebook_with_decorative_cover: Documentation",
        "feat": ":rocket: Features",
        "fix": ":bug: Fixes",
        "revert": ":scream: Revert",
        "others": ":nut_and_bolt: Others",
    }
    commit_by_type = {}
    for commit in commits:
        if commit.commit_type in types:
            commit_by_type.setdefault(commit.commit_type, []).append(commit)
        else:
            commit_by_type.setdefault("others", []).append(commit)

    return [
        CommitTree(commit_type=title, commits=commit_by_type[commit_type])
        for commit_type, title in titles.items()
        if commit_type in commit_by_type
    ]


def generate(
    repository_path: str,
    target: Optional[str] = None,
    prefix: Optional[str] = None,
    filter_paths: Optional[str] = None,
) -> str:
    repository = RepositoryManager(
        uri=repository_path, prefix=prefix, filter_paths=filter_paths
    )
    if target:
        commits = repository.from_target(target)
        previous_tag, current_tag = target.split("..")
        diff = None
    else:
        commits = repository.commits_since_last_tag
        previous_tag, current_tag = repository.previous_tag, repository.current_tag
        diff = repository.get_diff_since_last_tag

    changelog = render_changelog(
        organization=repository.organization,
        repository=repository.name,
        previous_tag=previous_tag,
        current_tag=current_tag,
        commit_trees=get_commit_trees(commits),
        ai_summary=generate_ai_summary(diff),
    )
    return changelog
