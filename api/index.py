"""
Main Vercel Serverless API Handler
Routes requests to appropriate endpoints
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

# Import handlers
from health import health as health_handler
from analyze import analyze as analyze_handler

app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins, configure for production

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return health_handler()

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """Leaf analysis endpoint"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    return analyze_handler()

# For local testing
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
