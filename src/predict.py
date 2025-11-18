"""
Model Prediction Service
Author: Narsimha Betini
Purpose: Load deployed models and generate predictions on new data

This module provides prediction capabilities for deployed models:
- Load models from any stage (Staging or GNU_Production)
- Support multiple input formats (dict, array, DataFrame)
- Single and batch prediction modes
- File-based batch processing
- Flexible output options

The prediction service ensures:
- Consistent preprocessing (uses saved scaler)
- Production-ready inference
- Error handling and logging
- Support for real-time and batch predictions
"""

import os
import mlflow
import yaml
import pandas as pd
import numpy as np
import logging

# Configure logging for prediction operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelPredictor:
    """
    Model prediction service for loading and using deployed ML models
    
    This class provides a complete prediction interface that:
    - Loads models from MLflow Model Registry
    - Supports both Staging and GNU_Production stages
    - Handles multiple input formats (dict, numpy, pandas)
    - Provides single and batch prediction modes
    - Ensures consistent preprocessing with training
    
    Attributes:
        config (dict): Loaded configuration from YAML file
        model_name (str): Name of the model in Model Registry
        stage (str): Model stage to use (Staging or GNU_Production)
        model: Loaded MLflow model ready for predictions
        
    Typical Usage:
        # Load production model
        predictor = ModelPredictor(stage='GNU_Production')
        
        # Make prediction
        result = predictor.predict({'feature1': 45.5, 'feature2': 32000, 'feature3': 24})
    """
    
    def __init__(self, config_path='config.yaml', stage='GNU_Production'):
        """
        Initialize prediction service with model loading
        
        Loads configuration, connects to MLflow, and loads the specified
        model version for making predictions.
        
        Args:
            config_path (str): Path to YAML configuration file
                             Defaults to 'config.yaml'
            stage (str): Which model stage to use
                        Options: 'Staging' or 'GNU_Production'
                        Default: 'GNU_Production'
                        
        Raises:
            FileNotFoundError: If config file doesn't exist
            Exception: If model loading fails
            
        Example:
            >>> # Load production model
            >>> predictor = ModelPredictor(stage='GNU_Production')
            >>> 
            >>> # Load staging model for testing
            >>> test_predictor = ModelPredictor(stage='Staging')
        """
        # Load configuration from YAML file
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set up MLflow tracking connection with intelligent fallback
        # Check if Databricks credentials are available
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        force_databricks = os.getenv('FORCE_DATABRICKS') == 'true'
        databricks_host = os.getenv('DATABRICKS_HOST') or os.getenv('DATABRICKS_SERVER_HOSTNAME')
        databricks_token = os.getenv('DATABRICKS_TOKEN') or os.getenv('DATABRICKS_ACCESS_TOKEN')
        
        config_tracking_uri = self.config.get('mlflow', {}).get('tracking_uri', 'sqlite:///mlflow.db')
        env_tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
        
        # CRITICAL: Force SQLite in GitHub Actions (unless forced)
        if is_github_actions and not force_databricks:
            tracking_uri = 'sqlite:///mlflow.db'
            logger.info("=" * 70)
            logger.info("GitHub Actions detected - FORCING SQLite (Databricks disabled)")
            logger.info("To use Databricks in GitHub Actions, set FORCE_DATABRICKS=true")
            logger.info("=" * 70)
        elif env_tracking_uri and (env_tracking_uri.startswith('sqlite:///') or env_tracking_uri.startswith('file:///')):
            # If explicitly set to SQLite, use it
            tracking_uri = env_tracking_uri
        elif (env_tracking_uri == 'databricks' or config_tracking_uri == 'databricks') and (not is_github_actions or force_databricks):
            if databricks_host and databricks_token and databricks_token not in ['YOUR_TOKEN', 'YOUR_DATABRICKS_ACCESS_TOKEN_HERE', '']:
                tracking_uri = 'databricks'
                logger.info("Databricks credentials available, using Databricks MLflow tracking")
            else:
                logger.warning("Databricks tracking URI specified but credentials not available, using SQLite")
                tracking_uri = 'sqlite:///mlflow.db'
        elif env_tracking_uri:
            tracking_uri = env_tracking_uri
        else:
            tracking_uri = config_tracking_uri if config_tracking_uri != 'databricks' else 'sqlite:///mlflow.db'
        
        mlflow.set_tracking_uri(tracking_uri)
        
        # Store model information
        # Databricks requires three-part name: catalog.schema.model_name
        # SQLite uses simple name: model_name
        base_model_name = self.config['mlflow']['model_name']
        if tracking_uri == 'databricks':
            # Construct Databricks three-part model name
            # Try to get catalog and schema from config or environment, default to main.default
            catalog = self.config.get('databricks', {}).get('catalog', os.getenv('DATABRICKS_CATALOG', 'main'))
            schema = self.config.get('databricks', {}).get('schema', os.getenv('DATABRICKS_SCHEMA', 'default'))
            self.model_name = f"{catalog}.{schema}.{base_model_name}"
            logger.info(f"Using Databricks model name format: {self.model_name}")
        else:
            # Use simple name for SQLite/local
            self.model_name = base_model_name
        
        self.stage = stage
        
        # Load the model from MLflow Model Registry
        # This retrieves the model artifacts and makes it ready for predictions
        self.model = self._load_model()
        
        logger.info(f"Loaded {stage} model: {self.model_name}")
        logger.info(f"MLflow tracking URI: {tracking_uri}")
    
    def _load_model(self):
        """
        Load model from MLflow Model Registry
        
        Retrieves the model artifacts from MLflow for the specified stage.
        The model is loaded in MLflow's generic python_function format
        which works with any sklearn-compatible model.
        
        Returns:
            mlflow.pyfunc.PyFuncModel: Loaded model ready for predictions
            
        Raises:
            Exception: If model doesn't exist or loading fails
            
        Model URI Format:
            "models:/model_name/stage"
            Example: "models:/gnu-mlops-model/GNU_Production"
            
        Note:
            The model includes all necessary artifacts (scaler, preprocessor)
            that were logged during training.
        """
        try:
            # Map "GNU_Production" to "Production" for MLflow API
            # MLflow only accepts "Production" as a valid stage name, not "GNU_Production"
            mlflow_stage = "Production" if self.stage == "GNU_Production" else self.stage
            
            # Construct MLflow model URI
            # Format: models:/model_name/stage
            model_uri = f"models:/{self.model_name}/{mlflow_stage}"
            
            logger.info(f"Loading model from stage: {self.stage} (MLflow stage: {mlflow_stage})")
            
            # Load model from MLflow in generic python_function format
            # This format works with any sklearn-compatible model
            model = mlflow.pyfunc.load_model(model_uri)
            
            logger.info(f"Successfully loaded model from {model_uri}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.error(f"Make sure model is deployed to {self.stage} stage")
            raise
    
    def predict(self, data):
        """
        Generate predictions for input data
        
        Accepts data in multiple formats and returns predictions.
        Automatically handles format conversion and preprocessing.
        
        Args:
            data: Input data in one of these formats:
                - dict: Single prediction, e.g., {'feature1': 45.5, 'feature2': 32000, ...}
                - numpy.ndarray: Batch predictions, shape (n_samples, n_features)
                - pandas.DataFrame: Batch predictions with column names
                
        Returns:
            numpy.ndarray: Predictions array
                For binary classification: array of 0s and 1s
                Shape: (n_samples,)
                
        Raises:
            Exception: If prediction fails (wrong format, missing features, etc.)
            
        Examples:
            >>> # Single prediction with dict
            >>> result = predictor.predict({'feature1': 45.5, 'feature2': 32000, 'feature3': 24})
            >>> # Returns: array([0])
            >>> 
            >>> # Batch prediction with DataFrame
            >>> df = pd.DataFrame({'feature1': [45, 38], 'feature2': [32000, 45000], 'feature3': [24, 36]})
            >>> results = predictor.predict(df)
            >>> # Returns: array([0, 1])
        """
        try:
            # ===== Input Format Conversion =====
            # Convert various input formats to pandas DataFrame (model's expected format)
            
            if isinstance(data, dict):
                # Single prediction: convert dict to DataFrame with one row
                # Example: {'feature1': 45.5, ...} → DataFrame with 1 row
                data = pd.DataFrame([data])
                
            elif isinstance(data, np.ndarray):
                # Numpy array: add column names from config
                # This ensures features are properly labeled
                feature_cols = self.config['data']['features']
                data = pd.DataFrame(data, columns=feature_cols)
            
            # If already a DataFrame, use as-is
            
            # ===== Generate Predictions =====
            # Model automatically handles preprocessing (uses saved scaler)
            predictions = self.model.predict(data)
            
            logger.info(f"Generated predictions for {len(data)} samples")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            logger.error(f"Input data shape: {data.shape if hasattr(data, 'shape') else 'unknown'}")
            raise
    
    def predict_proba(self, data):
        """Get prediction probabilities"""
        try:
            # Note: Not all models support predict_proba
            predictions = self.model.predict(data)
            return predictions
        except Exception as e:
            logger.error(f"Prediction probability error: {str(e)}")
            raise
    
    def batch_predict(self, data_path, output_path=None):
        """
        Generate predictions for data in a file (batch processing)
        
        Reads data from CSV or Parquet file, generates predictions for all rows,
        and optionally saves results to an output file.
        
        Args:
            data_path (str): Path to input file
                           Supported formats: .csv, .parquet
            output_path (str, optional): Path to save predictions
                                        If None, results are returned but not saved
                                        Format determined by file extension
                                        
        Returns:
            pandas.DataFrame: Original data with added 'predictions' column
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If input file doesn't exist
            Exception: If prediction or file I/O fails
            
        Supported Formats:
            - CSV (.csv): Comma-separated values
            - Parquet (.parquet): Compressed columnar format
            
        Example:
            >>> # Predict on CSV file and save results
            >>> predictor.batch_predict(
            >>>     data_path='test_data.csv',
            >>>     output_path='predictions.csv'
            >>> )
            >>> 
            >>> # Predict without saving (get results as DataFrame)
            >>> results_df = predictor.batch_predict('test_data.csv')
            >>> print(results_df.head())
        """
        logger.info(f"Loading data from {data_path}")
        
        # ===== STEP 1: Load Input Data =====
        # Support both CSV and Parquet formats
        if data_path.endswith('.csv'):
            data = pd.read_csv(data_path)
        elif data_path.endswith('.parquet'):
            data = pd.read_parquet(data_path)
        else:
            raise ValueError(
                f"Unsupported file format: {data_path}. "
                "Please use CSV (.csv) or Parquet (.parquet) files."
            )
        
        # ===== STEP 2: Generate Predictions =====
        # Use the predict method which handles preprocessing
        predictions = self.predict(data)
        
        # ===== STEP 3: Add Predictions to DataFrame =====
        # Create new column with prediction results
        data['predictions'] = predictions
        
        # ===== STEP 4: Save Results (if output path provided) =====
        if output_path:
            # Save in the format specified by output file extension
            if output_path.endswith('.csv'):
                data.to_csv(output_path, index=False)
            elif output_path.endswith('.parquet'):
                data.to_parquet(output_path, index=False)
            else:
                # Default to CSV if extension not recognized
                data.to_csv(output_path, index=False)
                
            logger.info(f"Predictions saved to {output_path}")
        
        return data


def main():
    """
    Main prediction function for command-line usage
    
    Provides CLI interface for making predictions using deployed models.
    Supports both batch prediction from files and interactive mode.
    
    Command-line Arguments:
        --input: Optional. Path to input data file (CSV or Parquet)
        --output: Optional. Path to save predictions
        --stage: Optional. Model stage to use (default: GNU_Production)
        
    Usage Examples:
        # Batch predictions with file I/O
        python src/predict.py --input test.csv --output predictions.csv --stage GNU_Production
        
        # Predictions without saving (displays to console)
        python src/predict.py --input test.csv --stage Staging
        
        # Interactive mode (loads model, no predictions)
        python src/predict.py --stage GNU_Production
        
    Raises:
        Exception: If model loading or prediction fails
    """
    import argparse
    
    # ===== Parse Command Line Arguments =====
    parser = argparse.ArgumentParser(
        description='Make predictions using deployed ML model from MLflow'
    )
    
    # Optional: input data file
    parser.add_argument(
        '--input',
        type=str,
        help='Input data file path (CSV or Parquet format)'
    )
    
    # Optional: output file for predictions
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for predictions (will add predictions column)'
    )
    
    # Optional: which model stage to use
    parser.add_argument(
        '--stage',
        type=str,
        default='GNU_Production',
        choices=['Staging', 'GNU_Production'],
        help='Model stage to use for predictions (default: GNU_Production)'
    )
    
    args = parser.parse_args()
    
    try:
        # ===== Initialize Predictor =====
        # Load model from specified stage
        predictor = ModelPredictor(stage=args.stage)
        
        if args.input:
            # ===== MODE 1: Batch Prediction from File =====
            # Read input file, generate predictions, save results
            results = predictor.batch_predict(args.input, args.output)
            
            # Display summary
            print(f"\n✓ Predictions completed for {len(results)} samples")
            print(f"\nSample predictions (first 5):")
            print(results[['predictions']].head())
            
            if args.output:
                print(f"\n✓ Full results saved to: {args.output}")
                
        else:
            # ===== MODE 2: Interactive Mode =====
            # Model loaded but no predictions made yet
            # Useful for programmatic usage
            print("\n✓ Model loaded successfully!")
            print(f"   Stage: {args.stage}")
            print(f"   Model: {predictor.model_name}")
            print("\nTo make predictions:")
            print("  predictor.predict(your_data)")
            print("\nExample:")
            print("  data = {'feature1': 45.5, 'feature2': 32000, 'feature3': 24}")
            print("  prediction = predictor.predict(data)")
    
    except Exception as e:
        # Log error and re-raise for visibility
        logger.error(f"Prediction failed: {str(e)}")
        raise


# Script entry point - only executes if run directly (not when imported)
if __name__ == "__main__":
    main()

