# Quick Start Guide

Get up and running with GNU MLOps in 5 minutes!

## Prerequisites

- Python 3.8+
- Databricks account
- Git

## Step 1: Clone and Install (2 minutes)

```bash
# Clone repository
git clone https://github.com/nbetini99/gnu-mlops-repo.git
cd gnu-mlops-repo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure (1 minute)

Create `.env` file:
```bash
DATABRICKS_HOST=https://diba-5e288a33-e706.cloud.databricks.com
DATABRICKS_TOKEN=your_token_here
MLFLOW_TRACKING_URI=databricks
```

Edit `config.yaml`:
- Update `token` with your Databricks token
- Adjust `workspace_path` if needed
- Customize model hyperparameters (optional)

## Step 3: Train Your First Model (1 minute)

```bash
python src/train_model.py
```

You should see:
```
Training Completed Successfully!
Run ID: abc123...
Accuracy: 0.8542
F1 Score: 0.8398
```

## Step 4: Deploy to Staging (30 seconds)

```bash
python src/deploy_model.py --stage staging
```

## Step 5: Deploy to Production (30 seconds)

```bash
python src/deploy_model.py --stage production
```

## Success! 🎉

Your ML model is now deployed to production!

## Next Steps

- Make predictions: `python src/predict.py --input data.csv`
- View in MLflow: Visit your Databricks workspace
- Set up CI/CD: Configure GitHub Actions
- Customize model: Edit `config.yaml`

## Using Makefile (Bonus)

```bash
make train              # Train model
make deploy-staging     # Deploy to staging
make deploy-production  # Deploy to production
make info              # Check current model
```

## Need Help?

- Read the full [README.md](README.md)
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guide
- Contact: nbetini@gmail.com

---

**That's it! You're now running a production MLOps pipeline! 🚀**

