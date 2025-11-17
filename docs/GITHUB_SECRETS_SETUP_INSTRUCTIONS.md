# GitHub Secrets Setup Instructions

## Quick Setup Guide

This guide will help you set up GitHub Secrets for Databricks integration in your repository.

## Step 1: Navigate to GitHub Repository Settings

1. **Open your repository in a browser:**
   - Go to: https://github.com/nbetini99/gnu-mlops-repo

2. **Click on Settings:**
   - Click on "Settings" in the top menu bar

3. **Navigate to Secrets:**
   - In the left sidebar, click on: **Secrets and variables** → **Actions**

## Step 2: Add Required Secrets

Click **"New repository secret"** for each secret below:

### 1. DATABRICKS_HOST

- **Name:** `DATABRICKS_HOST`
- **Value:** `https://dbc-5e289a33-a706.cloud.databricks.com`
- **Description:** Your Databricks workspace URL

### 2. DATABRICKS_TOKEN

- **Name:** `DATABRICKS_TOKEN`
- **Value:** `dapicb7282387c50cc9aa3e8e3d18378b5fd`
- **Description:** Your Databricks access token

## Step 3: Add Optional Secrets (Recommended)

### 3. DATABRICKS_WORKSPACE_PATH

- **Name:** `DATABRICKS_WORKSPACE_PATH`
- **Value:** `/Users/nbatink@gmail.com/gnu-mlops/liveprod`
- **Description:** Workspace path for Databricks files

### 4. DATABRICKS_EXPERIMENT_PATH

- **Name:** `DATABRICKS_EXPERIMENT_PATH`
- **Value:** `/Users/nbatink@gmail.com/gnu-mlops/experiments`
- **Description:** MLflow experiment path

## Step 4: Verify Secrets Are Set

After adding all secrets, you should see them listed on the secrets page:

- ✅ DATABRICKS_HOST
- ✅ DATABRICKS_TOKEN
- ✅ DATABRICKS_WORKSPACE_PATH (optional)
- ✅ DATABRICKS_EXPERIMENT_PATH (optional)

**Note:** You cannot view secret values after adding them for security reasons.

## Step 5: Test GitHub Actions Workflow

1. **Go to Actions tab:**
   - Click on "Actions" in the top menu bar

2. **Trigger a workflow:**
   - Push a commit to trigger the workflow, OR
   - Click "Run workflow" button manually

3. **Check workflow logs:**
   - Look for: `✓ Databricks credentials found in GitHub Secrets`
   - Look for: `✓ Environment configured for Databricks`
   - Look for: `✓ Databricks credentials loaded from GitHub Secrets`

## Direct Link to Secrets Page

**Quick access:**
https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions

Click the link above to go directly to the secrets page.

## Visual Guide

### Screenshot Locations:

1. **Settings Page:**
   - Click "Settings" → "Secrets and variables" → "Actions"

2. **New Secret Button:**
   - Click "New repository secret" button (top right)

3. **Add Secret Form:**
   - Enter secret name
   - Enter secret value
   - Click "Add secret"

## Verification Checklist

- [ ] DATABRICKS_HOST secret added
- [ ] DATABRICKS_TOKEN secret added
- [ ] DATABRICKS_WORKSPACE_PATH secret added (optional)
- [ ] DATABRICKS_EXPERIMENT_PATH secret added (optional)
- [ ] All secrets visible on secrets page
- [ ] Workflow triggered successfully
- [ ] Workflow logs show credentials loaded

## Troubleshooting

### Issue: "Databricks credentials not found"

**Solution:**
- Verify secrets are added correctly
- Check secret names match exactly (case-sensitive)
- Ensure workflow has access to secrets

### Issue: "Connection failed"

**Solution:**
- Verify DATABRICKS_HOST is correct (no trailing slash)
- Verify DATABRICKS_TOKEN is valid and not expired
- Check network connectivity to Databricks

### Issue: "Authentication failed"

**Solution:**
- Verify token has correct permissions
- Check if token is expired
- Generate a new token if needed

## Security Notes

✅ **Secrets are encrypted** by GitHub
✅ **Never exposed** in logs or code
✅ **Only accessible** to repository administrators
✅ **Masked** in workflow logs automatically

## Next Steps

After setting up secrets:

1. ✅ Verify workflow runs successfully
2. ✅ Check workflow logs for credential loading
3. ✅ Test training pipeline
4. ✅ Test deployment pipeline
5. ✅ Monitor workflow execution

## Summary

You need to add these secrets to GitHub:

| Secret Name | Value | Required |
|------------|-------|----------|
| `DATABRICKS_HOST` | `https://dbc-5e289a33-a706.cloud.databricks.com` | Yes |
| `DATABRICKS_TOKEN` | `dapicb7282387c50cc9aa3e8e3d18378b5fd` | Yes |
| `DATABRICKS_WORKSPACE_PATH` | `/Users/nbatink@gmail.com/gnu-mlops/liveprod` | No |
| `DATABRICKS_EXPERIMENT_PATH` | `/Users/nbatink@gmail.com/gnu-mlops/experiments` | No |

## Quick Command Reference

To open the secrets page directly:
```bash
open "https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions"
```

Or run the setup script:
```bash
./SETUP_GITHUB_SECRETS.sh
```

---

**Last Updated:** November 2025  
**Repository:** https://github.com/nbetini99/gnu-mlops-repo

