import subprocess
from resnap import __version__ as current_version


def git_tag(version: str) -> None:
    """
    Create a git tag with the given version and push it to the remote repository.

    Args:
        version (str): The version to tag.
    """
    tag = f"v{version}"
    print(f"Création du tag : {tag}")
    subprocess.run(["git", "tag", tag], check=True)
    subprocess.run(["git", "push", "origin", tag], check=True)
    print(f"Tag {tag} poussé sur origin")


if __name__ == "__main__":
    git_tag(current_version)
