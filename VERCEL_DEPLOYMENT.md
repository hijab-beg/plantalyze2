# Plantalyze - Vercel Deployment Guide

Complete guide for deploying Plantalyze (React + Python Flask) to Vercel.

## 🚀 Overview

Plantalyze is deployed as a full-stack application on Vercel:
- **Frontend**: React + TypeScript + Vite (Static Build)
- **Backend**: Python Flask Serverless Functions
- **ML Models**: UNet segmentation model (unet_model.h5)

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to GitHub
3. **ML Model File**: `unet_model.h5` (must be uploaded separately)
4. **Node.js**: v18+ installed locally
5. **Python**: 3.11+ installed locally

## 🛠️ Project Structure

```
plantalyze-main/
├── api/                          # Serverless Functions
│   ├── health.py                 # Health check endpoint
│   ├── analyze.py                # Main analysis endpoint
│   └── requirements.txt          # Python dependencies for serverless
├── backend/                      # Backend logic (imported by API)
│   ├── preprocessing.py
│   ├── segmentation.py
│   ├── classification.py
│   ├── unet_model.h5            # UNet model (upload separately)
│   └── Best_ShuffleNet_Model.pth
├── src/                          # Frontend React app
├── vercel.json                   # Vercel configuration
├── .env.example                  # Environment variables template
└── package.json                  # Node dependencies
```

## 📝 Step-by-Step Deployment

### 1. Prepare Your Repository

```bash
# Ensure all files are committed
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"**
3. **Import** your GitHub repository
4. Vercel will auto-detect the framework (Vite)

### 3. Configure Environment Variables

In Vercel Dashboard → **Settings → Environment Variables**, add:

```env
VITE_BACKEND_URL=https://your-project.vercel.app
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

**Note**: `VITE_BACKEND_URL` should be your Vercel deployment URL (e.g., `https://plantalyze.vercel.app`)

### 4. Upload ML Model Files

**CRITICAL**: ML models are too large for Git (100MB+ files).

#### Option A: Vercel CLI Upload (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Link your project
vercel link

# Upload model file to Vercel Blob Storage
vercel blob upload backend/unet_model.h5
```

#### Option B: External Storage (Alternative)

Store models on cloud storage and download on cold start:

```python
# In backend/segmentation.py
import urllib.request
import os

MODEL_URL = "https://your-storage.com/unet_model.h5"
MODEL_PATH = "backend/unet_model.h5"

