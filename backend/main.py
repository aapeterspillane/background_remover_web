"""FastAPI application for background removal."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.image_processor import ImageProcessor
from backend.routes import process


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - initialize processor on startup."""
    # Initialize the image processor (loads the model)
    image_processor = ImageProcessor()
    process.set_processor(image_processor)
    yield
    # Cleanup if needed


app = FastAPI(
    title="Background Remover",
    description="Remove backgrounds from images using AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(process.router)

# Get the frontend directory path
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


# Mount static files
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse(FRONTEND_DIR / "index.html")
