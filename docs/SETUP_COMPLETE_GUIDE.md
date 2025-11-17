# Complete Setup Guide - GitHub Secrets Configuration

## ⚠️ Important Note

GitHub **no longer accepts passwords** for API authentication. You **must** create a **Personal Access Token** manually in the browser. However, once you have the token, the setup process is fully automated.

## 🚀 Quick Start (Recommended)

### Step 1: Create Personal Access Token

1. **Open token creation page:**
   - Link: https://github.com/settings/tokens/new
   - (Should already be open in your browser)

2. **Fill in the form:**
   - **Note:** `GNU MLOps Secrets Setup`
   - **Expiration:** `90 days` (or your preference)
   - **Select scope:** ✅ **repo** (Full control of private repositories)
   - Click **"Generate token"**

3. **⚠️ IMPORTANT:** Copy the token immediately (you won't see it again!)

### Step 2: Run Automated Setup

After creating the token, run this command:

```bash
./QUICK_START_SETUP.sh
```

Or use the detailed script:

```bash
./create_token_and_setup.sh
```

Enter your token when prompted, and all secrets will be set automatically!

## 📋 What Gets Set Up

The following secrets will be automatically configured:

### Required Secrets:
- **DATABRICKS_HOST:** `https://dbc-5e289a33-a706.cloud.databricks.com`
- **DATABRICKS_TOKEN:** `dapicb7282387c50cc9aa3e8e3d18378b5fd`

### Optional Secrets:
- **DATABRICKS_WORKSPACE_PATH:** `/Users/nbatink@gmail.com/gnu-mlops/liveprod`
- **DATABRICKS_EXPERIMENT_PATH:** `/Users/nbatink@gmail.com/gnu-mlops/experiments`

## ✅ Verification

After running the setup script:

1. **Check secrets page:**
   - Go to: https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
   - Verify all secrets are listed

2. **Test GitHub Actions:**
   - Go to: https://github.com/nbetini99/gnu-mlops-repo/actions
   - Trigger a workflow
   - Check logs for: `✓ Databricks credentials found in GitHub Secrets`

## 🔄 Alternative Methods

### Method 1: Manual Setup

If you prefer to set secrets manually:

1. Go to: https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
2. Click **"New repository secret"** for each secret
3. Enter the name and value for each secret
4. Click **"Add secret"**

### Method 2: Using Environment Variable

```bash
# 1. Create token at https://github.com/settings/tokens/new
# 2. Export token
export GITHUB_TOKEN=your_token_here

# 3. Run setup script
./venv/bin/python3 setup_secrets_with_auth.py --token $GITHUB_TOKEN --username nbetini99
```

### Method 3: Using Setup Script Directly

```bash
# 1. Create token
# 2. Run setup script
./setup_secrets_now.sh
# 3. Enter token when prompted
```

## 📚 Available Scripts

- **QUICK_START_SETUP.sh** - Quick interactive setup (recommended)
- **create_token_and_setup.sh** - Detailed interactive setup
- **setup_secrets_now.sh** - Simple token-based setup
- **setup_secrets_with_auth.py** - Python API script
- **setup_secrets_curl.sh** - curl-based alternative

## 🔍 Troubleshooting

### Issue: "Invalid token"

**Solution:**
- Verify token has `repo` scope
- Check if token is expired
- Create a new token if needed

### Issue: "Access forbidden"

**Solution:**
- Verify you have admin access to the repository
- Check token permissions

### Issue: "Connection failed"

**Solution:**
- Check network connectivity
- Verify GitHub API is accessible

### Issue: "Token not found"

**Solution:**
- Verify you copied the token correctly
- Check if token was created successfully
- Create a new token if needed

## ✅ Next Steps After Setup

1. **Verify secrets are set:**
   - Check GitHub Secrets page
   - Verify all secrets are listed

2. **Test GitHub Actions:**
   - Go to Actions tab
   - Trigger a workflow
   - Check logs for successful credential loading

3. **Monitor workflow:**
   - Check workflow runs
   - Verify training completes successfully
   - Check deployment logs

## 📝 Summary

**Status:** ✅ All setup scripts are ready  
**Next Step:** Create Personal Access Token and run setup script  
**Time Required:** ~5 minutes  
**Difficulty:** Easy (fully automated after token creation)

---

**Ready to proceed?** Create your token and run `./QUICK_START_SETUP.sh`!

