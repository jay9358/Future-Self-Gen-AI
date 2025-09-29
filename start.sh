#!/bin/bash

# Set default port if PORT is not set
export PORT=${PORT:-5000}

# Start the application
echo "Starting Future Self AI Backend on port $PORT"
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --chdir backend app:app
