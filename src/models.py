"""Domain records independent of filesystem operations."""
from dataclasses import dataclass
from pathlib import Path

@dataclass(slots=True)
class Artwork:
    """One idea and its shared prompt, with image IDs mapped to relative paths."""
    title: str
    prompt: str
    images: dict[str, str]

@dataclass(frozen=True, slots=True)
class BuildResult:
    """Build summary for IDE, future UI, or other callers."""
    output_file: Path
    artwork_count: int
    image_count: int
