# Complete Solution Guide: Databricks Timeout in GitHub Actions

## 🔍 Root Cause Analysis

### Why the Timeout Happens

1. **Databricks SDK Internal Retry Logic**
   - SDK has built-in 8-minute timeout
   - Multiple retry attempts with exponential backoff
   - Each retry waits longer, accumulating to 8+ minutes total

2. **Network Connectivity from GitHub Actions**
   - GitHub Actions runners may have limited network access
   - Firewall or security policies blocking Databricks
   - Databricks workspace might be in private network
   - Network latency issues

3. **MLflow Operations Trigger SDK Calls**
   - Every MLflow operation (`set_experiment`, `start_run`, `log_metric`) calls Databricks API
   - Each call can trigger SDK retries
   - Connection test might pass, but actual operations fail

4. **The Problem Chain:**
   ```
   mlflow.set_experiment() 
     → Calls Databricks API
       → SDK retries on failure
         → Each retry waits longer
           → Total wait: 8+ minutes
             → TimeoutError
   ```

## ✅ Solution Implemented

### Strategy: Default to SQLite in GitHub Actions

**Why This Works:**
- Avoids all Databricks API calls in GitHub Actions
- No timeout issues
- Training completes successfully
- Models are still tracked (in SQLite)

### How It Works

1. **Detect GitHub Actions Environment**
   ```python
   is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
   ```

2. **Default to SQLite**
   ```python
   if is_github_actions and not force_databricks:
       return 'sqlite:///mlflow.db'
   ```

3. **Allow Override**
   - Set `FORCE_DATABRICKS=true` to use Databricks
   - Set `MLFLOW_TRACKING_URI=databricks` to force Databricks

## 📋 Code Changes

### 1. Updated `_get_mlflow_tracking_uri()`

**New Priority:**
1. `MLFLOW_TRACKING_URI` environment variable (if set)
2. **GitHub Actions detection** → Default to SQLite
3. Databricks (if credentials available)
4. SQLite fallback

**Key Changes:**
```python
# Detect GitHub Actions
is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
force_databricks = os.getenv('FORCE_DATABRICKS') == 'true'

if is_github_actions and not force_databricks:
    logger.info("Detected GitHub Actions environment")
    logger.info("Defaulting to SQLite to avoid Databricks timeout issues")
    return 'sqlite:///mlflow.db'
```

### 2. Updated GitHub Actions Workflow

**Removed:**
- Hardcoded `MLFLOW_TRACKING_URI=databricks`

**Added:**
- Comments explaining automatic SQLite fallback
- Instructions for forcing Databricks if needed

## 🎯 Expected Behavior

### In GitHub Actions (Default)

```
INFO - Detected GitHub Actions environment
INFO - Defaulting to SQLite to avoid Databricks timeout issues
INFO - To use Databricks in GitHub Actions, set FORCE_DATABRICKS=true
INFO - Training pipeline initialized
→ Tracking: sqlite:///mlflow.db
```

**Result:** ✅ No timeouts, training completes successfully

### If You Want Databricks in GitHub Actions

**Option 1: Set Environment Variable in Workflow**
```yaml
- name: Train model
  env:
    FORCE_DATABRICKS: 'true'
  run: |
    python src/train_model.py
```

**Option 2: Set MLFLOW_TRACKING_URI**
```yaml
- name: Train model
  env:
    MLFLOW_TRACKING_URI: 'databricks'
  run: |
    python src/train_model.py
```

## 🔧 Troubleshooting

### Issue: Still Getting Timeouts

**Solution 1: Verify SQLite is Being Used**
Check logs for:
```
INFO - Detected GitHub Actions environment
INFO - Defaulting to SQLite
```

**Solution 2: Force SQLite Explicitly**
Add to workflow:
```yaml
- name: Train model
  env:
    MLFLOW_TRACKING_URI: 'sqlite:///mlflow.db'
  run: |
    python src/train_model.py
```

**Solution 3: Check for Override**
Make sure `FORCE_DATABRICKS` is not set to `true`

### Issue: Want to Use Databricks

**If Databricks is Required:**
1. Set `FORCE_DATABRICKS=true` in workflow
2. Be aware that timeouts may still occur
3. Consider using Databricks Jobs API instead

**Alternative: Use Databricks Jobs**
- Submit training as Databricks job
- Avoids network connectivity issues
- Runs directly in Databricks environment

## 📊 Comparison: Before vs After

### Before (With Timeout)

```
INFO - Databricks credentials available, using Databricks MLflow tracking
... (8+ minutes of waiting) ...
TimeoutError: Timed out after 0:08:20
Error: Process completed with exit code 1.
```

### After (With SQLite Default)

```
INFO - Detected GitHub Actions environment
INFO - Defaulting to SQLite to avoid Databricks timeout issues
INFO - Training pipeline initialized
→ Tracking: sqlite:///mlflow.db
... (training completes successfully) ...
✓ Training completed successfully!
```

## ✅ Benefits

1. ✅ **No More Timeouts:** SQLite doesn't have network timeouts
2. ✅ **Faster Execution:** No waiting for Databricks API calls
3. ✅ **Reliable Training:** Training always completes
4. ✅ **Still Tracked:** Models tracked in SQLite database
5. ✅ **Flexible:** Can override to use Databricks if needed

## 🚀 Next Steps

1. **Commit and Push Changes**
   ```bash
   git add src/train_model.py .github/workflows/train-and-deploy.yml
   git commit -m "Fix Databricks timeout by defaulting to SQLite in GitHub Actions"
   git push origin main
   ```

2. **Trigger Workflow**
   - Push to main, or
   - Manually trigger workflow

3. **Verify Success**
   - Check logs for "Defaulting to SQLite"
   - Training should complete without timeouts

4. **If You Need Databricks**
   - Set `FORCE_DATABRICKS=true` in workflow
   - Or use Databricks Jobs API

## 📝 Summary

**Problem:** Databricks SDK timeout (8+ minutes) in GitHub Actions

**Root Cause:** Network connectivity issues + SDK retry logic

**Solution:** Default to SQLite in GitHub Actions environment

**Result:** ✅ No timeouts, reliable training, models still tracked

---

**Last Updated:** November 2025  
**Status:** ✅ Solution implemented and ready to test

