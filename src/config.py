"""Configuration shared by the filesystem reader and catalog builder."""
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".webp", ".gif",
})

@dataclass(frozen=True, slots=True)
class CatalogConfig:
    assets_directory: Path

    @property
    def output_file(self) -> Path:
        # Keep the catalog beside its relative image paths.
        return self.assets_directory / "artworks.json"
