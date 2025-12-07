#!/bin/bash

# Socify Backend Startup Script

echo "Starting Socify SIEM Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found. Please create one from .env.example"
    echo "Copy .env.example to .env and configure your AWS credentials"
    exit 1
fi

# Start the backend
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
