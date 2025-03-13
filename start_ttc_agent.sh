#!/bin/bash

# Start the ttc_agent backend
start_backend() {
    echo "Starting ttc_agent backend..."
    cd "$(dirname "$0")"
    # Using python -m to run the module
    python -m ttc_agent.chat_app &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
}

# Wait for backend to be ready
wait_for_backend() {
    echo "Waiting for backend to be ready..."
    # Try to connect to the backend server
    max_attempts=60  # Increased to 60 seconds
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        # Check if the process is still running
        if ! ps -p $BACKEND_PID > /dev/null; then
            echo "Backend process died unexpectedly."
            return 1
        fi
        
        # Try to connect to the backend server
        if curl -s http://127.0.0.1:8000 > /dev/null 2>&1; then
            echo "Backend is responding on http://127.0.0.1:8000"
            # Additional check for specific endpoints
            if curl -s http://127.0.0.1:8000/conversations > /dev/null 2>&1; then
                echo "Backend API endpoints are ready!"
                return 0
            fi
        fi
        
        attempt=$((attempt+1))
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "Waiting for backend to start... ($attempt/$max_attempts)"
        fi
        sleep 1
    done
    echo "Backend failed to start within the expected time."
    return 1
}

# Start the React frontend
start_frontend() {
    echo "Starting ttc_agent frontend..."
    # Save current directory
    CURRENT_DIR=$(pwd)
    cd "$(dirname "$0")/ttc_agent/react_frontend"
    npm run dev &
    FRONTEND_PID=$!
    # Return to original directory
    cd "$CURRENT_DIR"
    echo "Frontend started with PID: $FRONTEND_PID"
}

# Handle script termination
cleanup() {
    echo "Stopping ttc_agent services..."
    # Kill the processes when the script is terminated
    if [ -n "$BACKEND_PID" ]; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ -n "$FRONTEND_PID" ]; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    echo "All services stopped."
    exit 0
}

# Set up trap to catch termination signals
trap cleanup SIGINT SIGTERM

# Start both services
echo "=== Starting ttc_agent services ==="
start_backend
if ! wait_for_backend; then
    echo "ERROR: Failed to start backend. Exiting."
    cleanup
    exit 1
fi

echo "=== Backend is ready, starting frontend ==="
start_frontend

echo "=== Both services are running ==="
echo "Backend: http://127.0.0.1:8000"
echo "Frontend: http://localhost:5173 (or another port if 5173 is in use)"
echo "Press Ctrl+C to stop all services."

# Keep the script running
wait  