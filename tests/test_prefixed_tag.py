from pathlib import Path

from git import Repo

from changelog_generator.repository_manager import RepositoryManager


def test_get_cms_changelog(core_repo: Repo):
    path = str(Path(core_repo.git_dir).parent)
    repository = RepositoryManager(path, "cms")
    current_tag = repository.current_tag
    assert current_tag
    previous_tag = repository.previous_tag
    assert previous_tag

    commits = repository.commits_since_last_tag
    assert commits


def test_get_rbac_changelog(core_repo: Repo):
    path = str(Path(core_repo.git_dir).parent)
    repository = RepositoryManager(path, "rbac")
    current_tag = repository.current_tag
    assert current_tag
    previous_tag = repository.previous_tag
    assert previous_tag

    commits = repository.commits_since_last_tag
    assert commits
