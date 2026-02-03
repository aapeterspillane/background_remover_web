"""Image processing module using rembg for background removal."""

import os
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image
from rembg import remove, new_session


def _setup_bundled_model():
    """Configure model path for PyInstaller bundled executable."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        bundle_dir = sys._MEIPASS
        model_dir = os.path.join(bundle_dir, 'u2net_models')
        if os.path.exists(model_dir):
            os.environ['U2NET_HOME'] = model_dir


class ImageProcessor:
    """Handles background removal using the rembg library."""

    SUPPORTED_FORMATS = {"image/jpeg", "image/png", "image/webp", "image/gif"}

    def __init__(self):
        """Initialize the processor and load the model."""
        # Set up bundled model path if running as frozen executable
        _setup_bundled_model()
        # Create session to cache the model (176MB download on first run)
        self._session = new_session("u2net")
        self._model_loaded = True

    @property
    def model_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._model_loaded

    def is_supported_format(self, content_type: str) -> bool:
        """Check if the content type is supported."""
        return content_type in self.SUPPORTED_FORMATS

    def remove_background(self, input_path: Path) -> bytes:
        """
        Remove background from an image.

        Args:
            input_path: Path to the input image file.

        Returns:
            PNG image bytes with transparent background.
        """
        with Image.open(input_path) as img:
            # Convert to RGBA if necessary
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Remove background using cached session
            output = remove(img, session=self._session)

            # Save to bytes
            buffer = BytesIO()
            output.save(buffer, format="PNG")
            return buffer.getvalue()

    def remove_background_from_bytes(self, image_bytes: bytes) -> bytes:
        """
        Remove background from image bytes.

        Args:
            image_bytes: Raw image bytes.

        Returns:
            PNG image bytes with transparent background.
        """
        input_buffer = BytesIO(image_bytes)
        with Image.open(input_buffer) as img:
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            output = remove(img, session=self._session)

            buffer = BytesIO()
            output.save(buffer, format="PNG")
            return buffer.getvalue()
