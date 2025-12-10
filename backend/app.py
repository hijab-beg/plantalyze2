"""
Flask API for Plantalyze - Plant Disease Detection Backend
Handles image preprocessing, UNet segmentation, and ShuffleNet classification
"""

import os
import base64
import io
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import cv2

from preprocessing import preprocess_leaf
from segmentation import load_unet_model, predict_segmentation
# Classification removed - only doing segmentation

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
BACKEND_DIR = Path(__file__).parent
UNET_MODEL_PATH = BACKEND_DIR / "unet_model.h5"

# Load models at startup
print("Loading models...")
unet_model = load_unet_model(str(UNET_MODEL_PATH))
print("Models loaded successfully!")


def decode_base64_image(base64_string):
    """Decode base64 image string to numpy array"""
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return np.array(image)
    except Exception as e:
        raise ValueError(f"Failed to decode image: {str(e)}")


def is_valid_leaf_image(image_array):
    """
    Simple check to validate if image contains greenish colors typical of leaves
    """
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
    
    # Define green color range
    lower_green = np.array([25, 30, 30])
    upper_green = np.array([90, 255, 255])
    
    # Create mask for green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Calculate percentage of green pixels
    green_percentage = (np.count_nonzero(mask) / mask.size) * 100
    
    # If less than 5% green, probably not a leaf
    return green_percentage > 5.0


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': {
            'unet': unet_model is not None
        }
    })


@app.route('/analyze', methods=['POST'])
def analyze_leaf():
    """
    Main endpoint for leaf analysis
    Expects JSON: { "image": "base64_string", "mimeType": "image/jpeg" }
    Returns: { "isLeaf": bool, "disease": str|null, "confidence": float, "description": str }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        base64_image = data['image']
        
        # Decode image
        print("Decoding image...")
        image_array = decode_base64_image(base64_image)
        
        # Validate if it's a leaf image
        print("Validating leaf image...")
        is_leaf = is_valid_leaf_image(image_array)
        
        if not is_leaf:
            return jsonify({
                'isLeaf': False,
                'disease': None,
                'confidence': 0.0,
                'description': 'No plant leaf detected in the image. Please upload a clear photo of a plant leaf.'
            })
        
        # Save to temporary file for processing
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            temp_path = tmp_file.name
            cv2.imwrite(temp_path, cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))
        
        try:
            # Step 1: Preprocess the image
            print("Preprocessing image...")
            preprocessed_image = preprocess_leaf(temp_path)
            
            if preprocessed_image is None:
                raise ValueError("Preprocessing failed")
            
            # Save preprocessed image temporarily
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_preprocessed:
                preprocessed_path = tmp_preprocessed.name
                cv2.imwrite(preprocessed_path, cv2.cvtColor(preprocessed_image, cv2.COLOR_RGB2BGR))
            
            # Step 2: Generate segmentation mask using UNet
            print("Generating segmentation mask...")
            mask = predict_segmentation(preprocessed_path, unet_model)
            
            if mask is None:
                raise ValueError("Segmentation failed")
            
            # Debug: Check mask values
            unique_values = np.unique(mask)
            print(f"Mask unique values: {unique_values}")
            print(f"Mask shape: {mask.shape}")
            print(f"Mask dtype: {mask.dtype}")
            
            # Count pixels for each class
            background_pixels = np.sum(mask == 0)
            healthy_pixels = np.sum(mask == 128)
            diseased_pixels = np.sum(mask == 255)
            total_pixels = mask.size
            print(f"Background: {background_pixels}/{total_pixels} ({background_pixels/total_pixels*100:.1f}%)")
            print(f"Healthy leaf: {healthy_pixels}/{total_pixels} ({healthy_pixels/total_pixels*100:.1f}%)")
            print(f"Diseased: {diseased_pixels}/{total_pixels} ({diseased_pixels/total_pixels*100:.1f}%)")
            
            # Convert mask to base64 for frontend display
            import io
            import base64
            from PIL import Image
            
            # Convert mask to PIL Image
            mask_image = Image.fromarray(mask.astype(np.uint8))
            
            # Save to bytes buffer
            buffer = io.BytesIO()
            mask_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Encode to base64
            mask_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Clean up temporary files
            os.unlink(preprocessed_path)
            
            result = {
                'isLeaf': True,
                'segmentationMask': f'data:image/png;base64,{mask_base64}',
                'maskStats': {
                    'backgroundPercent': float(background_pixels/total_pixels*100),
                    'healthyPercent': float(healthy_pixels/total_pixels*100),
                    'diseasedPercent': float(diseased_pixels/total_pixels*100)
                }
            }
            
            print(f"Segmentation complete!")
            return jsonify(result)
            
        finally:
            # Clean up original temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        print(f"Error in analyze_leaf: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500


if __name__ == '__main__':
    # Check if models exist
    if not UNET_MODEL_PATH.exists():
        print(f"WARNING: UNet model not found at {UNET_MODEL_PATH}")
    
    # Run Flask app
    print("Starting Plantalyze Backend API...")
    print("Server running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
