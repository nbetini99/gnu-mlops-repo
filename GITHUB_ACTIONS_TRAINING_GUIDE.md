# GitHub Actions Training Guide - Step-by-Step Process

## 📋 Overview

This guide provides a complete step-by-step process for running model training on GitHub Actions. The workflow automatically trains your model, validates it, and deploys it to staging and production.

---

## 🚀 Quick Start

### Prerequisites Checklist

Before running training on GitHub Actions, ensure:

- [ ] GitHub repository is set up: `https://github.com/nbetini99/gnu-mlops-repo`
- [ ] GitHub Secrets are configured (see below)
- [ ] Workflow file exists: `.github/workflows/train-and-deploy.yml`
- [ ] Code is pushed to the repository

---

## 📝 Step 1: Set Up GitHub Secrets

### 1.1 Navigate to Secrets Page

**Direct Link:**
https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions

**Or navigate manually:**
1. Go to: https://github.com/nbetini99/gnu-mlops-repo
2. Click: **Settings** (top menu bar)
3. Click: **Secrets and variables** → **Actions** (left sidebar)

### 1.2 Add Required Secrets

Click **"New repository secret"** for each:

#### Secret 1: DATABRICKS_HOST
- **Name:** `DATABRICKS_HOST`
- **Value:** `https://dbc-5e289a33-a706.cloud.databricks.com`
- **Required:** Yes

#### Secret 2: DATABRICKS_TOKEN
- **Name:** `DATABRICKS_TOKEN`
- **Value:** `dapicb7282387c50cc9aa3e8e3d18378b5fd`
- **Required:** Yes

#### Secret 3: DATABRICKS_WORKSPACE_PATH (Optional)
- **Name:** `DATABRICKS_WORKSPACE_PATH`
- **Value:** `/Users/nbatink@gmail.com/gnu-mlops/liveprod`
- **Required:** No (but recommended)

#### Secret 4: DATABRICKS_EXPERIMENT_PATH (Optional)
- **Name:** `DATABRICKS_EXPERIMENT_PATH`
- **Value:** `/Users/nbatink@gmail.com/gnu-mlops/experiments`
- **Required:** No (but recommended)

### 1.3 Verify Secrets

After adding secrets, verify they're listed:
- ✅ DATABRICKS_HOST
- ✅ DATABRICKS_TOKEN
- ✅ DATABRICKS_WORKSPACE_PATH (optional)
- ✅ DATABRICKS_EXPERIMENT_PATH (optional)

**Note:** You cannot view secret values after adding them (for security).

---

## 🔄 Step 2: Trigger GitHub Actions Workflow

### Method 1: Automatic Trigger (Push to Main Branch)

**When it triggers:**
- Automatically runs when you push code to the `main` branch
- Runs on every commit to `main`

**Commands:**

```bash
# 1. Make sure you're in the repository directory
cd /Users/narsimhabetini/gnu-mlops-repo

# 2. Make any change (or create a commit)
echo "# Training trigger" >> README.md
git add README.md
git commit -m "Trigger GitHub Actions training"

# 3. Push to main branch
git push origin main

# 4. Workflow will automatically start
```

**What happens:**
1. GitHub detects the push to `main`
2. Automatically triggers the workflow
3. Training job starts
4. Deployment job runs after training completes

### Method 2: Manual Trigger (Recommended for Testing)

**Steps:**

1. **Navigate to Actions Tab:**
   - Go to: https://github.com/nbetini99/gnu-mlops-repo/actions

2. **Select Workflow:**
   - Click on **"Train and Deploy"** workflow (left sidebar)

3. **Click "Run workflow":**
   - Click the **"Run workflow"** dropdown button (top right)
   - Select branch: **main**
   - Click **"Run workflow"** button

4. **Workflow starts:**
   - You'll see a new workflow run appear
   - Status will show "Queued" then "In progress"

**Visual Guide:**
```
GitHub Repository → Actions Tab → Train and Deploy → Run workflow → main → Run workflow
```

