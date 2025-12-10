# Gunicorn configuration for Railway deployment
import multiprocessing
import os

# Bind to PORT provided by Railway
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Worker configuration
# For ML models, use fewer workers to reduce memory usage
# TensorFlow/PyTorch models can be memory-intensive
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Longer timeout for ML inference

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "plantalyze-api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (Railway handles this)
keyfile = None
certfile = None
