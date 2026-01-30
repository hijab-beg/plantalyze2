"""
Vercel Serverless Function for Leaf Analysis
Main endpoint for plant disease detection using UNet segmentation
"""

import os
import sys
import json
import base64
import io
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import cv2

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

from preprocessing import preprocess_leaf
from segmentation import load_unet_model, predict_segmentation

app = Flask(__name__)
CORS(app)

# Global model variable (loaded on cold start)
unet_model = None

def get_model():
    """Lazy load model on first request"""
    global unet_model
    if unet_model is None:
        model_path = os.path.join(backend_dir, 'unet_model.h5')
        if os.path.exists(model_path):
            unet_model = load_unet_model(model_path)
        else:
            print(f"WARNING: Model not found at {model_path}")
    return unet_model

def decode_base64_image(base64_string):
    """Decode base64 image string to numpy array"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
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

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main endpoint for leaf analysis
    Expects JSON: { "image": "base64_string", "mimeType": "image/jpeg" }
    Returns: { "isLeaf": bool, "segmentationMask": str, "maskStats": object }
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
        
        # Get model
        model = get_model()
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
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
            mask = predict_segmentation(preprocessed_path, model)
            
            if mask is None:
                raise ValueError("Segmentation failed")
            
            # Count pixels for each class
            background_pixels = np.sum(mask == 0)
            healthy_pixels = np.sum(mask == 128)
            diseased_pixels = np.sum(mask == 255)
            total_pixels = mask.size
            
            # Convert mask to base64 for frontend display
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
        print(f"Error in analyze: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500

# Vercel expects a handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
