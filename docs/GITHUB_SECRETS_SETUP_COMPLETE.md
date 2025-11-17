# GitHub Secrets Setup - Complete Guide

## 🎯 Quick Setup (Recommended)

### Direct Link to Secrets Page
**👉 https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions**

### Step-by-Step Instructions

1. **Click the link above** (or copy/paste into your browser)

2. **Click "New repository secret"** button (top right)

3. **Add each secret below:**

---

## Required Secrets

### 1. DATABRICKS_HOST

**Name:** `DATABRICKS_HOST`
**Value:** `https://dbc-5e289a33-a706.cloud.databricks.com`

**Steps:**
1. Click "New repository secret"
2. Name: `DATABRICKS_HOST`
3. Value: `https://dbc-5e289a33-a706.cloud.databricks.com`
4. Click "Add secret"

### 2. DATABRICKS_TOKEN

**Name:** `DATABRICKS_TOKEN`
**Value:** `dapicb7282387c50cc9aa3e8e3d18378b5fd`

**Steps:**
1. Click "New repository secret"
2. Name: `DATABRICKS_TOKEN`
3. Value: `dapicb7282387c50cc9aa3e8e3d18378b5fd`
4. Click "Add secret"

---

## Optional Secrets (Recommended)

### 3. DATABRICKS_WORKSPACE_PATH

**Name:** `DATABRICKS_WORKSPACE_PATH`
**Value:** `/Users/nbatink@gmail.com/gnu-mlops/liveprod`

**Steps:**
1. Click "New repository secret"
2. Name: `DATABRICKS_WORKSPACE_PATH`
3. Value: `/Users/nbatink@gmail.com/gnu-mlops/liveprod`
4. Click "Add secret"

### 4. DATABRICKS_EXPERIMENT_PATH

**Name:** `DATABRICKS_EXPERIMENT_PATH`
**Value:** `/Users/nbatink@gmail.com/gnu-mlops/experiments`

**Steps:**
1. Click "New repository secret"
2. Name: `DATABRICKS_EXPERIMENT_PATH`
3. Value: `/Users/nbatink@gmail.com/gnu-mlops/experiments`
4. Click "Add secret"

---

## Verification Checklist

After adding all secrets, verify:

- [ ] DATABRICKS_HOST is listed
- [ ] DATABRICKS_TOKEN is listed
- [ ] DATABRICKS_WORKSPACE_PATH is listed (optional)
- [ ] DATABRICKS_EXPERIMENT_PATH is listed (optional)

**Note:** You cannot view secret values after adding them for security reasons.

---

## Testing

### 1. Test GitHub Actions Workflow

1. Go to: **Actions** tab in your repository
2. Trigger a workflow:
   - Push a commit, OR
   - Click "Run workflow" button manually
3. Check workflow logs for:
   - ✅ `✓ Databricks credentials found in GitHub Secrets`
   - ✅ `✓ Environment configured for Databricks`
   - ✅ `✓ Databricks credentials loaded from GitHub Secrets`

### 2. Verify Workflow Success

If secrets are set correctly, you should see:
- ✅ Workflow completes successfully
- ✅ Training runs without errors
- ✅ Model is registered in MLflow
- ✅ Deployment to staging works (if configured)

---

## Alternative Setup Methods

### Method 1: Interactive Setup Script

Run the interactive setup script:

```bash
./SETUP_GITHUB_SECRETS.sh
```

This will display step-by-step instructions.

### Method 2: Python Script (Requires GitHub Token)

If you have a GitHub Personal Access Token:

```bash
# Install required packages
pip install requests pynacl

# Run setup script
python3 setup_github_secrets.py --token YOUR_GITHUB_TOKEN
```

**To get a GitHub Personal Access Token:**
1. Go to: https://github.com/settings/tokens
2. Click: "Generate new token (classic)"
3. Select scope: **repo** (full control)
4. Generate and copy the token

### Method 3: Manual Setup (Recommended)

Use the direct link above and follow the step-by-step instructions.

---

## Quick Reference

### Secret Values (Copy/Paste Ready)

