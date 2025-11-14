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
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from databricks import sql
import logging
from pathlib import Path

# Setup logging with custom format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLModelTrainer:
    """
    Handles end-to-end model training workflow
    
    This class orchestrates the entire training process from data loading
    through model evaluation and registration. It integrates with MLflow
    for experiment tracking and model versioning.
    """
    
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
        
        # Initialize MLflow connection
        # Priority: environment variable > config file > default
        tracking_uri = os.getenv('MLFLOW_TRACKING_URI') or self.config.get('mlflow', {}).get('tracking_uri', 'sqlite:///mlflow.db')
        mlflow.set_tracking_uri(tracking_uri)
        
        # Set up experiment for organizing runs
        gnu_mlflow_config = self.config['mlflow']['gnu_mlflow_config']
        mlflow.set_experiment(gnu_mlflow_config)
        
        logger.info(f"Training pipeline initialized")
        logger.info(f"→ Experiment: {gnu_mlflow_config}")
        logger.info(f"→ Tracking: {tracking_uri}")
    
    def load_data(self):
        """
        Fetch training data from configured source
        
        Returns:
            pandas.DataFrame: Loaded dataset
        """
        data_source = self.config['data'].get('source', 'databricks')
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
                logger.info("Falling back to sample data generation...")
        
        # Generate sample data for local development
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
        
        # Build feature dictionary
        synthetic_data = {
            'feature1': np.random.randn(num_records),
            'feature2': np.random.randn(num_records), 
            'feature3': np.random.randn(num_records),
            'target_column': np.random.randint(0, 2, num_records)
        }
        
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
        
        # Perform stratified split to maintain class distribution
        X_train, X_test, y_train, y_test = train_test_split(
            X_features, 
            y_target, 
            test_size=test_ratio, 
            random_state=seed_value,
            stratify=y_target  # Keep same class proportions
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
            
            # ===== STEP 5: Log Model to MLflow =====
            # Save trained model in MLflow format
            # This automatically registers the model in Model Registry
            # The model can now be deployed to Staging or GNU_Production
            mlflow.sklearn.log_model(
                model,
                "model",
                registered_model_name=self.config['mlflow']['model_name']
            )
            
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
            mlflow.log_artifact('config.yaml')
            
            # ===== STEP 8: Complete and Return Results =====
            logger.info(f"Model training completed. Run ID: {run.info.run_id}")
            logger.info(f"Model registered as: {self.config['mlflow']['model_name']}")
            
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

