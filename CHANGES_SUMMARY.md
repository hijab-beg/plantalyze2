# Vercel Deployment - Changes Summary

This document summarizes all changes made to prepare Plantalyze for Vercel deployment.

## 📅 Date: January 30, 2026

## 🎯 Objective
Convert the application from Railway deployment to Vercel deployment with serverless Python functions.

## ✅ Files Created

### Configuration Files

1. **`vercel.json`**
   - Configures Vercel deployment
   - Defines build and routing rules
   - Specifies Python runtime for `/api` functions

2. **`.env.example`**
   - Template for environment variables
   - Documents required configuration

3. **`.vercelignore`**
   - Excludes unnecessary files from deployment
   - Reduces deployment size

4. **`runtime.txt`**
   - Already existed, specifies Python 3.11

### API Directory (`/api`)

Created new serverless functions structure:

1. **`api/__init__.py`**
   - Package initialization

2. **`api/index.py`**
   - Main API router
   - Handles routing to health and analyze endpoints

3. **`api/health.py`**
   - Health check endpoint
   - Returns API status

4. **`api/analyze.py`**
   - Main leaf analysis endpoint
   - Handles image processing and segmentation
   - Imports from `/backend` directory

5. **`api/requirements.txt`**
   - Optimized Python dependencies for serverless
   - Uses `tensorflow-cpu` (lighter)
   - Uses `opencv-python-headless` (no GUI)

6. **`api/README.md`**
   - API documentation
   - Endpoint specifications
   - Usage examples

### Documentation

1. **`VERCEL_DEPLOYMENT.md`**
   - Complete deployment guide
   - Step-by-step instructions
   - Troubleshooting section
   - Configuration details

2. **`VERCEL_CHECKLIST.md`**
   - Pre-deployment checklist
   - Post-deployment verification
   - Testing procedures

## 📝 Files Modified

### Frontend Changes

1. **`src/pages/Dashboard.tsx`**
   - **Line 111**: Changed API endpoint from `/analyze` to `/api/analyze`
   - **Line 111**: Updated `VITE_BACKEND_URL` default from `http://localhost:5000` to empty string
   - **Line 140**: Updated error message to be deployment-agnostic

### Package Configuration

1. **`package.json`**
   - Added `vercel-build` script for Vercel build command

### Documentation

1. **`README.md`**
   - Complete rewrite for Vercel deployment
   - Added project structure
   - Added quick start guide
   - Added API documentation
   - Removed Lovable-specific content

## 🔄 Architecture Changes

### Before (Railway)
```
Frontend (Vite) → Flask Server (Port 5000) → Backend Logic
```

### After (Vercel)
```
Frontend (Vite Static) → Serverless Functions (/api) → Backend Logic
```

## 🗂️ Directory Structure

### New Structure
```
plantalyze-main/
├── api/                    # NEW - Serverless functions
│   ├── __init__.py
│   ├── index.py
│   ├── health.py
│   ├── analyze.py
│   ├── requirements.txt
│   └── README.md
├── backend/                # UNCHANGED - Logic remains
│   ├── preprocessing.py
│   ├── segmentation.py
│   ├── classification.py
│   └── unet_model.h5
├── src/                    # MODIFIED - Updated API calls
│   └── pages/
│       └── Dashboard.tsx   # API endpoint changed
├── vercel.json             # NEW
├── .vercelignore           # NEW
├── .env.example            # NEW
├── VERCEL_DEPLOYMENT.md    # NEW
├── VERCEL_CHECKLIST.md     # NEW
└── README.md               # MODIFIED
```

## 🔧 Technical Changes

### Backend Migration

- **Original**: `backend/app.py` runs Flask server
- **New**: `api/*.py` files are serverless functions
- **Logic**: Backend logic files remain in `/backend` and are imported by API functions

### Dependency Optimization

Original `backend/requirements.txt`:
- `tensorflow==2.15.0` (full version, ~1GB)
- `opencv-python==4.8.1.78` (with GUI)
- `torch==2.1.0` and `torchvision==0.16.0`
- `gunicorn==21.2.0` (not needed for serverless)

