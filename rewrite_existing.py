"""
Uses the gh cli to easily rewrite a existing release note

How To Use:
  python -m path_to_repository previousTag..nextTag [filter_path1 filter_path2]

"""
import subprocess
from argparse import ArgumentParser

from changelog_generator.generator import generate


def run():
    parser = ArgumentParser()
    parser.add_argument(
        "repository_path",
        help="The path to the repository",
    )
    parser.add_argument(
        "target",
        help="A rev1..rev2 string to be used to generate the commit list",
    )
    parser.add_argument(
        "filter_paths",
        nargs="*",
        help="A space separated list of path to be used to the commits that edited files within "
        "them",
    )
    args = parser.parse_args()
    (tag_n, tag_n1) = args.target.split("..")

    print("Will rewrite the release with the commits between ", tag_n, tag_n1)
    changelog = generate(
        args.repository_path, target=args.target, filter_paths=args.filter_paths
    )
    print(
        subprocess.check_output(
            ["gh", "release", "edit", tag_n1, "-F", "-"],
            input=changelog.encode(),
            cwd=args.repository_path,
        )
    )


if __name__ == "__main__":
    run()
