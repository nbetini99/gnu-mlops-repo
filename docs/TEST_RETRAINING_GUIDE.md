# Testing Retraining Every 30 Days

This guide provides step-by-step instructions and commands to test the automatic retraining functionality.

---

## 📋 Overview

The retraining system:
- Checks if 30 days have passed since last training
- Trains a new model with latest data
- Compares performance with current production model
- Auto-deploys if new model is better
- Logs all activities

---

## 🧪 Testing Methods

### Method 1: Force Retraining (Recommended for Testing)

**Use this to bypass the 30-day check and test immediately:**

```bash
# Force retraining regardless of schedule
python src/retrain_model.py --force
```

**What it does:**
- Skips the 30-day check
- Immediately trains a new model
- Compares with production
- Deploys if better

---

### Method 2: Test with Modified Interval

**Temporarily change the interval to test the schedule check:**

1. **Edit config.yaml:**
   ```yaml
   retraining:
     enabled: true
     interval_days: 0  # Change from 30 to 0 for immediate retraining
   ```

2. **Run retraining:**
   ```bash
   python src/retrain_model.py
   ```

3. **Restore original interval:**
   ```yaml
   retraining:
     interval_days: 30  # Change back to 30
   ```

---

### Method 3: Simulate 30 Days Passed

**Manually adjust the last training date in MLflow:**

This is more complex and requires direct MLflow database manipulation. Use Method 1 or 2 instead.

---

## 📝 Step-by-Step Testing Guide

### Step 1: Check Current Model Status

```bash
# Check what models are deployed
python src/deploy_model.py --stage info

# Check last training date (if any)
python src/retrain_model.py
# This will show: "Days since last training: X"
```

### Step 2: Run Initial Training (if needed)

```bash
# Train initial model
python src/train_model.py

# Deploy to production
python src/deploy_model.py --stage production
```

### Step 3: Test Retraining with Force Flag

```bash
# Force retraining (bypasses 30-day check)
python src/retrain_model.py --force
```

**Expected output:**
```
✓ Retraining needed: Force mode enabled
Training new model...
✓ Model training completed
Comparing with production model...
✓ New model is better (or worse)
Deployment status: ...
```

### Step 4: Verify Retraining Results

```bash
# Check model versions
python src/deploy_model.py --stage info

# Check retraining logs
ls -lh logs/retraining_*.log
tail -50 logs/retraining_*.log
```

### Step 5: Test Schedule Check (Normal Mode)

```bash
# Run without --force (checks 30-day schedule)
python src/retrain_model.py
```

**If less than 30 days have passed:**
```
✗ Retraining not needed: X days remaining
Status: skipped
```

**If 30+ days have passed:**
```
✓ Retraining needed: X days >= 30 days
Training new model...
```

---

## 🔧 Testing Commands Reference

### Basic Commands

```bash
# Normal retraining (checks schedule)
python src/retrain_model.py

# Force retraining (ignores schedule)
python src/retrain_model.py --force

# Use different config file
python src/retrain_model.py --config config.local.yaml

# Force with custom config
python src/retrain_model.py --force --config config.local.yaml
```

### Verification Commands

```bash
# Check model info
python src/deploy_model.py --stage info

# View retraining logs
ls -lh logs/retraining_*.log
tail -f logs/retraining_*.log

# Check MLflow runs
mlflow ui  # Then open http://localhost:5000
```

### Testing Different Scenarios

```bash
# Test 1: First retraining (no previous model)
python src/retrain_model.py --force

# Test 2: Retraining with better model
python src/retrain_model.py --force

# Test 3: Retraining with worse model (should not deploy)
python src/retrain_model.py --force

# Test 4: Schedule check (should skip if < 30 days)
python src/retrain_model.py
```

---

## 📊 Understanding the Output

### Successful Retraining

