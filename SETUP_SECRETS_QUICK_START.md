# Quick Start: Set Up GitHub Secrets

## Option 1: Manual Setup (Recommended - No Tools Required)

### Step 1: Open Secrets Page

**Direct Link:**
https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions

Or navigate manually:
1. Go to: https://github.com/nbetini99/gnu-mlops-repo
2. Click: **Settings** → **Secrets and variables** → **Actions**

### Step 2: Add Required Secrets

Click **"New repository secret"** and add:

#### 1. DATABRICKS_HOST
- **Name:** `DATABRICKS_HOST`
- **Value:** `https://dbc-5e289a33-a706.cloud.databricks.com`

#### 2. DATABRICKS_TOKEN
- **Name:** `DATABRICKS_TOKEN`
- **Value:** `dapicb7282387c50cc9aa3e8e3d18378b5fd`

### Step 3: Add Optional Secrets

#### 3. DATABRICKS_WORKSPACE_PATH
- **Name:** `DATABRICKS_WORKSPACE_PATH`
- **Value:** `/Users/nbatink@gmail.com/gnu-mlops/liveprod`

#### 4. DATABRICKS_EXPERIMENT_PATH
- **Name:** `DATABRICKS_EXPERIMENT_PATH`
- **Value:** `/Users/nbatink@gmail.com/gnu-mlops/experiments`

### Step 4: Verify

After adding all secrets, verify they're listed on the secrets page.

### Step 5: Test

1. Go to **Actions** tab
2. Trigger a workflow
3. Check logs for: `✓ Databricks credentials found in GitHub Secrets`

---

## Option 2: Automated Setup (Using Script)

### Prerequisites

```bash
# Install required Python packages
pip install requests pynacl
```

### Get GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click: **Generate new token (classic)**
3. Select scopes: **repo** (full control)
4. Click: **Generate token**
5. Copy the token

### Run Setup Script

```bash
# Option 1: Use environment variable
export GITHUB_TOKEN=your_github_token_here
python3 setup_github_secrets.py

# Option 2: Use command line argument
python3 setup_github_secrets.py --token your_github_token_here

# Option 3: Dry run (see what would be set)
python3 setup_github_secrets.py --token your_github_token_here --dry-run
```

---

## Option 3: Using Setup Script (Interactive)

Run the interactive setup script:

```bash
./SETUP_GITHUB_SECRETS.sh
```

This will display step-by-step instructions.

---

## Verification

After setting up secrets, verify by:

1. **Check Secrets Page:**
   - Go to: https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions
   - Verify all secrets are listed

2. **Test Workflow:**
   - Go to: https://github.com/nbetini99/gnu-mlops-repo/actions
   - Trigger a workflow
   - Check logs for successful credential loading

3. **Check Logs:**
   - Look for: `✓ Databricks credentials found in GitHub Secrets`
   - Look for: `✓ Environment configured for Databricks`

---

## Troubleshooting

### Issue: "Secrets not found"

**Solution:**
- Verify secrets are added correctly
- Check secret names match exactly (case-sensitive)
- Ensure you're looking at the right repository

### Issue: "Authentication failed"

**Solution:**
- Verify DATABRICKS_TOKEN is correct
- Check if token is expired
- Generate a new token if needed

### Issue: "Connection failed"

**Solution:**
- Verify DATABRICKS_HOST is correct
- Check network connectivity
- Verify Databricks workspace is accessible

---

## Quick Reference

| Secret Name | Value | Required |
|------------|-------|----------|
| `DATABRICKS_HOST` | `https://dbc-5e289a33-a706.cloud.databricks.com` | Yes |
| `DATABRICKS_TOKEN` | `dapicb7282387c50cc9aa3e8e3d18378b5fd` | Yes |
| `DATABRICKS_WORKSPACE_PATH` | `/Users/nbatink@gmail.com/gnu-mlops/liveprod` | No |
| `DATABRICKS_EXPERIMENT_PATH` | `/Users/nbatink@gmail.com/gnu-mlops/experiments` | No |

---

## Security Notes

✅ **Secrets are encrypted** by GitHub
✅ **Never exposed** in logs or code
✅ **Only accessible** to repository administrators
✅ **Automatically masked** in workflow logs

---

## Next Steps

After setting up secrets:

1. ✅ Verify secrets are set correctly
2. ✅ Test GitHub Actions workflow
3. ✅ Check workflow logs
4. ✅ Deploy to staging/production

---

**For detailed instructions, see:** `GITHUB_SECRETS_SETUP_INSTRUCTIONS.md`

