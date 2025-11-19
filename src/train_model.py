"""
Custom ML Training Pipeline
Author: Narsimha Betini
Purpose: Train and track ML models using MLflow with Databricks backend
Created: 2025

This module handles the complete lifecycle of model training including:
- Data ingestion from various sources
- Preprocessing and feature engineering  
- Model training with validation
- Performance tracking and logging
"""

import os
import yaml
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import logging
from pathlib import Path
import sys
import signal
from contextlib import contextmanager
from mlflow.models.signature import infer_signature


# Setup logging with custom format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _validate_databricks_credentials():
    """
    Check if Databricks credentials are available and valid
    
    Validates that Databricks host and token are set and not placeholders.
    This allows the system to determine if Databricks connectivity is possible.
    
    Returns:
        bool: True if Databricks credentials are available, False otherwise
    """
    databricks_host = os.getenv('DATABRICKS_HOST') or os.getenv('DATABRICKS_SERVER_HOSTNAME')
    databricks_token = os.getenv('DATABRICKS_TOKEN') or os.getenv('DATABRICKS_ACCESS_TOKEN')
    
    if not databricks_host or not databricks_token:
        return False
    
    # Check if credentials are not placeholders
    if databricks_token in ['YOUR_TOKEN', 'YOUR_DATABRICKS_ACCESS_TOKEN_HERE', '']:
        return False
    
    return True


def _test_databricks_connection(timeout_seconds=10):
    """
    Test Databricks connection with timeout
    
    Attempts a lightweight connection test to verify Databricks is reachable.
    This prevents long timeouts during actual operations.
    
    NOTE: Currently commented out to avoid timeout issues in GitHub Actions.
    Uncomment when Databricks connectivity is reliable.
    
    Args:
        timeout_seconds: Maximum time to wait for connection test (default: 10 seconds)
        
    Returns:
        bool: True if connection is successful, False if timeout or error
    """
    if not _validate_databricks_credentials():
        return False
    
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        
        # Save current tracking URI
        original_uri = mlflow.get_tracking_uri()
        
        # Try to connect to Databricks with timeout
        if hasattr(signal, 'SIGALRM'):
            # Unix/Linux/Mac - use signal-based timeout
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Databricks connection test timed out after {timeout_seconds} seconds")
            
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            try:
                mlflow.set_tracking_uri('databricks')
                client = MlflowClient()
                # Try a lightweight operation - list experiments (should be fast)
                # This will fail fast if Databricks is unreachable
                try:
                    experiments = client.list_experiments(max_results=1)
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                    mlflow.set_tracking_uri(original_uri)
                    return True
                except Exception as e:
                    # If we can't list experiments, Databricks is likely unreachable
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                    mlflow.set_tracking_uri(original_uri)
                    logger.warning(f"Databricks connection test failed: {e}")
                    return False
            except TimeoutError:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
                mlflow.set_tracking_uri(original_uri)
                logger.warning(f"Databricks connection test timed out after {timeout_seconds} seconds")
                return False
            except Exception as e:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
                mlflow.set_tracking_uri(original_uri)
                logger.warning(f"Databricks connection test error: {e}")
                return False
        else:
            # Windows - use threading timeout
            import threading
            result = {'success': False, 'error': None}
            
            def test_connection():
                try:
                    mlflow.set_tracking_uri('databricks')
                    client = MlflowClient()
                    experiments = client.list_experiments(max_results=1)
                    result['success'] = True
                except Exception as e:
                    result['error'] = e
            
            thread = threading.Thread(target=test_connection)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)
            
            mlflow.set_tracking_uri(original_uri)
            
            if thread.is_alive():
                logger.warning(f"Databricks connection test timed out after {timeout_seconds} seconds")
                return False
            
            if result['error']:
                logger.warning(f"Databricks connection test failed: {result['error']}")
                return False
            
            return result['success']
            
    except Exception as e:
        logger.warning(f"Error testing Databricks connetion")
        return False
    
    #Always return False when commented out (forces SQLite fallback)
    #return False


