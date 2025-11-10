#!/bin/bash
# Training Pipeline Execution Script

set -e

echo "========================================="
echo "GNU MLOps - Training Pipeline"
echo "========================================="

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ Environment variables loaded from .env"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

echo "✓ Dependencies installed"

# Run training
echo ""
echo "Starting model training..."
echo "========================================="
python src/train_model.py

echo ""
echo "========================================="
echo "Training completed!"
echo "Check MLflow UI for experiment results"
echo "========================================="

