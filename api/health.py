"""
Vercel Serverless Function for Health Check
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Plantalyze API is running on Vercel'
    })

# Vercel expects a handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
