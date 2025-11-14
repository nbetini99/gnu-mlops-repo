#!/bin/bash
# Environment Setup Script
# SECURITY: This script reads credentials from .env file or prompts for them
# NEVER hardcode credentials in this file!

# Check if .env file exists and source it
if [ -f ".env" ]; then
    echo "Loading credentials from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ Credentials loaded from .env file"
else
    echo "⚠ .env file not found"
    echo ""
    echo "Please create a .env file with:"
    echo "  DATABRICKS_HOST=https://dbc-5e289a33-a706.cloud.databricks.com"
    echo "  DATABRICKS_TOKEN=your-token-here"
    echo "  DATABRICKS_WORKSPACE_PATH=/Users/nbatink@gmail.com/gnu-mlops/liveprod"
    echo "  DATABRICKS_EXPERIMENT_PATH=/Users/nbatink@gmail.com/gnu-mlops/experiments"
    echo "  MLFLOW_TRACKING_URI=databricks"
    echo ""
    echo "Or set environment variables manually:"
    echo "  export DATABRICKS_HOST='https://dbc-5e289a33-a706.cloud.databricks.com'"
    echo "  export DATABRICKS_TOKEN='your-token-here'"
    echo ""
    exit 1
fi

# Set defaults if not provided
export DATABRICKS_HOST="${DATABRICKS_HOST:-https://dbc-5e289a33-a706.cloud.databricks.com}"
export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-databricks}"
export DATABRICKS_WORKSPACE_PATH="${DATABRICKS_WORKSPACE_PATH:-/Users/nbatink@gmail.com/gnu-mlops/liveprod}"
export DATABRICKS_EXPERIMENT_PATH="${DATABRICKS_EXPERIMENT_PATH:-/Users/nbatink@gmail.com/gnu-mlops/experiments}"

# Validate required variables
if [ -z "$DATABRICKS_TOKEN" ]; then
    echo "✗ Error: DATABRICKS_TOKEN must be set"
    echo "  Please set it in .env file or export it"
    exit 1
fi

echo "✓ Environment variables configured"
echo "  Host: $DATABRICKS_HOST"
echo "  Token: ${DATABRICKS_TOKEN:0:15}..."
echo "  Workspace Path: $DATABRICKS_WORKSPACE_PATH"
echo "  Experiment Path: $DATABRICKS_EXPERIMENT_PATH"
echo "  MLflow URI: $MLFLOW_TRACKING_URI"

