# Deployment Guide - Artera Storage API

## Important: Data Persistence

### Artera Folder Persistence

**CRITICAL**: The `artera` folder and all its contents are **NEVER deleted** during application startup or redeployment.

- The application only creates the `artera` directory if it doesn't exist
- Existing files and folders are **always preserved**
- Default folders (`logo`, `potentials`) are only created if they don't exist
- All user-uploaded files and folders remain intact across redeployments

### How It Works

1. **On First Deployment**:
   - Creates `artera` directory
   - Creates default folders: `logo`, `potentials`

2. **On Redeployment**:
   - Checks if `artera` directory exists (preserves it if it does)
   - Checks if default folders exist (creates only if missing)
   - **Never deletes or modifies existing content**

### Deployment Checklist

When deploying or redeploying the application:

- ✅ **DO**: Deploy application code and dependencies
- ✅ **DO**: Ensure `artera` folder exists (will be created if missing)
- ✅ **DO**: Preserve the `artera` folder and all its contents
- ❌ **DON'T**: Delete or clear the `artera` folder
- ❌ **DON'T**: Remove existing files or folders during deployment

### File System Structure

```
artera-storage/
├── artera/              # ⚠️ PRESERVE THIS FOLDER - Contains all user data
│   ├── logo/            # Default folder (created if missing)
│   ├── potentials/      # Default folder (created if missing)
│   └── [user files]/    # User-uploaded files and folders
├── main.py
├── routers/
├── schemas/
├── services/
└── static/
```

### Backup Recommendations

Before major deployments or updates:

1. **Backup the `artera` folder**:
   ```bash
   tar -czf artera-backup-$(date +%Y%m%d).tar.gz artera/
   ```

2. **Verify backup**:
   ```bash
   tar -tzf artera-backup-*.tar.gz
   ```

3. **Restore if needed**:
   ```bash
   tar -xzf artera-backup-*.tar.gz
   ```

## 🐳 Docker/Coolify Deployment Guide

### **CRITICAL: Configuring Persistent Volumes**

To ensure the `artera` folder persists across redeployments in Docker/Coolify, you **MUST** configure a persistent volume.

---

### **Option 1: Coolify Deployment (Recommended)**

#### Step 1: Prepare Your Repository

1. Ensure these files are in your repository:
   - `Dockerfile`
   - `docker-compose.yml` (optional, but recommended)
   - `requirements.txt`
   - All application code

#### Step 2: Configure Persistent Volume in Coolify

**CRITICAL**: Configure the volume BEFORE first deployment!

1. **In Coolify Dashboard**:
   - Go to your application settings
   - Navigate to **"Volumes"** or **"Persistent Storage"** section
   - Click **"Add Volume"** or **"Add Persistent Storage"**

2. **Volume Configuration**:
   ```
   Container Path: /app/artera
   Volume Name: artera-storage-data
   Volume Type: Named Volume (recommended)
   ```

3. **Save** the configuration

#### Step 3: Environment Variables in Coolify

Set these environment variables (if not using defaults):

- `BASE_URL`: Your application URL (e.g., `https://your-domain.com`)
- `PORT`: `8975`
- `CORS_ORIGINS`: Your allowed origins (comma-separated, e.g., `https://frontend.com`)

#### Step 4: Deploy

- Click **"Deploy"** or **"Redeploy"**
- The volume will persist data across all redeployments

---

### **Option 2: Docker Compose (Local/Server)**

#### Using docker-compose.yml

1. **Start the application**:
   ```bash
   docker-compose up -d
   ```

2. **The `artera` folder** will be mounted from `./artera` on your host machine
   - All files persist in `./artera` directory
   - Data survives container recreation

3. **To redeploy**:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```
   - The `artera` folder remains untouched!

#### Using Named Volume (Production Recommended)

Edit `docker-compose.yml` to use named volume:

```yaml
volumes:
  - artera-data:/app/artera

volumes:
  artera-data:
    driver: local
```

---

### **Option 3: Manual Docker Run**

```bash
# Create artera directory on host (if it doesn't exist)
mkdir -p ./artera

# Run with volume mount
docker run -d \
  --name artera-storage \
  -p 8975:8975 \
  -v $(pwd)/artera:/app/artera \
  -e BASE_URL=http://localhost:8975 \
  -e PORT=8975 \
  -e CORS_ORIGINS=* \
  --restart unless-stopped \
  your-image-name
```

**Important**: The `-v $(pwd)/artera:/app/artera` flag ensures data persistence!

---

### **How Volume Persistence Works**

1. **Volume Mount**: The `artera` folder is mounted from host/volume to container
2. **Data Location**: Files are stored OUTSIDE the container
3. **Container Recreation**: When container is recreated, volume persists
4. **Redeployment**: New container mounts the same volume with all data intact

### **Verifying Persistence**

After deployment:

1. **Upload a test file** via API or UI
2. **Redeploy the application**
3. **Check if file still exists** - it should!
4. **Check logs** for: `✓ Existing items preserved: X items found`

### **Troubleshooting Docker/Coolify Deployment**

**Issue**: Files disappear after redeployment
- ✅ **Solution**: Ensure persistent volume is configured
- ✅ **Check**: Volume path is `/app/artera` in container
- ✅ **Verify**: Volume exists in Coolify's volume management

**Issue**: Permission errors
- ✅ **Solution**: Check file permissions on volume
- ✅ **Fix**: Ensure volume has correct ownership (usually handled automatically)

**Issue**: Volume not mounting
- ✅ **Solution**: Verify volume configuration in Coolify
- ✅ **Check**: Container path must be exactly `/app/artera`
- ✅ **Verify**: Volume name is correct

**Issue**: Data in wrong location
- ✅ **Check**: Volume mount path matches `/app/artera`
- ✅ **Verify**: Application logs show correct artera path

---

### **Backup Strategy for Docker**

#### Backup Volume Data

```bash
# If using bind mount (./artera)
tar -czf artera-backup-$(date +%Y%m%d).tar.gz ./artera/

# If using named volume
docker run --rm \
  -v artera-storage_artera-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/artera-backup-$(date +%Y%m%d).tar.gz -C /data .
```

#### Restore Volume Data

```bash
# Restore from backup
tar -xzf artera-backup-YYYYMMDD.tar.gz -C ./artera/
```

### Environment Variables

The application uses environment variables from `.env`:

- `BASE_URL`: API base URL (default: http://localhost:8975)
- `PORT`: Server port (default: 8975)
- `CORS_ORIGINS`: CORS allowed origins (default: *)

### Startup Logs

On application startup, you'll see:

```
✓ Default folder created: logo (or already exists)
✓ Default folder created: potentials (or already exists)
✓ Artera root directory initialized at: /path/to/artera
✓ Existing items preserved: X items found
⚠ IMPORTANT: All files and folders in artera directory persist across redeployments
```

### Troubleshooting

**Issue**: Files are missing after redeployment
- **Check**: Ensure `artera` folder wasn't deleted during deployment
- **Check**: Verify file paths are correct
- **Solution**: Restore from backup if available

**Issue**: Default folders missing
- **Check**: Application logs for startup messages
- **Solution**: Default folders are created automatically if missing

### Security Notes

- The `artera` folder is excluded from git (see `.gitignore`)
- All operations are restricted to the `artera` directory
- Path traversal attacks are prevented
- File permissions should be set appropriately for your deployment environment

