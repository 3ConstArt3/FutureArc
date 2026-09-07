"""Errors callers can handle without inspecting implementation details."""

class GenAIArtError(Exception):
    """Base error raised by src workflows."""

class InvalidCollectionError(GenAIArtError):
    """An idea or collection does not satisfy the expected folder structure."""

class CatalogBuildError(GenAIArtError):
    """Reading or saving the catalog failed."""
