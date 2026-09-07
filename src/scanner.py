"""Read immediate idea folders without changing source files."""
from pathlib import Path

from src.config import IMAGE_EXTENSIONS
from src.exceptions import InvalidCollectionError
from src.identifiers import image_id
from src.models import Artwork


def read_artwork(idea: Path, root: Path) -> Artwork:
    prompt_file = idea / "prompt.txt"
    images_directory = idea / "images"
    if prompt_file.is_symlink() or not prompt_file.is_file():
        raise InvalidCollectionError(f"{idea.name}: missing regular prompt.txt file")
    if images_directory.is_symlink() or not images_directory.is_dir():
        raise InvalidCollectionError(f"{idea.name}: missing regular images directory")
    prompt = prompt_file.read_text(encoding="utf-8-sig")
    if not prompt.strip():
        raise InvalidCollectionError(f"{idea.name}: prompt.txt is empty")

    images: dict[str, str] = {}
    for image in sorted(images_directory.iterdir(), key=lambda path: path.name):
        if image.is_symlink():
            raise InvalidCollectionError(f"{idea.name}: symbolic links are not supported: {image.name}")
        if image.is_file() and image.suffix.lower() in IMAGE_EXTENSIONS:
            relative_path = image.relative_to(root).as_posix()
            images[image_id(relative_path)] = relative_path
    if not images:
        raise InvalidCollectionError(f"{idea.name}: no supported image files in images/")
    return Artwork(title=idea.name, prompt=prompt, images=images)


def scan_collection(root: Path) -> list[Artwork]:
    """Every immediate, non-hidden directory is an idea; files are ignored."""
    if not root.is_dir():
        raise InvalidCollectionError(f"Collection folder does not exist: {root}")
    artworks = []
    for idea in sorted(root.iterdir(), key=lambda path: path.name):
        if idea.name.startswith("."):
            continue
        if idea.is_symlink():
            raise InvalidCollectionError(f"Symbolic links are not supported: {idea.name}")
        if idea.is_dir():
            artworks.append(read_artwork(idea, root))
    if not artworks:
        raise InvalidCollectionError("No idea folders found")
    return artworks
