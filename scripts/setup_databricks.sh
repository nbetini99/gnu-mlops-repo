#!/bin/bash
# Databricks Setup Script
# This script sets up the Databricks workspace for MLOps

set -e

echo "========================================="
echo "GNU MLOps - Databricks Setup"
echo "========================================="

# Check if required environment variables are set
if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo "Error: DATABRICKS_HOST and DATABRICKS_TOKEN must be set"
    echo "Please create a .env file with these variables or export them"
    exit 1
fi

echo "✓ Environment variables configured"

# Configure Databricks CLI
echo "Configuring Databricks CLI..."
databricks configure --token <<EOF
$DATABRICKS_HOST
$DATABRICKS_TOKEN
EOF

echo "✓ Databricks CLI configured"

# Create workspace directory
echo "Creating workspace directory..."
databricks workspace mkdirs /Users/nbetini@gmail.com/gnu-mlops/liveprod || true
databricks workspace mkdirs /Users/nbetini@gmail.com/gnu-mlops/experiments || true

echo "✓ Workspace directories created"

# Upload source files to Databricks
echo "Uploading source files..."
databricks workspace import-dir src /Users/nbetini@gmail.com/gnu-mlops/liveprod/src --overwrite

echo "✓ Source files uploaded"

# Create MLflow experiment
echo "Creating MLflow experiment..."
databricks experiments create --experiment-name "/Users/nbetini@gmail.com/gnu-mlops/experiments" || true

echo "✓ MLflow experiment created"

echo ""
echo "========================================="
echo "Setup completed successfully!"
echo "========================================="
echo "Next steps:"
echo "1. Run: python src/train_model.py"
echo "2. Deploy: python src/deploy_model.py --stage staging"
echo "========================================="

