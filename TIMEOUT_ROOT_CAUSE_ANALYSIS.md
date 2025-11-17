# Databricks Timeout Root Cause Analysis

## 🔍 Why the Timeout is Happening

### The Problem

The timeout occurs in the **Databricks SDK** during actual API calls, not just during connection tests:

```
File "databricks/sdk/retries.py", line 67
raise TimeoutError(f"Timed out after {timeout}") from last_err
TimeoutError: Timed out after 0:08:20
```

### Root Causes

1. **Network Connectivity Issues**
   - GitHub Actions runners may have limited network access to Databricks
   - Firewall or security policies blocking connections
   - Databricks workspace might be in a private network

2. **Databricks SDK Internal Timeout**
   - SDK has built-in 8-minute timeout for retries
   - Multiple retry attempts before giving up
   - Each retry waits longer, accumulating to 8+ minutes

3. **MLflow Operations Triggering SDK Calls**
   - `mlflow.set_experiment()` → Calls Databricks API
   - `mlflow.start_run()` → Calls Databricks API
   - `mlflow.log_metric()` → Calls Databricks API
   - Each operation can trigger SDK retries

4. **Connection Test May Pass, But Operations Fail**
   - Connection test might succeed (lightweight operation)
   - But actual MLflow operations fail (heavier operations)
   - SDK retries accumulate to 8-minute timeout

## 🎯 Solution Strategy

### Option 1: Force SQLite in GitHub Actions (Recommended)

**Best for:** Unreliable Databricks connectivity from GitHub Actions

**Approach:**
- Detect GitHub Actions environment
- Automatically use SQLite instead of Databricks
- No connection attempts to Databricks

### Option 2: Improve Connection Test

**Best for:** When Databricks should work but is slow

**Approach:**
- More robust connection test
- Test actual MLflow operations, not just connectivity
- Shorter timeout (5 seconds)
- Better fallback logic

### Option 3: Hybrid Approach (Best)

**Best for:** Flexibility and reliability

**Approach:**
- Check for `GITHUB_ACTIONS` environment variable
- If in GitHub Actions, default to SQLite (can be overridden)
- If local, test Databricks connection
- Provide environment variable to force mode

## 📋 Recommended Solution

**Force SQLite in GitHub Actions by default**, but allow override:

1. Detect GitHub Actions environment
2. Default to SQLite in GitHub Actions
3. Allow override via environment variable
4. Test connection only if explicitly requested

This prevents timeouts while maintaining flexibility.

