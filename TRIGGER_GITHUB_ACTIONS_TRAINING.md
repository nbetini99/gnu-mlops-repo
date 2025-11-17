# How to Trigger Training from GitHub Actions

## 🚀 Quick Methods

### Method 1: Automatic Trigger (Push to Main) ⭐ Easiest

**Simply push any commit to the `main` branch:**

```bash
cd /Users/narsimhabetini/gnu-mlops-repo

# Make any change (or empty commit)
git commit --allow-empty -m "Trigger training"
git push origin main
```

**What happens:**
- ✅ GitHub Actions automatically detects the push
- ✅ Workflow "MLOps Training and Deployment Pipeline" starts
- ✅ Training runs automatically
- ✅ Model deploys to staging and production

---

### Method 2: Manual Trigger via GitHub UI ⭐ Recommended

**Step-by-step:**

1. **Go to Actions Tab:**
   ```
   https://github.com/nbetini99/gnu-mlops-repo/actions
   ```

2. **Click on Workflow:**
   - Look for **"MLOps Training and Deployment Pipeline"** in the left sidebar
   - If you don't see it, use the direct link:
   ```
   https://github.com/nbetini99/gnu-mlops-repo/actions/workflows/train-and-deploy.yml
   ```

3. **Click "Run workflow":**
   - Click the **"Run workflow"** dropdown button (top right)
   - Select branch: **main**
   - (Optional) Check "Deploy to production" if you want to deploy
   - Click **"Run workflow"** button

4. **Monitor Progress:**
   - Workflow will start immediately
   - Click on the running workflow to see logs
   - Watch real-time progress

**Visual Guide:**
```
GitHub Repository 
  → Actions Tab 
    → MLOps Training and Deployment Pipeline 
      → Run workflow (button) 
        → Select branch: main 
          → Run workflow
```

---

### Method 3: Using GitHub CLI (if installed)

```bash
# Install GitHub CLI (if not installed)
brew install gh

# Authenticate
gh auth login

# Trigger workflow
gh workflow run train-and-deploy.yml

# Or trigger with specific branch
gh workflow run train-and-deploy.yml --ref main
```

---

## 📋 Prerequisites Checklist

Before triggering, ensure:

- [ ] **GitHub Secrets are configured:**
  - Go to: https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
  - Verify these secrets exist:
    - ✅ `DATABRICKS_HOST`
    - ✅ `DATABRICKS_TOKEN`
    - ✅ `DATABRICKS_WORKSPACE_PATH` (optional)
    - ✅ `DATABRICKS_EXPERIMENT_PATH` (optional)

- [ ] **Workflow file exists:**
  - `.github/workflows/train-and-deploy.yml` is in the repository

- [ ] **Code is pushed:**
  - Latest code is committed and pushed to GitHub

---

## 🔍 How to Find the Workflow

### If Workflow Not Visible:

**Option A: Direct Link**
```
https://github.com/nbetini99/gnu-mlops-repo/actions/workflows/train-and-deploy.yml
```

**Option B: Trigger It First**
Workflows only appear after they've run at least once. Trigger it automatically:
```bash
git commit --allow-empty -m "Trigger workflow"
git push origin main
```

Then go to Actions tab - workflow will appear.

---

## 📊 What Happens During Training

### Workflow Steps:

1. **Checkout code** - Downloads repository
2. **Set up Python** - Configures Python 3.9 environment
3. **Install dependencies** - Installs packages from requirements.txt
4. **Check Databricks credentials** - Verifies secrets exist
5. **Set up environment** - Configures environment variables
6. **Run tests** - Runs pytest (6 tests)
7. **Train model** - Executes `python src/train_model.py`
8. **Deploy to staging** - Deploys model to staging environment
9. **Deploy to production** - Deploys model to GNU_Production

### Expected Duration:
- **Total time:** ~15 minutes
- **Tests:** ~1 minute
- **Training:** ~5-10 minutes
- **Deployment:** ~2-5 minutes

---

## 📈 Monitor Training Progress

### View Workflow Runs:

**Link:**
```
https://github.com/nbetini99/gnu-mlops-repo/actions
```

### Check Status:

- 🟡 **Yellow circle** = Running/In progress
- ✅ **Green checkmark** = Success
- ❌ **Red X** = Failed
- ⚪ **Gray circle** = Queued

