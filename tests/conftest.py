import os
import tempfile
from pathlib import Path

import pytest
from git import Repo


@pytest.fixture(scope="session", autouse=True)
def core_repo() -> Repo:
    tempdir = Path(tempfile.gettempdir()) / "changelog_generator" / "core"
    try:
        os.makedirs(tempdir)
        repo = Repo.clone_from("git@github.com:lumapps/core.git", tempdir)
    except OSError:
        repo = Repo(tempdir)
    return repo


@pytest.fixture(scope="session", autouse=True)
def organization_repo() -> Repo:
    tempdir = Path(tempfile.gettempdir()) / "changelog_generator" / "organization"
    try:
        os.makedirs(tempdir)
        repo = Repo.clone_from("git@github.com:lumapps/organization.git", tempdir)
    except OSError:
        repo = Repo(tempdir)
    return repo
