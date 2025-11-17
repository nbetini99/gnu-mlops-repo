# Databricks Connectivity Guide for GitHub Actions

## 🔍 Current Issue

**Problem:** GitHub Actions cannot reliably connect to Databricks, causing 8+ minute timeouts.

**Root Cause:**
- Network connectivity issues from GitHub Actions runners to Databricks
- Databricks SDK internal timeout (8 minutes)
- Firewall/security policies blocking connections

## ✅ Immediate Solution (Implemented)

**Default to SQLite in GitHub Actions** - This is already implemented and will prevent timeouts.

## 🔧 Options to Improve Databricks Connectivity

### Option 1: Use Databricks Jobs API (Recommended)

**Best Solution:** Instead of running training in GitHub Actions, submit it as a Databricks Job.

**Benefits:**
- Runs directly in Databricks environment (no network issues)
- Better performance and resource management
- Native Databricks integration

**How to Implement:**

1. **Create Databricks Job:**
   ```python
   from databricks.sdk import WorkspaceClient
   from databricks.sdk.service import jobs
   
   w = WorkspaceClient()
   
   job = w.jobs.create(
       name="MLOps Training Pipeline",
       tasks=[jobs.Task(
           task_key="train_model",
           spark_python_task=jobs.SparkPythonTask(
               python_file="dbfs:/path/to/train_model.py"
           ),
           existing_cluster_id="your-cluster-id"
       )]
   )
   ```

2. **Trigger from GitHub Actions:**
   ```yaml
   - name: Submit Databricks Job
     run: |
       databricks jobs run-now --job-id ${{ secrets.DATABRICKS_JOB_ID }}
   ```

### Option 2: Use Databricks Connect

**Alternative:** Use Databricks Connect to run code locally but connect to Databricks.

**Setup:**
```bash
pip install databricks-connect
databricks-connect configure
```

**Limitations:**
- Still requires network connectivity
- May have same timeout issues

### Option 3: VPN or Network Configuration

**For Enterprise:** Configure VPN or network rules to allow GitHub Actions to reach Databricks.

**Steps:**
1. Whitelist GitHub Actions IP ranges in Databricks firewall
2. Use VPN or private network connection
3. Configure network security groups

**GitHub Actions IP Ranges:**
- Check: https://api.github.com/meta
- Add to Databricks allowed IPs

### Option 4: Use Self-Hosted Runners

**Alternative:** Use self-hosted GitHub Actions runners with better network access.

**Benefits:**
- Full control over network configuration
- Can configure VPN/firewall rules
- Better connectivity to Databricks

**Setup:**
1. Set up self-hosted runner on machine with Databricks access
2. Configure runner in GitHub repository settings
3. Use `runs-on: self-hosted` in workflow

### Option 5: Force Databricks with Shorter Timeout

**If you must use Databricks:** Set shorter timeout and handle failures gracefully.

**In workflow:**
```yaml
- name: Train model
  env:
    FORCE_DATABRICKS: 'true'
    DATABRICKS_REQUEST_TIMEOUT: '30'  # 30 seconds
  timeout-minutes: 2  # Fail fast if takes too long
  run: |
    python src/train_model.py
```

## 📋 Recommended Approach

### For Production: Use Databricks Jobs

**Best Practice:**
1. Store training code in Databricks workspace (DBFS)
2. Create Databricks Job for training
3. Trigger job from GitHub Actions
4. Job runs in Databricks environment (no connectivity issues)

**Workflow:**
```
GitHub Actions
  → Trigger Databricks Job
    → Job runs in Databricks
      → Training completes
        → Results back to GitHub Actions
```

### For Development: Use SQLite

**Current Implementation:**
- Defaults to SQLite in GitHub Actions
- No connectivity issues
- Fast and reliable
- Models still tracked

## 🚀 Implementation Steps

### Step 1: Current Fix (Already Done)

✅ Code defaults to SQLite in GitHub Actions
✅ No Databricks API calls = No timeouts

### Step 2: If You Need Databricks

**Option A: Use Databricks Jobs (Recommended)**

1. Upload training script to DBFS:
   ```bash
   databricks fs cp src/train_model.py dbfs:/scripts/train_model.py
   ```

2. Create Databricks Job:
   ```python
   # Create job via Databricks UI or API
   ```

3. Update GitHub Actions workflow:
   ```yaml
   - name: Submit Databricks Job
     run: |
       databricks jobs run-now --job-id ${{ secrets.DATABRICKS_JOB_ID }}
   ```

**Option B: Force Databricks (Not Recommended)**

1. Set environment variable:
   ```yaml
   - name: Train model
     env:
       FORCE_DATABRICKS: 'true'
     run: |
       python src/train_model.py
   ```

2. Be aware: May still timeout if connectivity is poor

## 🔍 Troubleshooting Connectivity

### Check Network Connectivity

**From GitHub Actions:**
```yaml
- name: Test Databricks Connectivity
  run: |
    curl -v https://dbc-5e289a33-a706.cloud.databricks.com
    ping -c 3 dbc-5e289a33-a706.cloud.databricks.com
```

### Check Databricks Access

**Verify credentials:**
```bash
databricks configure --token
databricks clusters list
```

### Check Firewall Rules

**In Databricks:**
1. Go to Admin Settings
2. Check IP Access Lists
3. Ensure GitHub Actions IPs are allowed

## 📊 Comparison: Options

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **SQLite (Current)** | ✅ No timeouts<br>✅ Fast<br>✅ Reliable | ❌ Not in Databricks | Development, CI/CD |
| **Databricks Jobs** | ✅ Native integration<br>✅ No connectivity issues<br>✅ Better resources | ❌ More setup | Production |
| **Force Databricks** | ✅ Direct connection | ❌ May timeout<br>❌ Network issues | Testing only |
| **Self-Hosted Runners** | ✅ Full control<br>✅ Better network | ❌ Maintenance<br>❌ Setup complexity | Enterprise |

## ✅ Current Status

**Implemented:**
- ✅ Defaults to SQLite in GitHub Actions
- ✅ Prevents all Databricks API calls
- ✅ No timeout issues
- ✅ Training completes successfully

**If you need Databricks:**
- Use Databricks Jobs API (recommended)
- Or set `FORCE_DATABRICKS=true` (may still timeout)

## 🎯 Next Steps

1. **For Now:** Use SQLite (already working)
2. **For Production:** Set up Databricks Jobs
3. **For Testing:** Try `FORCE_DATABRICKS=true` with shorter timeout

---

**Last Updated:** November 2025  
**Status:** ✅ SQLite default implemented, Databricks Jobs recommended for production

