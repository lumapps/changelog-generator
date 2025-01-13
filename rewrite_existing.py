"""
Uses the GitHub command line tool to easily rewrite a existing release note

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
    target = args.target
    filter_paths = args.filter_paths
    path = args.repository_path

    update_release_note(filter_paths, path, target)


def update_release_note(filter_paths, path, target, create: bool = True):
    tag_n, tag_n1 = target.split("..")
    print("Will rewrite the release with the commits between ", tag_n, tag_n1)
    changelog = generate(path, target=target, filter_paths=filter_paths)
    changelog = changelog[:125000]
    try:
        # checking if the release exists
        subprocess.check_output(
            ["gh", "release", "view", tag_n1],
            input=changelog.encode(),
            cwd=path,
        )
    except subprocess.CalledProcessError:
        print(f"the tag {tag_n1} exists but has not been released yet")
        if create:
            print(
                subprocess.check_output(
                    [
                        "gh",
                        "release",
                        "create",
                        tag_n1,
                        "--title",
                        f"Release {tag_n1}",
                        "-F",
                        "-",
                    ],
                    input=changelog.encode(),
                    cwd=path,
                )
            )
    else:
        print(
            subprocess.check_output(
                ["gh", "release", "edit", tag_n1, "-F", "-"],
                input=changelog.encode(),
                cwd=path,
            )
        )


if __name__ == "__main__":
    run()