```
RETRAINING SUMMARY
======================================================================
Status: completed
New Model Accuracy: 0.4300
Improvement: +0.0000
Deployed: True
Production Version: 7
======================================================================
Log file: logs/retraining_*.log
======================================================================
```

### Skipped Retraining (Too Soon)

```
Days since last training: 5
Retraining interval: 30 days
✗ Retraining not needed: 25 days remaining
Status: skipped
```

### Force Retraining

```
✓ Retraining needed: Force mode enabled
Training new model...
...
Status: completed
```

---

## 🧪 Complete Test Workflow

### Test Scenario 1: Full Retraining Cycle

```bash
# 1. Initial setup
python src/train_model.py
python src/deploy_model.py --stage production

# 2. Force retraining
python src/retrain_model.py --force

# 3. Verify results
python src/deploy_model.py --stage info
cat logs/retraining_*.log | tail -20
```

### Test Scenario 2: Schedule Check

```bash
# 1. Run retraining (will check schedule)
python src/retrain_model.py

# 2. If skipped, note the days remaining
# 3. Force retraining to test functionality
python src/retrain_model.py --force
```

### Test Scenario 3: Multiple Retraining Runs

```bash
# Run multiple retraining cycles
for i in {1..3}; do
  echo "=== Retraining Run $i ==="
  python src/retrain_model.py --force
  sleep 2
done

# Check all results
python src/deploy_model.py --stage info
```

---

## 🔍 Troubleshooting

### Issue: "No previous training found"

**Solution:** Train an initial model first:
```bash
python src/train_model.py
python src/deploy_model.py --stage production
```

### Issue: "Retraining not needed"

**Solution:** Use `--force` flag:
```bash
python src/retrain_model.py --force
```

### Issue: "Model not found in Production"

**Solution:** Deploy a model to production first:
```bash
python src/train_model.py
python src/deploy_model.py --stage production
```

### Issue: Check Logs

```bash
# View latest retraining log
ls -t logs/retraining_*.log | head -1 | xargs cat

# View all retraining logs
ls -lh logs/retraining_*.log

# Follow log in real-time
tail -f logs/retraining_*.log
```

---

## 📅 Testing the 30-Day Schedule

### Quick Test (Change Interval to 0)

1. **Edit `config.yaml`:**
   ```yaml
   retraining:
     interval_days: 0  # Test with 0 days
   ```

2. **Run retraining:**
   ```bash
   python src/retrain_model.py
   ```

3. **Restore original:**
   ```yaml
   retraining:
     interval_days: 30  # Restore to 30 days
   ```

### Test with Custom Interval

```yaml
retraining:
  interval_days: 1  # Test with 1 day interval
```

Then wait 1 day and run:
```bash
python src/retrain_model.py
```

---

## ✅ Verification Checklist

After testing retraining, verify:

- [ ] New model was trained successfully
- [ ] Model metrics were logged to MLflow
- [ ] Comparison with production model completed
- [ ] Deployment status is correct
- [ ] Log file was created in `logs/`
- [ ] Model version incremented in MLflow
- [ ] Production model updated (if new model was better)

---

## 📝 Example Test Session

```bash
# 1. Check current status
python src/deploy_model.py --stage info

# 2. Force retraining
python src/retrain_model.py --force

# 3. Check results
python src/deploy_model.py --stage info

# 4. View logs
tail -50 logs/retraining_*.log

# 5. Test inference with new model
python src/predict.py --input data/test/test_small.csv --output test_pred.csv

# 6. Test schedule check (should skip if < 30 days)
python src/retrain_model.py
```

---

## 🎯 Quick Reference

| Command | Purpose |
|---------|---------|
| `python src/retrain_model.py` | Check schedule and retrain if needed |
| `python src/retrain_model.py --force` | Force immediate retraining |
| `python src/deploy_model.py --stage info` | Check model versions |
| `tail -f logs/retraining_*.log` | View retraining logs |

---

**Last Updated**: November 2025  
**Author**: Narsimha Betini

