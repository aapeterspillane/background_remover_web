"""Temporary file management utilities."""

import tempfile
from pathlib import Path
from contextlib import contextmanager
from typing import Generator


@contextmanager
def temp_file(suffix: str = "") -> Generator[Path, None, None]:
    """
    Context manager for creating and cleaning up temporary files.

    Args:
        suffix: Optional file suffix (e.g., ".png").

    Yields:
        Path to the temporary file.
    """
    temp_path = None
    try:
        fd, temp_path_str = tempfile.mkstemp(suffix=suffix)
        temp_path = Path(temp_path_str)
        # Close the file descriptor, we just need the path
        import os
        os.close(fd)
        yield temp_path
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


async def save_upload_file(upload_file, destination: Path) -> None:
    """
    Save an uploaded file to the specified destination.

    Args:
        upload_file: The uploaded file from FastAPI.
        destination: Path where the file should be saved.
    """
    content = await upload_file.read()
    destination.write_bytes(content)
