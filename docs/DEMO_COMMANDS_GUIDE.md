# GNU MLOps Pipeline - Complete Demo Commands Guide

**Author:** Narsimha Betini  
**Purpose:** Comprehensive guide for demonstrating all MLOps pipeline features

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Training](#training)
3. [Deployment](#deployment)
4. [Single Inference](#single-inference)
5. [Batch Inference](#batch-inference)
6. [Daily Scheduled Inference](#daily-scheduled-inference)
7. [Retraining](#retraining)
8. [Model Management](#model-management)
9. [Complete End-to-End Demo](#complete-end-to-end-demo)

---

## 🔧 Prerequisites

### Activate Virtual Environment
```bash
source venv/bin/activate
# or
source .venv/bin/activate
```

### Verify Setup
```bash
python --version
pip list | grep -E "mlflow|pandas|scikit-learn"
```

---

## 🎯 1. Training

### Basic Training
```bash
# Train model with Titanic data
python src/train_model.py
```

### Training with Custom Config
```bash
# Use local config
python src/train_model.py --config config.local.yaml
```

### Expected Output
- Model training metrics (accuracy, precision, recall, F1, ROC-AUC)
- Model registered in MLflow
- Run ID and model version logged

---

## 🚀 2. Deployment

### Deploy to Staging
```bash
# Deploy latest model to Staging (35% accuracy threshold)
python src/deploy_model.py --stage staging
```

### Deploy to Production (GNU_Production)
```bash
# Deploy from Staging to Production (40% accuracy threshold)
python src/deploy_model.py --stage production
# or
python src/deploy_model.py --stage GNU_Production
```

### Check Model Information
```bash
# View model registry information
python src/deploy_model.py --stage info
```

### Rollback Production Model
```bash
# Rollback to previous production version
python src/deploy_model.py --stage rollback
```

---

## 🔮 3. Single Inference

### Single File Inference
```bash
# Run inference on a single file
python src/predict.py --input data/inference_input/titanic_inference_batch_01_20251119_104516.csv

# Run inference on another file
python src/predict.py --input data/inference_input/titanic_inference_batch_02_20251119_104516.csv
```

### Single Inference with Custom Stage
```bash
# Use Staging model
python src/predict.py --input data/inference_input/titanic_inference_batch_01_20251119_104516.csv --stage Staging

# Use Production model (default)
python src/predict.py --input data/inference_input/titanic_inference_batch_01_20251119_104516.csv --stage GNU_Production
```

### Single Inference with Output File
```bash
# Save predictions to file
python src/predict.py --input data/inference_input/titanic_inference_batch_01_20251119_104516.csv --output predictions_single.csv
```

### Expected Output
- Predictions for each record
- Prediction probabilities (if available)
- Results saved to CSV file

---

## 📦 4. Batch Inference

### Batch Inference on Directory
```bash
# Process all files in inference_input directory
python src/batch_inference.py --input data/inference_input/
```

### Batch Inference on Specific File
```bash
# Process a specific file
python src/batch_inference.py --input data/inference_input/titanic_inference_batch_01_20251119_104516.csv
```

### Batch Inference with Custom Output
```bash
# Specify custom output directory
python src/batch_inference.py --input data/inference_input/ --output data/custom_batch_output/
```

### Batch Inference with Custom Config
```bash
# Use different config file
python src/batch_inference.py --input data/inference_input/ --config config.local.yaml
```

### Expected Output
- Processed all files in directory
- Predictions saved to `data/batch_output/`
- Input files archived to `data/batch_archive/`
- Summary with total rows processed

---

## 📅 5. Daily Scheduled Inference

### Manual Daily Inference (Simulates 1 PM PST Run)
```bash
# Run daily batch inference manually
python src/batch_inference.py --input data/inference_input/
```

### Setup Cron Job for Daily Inference
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 1 PM PST (13:00)
0 13 * * * cd /Users/narsimhabetini/gnu-mlops-repo && /path/to/venv/bin/python src/batch_inference.py --input data/inference_input/ >> logs/daily_inference.log 2>&1
```

### Test Cron Job
```bash
# Test the cron job command manually
cd /Users/narsimhabetini/gnu-mlops-repo
source venv/bin/activate
python src/batch_inference.py --input data/inference_input/
```

---

## 🔄 6. Retraining

### Check if Retraining is Needed
```bash
# Check retraining status (checks if 30 days have passed)
python src/retrain_model.py
```

### Force Retraining (Ignore 30-Day Check)
```bash
# Force immediate retraining
python src/retrain_model.py --force
```

### Retraining with Custom Config
```bash
# Use different config file
python src/retrain_model.py --force --config config.local.yaml
```

### Setup Cron Job for Automatic Retraining
```bash
# Edit crontab
crontab -e

# Add this line to check retraining daily at 1 PM PST
0 13 * * * cd /Users/narsimhabetini/gnu-mlops-repo && /path/to/venv/bin/python src/retrain_model.py >> logs/retraining.log 2>&1
```

### Expected Output
- Checks last training date
- Trains new model if needed
- Compares with production model
- Auto-deploys if new model is better
- Summary with improvement metrics

---

## 📊 7. Model Management

### View Model Registry Info
```bash
# Get model information
python src/deploy_model.py --stage info
```

### Check Production Model
```bash
# Get production model details
python src/deploy_model.py --stage info
```

### List All Model Versions
```bash
# View all versions in MLflow UI
mlflow ui
# Then open http://localhost:5000
```

---

## 🎬 8. Complete End-to-End Demo

### Full Pipeline Demo (Step by Step)

```bash
# Step 1: Preprocess Titanic Data (if not done)
python scripts/preprocess_titanic_data.py

# Step 2: Train Model
python src/train_model.py

# Step 3: Deploy to Staging
python src/deploy_model.py --stage staging

# Step 4: Deploy to Production
python src/deploy_model.py --stage production

# Step 5: Single Inference
python src/predict.py --input data/inference_input/titanic_inference_batch_01_20251119_104516.csv

# Step 6: Batch Inference
python src/batch_inference.py --input data/inference_input/

# Step 7: Retraining (Force)
python src/retrain_model.py --force

# Step 8: View Results
mlflow ui
```

---

## 📁 9. Data Files for Demo

### Training Data
- **Location:** `data/training/titanic_training_data.csv`
- **Source:** `data/titanic/train.csv` (preprocessed)
- **Records:** ~712 rows (80% of Titanic training data)

### Test Data
- **Location:** `data/testing/titanic_test_data.csv`
- **Source:** `data/titanic/train.csv` (preprocessed)
- **Records:** ~178 rows (20% of Titanic training data)

### Inference Data Files (5 files, 10 records each)
- `data/inference_input/titanic_inference_batch_01_20251119_104516.csv`
- `data/inference_input/titanic_inference_batch_02_20251119_104516.csv`
- `data/inference_input/titanic_inference_batch_03_20251119_104516.csv`
- `data/inference_input/titanic_inference_batch_04_20251119_104516.csv`
- `data/inference_input/titanic_inference_batch_05_20251119_104516.csv`

### Generate More Inference Files
```bash
# Generate additional inference files
python scripts/generate_titanic_inference_data.py
```

---

## 🎯 10. Quick Demo Scenarios

### Scenario 1: First-Time Setup Demo
```bash
# 1. Preprocess data
python scripts/preprocess_titanic_data.py

# 2. Train model
python src/train_model.py

# 3. Deploy to production
python src/deploy_model.py --stage production

# 4. Run inference
python src/predict.py --input data/inference_input/titanic_inference_batch_01_20251119_104516.csv
```

### Scenario 2: Batch Processing Demo
```bash
# 1. Process all inference files
python src/batch_inference.py --input data/inference_input/

# 2. Check results
ls -lh data/batch_output/
cat data/batch_output/*.csv | head -20
```

### Scenario 3: Retraining Demo
```bash
# 1. Force retraining
python src/retrain_model.py --force

# 2. Check if new model is better
python src/deploy_model.py --stage info
```

### Scenario 4: Model Lifecycle Demo
```bash
# 1. Train
python src/train_model.py

# 2. Deploy to Staging
python src/deploy_model.py --stage staging

# 3. Deploy to Production
python src/deploy_model.py --stage production

# 4. Run inference
python src/predict.py --input data/inference_input/titanic_inference_batch_01_20251119_104516.csv

# 5. Retrain
python src/retrain_model.py --force

# 6. Deploy new model if better
python src/deploy_model.py --stage production
```

---

## 🔍 11. Monitoring and Logs

### View Training Logs
```bash
# Check latest training log
ls -lt logs/ | head -5
tail -50 logs/training_*.log
```

### View Batch Inference Logs
```bash
# Check batch inference logs
tail -50 logs/batch_inference_*.log
```

### View Retraining Logs
```bash
# Check retraining logs
tail -50 logs/retraining_*.log
```

### MLflow UI

#### Option 1: Use Databricks UI (Default)
```bash
# Launch MLflow UI with Databricks backend (default)
mlflow ui
# or
python scripts/launch_mlflow_ui.py --backend databricks

# Access at: http://localhost:5000
```

#### Option 2: Use Local SQLite UI
```bash
# Launch MLflow UI with SQLite backend (local)
python scripts/launch_mlflow_ui.py --backend sqlite

# Or using shell script
./scripts/launch_mlflow_ui.sh sqlite

# Or manually
mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns

# Access at: http://localhost:5000
```

#### Option 3: Custom Port
```bash
# Launch on different port
python scripts/launch_mlflow_ui.py --backend sqlite --port 5001
# Access at: http://localhost:5001
```

---

## 📝 12. Troubleshooting Commands

### Check Data Files
```bash
# Verify training data exists
ls -lh data/training/titanic_training_data.csv

# Check inference files
ls -lh data/inference_input/titanic_inference_batch_*.csv

# Count records
wc -l data/training/titanic_training_data.csv
wc -l data/inference_input/titanic_inference_batch_*.csv
```

### Verify Model Exists
```bash
# Check if model is registered
python src/deploy_model.py --stage info
```

### Test Data Loading
```bash
# Quick test of data loading
python -c "
import pandas as pd
df = pd.read_csv('data/training/titanic_training_data.csv')
print(f'Rows: {len(df)}')
print(f'Columns: {list(df.columns)}')
print(df.head())
"
```

---

## 🎪 13. Presentation Demo Flow

### Recommended Demo Order:

1. **Setup & Training** (2 min)
   ```bash
   python scripts/preprocess_titanic_data.py
   python src/train_model.py
   ```

2. **Deployment** (1 min)
   ```bash
   python src/deploy_model.py --stage staging
   python src/deploy_model.py --stage production
   ```

3. **Single Inference** (1 min)
   ```bash
   python src/predict.py --input data/inference_input/titanic_inference_batch_01_20251119_104516.csv
   ```

4. **Batch Inference** (1 min)
   ```bash
   python src/batch_inference.py --input data/inference_input/
   ```

5. **Retraining** (1 min)
   ```bash
   python src/retrain_model.py --force
   ```

6. **MLflow UI** (1 min)
   ```bash
   mlflow ui
   # Show experiments, models, metrics
   ```

**Total Demo Time: ~7 minutes**

---

## 📚 14. Additional Resources

### Configuration Files
- `config.yaml` - Main configuration
- `config.local.yaml` - Local testing configuration

### Scripts
- `scripts/preprocess_titanic_data.py` - Data preprocessing
- `scripts/generate_titanic_inference_data.py` - Generate inference files
- `scripts/schedule_retraining.sh` - Setup retraining cron job
- `scripts/schedule_batch_inference.sh` - Setup batch inference cron job

### Documentation
- `docs/README.md` - Project overview
- `docs/DEPLOYMENT_GUIDE.md` - Deployment instructions
- `docs/INFERENCE_COMMANDS.md` - Inference guide

---

## ✅ Quick Reference Card

```bash
# Training
python src/train_model.py

# Deployment
python src/deploy_model.py --stage staging
python src/deploy_model.py --stage production

# Single Inference
python src/predict.py --input data/inference_input/titanic_inference_batch_01_20251119_104516.csv

# Batch Inference
python src/batch_inference.py --input data/inference_input/

# Retraining
python src/retrain_model.py --force

# Model Info
python src/deploy_model.py --stage info

# MLflow UI
mlflow ui
```

---

**Last Updated:** November 19, 2025  
**Author:** Narsimha Betini

