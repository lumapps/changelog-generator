from pathlib import Path

from git import Repo

from changelog_generator.repository_manager import RepositoryManager


def test_get_cms_changelog(core_repo: Repo):
    # GIVEN
    path = str(Path(core_repo.git_dir).parent)

    # WHEN
    repository = RepositoryManager(path, "cms")

    # THEN
    current_tag = repository.current_tag
    assert current_tag
    previous_tag = repository.previous_tag
    assert previous_tag
    commits = repository.commits_since_last_tag
    assert commits
