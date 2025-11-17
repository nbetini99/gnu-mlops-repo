# Complete Deployment Guide - GNU MLOps Pipeline

## 📋 Overview

This guide provides comprehensive step-by-step instructions for deploying and running the GNU MLOps pipeline in three different environments:

1. **Local Machine** - Run everything on your local computer
2. **Databricks** - Run on Databricks cloud platform
3. **GitHub Actions** - Automated CI/CD pipeline

---

## 🖥️ Part 1: Local Deployment

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (venv)
- Access to the repository

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/nbetini99/gnu-mlops-repo.git
cd gnu-mlops-repo
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 4: Configure Local Environment

```bash
# Create .env file for local credentials (optional for Databricks)
cat > .env << EOF
DATABRICKS_HOST=https://dbc-5e289a33-a706.cloud.databricks.com
DATABRICKS_TOKEN=dapicb7282387c50cc9aa3e8e3d18378b5fd
DATABRICKS_WORKSPACE_PATH=/Users/nbatink@gmail.com/gnu-mlops/liveprod
DATABRICKS_EXPERIMENT_PATH=/Users/nbatink@gmail.com/gnu-mlops/experiments
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
EOF

# Source the environment variables (optional, for Databricks mode)
source .env
```

**Note:** For local-only deployment (without Databricks), you don't need the .env file. The system will automatically use SQLite for MLflow tracking.

### Step 5: Run Training Pipeline

```bash
# Train the model locally
python src/train_model.py

# Expected output:
# - Model training starts
# - MLflow tracking initialized (SQLite)
# - Model saved to MLflow
# - Training metrics logged
```

### Step 6: Deploy Model to Staging

```bash
# Deploy model to staging
python src/deploy_model.py --stage staging

# Expected output:
# - Model version found
# - Performance validation
# - Model transitioned to staging
```

### Step 7: Deploy Model to Production (GNU_Production)

```bash
# Deploy model to production
python src/deploy_model.py --stage GNU_Production

# Expected output:
# - Model version found
# - Performance validation (higher threshold)
# - Model transitioned to GNU_Production
```

### Step 8: Make Predictions

```bash
# Create sample input file
echo "feature1,feature2,feature3
0.5,0.3,0.2
0.7,0.4,0.1" > input.csv

# Run predictions
python src/predict.py --input input.csv --output predictions.csv --stage GNU_Production

# Expected output:
# - Model loaded
# - Predictions generated
# - Results saved to predictions.csv
```

### Step 9: View MLflow UI (Local)

```bash
# Start MLflow UI
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Open browser to:
# http://localhost:5000
```

### Step 10: Schedule Automatic Retraining (Optional)

```bash
# Set up cron job for retraining every 30 days
# Edit crontab
crontab -e

# Add this line:
# 0 0 1 * * /Users/narsimhabetini/gnu-mlops-repo/scripts/schedule_retraining.sh
```

### Step 11: Schedule Batch Inference (Optional)

```bash
# Set up cron job for daily batch inference at 1 PM PST
# Edit crontab
crontab -e

# Add this line:
# 0 13 * * * /Users/narsimhabetini/gnu-mlops-repo/scripts/schedule_batch_inference.sh
```

### Local Deployment Checklist

- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Training completed successfully
- [ ] Model deployed to staging
- [ ] Model deployed to production
- [ ] Predictions working
- [ ] MLflow UI accessible

---

## ☁️ Part 2: Databricks Deployment

### Prerequisites

- Databricks account
- Databricks workspace URL
- Databricks access token
- Databricks CLI (optional)

### Step 1: Get Databricks Credentials

1. **Get Workspace URL:**
   - Your workspace URL: `https://dbc-5e289a33-a706.cloud.databricks.com`

2. **Create Access Token:**
   - Go to: Databricks → User Settings → Access Tokens
   - Click "Generate New Token"
   - Copy the token: `dapicb7282387c50cc9aa3e8e3d18378b5fd`

