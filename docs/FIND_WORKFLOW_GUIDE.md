# How to Find and Trigger Your GitHub Actions Workflow

## 🔍 Issue: Workflow Not Visible

If you don't see the workflow in GitHub Actions, here's how to find and trigger it:

---

## 📋 Method 1: Find by Workflow Name

The workflow is named: **"MLOps Training and Deployment Pipeline"**

### Steps:

1. **Go to Actions Tab:**
   ```
   https://github.com/nbetini99/gnu-mlops-repo/actions
   ```

2. **Look for the workflow name:**
   - The workflow name appears in the left sidebar
   - Look for: **"MLOps Training and Deployment Pipeline"**
   - It may be collapsed or at the bottom of the list

3. **If you see it:**
   - Click on **"MLOps Training and Deployment Pipeline"**
   - Click **"Run workflow"** button (top right)
   - Select branch: **main**
   - Click **"Run workflow"**

---

## 🚀 Method 2: Trigger It First (Recommended)

**GitHub Actions only shows workflows after they've run at least once.**

### Quick Trigger (Automatic):

```bash
cd /Users/narsimhabetini/gnu-mlops-repo

# Make a small change to trigger the workflow
echo "" >> README.md
git add README.md
git commit -m "Trigger GitHub Actions workflow"
git push origin main
```

**What happens:**
1. Push triggers the workflow automatically (because of `push: branches: [main]`)
2. Go to Actions tab: https://github.com/nbetini99/gnu-mlops-repo/actions
3. You'll see the workflow running
4. After it completes, the workflow will appear in the sidebar for manual triggers

---

## 🔎 Method 3: Find by Workflow File

The workflow file is: `.github/workflows/train-and-deploy.yml`

### Steps:

1. **Go to your repository:**
   ```
   https://github.com/nbetini99/gnu-mlops-repo
   ```

2. **Navigate to the workflow file:**
   - Click on `.github` folder
   - Click on `workflows` folder
   - Click on `train-and-deploy.yml`

3. **From the file view:**
   - Look for a button that says **"Actions"** or **"View workflow"**
   - Or go directly to: https://github.com/nbetini99/gnu-mlops-repo/actions/workflows/train-and-deploy.yml

4. **On the workflow page:**
   - You'll see all runs of this workflow
   - Click **"Run workflow"** button (top right)
   - Select branch: **main**
   - Click **"Run workflow"**

---

## 📍 Direct Links

### Workflow Runs Page:
```
https://github.com/nbetini99/gnu-mlops-repo/actions/workflows/train-and-deploy.yml
```

### All Actions:
```
https://github.com/nbetini99/gnu-mlops-repo/actions
```

### Workflow File:
```
https://github.com/nbetini99/gnu-mlops-repo/blob/main/.github/workflows/train-and-deploy.yml
```

---

## 🎯 Step-by-Step: First Time Setup

### If the workflow has NEVER run:

1. **Trigger it automatically:**
   ```bash
   cd /Users/narsimhabetini/gnu-mlops-repo
   git commit --allow-empty -m "Trigger GitHub Actions workflow"
   git push origin main
   ```

2. **Wait 10-20 seconds**

3. **Go to Actions:**
   ```
   https://github.com/nbetini99/gnu-mlops-repo/actions
   ```

4. **You should now see:**
   - A workflow run in progress
   - Workflow name: "MLOps Training and Deployment Pipeline"
   - Status: Yellow circle (running)

5. **After it completes:**
   - The workflow will appear in the left sidebar
   - You can click "Run workflow" for future manual triggers

---

## 🔍 Visual Guide: Where to Look

### In GitHub Actions Page:

```
┌─────────────────────────────────────────────────┐
│  Actions  │  Code  │  Issues  │  Pull requests  │
├─────────────────────────────────────────────────┤
│                                                   │
│  All workflows                                    │
│  ┌─────────────────────────────────────────┐   │
│  │ MLOps Training and Deployment Pipeline  │ ← Look here
│  └─────────────────────────────────────────┘   │
│                                                   │
│  [Run workflow] ← Button at top right            │
│                                                   │
└─────────────────────────────────────────────────┘
```

### If You Don't See It:

1. **Check the left sidebar** - workflows are listed there
2. **Scroll down** - it might be below other workflows
3. **Check "All workflows"** section
4. **Use the search box** - type "MLOps" or "train"

---

## ✅ Verification Checklist

Before troubleshooting, verify:

- [ ] Workflow file exists: `.github/workflows/train-and-deploy.yml`
- [ ] File is committed to repository
- [ ] File is pushed to GitHub
- [ ] You're looking at the correct repository: `nbetini99/gnu-mlops-repo`
- [ ] You're on the `main` branch

**Check if file is on GitHub:**
```
https://github.com/nbetini99/gnu-mlops-repo/tree/main/.github/workflows
```

You should see `train-and-deploy.yml` listed there.

---

## 🛠️ Troubleshooting

### Issue 1: Workflow file not found on GitHub

**Solution:**
```bash
# Make sure file is committed and pushed
cd /Users/narsimhabetini/gnu-mlops-repo
git add .github/workflows/train-and-deploy.yml
git commit -m "Add workflow file"
git push origin main
```

### Issue 2: Workflow appears but can't run manually

**Check:**
- The workflow has `workflow_dispatch:` in the YAML (it does)
- You're on the correct branch (main)
- You have write access to the repository

### Issue 3: Workflow runs but fails immediately

**Check:**
- Workflow file syntax is correct
- All required files exist (requirements.txt, src/train_model.py, etc.)

---

## 🚀 Quick Commands Summary

### Trigger Workflow (Automatic):
```bash
cd /Users/narsimhabetini/gnu-mlops-repo
git commit --allow-empty -m "Trigger workflow"
git push origin main
```

### View Workflow:
```
https://github.com/nbetini99/gnu-mlops-repo/actions/workflows/train-and-deploy.yml
```

### Direct Workflow Link:
```
https://github.com/nbetini99/gnu-mlops-repo/actions/workflows/train-and-deploy.yml
```

---

## 📝 What the Workflow Does

Once triggered, the workflow will:

1. ✅ Checkout your code
2. ✅ Set up Python 3.9
3. ✅ Install dependencies
4. ✅ Check Databricks credentials
5. ✅ Train the model
6. ✅ Deploy to staging
7. ✅ Deploy to production (if conditions met)

**Total time:** ~15 minutes

---

## 🎯 Recommended Approach

**For first-time setup:**

1. **Trigger automatically** (push to main):
   ```bash
   git commit --allow-empty -m "Trigger GitHub Actions"
   git push origin main
   ```

2. **Go to Actions tab** and watch it run

3. **After it completes**, the workflow will be visible for manual triggers

4. **Future runs:** Use "Run workflow" button

---

**Last Updated:** November 2025  
**Repository:** https://github.com/nbetini99/gnu-mlops-repo

