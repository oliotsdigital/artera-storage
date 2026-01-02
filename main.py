"""
FastAPI application for managing files and folders within a configurable storage root directory.
The storage folder name is configurable via STORAGE_ROOT environment variable (default: 'artera').
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
STORAGE_ROOT = os.getenv("STORAGE_ROOT", "artera")  # Configurable storage folder name

# Initialize FastAPI app with enhanced OpenAPI documentation
app = FastAPI(
    title="Artera Storage API",
    description=f"""
    ## Artera Storage API
    
    A secure FastAPI application for managing files and folders within a configurable storage root directory.
    
    ### Configuration (Environment Variables)
    
    All configuration is done via environment variables (see `.env` file):
    
    * **BASE_URL**: API base URL - `{BASE_URL}` (used in API docs, responses, web UI)
    * **PORT**: Server port - `{PORT}` (default: 8975)
    * **STORAGE_ROOT**: Storage folder name - `{STORAGE_ROOT}` (default: artera)
    * **CORS_ORIGINS**: Allowed CORS origins (comma-separated or `*` for all)
    * **RELOAD**: Enable auto-reload for development (true/false)
    
    ### Features
    
    * 📁 **Folder Management**: Create and delete folders with nested directory support
    * 📄 **File Management**: Upload, delete, and list files
    * 🔒 **Security**: Path traversal protection, input validation
    * 🌳 **Tree Structure**: Get hierarchical tree view of all files and folders
    * 🎨 **Web UI**: Built-in HTML interface for browsing files
    
    ### Security
    
    * All operations are restricted to the storage root directory (`{STORAGE_ROOT}`)
    * Path traversal attacks are prevented (`../` blocked)
    * Input validation using Pydantic models
    * Proper HTTP status codes for all operations
    
    ### Data Persistence
    
    * The storage folder (`{STORAGE_ROOT}`) and all contents persist across redeployments
    * Default folders (`logo`, `potentials`) are created automatically
    * All user data is preserved during application updates
    
    ### API Documentation
    
    * **Swagger UI**: Available at `{BASE_URL}/docs`
    * **ReDoc**: Available at `{BASE_URL}/redoc`
    * **OpenAPI JSON**: Available at `{BASE_URL}/openapi.json`
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


def custom_openapi():
    """Customize OpenAPI schema to include environment variable information."""
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add environment variable information to the schema
    openapi_schema["info"]["x-environment-variables"] = {
        "BASE_URL": {
            "description": "API base URL used in documentation, responses, and web UI",
            "default": "http://localhost:8975",
            "current": BASE_URL
        },
        "PORT": {
            "description": "Server port number",
            "default": "8975",
            "current": str(PORT)
        },
        "STORAGE_ROOT": {
            "description": "Storage folder name where all files are stored",
            "default": "artera",
            "current": STORAGE_ROOT
        },
        "CORS_ORIGINS": {
            "description": "CORS allowed origins (comma-separated or * for all)",
            "default": "*",
            "current": ",".join(CORS_ORIGINS) if isinstance(CORS_ORIGINS, list) else str(CORS_ORIGINS)
        },
        "RELOAD": {
            "description": "Enable auto-reload for development",
            "default": "true",
            "current": os.getenv("RELOAD", "true")
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
async def startup_event():
    """
    Initialize the storage root directory on application startup.
    
    IMPORTANT: This function only creates directories if they don't exist.
    Existing files and folders in the storage directory are NEVER deleted or modified.
    The storage folder and all its contents persist across redeployments.
    
    - Creates the storage directory if it doesn't exist (name from STORAGE_ROOT env var)
    - Creates default folders (logo, potentials) if they don't exist
    - Preserves all existing files and folders
    """
    storage_root = Path(__file__).parent / STORAGE_ROOT
    
    # Create storage root directory if it doesn't exist (preserves existing content)
    storage_root.mkdir(exist_ok=True)
    
    # Create default folders only if they don't exist (preserves existing content)
    default_folders = ["logo", "potentials"]
    for folder_name in default_folders:
        folder_path = storage_root / folder_name
        if not folder_path.exists():
            folder_path.mkdir(exist_ok=True)
            print(f"✓ Default folder created: {folder_name}")
        else:
            print(f"✓ Default folder already exists: {folder_name} (preserved)")
    
    # Count existing items to show preservation status
    existing_items_count = len(list(storage_root.iterdir())) if storage_root.exists() else 0
    
    print(f"✓ Storage root directory initialized at: {storage_root.absolute()}")
    print(f"✓ Storage folder name: {STORAGE_ROOT}")
    print(f"✓ Existing items preserved: {existing_items_count} items found")
    print(f"⚠ IMPORTANT: All files and folders in {STORAGE_ROOT} directory persist across redeployments")


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
    description=f"""
    Returns API information including version, status, base URL, and configuration.
    
    **Configuration:**
    - Base URL: `{BASE_URL}` (from BASE_URL env var)
    - Port: `{PORT}` (from PORT env var)
    - Storage Root: `{STORAGE_ROOT}` (from STORAGE_ROOT env var)
    """,
    response_description="API information, status, and configuration"
)
async def api_info():
    """
    API information endpoint.
    Returns current configuration from environment variables.
    """
    return {
        "message": "Artera Storage API",
        "status": "running",
        "version": "1.0.0",
        "base_url": BASE_URL,
        "port": PORT,
        "storage_root": STORAGE_ROOT,
        "configuration": {
            "base_url": BASE_URL,
            "port": PORT,
            "storage_root": STORAGE_ROOT,
            "cors_enabled": CORS_ORIGINS != ["*"] if isinstance(CORS_ORIGINS, list) else CORS_ORIGINS == "*"
        }
    }


@app.get(
    "/health",
    tags=["utilities"],
    summary="Health Check",
    description=f"""
    Returns the health status of the API and storage directory information.
    
    **Configuration:**
    - Storage folder name: `{STORAGE_ROOT}` (from STORAGE_ROOT env var)
    - Base URL: `{BASE_URL}` (from BASE_URL env var)
    """,
    response_description="Health status, storage root directory information, and configuration"
)
async def health_check():
    """
    Health check endpoint.
    Returns health status and current configuration from environment variables.
    """
    storage_root = Path(__file__).parent / STORAGE_ROOT
    return {
        "status": "healthy",
        "base_url": BASE_URL,
        "port": PORT,
        "storage_root": STORAGE_ROOT,
        "storage_root_exists": storage_root.exists(),
        "storage_root_path": str(storage_root.absolute()),
        "configuration": {
            "base_url": BASE_URL,
            "port": PORT,
            "storage_root": STORAGE_ROOT
        }
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

