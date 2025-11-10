"""
ML Model Training Script with MLflow Integration
This script trains a machine learning model using Databricks and MLflow
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLModelTrainer:
    """MLOps Model Training Pipeline"""
    
    def __init__(self, config_path='config.yaml'):
        """Initialize the trainer with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set up MLflow
        mlflow.set_tracking_uri(self.config['mlflow']['tracking_uri'])
        mlflow.set_experiment(self.config['mlflow']['experiment_name'])
        
        logger.info(f"Initialized trainer with experiment: {self.config['mlflow']['experiment_name']}")
    
    def load_data(self):
        """Load data from Databricks"""
        logger.info("Loading data from Databricks...")
        
        # For Databricks, you can use spark or databricks-sql-connector
        # Example using spark (when running on Databricks)
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()
            df = spark.table(self.config['data']['table_name']).toPandas()
            logger.info(f"Loaded {len(df)} rows from {self.config['data']['table_name']}")
            return df
        except Exception as e:
            logger.warning(f"Spark not available: {e}")
            # Fallback to sample data for local testing
            logger.info("Using sample data for demonstration")
            return self._generate_sample_data()
    
    def _generate_sample_data(self, n_samples=1000):
        """Generate sample data for testing"""
        np.random.seed(42)
        data = {
            'feature1': np.random.randn(n_samples),
            'feature2': np.random.randn(n_samples),
            'feature3': np.random.randn(n_samples),
            'target_column': np.random.randint(0, 2, n_samples)
        }
        return pd.DataFrame(data)
    
    def preprocess_data(self, df):
        """Preprocess the data"""
        logger.info("Preprocessing data...")
        
        # Extract features and target
        feature_cols = self.config['data']['features']
        target_col = self.config['data']['target']
        
        # Handle missing values
        df = df.dropna()
        
        X = df[feature_cols]
        y = df[target_col]
        
        # Split data
        test_size = self.config['training']['test_size']
        random_state = self.config['training']['random_state']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        logger.info(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")
        
        return X_train_scaled, X_test_scaled, y_train, y_test, scaler
    
    def train_model(self, X_train, y_train):
        """Train the ML model"""
        logger.info("Training model...")
        
        # Get model hyperparameters from config
        hyperparams = self.config['model']['hyperparameters']
        
        # Initialize model
        model = RandomForestClassifier(**hyperparams)
        
        # Perform cross-validation
        cv_scores = cross_val_score(
            model, X_train, y_train, 
            cv=self.config['training']['cv_folds'],
            scoring='accuracy'
        )
        
        logger.info(f"Cross-validation scores: {cv_scores}")
        logger.info(f"Mean CV score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Train final model
        model.fit(X_train, y_train)
        
        return model, cv_scores
    
    def evaluate_model(self, model, X_test, y_test):
        """Evaluate the trained model"""
        logger.info("Evaluating model...")
        
        # Make predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted'),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        logger.info("Model Metrics:")
        for metric_name, metric_value in metrics.items():
            logger.info(f"  {metric_name}: {metric_value:.4f}")
        
        return metrics
    
    def run_training_pipeline(self):
        """Execute the complete training pipeline with MLflow tracking"""
        
        with mlflow.start_run() as run:
            logger.info(f"Started MLflow run: {run.info.run_id}")
            
            # Log parameters
            mlflow.log_params(self.config['model']['hyperparameters'])
            mlflow.log_param("test_size", self.config['training']['test_size'])
            mlflow.log_param("cv_folds", self.config['training']['cv_folds'])
            
            # Load and preprocess data
            df = self.load_data()
            X_train, X_test, y_train, y_test, scaler = self.preprocess_data(df)
            
            # Train model
            model, cv_scores = self.train_model(X_train, y_train)
            
            # Log cross-validation metrics
            mlflow.log_metric("cv_mean_accuracy", cv_scores.mean())
            mlflow.log_metric("cv_std_accuracy", cv_scores.std())
            
            # Evaluate model
            metrics = self.evaluate_model(model, X_test, y_test)
            
            # Log evaluation metrics
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Log model
            mlflow.sklearn.log_model(
                model,
                "model",
                registered_model_name=self.config['mlflow']['model_name']
            )
            
            # Log scaler as artifact
            import joblib
            scaler_path = "scaler.pkl"
            joblib.dump(scaler, scaler_path)
            mlflow.log_artifact(scaler_path)
            os.remove(scaler_path)
            
            # Log config
            mlflow.log_artifact('config.yaml')
            
            logger.info(f"Model training completed. Run ID: {run.info.run_id}")
            logger.info(f"Model registered as: {self.config['mlflow']['model_name']}")
            
            return run.info.run_id, metrics


def main():
    """Main execution function"""
    try:
        trainer = MLModelTrainer()
        run_id, metrics = trainer.run_training_pipeline()
        
        print("\n" + "="*50)
        print("Training Completed Successfully!")
        print("="*50)
        print(f"Run ID: {run_id}")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"F1 Score: {metrics['f1_score']:.4f}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()

