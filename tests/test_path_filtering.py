from pathlib import Path

from git import Repo

from changelog_generator.repository_manager import RepositoryManager


def generate_service_related_paths(service: str, include_common: bool = True):
    common_paths = [f"core/common"]
    service_paths = [f"core/{service}"]
    return service_paths if not include_common else common_paths + service_paths


def test_get_cms_changelog(core_repo: Repo):
    # GIVEN
    path = str(Path(core_repo.git_dir).parent)
    service = "cms"

    # WHEN
    repository = RepositoryManager(
        path, service, generate_service_related_paths(service)
    )

    # THEN
    current_tag = repository.current_tag
    assert current_tag
    previous_tag = repository.previous_tag
    assert previous_tag
    commits = repository.commits_since_last_tag
    assert commits
