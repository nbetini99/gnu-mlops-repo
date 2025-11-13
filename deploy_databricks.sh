#!/bin/bash
# Databricks Deployment Script
# Automated deployment to Databricks with your credentials

set -e

echo "========================================="
echo "GNU MLOps - Databricks Deployment"
echo "========================================="
echo ""

# Set Databricks credentials
export DATABRICKS_HOST="https://diba-5e288a33-e706.cloud.databricks.com"
export DATABRICKS_TOKEN="dapicb7282387c50cc9aa3e8e3d18378b5fd"
export MLFLOW_TRACKING_URI="databricks"

echo "✓ Databricks credentials configured"
echo "  Host: $DATABRICKS_HOST"
echo "  Token: ${DATABRICKS_TOKEN:0:15}..."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "✗ Virtual environment not found"
    echo "  Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Test Databricks connection
echo ""
echo "========================================="
echo "Step 1: Testing Databricks Connection"
echo "========================================="
python3 << 'EOF'
import mlflow
import sys

try:
    mlflow.set_tracking_uri("databricks")
    experiments = mlflow.search_experiments(max_results=1)
    print("✓ Successfully connected to Databricks MLflow")
    print(f"✓ Authentication successful")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "✗ Connection test failed"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 2: Training Model on Databricks"
echo "========================================="
python3 src/train_model.py

if [ $? -ne 0 ]; then
    echo "✗ Training failed"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 3: Deploying to Staging"
echo "========================================="
python3 src/deploy_model.py --stage staging

echo ""
echo "========================================="
echo "Step 4: Checking Model Info"
echo "========================================="
python3 src/deploy_model.py --stage info

echo ""
echo "========================================="
echo "Deployment to Staging Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Review model in Databricks MLflow UI"
echo "  2. Validate model performance"
echo "  3. Deploy to production:"
echo "     python3 src/deploy_model.py --stage production"
echo ""
echo "MLflow UI: https://diba-5e288a33-e706.cloud.databricks.com/#mlflow"
echo ""

