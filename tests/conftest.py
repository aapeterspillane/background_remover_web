"""Pytest configuration and fixtures."""

import io
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from backend.main import app
from backend.image_processor import ImageProcessor
from backend.routes import process


@pytest.fixture(scope="session")
def image_processor():
    """Create a shared image processor for all tests."""
    return ImageProcessor()


@pytest.fixture
async def client(image_processor):
    """Create an async test client."""
    # Set the processor before tests
    process.set_processor(image_processor)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_image_bytes():
    """Create a sample image for testing."""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def sample_jpeg_bytes():
    """Create a sample JPEG image for testing."""
    img = Image.new("RGB", (100, 100), color="blue")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def large_image_bytes():
    """Create an image that exceeds the size limit (simulated)."""
    # Create a small image but we'll use it to test validation
    img = Image.new("RGB", (100, 100), color="green")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