3. **Set Workspace Paths:**
   - Workspace Path: `/Users/nbatink@gmail.com/gnu-mlops/liveprod`
   - Experiment Path: `/Users/nbatink@gmail.com/gnu-mlops/experiments`

### Step 2: Configure Environment Variables

```bash
# Set Databricks environment variables
export DATABRICKS_HOST=https://dbc-5e289a33-a706.cloud.databricks.com
export DATABRICKS_TOKEN=dapicb7282387c50cc9aa3e8e3d18378b5fd
export DATABRICKS_WORKSPACE_PATH=/Users/nbatink@gmail.com/gnu-mlops/liveprod
export DATABRICKS_EXPERIMENT_PATH=/Users/nbatink@gmail.com/gnu-mlops/experiments
export MLFLOW_TRACKING_URI=databricks

# Or create .env file
cat > .env << EOF
DATABRICKS_HOST=https://dbc-5e289a33-a706.cloud.databricks.com
DATABRICKS_TOKEN=dapicb7282387c50cc9aa3e8e3d18378b5fd
DATABRICKS_WORKSPACE_PATH=/Users/nbatink@gmail.com/gnu-mlops/liveprod
DATABRICKS_EXPERIMENT_PATH=/Users/nbatink@gmail.com/gnu-mlops/experiments
MLFLOW_TRACKING_URI=databricks
EOF

source .env
```

### Step 3: Verify Databricks Connection

```bash
# Test connection
python -c "
import mlflow
mlflow.set_tracking_uri('databricks')
experiments = mlflow.search_experiments(max_results=1)
print('✓ Databricks connection successful')
print(f'Found {len(experiments)} experiment(s)')
"
```

### Step 4: Train Model on Databricks

```bash
# Run training with Databricks tracking
python src/train_model.py

# Expected output:
# - Connected to Databricks
# - Experiment created/accessed
# - Model trained
# - Metrics logged to Databricks MLflow
# - Model registered in Databricks
```

### Step 5: Deploy Model to Staging (Databricks)

```bash
# Deploy to staging
python src/deploy_model.py --stage staging

# Expected output:
# - Model found in Databricks MLflow
# - Performance validated
# - Model transitioned to staging in Databricks
```

### Step 6: Deploy Model to Production (Databricks)

```bash
# Deploy to production
python src/deploy_model.py --stage GNU_Production

# Expected output:
# - Model found in Databricks MLflow
# - Performance validated (80% threshold)
# - Model transitioned to GNU_Production in Databricks
```

### Step 7: Make Predictions (Databricks)

```bash
# Create input file
echo "feature1,feature2,feature3
0.5,0.3,0.2
0.7,0.4,0.1" > input.csv

# Run predictions using Databricks model
python src/predict.py --input input.csv --output predictions.csv --stage GNU_Production

# Expected output:
# - Model loaded from Databricks MLflow
# - Predictions generated
# - Results saved
```

### Step 8: View MLflow UI (Databricks)

1. **Access Databricks MLflow:**
   - Go to your Databricks workspace
   - Click "MLflow" in the left sidebar
   - View experiments, models, and runs

2. **Or use MLflow UI locally:**
   ```bash
   mlflow ui --backend-store-uri databricks
   ```

### Step 9: Deploy Using Databricks Script

```bash
# Use the provided deployment script
chmod +x deploy_databricks.sh
./deploy_databricks.sh

# This script will:
# - Verify Databricks connection
# - Train the model
# - Deploy to staging
# - Deploy to production (if staging successful)
```

### Databricks Deployment Checklist

- [ ] Databricks credentials configured
- [ ] Environment variables set
- [ ] Connection to Databricks verified
- [ ] Training completed on Databricks
- [ ] Model deployed to staging in Databricks
- [ ] Model deployed to production in Databricks
- [ ] Predictions working with Databricks model
- [ ] MLflow UI accessible in Databricks

---

## 🔄 Part 3: GitHub Actions Deployment

### Prerequisites

- GitHub account
- Repository access
- GitHub Secrets configured (already done)

