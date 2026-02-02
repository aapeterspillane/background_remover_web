"""API endpoint tests."""

import pytest


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    async def test_health_check(self, client):
        """Test that health endpoint returns ok status."""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "model_loaded" in data


class TestProcessEndpoint:
    """Tests for the image processing endpoint."""

    async def test_process_png_image(self, client, sample_image_bytes):
        """Test processing a PNG image."""
        response = await client.post(
            "/api/process",
            files={"file": ("test.png", sample_image_bytes, "image/png")},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert len(response.content) > 0

    async def test_process_jpeg_image(self, client, sample_jpeg_bytes):
        """Test processing a JPEG image."""
        response = await client.post(
            "/api/process",
            files={"file": ("test.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    async def test_unsupported_format(self, client):
        """Test that unsupported formats are rejected."""
        response = await client.post(
            "/api/process",
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )
        assert response.status_code == 400
        assert "Unsupported format" in response.json()["detail"]

    async def test_missing_file(self, client):
        """Test that missing file returns an error."""
        response = await client.post("/api/process")
        assert response.status_code == 422  # Validation error


class TestStaticFiles:
    """Tests for static file serving."""

    async def test_index_html(self, client):
        """Test that the root serves index.html."""
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Background Remover" in response.text

    async def test_css_file(self, client):
        """Test that CSS files are served."""
        response = await client.get("/css/styles.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

    async def test_js_file(self, client):
        """Test that JS files are served."""
        response = await client.get("/js/app.js")
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]
