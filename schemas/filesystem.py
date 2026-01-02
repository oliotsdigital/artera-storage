"""
Pydantic schemas for filesystem operations.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class TreeNode(BaseModel):
    """Schema for tree node representing files and folders in a nested structure."""
    name: str = Field(..., description="Name of the file or folder")
    type: Literal["file", "folder"] = Field(..., description="Type of the item")
    relative_path: str = Field(..., description="Relative path from artera root")
    size: Optional[int] = Field(None, description="File size in bytes (None for folders)")
    children: Optional[List["TreeNode"]] = Field(default=None, description="Child nodes (only for folders)")


class TreeResponse(BaseModel):
    """Response schema for tree structure."""
    tree: List[TreeNode] = Field(..., description="Root level tree nodes")
    total_files: int = Field(..., description="Total number of files")
    total_folders: int = Field(..., description="Total number of folders")


class CreateFolderRequest(BaseModel):
    """Request schema for creating a folder."""
    path: str = Field(
        ...,
        description="Relative path inside artera directory (e.g., 'projects/project1/assets')",
        min_length=1
    )


class DeleteFolderRequest(BaseModel):
    """Request schema for deleting a folder."""
    path: str = Field(
        ...,
        description="Relative path inside artera directory",
        min_length=1
    )


class FileItem(BaseModel):
    """Schema for file/folder item in listings."""
    name: str = Field(..., description="Name of the file or folder")
    type: Literal["file", "folder"] = Field(..., description="Type of the item")
    relative_path: str = Field(..., description="Relative path from artera root")
    size: Optional[int] = Field(None, description="File size in bytes (None for folders)")


class ListResponse(BaseModel):
    """Response schema for listing files and folders."""
    items: List[FileItem] = Field(..., description="List of files and folders")
    total_count: int = Field(..., description="Total number of items")


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str = Field(..., description="Response message")
    path: Optional[str] = Field(None, description="Path related to the operation")


# Update forward references for recursive TreeNode
TreeNode.model_rebuild()