if not os.path.exists(MODEL_PATH):
    print("Downloading model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
```

#### Option C: Git LFS (For GitHub)

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.h5" "*.pth"

# Commit and push
git add .gitattributes backend/*.h5 backend/*.pth
git commit -m "Add models with Git LFS"
git push
```

### 5. Deploy

```bash
# Automatic deployment via Git push
git push origin main

# Or manual deployment via CLI
vercel --prod
```

## 🔧 Configuration Files

### vercel.json

Already configured in your project:
- Builds frontend as static site
- Deploys Python files in `/api` as serverless functions
- Routes `/api/*` to serverless functions
- Routes everything else to frontend

### api/requirements.txt

Optimized Python dependencies for serverless:
- Uses `tensorflow-cpu` (lighter than full TensorFlow)
- Uses `opencv-python-headless` (no GUI dependencies)
- Minimal set of required packages

## 🌐 API Endpoints

Once deployed, your API will be available at:

### GET /api/health
Health check endpoint

```bash
curl https://your-project.vercel.app/api/health
```

Response:
```json
{
  "status": "healthy",
  "message": "Plantalyze API is running on Vercel"
}
```

### POST /api/analyze
Analyze leaf image

```bash
curl -X POST https://your-project.vercel.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_image", "mimeType": "image/jpeg"}'
```

Response:
```json
{
  "isLeaf": true,
  "segmentationMask": "data:image/png;base64,...",
  "maskStats": {
    "backgroundPercent": 25.5,
    "healthyPercent": 60.2,
    "diseasedPercent": 14.3
  }
}
```

## 🧪 Local Testing

### Test Frontend Locally

```bash
# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local with your values

# Run dev server
npm run dev
```

Frontend runs on `http://localhost:8080`

### Test Backend Locally

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run Flask server
python app.py
```

Backend runs on `http://localhost:5000`

### Test Serverless Functions Locally

```bash
# Install Vercel CLI
npm install -g vercel

# Run local development server
vercel dev
```

This simulates the Vercel environment locally.

## 📊 Vercel Serverless Limits

**Important Limitations:**

| Resource | Free Plan | Pro Plan |
|----------|-----------|----------|
| Function Duration | 10s | 60s |
| Function Memory | 1024 MB | 3008 MB |
| Deployment Size | 100 MB | 500 MB |
| Serverless Function Size | 50 MB | 250 MB |

### Optimization Tips

1. **Model Size**: Keep models under 50MB or use external storage
2. **Cold Starts**: First request may take 5-10s (model loading)
3. **Timeouts**: Large images may timeout on free plan
4. **Memory**: TensorFlow models need significant memory

## 🔍 Troubleshooting

### Issue: "Model not found"

**Solution**: Ensure `unet_model.h5` is uploaded to Vercel
```bash
vercel blob upload backend/unet_model.h5
```

### Issue: Function timeout (10s limit)

**Solution**: 
- Upgrade to Pro plan for 60s timeout
- Optimize image preprocessing
- Reduce model complexity

### Issue: "Module not found" error

**Solution**: Check `api/requirements.txt` has all dependencies
```bash
# Test locally first
cd api
pip install -r requirements.txt
python analyze.py
```

### Issue: CORS errors

**Solution**: Already handled with `flask-cors` in API functions

### Issue: Large model download fails

**Solution**: Use Vercel Blob Storage or CDN:
```python
# Store model on CDN
MODEL_URL = "https://cdn.example.com/unet_model.h5"
```

## 🚦 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Repository connected to Vercel
- [ ] Environment variables configured
- [ ] ML model files uploaded
- [ ] Frontend builds successfully
- [ ] `/api/health` endpoint responds
- [ ] `/api/analyze` endpoint works with test image
- [ ] Supabase authentication works
- [ ] Custom domain configured (optional)

## 🔐 Security Best Practices

1. **API Rate Limiting**: Configure in Vercel settings
2. **Environment Variables**: Never commit `.env` files
3. **CORS**: Restrict origins in production
4. **File Upload Limits**: Validate image sizes
5. **Input Validation**: Sanitize all user inputs

## 📈 Monitoring

Monitor your deployment in Vercel Dashboard:
- **Analytics**: Page views and visitor data
- **Logs**: Function execution logs
- **Performance**: Response times and errors
- **Usage**: Bandwidth and function invocations

## 🔄 Continuous Deployment

Vercel automatically deploys on Git push:

1. Push to `main` branch → Production deployment
2. Push to feature branch → Preview deployment
3. Pull requests → Automatic preview URLs

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [TensorFlow on Vercel](https://vercel.com/guides/using-tensorflow-with-vercel)
- [Git LFS Guide](https://git-lfs.github.com/)

## 💡 Tips for Success

1. **Test Locally First**: Use `vercel dev` before deploying
2. **Monitor Logs**: Check Vercel logs for errors
3. **Optimize Images**: Compress before upload
4. **Cache Models**: Reuse loaded models across invocations
5. **Set Timeouts**: Handle long-running operations gracefully

## 🆘 Need Help?

- Vercel Support: [vercel.com/support](https://vercel.com/support)
- GitHub Issues: Report bugs in your repository
- Community: [Vercel Discord](https://vercel.com/discord)

---

## Quick Deploy Button

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/plantalyze)

---

**Last Updated**: January 2026  
**Vercel Runtime**: Python 3.11  
**Framework**: Vite + React + TypeScript
