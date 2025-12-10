"""
Simple test client to verify backend API is working
Usage: python test_api.py <image_path>
"""

import sys
import base64
import requests
import json
from pathlib import Path

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Health check passed")
            print(f"  Status: {data.get('status')}")
            print(f"  UNet loaded: {data.get('models_loaded', {}).get('unet')}")
            print(f"  ShuffleNet loaded: {data.get('models_loaded', {}).get('shufflenet')}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend. Is it running on http://localhost:5000?")
        return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_analyze(image_path):
    """Test analyze endpoint with an image"""
    print(f"\nTesting /analyze endpoint with {image_path}...")
    
    # Check if file exists
    if not Path(image_path).exists():
        print(f"✗ File not found: {image_path}")
        return False
    
    # Read and encode image
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Determine mime type
        ext = Path(image_path).suffix.lower()
        mime_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }.get(ext, 'image/jpeg')
        
        print(f"  Image size: {len(image_data)} bytes")
        print(f"  MIME type: {mime_type}")
        
    except Exception as e:
        print(f"✗ Failed to read image: {e}")
        return False
    
    # Send request
    try:
        print("  Sending request to backend...")
        response = requests.post(
            "http://localhost:5000/analyze",
            json={
                "image": base64_image,
                "mimeType": mime_type
            },
            timeout=30  # Give it 30 seconds (processing can take time)
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Analysis complete!")
            print("\n" + "=" * 60)
            print("RESULTS:")
            print("=" * 60)
            print(f"Is Leaf: {result.get('isLeaf')}")
            print(f"Disease: {result.get('disease', 'None (Healthy)')}")
            print(f"Confidence: {result.get('confidence', 0) * 100:.1f}%")
            print(f"Description: {result.get('description')}")
            print("=" * 60)
            return True
        else:
            print(f"✗ Analysis failed: {response.status_code}")
            try:
                error = response.json()
                print(f"  Error: {error.get('error', 'Unknown error')}")
            except:
                print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out (>30s). Backend might be slow or stuck.")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend. Is it running?")
        return False
    except Exception as e:
        print(f"✗ Request error: {e}")
        return False


def main():
    print("=" * 60)
    print("Plantalyze Backend API Test Client")
    print("=" * 60)
    print()
    
    # Test health
    if not test_health():
        print("\n❌ Backend is not responding. Please start it first:")
        print("   cd backend")
        print("   python app.py")
        return
    
    # Test analyze if image provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_analyze(image_path)
    else:
        print("\n✓ Backend is running!")
        print("\nTo test image analysis:")
        print("  python test_api.py <path_to_leaf_image.jpg>")


if __name__ == "__main__":
    main()