### Method 3: Using GitHub CLI (if installed)

```bash
# Install GitHub CLI (if not installed)
# brew install gh

# Authenticate
gh auth login

# Trigger workflow manually
gh workflow run train-and-deploy.yml

# Or trigger with specific branch
gh workflow run train-and-deploy.yml --ref main
```

---

## 📊 Step 3: Monitor Workflow Execution

### 3.1 View Workflow Runs

**Link:**
https://github.com/nbetini99/gnu-mlops-repo/actions

**Steps:**
1. Go to **Actions** tab in your repository
2. Click on the running workflow (or latest run)
3. View real-time logs

### 3.2 Check Workflow Status

**Status Indicators:**
- 🟡 **Yellow circle** = Running/In progress
- ✅ **Green checkmark** = Success
- ❌ **Red X** = Failed
- ⚪ **Gray circle** = Queued

### 3.3 View Detailed Logs

**Steps:**
1. Click on the workflow run
2. Click on the job (e.g., **"train"** or **"deploy-production"**)
3. Click on individual steps to see logs
4. Expand steps to view detailed output

**Key Steps to Monitor:**
- ✅ **Checkout code** - Downloads repository code
- ✅ **Set up Python** - Installs Python environment
- ✅ **Install dependencies** - Installs required packages
- ✅ **Check Databricks credentials** - Verifies secrets
- ✅ **Train model** - Runs training pipeline
- ✅ **Deploy to staging** - Deploys model to staging
- ✅ **Deploy to production** - Deploys model to production

---

## 🔍 Step 4: Verify Training Success

### 4.1 Check Workflow Logs

**Look for these success messages:**

```
✓ Databricks credentials found in GitHub Secrets
✓ Environment configured for Databricks
✓ Model training completed
✓ Model registered in MLflow
✓ Model deployed to staging
✓ Model deployed to GNU_Production
```

### 4.2 Check Training Output

**In the "Train model" step logs, you should see:**

```
Training Completed Successfully!
Run ID: [some-run-id]
Accuracy: [accuracy-value]
F1 Score: [f1-score]
```

### 4.3 Verify Model Deployment

**Check deployment logs for:**

```
✓ Model version [X] deployed to Staging
✓ Model version [X] deployed to GNU_Production
```

### 4.4 View Model in MLflow

**If using Databricks:**
- Go to: https://dbc-5e289a33-a706.cloud.databricks.com
- Navigate to MLflow → Models
- Verify model is registered

**If using local SQLite (fallback):**
- Model is stored in MLflow database
- Can be viewed with MLflow UI locally

---

## 📋 Step 5: Complete Workflow Process

### Workflow Structure

The workflow consists of two jobs:

#### Job 1: Train Model

**Steps:**
1. **Checkout code** - Downloads repository
2. **Set up Python** - Configures Python environment
3. **Install dependencies** - Installs packages from requirements.txt
4. **Check Databricks credentials** - Verifies secrets exist
5. **Set up environment** - Configures environment variables
6. **Train model** - Runs `python src/train_model.py`
7. **Register model** - Model is registered in MLflow

**Expected Duration:** 5-10 minutes

#### Job 2: Deploy to Production

**Steps:**
1. **Wait for training** - Waits for training job to complete
2. **Checkout code** - Downloads repository
3. **Set up Python** - Configures Python environment
4. **Install dependencies** - Installs packages
5. **Set up environment** - Configures environment variables
6. **Deploy to staging** - Runs `python src/deploy_model.py --stage staging`
7. **Deploy to production** - Runs `python src/deploy_model.py --stage production`

**Expected Duration:** 2-5 minutes

**Total Workflow Time:** 7-15 minutes

---

## 🛠️ Step 6: Troubleshooting

### Issue 1: Workflow Not Triggering

**Symptoms:**
- No workflow runs appear
- Push to main doesn't trigger workflow

**Solutions:**

