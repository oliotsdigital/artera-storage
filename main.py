"""
FastAPI application for managing files and folders within the 'artera' root directory.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv

from routers import files, folders

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
BASE_URL = os.getenv("BASE_URL", "http://localhost:8975")
PORT = int(os.getenv("PORT", "8975"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") != "*" else ["*"]

# Initialize FastAPI app
app = FastAPI(
    title="Artera Storage API",
    description="API for managing files and folders within the artera directory",
    version="1.0.0"
)

# Add CORS middleware (optional, useful for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Configured from .env file
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(folders.router, prefix="/api/folders", tags=["folders"])
app.include_router(files.router, prefix="/api/files", tags=["files"])

# Mount static files directory
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
async def startup_event():
    """
    Initialize the artera root directory on application startup.
    
    IMPORTANT: This function only creates directories if they don't exist.
    Existing files and folders in the artera directory are NEVER deleted or modified.
    The artera folder and all its contents persist across redeployments.
    
    - Creates the artera directory if it doesn't exist
    - Creates default folders (logo, potentials) if they don't exist
    - Preserves all existing files and folders
    """
    artera_root = Path(__file__).parent / "artera"
    
    # Create artera root directory if it doesn't exist (preserves existing content)
    artera_root.mkdir(exist_ok=True)
    
    # Create default folders only if they don't exist (preserves existing content)
    default_folders = ["logo", "potentials"]
    for folder_name in default_folders:
        folder_path = artera_root / folder_name
        if not folder_path.exists():
            folder_path.mkdir(exist_ok=True)
            print(f"✓ Default folder created: {folder_name}")
        else:
            print(f"✓ Default folder already exists: {folder_name} (preserved)")
    
    # Count existing items to show preservation status
    existing_items_count = len(list(artera_root.iterdir())) if artera_root.exists() else 0
    
    print(f"✓ Artera root directory initialized at: {artera_root.absolute()}")
    print(f"✓ Existing items preserved: {existing_items_count} items found")
    print("⚠ IMPORTANT: All files and folders in artera directory persist across redeployments")


@app.get("/")
async def root():
    """Serve the HTML UI."""
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {
        "message": "Artera Storage API",
        "status": "running",
        "version": "1.0.0",
        "base_url": BASE_URL
    }


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "message": "Artera Storage API",
        "status": "running",
        "version": "1.0.0",
        "base_url": BASE_URL
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    artera_root = Path(__file__).parent / "artera"
    return {
        "status": "healthy",
        "artera_root_exists": artera_root.exists(),
        "artera_root_path": str(artera_root.absolute())
    }

