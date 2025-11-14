# GNU MLOps - Comprehensive File Documentation

**Author:** Narsimha Betini  
**Date:** November 2025  
**Purpose:** Complete documentation of all files in the GNU MLOps repository

---

## Table of Contents

1. [Core Source Files](#core-source-files)
2. [Configuration Files](#configuration-files)
3. [Scripts and Automation](#scripts-and-automation)
4. [CI/CD Files](#cicd-files)
5. [Documentation Files](#documentation-files)
6. [Build and Setup Files](#build-and-setup-files)
7. [Test Files](#test-files)

---

## Core Source Files

| File Path | Purpose | What It Does | How It Does It |
|-----------|---------|--------------|----------------|
| `src/train_model.py` | **Model Training Pipeline** | Trains ML models with MLflow tracking and Databricks integration | **Data Loading:** Attempts to load from Databricks Spark tables, falls back to synthetic data generation if unavailable. Uses pandas for data manipulation.<br><br>**Preprocessing:** Handles missing values, splits data (80/20 train/test), applies StandardScaler for feature normalization, validates data quality.<br><br>**Training:** Uses RandomForestClassifier with configurable hyperparameters, performs 5-fold cross-validation, trains on scaled features.<br><br>**Evaluation:** Calculates accuracy, precision, recall, F1-score, ROC-AUC. Logs all metrics to MLflow.<br><br>**MLflow Integration:** Sets experiment name from config (`gnu_mlflow_config`), logs parameters, metrics, and artifacts (model, scaler, config). Registers model in Model Registry.<br><br>**Error Handling:** Graceful fallback to local data if Databricks unavailable, comprehensive logging at each step. |
| `src/deploy_model.py` | **Model Deployment Automation** | Manages staged model deployments with validation gates | **Stage Management:** Implements 3-stage workflow: None → Staging → GNU_Production. Each stage has performance thresholds (70% for Staging, 80% for Production).<br><br>**Validation:** Checks model accuracy against thresholds before deployment. Validates model artifacts exist and are loadable.<br><br>**Deployment:** Uses MLflow Model Registry to transition models between stages. Archives previous versions when promoting new ones. Adds deployment metadata (timestamp, user, notes).<br><br>**Rollback:** Retrieves previous production version and promotes it back. Maintains version history for quick recovery.<br><br>**Information Retrieval:** Queries MLflow to get current production model details, version, metrics, and deployment history.<br><br>**CLI Interface:** Command-line interface with argparse for different deployment operations (staging, production, rollback, info). |
| `src/predict.py` | **Model Prediction Service** | Loads deployed models and generates predictions on new data | **Model Loading:** Connects to MLflow Model Registry, loads model from specified stage (Staging or GNU_Production). Retrieves model artifacts including saved scaler for consistent preprocessing.<br><br>**Input Handling:** Supports multiple input formats: Python dict, numpy array, pandas DataFrame, CSV file. Automatically converts between formats.<br><br>**Preprocessing:** Applies same StandardScaler used during training to ensure consistency. Validates feature count matches training data.<br><br>**Prediction:** Generates predictions using loaded model. Returns both class predictions and probability scores. Handles single predictions and batch predictions efficiently.<br><br>**File I/O:** Reads CSV files for batch predictions, writes results to output files with timestamps. Supports custom output formats.<br><br>**Error Handling:** Validates model is loaded before predictions, checks input format compatibility, provides clear error messages. |
| `src/batch_inference.py` | **Daily Batch Inference System** | Processes daily data files automatically with scheduled execution | **File Monitoring:** Scans configured input directory (`data/batch_input/`) for new CSV or Parquet files. Supports single file or directory processing.<br><br>**Model Loading:** Loads production model from MLflow Model Registry using ModelPredictor class. Ensures model is ready before processing.<br><br>**Batch Processing:** Processes large files in configurable batches (default 10K rows) to manage memory. Reads data incrementally using pandas chunking.<br><br>**Prediction Generation:** Generates predictions for all rows in input files. Adds prediction columns and timestamps to output.<br><br>**Output Management:** Saves predictions to output directory with timestamped filenames. Formats output as CSV with all original columns plus predictions.<br><br>**Archiving:** Moves processed input files to archive directory after successful processing. Maintains original filenames with timestamps.<br><br>**Logging:** Comprehensive logging to both file and console. Creates timestamped log files in `logs/` directory for scheduled runs.<br><br>**Notifications:** Sends email notifications (if configured) with processing summary, file counts, and any errors encountered.<br><br>**Error Handling:** Continues processing other files if one fails. Logs errors without stopping entire batch. |
| `src/retrain_model.py` | **Automatic Model Retraining** | Schedules and executes automatic model retraining every 30 days | **Schedule Checking:** Queries MLflow to find last training timestamp. Compares with configured interval (default 30 days) to determine if retraining needed.<br><br>**Training Execution:** Uses MLModelTrainer class to train new model with latest data. Follows same training pipeline as manual training.<br><br>**Performance Comparison:** Retrieves current production model metrics from MLflow. Compares new model performance with production model.<br><br>**Auto-Deployment:** If new model meets improvement threshold (configurable), automatically deploys to Staging, then to Production if better. Uses ModelDeployment class for deployment workflow.<br><br>**History Tracking:** Maintains retraining history in MLflow with metadata. Records retraining date, performance comparison, deployment status.<br><br>**Safety Checks:** Validates retraining is needed before executing. Checks data availability. Verifies model quality before deployment.<br><br>**Notifications:** Sends email notifications on retraining completion, deployment status, and performance changes.<br><br>**Force Mode:** Supports `--force` flag to bypass schedule check for manual retraining. |
| `src/__init__.py` | **Package Initialization** | Makes src directory a Python package | Exports main classes (MLModelTrainer, ModelDeployment, ModelPredictor) for easy imports. Defines package-level constants and version information. |

---

## Configuration Files

| File Path | Purpose | What It Does | How It Does It |
|-----------|---------|--------------|----------------|
| `config.yaml` | **Main Configuration File** | Central configuration for entire MLOps pipeline | **Structure:** YAML format with nested sections for different components.<br><br>**Databricks Config:** Stores Databricks host URL, access token (or env var reference), workspace path for file storage.<br><br>**MLflow Config:** Defines experiment name (`gnu_mlflow_config`), model name in registry, tracking URI (databricks or local).<br><br>**Model Config:** Specifies algorithm type (random_forest, xgboost, etc.), hyperparameters (n_estimators, max_depth, random_state).<br><br>**Training Config:** Sets test/validation split ratios, cross-validation folds, random seed for reproducibility.<br><br>**Data Config:** Defines data source (databricks/s3/local), table name for Databricks, feature columns, target column name.<br><br>**Deployment Config:** Sets model stage preferences, endpoint configuration, compute resources (workers, instance types).<br><br>**Monitoring Config:** Enables drift detection, prediction logging, alert email addresses.<br><br>**Retraining Config:** Enables/disables automatic retraining, sets interval (days), auto-deploy flag, improvement threshold, notification email.<br><br>**Batch Inference Config:** Configures input/output/archive paths, model stage to use, batch size, archiving behavior, notification email.<br><br>**Usage:** Loaded by all Python modules using `yaml.safe_load()`. Environment variables can override config values. |
| `config.local.yaml` | **Local Development Configuration** | Local testing configuration with SQLite MLflow | **Purpose:** Same structure as `config.yaml` but configured for local development without Databricks.<br><br>**MLflow Tracking:** Uses `sqlite:///mlflow.db` instead of Databricks for local MLflow tracking.<br><br>**Data Source:** Typically set to "local" to use local CSV files instead of Databricks tables.<br><br>**Usage:** Used when running pipeline locally for development/testing. Can be specified with `--config` flag in scripts. |

---

## Scripts and Automation

| File Path | Purpose | What It Does | How It Does It |
|-----------|---------|--------------|----------------|
| `scripts/schedule_batch_inference.sh` | **Batch Inference Cron Setup** | Sets up cron job for daily batch inference at 1 PM PST | **Environment Detection:** Finds project directory, virtual environment, Python executable, and script paths automatically.<br><br>**Validation:** Checks virtual environment exists, batch inference script exists, config file exists. Provides helpful error messages if missing.<br><br>**Directory Creation:** Creates required directories: `data/batch_input/`, `data/batch_output/`, `data/batch_archive/`, `logs/`.<br><br>**Schedule Selection:** Interactive menu for choosing schedule (1 PM PST, 2 PM PST, custom cron expression). Handles timezone conversion (PST to UTC).<br><br>**Cron Job Creation:** Builds cron job entry with environment variables, project directory, Python path, script path, and log file. Checks for existing jobs and offers to replace.<br><br>**Installation:** Adds cron job using `crontab` command. Provides instructions for viewing, editing, and removing cron jobs.<br><br>**Testing:** Provides commands for manual testing and log viewing. |
| `scripts/schedule_retraining.sh` | **Retraining Cron Setup** | Sets up cron job for automatic retraining every 30 days | **Similar to batch inference scheduler:** Same structure but for retraining script.<br><br>**Schedule Options:** Daily (testing), weekly (Monday 2 AM), monthly (1st of month), every 30 days (1st and 15th), or custom cron expression.<br><br>**Cron Job:** Creates cron job that runs `retrain_model.py` with proper environment setup and logging.<br><br>**Instructions:** Provides commands for testing, force retraining, and log viewing. |
| `scripts/setup_databricks.sh` | **Databricks Workspace Setup** | Configures Databricks workspace and environment | Sets up Databricks CLI, configures authentication, creates workspace directories, uploads scripts to DBFS. |
| `scripts/test_setup.sh` | **Environment Validation** | Validates project setup and dependencies | Checks Python version, verifies virtual environment, tests imports, validates configuration files, checks MLflow connection. |
| `scripts/run_training.sh` | **Training Execution Script** | Wrapper script for running training pipeline | Activates virtual environment, sets environment variables, runs `train_model.py` with proper error handling and logging. |
| `scripts/deploy.sh` | **Deployment Wrapper** | Wrapper script for model deployment | Provides convenient interface for deploying models to different stages with proper environment setup. |
| `scripts/test_local.sh` | **Local Testing Script** | Runs local tests without Databricks | Sets MLFLOW_TRACKING_URI to SQLite, runs training and deployment tests locally, validates functionality. |

---

## CI/CD Files

| File Path | Purpose | What It Does | How It Does It |
|-----------|---------|--------------|----------------|
| `.github/workflows/train-and-deploy.yml` | **GitHub Actions CI/CD Pipeline** | Automated training and deployment on code changes | **Triggers:** Activates on push to main/develop branches, pull requests, or manual workflow dispatch.<br><br>**Environment:** Sets up Databricks secrets (host, token) and MLflow tracking URI from GitHub secrets.<br><br>**Train Job:** Checks out code, sets up Python 3.9, caches dependencies, installs packages, runs tests, trains model, deploys to Staging (if main branch).<br><br>**Deploy-Production Job:** Conditional job that runs after training. Deploys to Production if manual trigger with `deploy_to_production=true` or commit message contains `[deploy-prod]`.<br><br>**Notifications:** Sends deployment notifications on completion. Logs all steps for debugging.<br><br>**Error Handling:** Fails fast on errors, provides detailed logs for troubleshooting. |

---

## Documentation Files

| File Path | Purpose | What It Does | How It Does It |
|-----------|---------|--------------|----------------|
| `README.md` | **Project Overview** | Main project documentation and quick start guide | Provides project description, features list, installation instructions, configuration guide, usage examples, project structure, CI/CD information, troubleshooting tips. Serves as entry point for new users. |
| `PRESENTATION_GNU_MLOPS.md` | **Interview Presentation** | 31-slide presentation for interview panel | Comprehensive presentation covering: architecture diagrams, data flow, GitHub Actions, DBFS, Databricks pipelines, current features, future enhancements. Includes ASCII diagrams and detailed explanations. |
| `PPT_CONVERSION_GUIDE.md` | **PowerPoint Conversion Guide** | Instructions for converting markdown to PowerPoint | Provides multiple methods (manual, pandoc, online tools, Python) for converting presentation markdown to PowerPoint. Includes design tips, visual element suggestions, and time estimates. |
| `DEPLOYMENT.md` | **Deployment Guide** | Detailed deployment instructions | Explains deployment workflow, prerequisites, staging/production deployment steps, rollback procedures, monitoring, and automated deployment via GitHub Actions. |
| `QUICKSTART.md` | **Quick Start Guide** | Fast setup instructions | Condensed version of README with essential commands and steps to get started quickly. |
| `LOCAL_RUN_GUIDE.md` | **Local Execution Guide** | Step-by-step local machine setup | Detailed instructions for running pipeline on local machine without Databricks. Includes environment setup, configuration, execution commands, and troubleshooting. |
| `AUTOMATIC_RETRAINING_GUIDE.md` | **Retraining Documentation** | Guide for automatic retraining system | Explains retraining configuration, scheduling setup, manual execution, monitoring, and troubleshooting. |
| `BATCH_INFERENCE_GUIDE.md` | **Batch Inference Documentation** | Guide for batch inference system | Documents batch inference setup, file formats, scheduling, output format, archiving, and monitoring. |
| `CODE_EDUCATION_GUIDE.md` | **Code Education Guide** | Comprehensive code walkthrough | Detailed explanation of each module, MLOps concepts, design patterns, best practices. Educational resource for understanding the codebase. |
| `CODE_QUICK_REFERENCE.md` | **Quick Reference Cheat Sheet** | Quick lookup for methods and commands | Condensed reference for methods, workflows, and commands. Quick lookup guide for developers. |

---

## Build and Setup Files

| File Path | Purpose | What It Does | How It Does It |
|-----------|---------|--------------|----------------|
| `requirements.txt` | **Python Dependencies** | Lists all Python package dependencies | **Core Libraries:** numpy, pandas, scikit-learn, scipy for data science.<br><br>**MLflow & Databricks:** mlflow, databricks-cli, databricks-sql-connector for MLOps infrastructure.<br><br>**ML Libraries:** xgboost, lightgbm for additional algorithms.<br><br>**Utilities:** pyyaml for config, python-dotenv for env vars, joblib for serialization, click for CLI.<br><br>**Logging:** loguru for advanced logging.<br><br>**API:** fastapi, uvicorn, pydantic for API deployment.<br><br>**Testing:** pytest, pytest-cov for testing.<br><br>**Development:** black, flake8, mypy for code quality.<br><br>**Usage:** Installed via `pip install -r requirements.txt`. |
| `setup.py` | **Python Package Setup** | Makes project installable as Python package | **Package Definition:** Defines package name (gnu-mlops), version, author, description, URL.<br><br>**Dependencies:** Lists core dependencies for package installation.<br><br>**Extras:** Defines optional dev dependencies (pytest, black, flake8).<br><br>**Usage:** Install with `pip install -e .` for development or `pip install .` for production. |
| `Makefile` | **Build Automation** | Provides convenient make commands | **Commands:** `make install` (install deps), `make setup` (Databricks setup), `make train` (train model), `make deploy-staging` (deploy to staging), `make deploy-production` (deploy to production), `make predict` (run predictions), `make test` (run tests), `make lint` (code linting), `make format` (code formatting), `make clean` (clean generated files).<br><br>**Usage:** Run `make <command>` for quick access to common operations. |
| `setup_env.sh` | **Environment Setup Script** | Sets up development environment | Creates virtual environment, installs dependencies, sets up environment variables, validates installation. |
| `.gitignore` | **Git Ignore Rules** | Excludes files from version control | **Python:** __pycache__, *.pyc, *.egg-info, build/, dist/<br><br>**Environment:** venv/, .env files<br><br>**MLflow:** mlruns/, mlartifacts/, mlflow.db<br><br>**Data:** *.csv, *.parquet, data/ directory<br><br>**Logs:** *.log, logs/<br><br>**Models:** models/, artifacts/<br><br>**OS:** .DS_Store, Thumbs.db<br><br>**Documentation:** Generated docs, test files, zip files |

---

## Test Files

| File Path | Purpose | What It Does | How It Does It |
|-----------|---------|--------------|----------------|
| `tests/test_train_model.py` | **Training Tests** | Unit tests for training pipeline | Tests data loading, preprocessing, model training, MLflow logging, error handling. Uses pytest framework. |
| `tests/test_deploy_model.py` | **Deployment Tests** | Unit tests for deployment system | Tests model validation, stage transitions, rollback functionality, metadata management. |
| `tests/__init__.py` | **Test Package Init** | Makes tests directory a package | Standard Python package initialization for test modules. |

---

## Additional Utility Files

| File Path | Purpose | What It Does | How It Does It |
|-----------|---------|--------------|----------------|
| `create_datasets.py` | **Dataset Generator** | Creates sample training and test datasets | Generates synthetic datasets with configurable features, target variable, sample size. Useful for testing and development. |
| `deploy_databricks.sh` | **Databricks Deployment Script** | Deploys model to Databricks workspace | Uploads model artifacts to DBFS, creates Databricks job, configures endpoint for serving. |

---

## File Statistics Summary

### By Category

- **Core Source Files:** 6 files (train_model.py, deploy_model.py, predict.py, batch_inference.py, retrain_model.py, __init__.py)
- **Configuration Files:** 2 files (config.yaml, config.local.yaml)
- **Scripts:** 7 files (scheduling, setup, testing scripts)
- **CI/CD Files:** 1 file (GitHub Actions workflow)
- **Documentation Files:** 12+ files (README, guides, presentations)
- **Build Files:** 4 files (requirements.txt, setup.py, Makefile, .gitignore)
- **Test Files:** 3 files (test modules)

### Total Lines of Code

- **Python Source Code:** ~3,500+ lines
- **Documentation:** ~5,000+ lines
- **Configuration:** ~200 lines
- **Scripts:** ~500 lines
- **Total:** ~9,200+ lines

---

## Key Design Patterns

### 1. **Configuration-Driven Architecture**
- All modules load from `config.yaml`
- Environment variables can override config
- Separate configs for local/production

### 2. **Modular Design**
- Each module has single responsibility
- Classes encapsulate functionality
- Clear interfaces between modules

### 3. **Error Handling**
- Graceful fallbacks (Databricks → local)
- Comprehensive logging at all levels
- Clear error messages for debugging

### 4. **MLflow Integration**
- Centralized experiment tracking
- Model Registry for versioning
- Artifact storage for reproducibility

### 5. **Staged Deployment**
- Validation gates at each stage
- Automatic archiving of previous versions
- Rollback capabilities

### 6. **Scheduled Operations**
- Cron-based scheduling
- Automated retraining
- Daily batch inference

---

## Usage Workflow

### 1. **Initial Setup**
```
1. Clone repository
2. Create virtual environment: python -m venv venv
3. Install dependencies: pip install -r requirements.txt
4. Configure config.yaml with your settings
5. Set up Databricks credentials (if using)
```

### 2. **Training Workflow**
```
1. Prepare data (Databricks table or local CSV)
2. Run training: python src/train_model.py
3. Model automatically registered in MLflow
4. View results in MLflow UI
```

### 3. **Deployment Workflow**
```
1. Deploy to Staging: python src/deploy_model.py --stage staging
2. Validate in Staging environment
3. Deploy to Production: python src/deploy_model.py --stage production
4. Monitor production model
```

### 4. **Prediction Workflow**
```
1. Load predictor: predictor = ModelPredictor(stage='GNU_Production')
2. Make predictions: predictions = predictor.predict(data)
3. Or use batch inference: python src/batch_inference.py
```

### 5. **Scheduled Operations**
```
1. Set up batch inference: bash scripts/schedule_batch_inference.sh
2. Set up retraining: bash scripts/schedule_retraining.sh
3. Monitor logs in logs/ directory
```

---

## Integration Points

### **MLflow Integration**
- Experiment tracking for all training runs
- Model Registry for version management
- Artifact storage for models and scalers
- Metrics logging for performance tracking

### **Databricks Integration**
- DBFS for file storage
- Spark for data processing
- Databricks SQL for data access
- Databricks Jobs for scheduling

### **GitHub Actions Integration**
- Automated testing on pull requests
- Automated training on code changes
- Automated deployment to staging
- Manual production deployment trigger

---

## Security Considerations

### **Credential Management**
- No hardcoded secrets in code
- Environment variables for sensitive data
- GitHub Secrets for CI/CD
- Config file for non-sensitive settings

### **Access Control**
- Databricks token-based authentication
- MLflow access via tracking URI
- File system permissions for local files

### **Data Protection**
- Input validation in all modules
- Error handling prevents data leakage
- Logging excludes sensitive information

---

## Performance Optimizations

### **Training**
- Cross-validation parallelization (`n_jobs=-1`)
- Efficient data loading (pandas/Spark)
- Memory-efficient batch processing

### **Inference**
- Model caching (loaded once, reused)
- Batch processing for large datasets
- Efficient preprocessing pipeline

### **Scheduling**
- Cron-based lightweight scheduling
- Separate log files for each run
- Error recovery without stopping pipeline

---

## Future Enhancement Areas

1. **Real-time Inference API** (FastAPI endpoint)
2. **Model Monitoring Dashboard** (Grafana/MLflow UI)
3. **A/B Testing Framework** (Multiple model comparison)
4. **Feature Store** (Centralized feature management)
5. **Automated Hyperparameter Tuning** (Optuna/Hyperopt)
6. **Model Explainability** (SHAP/LIME integration)
7. **Distributed Training** (Spark MLlib)
8. **GPU Support** (CUDA acceleration)
9. **Kubernetes Deployment** (Container orchestration)
10. **Advanced Monitoring** (Drift detection, performance alerts)

---

## Conclusion

This GNU MLOps framework provides a complete, production-ready solution for machine learning operations. All files work together to create an automated, scalable, and maintainable ML pipeline with comprehensive documentation and testing capabilities.

**For questions or contributions, please refer to the README.md or contact the maintainer.**

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Maintained By:** Narsimha Betini