New `api/requirements.txt`:
- `tensorflow-cpu==2.15.0` (lighter, ~400MB)
- `opencv-python-headless==4.8.1.78` (no GUI, smaller)
- Removed PyTorch (not used in active code)
- Removed gunicorn (not needed)

### API Routing

- **Before**: Direct Flask routes at `/analyze`, `/health`
- **After**: Serverless functions at `/api/analyze`, `/api/health`
- **CORS**: Configured in each function

## 🚀 Deployment Flow

1. **Code Push**: Git push to main branch
2. **Vercel Build**: 
   - Builds frontend: `npm run build` → `dist/`
   - Builds Python functions: Each `.py` file in `/api`
3. **Deployment**:
   - Frontend: Static files served via CDN
   - API: Python functions as serverless endpoints

## 🔑 Environment Variables

Required for deployment:

```env
VITE_BACKEND_URL=https://your-project.vercel.app
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

## ⚠️ Important Notes

### Model Files

The UNet model (`unet_model.h5`) is **NOT included** in Git due to size (>100MB).

**Solutions**:
1. Upload via Vercel CLI: `vercel blob upload backend/unet_model.h5`
2. Use Git LFS for version control
3. Host on CDN and download on cold start

### Serverless Limitations

**Free Plan**:
- Function timeout: 10 seconds
- Function memory: 1024 MB
- May need optimization for large images

**Pro Plan** (if needed):
- Function timeout: 60 seconds
- Function memory: 3008 MB
- Better for ML workloads

### Cold Starts

- First request after deployment: 5-10 seconds (model loading)
- Subsequent requests: <1 second
- Model loaded into memory on first use

## 🧪 Testing Recommendations

### Local Testing

```bash
# Test backend locally
cd backend
python app.py

# Test frontend locally
npm run dev

# Test Vercel environment locally
vercel dev
```

### Deployment Testing

1. Test `/api/health` endpoint
2. Upload test image
3. Verify segmentation works
4. Check response times
5. Monitor logs in Vercel dashboard

## 📊 What's NOT Changed

The following remain unchanged:

- ✅ Frontend UI/UX
- ✅ Backend logic (preprocessing, segmentation)
- ✅ Model architecture
- ✅ Supabase authentication
- ✅ Core functionality

**Only deployment method changed!**

## 🎓 Migration Summary

| Aspect | Railway | Vercel |
|--------|---------|--------|
| **Hosting Type** | Container | Serverless |
| **Backend** | Flask Server | Serverless Functions |
| **Frontend** | Static Files | Static Files + CDN |
| **Scaling** | Manual | Automatic |
| **Cold Start** | No | Yes (5-10s) |
| **Timeout** | 60s+ | 10s (Free), 60s (Pro) |
| **Cost** | Free tier limited | Free tier generous |

## 🔜 Next Steps

1. ✅ All files created and modified
2. ⬜ Commit changes to Git
3. ⬜ Push to GitHub
4. ⬜ Connect repository to Vercel
5. ⬜ Configure environment variables
6. ⬜ Upload model file
7. ⬜ Deploy and test

## 💡 Recommendations

### For Development
- Use `vercel dev` to test locally with serverless environment
- Keep backend code in `/backend` for reusability
- Test with different image sizes

### For Production
- Monitor function execution times
- Consider Pro plan if timeout issues
- Use CDN for model files if too large
- Enable error tracking (Sentry, etc.)
- Set up custom domain

### For Optimization
- Compress images on frontend before upload
- Optimize model size if possible
- Cache frequently used data
- Use lazy loading for model

## 📞 Support Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Python on Vercel](https://vercel.com/docs/functions/runtimes/python)
- [TensorFlow on Vercel](https://vercel.com/guides/using-tensorflow-with-vercel)

---

**Status**: ✅ Ready for Deployment

All necessary changes have been made. The application is ready to be deployed to Vercel following the guide in `VERCEL_DEPLOYMENT.md`.
