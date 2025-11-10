# Testing Guide for GNU MLOps

This guide shows you how to test the MLOps framework at different levels.

## 🧪 Testing Levels

1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test with sample data (no Databricks needed)
3. **End-to-End Tests** - Full pipeline test with Databricks
4. **Quick Validation** - Verify setup and configuration

---

## 1️⃣ Unit Tests (No Databricks Required)

### Run All Tests

```bash
# Make sure you're in the project directory
cd gnu-mlops-repo

# Install test dependencies (if not already installed)
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=html
```

### Run Specific Tests

```bash
# Test training module only
pytest tests/test_train_model.py -v

# Test deployment module only
pytest tests/test_deploy_model.py -v

# Run a specific test function
pytest tests/test_train_model.py::TestMLModelTrainer::test_train_model -v
```

### Expected Output

```
tests/test_train_model.py::TestMLModelTrainer::test_generate_sample_data PASSED
tests/test_train_model.py::TestMLModelTrainer::test_preprocess_data PASSED
tests/test_train_model.py::TestMLModelTrainer::test_train_model PASSED
tests/test_train_model.py::TestMLModelTrainer::test_evaluate_model PASSED
tests/test_deploy_model.py::TestModelDeployment::test_validate_model_performance PASSED
tests/test_deploy_model.py::TestModelDeployment::test_get_model_metrics PASSED

================== 6 passed in 5.32s ==================
```

---

## 2️⃣ Integration Test (Local - No Databricks)

### Test Training Pipeline Locally

The training script can run locally with sample data:

```bash
# Set environment to use local MLflow (not Databricks)
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db

# Run training with sample data
python3 src/train_model.py
```

This will:
- Generate sample data automatically
- Train a model locally
- Log to local MLflow (sqlite database)
- Save model artifacts

### View Local MLflow UI

```bash
# Start MLflow UI
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Open browser to: http://localhost:5000
```

You should see:
- Experiment runs
- Metrics (accuracy, F1 score, etc.)
- Model parameters
- Artifacts

---

## 3️⃣ End-to-End Test (With Databricks)

### Prerequisites

1. **Set up environment variables:**

```bash
# Create .env file
cat > .env << EOF
DATABRICKS_HOST=https://diba-5e288a33-e706.cloud.databricks.com
DATABRICKS_TOKEN=your_actual_token_here
MLFLOW_TRACKING_URI=databricks
EOF
```

2. **Or export variables:**

```bash
export DATABRICKS_HOST="https://diba-5e288a33-e706.cloud.databricks.com"
export DATABRICKS_TOKEN="your_token"
export MLFLOW_TRACKING_URI="databricks"
```

### Test Complete Pipeline

```bash
# 1. Test training
echo "Step 1: Training model..."
python3 src/train_model.py

# 2. Test staging deployment
echo "Step 2: Deploying to staging..."
python3 src/deploy_model.py --stage staging

# 3. Test production deployment
echo "Step 3: Deploying to production..."
python3 src/deploy_model.py --stage production

# 4. Check deployment info
echo "Step 4: Checking production model..."
python3 src/deploy_model.py --stage info

# 5. Test predictions (if you have test data)
# python3 src/predict.py --input test_data.csv --output predictions.csv
```

### Using Make Commands

```bash
# Test training
make train

# Test staging deployment
make deploy-staging

# Test production deployment
make deploy-production

# Check model info
make info
```

---

## 4️⃣ Quick Validation Tests

### Test 1: Verify Configuration

```bash
# Check if config file is valid
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

Expected: Should print configuration without errors

### Test 2: Verify Dependencies

```bash
# Check if all required packages are importable
python3 << EOF
import numpy
import pandas
import sklearn
import mlflow
print("✓ All core dependencies available")
EOF
```

### Test 3: Verify Databricks Connection

```bash
python3 << EOF
import os
from databricks import sql

host = os.getenv('DATABRICKS_HOST')
token = os.getenv('DATABRICKS_TOKEN')

if host and token:
    print(f"✓ Databricks credentials configured")
    print(f"  Host: {host}")
else:
    print("✗ Missing Databricks credentials")
