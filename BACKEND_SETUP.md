# Plantalyze - Backend Integration Setup Guide

## Overview

The backend has been successfully integrated! Your Plantalyze application now uses:

1. **Preprocessing Module** - White balance, CLAHE, denoising, and sharpening
2. **UNet Segmentation** - Generates 3-class masks (background, healthy leaf, diseased regions)
3. **ShuffleNet Classification** - 4-channel input (RGB + Mask) to classify 26 disease types

## Quick Start

### Step 1: Install Python Backend Dependencies

Open a new terminal in the `backend` folder:

**Windows:**
```bash
cd backend
start_backend.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x start_backend.sh
./start_backend.sh
```

Or manually:
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

The backend will start on `http://localhost:5000`

### Step 2: Configure Frontend

The frontend (`supabase/functions/analyze-leaf/index.ts`) has been updated to call your Python backend instead of the AI gateway.

**Optional:** Set the backend URL as an environment variable:
```bash
# In .env file or Supabase environment
BACKEND_URL=http://localhost:5000
```

### Step 3: Run Frontend (Already Running)

Your frontend is already running on `http://localhost:8080`. The dashboard will now use your actual ML pipeline!

## Architecture

```
User Upload Image
    ↓
Frontend (React) → Supabase Edge Function
    ↓
Flask Backend API (localhost:5000)
    ↓
1. Preprocessing (white balance, CLAHE, denoise, sharpen)
    ↓
2. UNet Segmentation (generates mask)
    ↓
3. Create 4-channel input (RGB + Mask)
    ↓
4. ShuffleNet Classification (predict disease)
    ↓
Return: { isLeaf, disease, confidence, description }
```

## Model Files (✓ Verified)

Both models are in the correct location:

- ✓ `backend/unet_model.h5` - UNet segmentation model
- ✓ `backend/Best_ShuffleNet_Model.pth` - ShuffleNet classification model

## Disease Classes Supported

The model can detect **26 disease classes**:

1. healthy
2. Apple___Apple_scab
3. Apple___Black_rot
4. Apple___Cedar_apple_rust
5. Cherry___Powdery_mildew
6. Corn___Cercospora_leaf_spot Gray_leaf_spot
7. Corn___Common_rust
8. Corn___Northern_Leaf_Blight
9. Grape___Black_rot
10. Grape___Esca_(Black_Measles)
11. Grape___Leaf_blight_(Isariopsis_Leaf_Spot)
12. Peach___Bacterial_spot
13. Pepper,_bell___Bacterial_spot
14. Potato___Early_blight
15. Potato___Late_blight
16. Squash___Powdery_mildew
17. Strawberry___Leaf_scorch
18. Tomato___Bacterial_spot
19. Tomato___Early_blight
20. Tomato___Late_blight
21. Tomato___Leaf_Mold
22. Tomato___Septoria_leaf_spot
23. Tomato___Spider_mites_Two-spotted_spider_mite
24. Tomato___Target_Spot
25. Tomato___Tomato_Yellow_Leaf_Curl_Virus
26. Tomato___Tomato_mosaic_virus

## API Endpoints

### Health Check
```
GET http://localhost:5000/health
```

### Analyze Leaf
```
POST http://localhost:5000/analyze
Content-Type: application/json

{
  "image": "base64_encoded_image",
  "mimeType": "image/jpeg"
}
```

Response:
```json
{
  "isLeaf": true,
  "disease": "Tomato___Early_blight",
  "confidence": 0.95,
  "description": "Early blight causes concentric ring spots on older leaves. Remove affected leaves and apply fungicide."
}
```

## Testing

### Test Individual Components

1. **Test Preprocessing:**
   ```bash
   cd backend
   python preprocessing.py path/to/test/image.jpg
   ```

2. **Test Segmentation:**
   ```bash
   python segmentation.py unet_model.h5 path/to/test/image.jpg
   ```

3. **Test Classification:**
   ```bash
   python classification.py Best_ShuffleNet_Model.pth path/to/test/input.npy
   ```

### Test Full Pipeline

1. Start backend: `cd backend && python app.py`
2. Open browser: `http://localhost:8080`
3. Log in to dashboard
4. Upload a leaf image
5. See real predictions from your models!

## Troubleshooting

### Backend Not Starting

**Issue:** `ModuleNotFoundError`
```bash
cd backend
pip install -r requirements.txt
```

**Issue:** Models not found
- Verify `unet_model.h5` and `Best_ShuffleNet_Model.pth` are in `backend/` folder

### Frontend Can't Connect to Backend

**Issue:** `Backend service is not available`
- Ensure backend is running: `cd backend && python app.py`
- Check backend URL: should be `http://localhost:5000`
- Test manually: `curl http://localhost:5000/health`

### CORS Errors

The Flask backend has CORS enabled. If you still see CORS errors:
- Ensure you're accessing frontend from `http://localhost:8080`
- Check browser console for specific CORS messages

## Dependencies

### Python Backend
- Flask (web framework)
- TensorFlow/Keras (UNet model)
- PyTorch (ShuffleNet model)
- OpenCV (image processing)
- NumPy, Pillow (utilities)

See `backend/requirements.txt` for full list.

### Frontend (Already Installed)
- React + TypeScript
- Vite
- Supabase
- Tailwind CSS + shadcn/ui

## Next Steps

1. ✅ Start the backend server
2. ✅ Test with real leaf images
3. ✅ Verify predictions match your training data
4. Consider adding:
   - Model versioning
   - Batch processing
   - Result caching
   - Performance monitoring
   - Additional plant species

## Notes

- The backend processes images through the full pipeline:
  - Preprocessing (improves image quality)
  - Segmentation (identifies healthy vs diseased regions)
  - Classification (predicts specific disease)

- Predictions include confidence scores and actionable descriptions

- The system validates if uploaded images actually contain leaves

- Temporary files are automatically cleaned up after processing

---

**Ready to test!** Start the backend and upload a leaf image to see your ML pipeline in action! 🌿
