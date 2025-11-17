# GitHub Personal Access Token Setup Guide

## 📋 Complete Step-by-Step Instructions with Links

This guide provides detailed instructions for creating a GitHub Personal Access Token and using it to set up your repository secrets.

---

## 🚀 Quick Links

### Direct Links:
- **Create Token:** https://github.com/settings/tokens/new
- **View Tokens:** https://github.com/settings/tokens
- **Repository Secrets:** https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
- **GitHub Actions:** https://github.com/nbetini99/gnu-mlops-repo/actions

---

## 📝 Step 1: Create Personal Access Token

### Step 1.1: Navigate to Token Creation Page

**Direct Link:** https://github.com/settings/tokens/new

**Or navigate manually:**
1. Go to: https://github.com
2. Click on your profile picture (top right)
3. Click **Settings**
4. Scroll down to **Developer settings** (left sidebar)
5. Click **Personal access tokens**
6. Click **Tokens (classic)**
7. Click **Generate new token**
8. Click **Generate new token (classic)**

### Step 1.2: Fill in the Token Form

1. **Note:** Enter a descriptive name
   - Example: `GNU MLOps Secrets Setup`
   - This helps you identify the token later

2. **Expiration:** Select expiration period
   - Options: `30 days`, `60 days`, `90 days`, `No expiration`
   - Recommended: `90 days` (you can extend later)

3. **Select scopes:** Check the required scope
   - ✅ **repo** (Full control of private repositories)
     - This is required for setting up repository secrets
     - This gives full access to private repositories
   
   **What each scope does:**
   - `repo`: Full control of private repositories
   - `workflow`: Update GitHub Action workflows
   - `admin:repo_hook`: Full control of repository hooks
   - `write:packages`: Upload packages to GitHub Package Registry

   **⚠️ IMPORTANT:** You need at least the `repo` scope to set up secrets.

### Step 1.3: Generate Token

1. Scroll down to the bottom of the page
2. Click **Generate token** (green button)
3. **⚠️ IMPORTANT:** Copy the token immediately!
   - You will see a page with your new token
   - The token will look like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **You won't be able to see this token again!**
   - Copy it to a secure location (password manager, text file, etc.)

### Step 1.4: Save Token Securely

**⚠️ SECURITY WARNING:**
- Never share your token with anyone
- Never commit your token to a repository
- Store it securely (password manager recommended)
- If you lose it, you'll need to create a new one

---

## 🔧 Step 2: Use Token to Set Up Secrets

### Option 1: Automated Setup (Recommended)

#### Step 2.1: Run Setup Script

```bash
# Navigate to your repository
cd /Users/narsimhabetini/gnu-mlops-repo

# Run the quick start setup script
./QUICK_START_SETUP.sh
```

#### Step 2.2: Enter Token

When prompted, enter your Personal Access Token:

```bash
Enter your GitHub Personal Access Token: [paste your token here]
```

#### Step 2.3: Wait for Setup

The script will:
1. ✅ Validate your token
2. ✅ Get repository public key
3. ✅ Encrypt each secret
4. ✅ Set up all 4 secrets automatically
5. ✅ Verify the setup

**Expected output:**
```
✓ Got public key: abc12345...
Setting DATABRICKS_HOST... ✓ Success
Setting DATABRICKS_TOKEN... ✓ Success
Setting DATABRICKS_WORKSPACE_PATH... ✓ Success
Setting DATABRICKS_EXPERIMENT_PATH... ✓ Success

✅ All required secrets set successfully!
```

### Option 2: Manual Setup

If you prefer to set secrets manually:

#### Step 2.1: Navigate to Secrets Page

**Direct Link:** https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions

**Or navigate manually:**
1. Go to: https://github.com/nbetini99/gnu-mlops-repo
2. Click **Settings** (top menu bar)
3. Click **Secrets and variables** → **Actions** (left sidebar)

#### Step 2.2: Add Each Secret

Click **New repository secret** for each secret:

**Secret 1: DATABRICKS_HOST**
- **Name:** `DATABRICKS_HOST`
- **Value:** `https://dbc-5e289a33-a706.cloud.databricks.com`
- Click **Add secret**

**Secret 2: DATABRICKS_TOKEN**
- **Name:** `DATABRICKS_TOKEN`
- **Value:** `dapicb7282387c50cc9aa3e8e3d18378b5fd`
- Click **Add secret**

**Secret 3: DATABRICKS_WORKSPACE_PATH** (Optional)
- **Name:** `DATABRICKS_WORKSPACE_PATH`
- **Value:** `/Users/nbatink@gmail.com/gnu-mlops/liveprod`
- Click **Add secret**

**Secret 4: DATABRICKS_EXPERIMENT_PATH** (Optional)
- **Name:** `DATABRICKS_EXPERIMENT_PATH`
- **Value:** `/Users/nbatink@gmail.com/gnu-mlops/experiments`
- Click **Add secret**

### Option 3: Using Environment Variable

#### Step 2.1: Set Environment Variable

```bash
# Export your token as an environment variable
export GITHUB_TOKEN=ghp_your_token_here

# Verify it's set
echo $GITHUB_TOKEN
```

#### Step 2.2: Run Setup Script

```bash
# Activate virtual environment
source venv/bin/activate

# Run setup script with token
python3 setup_secrets_with_auth.py --token $GITHUB_TOKEN --username nbetini99
```

---

## ✅ Step 3: Verify Setup

### Step 3.1: Check Secrets Page

**Direct Link:** https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions

1. Go to the secrets page
2. Verify all secrets are listed:
   - ✅ DATABRICKS_HOST
   - ✅ DATABRICKS_TOKEN
   - ✅ DATABRICKS_WORKSPACE_PATH (optional)
   - ✅ DATABRICKS_EXPERIMENT_PATH (optional)

