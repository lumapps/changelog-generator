from pathlib import Path

from git import Repo

from changelog_generator.commit import construct_commit_trees, cut_trees_commits
from changelog_generator.repository_manager import RepositoryManager


def test_repository_github_link_since_tag(core_repo: Repo) -> None:
    # Given
    path = str(Path(core_repo.git_dir).parent)
    repository = RepositoryManager(path, "monolite")
    tag = "monolite/7.5.0"

    link = repository.get_github_link_for_commits_since_tag(tag)

    assert (
        link
        == f"https://github.com/lumapps/core/compare/monolite/7.5.0...{repository.current_tag}"
    )


def test_cut_trees_commits(core_repo: Repo) -> None:
    # Given
    path = str(Path(core_repo.git_dir).parent)
    repository = RepositoryManager(path, "monolite")
    tag = "monolite/7.5.0"
    commits = repository.get_commits_since_tag(tag)
    n_commits_before_cut = len(commits)
    trees = construct_commit_trees(commits)

    max_commits = 2000

    # When
    cut_trees_commits(trees, n_commits_before_cut, max_commits)

    # Then
    n_commits_after_cut = sum([len(t.commits) for t in trees])

    assert trees
    assert n_commits_after_cut < max_commits

    # Check that only others section have been cut
    # since monolite/7.5.0 others section contains at least 2000 commits (and 2500 total)
    # so it should be the first and only one to be cut to reach 2000 commits
    others_commits = trees[-1]
    assert others_commits.id == "others"
    assert len(others_commits.commits) == 10
    assert (
        n_commits_after_cut - len(others_commits.commits) + 1 + max_commits
        == n_commits_before_cut
    )
