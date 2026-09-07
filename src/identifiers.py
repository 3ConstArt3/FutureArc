"""Stable image identifiers compatible with the original builder."""
from uuid import NAMESPACE_URL, uuid5


def image_id(relative_path: str) -> str:
    """Identify a relative path, not image contents; renaming changes the ID."""
    return str(uuid5(NAMESPACE_URL, "genaiart:image:" + relative_path))
