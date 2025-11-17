# Databricks Timeout Fix for GitHub Actions

## 🔍 Issue

**Error in GitHub Actions:**
```
TimeoutError: Timed out after 0:08:20
Error: Process completed with exit code 1.
```

**Root Cause:**
- Databricks SDK has an internal 8-minute timeout
- Code was trying to use Databricks even when unreachable
- No early detection of connectivity issues

## ✅ Fix Applied

### 1. Added Connection Test Function

**New Function: `_test_databricks_connection()`**
- Tests Databricks connectivity with 10-second timeout
- Performs lightweight operation (`list_experiments`)
- Fails fast if Databricks is unreachable
- Returns `True` if connection works, `False` otherwise

### 2. Early Connection Testing

**Before deciding to use Databricks:**
```python
# OLD: Just checked credentials, then tried to use Databricks
if _validate_databricks_credentials():
    return 'databricks'  # Could timeout 8+ minutes later
```

**After:**
```python
# NEW: Test connection first, then decide
if _validate_databricks_credentials():
    logger.info("Testing Databricks connection...")
    if _test_databricks_connection(timeout_seconds=10):
        logger.info("Databricks connection successful")
        return 'databricks'
    else:
        logger.warning("Connection test failed, falling back to SQLite")
        return 'sqlite:///mlflow.db'
```

### 3. Updated GitHub Actions Workflow

**Changed:**
- Removed hardcoded `MLFLOW_TRACKING_URI=databricks` from environment
- Code now decides based on connection test
- Allows automatic fallback to SQLite

**Before:**
```yaml
echo "MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI" >> $GITHUB_ENV
```

**After:**
```yaml
# Don't set MLFLOW_TRACKING_URI here - let the code decide based on connection test
# This allows automatic fallback to SQLite if Databricks is unreachable
```

## 🎯 How It Works Now

### Step-by-Step Flow:

1. **Credentials Check:**
   - Verify `DATABRICKS_HOST` and `DATABRICKS_TOKEN` exist
   - If missing → Use SQLite immediately

2. **Connection Test (NEW):**
   - Attempt lightweight connection to Databricks
   - 10-second timeout
   - If successful → Use Databricks
   - If fails/times out → Use SQLite

3. **Training Proceeds:**
   - Uses whichever backend worked (Databricks or SQLite)
   - No more 8-minute timeouts

## ✅ Expected Behavior

### Scenario 1: Databricks Works

```
INFO - Testing Databricks connection...
INFO - Databricks connection successful, using Databricks MLflow tracking
INFO - Training pipeline initialized
→ Tracking: databricks
```

### Scenario 2: Databricks Unreachable (Fixed)

```
INFO - Testing Databricks connection...
WARNING - Databricks connection test timed out after 10 seconds
WARNING - Databricks connection test failed or timed out
INFO - Falling back to SQLite for local tracking
INFO - Training pipeline initialized
→ Tracking: sqlite:///mlflow.db
```

**Result:** Training continues with SQLite, no 8-minute wait!

## 📋 Code Changes

### Files Modified:

1. **`src/train_model.py`**
   - Added `_test_databricks_connection()` function
   - Modified `_get_mlflow_tracking_uri()` to test connection first
   - Early fallback to SQLite

2. **`.github/workflows/train-and-deploy.yml`**
   - Removed hardcoded `MLFLOW_TRACKING_URI=databricks`
   - Added comment explaining connection test logic

## 🚀 Benefits

1. ✅ **No More 8-Minute Timeouts:** Fails fast after 10 seconds
2. ✅ **Automatic Fallback:** Switches to SQLite automatically
3. ✅ **Training Continues:** Model training proceeds even if Databricks is down
4. ✅ **Better User Experience:** Clear warning messages
5. ✅ **Works in GitHub Actions:** Handles network issues gracefully

## 🔧 Testing

**To test locally:**
```bash
# With Databricks credentials (will test connection)
python src/train_model.py

# Force SQLite (skip Databricks)
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db
python src/train_model.py
```

**In GitHub Actions:**
- Code automatically tests connection
- Falls back to SQLite if Databricks is unreachable
- Training completes successfully

## 📝 Timeout Configuration

**Current Settings:**
- Connection test: **10 seconds**
- Experiment setup: **30 seconds** (with fallback)

**To Change:**
Modify `timeout_seconds` parameter:
```python
# Line 310 - Connection test timeout
if _test_databricks_connection(timeout_seconds=10):
```

## ✅ Verification

**Check logs for:**
- `Testing Databricks connection...` - Connection test started
- `Databricks connection successful` - Using Databricks
- `Connection test failed or timed out` - Using SQLite fallback
- `Training pipeline initialized` - Ready to train

---

**Last Updated:** November 2025  
**Status:** ✅ Connection test and early fallback implemented

