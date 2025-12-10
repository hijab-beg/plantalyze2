"""
Image preprocessing module for Plantalyze
Implements white balance, CLAHE, denoising, and sharpening
"""

import cv2
import numpy as np
from pathlib import Path


def preprocess_leaf(image_path, output_dir=None):
    """
    Preprocess leaf image with:
    1. White balance correction
    2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    3. Denoising
    4. Sharpening
    
    Args:
        image_path: Path to input image
        output_dir: Optional directory to save processed image
    
    Returns:
        Preprocessed image as numpy array (RGB format)
    """
    # Read image
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return None
    
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Step 1: White Balance Correction
    img_wb = apply_white_balance(img)
    
    # Step 2: CLAHE on L channel
    img_clahe = apply_clahe(img_wb)
    
    # Step 3: Denoise
    img_denoised = cv2.fastNlMeansDenoisingColored(
        img_clahe, 
        None, 
        h=10,           # Filter strength for luminance
        hColor=10,      # Filter strength for color
        templateWindowSize=7,
        searchWindowSize=21
    )
    
    # Step 4: Sharpen
    img_sharp = apply_sharpening(img_denoised)
    
    # Save if output directory specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        stem = Path(image_path).stem
        out_file = output_path / f"{stem}_preprocessed.png"
        cv2.imwrite(str(out_file), cv2.cvtColor(img_sharp, cv2.COLOR_RGB2BGR))
        print(f"Saved preprocessed image to {out_file}")
    
    return img_sharp


def apply_white_balance(img):
    """
    Apply white balance correction to image
    Uses opencv xphoto module if available, otherwise falls back to simple gray-world algorithm
    
    Args:
        img: RGB image as numpy array
    
    Returns:
        White-balanced RGB image
    """
    try:
        # Try using OpenCV's xphoto module (requires opencv-contrib-python)
        if hasattr(cv2, 'xphoto') and hasattr(cv2.xphoto, 'createSimpleWB'):
            wb = cv2.xphoto.createSimpleWB()
            img_wb = wb.balanceWhite(img)
        else:
            raise AttributeError("xphoto not available")
    except (AttributeError, cv2.error):
        # Fallback: Simple gray-world white balance algorithm
        img_wb = gray_world_white_balance(img)
    
    return img_wb


def gray_world_white_balance(img):
    """
    Simple gray-world white balance algorithm
    Assumes average color of scene should be gray
    
    Args:
        img: RGB image as numpy array
    
    Returns:
        White-balanced RGB image
    """
    img_float = img.astype(np.float32)
    
    # Calculate global mean
    mean_global = np.mean(img)
    
    # Balance each channel
    for i in range(3):
        mean_channel = np.mean(img[:, :, i])
        if mean_channel > 0:  # Avoid division by zero
            img_float[:, :, i] = img_float[:, :, i] * (mean_global / mean_channel)
    
    # Clip values to valid range
    img_wb = np.clip(img_float, 0, 255).astype(np.uint8)
    
    return img_wb


def apply_clahe(img):
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    Enhances local contrast while avoiding over-amplification
    
    Args:
        img: RGB image as numpy array
    
    Returns:
        CLAHE-enhanced RGB image
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    
    # Split LAB channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    
    # Merge channels back
    lab_clahe = cv2.merge((l_clahe, a, b))
    
    # Convert back to RGB
    img_clahe = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2RGB)
    
    return img_clahe


def apply_sharpening(img):
    """
    Apply unsharp masking for image sharpening
    
    Args:
        img: RGB image as numpy array
    
    Returns:
        Sharpened RGB image
    """
    # Create Gaussian blur
    blur = cv2.GaussianBlur(img, (0, 0), sigmaX=1, sigmaY=1)
    
    # Unsharp mask: original + (original - blur) * amount
    # Using addWeighted: img * 1.5 + blur * (-0.5)
    img_sharp = cv2.addWeighted(img, 1.5, blur, -0.5, 0)
    
    return img_sharp


def preprocess_batch(image_paths, output_dir=None):
    """
    Preprocess multiple images
    
    Args:
        image_paths: List of image paths
        output_dir: Optional directory to save processed images
    
    Returns:
        List of preprocessed images
    """
    results = []
    
    for img_path in image_paths:
        preprocessed = preprocess_leaf(img_path, output_dir)
        if preprocessed is not None:
            results.append(preprocessed)
        else:
            print(f"Warning: Failed to preprocess {img_path}")
    
    return results


if __name__ == "__main__":
    # Test preprocessing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python preprocessing.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = "preprocessed_output"
    
    print(f"Preprocessing {image_path}...")
    result = preprocess_leaf(image_path, output_dir)
    
    if result is not None:
        print("Preprocessing complete!")
        print(f"Output shape: {result.shape}")
    else:
        print("Preprocessing failed!")
