# Plantalyze API - Vercel Serverless Functions

This directory contains the Python serverless functions for the Plantalyze backend, deployed on Vercel.

## Structure

```
api/
├── __init__.py          # Package initialization
├── index.py             # Main API handler (routes requests)
├── health.py            # Health check endpoint
├── analyze.py           # Leaf analysis endpoint
└── requirements.txt     # Python dependencies for serverless
```

## Endpoints

### GET /api/health
Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Plantalyze API is running on Vercel"
}
```

### POST /api/analyze
Analyze a plant leaf image for disease detection.

**Request:**
```json
{
  "image": "base64_encoded_image_data",
  "mimeType": "image/jpeg"
}
```

**Response (Success - Leaf Detected):**
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

**Response (No Leaf):**
```json
{
  "isLeaf": false,
  "disease": null,
  "confidence": 0.0,
  "description": "No plant leaf detected in the image. Please upload a clear photo of a plant leaf."
}
```

**Response (Error):**
```json
{
  "error": "Error message description"
}
```

## Dependencies

See [requirements.txt](./requirements.txt) for all Python dependencies.

Key libraries:
- **Flask**: Web framework
- **flask-cors**: CORS handling
- **tensorflow-cpu**: Machine learning (UNet model)
- **opencv-python-headless**: Image processing
- **Pillow**: Image handling
- **numpy**: Numerical operations

## Local Testing

Test the API functions locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API locally
python index.py
```

The API will be available at `http://localhost:5000/api/`

## Vercel Deployment

The functions in this directory are automatically deployed as serverless functions by Vercel.

### Configuration

Vercel configuration is handled in the root `vercel.json`:

```json
{
  "builds": [
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ]
}
```

### Environment

- **Python Version**: 3.11 (specified in `runtime.txt`)
- **Max Duration**: 10s (Free), 60s (Pro)
- **Max Memory**: 1024 MB (Free), 3008 MB (Pro)

## Backend Logic

The API functions import backend modules from `../backend/`:

- `preprocessing.py`: Image preprocessing (white balance, CLAHE, denoising)
- `segmentation.py`: UNet model loading and inference
- `classification.py`: Disease classification (optional)

## Model Files

The UNet model (`unet_model.h5`) must be present in the `backend/` directory.

For deployment, use one of these methods:
1. **Vercel Blob Storage** (recommended)
2. **Git LFS** for large files
3. **External CDN** and download on cold start

See [VERCEL_DEPLOYMENT.md](../VERCEL_DEPLOYMENT.md) for details.

## Error Handling

All endpoints include comprehensive error handling:
- Input validation
- Model loading errors
- Image processing failures
- Timeout handling

Errors return appropriate HTTP status codes and JSON error messages.

## CORS

CORS is enabled for all origins in development. For production, configure specific allowed origins in `index.py`:

```python
CORS(app, origins=["https://your-frontend-domain.com"])
```

## Performance

- **Cold Start**: 3-10s (model loading)
- **Warm Start**: < 1s
- **Image Processing**: 2-5s depending on size

Optimize by:
- Keeping images under 5MB
- Using model caching
- Upgrading to Vercel Pro for longer timeouts
