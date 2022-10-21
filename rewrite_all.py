from argparse import ArgumentParser
from collections import deque
from itertools import islice
from typing import Iterator, Tuple, TypeVar

from changelog_generator.repository_manager import RepositoryManager
from rewrite_existing import update_release_note

Item = TypeVar("Item")


def sliding_window_iter(it: Iterator[Item], size: int) -> Iterator[Tuple[Item, ...]]:
    """
    Get a iterator of sliding sequences

    Examples:
        it=[1 2 3 4], size=2 -> [(1,2) (2,3) (3,4)]
    """
    window = deque(islice(it, size), maxlen=size)
    for item in it:
        yield tuple(window)
        window.append(item)
    if window:
        yield tuple(window)


def rewrite_all_release_notes_by_prefix():
    parser = ArgumentParser()
    parser.add_argument(
        "repository_path",
        help="The path to the repository",
    )
    parser.add_argument(
        "prefix",
        help="The prefix to filter the tags",
    )
    parser.add_argument(
        "filter_paths",
        nargs="*",
        help="A space separated list of path to be used to the commits that edited files within "
        "them",
    )
    args = parser.parse_args()

    filter_paths = args.filter_paths
    path = args.repository_path
    prefix = args.prefix
    all_tags_descending = RepositoryManager(
        path, prefix=prefix, filter_paths=filter_paths
    ).tags

    for chunk in sliding_window_iter(reversed(all_tags_descending), 2):
        n, n1 = chunk
        update_release_note(filter_paths, path, f"{n}..{n1}")


if __name__ == "__main__":
    rewrite_all_release_notes_by_prefix()