1. **Check workflow file exists:**
   ```bash
   ls -la .github/workflows/train-and-deploy.yml
   ```

2. **Verify file is committed:**
   ```bash
   git log --oneline --all -- .github/workflows/train-and-deploy.yml
   ```

3. **Check branch name:**
   - Workflow triggers on `main` branch
   - Make sure you're pushing to `main`, not `master`

4. **Verify workflow syntax:**
   - Go to Actions tab
   - Check for syntax errors in workflow file

### Issue 2: Training Fails

**Symptoms:**
- Workflow shows red X
- Training step fails

**Solutions:**

1. **Check logs:**
   - Click on failed workflow
   - Click on failed step
   - Read error messages

2. **Common errors:**

   **Error: "Module not found"**
   ```bash
   # Solution: Add missing package to requirements.txt
   echo "package-name" >> requirements.txt
   git add requirements.txt
   git commit -m "Add missing dependency"
   git push origin main
   ```

   **Error: "Databricks credentials not found"**
   - Verify secrets are set in GitHub Settings
   - Check secret names match exactly (case-sensitive)
   - Re-add secrets if needed

   **Error: "Model validation failed"**
   - Check model accuracy in logs
   - Verify thresholds are set correctly (35% staging, 40% production)
   - Model may need retraining with better data

### Issue 3: Deployment Fails

**Symptoms:**
- Training succeeds but deployment fails
- Model not deployed to production

**Solutions:**

1. **Check deployment logs:**
   - Look for specific error messages
   - Common: "Model accuracy < threshold"

2. **Verify model exists:**
   - Check training logs for model registration
   - Verify model is in MLflow

3. **Check thresholds:**
   - Staging: 35% accuracy
   - Production: 40% accuracy
   - Model must meet these thresholds

### Issue 4: Secrets Not Found

**Symptoms:**
- Error: "Databricks credentials not found"
- Workflow falls back to local mode

**Solutions:**

1. **Verify secrets are set:**
   - Go to: https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
   - Verify all required secrets are listed

2. **Check secret names:**
   - Must be exactly: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`
   - Case-sensitive

3. **Re-add secrets:**
   - Delete and re-add secrets if needed
   - Make sure values are correct

---

## 📝 Step 7: Workflow Configuration

### Workflow File Location

`.github/workflows/train-and-deploy.yml`

### Key Configuration Points

**Triggers:**
```yaml
on:
  push:
    branches: [ main ]
  workflow_dispatch:  # Allows manual trigger
```

**Environment Variables:**
- Set from GitHub Secrets
- Automatically configured in workflow

**Python Version:**
- Currently uses: `python-version: '3.9'`
- Can be changed in workflow file

**Dependencies:**
- Installed from `requirements.txt`
- Make sure all dependencies are listed

---

## 🔄 Step 8: Re-running Failed Workflows

### Method 1: Re-run from GitHub UI

1. Go to: https://github.com/nbetini99/gnu-mlops-repo/actions
2. Click on failed workflow run
3. Click **"Re-run all jobs"** or **"Re-run failed jobs"**
4. Workflow will restart

### Method 2: Push New Commit

```bash
# Make a small change
echo "# Retry" >> README.md
git add README.md
git commit -m "Retry workflow"
git push origin main
```

### Method 3: Manual Trigger

1. Go to Actions tab
2. Click "Run workflow"
3. Select branch and run

---

## 📊 Step 9: Viewing Results

### 9.1 View Workflow History

**Link:**
https://github.com/nbetini99/gnu-mlops-repo/actions

**Shows:**
- All workflow runs
- Success/failure status
- Duration
- Commit that triggered it

### 9.2 View Model Metrics

**In workflow logs:**
- Training accuracy
- F1 score
- Other metrics

**In MLflow:**
- Go to Databricks MLflow UI
- View experiment runs
- Compare model versions

### 9.3 Check Deployment Status

**In workflow logs:**
- Deployment success/failure
- Model version deployed
- Stage (Staging/Production)

**In MLflow:**
- Model registry
- Current production model
- Model versions

---

## 🎯 Step 10: Best Practices

### 10.1 Before Pushing

**Checklist:**
- [ ] Code is tested locally
- [ ] Requirements.txt is up to date
- [ ] No hardcoded credentials
- [ ] Workflow file is correct
- [ ] Secrets are configured

### 10.2 Monitoring

**Regular checks:**
- Monitor workflow runs
- Check for failures
- Review logs
- Verify deployments

### 10.3 Troubleshooting

**When workflow fails:**
1. Read error logs carefully
2. Check common issues (see Step 6)
3. Test locally if possible
4. Fix issues and re-run

### 10.4 Security

**Important:**
- Never commit secrets
- Use GitHub Secrets only
- Review workflow logs (secrets are masked)
- Rotate tokens regularly

---

## 📋 Quick Reference Commands

### Trigger Workflow

```bash
# Method 1: Push to main (automatic)
git add .
git commit -m "Trigger training"
git push origin main

