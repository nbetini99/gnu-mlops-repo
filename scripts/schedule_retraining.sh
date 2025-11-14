#!/bin/bash
# Automatic Retraining Scheduler Setup
# Author: Narsimha Betini
# Purpose: Set up cron job for automatic retraining every 30 days

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     GNU MLOps - Automatic Retraining Scheduler Setup     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_DIR/venv"
PYTHON_PATH="$VENV_PATH/bin/python"
RETRAIN_SCRIPT="$PROJECT_DIR/src/retrain_model.py"
CONFIG_PATH="$PROJECT_DIR/config.yaml"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}⚠ Warning: Virtual environment not found at $VENV_PATH${NC}"
    echo "Please create it first: python -m venv venv"
    exit 1
fi

# Check if retrain script exists
if [ ! -f "$RETRAIN_SCRIPT" ]; then
    echo -e "${YELLOW}⚠ Error: Retraining script not found at $RETRAIN_SCRIPT${NC}"
    exit 1
fi

# Check if config exists
if [ ! -f "$CONFIG_PATH" ]; then
    echo -e "${YELLOW}⚠ Warning: Config file not found at $CONFIG_PATH${NC}"
    echo "Using default config.yaml"
fi

echo -e "${GREEN}✓ Project directory: $PROJECT_DIR${NC}"
echo -e "${GREEN}✓ Python: $PYTHON_PATH${NC}"
echo -e "${GREEN}✓ Retrain script: $RETRAIN_SCRIPT${NC}"
echo ""

# Create log directory
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓ Log directory: $LOG_DIR${NC}"
echo ""

# Ask user for schedule preference
echo "Select retraining schedule:"
echo "  1) Daily (for testing)"
echo "  2) Weekly (every Monday at 2 AM)"
echo "  3) Monthly (1st of month at 2 AM)"
echo "  4) Every 30 days (custom cron)"
echo "  5) Custom cron expression"
echo ""
read -p "Enter choice [1-5] (default: 4): " choice
choice=${choice:-4}

case $choice in
    1)
        CRON_SCHEDULE="0 2 * * *"  # Daily at 2 AM
        SCHEDULE_DESC="Daily at 2:00 AM"
        ;;
    2)
        CRON_SCHEDULE="0 2 * * 1"  # Every Monday at 2 AM
        SCHEDULE_DESC="Every Monday at 2:00 AM"
        ;;
    3)
        CRON_SCHEDULE="0 2 1 * *"  # 1st of month at 2 AM
        SCHEDULE_DESC="1st of each month at 2:00 AM"
        ;;
    4)
        # Every 30 days - run on 1st and 15th of month (approximation)
        CRON_SCHEDULE="0 2 1,15 * *"  # 1st and 15th at 2 AM
        SCHEDULE_DESC="1st and 15th of each month at 2:00 AM (every ~30 days)"
        ;;
    5)
        echo ""
        echo "Enter custom cron expression (minute hour day month weekday):"
        echo "Example: '0 2 * * *' = Daily at 2 AM"
        read -p "Cron expression: " CRON_SCHEDULE
        SCHEDULE_DESC="Custom: $CRON_SCHEDULE"
        ;;
    *)
        echo -e "${YELLOW}Invalid choice, using default (every 30 days)${NC}"
        CRON_SCHEDULE="0 2 1,15 * *"
        SCHEDULE_DESC="1st and 15th of each month at 2:00 AM"
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
CRON_JOB="$CRON_SCHEDULE cd $PROJECT_DIR && $ENV_SETUP && $PYTHON_PATH $RETRAIN_SCRIPT --config $CONFIG_PATH >> $LOG_DIR/cron_retraining.log 2>&1"

# Check if cron job already exists
CRON_TMP=$(mktemp)
crontab -l 2>/dev/null > "$CRON_TMP" || true

if grep -q "retrain_model.py" "$CRON_TMP" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Existing retraining cron job found!${NC}"
    echo ""
    echo "Current cron jobs:"
    grep "retrain_model.py" "$CRON_TMP" || true
    echo ""
    read -p "Replace existing job? [y/N]: " replace
    if [[ "$replace" =~ ^[Yy]$ ]]; then
        # Remove old job
        grep -v "retrain_model.py" "$CRON_TMP" > "${CRON_TMP}.new" || true
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
echo -e "${GREEN}║              ✅ SCHEDULER SETUP COMPLETE! ✅                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Retraining Schedule: $SCHEDULE_DESC"
echo ""
echo "View scheduled jobs:"
echo "  crontab -l"
echo ""
echo "Edit schedule:"
echo "  crontab -e"
echo ""
echo "Remove schedule:"
echo "  crontab -e  # Then delete the retrain_model.py line"
echo ""
echo "Test retraining manually:"
echo "  cd $PROJECT_DIR"
echo "  source venv/bin/activate"
echo "  python src/retrain_model.py"
echo ""
echo "Force retraining (ignore schedule):"
echo "  python src/retrain_model.py --force"
echo ""
echo "View logs:"
echo "  tail -f $LOG_DIR/cron_retraining.log"
echo "  ls -lh $LOG_DIR/retraining_*.log"
echo ""

