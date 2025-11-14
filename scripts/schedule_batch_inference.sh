#!/bin/bash
# Daily Batch Inference Scheduler Setup
# Author: Narsimha Betini
# Purpose: Set up cron job for daily batch inference at 1 PM PST

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     GNU MLOps - Daily Batch Inference Scheduler Setup      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_DIR/venv"
PYTHON_PATH="$VENV_PATH/bin/python"
BATCH_SCRIPT="$PROJECT_DIR/src/batch_inference.py"
CONFIG_PATH="$PROJECT_DIR/config.yaml"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}⚠ Warning: Virtual environment not found at $VENV_PATH${NC}"
    echo "Please create it first: python -m venv venv"
    exit 1
fi

# Check if batch inference script exists
if [ ! -f "$BATCH_SCRIPT" ]; then
    echo -e "${YELLOW}⚠ Error: Batch inference script not found at $BATCH_SCRIPT${NC}"
    exit 1
fi

# Check if config exists
if [ ! -f "$CONFIG_PATH" ]; then
    echo -e "${YELLOW}⚠ Warning: Config file not found at $CONFIG_PATH${NC}"
    echo "Using default config.yaml"
fi

echo -e "${GREEN}✓ Project directory: $PROJECT_DIR${NC}"
echo -e "${GREEN}✓ Python: $PYTHON_PATH${NC}"
echo -e "${GREEN}✓ Batch inference script: $BATCH_SCRIPT${NC}"
echo ""

# Create data directories
BATCH_INPUT_DIR="$PROJECT_DIR/data/batch_input"
BATCH_OUTPUT_DIR="$PROJECT_DIR/data/batch_output"
BATCH_ARCHIVE_DIR="$PROJECT_DIR/data/batch_archive"

mkdir -p "$BATCH_INPUT_DIR"
mkdir -p "$BATCH_OUTPUT_DIR"
mkdir -p "$BATCH_ARCHIVE_DIR"

echo -e "${GREEN}✓ Input directory: $BATCH_INPUT_DIR${NC}"
echo -e "${GREEN}✓ Output directory: $BATCH_OUTPUT_DIR${NC}"
echo -e "${GREEN}✓ Archive directory: $BATCH_ARCHIVE_DIR${NC}"
echo ""

# Create log directory
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓ Log directory: $LOG_DIR${NC}"
echo ""

# Ask user for time preference
echo "Select batch inference schedule:"
echo "  1) Daily at 1:00 PM PST (13:00 local time)"
echo "  2) Daily at 1:00 PM PST (21:00 UTC - for servers)"
echo "  3) Daily at 2:00 PM PST (14:00 local time)"
echo "  4) Custom time"
echo ""
read -p "Enter choice [1-4] (default: 1): " choice
choice=${choice:-1}

case $choice in
    1)
        CRON_SCHEDULE="0 13 * * *"  # 1 PM local time (PST)
        SCHEDULE_DESC="Daily at 1:00 PM PST (13:00 local time)"
        ;;
    2)
        CRON_SCHEDULE="0 21 * * *"  # 1 PM PST = 9 PM UTC (PST is UTC-8)
        SCHEDULE_DESC="Daily at 1:00 PM PST (21:00 UTC)"
        ;;
    3)
        CRON_SCHEDULE="0 14 * * *"  # 2 PM local time
        SCHEDULE_DESC="Daily at 2:00 PM PST (14:00 local time)"
        ;;
    4)
        echo ""
        echo "Enter custom cron expression (minute hour day month weekday):"
        echo "Example: '0 13 * * *' = Daily at 1:00 PM"
        read -p "Cron expression: " CRON_SCHEDULE
        SCHEDULE_DESC="Custom: $CRON_SCHEDULE"
        ;;
    *)
        echo -e "${YELLOW}Invalid choice, using default (1 PM PST)${NC}"
        CRON_SCHEDULE="0 13 * * *"
        SCHEDULE_DESC="Daily at 1:00 PM PST (13:00 local time)"
        ;;
esac

echo ""
echo -e "${BLUE}Schedule: $SCHEDULE_DESC${NC}"
echo ""

# Set up environment variables for cron
ENV_SETUP="MLFLOW_TRACKING_URI=sqlite:///mlflow.db"
ENV_SETUP="$ENV_SETUP\nPATH=$PATH"
ENV_SETUP="$ENV_SETUP\nHOME=$HOME"

# Create cron job entry
CRON_JOB="$CRON_SCHEDULE cd $PROJECT_DIR && $ENV_SETUP && $PYTHON_PATH $BATCH_SCRIPT --config $CONFIG_PATH >> $LOG_DIR/cron_batch_inference.log 2>&1"

# Check if cron job already exists
CRON_TMP=$(mktemp)
crontab -l 2>/dev/null > "$CRON_TMP" || true

if grep -q "batch_inference.py" "$CRON_TMP" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Existing batch inference cron job found!${NC}"
    echo ""
    echo "Current cron jobs:"
    grep "batch_inference.py" "$CRON_TMP" || true
    echo ""
    read -p "Replace existing job? [y/N]: " replace
    if [[ "$replace" =~ ^[Yy]$ ]]; then
        # Remove old job
        grep -v "batch_inference.py" "$CRON_TMP" > "${CRON_TMP}.new" || true
        mv "${CRON_TMP}.new" "$CRON_TMP"
        # Add new job
        echo -e "$CRON_JOB" >> "$CRON_TMP"
        crontab "$CRON_TMP"
        echo -e "${GREEN}✓ Cron job updated${NC}"
    else
        echo "Keeping existing cron job. Exiting."
        rm "$CRON_TMP"
        exit 0
    fi
else
    # Add new cron job
    echo -e "$CRON_JOB" >> "$CRON_TMP"
    crontab "$CRON_TMP"
    echo -e "${GREEN}✓ Cron job added${NC}"
fi

rm "$CRON_TMP"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✅ BATCH INFERENCE SCHEDULER SETUP COMPLETE! ✅      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Batch Inference Schedule: $SCHEDULE_DESC"
echo ""
echo "Input directory: $BATCH_INPUT_DIR"
echo "  → Place your daily data files here (CSV or Parquet)"
echo ""
echo "Output directory: $BATCH_OUTPUT_DIR"
echo "  → Predictions will be saved here with timestamps"
echo ""
echo "Archive directory: $BATCH_ARCHIVE_DIR"
echo "  → Processed input files will be archived here"
echo ""
echo "View scheduled jobs:"
echo "  crontab -l"
echo ""
echo "Edit schedule:"
echo "  crontab -e"
echo ""
echo "Remove schedule:"
echo "  crontab -e  # Then delete the batch_inference.py line"
echo ""
echo "Test batch inference manually:"
echo "  cd $PROJECT_DIR"
echo "  source venv/bin/activate"
echo "  # Place test file in input directory:"
echo "  cp test_data.csv $BATCH_INPUT_DIR/"
echo "  python src/batch_inference.py"
echo ""
echo "View logs:"
echo "  tail -f $LOG_DIR/cron_batch_inference.log"
echo "  ls -lh $LOG_DIR/batch_inference_*.log"
echo ""

