"""
ShuffleNet classification module for Plantalyze
Loads ShuffleNet model with 4-channel input (RGB + Mask) for disease classification
"""

import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np


def load_shufflenet_model(checkpoint_path, num_classes=26):
    """
    Load ShuffleNet v2 model with 4-channel input and custom number of classes
    
    Args:
        checkpoint_path: Path to model checkpoint (.pth file)
        num_classes: Number of disease classes (default: 26)
    
    Returns:
        Tuple of (model, device)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    try:
        # Create ShuffleNet v2 base model
        model = models.shufflenet_v2_x1_0(pretrained=False)
        
        # Modify first convolutional layer to accept 4 channels (RGB + Mask)
        old_conv = model.conv1[0]
        new_conv = nn.Conv2d(
            in_channels=4,          # 4 channels instead of 3 (RGB + mask)
            out_channels=24,
            kernel_size=3,
            stride=2,
            padding=1,
            bias=False
        )
        
        # Initialize new conv layer weights
        # Copy pretrained weights for first 3 channels (RGB)
        with torch.no_grad():
            new_conv.weight[:, :3, :, :] = old_conv.weight
            # Initialize 4th channel (mask) with small random values
            new_conv.weight[:, 3:, :, :] = old_conv.weight[:, :1, :, :] * 0.01
        
        model.conv1[0] = new_conv
        
        # Modify classifier for custom number of classes
        if hasattr(model, 'fc'):
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, num_classes)
        elif hasattr(model, 'classifier'):
            in_features = model.classifier.in_features
            model.classifier = nn.Linear(in_features, num_classes)
        else:
            raise ValueError("Model has no 'fc' or 'classifier' attribute")
        
        # Load checkpoint
        if not os.path.exists(checkpoint_path):
            print(f"Error: Checkpoint file not found at {checkpoint_path}")
            return None, device
        
        print(f"Loading checkpoint from {checkpoint_path}...")
        checkpoint = torch.load(checkpoint_path, map_location=device)
        
        # Extract state dict
        if 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        elif 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
        
        # Remove 'module.' prefix if present (from DataParallel)
        new_state_dict = {}
        for k, v in state_dict.items():
            new_key = k.replace("module.", "")
            new_state_dict[new_key] = v
        
        # Load weights (strict=False to allow minor mismatches)
        missing_keys, unexpected_keys = model.load_state_dict(new_state_dict, strict=False)
        
        if missing_keys:
            print(f"   Warning: Missing keys in checkpoint: {missing_keys[:5]}...")  # Show first 5
        if unexpected_keys:
            print(f"   Warning: Unexpected keys in checkpoint: {unexpected_keys[:5]}...")
        
        print("Checkpoint loaded successfully!")
        
        # Move model to device and set to evaluation mode
        model = model.to(device)
        model.eval()
        
        return model, device
        
    except Exception as e:
        print(f"Error loading ShuffleNet model: {e}")
        import traceback
        traceback.print_exc()
        return None, device


def predict_disease(input_path, model, device, class_names):
    """
    Predict disease class from 4-channel input
    
    Args:
        input_path: Path to input (.npy file containing 4-channel array or RGB image)
        model: Loaded ShuffleNet model
        device: Torch device (CPU or CUDA)
        class_names: List of disease class names
    
    Returns:
        Tuple of (predicted_label, confidence)
    """
    if model is None:
        print("Error: Model is None")
        return None, None
    
    try:
        # Load input
        if str(input_path).endswith(".npy"):
            # Load 4-channel numpy array
            img_array = np.load(input_path).astype(np.float32)
            
            print(f"Loaded 4-channel input shape: {img_array.shape}")
            print(f"Channel 0 (R) range: [{img_array[:,:,0].min():.3f}, {img_array[:,:,0].max():.3f}]")
            print(f"Channel 1 (G) range: [{img_array[:,:,1].min():.3f}, {img_array[:,:,1].max():.3f}]")
            print(f"Channel 2 (B) range: [{img_array[:,:,2].min():.3f}, {img_array[:,:,2].max():.3f}]")
            print(f"Channel 3 (Mask) range: [{img_array[:,:,3].min():.3f}, {img_array[:,:,3].max():.3f}]")
            
            # Check mask channel statistics
            mask_channel = img_array[:,:,3]
            unique_mask_values = np.unique(mask_channel)
            print(f"Mask channel unique values: {unique_mask_values[:10]}")  # First 10
            
            # Ensure shape is (H, W, 4)
            if img_array.ndim != 3 or img_array.shape[2] != 4:
                print(f"Error: Expected 4-channel input, got shape {img_array.shape}")
                return None, None
            
            # Resize to 224x224 if needed
            if img_array.shape[:2] != (224, 224):
                from PIL import Image
                # Split channels
                rgb = img_array[:, :, :3]
                mask = img_array[:, :, 3]
                
                # Resize each component
                rgb_pil = Image.fromarray((rgb * 255).astype(np.uint8))
                rgb_resized = np.array(rgb_pil.resize((224, 224))) / 255.0
                
                mask_pil = Image.fromarray((mask * 255).astype(np.uint8))
                mask_resized = np.array(mask_pil.resize((224, 224))) / 255.0
                
                # Recombine
                img_array = np.concatenate([rgb_resized, mask_resized[..., None]], axis=2)
            
            # Convert to tensor: (H, W, C) -> (C, H, W)
            img_tensor = torch.from_numpy(img_array.transpose(2, 0, 1)).unsqueeze(0)
            
            # Normalize (using ImageNet stats for RGB, pass-through for mask)
            mean = [0.485, 0.456, 0.406, 0.0]
            std = [0.229, 0.224, 0.225, 1.0]
            
            for c in range(4):
                img_tensor[0, c, :, :] = (img_tensor[0, c, :, :] - mean[c]) / std[c]
        
        else:
            # Load as regular RGB image (for testing purposes)
            image = Image.open(input_path).convert('RGB')
            
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            img_tensor = transform(image).unsqueeze(0)
            
            # Add dummy mask channel (zeros)
            dummy_mask = torch.zeros(1, 1, 224, 224)
            img_tensor = torch.cat([img_tensor, dummy_mask], dim=1)
        
        # Move to device
        img_tensor = img_tensor.to(device)
        
        # Predict
        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
        
        # Get predicted class
        predicted_idx = int(predicted_idx.item())
        confidence_val = float(confidence.item())
        
        if predicted_idx < len(class_names):
            predicted_label = class_names[predicted_idx]
        else:
            predicted_label = f"Class_{predicted_idx}"
        
        print(f"Prediction: {predicted_label} (confidence: {confidence_val:.2%})")
        
        return predicted_label, confidence_val
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def get_top_k_predictions(input_path, model, device, class_names, k=3):
    """
    Get top-k disease predictions
    
    Args:
        input_path: Path to input file
        model: Loaded ShuffleNet model
        device: Torch device
        class_names: List of disease class names
        k: Number of top predictions to return
    
    Returns:
        List of tuples (class_name, confidence)
    """
    if model is None:
        return []
    
    try:
        # Load and preprocess input (similar to predict_disease)
        if str(input_path).endswith(".npy"):
            img_array = np.load(input_path).astype(np.float32)
            img_tensor = torch.from_numpy(img_array.transpose(2, 0, 1)).unsqueeze(0)
            
            mean = [0.485, 0.456, 0.406, 0.0]
            std = [0.229, 0.224, 0.225, 1.0]
            
            for c in range(4):
                img_tensor[0, c, :, :] = (img_tensor[0, c, :, :] - mean[c]) / std[c]
        else:
            image = Image.open(input_path).convert('RGB')
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            img_tensor = transform(image).unsqueeze(0)
            dummy_mask = torch.zeros(1, 1, 224, 224)
            img_tensor = torch.cat([img_tensor, dummy_mask], dim=1)
        
        img_tensor = img_tensor.to(device)
        
        # Get predictions
        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
        
        # Get top-k
        top_k_probs, top_k_indices = torch.topk(probabilities, k=min(k, len(class_names)))
        
        results = []
        for prob, idx in zip(top_k_probs, top_k_indices):
            idx = int(idx.item())
            prob = float(prob.item())
            label = class_names[idx] if idx < len(class_names) else f"Class_{idx}"
            results.append((label, prob))
        
        return results
        
    except Exception as e:
        print(f"Error getting top-k predictions: {e}")
        return []


if __name__ == "__main__":
    # Test classification
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python classification.py <model_path> <input_path> [num_classes]")
        sys.exit(1)
    
    model_path = sys.argv[1]
    input_path = sys.argv[2]
    num_classes = int(sys.argv[3]) if len(sys.argv) > 3 else 35  # Default to 35 classes
    
    # Example class names (35 classes - PlantVillage dataset)
    class_names = [
        "Apple___Apple_scab",
        "Apple___Black_rot",
        "Apple___Cedar_apple_rust",
        "Apple___healthy",
        "Cherry___Powdery_mildew",
        "Cherry___healthy",
        "Corn___Cercospora_leaf_spot Gray_leaf_spot",
        "Corn___Common_rust",
        "Corn___Northern_Leaf_Blight",
        "Corn___healthy",
        "Grape___Black_rot",
        "Grape___Esca_(Black_Measles)",
        "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
        "Grape___healthy",
        "Peach___Bacterial_spot",
        "Peach___healthy",
        "Pepper,_bell___Bacterial_spot",
        "Pepper,_bell___healthy",
        "Potato___Early_blight",
        "Potato___Late_blight",
        "Potato___healthy",
        "Squash___Powdery_mildew",
        "Strawberry___Leaf_scorch",
        "Strawberry___healthy",
        "Tomato___Bacterial_spot",
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___Leaf_Mold",
        "Tomato___Septoria_leaf_spot",
        "Tomato___Spider_mites_Two-spotted_spider_mite",
        "Tomato___Target_Spot",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "Tomato___Tomato_mosaic_virus",
        "Tomato___healthy",
        "Background_without_leaves"
    ]
    
    print("Loading model...")
    model, device = load_shufflenet_model(model_path, num_classes)
    
    if model is None:
        print("Failed to load model!")
        sys.exit(1)
    
    print(f"Predicting for {input_path}...")
    label, confidence = predict_disease(input_path, model, device, class_names)
    
    if label:
        print(f"\nPrediction: {label}")
        print(f"Confidence: {confidence:.2%}")
        
        print("\nTop 3 predictions:")
        top_3 = get_top_k_predictions(input_path, model, device, class_names, k=3)
        for i, (lbl, conf) in enumerate(top_3, 1):
            print(f"{i}. {lbl}: {conf:.2%}")
    else:
        print("Prediction failed!")
