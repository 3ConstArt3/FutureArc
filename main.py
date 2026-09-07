"""Open this file in your IDE and press Run. No arguments required."""
from pathlib import Path
import sys

from src.config import CatalogConfig
from src.exceptions import GenAIArtError
from src.service import build_catalog


def main() -> int:
    config = CatalogConfig(
        assets_directory=Path(__file__).resolve().parent / "assets",
    )
    try:
        result = build_catalog(config)
    except GenAIArtError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(
        f"Saved {result.artwork_count} ideas and {result.image_count} images "
        f"to {result.output_file}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())