"""
Router for folder management operations.
"""
from fastapi import APIRouter, HTTPException, status
from schemas.filesystem import CreateFolderRequest, DeleteFolderRequest, MessageResponse
from services.filesystem_service import FilesystemService

router = APIRouter()
filesystem_service = FilesystemService()


@router.post("/create", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(request: CreateFolderRequest):
    """
    Create a folder at the specified relative path inside artera.
    
    - Creates intermediate directories if they don't exist
    - If folder already exists, returns success (idempotent operation)
    - Supports nested folder creation in a single request
    
    Example:
        {
            "path": "projects/project1/assets/images"
        }
    """
    try:
        created_path = filesystem_service.create_folder(request.path)
        relative_path = created_path.relative_to(filesystem_service.get_artera_root())
        
        return MessageResponse(
            message=f"Folder created successfully: {relative_path}",
            path=str(relative_path).replace("\\", "/")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.delete("/delete", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_folder(request: DeleteFolderRequest):
    """
    Delete a folder at the specified relative path inside artera.
    
    - Validates that the path exists and is a folder
    - Recursively deletes folder and all its contents
    - Returns 404 if folder doesn't exist
    
    Example:
        {
            "path": "projects/project1/assets/images"
        }
    """
    try:
        filesystem_service.delete_folder(request.path, recursive=True)
        
        return MessageResponse(
            message=f"Folder deleted successfully: {request.path}",
            path=request.path
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

