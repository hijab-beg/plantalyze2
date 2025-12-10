# Plantalyze - Plant Disease Detection

A full-stack web application for plant disease detection using UNet segmentation.

## Features

- 🌿 Plant leaf image upload
- 🔬 UNet-based segmentation (3-class: background, healthy, diseased)
- 📊 Pixel distribution visualization
- 🎨 Modern UI with React + TypeScript

## Tech Stack

**Frontend:**
- React + TypeScript
- Vite
- TailwindCSS
- Supabase (Auth)

**Backend:**
- Flask (Python)
- TensorFlow/Keras (UNet)
- OpenCV (preprocessing)

## Deployment on Railway

### Prerequisites
1. GitHub account
2. Railway account (sign up at railway.app)
3. Model files: `unet_model.h5` (not in git due to size)

### Steps

1. **Connect Repository to Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `hijab-beg/plantalyze2`

2. **Upload Model File:**
   - After deployment, you'll need to upload `unet_model.h5` to Railway
   - Option A: Use Railway CLI to upload the model
   - Option B: Use cloud storage (AWS S3, Google Cloud Storage) and download on startup

3. **Set Environment Variables:**
   ```
   PORT=5000
   FLASK_ENV=production
   ```

4. **Configure Build:**
   - Railway will auto-detect Python and use `railway.json` config
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`

5. **Update Frontend:**
   - Copy your Railway backend URL (e.g., `https://plantalyze.up.railway.app`)
   - Update `.env.local`:
     ```
     VITE_BACKEND_URL=https://your-backend.up.railway.app
     ```
   - Deploy frontend to Vercel/Netlify

### Model File Handling

Since ML models are too large for git, you have options:

**Option 1: Railway Volumes (Recommended)**
```bash
# Upload model using Railway CLI
railway up unet_model.h5
```

**Option 2: Cloud Storage**
Modify `backend/app.py` to download from cloud storage:
```python
import urllib.request
if not UNET_MODEL_PATH.exists():
    print("Downloading model...")
    urllib.request.urlretrieve(
        "YOUR_MODEL_URL", 
        str(UNET_MODEL_PATH)
    )
```

**Option 3: Git LFS**
```bash
git lfs install
git lfs track "*.h5"
git add .gitattributes backend/unet_model.h5
git commit -m "Add model with LFS"
git push
```

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend runs on `http://localhost:5000`

### Frontend
```bash
npm install
npm run dev
```
Frontend runs on `http://localhost:8080`

## API Endpoints

### `GET /health`
Health check endpoint
```json
{
  "status": "healthy",
  "models_loaded": {
    "unet": true
  }
}
```

### `POST /analyze`
Analyze leaf image
```json
// Request
{
  "image": "base64_encoded_image",
  "mimeType": "image/jpeg"
}

// Response
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

## Segmentation Output

The UNet model produces a 3-class segmentation mask:
- **0 (Black)**: Background
- **128 (Grey)**: Healthy leaf tissue
- **255 (White)**: Diseased areas

## Project Structure

```
plantalyze2/
├── backend/
│   ├── app.py                 # Flask API
│   ├── preprocessing.py       # Image preprocessing
│   ├── segmentation.py        # UNet model
│   ├── requirements.txt       # Python dependencies
│   └── unet_model.h5         # UNet model (not in git)
├── src/
│   ├── pages/
│   │   └── Dashboard.tsx     # Main analysis UI
│   └── ...
├── railway.json              # Railway config
├── Procfile                  # Process definition
└── runtime.txt              # Python version

```

## Notes

- Model files (`.h5`, `.pth`) are excluded from git (too large)
- Need to upload model separately to Railway
- Classification module removed - only segmentation active
- Frontend calls Flask backend directly

## License

MIT
