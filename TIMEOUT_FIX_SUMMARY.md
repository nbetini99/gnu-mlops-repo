# Databricks Timeout Fix Summary

## 🔍 Issue Identified

**Error:**
```
2025-11-17 05:12:07,532 - __main__ - INFO - Databricks credentials available, using Databricks MLflow tracking
2025-11-17 05:20:31,561 - __main__ - WARNING - Could not set experiment ***: Timed out after 0:08:20
```

**Problem:**
- `mlflow.set_experiment()` was hanging for 8+ minutes when Databricks was slow or unreachable
- No timeout mechanism was in place
- No automatic fallback to local SQLite when Databricks times out

## ✅ Fixes Applied

### 1. Added Timeout Function

**New Function: `_set_experiment_with_timeout()`**
- Implements 30-second timeout for Databricks experiment setup
- Uses signal-based timeout on Unix/Linux/Mac (SIGALRM)
- Uses threading-based timeout on Windows
- Automatically detects timeout and connection errors

**Features:**
- ✅ 30-second timeout for Databricks (configurable)
- ✅ 10-second timeout for local SQLite
- ✅ Automatic fallback to SQLite on timeout
- ✅ Graceful error handling

### 2. Enhanced Experiment Setup Logic

**Before:**
```python
try:
    mlflow.set_experiment(gnu_mlflow_config)
except Exception as e:
    logger.warning(f"Could not set experiment {gnu_mlflow_config}: {e}")
    mlflow.set_experiment("gnu-mlops-experiments")
```

**After:**
```python
success, fallback_uri = _set_experiment_with_timeout(gnu_mlflow_config, tracking_uri, timeout_seconds=30)
if not success:
    if fallback_uri:
        # Fallback to SQLite if Databricks times out
        tracking_uri = fallback_uri
        mlflow.set_tracking_uri(tracking_uri)
        # Use local experiment name
        mlflow.set_experiment(experiment_name)
```

### 3. Automatic Fallback Mechanism

**When Databricks times out:**
1. ✅ Detects timeout after 30 seconds
2. ✅ Logs warning message
3. ✅ Automatically switches to SQLite (`sqlite:///mlflow.db`)
4. ✅ Extracts simpler experiment name from Databricks path
5. ✅ Sets local experiment successfully
6. ✅ Continues training with local tracking

## 📋 Code Changes

### New Imports
```python
import signal
from contextlib import contextmanager
```

### New Functions
1. `timeout_context()` - Context manager for timeout operations (not used directly, but available)
2. `_set_experiment_with_timeout()` - Main timeout function with fallback logic

### Modified Sections
1. **Experiment Setup** (lines 289-346)
   - Added timeout protection
   - Added automatic fallback to SQLite
   - Better error handling

## ✅ Expected Behavior

### Scenario 1: Databricks Works (Normal)
```
INFO - Databricks credentials available, using Databricks MLflow tracking
INFO - Training pipeline initialized
INFO - → Experiment: /Users/nbatink@gmail.com/gnu-mlops/experiments
INFO - → Tracking: databricks
```
**Result:** Uses Databricks, no timeout

### Scenario 2: Databricks Times Out (Fixed)
```
INFO - Databricks credentials available, using Databricks MLflow tracking
WARNING - Timeout setting experiment '/Users/.../experiments': Setting experiment timed out after 30 seconds
INFO - Falling back to local SQLite tracking due to timeout
WARNING - Databricks experiment setup timed out, falling back to local SQLite
INFO - Using local experiment: experiments
INFO - Training pipeline initialized
INFO - → Experiment: experiments
INFO - → Tracking: sqlite:///mlflow.db
```
**Result:** Automatically falls back to SQLite, training continues

### Scenario 3: Databricks Connection Error (Fixed)
```
INFO - Databricks credentials available, using Databricks MLflow tracking
WARNING - Error setting experiment '...': Connection timeout
INFO - Falling back to local SQLite tracking due to connection issue
INFO - Using local experiment: experiments
```
**Result:** Detects connection error, falls back to SQLite

## 🎯 Benefits

1. ✅ **No More Hanging:** Training won't hang for 8+ minutes
2. ✅ **Automatic Recovery:** Falls back to local SQLite automatically
3. ✅ **Faster Failures:** 30-second timeout instead of 8+ minutes
4. ✅ **Better User Experience:** Clear warning messages
5. ✅ **Training Continues:** Model training proceeds even if Databricks is down

## 📝 Timeout Configuration

**Current Settings:**
- Databricks experiment setup: **30 seconds**
- Local SQLite experiment setup: **10 seconds**

**To Change Timeout:**
Modify the `timeout_seconds` parameter in `_set_experiment_with_timeout()` calls:
```python
# Line 320 - Databricks timeout
success, fallback_uri = _set_experiment_with_timeout(gnu_mlflow_config, tracking_uri, timeout_seconds=30)

# Line 305 - Local timeout
success, fallback_uri = _set_experiment_with_timeout(experiment_name, tracking_uri, timeout_seconds=10)
```

## ✅ Testing

**To test the fix:**
```bash
# Run training (will automatically fallback if Databricks times out)
python src/train_model.py
```

**Expected output if Databricks times out:**
- Warning message about timeout
- Automatic fallback to SQLite
- Training continues successfully
- Model saved to local MLflow database

## 🔧 Troubleshooting

**If you still see timeouts:**
1. Check network connectivity to Databricks
2. Verify Databricks credentials are correct
3. Check if Databricks workspace is accessible
4. Consider using local mode explicitly: `export MLFLOW_TRACKING_URI=sqlite:///mlflow.db`

**To force local mode:**
```bash
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db
python src/train_model.py
```

---

**Last Updated:** November 2025  
**Status:** ✅ Timeout fix implemented and tested

