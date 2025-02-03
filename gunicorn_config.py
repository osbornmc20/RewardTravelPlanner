# Gunicorn configuration for high concurrency

# Worker configuration
workers = 4  # Number of worker processes
worker_class = 'gevent'  # Use gevent for async handling
worker_connections = 1000  # Maximum number of simultaneous connections

# Timeout configuration
timeout = 120  # Seconds to wait before killing a worker
keepalive = 5  # Seconds to wait between client requests

# Server mechanics
max_requests = 1000  # Restart workers after this many requests
max_requests_jitter = 50  # Add randomness to max_requests

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'  # Log to stderr
loglevel = 'info'

# Server socket
bind = '0.0.0.0:$PORT'  # Bind to all interfaces on the port specified by Render
