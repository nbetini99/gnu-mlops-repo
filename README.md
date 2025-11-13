# GNU MLOps - Machine Learning Operations Framework

A comprehensive MLOps framework for training, deploying, and managing machine learning models using Databricks and MLflow.

![MLOps Pipeline](https://img.shields.io/badge/MLOps-Pipeline-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Databricks](https://img.shields.io/badge/Databricks-Ready-orange)
![MLflow](https://img.shields.io/badge/MLflow-Integrated-red)

## 🚀 Features

- **Automated Training Pipeline**: Complete ML training workflow with MLflow experiment tracking
- **Model Registry**: Automated model versioning and registration
- **Deployment Automation**: One-command deployment to Staging/Production
- **Performance Monitoring**: Track model metrics and performance
- **Rollback Support**: Quick rollback to previous model versions
- **CI/CD Integration**: GitHub Actions workflow for automated training and deployment
- **Databricks Integration**: Seamless integration with Databricks workspace

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Training Models](#training-models)
- [Deploying Models](#deploying-models)
- [Making Predictions](#making-predictions)
- [Project Structure](#project-structure)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

- Python 3.8 or higher
- Databricks workspace account
- Databricks access token
- Git

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/nbetini99/gnu-mlops-repo.git
cd gnu-mlops-repo
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Package (Optional)

```bash
pip install -e .
```

## ⚙️ Configuration

### 1. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
DATABRICKS_HOST=https://diba-5e288a33-e706.cloud.databricks.com
DATABRICKS_TOKEN=your_databricks_access_token_here
MLFLOW_TRACKING_URI=databricks
```

### 2. Configure Project Settings

Edit `config.yaml` to customize your project:

```yaml
databricks:
  host: "https://diba-5e288a33-e706.cloud.databricks.com"
  token: "YOUR_TOKEN"  # Or use environment variable
  workspace_path: "/Users/nbetini@gmail.com/gnu-mlops/liveprod"

mlflow:
  gnu_mlflow_config: "/Users/nbetini@gmail.com/gnu-mlops/experiments"
  model_name: "gnu-mlops-model"

model:
  algorithm: "random_forest"
  hyperparameters:
    n_estimators: 100
    max_depth: 10
```

### 3. Set Up Databricks Workspace

```bash
chmod +x scripts/setup_databricks.sh
./scripts/setup_databricks.sh
```

## 🎯 Quick Start

### Train Your First Model

```bash
# Option 1: Direct Python execution
python src/train_model.py

# Option 2: Using the training script
chmod +x scripts/run_training.sh
./scripts/run_training.sh
```

### Deploy to Staging

```bash
python src/deploy_model.py --stage staging
```

### Deploy to Production

```bash
python src/deploy_model.py --stage production
```

## 🏋️ Training Models

### Basic Training

The training pipeline includes:
- Data loading from Databricks
- Data preprocessing and feature scaling
- Cross-validation
- Model training with configurable hyperparameters
- Automatic MLflow experiment tracking
- Model registration

```python
from src.train_model import MLModelTrainer

trainer = MLModelTrainer()
run_id, metrics = trainer.run_training_pipeline()
print(f"Model trained with accuracy: {metrics['accuracy']:.4f}")
```

### Custom Training Configuration

Modify `config.yaml` to customize:
- Algorithm selection (Random Forest, XGBoost, LightGBM)
- Hyperparameters
- Train/test split ratios
- Cross-validation folds
- Feature selection

### Monitor Training

Access MLflow UI to monitor experiments:
```bash
mlflow ui
# Or visit Databricks workspace: https://diba-5e288a33-e706.cloud.databricks.com
```

## 🚢 Deploying Models

### Deployment Stages

1. **Staging**: For testing and validation
2. **Production**: For live serving

### Deploy to Staging

```bash
python src/deploy_model.py --stage staging
```

This will:
- Get the latest model version
- Validate performance (threshold: 70% accuracy)
- Transition to Staging stage
- Add deployment metadata

### Deploy to Production

```bash
python src/deploy_model.py --stage production
```

This will:
- Get the current Staging model
- Validate performance (threshold: 80% accuracy)
- Transition to Production stage
- Archive previous production versions

### Deploy Specific Version

```bash
python src/deploy_model.py --stage production --version 3
```

### Check Production Model

```bash
python src/deploy_model.py --stage info
```

### Rollback Production

```bash
# Rollback to previous version
python src/deploy_model.py --stage rollback

# Rollback to specific version
python src/deploy_model.py --stage rollback --version 2
```

## 🔮 Making Predictions

### Batch Predictions

```bash
python src/predict.py --input data/test_data.csv --output predictions.csv --stage Production
```

### Python API

```python
from src.predict import ModelPredictor

# Load production model
predictor = ModelPredictor(stage='Production')

# Single prediction
data = {'feature1': 0.5, 'feature2': 1.2, 'feature3': -0.3}
prediction = predictor.predict(data)

# Batch predictions
import pandas as pd
df = pd.read_csv('test_data.csv')
predictions = predictor.predict(df)
```

## 📁 Project Structure

```
gnu-mlops-repo/
├── src/
│   ├── __init__.py
│   ├── train_model.py          # Training pipeline
│   ├── deploy_model.py         # Deployment automation
│   └── predict.py              # Prediction service
├── scripts/
│   ├── setup_databricks.sh     # Databricks setup
│   ├── run_training.sh         # Training script
│   └── deploy.sh               # Deployment script
├── .github/
│   └── workflows/
│       └── train-and-deploy.yml # CI/CD pipeline
├── config.yaml                  # Configuration file
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── .gitignore
└── README.md
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The project includes an automated CI/CD pipeline that:

1. **On Push to Main**:
   - Runs tests
   - Trains new model
   - Deploys to Staging automatically

2. **Manual Production Deployment**:
   - Go to Actions → MLOps Training and Deployment Pipeline
   - Click "Run workflow"
   - Select "Deploy to production: true"

3. **Deploy with Commit Message**:
   ```bash
   git commit -m "Update model [deploy-prod]"
   git push origin main
   ```

### Setup GitHub Secrets

Add these secrets in GitHub repository settings:
- `DATABRICKS_HOST`: Your Databricks workspace URL
- `DATABRICKS_TOKEN`: Your Databricks access token

## 🔍 Monitoring and Logging

### View Experiment Runs

```python
import mlflow
mlflow.set_tracking_uri("databricks")
experiments = mlflow.search_experiments()
```

### Check Model Metrics

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()
runs = client.search_runs(experiment_ids=["1"])
for run in runs:
    print(f"Run ID: {run.info.run_id}")
    print(f"Metrics: {run.data.metrics}")
```

## 🛠️ Troubleshooting

### Common Issues

**1. Authentication Error**
```
Error: Databricks authentication failed
```
Solution: Check your `.env` file and ensure `DATABRICKS_TOKEN` is set correctly.

**2. Model Not Found**
```
Error: No model versions found
```
Solution: Run training first: `python src/train_model.py`

**3. Deployment Threshold Not Met**
```
Warning: Model did not meet production threshold
```
Solution: Improve model performance or lower threshold in `src/deploy_model.py`

### Getting Help

- Check logs: Models generate detailed logs for debugging
- MLflow UI: View experiment details and model artifacts
- Databricks Workspace: Check job runs and cluster logs

## 🎓 Best Practices

1. **Always test in Staging first** before deploying to Production
2. **Monitor model performance** regularly using MLflow metrics
3. **Version your data** along with your models
4. **Document model changes** in commit messages
5. **Set up alerts** for model performance degradation
6. **Keep staging and production environments separate**
7. **Regularly review and update hyperparameters**

## 📊 Example Workflow

```bash
# 1. Train a new model
python src/train_model.py

# 2. Check the results in MLflow
python src/deploy_model.py --stage info

# 3. Deploy to staging
python src/deploy_model.py --stage staging

# 4. Test predictions in staging
python src/predict.py --input test_data.csv --stage Staging

# 5. If satisfied, deploy to production
python src/deploy_model.py --stage production

# 6. Monitor production model
python src/deploy_model.py --stage info
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- **GNU MLOps Team** - [nbetini@gmail.com](mailto:nbetini@gmail.com)

## 🔗 Resources

- [Databricks Documentation](https://docs.databricks.com/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)

## 📧 Contact

For questions or support, please contact: nbetini@gmail.com

---

**Built with ❤️ for the MLOps community**