**Note:** You won't be able to see the secret values (for security reasons).

### Step 3.2: Test GitHub Actions Workflow

**Direct Link:** https://github.com/nbetini99/gnu-mlops-repo/actions

1. Go to the Actions tab
2. Trigger a workflow:
   - Push a commit, OR
   - Click **Run workflow** manually
3. Check workflow logs:
   - Look for: `✓ Databricks credentials found in GitHub Secrets`
   - Look for: `✓ Environment configured for Databricks`
   - Look for: `✓ Databricks credentials loaded from GitHub Secrets`

### Step 3.3: Verify Workflow Success

If secrets are set correctly, you should see:
- ✅ Workflow completes successfully
- ✅ Training runs without errors
- ✅ Model is registered in MLflow
- ✅ Deployment to staging works (if configured)

---

## 🔍 Troubleshooting

### Issue: "Invalid token"

**Symptoms:**
- Error: `401 Unauthorized`
- Error: `Invalid GitHub token`

**Solutions:**
1. **Verify token is correct:**
   - Check if you copied the token correctly
   - Make sure there are no extra spaces or characters

2. **Check token expiration:**
   - Go to: https://github.com/settings/tokens
   - Check if your token is still valid
   - Create a new token if expired

3. **Verify token scope:**
   - Make sure token has `repo` scope
   - Create a new token with correct scope

### Issue: "Access forbidden"

**Symptoms:**
- Error: `403 Forbidden`
- Error: `Access forbidden`

**Solutions:**
1. **Check repository access:**
   - Verify you have admin access to the repository
   - Check if you're a collaborator on the repository

2. **Verify token permissions:**
   - Make sure token has `repo` scope
   - Check if token has necessary permissions

3. **Check repository settings:**
   - Verify repository allows Actions
   - Check if repository is private (tokens work for private repos)

### Issue: "Connection failed"

**Symptoms:**
- Error: `Connection failed`
- Error: `Network error`

**Solutions:**
1. **Check network connectivity:**
   - Verify internet connection
   - Check if GitHub API is accessible

2. **Verify GitHub API status:**
   - Check: https://www.githubstatus.com
   - Verify GitHub API is operational

3. **Check firewall/proxy:**
   - Verify firewall allows GitHub API access
   - Check if proxy is blocking requests

### Issue: "Token not found"

**Symptoms:**
- Error: `Token not found`
- Error: `Invalid token`

**Solutions:**
1. **Recreate token:**
   - Go to: https://github.com/settings/tokens/new
   - Create a new token
   - Make sure to copy it immediately

2. **Verify token format:**
   - Token should start with `ghp_`
   - Token should be 40+ characters long

3. **Check token storage:**
   - Verify token is stored securely
   - Make sure token wasn't accidentally deleted

---

## 📚 Additional Resources

### GitHub Documentation:
- **Personal Access Tokens:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- **Repository Secrets:** https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **GitHub API:** https://docs.github.com/en/rest

### Useful Links:
- **Token Management:** https://github.com/settings/tokens
- **Repository Settings:** https://github.com/nbetini99/gnu-mlops-repo/settings
- **Actions Secrets:** https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
- **GitHub Status:** https://www.githubstatus.com

---

## 🔒 Security Best Practices

### ✅ DO:
1. **Use Personal Access Tokens** instead of passwords
2. **Store tokens securely** (password manager recommended)
3. **Use minimal scopes** (only grant necessary permissions)
4. **Rotate tokens regularly** (every 90 days recommended)
5. **Revoke unused tokens** (delete old tokens)

### ❌ DON'T:
1. **Don't share tokens** with anyone
2. **Don't commit tokens** to repositories
3. **Don't use tokens** in public places
4. **Don't use expired tokens**
5. **Don't use tokens** with excessive permissions

---

## 📋 Quick Reference

### Token Creation:
- **Link:** https://github.com/settings/tokens/new
- **Scope:** `repo` (Full control)
- **Expiration:** `90 days` (recommended)

### Secrets Setup:
- **Automated:** `./QUICK_START_SETUP.sh`
- **Manual:** https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
- **Environment Variable:** `export GITHUB_TOKEN=your_token_here`

### Verification:
- **Secrets Page:** https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
- **Actions:** https://github.com/nbetini99/gnu-mlops-repo/actions

### Secrets to Set:
- `DATABRICKS_HOST`: `https://dbc-5e289a33-a706.cloud.databricks.com`
- `DATABRICKS_TOKEN`: `dapicb7282387c50cc9aa3e8e3d18378b5fd`
- `DATABRICKS_WORKSPACE_PATH`: `/Users/nbatink@gmail.com/gnu-mlops/liveprod` (optional)
- `DATABRICKS_EXPERIMENT_PATH`: `/Users/nbatink@gmail.com/gnu-mlops/experiments` (optional)

---

## 🎯 Summary

### Step 1: Create Token (2 minutes)
1. Go to: https://github.com/settings/tokens/new
2. Fill in: Note, Expiration, Scope (`repo`)
3. Click: Generate token
4. Copy: Token immediately

### Step 2: Set Up Secrets (1 minute)
1. Run: `./QUICK_START_SETUP.sh`
2. Enter: Your token when prompted
3. Wait: Script sets up all secrets automatically

### Step 3: Verify Setup (1 minute)
1. Check: Secrets page
2. Test: GitHub Actions workflow
3. Verify: Logs show successful credential loading

**Total Time:** ~5 minutes  
**Difficulty:** Easy  
**Status:** Fully automated after token creation

---

**Ready to proceed?** Follow the steps above to create your token and set up secrets!