```
DATABRICKS_HOST
https://dbc-5e289a33-a706.cloud.databricks.com

DATABRICKS_TOKEN
dapicb7282387c50cc9aa3e8e3d18378b5fd

DATABRICKS_WORKSPACE_PATH
/Users/nbatink@gmail.com/gnu-mlops/liveprod

DATABRICKS_EXPERIMENT_PATH
/Users/nbatink@gmail.com/gnu-mlops/experiments
```

### Direct Links

- **Secrets Page:** https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
- **Actions Page:** https://github.com/nbetini99/gnu-mlops-repo/actions
- **Repository:** https://github.com/nbetini99/gnu-mlops-repo

---

## Troubleshooting

### Issue: "Databricks credentials not found"

**Solution:**
1. Verify secrets are added in the correct repository
2. Check secret names match exactly (case-sensitive)
3. Ensure you're looking at "Actions" secrets (not "Dependencies")
4. Try triggering the workflow again

### Issue: "Connection failed"

**Solution:**
1. Verify DATABRICKS_HOST is correct (no trailing slash)
2. Verify DATABRICKS_TOKEN is valid and not expired
3. Check network connectivity to Databricks
4. Verify Databricks workspace is accessible

### Issue: "Authentication failed"

**Solution:**
1. Verify DATABRICKS_TOKEN is correct
2. Check if token has expired
3. Generate a new Databricks token if needed
4. Update the secret with the new token

### Issue: "Secrets not showing in workflow"

**Solution:**
1. Verify secrets are added to the correct repository
2. Check if you have admin access to the repository
3. Ensure secrets are added to "Actions" secrets (not "Dependencies")
4. Try triggering a new workflow run

---

## Security Best Practices

### ✅ DO:

1. **Use GitHub Secrets** for all sensitive credentials
2. **Never commit** credentials to the repository
3. **Rotate tokens** regularly (every 90 days)
4. **Use least privilege** - only grant necessary permissions
5. **Review access** - regularly audit who has access to secrets

### ❌ DON'T:

1. **Don't hardcode** credentials in code
2. **Don't commit** `.env` files with credentials
3. **Don't share** tokens in issues or pull requests
4. **Don't log** secrets in workflow logs
5. **Don't use** the same token for multiple environments

---

## Next Steps

After setting up secrets:

1. ✅ **Verify secrets are set correctly**
   - Check secrets page
   - Verify all secrets are listed

2. ✅ **Test GitHub Actions workflow**
   - Go to Actions tab
   - Trigger a workflow
   - Check logs for successful credential loading

3. ✅ **Verify training works**
   - Check workflow logs
   - Verify model training completes
   - Check MLflow for registered models

4. ✅ **Test deployment**
   - Verify deployment to staging works
   - Check deployment logs
   - Verify model is accessible

5. ✅ **Monitor workflow**
   - Check workflow runs regularly
   - Monitor for any errors
   - Review logs for issues

---

## Summary

### Required Secrets (Must Set)

- ✅ `DATABRICKS_HOST`: `https://dbc-5e289a33-a706.cloud.databricks.com`
- ✅ `DATABRICKS_TOKEN`: `dapicb7282387c50cc9aa3e8e3d18378b5fd`

### Optional Secrets (Recommended)

- ✅ `DATABRICKS_WORKSPACE_PATH`: `/Users/nbatink@gmail.com/gnu-mlops/liveprod`
- ✅ `DATABRICKS_EXPERIMENT_PATH`: `/Users/nbatink@gmail.com/gnu-mlops/experiments`

### Setup Methods

1. **Manual Setup** (Recommended) - Use direct link above
2. **Interactive Script** - Run `./SETUP_GITHUB_SECRETS.sh`
3. **Python Script** - Run `python3 setup_github_secrets.py --token YOUR_TOKEN`

### Verification

- ✅ Secrets listed on secrets page
- ✅ Workflow runs successfully
- ✅ Logs show credentials loaded
- ✅ Training completes successfully

---

## Quick Start Command

**Open secrets page directly:**
```bash
open "https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions"
```

**Or run interactive script:**
```bash
./SETUP_GITHUB_SECRETS.sh
```

---

**Status:** ✅ Ready to Set Up  
**Last Updated:** November 2025  
**Repository:** https://github.com/nbetini99/gnu-mlops-repo

