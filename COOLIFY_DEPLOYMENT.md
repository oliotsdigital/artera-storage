# 🚀 Coolify Deployment Quick Guide

## ⚠️ CRITICAL: Data Persistence Setup

**IMPORTANT**: Follow these steps BEFORE your first deployment to ensure data persists across redeployments!

---

## 🎯 Quick Answer: How to Add Artera Folder to Persistent Storage

**TL;DR**: In Coolify, go to your application → **Storage/Volumes** tab → **Add Volume** → Set:
- **Container Path**: `/app/artera`
- **Volume Name**: `artera-storage-data`
- **Volume Type**: `Named Volume`

Then save and deploy!

---

## Step-by-Step Coolify Configuration

### 1. **Connect Your Repository**

1. Go to Coolify dashboard
2. Create new application or edit existing
3. Connect your Git repository containing this codebase

### 2. **Configure Persistent Volume (MANDATORY)**

**This is the MOST IMPORTANT step!**

#### Method 1: Using Coolify UI (Recommended)

**Note**: Coolify UI may vary by version. Look for "Storage", "Volumes", "Persistent Storage", or "Docker Volumes" in your application settings.

1. **Navigate to your application** in Coolify dashboard
2. **Find the volumes/storage section**:
   - Look for tabs like: "Storage", "Volumes", "Persistent Storage", or "Docker Volumes"
   - May be in left sidebar, top navigation, or under "Advanced Settings"
   - In some versions, it's under "Resources" → "Volumes"
3. **Click "Add Volume"** or **"Add Persistent Storage"** button
4. **Fill in the volume configuration**:
   - **Container Path**: `/app/artera` (must be exact, no trailing slash)
   - **Volume Name**: `artera-storage-data` (or any name you prefer)
   - **Volume Type**: Select **"Named Volume"** (recommended for production)
   - **Size**: Leave default or set as needed (if option available)
5. **Click "Save"** or **"Add"** to create the volume
6. **Verify** the volume appears in your volumes list with status "Mounted" or "Active"

#### Method 2: Using docker-compose.yml (If Coolify supports it)

If your Coolify instance allows docker-compose configuration, you can add this to your `docker-compose.yml`:

```yaml
volumes:
  - artera-data:/app/artera

volumes:
  artera-data:
    driver: local
```

#### Method 3: Manual Configuration via Coolify API/Settings

If the UI doesn't have a volumes section, you may need to:
1. Check Coolify's advanced settings or "Docker Compose" section
2. Add volume configuration manually in the compose override section
3. Or use Coolify's environment variables to configure volumes

**Why this matters**: Without this volume, all files will be lost on redeployment!

**⚠️ CRITICAL**: Configure this BEFORE your first deployment!

### 3. **Set Environment Variables**

In Coolify's environment variables section, set these variables (see `.env.example` for reference):

**Required:**
```
BASE_URL=https://your-domain.com
```

**Optional (defaults provided):**
```
PORT=8975
CORS_ORIGINS=https://your-frontend.com
STORAGE_ROOT=artera
```

**Note**: `STORAGE_ROOT` configures the folder name where files are stored (default: `artera`). If you change this, update the volume mount path accordingly.

**Important**: 
- `BASE_URL` is used throughout the application (API docs, responses, web UI)
- Set `BASE_URL` to your actual domain (e.g., `https://your-app-name.your-domain.com`)
- The application will use this URL in all API responses and documentation

### 4. **Build Settings**

- **Build Pack**: Docker
- **Dockerfile Path**: `Dockerfile` (or leave default)
- **Build Command**: (leave empty)
- **Start Command**: (leave empty)

### 5. **Deploy**

Click **"Deploy"** or **"Redeploy"**

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Application is running (check logs)
- [ ] Volume is mounted (check logs for: `✓ Artera root directory initialized`)
- [ ] Upload a test file via API
- [ ] Redeploy the application
- [ ] Verify test file still exists after redeploy
- [ ] Check logs show: `✓ Existing items preserved: X items found`

---

## 🔍 How to Verify Volume is Working

### Check Application Logs

Look for these messages on startup:

```
✓ Default folder created: logo (or already exists)
✓ Default folder created: potentials (or already exists)
✓ Artera root directory initialized at: /app/artera
✓ Existing items preserved: X items found
⚠ IMPORTANT: All files and folders in artera directory persist across redeployments
```

### Test Persistence

