"""
Router for file management operations.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, status
from typing import Optional
from schemas.filesystem import MessageResponse, ListResponse, FileItem, TreeResponse, TreeNode
from services.filesystem_service import FilesystemService

router = APIRouter()
filesystem_service = FilesystemService()


@router.post(
    "/upload",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload File",
    description="""
    Upload a file to the specified folder path inside the storage root directory.
    
    **Storage Location:**
    - Files are stored in the storage root directory (configurable via STORAGE_ROOT env var)
    - Default storage folder: `artera` (can be changed via STORAGE_ROOT environment variable)
    
    **Features:**
    - Accepts multipart/form-data with file and folder_path
    - Target folder must exist (does not auto-create)
    - By default, overwrites existing files with the same name
    - Supports multiple file types (no MIME type restrictions)
    - Path traversal protection (../ is blocked in filename)
    
    **Form Fields:**
    - `file`: The file to upload (required)
    - `folder_path`: Target folder path inside storage root (required)
    - `overwrite`: Whether to overwrite existing file (default: true)
    
    **Example:**
    ```
    file: document.pdf
    folder_path: projects/project1/docs
    overwrite: true
    ```
    """,
    responses={
        201: {
            "description": "File uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "File uploaded successfully: document.pdf",
                        "path": "projects/project1/docs/document.pdf"
                    }
                }
            }
        },
        400: {"description": "Invalid folder path or filename"},
        404: {"description": "Target folder does not exist"},
        409: {"description": "File already exists and overwrite=false"},
        500: {"description": "Internal server error"}
    }
)
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    folder_path: str = Form(..., description="Target folder path inside storage root (e.g., 'projects/project1/docs')"),
    overwrite: bool = Form(True, description="Overwrite existing file if it exists")
):
    """
    Upload a file to the specified folder path inside storage root (configurable via STORAGE_ROOT env var).
    
    - Accepts multipart/form-data with file and folder_path
    - Target folder must exist (does not auto-create)
    - By default, overwrites existing files with the same name
    - Supports multiple file types (no MIME type restrictions)
    - Returns 404 if target folder doesn't exist
    - Returns 409 if file exists and overwrite=False
    
    Example form data:
        file: [binary file data]
        folder_path: "projects/project1/assets"
        overwrite: true
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload file
        saved_path = filesystem_service.upload_file(
            file_content=file_content,
            relative_folder_path=folder_path,
            filename=file.filename,
            overwrite=overwrite
        )
        
        relative_path = saved_path.relative_to(filesystem_service.get_storage_root())
        
        return MessageResponse(
            message=f"File uploaded successfully: {file.filename}",
            path=str(relative_path).replace("\\", "/")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.delete(
    "/delete",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete File",
    description="""
    Delete a file at the specified relative path inside the storage root directory.
    
    **Storage Location:**
    - Files are stored in the storage root directory (configurable via STORAGE_ROOT env var)
    
    **Features:**
    - Validates that the path exists and is a file
    - Path traversal protection (../ is blocked)
    - Returns 404 if file doesn't exist
    - Returns 400 if path is not a file
    
    **Query Parameters:**
    - `file_path`: Relative path to the file inside artera (required)
    
    **Example:**
    ```
    DELETE /api/files/delete?file_path=projects/project1/docs/document.pdf
    ```
    """,
    responses={
        200: {
            "description": "File deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "File deleted successfully: projects/project1/docs/document.pdf",
                        "path": "projects/project1/docs/document.pdf"
                    }
                }
            }
        },
        400: {"description": "Invalid path or path is not a file"},
        404: {"description": "File not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_file(file_path: str = Query(..., description="Relative path to the file inside storage root")):
    """
    Delete a file at the specified relative path inside storage root (configurable via STORAGE_ROOT env var).
    
    - Validates that the path exists and is a file
    - Returns 404 if file doesn't exist
    - Returns 400 if path is not a file
    
    Example query parameter:
        ?file_path=projects/project1/docs/document.pdf
    """
    try:
        filesystem_service.delete_file(file_path)
        
        return MessageResponse(
            message=f"File deleted successfully: {file_path}",
            path=file_path
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/list",
    response_model=ListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Files and Folders",
    description="""
    List all files and folders inside the storage root directory.
    
    **Storage Location:**
    - Files are stored in the storage root directory (configurable via STORAGE_ROOT env var)
    - Default storage folder: `artera` (can be changed via STORAGE_ROOT environment variable)
    
    **Features:**
    - Returns nested directory structure by default (recursive=True)
    - Can list from a specific subdirectory using the path parameter
    - Returns flat list with full relative paths
    - Includes name, type (file/folder), relative_path, and size (for files)
    - Folders are listed first, then files (both alphabetically sorted)
    
    **Query Parameters:**
    - `path`: Optional relative path to list from (default: storage root)
    - `recursive`: If true, return all nested items. If false, return only direct children.
    
    **Examples:**
    ```
    GET /api/files/list
    GET /api/files/list?path=projects/project1
    GET /api/files/list?path=projects/project1&recursive=false
    ```
    """,
    responses={
        200: {
            "description": "List of files and folders",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "name": "logo",
                                "type": "folder",
                                "relative_path": "logo",
                                "size": None
                            },
                            {
                                "name": "document.pdf",
                                "type": "file",
                                "relative_path": "projects/project1/docs/document.pdf",
                                "size": 1024
                            }
                        ],
                        "total_count": 2
                    }
                }
            }
        },
        400: {"description": "Invalid path or path is not a folder"},
        404: {"description": "Path not found"},
        500: {"description": "Internal server error"}
    }
)
async def list_files_and_folders(
    path: Optional[str] = Query(None, description="Optional relative path to list from (default: storage root)"),
    recursive: bool = Query(True, description="If true, return nested structure. If false, return only direct children.")
):
    """
    List all files and folders inside storage root (configurable via STORAGE_ROOT env var).
    
    - Returns nested directory structure by default (recursive=True)
    - Can list from a specific subdirectory using the path parameter
    - Returns flat list with full relative paths
    - Includes name, type (file/folder), relative_path, and size (for files)
    - Folders are listed first, then files (both alphabetically sorted)
    
    Query parameters:
        path: Optional relative path to list from (e.g., "projects/project1")
        recursive: If true, return all nested items. If false, return only direct children.
    
    Example:
        GET /api/files/list
        GET /api/files/list?path=projects/project1
        GET /api/files/list?path=projects/project1&recursive=false
    """
    try:
        items_data = filesystem_service.list_items(relative_path=path, recursive=recursive)
        
        items = [FileItem(**item) for item in items_data]
        
        return ListResponse(
            items=items,
            total_count=len(items)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/tree",
    response_model=TreeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Tree Structure",
    description="""
    Get the full nested tree structure of all files and folders inside the storage root directory.
    
    **Storage Location:**
    - Files are stored in the storage root directory (configurable via STORAGE_ROOT env var)
    - Default storage folder: `artera` (can be changed via STORAGE_ROOT environment variable)
    
    **Features:**
    - Returns a hierarchical tree structure with parent-child relationships
    - Each folder contains its children in a nested structure
    - Folders are listed before files at each level
    - All items are sorted alphabetically within their type
    - Includes total file and folder counts
    
    **Query Parameters:**
    - `path`: Optional relative path to build tree from (default: storage root)
    
    **Examples:**
    ```
    GET /api/files/tree
    GET /api/files/tree?path=projects/project1
    ```
    
    **Response Structure:**
    The response contains a nested tree where each folder has a `children` array containing its files and subfolders.
    """,
    responses={
        200: {
            "description": "Tree structure of files and folders",
            "content": {
                "application/json": {
                    "example": {
                        "tree": [
                            {
                                "name": "logo",
                                "type": "folder",
                                "relative_path": "logo",
                                "size": None,
                                "children": [
                                    {
                                        "name": "image.png",
                                        "type": "file",
                                        "relative_path": "logo/image.png",
                                        "size": 1024,
                                        "children": None
                                    }
                                ]
                            },
                            {
                                "name": "potentials",
                                "type": "folder",
                                "relative_path": "potentials",
                                "size": None,
                                "children": []
                            }
                        ],
                        "total_files": 1,
                        "total_folders": 2
                    }
                }
            }
        },
        400: {"description": "Invalid path or path is not a folder"},
        404: {"description": "Path not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_tree(
    path: Optional[str] = Query(None, description="Optional relative path to build tree from (default: storage root)")
):
    """
    Get the full nested tree structure of all files and folders inside storage root (configurable via STORAGE_ROOT env var).
    
    - Returns a hierarchical tree structure with parent-child relationships
    - Each folder contains its children in a nested structure
    - Folders are listed before files at each level
    - All items are sorted alphabetically within their type
    - Includes total file and folder counts
    
    Query parameters:
        path: Optional relative path to build tree from (e.g., "projects/project1")
    
    Example:
        GET /api/files/tree
        GET /api/files/tree?path=projects/project1
    
    Response structure:
        {
            "tree": [
                {
                    "name": "logo",
                    "type": "folder",
                    "relative_path": "logo",
                    "size": null,
                    "children": [
                        {
                            "name": "image.png",
                            "type": "file",
                            "relative_path": "logo/image.png",
                            "size": 1024,
                            "children": null
                        }
                    ]
                }
            ],
            "total_files": 1,
            "total_folders": 1
        }
    """
    try:
        tree_data = filesystem_service.get_tree(relative_path=path)
        
        # Convert tree nodes to TreeNode models recursively
        def build_tree_nodes(nodes):
            result = []
            for node in nodes:
                tree_node = TreeNode(
                    name=node["name"],
                    type=node["type"],
                    relative_path=node["relative_path"],
                    size=node["size"],
                    children=build_tree_nodes(node["children"]) if node.get("children") else None
                )
                result.append(tree_node)
            return result
        
        tree_nodes = build_tree_nodes(tree_data["tree"])
        
        return TreeResponse(
            tree=tree_nodes,
            total_files=tree_data["total_files"],
            total_folders=tree_data["total_folders"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

