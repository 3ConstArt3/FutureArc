"""Serialize the public JSON format and replace complete catalogs atomically."""
import json
import os
from pathlib import Path
import tempfile

from src.models import Artwork


def save_catalog(artworks: list[Artwork], output: Path) -> None:
    # Explicit mapping keeps future internal model fields out of the file format.
    records = [
        {"title": art.title, "prompt": art.prompt, "images": art.images}
        for art in artworks
    ]
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output.parent,
            prefix=".artworks-", suffix=".tmp", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(records, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
        os.replace(temporary_path, output)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
