"""The catalog-building workflow, reusable independently of the entry point."""
from src.config import CatalogConfig
from src.exceptions import CatalogBuildError
from src.models import BuildResult
from src.scanner import scan_collection
from src.storage import save_catalog


def build_catalog(config: CatalogConfig) -> BuildResult:
    try:
        artworks = scan_collection(config.assets_directory)
        save_catalog(artworks, config.output_file)
    except (OSError, UnicodeError) as error:
        raise CatalogBuildError(f"Could not build catalog: {error}") from error
    return BuildResult(
        output_file=config.output_file,
        artwork_count=len(artworks),
        image_count=sum(len(art.images) for art in artworks),
    )
