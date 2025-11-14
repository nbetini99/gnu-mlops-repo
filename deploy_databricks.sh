#!/bin/bash
# Databricks Deployment Script
# Automated deployment to Databricks with your credentials

set -e

echo "========================================="
echo "GNU MLOps - Databricks Deployment"
echo "========================================="
echo ""

# SECURITY: Read Databricks credentials from environment variables
# NEVER hardcode credentials in scripts!
# Set these in your environment or .env file:
#   export DATABRICKS_HOST="https://dbc-5e289a33-a706.cloud.databricks.com"
#   export DATABRICKS_TOKEN="your-token-here"
#   export DATABRICKS_WORKSPACE_PATH="/Users/nbatink@gmail.com/gnu-mlops/liveprod"  # Optional
#   export DATABRICKS_EXPERIMENT_PATH="/Users/nbatink@gmail.com/gnu-mlops/experiments"  # Optional

# Check if credentials are set
if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo "✗ Error: DATABRICKS_HOST and DATABRICKS_TOKEN must be set"
    echo ""
    echo "Please set these environment variables:"
    echo "  export DATABRICKS_HOST='https://dbc-5e289a33-a706.cloud.databricks.com'"
    echo "  export DATABRICKS_TOKEN='your-token-here'"
    echo ""
    echo "Or create a .env file with:"
    echo "  DATABRICKS_HOST=https://dbc-5e289a33-a706.cloud.databricks.com"
    echo "  DATABRICKS_TOKEN=your-token-here"
    echo ""
    echo "Then source it:"
    echo "  source .env"
    exit 1
fi

# Set MLflow tracking URI
export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-databricks}"

# Set optional paths if not already set
export DATABRICKS_WORKSPACE_PATH="${DATABRICKS_WORKSPACE_PATH:-/Users/nbatink@gmail.com/gnu-mlops/liveprod}"
export DATABRICKS_EXPERIMENT_PATH="${DATABRICKS_EXPERIMENT_PATH:-/Users/nbatink@gmail.com/gnu-mlops/experiments}"

echo "✓ Databricks credentials configured from environment variables"
echo "  Host: $DATABRICKS_HOST"
echo "  Token: ${DATABRICKS_TOKEN:0:15}..."
echo "  Workspace Path: $DATABRICKS_WORKSPACE_PATH"
echo "  Experiment Path: $DATABRICKS_EXPERIMENT_PATH"
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
echo "MLflow UI: https://dbc-5e289a33-a706.cloud.databricks.com/#mlflow"
echo ""

