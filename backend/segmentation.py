"""
UNet segmentation module for Plantalyze
Loads UNet model and generates segmentation masks for leaf disease detection
"""

import cv2
import numpy as np
from tensorflow import keras
import tensorflow as tf
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


def load_unet_model(model_path):
    """
    Load UNet model from .h5 file
    
    Args:
        model_path: Path to UNet model file (.h5)
    
    Returns:
        Loaded Keras model or None if loading fails
    """
    try:
        print(f"Loading UNet model from {model_path}...")
        
        if not os.path.exists(model_path):
            print(f"Error: Model file not found at {model_path}")
            return None
        
        # Load model without compiling (we only need inference)
        model = keras.models.load_model(model_path, compile=False)
        
        print(f"UNet model loaded successfully!")
        print(f"Input shape: {model.input_shape}")
        print(f"Output shape: {model.output_shape}")
        
        return model
        
    except Exception as e:
        print(f"Error loading UNet model: {e}")
        import traceback
        traceback.print_exc()
        return None


def predict_segmentation(image_path, model):
    """
    Generate segmentation mask using UNet model
    
    The mask has 3 classes:
    - 0 (black): Background
    - 128 (gray): Healthy leaf tissue
    - 255 (white): Diseased regions
    
    Args:
        image_path: Path to preprocessed image
        model: Loaded UNet model
    
    Returns:
        Segmentation mask as numpy array (H, W) with values 0, 128, 255
        Returns None if prediction fails
    """
    if model is None:
        print("Error: Model is None")
        return None
    
    try:
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Error: Could not read image at {image_path}")
            return None
        
        # Store original size for resizing mask back
        original_size = (image.shape[1], image.shape[0])  # (width, height)
        
        # Resize to model input size (typically 256x256)
        image_resized = cv2.resize(image, (256, 256))
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1]
        image_normalized = image_rgb.astype(np.float32) / 255.0
        
        # Add batch dimension
        image_input = np.expand_dims(image_normalized, axis=0)
        
        # Predict
        prediction = model.predict(image_input, verbose=0)[0]
        
        # Process prediction based on output format
        mask = process_unet_output(prediction)
        
        # Resize mask back to original image size
        mask_resized = cv2.resize(
            mask, 
            original_size, 
            interpolation=cv2.INTER_NEAREST
        )
        
        return mask_resized
        
    except Exception as e:
        print(f"Error during segmentation prediction: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_unet_output(prediction):
    """
    Process UNet model output to create segmentation mask
    
    Handles different output formats:
    - Multi-class (H, W, C) where C >= 3: Use argmax and map to 0/128/255
    - Binary (H, W, 2): Threshold and map to 0/255
    - Single channel (H, W) or (H, W, 1): Threshold and map to 0/255
    
    Args:
        prediction: Model output (H, W, C) or (H, W)
    
    Returns:
        Segmentation mask (H, W) with values 0, 128, 255
    """
    print(f"UNet prediction shape: {prediction.shape}, dtype: {prediction.dtype}")
    print(f"UNet prediction range: [{prediction.min():.3f}, {prediction.max():.3f}]")
    
    # Case 1: Multi-class output (e.g., shape (256, 256, 3))
    if prediction.ndim == 3 and prediction.shape[-1] >= 3:
        print(f"Processing as multi-class output with {prediction.shape[-1]} classes")
        # Get class with highest probability
        mask_idx = np.argmax(prediction, axis=-1).astype(np.uint8)
        
        print(f"Class indices - unique values: {np.unique(mask_idx)}")
        print(f"Class 0 (background): {np.sum(mask_idx == 0)} pixels")
        print(f"Class 1 (healthy): {np.sum(mask_idx == 1)} pixels")
        print(f"Class 2 (diseased): {np.sum(mask_idx == 2)} pixels")
        
        # Map class indices to mask values
        # Class 0 -> 0 (background)
        # Class 1 -> 128 (healthy leaf)
        # Class 2 -> 255 (diseased)
        mapping = {0: 0, 1: 128, 2: 255}
        mask = np.vectorize(lambda x: mapping.get(x, 255))(mask_idx).astype(np.uint8)
    
    # Case 2: Binary classification (e.g., shape (256, 256, 2))
    elif prediction.ndim == 3 and prediction.shape[-1] == 2:
        # Use second channel (disease probability)
        mask_idx = np.argmax(prediction, axis=-1).astype(np.uint8)
        mask = (mask_idx * 255).astype(np.uint8)
    
    # Case 3: Single channel output
    else:
        # Squeeze to 2D if needed
        if prediction.ndim == 3:
            prediction = prediction.squeeze()
        
        # Threshold continuous values
        mask = (prediction * 255).astype(np.uint8)
        
        # Create 3-class mask based on thresholds
        mask_3class = np.zeros_like(mask)
        mask_3class[mask < 85] = 0       # Background
        mask_3class[(mask >= 85) & (mask < 170)] = 128  # Healthy leaf
        mask_3class[mask >= 170] = 255   # Diseased
        mask = mask_3class
    
    return mask


def create_colored_mask(mask):
    """
    Create colored visualization of segmentation mask
    
    Args:
        mask: Grayscale mask with values 0, 128, 255
    
    Returns:
        RGB colored mask (black/green/red)
    """
    h, w = mask.shape
    colored_mask = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Black for background
    colored_mask[mask == 0] = [0, 0, 0]
    
    # Green for healthy leaf tissue
    colored_mask[mask == 128] = [0, 255, 0]
    
    # Red for diseased regions
    colored_mask[mask == 255] = [255, 0, 0]
    
    return colored_mask


def create_overlay(image, mask, alpha=0.4):
    """
    Create overlay of mask on original image
    
    Args:
        image: Original RGB image
        mask: Grayscale segmentation mask
        alpha: Transparency factor for mask (0-1)
    
    Returns:
        Overlay image
    """
    colored_mask = create_colored_mask(mask)
    
    # Ensure same size
    if image.shape[:2] != mask.shape:
        colored_mask = cv2.resize(colored_mask, (image.shape[1], image.shape[0]))
    
    # Convert image to RGB if needed
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    elif len(image.shape) == 3 and image.shape[2] == 3:
        # Check if BGR, convert to RGB
        # Assume input is already RGB from preprocessing
        pass
    
    # Create overlay
    overlay = cv2.addWeighted(image, 1 - alpha, colored_mask, alpha, 0)
    
    return overlay


def extract_diseased_regions(image, mask):
    """
    Extract only diseased regions from image
    
    Args:
        image: Original RGB image
        mask: Segmentation mask
    
    Returns:
        Image with only diseased regions visible (rest is black)
    """
    result = image.copy()
    
    # Ensure same size
    if image.shape[:2] != mask.shape:
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]), 
                         interpolation=cv2.INTER_NEAREST)
    
    # Set non-diseased pixels to black
    result[mask != 255] = [0, 0, 0]
    
    return result


if __name__ == "__main__":
    # Test segmentation
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python segmentation.py <model_path> <image_path>")
        sys.exit(1)
    
    model_path = sys.argv[1]
    image_path = sys.argv[2]
    
    print("Loading model...")
    model = load_unet_model(model_path)
    
    if model is None:
        print("Failed to load model!")
        sys.exit(1)
    
    print(f"Predicting segmentation for {image_path}...")
    mask = predict_segmentation(image_path, model)
    
    if mask is not None:
        print("Segmentation complete!")
        print(f"Mask shape: {mask.shape}")
        print(f"Unique values in mask: {np.unique(mask)}")
        
        # Save mask
        output_path = "segmentation_mask.png"
        cv2.imwrite(output_path, mask)
        print(f"Saved mask to {output_path}")
        
        # Save colored mask
        colored = create_colored_mask(mask)
        cv2.imwrite("segmentation_colored.png", cv2.cvtColor(colored, cv2.COLOR_RGB2BGR))
        print("Saved colored mask to segmentation_colored.png")
    else:
        print("Segmentation failed!")
