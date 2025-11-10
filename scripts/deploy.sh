#!/bin/bash
# Deployment Automation Script

set -e

# Default values
STAGE="staging"
VERSION=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --stage)
            STAGE="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./deploy.sh --stage [staging|production] [--version VERSION]"
            exit 1
            ;;
    esac
done

echo "========================================="
echo "GNU MLOps - Model Deployment"
echo "========================================="
echo "Stage: $STAGE"
if [ -n "$VERSION" ]; then
    echo "Version: $VERSION"
fi
echo "========================================="

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Run deployment
echo "Deploying model..."
if [ -n "$VERSION" ]; then
    python src/deploy_model.py --stage $STAGE --version $VERSION
else
    python src/deploy_model.py --stage $STAGE
fi

echo ""
echo "========================================="
echo "Deployment completed!"
echo "========================================="