### View Detailed Logs:

1. Click on the workflow run
2. Click on the job (e.g., **"train"**)
3. Click on individual steps to see logs
4. Expand steps to view detailed output

### Key Logs to Watch:

**Training Step:**
```
✓ Databricks credentials found in GitHub Secrets
✓ Environment configured for Databricks
✓ Training model...
  - Run ID: abc123def456
  - Accuracy: 0.43
  - F1 Score: 0.4286
✓ Model registered: gnu-mlops-model (Version 1)
```

**Deployment Step:**
```
✓ Model version 1 deployed to Staging
✓ Model version 1 deployed to GNU_Production
```

---

## ✅ Verify Training Success

### Success Indicators:

1. **Workflow Status:** ✅ Green checkmark
2. **All Steps:** ✅ All steps show checkmarks
3. **Training Logs:** Show "Training Completed Successfully!"
4. **Deployment Logs:** Show "Model deployed to GNU_Production"

### Check Model in MLflow:

**If using Databricks:**
- Go to: https://dbc-5e289a33-a706.cloud.databricks.com
- Navigate to MLflow → Models
- Verify model is registered

**If using local SQLite (fallback):**
- Model is stored in MLflow database
- Can be viewed with MLflow UI locally

---

## 🔧 Troubleshooting

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

4. **Use direct link:**
   ```
   https://github.com/nbetini99/gnu-mlops-repo/actions/workflows/train-and-deploy.yml
   ```

### Issue 2: Training Fails

**Check logs for:**
- Missing dependencies (add to requirements.txt)
- Databricks credentials not found (set GitHub Secrets)
- Model validation failed (check accuracy thresholds)

### Issue 3: Timeout Errors

**If you see timeout errors:**
- The code now has automatic fallback to SQLite
- Training will continue with local tracking
- Check logs for "Falling back to local SQLite"

---

## 🎯 Quick Reference Commands

### Trigger Training:

```bash
# Method 1: Push to main (automatic)
git commit --allow-empty -m "Trigger training"
git push origin main

# Method 2: Manual trigger via GitHub UI
# Go to: Actions → Train and Deploy → Run workflow
```

### Check Workflow Status:

```bash
# View workflow runs
# Go to: https://github.com/nbetini99/gnu-mlops-repo/actions

# Or use GitHub CLI
gh run list --workflow=train-and-deploy.yml
```

### View Workflow Logs:

```bash
# Via GitHub UI
# Go to: Actions → Click on workflow run → View logs

# Or use GitHub CLI
gh run view [run-id] --log
```

---

## 📝 Workflow Configuration

### Triggers:

The workflow triggers on:
- ✅ Push to `main` branch (automatic)
- ✅ Push to `develop` branch (automatic)
- ✅ Pull requests to `main` (automatic)
- ✅ Manual trigger via UI (workflow_dispatch)

### Environment Variables:

Set automatically from GitHub Secrets:
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `DATABRICKS_WORKSPACE_PATH`
- `DATABRICKS_EXPERIMENT_PATH`
- `MLFLOW_TRACKING_URI`

---

## 🔗 Useful Links

### GitHub Actions:

- **Workflow Runs:** https://github.com/nbetini99/gnu-mlops-repo/actions
- **Direct Workflow:** https://github.com/nbetini99/gnu-mlops-repo/actions/workflows/train-and-deploy.yml
- **Secrets:** https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
- **Repository:** https://github.com/nbetini99/gnu-mlops-repo

### Databricks:

- **Workspace:** https://dbc-5e289a33-a706.cloud.databricks.com
- **MLflow:** Access via Databricks workspace

---

## ✅ Summary

**Easiest Way to Trigger:**
```bash
git commit --allow-empty -m "Trigger training"
git push origin main
```

**Or use GitHub UI:**
1. Go to: https://github.com/nbetini99/gnu-mlops-repo/actions
2. Click "Run workflow"
3. Select "main" branch
4. Click "Run workflow"

**Monitor:**
- Go to: https://github.com/nbetini99/gnu-mlops-repo/actions
- Click on running workflow
- View real-time logs

---

**Last Updated:** November 2025  
**Repository:** https://github.com/nbetini99/gnu-mlops-repo

