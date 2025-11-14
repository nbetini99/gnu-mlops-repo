# GitHub Secrets Setup Guide

## Overview

This guide explains how to securely configure Databricks credentials using GitHub Secrets. This ensures that sensitive credentials are never hardcoded in your codebase and are encrypted by GitHub.

## Required Secrets

You need to set the following secrets in your GitHub repository:

### Required Secrets

1. **`DATABRICKS_HOST`** (Required)
   - Your Databricks workspace URL
   - Example: `https://dbc-5e289a33-a706.cloud.databricks.com`

2. **`DATABRICKS_TOKEN`** (Required)
   - Your Databricks access token
   - Example: `dapicb7282387c50cc9aa3e8e3d18378b5fd`

### Optional Secrets

3. **`DATABRICKS_WORKSPACE_PATH`** (Optional)
   - Workspace path for your Databricks files
   - Default: `/Users/nbatink@gmail.com/gnu-mlops/liveprod`
   - Only set if different from default

4. **`DATABRICKS_EXPERIMENT_PATH`** (Optional)
   - MLflow experiment path
   - Default: `/Users/nbatink@gmail.com/gnu-mlops/experiments`
   - Only set if different from default

## Step-by-Step Setup Instructions

### 1. Navigate to GitHub Repository Settings

1. Go to your GitHub repository: `https://github.com/nbetini99/gnu-mlops-repo`
2. Click on **Settings** (top menu bar)
3. In the left sidebar, click on **Secrets and variables** → **Actions**

### 2. Add Required Secrets

#### Add DATABRICKS_HOST

1. Click **New repository secret**
2. Name: `DATABRICKS_HOST`
3. Value: `https://dbc-5e289a33-a706.cloud.databricks.com`
4. Click **Add secret**

#### Add DATABRICKS_TOKEN

1. Click **New repository secret**
2. Name: `DATABRICKS_TOKEN`
3. Value: `dapicb7282387c50cc9aa3e8e3d18378b5fd`
4. Click **Add secret**

#### Add DATABRICKS_WORKSPACE_PATH (Optional)

1. Click **New repository secret**
2. Name: `DATABRICKS_WORKSPACE_PATH`
3. Value: `/Users/nbatink@gmail.com/gnu-mlops/liveprod`
4. Click **Add secret**

#### Add DATABRICKS_EXPERIMENT_PATH (Optional)

1. Click **New repository secret**
2. Name: `DATABRICKS_EXPERIMENT_PATH`
3. Value: `/Users/nbatink@gmail.com/gnu-mlops/experiments`
4. Click **Add secret**

### 3. Verify Secrets

After adding all secrets, you should see them listed in the **Secrets and variables** → **Actions** page:

- ✅ DATABRICKS_HOST
- ✅ DATABRICKS_TOKEN
- ✅ DATABRICKS_WORKSPACE_PATH (optional)
- ✅ DATABRICKS_EXPERIMENT_PATH (optional)

**Note:** You cannot view the secret values after adding them for security reasons. You can only update or delete them.

## How GitHub Actions Uses These Secrets

The GitHub Actions workflow (`.github/workflows/train-and-deploy.yml`) automatically:

1. **Checks for secrets** at the start of the workflow
2. **Loads secrets** into environment variables if available
3. **Uses Databricks mode** if secrets are present
4. **Falls back to local mode** (SQLite) if secrets are not available

### Workflow Behavior

**With Secrets:**
- ✅ Uses Databricks for MLflow tracking
- ✅ Connects to your Databricks workspace
- ✅ Trains models on Databricks
- ✅ Deploys to Databricks Model Registry

**Without Secrets:**
- ✅ Uses SQLite for local MLflow tracking
- ✅ Generates synthetic data for training
- ✅ Works completely offline
- ✅ Perfect for testing and development

## Security Best Practices

### ✅ DO:

1. **Use GitHub Secrets** for all sensitive credentials
2. **Never commit** credentials to the repository
3. **Rotate tokens** regularly
4. **Use least privilege** - only grant necessary permissions
5. **Review access** - regularly audit who has access to secrets

### ❌ DON'T:

