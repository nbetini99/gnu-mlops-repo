# Automated GitHub Secrets Setup

## ⚠️ Important: GitHub API Authentication

GitHub **no longer accepts passwords** for API authentication. You need to create a **Personal Access Token** first.

## Quick Setup (Automated)

### Step 1: Create Personal Access Token

1. **Token creation page should be open in your browser**
   - If not, go to: https://github.com/settings/tokens/new

2. **Fill in the form:**
   - **Note:** `GNU MLOps Secrets Setup`
   - **Expiration:** `90 days` (or your preference)
   - **Select scope:** ✅ **repo** (Full control of private repositories)

3. **Click:** `Generate token`

4. **⚠️ IMPORTANT:** Copy the token immediately (you won't see it again!)

### Step 2: Run Automated Setup

After creating the token, run:

```bash
./setup_secrets_now.sh
```

Enter your token when prompted, and all secrets will be set automatically.

---

## Manual Setup (Alternative)

If you prefer to set secrets manually:

1. **Go to Secrets Page:**
   https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions

2. **Click "New repository secret"** for each:

   **Required Secrets:**
   - **DATABRICKS_HOST:** `https://dbc-5e289a33-a706.cloud.databricks.com`
   - **DATABRICKS_TOKEN:** `dapicb7282387c50cc9aa3e8e3d18378b5fd`

   **Optional Secrets:**
   - **DATABRICKS_WORKSPACE_PATH:** `/Users/nbatink@gmail.com/gnu-mlops/liveprod`
   - **DATABRICKS_EXPERIMENT_PATH:** `/Users/nbatink@gmail.com/gnu-mlops/experiments`

---

## Verification

After setting up secrets:

1. **Check secrets page:**
   - All secrets should be listed
   - You cannot view values (for security)

2. **Test workflow:**
   - Go to: https://github.com/nbetini99/gnu-mlops-repo/actions
   - Trigger a workflow
   - Check logs for: `✓ Databricks credentials found in GitHub Secrets`

---

## Troubleshooting

### "Invalid token" error
- Verify token has `repo` scope
- Check if token is expired
- Create a new token if needed

### "Access forbidden" error
- Verify you have admin access to the repository
- Check token permissions

### "Connection failed" error
- Check network connectivity
- Verify GitHub API is accessible

---

**Ready to proceed?** Run `./setup_secrets_now.sh` after creating your token!

