#!/bin/bash

# Remembrance Dev Startup Script
echo "========================================="
echo "      STARTING REMEMBRANCE DEV SERVERS"
echo "========================================="

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to kill child processes on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Trap Ctrl+C (SIGINT) and exit signals
trap cleanup SIGINT SIGTERM

# 1. Start Backend API
echo "Starting Python FastAPI Backend..."
cd "$DIR/backend"
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to bind to port 8000..."
sleep 2

# 2. Start Frontend Next.js App on port 1947
echo "Starting Next.js Frontend on port 1947..."
cd "$DIR/frontend"
npm run dev -- -p 1947 &
FRONTEND_PID=$!

# Wait for frontend
sleep 2
echo "========================================="
echo "Servers are running!"
echo "Access Remembrance at: http://localhost:1947"
echo "Press Ctrl+C to stop both servers cleanly."
echo "========================================="

# Try to open browser automatically
if command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:1947" >/dev/null 2>&1 &
fi

# Keep script alive, waiting for child processes
wait
