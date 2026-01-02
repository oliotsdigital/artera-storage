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

# Initialize FastAPI app with enhanced OpenAPI documentation
app = FastAPI(
    title="Artera Storage API",
    description="""
    ## Artera Storage API
    
    A secure FastAPI application for managing files and folders within the `artera` root directory.
    
    ### Features
    
    * 📁 **Folder Management**: Create and delete folders with nested directory support
    * 📄 **File Management**: Upload, delete, and list files
    * 🔒 **Security**: Path traversal protection, input validation
    * 🌳 **Tree Structure**: Get hierarchical tree view of all files and folders
    * 🎨 **Web UI**: Built-in HTML interface for browsing files
    
    ### Security
    
    * All operations are restricted to the `artera` directory
    * Path traversal attacks are prevented (`../` blocked)
    * Input validation using Pydantic models
    * Proper HTTP status codes for all operations
    
    ### Data Persistence
    
    * The `artera` folder and all contents persist across redeployments
    * Default folders (`logo`, `potentials`) are created automatically
    * All user data is preserved during application updates
    
    ### API Documentation
    
    * **Swagger UI**: Available at `/docs`
    * **ReDoc**: Available at `/redoc`
    * **OpenAPI JSON**: Available at `/openapi.json`
    """,
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Artera Storage API Support",
        "url": "https://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": BASE_URL,
            "description": "Server configured via BASE_URL environment variable"
        },
    ],
    tags_metadata=[
        {
            "name": "folders",
            "description": "Operations for managing folders. Create and delete folders with nested directory support.",
        },
        {
            "name": "files",
            "description": "Operations for managing files. Upload, delete, list files, and get tree structure.",
        },
        {
            "name": "utilities",
            "description": "Utility endpoints for health checks and API information.",
        },
    ],
)

# Add CORS middleware (optional, useful for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Configured from .env file
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with tags for Swagger documentation
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


@app.get(
    "/",
    response_class=HTMLResponse,
    tags=["utilities"],
    summary="Web UI",
    description="Serves the HTML web interface for browsing files and folders."
)
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


@app.get(
    "/api",
    tags=["utilities"],
    summary="API Information",
    description="Returns API information including version, status, and base URL.",
    response_description="API information and status"
)
async def api_info():
    """API information endpoint."""
    return {
        "message": "Artera Storage API",
        "status": "running",
        "version": "1.0.0",
        "base_url": BASE_URL
    }


@app.get(
    "/health",
    tags=["utilities"],
    summary="Health Check",
    description="Returns the health status of the API and artera directory information.",
    response_description="Health status and artera root directory information"
)
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