# Method 2: Manual trigger via GitHub UI
# Go to: Actions → Train and Deploy → Run workflow
```

### Check Workflow Status

```bash
# View workflow runs
# Go to: https://github.com/nbetini99/gnu-mlops-repo/actions

# Or use GitHub CLI
gh run list --workflow=train-and-deploy.yml
```

### View Workflow Logs

```bash
# Via GitHub UI
# Go to: Actions → Click on workflow run → View logs

# Or use GitHub CLI
gh run view [run-id] --log
```

### Re-run Workflow

```bash
# Via GitHub UI
# Actions → Failed run → Re-run all jobs

# Or trigger new run
git commit --allow-empty -m "Retry workflow"
git push origin main
```

---

## 🔗 Useful Links

### GitHub Actions

- **Workflow Runs:** https://github.com/nbetini99/gnu-mlops-repo/actions
- **Secrets:** https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
- **Repository:** https://github.com/nbetini99/gnu-mlops-repo

### Databricks

- **Workspace:** https://dbc-5e289a33-a706.cloud.databricks.com
- **MLflow:** Access via Databricks workspace

### Documentation

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **MLflow Docs:** https://mlflow.org/docs/latest/index.html

---

## ✅ Summary Checklist

### Before Running Training:

- [ ] GitHub Secrets configured
- [ ] Workflow file exists
- [ ] Code is pushed to repository
- [ ] Requirements.txt is up to date

### During Training:

- [ ] Workflow is triggered (automatic or manual)
- [ ] Monitor workflow execution
- [ ] Check logs for errors
- [ ] Verify training completes

### After Training:

- [ ] Check training metrics
- [ ] Verify model is registered
- [ ] Check deployment status
- [ ] View model in MLflow

---

## 🎯 Expected Workflow Timeline

```
0:00 - Workflow triggered
0:01 - Checkout code
0:02 - Set up Python
0:03 - Install dependencies
0:05 - Check Databricks credentials
0:06 - Set up environment
0:07 - Train model (5-10 minutes)
0:12 - Register model in MLflow
0:13 - Deploy to staging
0:14 - Deploy to production
0:15 - Workflow complete ✅
```

**Total Time:** ~15 minutes

---

## 📝 Example Workflow Run

### Successful Run Output:

```
✓ Checkout code
✓ Set up Python 3.9
✓ Install dependencies
✓ Databricks credentials found in GitHub Secrets
✓ Environment configured for Databricks
✓ Training model...
  - Run ID: abc123def456
  - Accuracy: 0.43
  - F1 Score: 0.4286
✓ Model registered: gnu-mlops-model (Version 1)
✓ Deploying to staging...
✓ Model version 1 deployed to Staging
✓ Deploying to production...
✓ Model version 1 deployed to GNU_Production
✓ Workflow completed successfully
```

---

**Last Updated:** November 2025  
**Repository:** https://github.com/nbetini99/gnu-mlops-repo

