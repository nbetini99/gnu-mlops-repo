#!/bin/bash
# Launch MLflow UI with different backend options
# Author: Narsimha Betini
# Usage: ./scripts/launch_mlflow_ui.sh [databricks|sqlite|local] [port]

set -e

# Default values
BACKEND="${1:-databricks}"
PORT="${2:-5000}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🚀 Launching MLflow UI                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

case "$BACKEND" in
    databricks|db)
        echo "📊 Using Databricks MLflow tracking..."
        echo "   Make sure DATABRICKS_HOST and DATABRICKS_TOKEN are set"
        echo ""
        mlflow ui --port "$PORT" --host 0.0.0.0
        ;;
    
    sqlite|local|sql)
        echo "📊 Using SQLite MLflow tracking (local)..."
        echo ""
        
        # Find MLflow database
        if [ -f "mlflow.db" ]; then
            DB_PATH="sqlite:///$(pwd)/mlflow.db"
        elif [ -f "$(pwd)/mlflow.db" ]; then
            DB_PATH="sqlite:///$(pwd)/mlflow.db"
        else
            echo "⚠️  Warning: mlflow.db not found in current directory"
            echo "   Creating new database..."
            DB_PATH="sqlite:///$(pwd)/mlflow.db"
        fi
        
        echo "   Database: $DB_PATH"
        echo "   Artifacts: $(pwd)/mlruns"
        echo ""
        
        mlflow ui \
            --backend-store-uri "$DB_PATH" \
            --default-artifact-root "$(pwd)/mlruns" \
            --port "$PORT" \
            --host 0.0.0.0
        ;;
    
    *)
        echo "❌ Invalid backend option: $BACKEND"
        echo ""
        echo "Usage: $0 [databricks|sqlite] [port]"
        echo ""
        echo "Options:"
        echo "  databricks, db  - Use Databricks MLflow tracking (default)"
        echo "  sqlite, local  - Use SQLite local tracking"
        echo "  port           - Port number (default: 5000)"
        echo ""
        echo "Examples:"
        echo "  $0 databricks     # Launch with Databricks backend"
        echo "  $0 sqlite         # Launch with SQLite backend"
        echo "  $0 sqlite 5001    # Launch SQLite on port 5001"
        exit 1
        ;;
esac

