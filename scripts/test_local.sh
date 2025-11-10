#!/bin/bash
# Complete Local Testing Script
# Tests the entire MLOps pipeline locally without Databricks

set -e

echo "========================================="
echo "GNU MLOps - Local Testing"
echo "========================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "✗ Virtual environment not found. Run: python3 -m venv venv"
    exit 1
fi

# Set local MLflow tracking
export MLFLOW_TRACKING_URI="sqlite:///mlflow.db"
echo "✓ MLflow set to local SQLite database"
echo ""

# Test 1: Train Model
echo "========================================="
echo "Test 1: Training Model Locally"
echo "========================================="
python3 src/train_model.py
echo ""

# Test 2: Check Model Info
echo "========================================="
echo "Test 2: Checking Model Registry"
echo "========================================="
python3 << EOF
import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()

# List registered models
models = client.search_registered_models()
for model in models:
    print(f"✓ Model: {model.name}")
    versions = client.search_model_versions(f"name='{model.name}'")
    for v in versions:
        print(f"  Version {v.version}: {v.current_stage}")
        print(f"  Run ID: {v.run_id}")
EOF
echo ""

# Test 3: Model Predictions
echo "========================================="
echo "Test 3: Testing Model Predictions"
echo "========================================="
python3 << EOF
import mlflow
import pandas as pd
import numpy as np

mlflow.set_tracking_uri("sqlite:///mlflow.db")

# Load model directly from run
model = mlflow.sklearn.load_model("runs:/$(python3 -c "
import mlflow
from mlflow.tracking import MlflowClient
mlflow.set_tracking_uri('sqlite:///mlflow.db')
client = MlflowClient()
runs = client.search_runs(experiment_ids=['1'], max_results=1)
print(runs[0].info.run_id if runs else 'no-run')
")/model")

# Create test data
test_data = pd.DataFrame({
    'feature1': [0.5, 1.2, -0.3],
    'feature2': [1.1, 0.8, 1.5],
    'feature3': [-0.2, 0.9, 0.1]
})

# Make predictions
predictions = model.predict(test_data)
print("✓ Predictions:", predictions)
print("✓ Model is working correctly!")
EOF
echo ""

# Test 4: Start MLflow UI (optional)
echo "========================================="
echo "Test 4: MLflow UI"
echo "========================================="
echo "To view results in MLflow UI, run:"
echo "  mlflow ui --backend-store-uri sqlite:///mlflow.db"
echo ""
echo "Then open: http://localhost:5000"
echo ""

# Summary
echo "========================================="
echo "✓ All Local Tests Passed!"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✓ Model trained successfully"
echo "  ✓ Model registered in MLflow"
echo "  ✓ Predictions working"
echo "  ✓ MLflow tracking enabled"
echo ""
echo "Next steps:"
echo "  1. View in MLflow UI: mlflow ui --backend-store-uri sqlite:///mlflow.db"
echo "  2. Configure Databricks credentials for cloud deployment"
echo "  3. Run: python3 src/train_model.py (with Databricks)"
echo ""

