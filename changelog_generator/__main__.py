import os
from argparse import ArgumentParser

from .generator import generate


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "-t",
        "--tag_prefix",
        nargs="?",  # optional argument
        help="Filter tag with this prefix. Note: also available as TAG_PREFIX env var",
    )
    parser.add_argument(
        "-p",
        "--path_filters",
        nargs="*",  # optional list
        help="Filter commits with this semicolon separated git path regex",
    )
    parser.add_argument(
        "--target",
        nargs="?",  # optional argument
        help="A rev1..rev2 string to be used to generate the commit list",
    )
    args = parser.parse_args()
    #
    prefix = args.tag_prefix or os.environ.get("TAG_PREFIX")
    filter_paths = args.path_filters

    changelog = generate(
        repository_path="./",
        prefix=prefix,
        filter_paths=filter_paths,
        target=args.target,
    )
    print(changelog)


if __name__ == "__main__":
    main()