### Step 1: Verify GitHub Secrets

1. **Check Secrets Page:**
   - Go to: https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
   - Verify these secrets exist:
     - `DATABRICKS_HOST`
     - `DATABRICKS_TOKEN`
     - `DATABRICKS_WORKSPACE_PATH` (optional)
     - `DATABRICKS_EXPERIMENT_PATH` (optional)

2. **Verify Secrets Are Set:**
   - All secrets should be listed
   - You cannot view values (for security)

### Step 2: Understanding GitHub Actions Workflow

The workflow is defined in: `.github/workflows/train-and-deploy.yml`

**Workflow Structure:**
1. **Training Job:**
   - Checks out code
   - Sets up Python
   - Installs dependencies
   - Loads Databricks secrets (if available)
   - Runs training
   - Registers model in MLflow

2. **Deployment Job:**
   - Waits for training to complete
   - Loads Databricks secrets
   - Deploys model to staging
   - Deploys model to production (if staging successful)

### Step 3: Trigger GitHub Actions Workflow

#### Option A: Automatic Trigger (Push to Main)

```bash
# Make any change and push
echo "# Test commit" >> README.md
git add README.md
git commit -m "Test: Trigger GitHub Actions"
git push origin main

# Workflow will automatically start
```

#### Option B: Manual Trigger

1. Go to: https://github.com/nbetini99/gnu-mlops-repo/actions
2. Click on "Train and Deploy" workflow
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"

### Step 4: Monitor Workflow Execution

1. **Go to Actions Tab:**
   - Link: https://github.com/nbetini99/gnu-mlops-repo/actions

2. **Click on Running Workflow:**
   - See real-time logs
   - Monitor each step
   - Check for errors

3. **Expected Workflow Steps:**
   - ✅ Checkout code
   - ✅ Set up Python
   - ✅ Install dependencies
   - ✅ Load Databricks secrets
   - ✅ Train model
   - ✅ Deploy to staging
   - ✅ Deploy to production

### Step 5: View Workflow Logs

**Look for these success messages:**
```
✓ Databricks credentials found in GitHub Secrets
✓ Environment configured for Databricks
✓ Databricks credentials loaded from GitHub Secrets
✓ Model training completed
✓ Model deployed to staging
✓ Model deployed to GNU_Production
```

**If secrets are not available, you'll see:**
```
⚠ Databricks credentials not found, using local mode
✓ Environment configured for local SQLite
```

### Step 6: Verify Deployment

1. **Check MLflow:**
   - Go to Databricks MLflow UI (if Databricks mode)
   - Or check local MLflow (if local mode)
   - Verify model is registered

2. **Check Model Registry:**
   - Verify model in staging
   - Verify model in GNU_Production (if applicable)

### Step 7: Workflow Status

**Successful Workflow:**
- ✅ Green checkmark on workflow
- ✅ All steps completed
- ✅ Model deployed

**Failed Workflow:**
- ❌ Red X on workflow
- ❌ Check logs for errors
- ❌ Fix issues and re-run

### GitHub Actions Deployment Checklist

- [ ] GitHub Secrets configured
- [ ] Workflow file exists (.github/workflows/train-and-deploy.yml)
- [ ] Workflow triggered (manual or automatic)
- [ ] Training job completed successfully
- [ ] Deployment job completed successfully
- [ ] Model deployed to staging
- [ ] Model deployed to production (if applicable)
- [ ] Workflow logs show success messages

---

## 🔄 Comparison: Local vs Databricks vs GitHub Actions

### Local Deployment

**Pros:**
- ✅ Full control over environment
- ✅ Fast iteration and debugging
- ✅ No cloud costs
- ✅ Works offline (for local mode)

**Cons:**
- ❌ Limited computing resources
- ❌ No automatic scheduling (requires manual setup)
- ❌ Single machine dependency

**Best For:**
- Development and testing
- Learning and experimentation
- Small datasets

### Databricks Deployment

