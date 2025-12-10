# Plantalyze Backend

Python backend for plant disease detection using deep learning.

## Architecture

The backend implements a complete image processing pipeline:

1. **Preprocessing** (`preprocessing.py`): Applies white balance correction, CLAHE, denoising, and sharpening
2. **Segmentation** (`segmentation.py`): Uses UNet model to generate 3-class masks (background, healthy leaf, diseased regions)
3. **Classification** (`classification.py`): Uses ShuffleNet v2 with 4-channel input (RGB + mask) to predict disease class

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Model Files

Ensure the following model files are in the `backend/` directory:
- `unet_model.h5` - UNet segmentation model
- `Best_ShuffleNet_Model.pth` - ShuffleNet classification model

### 3. Run the Flask Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /health
```

Returns server status and whether models are loaded.

### Analyze Leaf
```
POST /analyze
```

**Request Body:**
```json
{
  "image": "base64_encoded_image_string",
  "mimeType": "image/jpeg"
}
```

**Response:**
```json
{
  "isLeaf": true,
  "disease": "Tomato___Early_blight",
  "confidence": 0.95,
  "description": "Early blight causes concentric ring spots on older leaves..."
}
```

## Disease Classes

The model can detect 26 disease classes:
- healthy
- Apple diseases (scab, black rot, cedar apple rust)
- Cherry diseases (powdery mildew)
- Corn diseases (cercospora, common rust, northern leaf blight)
- Grape diseases (black rot, esca, leaf blight)
- Peach diseases (bacterial spot)
- Pepper diseases (bacterial spot)
- Potato diseases (early blight, late blight)
- Squash diseases (powdery mildew)
- Strawberry diseases (leaf scorch)
- Tomato diseases (bacterial spot, early blight, late blight, leaf mold, septoria, spider mites, target spot, TYLCV, mosaic virus)

## Model Details

### UNet Segmentation Model
- Input: 256x256 RGB image
- Output: 3-class mask (background, healthy leaf, diseased regions)
- Format: Keras .h5 file

### ShuffleNet Classification Model
- Input: 224x224 4-channel image (RGB + mask)
- Output: 26-class disease prediction
- Format: PyTorch .pth checkpoint

## Testing Individual Modules

### Test Preprocessing
```bash
python preprocessing.py path/to/image.jpg
```

### Test Segmentation
```bash
python segmentation.py unet_model.h5 path/to/image.jpg
```

### Test Classification
```bash
python classification.py Best_ShuffleNet_Model.pth path/to/input.npy
```

## Notes

- The server uses CORS to allow requests from the frontend
- Images are processed in temporary files and cleaned up after analysis
- TensorFlow warnings are suppressed for cleaner output
- GPU acceleration is used automatically if CUDA is available for PyTorch
