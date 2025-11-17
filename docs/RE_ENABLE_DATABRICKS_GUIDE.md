# Guide to Re-enable Databricks Code

## 📁 File Location

**File:** `src/train_model.py`

This file contains all the commented Databricks code that can be re-enabled in the future.

---

## 📍 Location 1: Connection Test Function

**Lines:** ~58-171

**Function:** `_test_databricks_connection(timeout_seconds=10)`

### What It Does:
- Tests Databricks connectivity with a configurable timeout
- Performs a lightweight connection test (`list_experiments`)
- Returns `True` if connection is successful, `False` otherwise
- Handles both Unix/Linux/Mac (signal-based) and Windows (threading-based) timeouts

### How to Re-enable:

1. **Find the function** starting at line ~58
2. **Look for the comment block:**
   ```python
   # ============================================================================
   # DATABRICKS CONNECTION TEST - COMMENTED OUT TO AVOID TIMEOUTS
   # ============================================================================
   ```

3. **Uncomment all the code** inside the function body (lines ~86-168)
   - Remove all `#` characters from the function body
   - Keep the function signature and docstring

4. **Remove or modify** the fallback line:
   ```python
   # Always return False when commented out (forces SQLite fallback)
   return False
   ```
   - Remove this line or change it to actually call the uncommented code

### Example After Uncommenting:

```python
def _test_databricks_connection(timeout_seconds=10):
    """Test Databricks connection with timeout"""
    if not _validate_databricks_credentials():
        return False
    
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        # ... rest of uncommented code ...
```

---

## 📍 Location 2: Connection Logic in `_get_mlflow_tracking_uri()`

**Lines:** ~338-372

### What It Does:
- Validates Databricks credentials
- Calls `_test_databricks_connection()` to test connectivity
- Returns `'databricks'` if connection is successful
- Falls back to SQLite if connection fails

### How to Re-enable:

1. **Find the section** starting at line ~338
2. **Look for the comment block:**
   ```python
   # ========================================================================
   # DATABRICKS CONNECTION LOGIC - COMMENTED OUT TO AVOID TIMEOUTS
   # ========================================================================
   ```

3. **Uncomment the if block** (lines ~351-365):
   ```python
   if (env_tracking_uri == 'databricks' or config_tracking_uri == 'databricks') and (not is_github_actions or force_databricks):
       if _validate_databricks_credentials():
           logger.info("Testing Databricks connection...")
           if _test_databricks_connection(timeout_seconds=5):
               logger.info("Databricks connection successful, using Databricks MLflow tracking")
               return 'databricks'
           else:
               logger.warning("Databricks connection test failed or timed out")
               logger.info("Falling back to SQLite for local tracking")
               return 'sqlite:///mlflow.db'
       else:
           logger.warning("Databricks tracking URI specified but credentials not available")
           logger.info("Falling back to SQLite for local tracking")
           return 'sqlite:///mlflow.db'
   ```

4. **Remove or comment out** the fallback code (lines ~367-372):
   ```python
   # COMMENTED OUT: Skip Databricks connection attempts, use SQLite instead
   if (env_tracking_uri == 'databricks' or config_tracking_uri == 'databricks') and (not is_github_actions or force_databricks):
       logger.warning("Databricks connection logic is currently disabled to avoid timeout issues")
       logger.info("Falling back to SQLite for local tracking")
       logger.info("To enable Databricks, uncomment the connection test code in train_model.py")
       return 'sqlite:///mlflow.db'
   ```

---

## 📍 Location 3: Critical GitHub Actions Check

**Lines:** ~445-472

### What It Does:
- Forces SQLite in GitHub Actions environment
- Prevents any Databricks calls in GitHub Actions
- Checks `GITHUB_ACTIONS` environment variable

### To Allow Databricks in GitHub Actions:

**Option 1: Use FORCE_DATABRICKS Flag**

The code already supports this! Just set:
```bash
export FORCE_DATABRICKS=true
```

**Option 2: Modify the Check**

1. **Find the section** at line ~445
2. **Modify the check** to allow override:
   ```python
   is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
   force_databricks = os.getenv('FORCE_DATABRICKS') == 'true'
   
   if is_github_actions and not force_databricks:
       # Force SQLite
   ```

**Option 3: Remove GitHub Actions Check Entirely**

1. **Remove or comment out** lines ~445-460
2. **Let the normal logic** in `_get_mlflow_tracking_uri()` handle it

---

## 🔧 Step-by-Step Re-enabling Process

### Step 1: Uncomment Connection Test Function

1. Open `src/train_model.py`
2. Go to line ~58
3. Find `_test_databricks_connection()` function
4. Uncomment all code inside the function (remove `#` from lines ~86-168)
5. Remove the `return False` fallback

### Step 2: Uncomment Connection Logic

1. Go to line ~338
2. Find the "DATABRICKS CONNECTION LOGIC" comment block
3. Uncomment the if block (lines ~351-365)
4. Remove the fallback code (lines ~367-372)

### Step 3: Test Locally First

```bash
# Test with Databricks credentials
export DATABRICKS_HOST="your-host"
export DATABRICKS_TOKEN="your-token"
python src/train_model.py
```

### Step 4: Test in GitHub Actions (Optional)

If you want to test in GitHub Actions:
1. Set `FORCE_DATABRICKS=true` in workflow
2. Ensure network connectivity to Databricks
3. Monitor for timeout issues

---

## ⚠️ Important Notes

### Before Re-enabling:

1. **Ensure Network Connectivity:**
   - GitHub Actions runners can reach Databricks
   - Firewall rules allow connections
   - Databricks workspace is accessible

2. **Test Connection First:**
   - Test locally with Databricks credentials
   - Verify connection works before enabling in CI/CD

3. **Consider Alternatives:**
   - Use Databricks Jobs API (recommended for production)
   - Use self-hosted runners with better network access
   - Use VPN or network configuration

### After Re-enabling:

1. **Monitor for Timeouts:**
   - Watch GitHub Actions logs
   - Check for 8+ minute timeouts
   - Have fallback plan ready

2. **Set Appropriate Timeouts:**
   - Connection test: 5-10 seconds
   - Experiment setup: 30 seconds
   - Consider shorter timeouts for faster failures

---

## 📋 Quick Checklist

- [ ] Uncomment `_test_databricks_connection()` function (line ~58)
- [ ] Uncomment Databricks connection logic (line ~338)
- [ ] Remove fallback code that forces SQLite
- [ ] Test locally with Databricks credentials
- [ ] Verify network connectivity
- [ ] Test in GitHub Actions (if needed)
- [ ] Monitor for timeout issues

---

## 🔗 Related Files

- **`src/train_model.py`** - Main file with commented Databricks code
- **`.github/workflows/train-and-deploy.yml`** - GitHub Actions workflow
- **`docs/DATABRICKS_CONNECTIVITY_GUIDE.md`** - Options for improving connectivity

---

**Last Updated:** November 2025  
**File:** `src/train_model.py`  
**Status:** Code preserved and ready for re-enabling