1. **Upload a file**:
   ```bash
   curl -X POST "https://your-domain.com/api/files/upload" \
        -F "file=@test.txt" \
        -F "folder_path=test"
   ```

2. **Verify file exists**:
   ```bash
   curl "https://your-domain.com/api/files/list"
   ```

3. **Redeploy** in Coolify

4. **Check again**:
   ```bash
   curl "https://your-domain.com/api/files/list"
   ```
   
   The file should still be there! ✅

---

## 🛠️ Troubleshooting

### Files Disappear After Redeploy

**Problem**: Volume not configured or incorrectly configured

**Solution**:
1. **Check volume configuration in Coolify**:
   - Go to your application → Storage/Volumes tab
   - Verify volume is listed and mounted
   - Check that container path is exactly `/app/artera`
   
2. **Verify volume exists**:
   - In Coolify, check the "Volumes" section (may be in server settings)
   - Ensure `artera-storage-data` volume exists
   
3. **Check application logs**:
   - Look for volume mount errors
   - Verify path `/app/artera` is accessible
   
4. **Reconfigure volume if needed**:
   - Remove existing volume configuration
   - Add it again with correct settings
   - **Note**: This may require manual data migration if files already exist

### Permission Errors

**Problem**: Container can't write to volume

**Solution**:
- Coolify usually handles permissions automatically
- If issues persist, check volume permissions in Coolify
- May need to adjust file ownership manually

### Volume Not Mounting

**Problem**: Container starts but volume isn't accessible

**Solution**:
1. **Verify volume configuration**:
   - Check Storage/Volumes tab in Coolify
   - Ensure volume is listed and shows as "mounted"
   - Verify container path is `/app/artera` (no trailing slash)
   
2. **Check container logs**:
   - Look for mount errors or permission issues
   - Check if `/app/artera` directory exists in container
   
3. **Verify volume name**:
   - Ensure volume name matches what's configured
   - Check for typos in volume name
   
4. **Try recreating the volume**:
   - Remove the volume from application settings
   - Re-add it with same configuration
   - Redeploy the application
   
5. **Check Coolify version**:
   - Some Coolify versions may have different UI locations
   - Check Coolify documentation for volume configuration

### Data in Wrong Location

**Problem**: Files exist but in different location

**Solution**:
- Verify volume mount path is `/app/artera`
- Check application logs for actual path being used
- Ensure volume is mounted before application starts

---

## 📋 Quick Reference

### Volume Configuration (Copy-Paste Ready)

**For Coolify UI:**
```
Container Path: /app/artera (or /app/{STORAGE_ROOT} if using custom folder name)
Volume Name: artera-storage-data
Volume Type: Named Volume
```

**Note**: The container path should match `/app/{STORAGE_ROOT}` where `STORAGE_ROOT` is the value from your `.env` file (default: `artera`).

**For docker-compose.yml (if supported):**
```yaml
volumes:
  - artera-data:/app/artera

volumes:
  artera-data:
    driver: local
```

### Step-by-Step Checklist

- [ ] Repository connected to Coolify
- [ ] Application created in Coolify
- [ ] **Volume configured** (`/app/artera` → `artera-storage-data`)
- [ ] Environment variables set (if needed)
- [ ] First deployment completed
- [ ] Verified volume mount in logs
- [ ] Tested file upload
- [ ] Tested persistence after redeploy

### Environment Variables

**Required:**
```
BASE_URL=https://your-domain.com
```

**Optional (defaults provided):**
```
PORT=8975
CORS_ORIGINS=https://your-frontend.com,https://another-domain.com
```

**Note**: Copy `.env.example` to `.env` and update `BASE_URL` with your actual domain. The `BASE_URL` is used throughout the application for API documentation, responses, and web UI.

### API Endpoints

- Web UI: `https://your-domain.com/`
- API Docs: `https://your-domain.com/docs`
- Health Check: `https://your-domain.com/health`
- Upload File: `POST https://your-domain.com/api/files/upload`
- List Files: `GET https://your-domain.com/api/files/tree`

---

## 🔐 Security Notes

- The `artera` folder is excluded from git (see `.gitignore`)
- All operations are restricted to the `artera` directory
- Path traversal attacks are prevented
- Volume data is managed by Coolify/Docker

---

## 📞 Need Help?

1. Check application logs in Coolify
2. Verify volume configuration
3. Test with a simple file upload/redeploy cycle
4. Review `DEPLOYMENT.md` for detailed information

---

**Remember**: Always configure the persistent volume BEFORE the first deployment!

