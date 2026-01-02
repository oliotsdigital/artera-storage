"""
FastAPI application for managing files and folders within the 'artera' root directory.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the HTML UI with BASE_URL injected from .env."""
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        # Read HTML file and inject BASE_URL
        html_content = html_file.read_text(encoding='utf-8')
        # Replace the API_BASE constant with BASE_URL from .env
        html_content = html_content.replace(
            'const API_BASE = window.location.origin;',
            f'const API_BASE = "{BASE_URL}";'
        )
        return HTMLResponse(content=html_content)
    return HTMLResponse(content=f"""
    <html>
        <body>
            <h1>Artera Storage API</h1>
            <p>Status: running</p>
            <p>Version: 1.0.0</p>
            <p>Base URL: {BASE_URL}</p>
            <p><a href="/docs">API Documentation</a></p>
        </body>
    </html>
    """)


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
        "base_url": BASE_URL,
        "artera_root_exists": artera_root.exists(),
        "artera_root_path": str(artera_root.absolute())
    }


if __name__ == "__main__":
    """
    Allow running the application directly with: python main.py
    
    This enables both:
    1. uvicorn main:app --reload --port 8975
    2. python main.py
    """
    import uvicorn
    
    # Check if reload should be enabled (default: True for development)
    reload_enabled = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 Starting Artera Storage API on {BASE_URL}")
    print(f"📝 Port: {PORT}")
    print(f"🔄 Auto-reload: {'enabled' if reload_enabled else 'disabled'}")
    print(f"📚 API Docs: {BASE_URL}/docs")
    print(f"🌐 Web UI: {BASE_URL}/")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=reload_enabled
    )