1. **Don't hardcode** credentials in code
2. **Don't commit** `.env` files with credentials
3. **Don't share** tokens in issues or pull requests
4. **Don't log** secrets in workflow logs
5. **Don't use** the same token for multiple environments

## Local Development Setup

For local development, create a `.env` file (never commit this):

```bash
# .env file (add to .gitignore)
DATABRICKS_HOST=https://dbc-5e289a33-a706.cloud.databricks.com
DATABRICKS_TOKEN=dapicb7282387c50cc9aa3e8e3d18378b5fd
DATABRICKS_WORKSPACE_PATH=/Users/nbatink@gmail.com/gnu-mlops/liveprod
DATABRICKS_EXPERIMENT_PATH=/Users/nbatink@gmail.com/gnu-mlops/experiments
MLFLOW_TRACKING_URI=databricks
```

Then source it:
```bash
source .env
# Or use: export $(cat .env | grep -v '^#' | xargs)
```

## Verifying Setup

### Check GitHub Actions Workflow

1. Push a commit to trigger the workflow
2. Go to **Actions** tab in GitHub
3. Click on the workflow run
4. Check the logs for:
   - `✓ Databricks credentials found in GitHub Secrets`
   - `✓ Environment configured for Databricks`

### Test Locally

```bash
# Set environment variables
export DATABRICKS_HOST="https://dbc-5e289a33-a706.cloud.databricks.com"
export DATABRICKS_TOKEN="dapicb7282387c50cc9aa3e8e3d18378b5fd"

# Run training
python src/train_model.py

# Check logs for successful Databricks connection
```

## Troubleshooting

### Issue: "Databricks credentials not found"

**Solution:** 
- Verify secrets are set in GitHub repository settings
- Check secret names match exactly (case-sensitive)
- Ensure workflow has access to secrets

### Issue: "Connection failed"

**Solution:**
- Verify `DATABRICKS_HOST` is correct (no trailing slash)
- Verify `DATABRICKS_TOKEN` is valid and not expired
- Check network connectivity to Databricks

### Issue: "Authentication failed"

**Solution:**
- Verify token has correct permissions
- Check if token is expired
- Generate a new token if needed

## Getting Databricks Access Token

1. Log in to your Databricks workspace
2. Click on your username (top right)
3. Select **User Settings**
4. Go to **Access Tokens** tab
5. Click **Generate New Token**
6. Copy the token (you won't see it again!)
7. Add it to GitHub Secrets as `DATABRICKS_TOKEN`

## Updating Secrets

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click on the secret you want to update
3. Click **Update** button
4. Enter new value
5. Click **Update secret**

## Removing Secrets

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click on the secret you want to remove
3. Click **Delete** button
4. Confirm deletion

**Note:** Removing secrets will cause the workflow to fall back to local mode (SQLite).

## Summary

✅ **Secrets are encrypted** by GitHub
✅ **Never exposed** in logs or code
✅ **Automatically loaded** in GitHub Actions
✅ **Easy to manage** through GitHub UI
✅ **Safe for collaboration** - secrets are not visible to collaborators

## Quick Reference

| Secret Name | Required | Default Value | Description |
|------------|----------|---------------|-------------|
| `DATABRICKS_HOST` | Yes | - | Databricks workspace URL |
| `DATABRICKS_TOKEN` | Yes | - | Databricks access token |
| `DATABRICKS_WORKSPACE_PATH` | No | `/Users/nbatink@gmail.com/gnu-mlops/liveprod` | Workspace path |
| `DATABRICKS_EXPERIMENT_PATH` | No | `/Users/nbatink@gmail.com/gnu-mlops/experiments` | MLflow experiment path |

## Next Steps

1. ✅ Set up GitHub Secrets (this guide)
2. ✅ Verify workflow runs successfully
3. ✅ Test local development setup
4. ✅ Deploy to staging/production
5. ✅ Monitor workflow logs

---

**Security Note:** Keep your Databricks tokens secure and rotate them regularly. Never share tokens or commit them to version control.

---

**Last Updated:** November 2025  
**Maintained By:** Narsimha Betini

