# 🚀 Coolify Deployment Quick Guide

## ⚠️ CRITICAL: Data Persistence Setup

**IMPORTANT**: Follow these steps BEFORE your first deployment to ensure data persists across redeployments!

---

## Step-by-Step Coolify Configuration

### 1. **Connect Your Repository**

1. Go to Coolify dashboard
2. Create new application or edit existing
3. Connect your Git repository containing this codebase

### 2. **Configure Persistent Volume (MANDATORY)**

**This is the MOST IMPORTANT step!**

1. In your application settings, find **"Volumes"** or **"Persistent Storage"** section
2. Click **"Add Volume"** or **"Add Persistent Storage"**
3. Configure as follows:

   ```
   Container Path: /app/artera
   Volume Name: artera-storage-data
   Volume Type: Named Volume (recommended)
   ```

4. **SAVE** the configuration

**Why this matters**: Without this volume, all files will be lost on redeployment!

### 3. **Set Environment Variables**

In Coolify's environment variables section, set (optional if using defaults):

```
BASE_URL=https://your-domain.com
PORT=8975
CORS_ORIGINS=https://your-frontend.com
```

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
1. Check volume configuration in Coolify
2. Verify container path is exactly `/app/artera`
3. Ensure volume exists in Coolify's volume management
4. Reconfigure volume if needed (may require manual data migration)

### Permission Errors

**Problem**: Container can't write to volume

**Solution**:
- Coolify usually handles permissions automatically
- If issues persist, check volume permissions in Coolify
- May need to adjust file ownership manually

### Volume Not Mounting

**Problem**: Container starts but volume isn't accessible

**Solution**:
1. Verify volume configuration in Coolify dashboard
2. Check container logs for errors
3. Ensure volume name is correct
4. Try recreating the volume

### Data in Wrong Location

**Problem**: Files exist but in different location

**Solution**:
- Verify volume mount path is `/app/artera`
- Check application logs for actual path being used
- Ensure volume is mounted before application starts

---

## 📋 Quick Reference

### Volume Configuration (Copy-Paste Ready)

```
Container Path: /app/artera
Volume Name: artera-storage-data
Volume Type: Named Volume
```

### Environment Variables (Optional)

```
BASE_URL=https://your-domain.com
PORT=8975
CORS_ORIGINS=https://your-frontend.com,https://another-domain.com
```

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