EOF
```

### Test 4: Verify MLflow Connection

```bash
python3 << EOF
import mlflow
mlflow.set_tracking_uri("databricks")
print("✓ MLflow tracking URI set")
EOF
```

### Test 5: Check File Structure

```bash
# Verify all required files exist
for file in config.yaml requirements.txt setup.py src/train_model.py src/deploy_model.py src/predict.py; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file missing"
    fi
done
```

---

## 5️⃣ Interactive Testing (Python REPL)

### Test Training Components

```python
# Start Python
python3

# Import and test
from src.train_model import MLModelTrainer

# Initialize trainer
trainer = MLModelTrainer()

# Generate sample data
df = trainer._generate_sample_data(n_samples=100)
print(f"Data shape: {df.shape}")

# Preprocess
X_train, X_test, y_train, y_test, scaler = trainer.preprocess_data(df)
print(f"Training samples: {X_train.shape[0]}")
print(f"Test samples: {X_test.shape[0]}")

# Train model
model, cv_scores = trainer.train_model(X_train, y_train)
print(f"CV scores: {cv_scores}")
print(f"Mean accuracy: {cv_scores.mean():.4f}")

# Evaluate
metrics = trainer.evaluate_model(model, X_test, y_test)
print(f"Test accuracy: {metrics['accuracy']:.4f}")
```

### Test Deployment Components

```python
from src.deploy_model import ModelDeployment

deployer = ModelDeployment()

# Test validation
metrics = {'accuracy': 0.85, 'f1_score': 0.82}
is_valid = deployer.validate_model_performance(metrics, threshold=0.8)
print(f"Model validation (85% accuracy): {is_valid}")

# Get production model info (if exists)
info = deployer.get_production_model_info()
print(f"Production model: {info}")
```

### Test Prediction

```python
from src.predict import ModelPredictor
import pandas as pd

# This requires a trained and deployed model
predictor = ModelPredictor(stage='Production')

# Test prediction with sample data
sample_data = {
    'feature1': [0.5, 1.2, -0.3],
    'feature2': [1.1, 0.8, 1.5],
    'feature3': [-0.2, 0.9, 0.1]
}
df = pd.DataFrame(sample_data)

predictions = predictor.predict(df)
print(f"Predictions: {predictions}")
```

---

## 6️⃣ Testing with Docker (Advanced)

### Create Test Environment

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "src/train_model.py"]
EOF

# Build image
docker build -t gnu-mlops-test .

# Run tests in container
docker run --env-file .env gnu-mlops-test
```

---

## 🔍 Troubleshooting Tests

### Issue: Import Errors

```bash
# Solution: Install in development mode
pip install -e .
```

### Issue: MLflow Connection Fails

```bash
# Check MLflow tracking URI
python3 -c "import mlflow; print(mlflow.get_tracking_uri())"

# Reset to local for testing
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db
```

### Issue: Databricks Authentication Fails

```bash
# Verify token is set
echo $DATABRICKS_TOKEN | head -c 20

# Test connection
databricks workspace ls /Users/
```

### Issue: Module Not Found

```bash
# Ensure you're in the right directory
pwd  # Should end with gnu-mlops-repo

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 📊 Test Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals

- **Unit Tests**: Target 80%+ coverage
- **Integration Tests**: Test critical paths
- **E2E Tests**: Verify complete workflow

---

## ✅ Test Checklist

Before considering the system tested:

- [ ] All unit tests pass
- [ ] Training runs successfully locally
- [ ] Training runs successfully on Databricks
- [ ] Staging deployment works
- [ ] Production deployment works
- [ ] Predictions are generated correctly
- [ ] MLflow tracking works
- [ ] Model registry is updated
- [ ] Rollback works
- [ ] CI/CD pipeline runs (if using GitHub)

---

## 🎯 Quick Test Commands

```bash
# Full local test suite
make test

# Quick validation
python3 -m pytest tests/ -v

# Integration test (local)
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db
python3 src/train_model.py

# E2E test (Databricks)
export MLFLOW_TRACKING_URI=databricks
python3 src/train_model.py
python3 src/deploy_model.py --stage staging
python3 src/deploy_model.py --stage production
```

---

## 📞 Need Help?

If tests fail:
1. Check error messages in output
2. Review logs
3. Verify configuration in `config.yaml`
4. Check environment variables
5. Ensure Databricks credentials are correct

For support: nbetini@gmail.com

