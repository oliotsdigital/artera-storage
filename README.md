# Artera Storage API

A FastAPI application for managing files and folders within a secure root directory named `artera`.

## Features

- **Folder Management**: Create and delete folders with nested directory support
- **File Management**: Upload, delete, and list files
- **Security**: Path traversal protection, input validation
- **RESTful API**: Clean endpoints with proper HTTP status codes
- **Auto-initialization**: Creates `artera` directory on startup

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application (choose one method):

**Method 1: Using Python command**
```bash
python main.py
```

**Method 2: Using uvicorn command**
```bash
uvicorn main:app --reload --port 8975
```

Both methods will:
- Load configuration from `.env` file (copy `.env.example` to `.env` and configure)
- Use the `BASE_URL` from `.env` (default: http://localhost:8975)
- Use the `PORT` from `.env` (default: 8975)
- Start the API server

**Configuration:**
1. Copy `.env.example` to `.env`
2. Update `BASE_URL` with your deployment URL (e.g., `https://your-domain.com`)
3. Adjust other variables as needed

The API will be available at the `BASE_URL` specified in `.env` (default: `http://localhost:8975`)

API documentation (Swagger UI) will be available at `{BASE_URL}/docs`

## API Endpoints

### Folder Management

#### Create Folder
- **POST** `/api/folders/create`
- **Request Body**:
  ```json
  {
    "path": "projects/project1/assets/images"
  }
  ```
- **Response**: 201 Created
- **Behavior**: Creates nested folders if they don't exist. Idempotent (returns success if folder already exists).

#### Delete Folder
- **DELETE** `/api/folders/delete`
- **Request Body**:
  ```json
  {
    "path": "projects/project1/assets/images"
  }
  ```
- **Response**: 200 OK
- **Behavior**: Recursively deletes folder and all contents.

### File Management

#### Upload File
- **POST** `/api/files/upload`
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file`: The file to upload
  - `folder_path`: Target folder path (e.g., `projects/project1/docs`)
  - `overwrite`: Boolean (default: `true`) - Whether to overwrite existing files
- **Response**: 201 Created
- **Behavior**: 
  - Target folder must exist (does not auto-create)
  - Overwrites existing files by default
  - Returns 404 if folder doesn't exist
  - Returns 409 if file exists and `overwrite=false`

#### Delete File
- **DELETE** `/api/files/delete?file_path=projects/project1/docs/document.pdf`
- **Query Parameter**: `file_path` - Relative path to the file
- **Response**: 200 OK
- **Behavior**: Validates file exists and is a file (not a folder).

#### List Files and Folders
- **GET** `/api/files/list`
- **Query Parameters**:
  - `path` (optional): Relative path to list from (default: artera root)
  - `recursive` (optional): Boolean (default: `true`) - Return nested structure or only direct children
- **Response**: 200 OK
- **Example**:
  ```
  GET /api/files/list
  GET /api/files/list?path=projects/project1
  GET /api/files/list?path=projects/project1&recursive=false
  ```
- **Response Format**:
  ```json
  {
    "items": [
      {
        "name": "project1",
        "type": "folder",
        "relative_path": "projects/project1",
        "size": null
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
  ```

### Health Check

#### Root
- **GET** `/`
- Returns API information

#### Health Check
- **GET** `/health`
- Returns health status and artera root path

## Security Features

- **Path Traversal Protection**: All paths are validated to prevent `../` attacks
- **Path Validation**: Ensures all operations stay within the `artera` directory
- **Input Validation**: Pydantic models validate all inputs
- **Error Handling**: Proper HTTP status codes and error messages

## Project Structure

```
artera-storage/
├── artera/              # Managed storage directory (auto-created)
├── main.py              # FastAPI app entry point
├── routers/
│   ├── __init__.py
│   ├── files.py         # File management endpoints
│   └── folders.py       # Folder management endpoints
├── schemas/
│   ├── __init__.py
│   └── filesystem.py    # Pydantic models
├── services/
│   ├── __init__.py
│   └── filesystem_service.py  # Core filesystem operations
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## HTTP Status Codes

- **200 OK**: Successful operation
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid input or path traversal detected
- **404 Not Found**: File or folder doesn't exist
- **409 Conflict**: Resource conflict (e.g., file exists when overwrite=false)
- **500 Internal Server Error**: Unexpected server error

## Notes

- All file and folder operations are restricted to the `artera` directory
- The `artera` directory is automatically created on application startup
- Folder deletion is recursive by default (deletes all contents)
- File uploads overwrite existing files by default
- The list endpoint returns folders first, then files (both alphabetically sorted)