@contextmanager
def timeout_context(seconds):
    """
    Context manager for timeout operations
    
    Args:
        seconds: Timeout in seconds
        
    Yields:
        None
        
    Raises:
        TimeoutError: If operation exceeds timeout
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # Set up signal handler for timeout (Unix only)
    if hasattr(signal, 'SIGALRM'):
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # Windows doesn't support SIGALRM, use threading timeout instead
        import threading
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = True
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(seconds)
        
        if thread.is_alive():
            raise TimeoutError(f"Operation timed out after {seconds} seconds")
        if exception[0]:
            raise exception[0]
        yield


def _set_experiment_with_timeout(experiment_name, tracking_uri, timeout_seconds=30):
    """
    Set MLflow experiment with timeout and automatic fallback
    
    Args:
        experiment_name: Name of the experiment to set
        tracking_uri: Current MLflow tracking URI
        timeout_seconds: Maximum time to wait (default: 30 seconds)
        
    Returns:
        tuple: (success: bool, fallback_uri: str or None)
               success: True if experiment was set successfully
               fallback_uri: SQLite URI if fallback needed, None otherwise
    """
    try:
        # Try to set experiment with timeout
        if hasattr(signal, 'SIGALRM'):
            # Unix/Linux/Mac - use signal-based timeout
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Setting experiment timed out after {timeout_seconds} seconds")
            
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            try:
                mlflow.set_experiment(experiment_name)
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
                return True, None
            except (TimeoutError, Exception) as e:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
                raise
        else:
            # Windows - use threading timeout
            import threading
            result = {'success': False, 'error': None}
            
            def set_experiment():
                try:
                    mlflow.set_experiment(experiment_name)
                    result['success'] = True
                except Exception as e:
                    result['error'] = e
            
            thread = threading.Thread(target=set_experiment)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"Setting experiment timed out after {timeout_seconds} seconds")
            
            if result['error']:
                raise result['error']
            
            return True, None
            
    except TimeoutError as e:
        logger.warning(f"Timeout setting experiment '{experiment_name}': {e}")
        logger.info("Falling back to local SQLite tracking due to timeout")
        return False, 'sqlite:///mlflow.db'
    except Exception as e:
        logger.warning(f"Error setting experiment '{experiment_name}': {e}")
        # If it's a network/connection error, fall back to SQLite
        if 'timeout' in str(e).lower() or 'timed out' in str(e).lower() or 'connection' in str(e).lower():
            logger.info("Falling back to local SQLite tracking due to connection issue")
            return False, 'sqlite:///mlflow.db'
        # For other errors, try default experiment
        try:
            mlflow.set_experiment("gnu-mlops-experiments")
            return True, None
        except:
            logger.warning("Could not set default experiment, will use current/default")
            return False, None


def _get_mlflow_tracking_uri(config_tracking_uri):
    """
    Determine the appropriate MLflow tracking URI with automatic fallback
    
    Priority:
    1. GitHub Actions detection (ALWAYS uses SQLite) - HIGHEST PRIORITY
    2. MLFLOW_TRACKING_URI environment variable (if set and valid)
    3. Databricks (if credentials available and config says databricks)
    4. SQLite fallback (local mode)
    
    Args:
        config_tracking_uri: Tracking URI from config file
        
    Returns:
        str: MLflow tracking URI to use (always SQLite in GitHub Actions)
    """
    # ========================================================================
    # CRITICAL: GitHub Actions ALWAYS uses SQLite - no exceptions
    # ========================================================================
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    force_databricks = os.getenv('FORCE_DATABRICKS') == 'true'
    
    if is_github_actions and not force_databricks:
        logger.info("=" * 70)
        logger.info("GitHub Actions detected - FORCING SQLite (Databricks disabled)")
        logger.info("To use Databricks in GitHub Actions, set FORCE_DATABRICKS=true")
        logger.info("=" * 70)
        return 'sqlite:///mlflow.db'
    
    # Check environment variable
    env_tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
    
    # If explicitly set to SQLite or file path, use it
    if env_tracking_uri and (env_tracking_uri.startswith('sqlite:///') or 
                             env_tracking_uri.startswith('file:///')):
        logger.info(f"Using MLflow tracking URI from environment: {env_tracking_uri}")
        return env_tracking_uri
    
    # ========================================================================
    # DATABRICKS CONNECTIVITY - ENABLED (when not in GitHub Actions)
    # ========================================================================
    # If explicitly set to databricks, validate credentials and test connection
    # Only do this if NOT in GitHub Actions (unless forced)
    if (env_tracking_uri == 'databricks' or config_tracking_uri == 'databricks') and (not is_github_actions or force_databricks):
        if _validate_databricks_credentials():
            # Test connection with short timeout to avoid long waits
            logger.info("Testing Databricks connection...")
            if _test_databricks_connection(timeout_seconds=5):
                logger.info("Databricks connection successful, using Databricks MLflow tracking")
                return 'databricks'
            else:
                logger.warning("Databricks connection test failed or timed out")
                logger.info("Falling back to SQLite for local tracking")
                return 'sqlite:///mlflow.db'
        else:
            logger.warning("Databricks tracking URI specified but credentials not available")
            logger.info("Falling back to SQLite for local tracking")
            return 'sqlite:///mlflow.db'
    
    # If environment variable is set, use it (but check GitHub Actions first)
    if env_tracking_uri:
        if is_github_actions and env_tracking_uri == 'databricks' and not force_databricks:
            logger.warning("MLFLOW_TRACKING_URI=databricks detected in GitHub Actions")
            logger.info("Overriding to SQLite to avoid timeout issues")
            logger.info("Set FORCE_DATABRICKS=true if you really need Databricks")
            return 'sqlite:///mlflow.db'
        logger.info(f"Using MLflow tracking URI from environment: {env_tracking_uri}")
        return env_tracking_uri
    
    # Default to SQLite for local development or GitHub Actions
    if not config_tracking_uri or config_tracking_uri == 'databricks':
        if is_github_actions:
            logger.info("Using SQLite for GitHub Actions (avoids timeout issues)")
        else:
            logger.info("Using SQLite for local MLflow tracking")
        return 'sqlite:///mlflow.db'
    
    return config_tracking_uri


class MLModelTrainer:
    """
    Handles end-to-end model training workflow
    
    This class orchestrates the entire training process from data loading
    through model evaluation and registration. It integrates with MLflow
    for experiment tracking and model versioning.
    """
    def __init__(self):
        # Load config (you probably already have this)
        self.config = load_config()

        # === SET MODEL NAME HERE ===
        base_name = self.config['mlflow']['model_name']  # typically "gnu-mlops-model"

        use_uc = (
            self.config.get('databricks', {}).get('use_unity_catalog', False)
            or os.getenv('DATABRICKS_USE_UNITY_CATALOG', '').lower() == 'true'
        )

        if use_uc:
            catalog = self.config.get('databricks', {}).get('catalog', os.getenv('DATABRICKS_CATALOG', 'workspace'))
            schema = self.config.get('databricks', {}).get('schema', os.getenv('DATABRICKS_SCHEMA', 'default'))
            self.model_name = f"{catalog}.{schema}.{base_name}"
        else:
            self.model_name = base_name

        logger.info(f"Trainer using model name: {self.model_name}")

        # ---------------------------------------------------------------
        # Determine model registry name (used for training & deployment)
        # ---------------------------------------------------------------
        base_model_name = self.config.get('mlflow', {}).get('model_name', 'gnu-mlops-model')

        # Unity Catalog is used when:
        #  - tracking URI is Databricks
        #  - AND UC is enabled via config or env
        use_unity_catalog = (
            tracking_uri == "databricks"
            and (
                self.config.get('databricks', {}).get('use_unity_catalog', False)
                or os.getenv('DATABRICKS_USE_UNITY_CATALOG', '').lower() == 'true'
            )
        )

        if use_unity_catalog:
            catalog = self.config.get('databricks', {}).get(
                'catalog', os.getenv('DATABRICKS_CATALOG', 'workspace')
            )
            schema = self.config.get('databricks', {}).get(
                'schema', os.getenv('DATABRICKS_SCHEMA', 'default')
            )
            self.model_name = f"{catalog}.{schema}.{base_model_name}"
            logger.info(f"Using Databricks Unity Catalog model name: {self.model_name}")
        else:
            # Simple name (SQLite/local or non-UC Databricks)
            self.model_name = base_model_name
            logger.info(f"Using simple model name: {self.model_name}")




    def __init__(self, config_path='config.yaml'):
        """
        Set up the training environment
        
        Args:
            config_path: Path to YAML configuration file
        """
        # Load configuration - validate it exists first
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Override config values from environment variables (secure credential management)
        # This ensures credentials are never hardcoded in config files
        if 'databricks' in self.config:
            # Override Databricks host from environment variable
            self.config['databricks']['host'] = os.getenv(
                'DATABRICKS_HOST',
                self.config['databricks'].get('host', '')
            )
            # Override Databricks token from environment variable (required for security)
            self.config['databricks']['token'] = os.getenv(
                'DATABRICKS_TOKEN',
                self.config['databricks'].get('token', '')
            )
            # Override workspace path from environment variable
            self.config['databricks']['workspace_path'] = os.getenv(
                'DATABRICKS_WORKSPACE_PATH',
                self.config['databricks'].get('workspace_path', '')
            )
        
        # Override MLflow experiment path from environment variable
        if 'mlflow' in self.config:
            self.config['mlflow']['gnu_mlflow_config'] = os.getenv(
                'DATABRICKS_EXPERIMENT_PATH',
                self.config['mlflow'].get('gnu_mlflow_config', 'gnu-mlops-experiments')
            )
        
        # ========================================================================
        # CRITICAL: Force SQLite in GitHub Actions - Databricks COMPLETELY DISABLED
        # ========================================================================
        # This check happens FIRST, before any other logic, to ensure we NEVER
        # try to use Databricks in GitHub Actions (which causes 8+ minute timeouts).
        # All Databricks connectivity code is disabled.
        # ========================================================================
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        env_tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
        force_databricks = os.getenv('FORCE_DATABRICKS', '').lower() == 'true'

        if is_github_actions and not force_databricks:
            # Default in GitHub Actions: use SQLite (fast, no Databricks calls)
            tracking_uri = 'sqlite:///mlflow.db'
            logger.info("=" * 70)
            logger.info("GitHub Actions detected - using SQLite (Databricks disabled)")
            logger.info(f"Tracking URI: {tracking_uri}")
            logger.info("=" * 70)
        elif env_tracking_uri:
            # If an explicit tracking URI is provided, use it (Databricks or SQLite)
            tracking_uri = env_tracking_uri
            logger.info(f"Using tracking URI from environment: {tracking_uri}")
        else:
            # Fallback for local dev: use value from config, possibly normalized
            config_tracking_uri = self.config.get('mlflow', {}).get('tracking_uri', 'sqlite:///mlflow.db')
            tracking_uri = _get_mlflow_tracking_uri(config_tracking_uri)

        # Set tracking URI (guaranteed to be SQLite - Databricks is disabled)
        mlflow.set_tracking_uri(tracking_uri)
        logger.info(f"Final MLflow tracking URI: {tracking_uri}")
        
        # Set up experiment for organizing runs with timeout protection
        # Use a local-friendly experiment name if using SQLite
                # Set up experiment for organizing runs
        gnu_mlflow_config = self.config['mlflow']['gnu_mlflow_config']

        gnu_mlflow_config = self.config['mlflow']['gnu_mlflow_config']

        if tracking_uri == "databricks":
            # Databricks: experiment names MUST be absolute workspace paths.
            # To avoid invalid or masked paths from env/config, force a safe shared location.
            exp_path = "/Shared/gnu-mlops-experiments"

            try:
                mlflow.set_experiment(exp_path)
                gnu_mlflow_config = exp_path
                logger.info(f"Using Databricks experiment path: {exp_path}")
            except Exception as e:
                logger.error(f"Failed to set Databricks experiment '{exp_path}': {e}")
                # Fail fast rather than running with an invalid experiment ID
                raise
        else:
            # --- Local/SQLite behavior (keep your existing timeout + fallback logic) ---
            # Use a local-friendly experiment name if using SQLite
            if tracking_uri.startswith("sqlite:///") and (
                gnu_mlflow_config.startswith("/Users/") or gnu_mlflow_config.startswith("/")
            ):
                # Extract experiment name from path or use default
                path_parts = [p for p in gnu_mlflow_config.strip("/").split("/") if p]
                if path_parts:
                    experiment_name = path_parts[-1]
                else:
                    experiment_name = "gnu-mlops-experiments"

                logger.info(f"Using local experiment name: {experiment_name} (from {gnu_mlflow_config})")
                success, fallback_uri = _set_experiment_with_timeout(
                    experiment_name, tracking_uri, timeout_seconds=10
                )
                if success:
                    gnu_mlflow_config = experiment_name  # Update for logging
                else:
                    if fallback_uri:
                        logger.warning(f"Could not set experiment {experiment_name}, using default")
                        try:
                            mlflow.set_experiment("gnu-mlops-experiments")
                            gnu_mlflow_config = "gnu-mlops-experiments"
                        except Exception:
                            logger.warning("Using current/default experiment")
                    else:
                        gnu_mlflow_config = experiment_name
            else:
                # For remote non-Databricks tracking (or simple SQLite), use timeout protection
                success, fallback_uri = _set_experiment_with_timeout(
                    gnu_mlflow_config, tracking_uri, timeout_seconds=30
                )
                if not success:
                    if fallback_uri:
                        # Fallback to SQLite if Databricks times out
                        logger.warning(
                            f"Remote experiment setup timed out, falling back to local SQLite"
                        )
                        tracking_uri = fallback_uri
                        mlflow.set_tracking_uri(tracking_uri)
                        path_parts = [p for p in gnu_mlflow_config.strip("/").split("/") if p]
                        if path_parts:
                            experiment_name = path_parts[-1]
                        else:
                            experiment_name = "gnu-mlops-experiments"
                        try:
                            mlflow.set_experiment(experiment_name)
                            gnu_mlflow_config = experiment_name
                            logger.info(f"Using local experiment: {experiment_name}")
                        except Exception:
                            mlflow.set_experiment("gnu-mlops-experiments")
                            gnu_mlflow_config = "gnu-mlops-experiments"
                    else:
                        try:
                            mlflow.set_experiment("gnu-mlops-experiments")
                            gnu_mlflow_config = "gnu-mlops-experiments"
                        except Exception:
                            logger.warning("Could not set experiment, using current/default")

        logger.info(f"Training pipeline initialized")
        logger.info(f"→ Experiment: {gnu_mlflow_config}")
        logger.info(f"→ Tracking: {tracking_uri}")

        # Store tracking URI for later use (may have changed during fallback)
        self.tracking_uri = tracking_uri

        # (model name logic continues below – keep your existing self.model_name block)
        self.config['mlflow']['gnu_mlflow_config'] = gnu_mlflow_config

                # ---------------------------------------------------------------
        # Determine model registry name (used for training & deployment)
        # ---------------------------------------------------------------
        base_model_name = self.config.get('mlflow', {}).get('model_name', 'gnu-mlops-model')

        # Unity Catalog is used when:
        #  - tracking URI is Databricks
        #  - AND UC is enabled via config or environment
        use_unity_catalog = (
            tracking_uri == "databricks"
            and (
                self.config.get('databricks', {}).get('use_unity_catalog', False)
                or os.getenv('DATABRICKS_USE_UNITY_CATALOG', '').lower() == 'true'
            )
        )

        if use_unity_catalog:
            catalog = self.config.get('databricks', {}).get(
                'catalog', os.getenv('DATABRICKS_CATALOG', 'workspace')
            )
            schema = self.config.get('databricks', {}).get(
                'schema', os.getenv('DATABRICKS_SCHEMA', 'default')
            )
            self.model_name = f"{catalog}.{schema}.{base_model_name}"
            logger.info(f"Using Databricks Unity Catalog model name: {self.model_name}")
        else:
            # Simple name (SQLite/local or non-UC Databricks)
            self.model_name = base_model_name
            logger.info(f"Using simple model name: {self.model_name}")


    
    def load_data(self):
        """
        Fetch training data from configured source
        
        Returns:
            pandas.DataFrame: Loaded dataset
        """
        data_source = self.config['data'].get('source', 'local')
        logger.info(f"Attempting to load data from: {data_source}")
        
        # Try Databricks/Spark first if available
        if data_source == 'databricks':
            try:
                from pyspark.sql import SparkSession
                spark = SparkSession.builder.getOrCreate()
                table_name = self.config['data']['table_name']
                
                logger.info(f"Connecting to Spark table: {table_name}")
                spark_df = spark.table(table_name)
                df = spark_df.toPandas()
                
                logger.info(f"✓ Successfully loaded {len(df):,} records from Databricks")
                return df
                
            except Exception as spark_error:
                logger.warning(f"Spark connection failed: {spark_error}")
                logger.info("Falling back to local data...")
        
        # Try loading from local file
        if data_source == 'local':
            local_data_path = self.config['data'].get('local_path', 'data/training/titanic_training_data.csv')
            data_file = Path(local_data_path)
            
            if data_file.exists():
                logger.info(f"Loading data from local file: {local_data_path}")
                try:
                    df = pd.read_csv(data_file)
                    logger.info(f"✓ Successfully loaded {len(df):,} records from {local_data_path}")
                    logger.info(f"  Columns: {list(df.columns)}")
                    return df
                except Exception as e:
                    logger.warning(f"Failed to load local data file: {e}")
                    logger.info("Trying to load raw Titanic data...")
            else:
                logger.warning(f"Local data file not found: {local_data_path}")
                logger.info("Trying to load raw Titanic data...")
            
            # Try loading raw Titanic data if preprocessed file doesn't exist
            titanic_train_path = Path('data/titanic/train.csv')
            if titanic_train_path.exists():
                logger.info("Loading raw Titanic training data...")
                try:
                    df_raw = pd.read_csv(titanic_train_path)
                    logger.info(f"Loaded raw Titanic data: {len(df_raw):,} rows")
                    logger.info(f"  Columns: {list(df_raw.columns)}")
                    
                    # Quick preprocessing inline
                    logger.info("Performing quick preprocessing...")
                    df = df_raw.copy()
                    
                    # Handle missing values
                    df['Age'].fillna(df['Age'].median(), inplace=True)
                    df['Embarked'].fillna(df['Embarked'].mode()[0], inplace=True)
                    df['Fare'].fillna(df['Fare'].median(), inplace=True)
                    df['HasCabin'] = df['Cabin'].notna().astype(int)
                    
                    # One-hot encode
                    features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked', 'HasCabin']
                    df_processed = pd.get_dummies(df[features], columns=['Sex', 'Embarked'], drop_first=True)
                    df_processed.columns = [f'feature{i+1}' for i in range(len(df_processed.columns))]
                    
                    # Add target
                    if 'Survived' in df.columns:
                        df_processed['target'] = df['Survived']
                    
                    logger.info(f"✓ Preprocessed data: {len(df_processed):,} rows, {len(df_processed.columns)} columns")
                    return df_processed
                except Exception as e:
                    logger.warning(f"Failed to load raw Titanic data: {e}")
                    logger.info("Falling back to sample data generation...")
        
        # Generate sample data for local development (fallback)
        logger.info("Generating synthetic sample data...")
        return self._create_synthetic_dataset()
    
    def _create_synthetic_dataset(self, num_records=1000):
        """
        Create synthetic dataset for testing purposes
        
        Args:
            num_records: Number of samples to generate
            
        Returns:
            pandas.DataFrame: Synthetic dataset
        """
        logger.info(f"Generating {num_records:,} synthetic records...")
        
        # Set seed for reproducibility
        np.random.seed(self.config['training'].get('random_state', 42))
        
        # Build feature dictionary - create all features from config if available
        feature_columns = self.config.get('data', {}).get('features', [])
        synthetic_data = {}
        
        # Generate all configured features
        for i, feature in enumerate(feature_columns, 1):
            if feature not in synthetic_data:
                synthetic_data[feature] = np.random.randn(num_records)
        
        # If no features in config, create default features
        if not synthetic_data:
            for i in range(1, 9):  # Create feature1 through feature8
                synthetic_data[f'feature{i}'] = np.random.randn(num_records)
        
        # Add target column (use config target name or default to 'target')
        target_name = self.config.get('data', {}).get('target', 'target')
        synthetic_data[target_name] = np.random.randint(0, 2, num_records)
        
        dataset = pd.DataFrame(synthetic_data)
        logger.info(f"✓ Created synthetic dataset with shape: {dataset.shape}")
        
        return dataset
    
    def preprocess_data(self, df):
        """
        Prepare data for model training
        
        Performs data cleaning, feature extraction, train/test splitting,
        and feature scaling. This ensures data is in the right format
        for the ML algorithm.
        
        Args:
            df: Raw input dataframe
            
        Returns:
            tuple: (X_train_scaled, X_test_scaled, y_train, y_test, scaler)
        """
        logger.info("Starting data preprocessing pipeline...")
        
        # Get column names from configuration
        feature_columns = self.config['data']['features']
        target_column = self.config['data']['target']
        
        # Check if columns exist in dataframe
        logger.info(f"Dataframe columns: {list(df.columns)}")
        logger.info(f"Looking for features: {feature_columns}")
        logger.info(f"Looking for target: {target_column}")
        
        available_features = [f for f in feature_columns if f in df.columns]
        if len(available_features) < len(feature_columns):
            missing = set(feature_columns) - set(available_features)
            logger.warning(f"Some configured features not found in data: {missing}")
            logger.info(f"Using available features: {available_features}")
            feature_columns = available_features
        
        if target_column not in df.columns:
            logger.error(f"Target column '{target_column}' not found in data!")
            logger.info(f"Available columns: {list(df.columns)}")
            # Try to find alternative target column names
            possible_targets = ['target', 'target_column', 'Survived', 'survived', 'Target', 'TARGET', 'Target_Column']
            for alt_target in possible_targets:
                if alt_target in df.columns:
                    logger.info(f"Found alternative target column: '{alt_target}'")
                    logger.info(f"Updating target column to: '{alt_target}'")
                    target_column = alt_target
                    break
            else:
                raise ValueError(f"Target column '{self.config['data']['target']}' not found in dataframe. Available columns: {list(df.columns)}")
        
        logger.info(f"→ Features to use: {', '.join(feature_columns)}")
        logger.info(f"→ Target variable: {target_column}")
        
        # Data cleaning - remove any incomplete records
        initial_rows = len(df)
        df_clean = df.dropna()
        rows_removed = initial_rows - len(df_clean)
        
        if rows_removed > 0:
            logger.warning(f"Removed {rows_removed} rows with missing values")
        
        # Separate features from target
        X_features = df_clean[feature_columns]
        y_target = df_clean[target_column]
        
        # Configure train/test split parameters
        test_ratio = self.config['training']['test_size']
        seed_value = self.config['training']['random_state']
        
        logger.info(f"Splitting data: {int((1-test_ratio)*100)}% train, {int(test_ratio*100)}% test")
        
        # Perform train/test split
        # For regression (continuous target), don't use stratify
        # For classification (discrete target), use stratify
        is_classification = y_target.dtype in ['int64', 'int32', 'object'] and y_target.nunique() < 20
        
        if is_classification:
            logger.info("Detected classification task - using stratified split")
            X_train, X_test, y_train, y_test = train_test_split(
                X_features, 
                y_target, 
                test_size=test_ratio, 
                random_state=seed_value,
                stratify=y_target  # Keep same class proportions
            )
        else:
            logger.info("Detected regression task - using standard split")
            X_train, X_test, y_train, y_test = train_test_split(
                X_features, 
                y_target, 
                test_size=test_ratio, 
                random_state=seed_value
            )
        
        # Apply feature scaling (normalize to mean=0, std=1)
        # Important: fit on train only to avoid data leakage!
        feature_scaler = StandardScaler()
        X_train_normalized = feature_scaler.fit_transform(X_train)
        X_test_normalized = feature_scaler.transform(X_test)
        
        logger.info(f"✓ Preprocessing complete")
        logger.info(f"  Training samples: {len(X_train):,}")
        logger.info(f"  Testing samples: {len(X_test):,}")
        logger.info(f"  Features: {X_train.shape[1]}")
        
        return X_train_normalized, X_test_normalized, y_train, y_test, feature_scaler
    
    def train_model(self, X_train, y_train):
        """
        Build and train the machine learning model
        
        Uses cross-validation to assess model quality before
        training the final model on all training data.
        
        Args:
            X_train: Training features (scaled)
            y_train: Training labels
            
        Returns:
            tuple: (trained_model, cv_scores)
        """
        logger.info("Initiating model training...")
        
        # Extract hyperparameters from config
        model_params = self.config['model']['hyperparameters']
        algorithm_type = self.config['model'].get('algorithm', 'random_forest')
        
        logger.info(f"→ Algorithm: {algorithm_type}")
        logger.info(f"→ Parameters: {model_params}")
        
        # Create model instance with configured parameters
        ml_model = RandomForestClassifier(**model_params)
        
        # Validate model using k-fold cross-validation
        num_folds = self.config['training']['cv_folds']
        logger.info(f"Running {num_folds}-fold cross-validation...")
        
        validation_scores = cross_val_score(
            ml_model, 
            X_train, 
            y_train,
            cv=num_folds,
            scoring='accuracy',
            n_jobs=-1  # Use all CPU cores
        )
        
        # Calculate summary statistics
        mean_score = validation_scores.mean()
        std_score = validation_scores.std()
        
        logger.info(f"✓ Cross-validation results:")
        logger.info(f"  Individual fold scores: {[f'{score:.4f}' for score in validation_scores]}")
        logger.info(f"  Mean accuracy: {mean_score:.4f}")
        logger.info(f"  Std deviation: ±{std_score:.4f}")
        
        # Now train on complete training set
        logger.info("Training final model on full training data...")
        ml_model.fit(X_train, y_train)
        logger.info("✓ Model training complete")
        
        return ml_model, validation_scores
    
    def evaluate_model(self, model, X_test, y_test):
        """
        Assess model performance on held-out test data
        
        Computes multiple metrics to get a comprehensive view
        of model quality from different perspectives.
        
        Args:
            model: Trained ML model
            X_test: Test features
            y_test: True labels for test set
            
        Returns:
            dict: Performance metrics
        """
        logger.info("Running model evaluation on test set...")
        
        # Generate predictions
        predicted_labels = model.predict(X_test)
        predicted_probabilities = model.predict_proba(X_test)[:, 1]
        
        # Compute comprehensive metrics
        performance_metrics = {
            'accuracy': accuracy_score(y_test, predicted_labels),
            'precision': precision_score(y_test, predicted_labels, average='weighted', zero_division=0),
            'recall': recall_score(y_test, predicted_labels, average='weighted', zero_division=0),
            'f1_score': f1_score(y_test, predicted_labels, average='weighted', zero_division=0),
            'roc_auc': roc_auc_score(y_test, predicted_probabilities)
        }
        
        # Display results
        logger.info("✓ Evaluation complete - Performance Summary:")
        for metric_name, score in performance_metrics.items():
            # Format metric name for display
            display_name = metric_name.replace('_', ' ').title()
            logger.info(f"  • {display_name}: {score:.4f}")
        
        return performance_metrics
    
    def run_training_pipeline(self):
        """
        Execute the complete end-to-end training pipeline with comprehensive MLflow tracking
        
        This is the main orchestration method that coordinates all training steps:
        1. Data loading from configured source
        2. Data preprocessing and feature engineering
        3. Model training with cross-validation
        4. Model evaluation on test set
        5. Logging all artifacts and metrics to MLflow
        6. Registering model in Model Registry
        
        Returns:
            tuple: (run_id, metrics_dict)
                - run_id: Unique identifier for this MLflow run
                - metrics_dict: Dictionary containing all evaluation metrics
                
        Raises:
            Exception: If any step in the pipeline fails
            
        Example:
            >>> trainer = MLModelTrainer()
            >>> run_id, metrics = trainer.run_training_pipeline()
            >>> print(f"Accuracy: {metrics['accuracy']:.4f}")
        """
        # Start MLflow run context - automatically closes on completion or error
        with mlflow.start_run() as run:
            logger.info(f"Started MLflow run: {run.info.run_id}")
            
            # ===== STEP 1: Log Training Parameters =====
            # Record all hyperparameters for reproducibility
            mlflow.log_params(self.config['model']['hyperparameters'])
            mlflow.log_param("test_size", self.config['training']['test_size'])
            mlflow.log_param("cv_folds", self.config['training']['cv_folds'])
            
            # ===== STEP 2: Load and Preprocess Data =====
            # Fetch data from Databricks or generate synthetic data for local testing
            df = self.load_data()
            
            # Clean data, split into train/test, and normalize features
            # This prevents data leakage by fitting scaler only on training data
            X_train, X_test, y_train, y_test, scaler = self.preprocess_data(df)
            
            # ===== STEP 3: Train Model with Cross-Validation =====
            # Build and train the ML model, validating with k-fold CV
            model, cv_scores = self.train_model(X_train, y_train)
            
            # Log cross-validation results for model comparison
            # These metrics help identify overfitting before test evaluation
            mlflow.log_metric("cv_mean_accuracy", cv_scores.mean())
            mlflow.log_metric("cv_std_accuracy", cv_scores.std())
            
            # ===== STEP 4: Evaluate on Test Set =====
            # Assess final model performance on unseen test data
            metrics = self.evaluate_model(model, X_test, y_test)
            
            # Log all evaluation metrics to MLflow for tracking and comparison
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # ===== STEP 5: Log Model to MLflow and Register =====
            logger.info("Registering model in MLflow Model Registry...")

            registered_name = self.model_name  # e.g., workspace.default.gnu-mlops-model

            # Infer model signature for Unity Catalog (required)
            try:
                # Use training data to infer signature
                y_pred_sample = model.predict(X_train)
                signature = infer_signature(X_train, y_pred_sample)
                logger.info("Inferred model signature for Unity Catalog registration")
            except Exception as e:
                logger.warning(f"Could not infer signature automatically: {e}")
                signature = None

            model_info = mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                registered_model_name=registered_name,
                signature=signature  # UC requirement
            )


            # Get model version information after registration
            client = MlflowClient()
            try:
                # Get the latest version of the registered model
                registered_model = client.get_registered_model(self.model_name)
                latest_version = registered_model.latest_versions[-1] if registered_model.latest_versions else None
                
                if latest_version:
                    logger.info(f"✓ Model successfully registered!")
                    logger.info(f"  Model Name: {self.model_name}")
                    logger.info(f"  Version: {latest_version.version}")
                    logger.info(f"  Stage: {latest_version.current_stage}")
                    logger.info(f"  Run ID: {run.info.run_id}")
                    
                    # Add model description with training metrics
                    description = (
                        f"Model trained on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Accuracy: {metrics.get('accuracy', 0):.4f}\n"
                        f"F1 Score: {metrics.get('f1_score', 0):.4f}\n"
                        f"Run ID: {run.info.run_id}"
                    )
                    client.update_model_version(
                        name=self.model_name,
                        version=latest_version.version,
                        description=description
                    )
                    logger.info(f"  Description updated with training metrics")
            except Exception as e:
                logger.warning(f"Could not retrieve model version info: {e}")
                logger.info("Model was logged but version info unavailable")
            
            # ===== STEP 6: Log Preprocessing Artifacts =====
            # Save the feature scaler so predictions use the same normalization
            # Critical: Predictions must use the SAME scaler as training
            import joblib
            scaler_path = "scaler.pkl"
            joblib.dump(scaler, scaler_path)
            mlflow.log_artifact(scaler_path)  # Upload to MLflow
            os.remove(scaler_path)  # Clean up temporary file
            
            # ===== STEP 7: Log Configuration for Reproducibility =====
            # Save config file so we know exactly what settings were used
            # Only log if file exists (might not exist in all environments)
            config_file_path = Path('config.yaml')
            if config_file_path.exists():
                try:
                    mlflow.log_artifact(str(config_file_path))
                except Exception as e:
                    logger.warning(f"Could not log config file: {e}")
            
            # ===== STEP 8: Complete and Return Results =====
            logger.info(f"Model training completed. Run ID: {run.info.run_id}")
            logger.info(f"Model registered as: {self.model_name}")
            
            # Return run ID for tracking and metrics for evaluation
            return run.info.run_id, metrics


def main():
    """
    Main execution function for standalone script usage
    
    This function serves as the entry point when running the script directly.
    It handles initialization, execution, and error reporting.
    
    Workflow:
        1. Initialize the training pipeline
        2. Execute complete training workflow
        3. Display results to user
        4. Handle any errors gracefully
        
    Raises:
        Exception: Propagates any errors from training pipeline
    """
    print("Hello TEST")
    logger.info(f"Logging HELLO TEST")
    try:
        # Initialize trainer with default config
        # Will use config.local.yaml if it exists, otherwise config.yaml
        trainer = MLModelTrainer()
        
        # Run the complete training pipeline
        # This handles: data loading, preprocessing, training, evaluation, and logging
        run_id, metrics = trainer.run_training_pipeline()
        
        # ===== Display Success Message =====
        print("\n" + "="*50)
        print("Training Completed Successfully!")
        print("="*50)
        print(f"Run ID: {run_id}")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"F1 Score: {metrics['f1_score']:.4f}")
        print("="*50)
        
    except Exception as e:
        # Log error and re-raise for visibility
        logger.error(f"Training failed: {str(e)}")
        raise


# Script entry point - only executes if run directly (not when imported)
if __name__ == "__main__":
    main()

