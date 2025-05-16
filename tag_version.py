import re
import subprocess
from pathlib import Path

INIT_PATH = Path("resnap/__init__.py")


def extract_version(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if not match:
        raise RuntimeError("Impossible de trouver __version__")
    return match.group(1)


def git_tag(version):
    tag = f"v{version}"
    print(f"Création du tag : {tag}")
    subprocess.run(["git", "tag", tag], check=True)
    subprocess.run(["git", "push", "origin", tag], check=True)
    print(f"Tag {tag} poussé sur origin")


if __name__ == "__main__":
    if not INIT_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {INIT_PATH}")
    version = extract_version(INIT_PATH)
    git_tag(version)
