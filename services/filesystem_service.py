"""
Filesystem service for secure file and folder operations.
Handles path validation and prevents path traversal attacks.
"""
import os
from pathlib import Path
from typing import List, Optional
from fastapi import HTTPException, status
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FilesystemService:
    """Service class for filesystem operations with security checks."""
    
    def __init__(self, root_dir: Optional[str] = None):
        """
        Initialize the filesystem service.
        
        Args:
            root_dir: Name of the root directory to manage. If None, reads from STORAGE_ROOT env var (default: 'artera')
        """
        # Get root directory name from parameter or environment variable
        if root_dir is None:
            root_dir = os.getenv("STORAGE_ROOT", "artera")
        
        self.project_root = Path(__file__).parent.parent
        self.storage_root = self.project_root / root_dir
        self.root_dir_name = root_dir
        self._ensure_storage_root()
    
    def _ensure_storage_root(self):
        """Ensure the storage root directory exists."""
        self.storage_root.mkdir(exist_ok=True)
    
    def _validate_path(self, relative_path: str) -> Path:
        """
        Validate and resolve a relative path, preventing path traversal attacks.
        
        Args:
            relative_path: Relative path string from user input
            
        Returns:
            Resolved Path object within artera root
            
        Raises:
            HTTPException: If path traversal is detected or path is invalid
        """
        if not relative_path or relative_path.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Path cannot be empty"
            )
        
        # Normalize the path and resolve it
        # Remove leading/trailing slashes and normalize separators
        normalized = relative_path.strip().strip("/").strip("\\")
        
        # Check for path traversal attempts
        if ".." in normalized or normalized.startswith("/") or ":" in normalized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Path traversal detected. Relative paths only."
            )
        
        # Resolve the full path
        full_path = (self.storage_root / normalized).resolve()
        
        # Ensure the resolved path is still within storage root
        try:
            full_path.relative_to(self.storage_root.resolve())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid path: path traversal detected"
            )
        
        return full_path
    
    def create_folder(self, relative_path: str) -> Path:
        """
        Create a folder at the given relative path.
        Creates intermediate directories if they don't exist.
        
        Args:
            relative_path: Relative path inside artera directory
            
        Returns:
            Path object of the created folder
            
        Raises:
            HTTPException: If path validation fails
        """
        full_path = self._validate_path(relative_path)
        
        # Create directory (and parents if needed)
        try:
            full_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create folder: {str(e)}"
            )
        
        return full_path
    
    def delete_folder(self, relative_path: str, recursive: bool = True) -> None:
        """
        Delete a folder at the given relative path.
        
        Args:
            relative_path: Relative path inside artera directory
            recursive: If True, delete folder and all contents. If False, only delete if empty.
            
        Raises:
            HTTPException: If path doesn't exist, is invalid, or deletion fails
        """
        full_path = self._validate_path(relative_path)
        
        if not full_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Folder not found: {relative_path}"
            )
        
        if not full_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path is not a folder: {relative_path}"
            )
        
        try:
            if recursive:
                shutil.rmtree(full_path)
            else:
                full_path.rmdir()  # Only works if folder is empty
        except OSError as e:
            if not recursive:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Folder is not empty. Use recursive delete or remove contents first: {str(e)}"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete folder: {str(e)}"
            )
    
    def upload_file(self, file_content: bytes, relative_folder_path: str, filename: str, overwrite: bool = True) -> Path:
        """
        Upload a file to the specified folder path.
        
        Args:
            file_content: Binary content of the file
            relative_folder_path: Relative path to the target folder inside artera
            filename: Name of the file to save
            overwrite: If True, overwrite existing file. If False, raise error on conflict.
            
        Returns:
            Path object of the saved file
            
        Raises:
            HTTPException: If folder doesn't exist, path is invalid, or save fails
        """
        # Validate folder path
        folder_path = self._validate_path(relative_folder_path)
        
        if not folder_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target folder does not exist: {relative_folder_path}"
            )
        
        if not folder_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path is not a folder: {relative_folder_path}"
            )
        
        # Validate filename
        if not filename or filename.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename cannot be empty"
            )
        
        # Prevent path traversal in filename
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename: path traversal detected"
            )
        
        file_path = folder_path / filename
        
        # Check if file exists
        if file_path.exists() and not overwrite:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"File already exists: {file_path.relative_to(self.storage_root)}"
            )
        
        # Write file
        try:
            file_path.write_bytes(file_content)
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        return file_path
    
    def delete_file(self, relative_file_path: str) -> None:
        """
        Delete a file at the given relative path.
        
        Args:
            relative_file_path: Relative path to the file inside artera
            
        Raises:
            HTTPException: If file doesn't exist or path is invalid
        """
        full_path = self._validate_path(relative_file_path)
        
        if not full_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {relative_file_path}"
            )
        
        if not full_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path is not a file: {relative_file_path}"
            )
        
        try:
            full_path.unlink()
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    def list_items(self, relative_path: Optional[str] = None, recursive: bool = True) -> List[dict]:
        """
        List all files and folders inside storage root.
        
        Args:
            relative_path: Optional relative path to list from (default: storage root)
            recursive: If True, return nested structure. If False, return only direct children.
            
        Returns:
            List of dictionaries with file/folder information
        """
        if relative_path:
            base_path = self._validate_path(relative_path)
            if not base_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Path not found: {relative_path}"
                )
            if not base_path.is_dir():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Path is not a folder: {relative_path}"
                )
        else:
            base_path = self.storage_root
        
        items = []
        
        if recursive:
            # Recursive listing: walk through all directories
            for item_path in base_path.rglob("*"):
                if item_path == base_path:
                    continue
                
                relative_item_path = item_path.relative_to(self.storage_root)
                
                items.append({
                    "name": item_path.name,
                    "type": "folder" if item_path.is_dir() else "file",
                    "relative_path": str(relative_item_path).replace("\\", "/"),
                    "size": item_path.stat().st_size if item_path.is_file() else None
                })
        else:
            # Non-recursive: only direct children
            for item_path in base_path.iterdir():
                relative_item_path = item_path.relative_to(self.storage_root)
                
                items.append({
                    "name": item_path.name,
                    "type": "folder" if item_path.is_dir() else "file",
                    "relative_path": str(relative_item_path).replace("\\", "/"),
                    "size": item_path.stat().st_size if item_path.is_file() else None
                })
        
        # Sort: folders first, then files, both alphabetically
        items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
        
        return items
    
    def get_tree(self, relative_path: Optional[str] = None) -> dict:
        """
        Build a nested tree structure of all files and folders.
        
        Args:
            relative_path: Optional relative path to build tree from (default: storage root)
            
        Returns:
            Dictionary with tree structure containing root nodes, total_files, and total_folders
        """
        if relative_path:
            base_path = self._validate_path(relative_path)
            if not base_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Path not found: {relative_path}"
                )
            if not base_path.is_dir():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Path is not a folder: {relative_path}"
                )
        else:
            base_path = self.storage_root
        
        # Get all items recursively
        items = []
        for item_path in base_path.rglob("*"):
            if item_path == base_path:
                continue
            
            relative_item_path = item_path.relative_to(self.storage_root)
            
            items.append({
                "name": item_path.name,
                "type": "folder" if item_path.is_dir() else "file",
                "relative_path": str(relative_item_path).replace("\\", "/"),
                "size": item_path.stat().st_size if item_path.is_file() else None,
                "parts": str(relative_item_path).replace("\\", "/").split("/")
            })
        
        # Build tree structure
        tree_map = {}
        root_nodes = []
        
        # Sort items by path depth (shallow first) and then alphabetically
        items.sort(key=lambda x: (len(x["parts"]), x["name"].lower()))
        
        for item in items:
            path_parts = item["parts"]
            depth = len(path_parts) - 1
            
            if depth == 0:
                # Root level item
                node = {
                    "name": item["name"],
                    "type": item["type"],
                    "relative_path": item["relative_path"],
                    "size": item["size"],
                    "children": [] if item["type"] == "folder" else None
                }
                tree_map[item["relative_path"]] = node
                root_nodes.append(node)
            else:
                # Child item - find parent
                parent_path = "/".join(path_parts[:-1])
                parent_node = tree_map.get(parent_path)
                
                if parent_node:
                    # Add to parent's children
                    if parent_node["children"] is None:
                        parent_node["children"] = []
                    
                    node = {
                        "name": item["name"],
                        "type": item["type"],
                        "relative_path": item["relative_path"],
                        "size": item["size"],
                        "children": [] if item["type"] == "folder" else None
                    }
                    parent_node["children"].append(node)
                    tree_map[item["relative_path"]] = node
                else:
                    # Parent not found, add as root (shouldn't happen with sorted items)
                    node = {
                        "name": item["name"],
                        "type": item["type"],
                        "relative_path": item["relative_path"],
                        "size": item["size"],
                        "children": [] if item["type"] == "folder" else None
                    }
                    tree_map[item["relative_path"]] = node
                    root_nodes.append(node)
        
        # Sort children: folders first, then files, both alphabetically
        def sort_children(node):
            if node["children"]:
                node["children"].sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
                for child in node["children"]:
                    if child["type"] == "folder":
                        sort_children(child)
        
        for root_node in root_nodes:
            sort_children(root_node)
        
        root_nodes.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
        
        # Count totals
        total_files = sum(1 for item in items if item["type"] == "file")
        total_folders = sum(1 for item in items if item["type"] == "folder")
        
        return {
            "tree": root_nodes,
            "total_files": total_files,
            "total_folders": total_folders
        }
    
    def get_storage_root(self) -> Path:
        """Get the storage root directory path."""
        return self.storage_root
    
    def get_artera_root(self) -> Path:
        """Get the storage root directory path (deprecated, use get_storage_root)."""
        return self.storage_root

