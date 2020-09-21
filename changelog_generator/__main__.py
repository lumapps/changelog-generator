from typing import Iterable, List

from changelog_generator.commit import Commit
from changelog_generator.generator import CommitTree, renderChangelog
from changelog_generator.repository_manager import RepositoryManager


def getCommitFromType(commits: List["Commit"], type: str) -> List["Commit"]:
    return sorted(
        filter(lambda commit: commit.type == type, commits),
        key=lambda commit: commit.scope,
    )


def getCommitButTypes(commits: List["Commit"], types: List[str]) -> List["Commit"]:
    return sorted(
        filter(lambda commit: commit.type and commit.type not in types, commits),
        key=lambda commit: commit.scope,
    )


def main() -> None:
    repository = RepositoryManager("./")
    commits = list(repository.getCommitsSinceLastTag())
    trees: List["CommitTree"] = []

    documentations = CommitTree()
    documentations.type = ":notebook_with_decorative_cover: Documentation"
    documentations.commits = getCommitFromType(commits, "docs")
    if len(documentations.commits):
        trees.append(documentations)

    features = CommitTree()
    features.type = ":rocket: Features"
    features.commits = getCommitFromType(commits, "feat")
    if len(features.commits):
        trees.append(features)

    fixes = CommitTree()
    fixes.type = ":bug: Fixes"
    fixes.commits = getCommitFromType(commits, "fix")
    if len(fixes.commits):
        trees.append(fixes)

    reverts = CommitTree()
    reverts.type = ":scream: Revert"
    reverts.commits = getCommitFromType(commits, "revert")
    if len(reverts.commits):
        trees.append(reverts)

    others = CommitTree()
    others.type = ":nut_and_bolt: Others"
    others.commits = getCommitButTypes(
        commits, ["documentations", "feat", "fix", "revert"]
    )
    if len(others.commits):
        trees.append(others)

    print(
        renderChangelog(
            organization=repository.getOrganization(),
            repository=repository.getName(),
            previousTag=repository.getPreviousTag() or "",
            currentTag=repository.getCurrentTag() or "HEAD",
            commitTrees=trees,
        )
    )


if __name__ == "__main__":
    main()
