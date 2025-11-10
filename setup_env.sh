#!/bin/bash
# Environment Setup Script
# Copy this and replace YOUR_TOKEN with your actual Databricks token

export DATABRICKS_HOST="https://diba-5e288a33-e706.cloud.databricks.com"
export DATABRICKS_TOKEN="YOUR_DATABRICKS_TOKEN_HERE"
export MLFLOW_TRACKING_URI="databricks"

echo "Environment variables set!"
echo "Host: $DATABRICKS_HOST"
echo "Token: ${DATABRICKS_TOKEN:0:10}..."
echo "MLflow URI: $MLFLOW_TRACKING_URI"

