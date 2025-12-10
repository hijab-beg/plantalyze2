"""
Quick test script to verify backend setup
Tests model loading without running full server
"""

import sys
from pathlib import Path

print("=" * 60)
print("Plantalyze Backend Setup Verification")
print("=" * 60)
print()

# Check Python version
print("1. Checking Python version...")
if sys.version_info < (3, 8):
    print("   ❌ Python 3.8+ required")
    sys.exit(1)
else:
    print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# Check required packages
print("\n2. Checking required packages...")
required_packages = [
    ('flask', 'Flask'),
    ('flask_cors', 'Flask-CORS'),
    ('cv2', 'OpenCV'),
    ('numpy', 'NumPy'),
    ('PIL', 'Pillow'),
    ('tensorflow', 'TensorFlow'),
    ('torch', 'PyTorch'),
]

missing_packages = []
for module_name, display_name in required_packages:
    try:
        __import__(module_name)
        print(f"   ✓ {display_name}")
    except ImportError:
        print(f"   ❌ {display_name} - NOT INSTALLED")
        missing_packages.append(display_name)

if missing_packages:
    print(f"\n   Missing packages: {', '.join(missing_packages)}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Check model files
print("\n3. Checking model files...")
backend_dir = Path(__file__).parent

unet_path = backend_dir / "unet_model.h5"
shufflenet_path = backend_dir / "Best_ShuffleNet_Model.pth"

if unet_path.exists():
    size_mb = unet_path.stat().st_size / (1024 * 1024)
    print(f"   ✓ UNet model found ({size_mb:.1f} MB)")
else:
    print(f"   ❌ UNet model NOT FOUND at {unet_path}")

if shufflenet_path.exists():
    size_mb = shufflenet_path.stat().st_size / (1024 * 1024)
    print(f"   ✓ ShuffleNet model found ({size_mb:.1f} MB)")
else:
    print(f"   ❌ ShuffleNet model NOT FOUND at {shufflenet_path}")

if not (unet_path.exists() and shufflenet_path.exists()):
    print("\n   Please ensure model files are in the backend directory")
    sys.exit(1)

# Test model loading
print("\n4. Testing model loading...")

try:
    print("   Loading UNet model...")
    from segmentation import load_unet_model
    unet_model = load_unet_model(str(unet_path))
    if unet_model is not None:
        print("   ✓ UNet model loaded successfully")
    else:
        print("   ❌ UNet model failed to load")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ UNet loading error: {e}")
    sys.exit(1)

try:
    print("   Loading ShuffleNet model...")
    from classification import load_shufflenet_model
    shufflenet_model, device = load_shufflenet_model(str(shufflenet_path), num_classes=26)
    if shufflenet_model is not None:
        print(f"   ✓ ShuffleNet model loaded successfully (device: {device})")
    else:
        print("   ❌ ShuffleNet model failed to load")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ ShuffleNet loading error: {e}")
    sys.exit(1)

# Check preprocessing
print("\n5. Testing preprocessing module...")
try:
    from preprocessing import apply_white_balance, apply_clahe, apply_sharpening
    import numpy as np
    import cv2
    
    # Create test image
    test_img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    
    # Test each preprocessing step
    wb_img = apply_white_balance(test_img)
    clahe_img = apply_clahe(wb_img)
    sharp_img = apply_sharpening(clahe_img)
    
    print("   ✓ Preprocessing functions working")
except Exception as e:
    print(f"   ❌ Preprocessing error: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✓ ALL CHECKS PASSED!")
print("=" * 60)
print("\nYour backend is ready to run!")
print("Start the server with: python app.py")
print("Or use: start_backend.bat (Windows) or ./start_backend.sh (Linux/Mac)")
print()