**Pros:**
- ✅ Scalable compute resources
- ✅ Managed MLflow tracking
- ✅ Collaboration features
- ✅ Enterprise-grade security
- ✅ Easy model registry

**Cons:**
- ❌ Requires cloud access
- ❌ Costs money (depending on usage)
- ❌ Requires Databricks account

**Best For:**
- Production workloads
- Large datasets
- Team collaboration
- Enterprise deployments

### GitHub Actions Deployment

**Pros:**
- ✅ Fully automated CI/CD
- ✅ Version-controlled deployments
- ✅ Automatic on code changes
- ✅ Integration with GitHub
- ✅ Free for public repos (limited for private)

**Cons:**
- ❌ Limited execution time
- ❌ Requires GitHub Secrets setup
- ❌ Less control over environment

**Best For:**
- Automated deployments
- CI/CD pipelines
- Continuous integration
- Production automation

---

## 📋 Quick Reference Commands

### Local Deployment

```bash
# Setup
cd gnu-mlops-repo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Training
python src/train_model.py

# Deployment
python src/deploy_model.py --stage staging
python src/deploy_model.py --stage GNU_Production

# Predictions
python src/predict.py --input input.csv --output predictions.csv --stage GNU_Production

# MLflow UI
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

### Databricks Deployment

```bash
# Setup credentials
export DATABRICKS_HOST=https://dbc-5e289a33-a706.cloud.databricks.com
export DATABRICKS_TOKEN=your_token_here
export MLFLOW_TRACKING_URI=databricks

# Training
python src/train_model.py

# Deployment
python src/deploy_model.py --stage staging
python src/deploy_model.py --stage GNU_Production

# Deploy script
./deploy_databricks.sh
```

### GitHub Actions Deployment

```bash
# Trigger workflow
git add .
git commit -m "Trigger training"
git push origin main

# Or manually trigger via GitHub UI
# Go to: Actions → Train and Deploy → Run workflow
```

---

## 🔍 Troubleshooting

### Local Deployment Issues

**Issue: Module not found**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue: MLflow connection failed**
```bash
# Solution: Use local SQLite
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db
```

### Databricks Deployment Issues

**Issue: Authentication failed**
```bash
# Solution: Verify credentials
echo $DATABRICKS_HOST
echo $DATABRICKS_TOKEN
```

**Issue: Connection timeout**
```bash
# Solution: Check network connectivity
ping dbc-5e289a33-a706.cloud.databricks.com
```

### GitHub Actions Issues

**Issue: Secrets not found**
```bash
# Solution: Verify secrets are set
# Go to: Repository Settings → Secrets → Actions
```

**Issue: Workflow failed**
```bash
# Solution: Check workflow logs
# Go to: Actions → Failed workflow → View logs
```

---

## 📚 Additional Resources

### Documentation
- **Local Run Guide:** `LOCAL_RUN_GUIDE.md`
- **GitHub Secrets Setup:** `GITHUB_SECRETS_SETUP_GUIDE.md`
- **Quick Start:** `QUICK_START_GUIDE.md`

### Links
- **Repository:** https://github.com/nbetini99/gnu-mlops-repo
- **GitHub Actions:** https://github.com/nbetini99/gnu-mlops-repo/actions
- **Secrets Page:** https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
- **Databricks Workspace:** https://dbc-5e289a33-a706.cloud.databricks.com

---

## ✅ Summary

### Deployment Methods:

1. **Local:** Best for development and testing
   - Commands: `python src/train_model.py`, `python src/deploy_model.py`
   - MLflow: `sqlite:///mlflow.db`

2. **Databricks:** Best for production and collaboration
   - Commands: Same as local, with Databricks credentials
   - MLflow: `databricks://`

3. **GitHub Actions:** Best for automation and CI/CD
   - Trigger: Push to main or manual trigger
   - Automation: Fully automated workflow

**All three methods use the same codebase and configuration files!**

---

**Last Updated:** November 2025  
**Repository:** https://github.com/nbetini99/gnu-mlops-repo

