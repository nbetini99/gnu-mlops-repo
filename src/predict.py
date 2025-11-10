"""
Model Prediction Script
Load and use deployed model for predictions
"""

import mlflow
import yaml
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelPredictor:
    """Load and use ML model for predictions"""
    
    def __init__(self, config_path='config.yaml', stage='Production'):
        """Initialize predictor with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set up MLflow
        mlflow.set_tracking_uri(self.config['mlflow']['tracking_uri'])
        self.model_name = self.config['mlflow']['model_name']
        self.stage = stage
        
        # Load model
        self.model = self._load_model()
        logger.info(f"Loaded {stage} model: {self.model_name}")
    
    def _load_model(self):
        """Load model from MLflow registry"""
        try:
            model_uri = f"models:/{self.model_name}/{self.stage}"
            model = mlflow.pyfunc.load_model(model_uri)
            logger.info(f"Successfully loaded model from {model_uri}")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def predict(self, data):
        """Make predictions on input data"""
        try:
            # Convert to DataFrame if necessary
            if isinstance(data, dict):
                data = pd.DataFrame([data])
            elif isinstance(data, np.ndarray):
                feature_cols = self.config['data']['features']
                data = pd.DataFrame(data, columns=feature_cols)
            
            # Make prediction
            predictions = self.model.predict(data)
            logger.info(f"Generated predictions for {len(data)} samples")
            
            return predictions
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
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
        """Make batch predictions from file"""
        logger.info(f"Loading data from {data_path}")
        
        # Load data
        if data_path.endswith('.csv'):
            data = pd.read_csv(data_path)
        elif data_path.endswith('.parquet'):
            data = pd.read_parquet(data_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or Parquet.")
        
        # Make predictions
        predictions = self.predict(data)
        
        # Add predictions to dataframe
        data['predictions'] = predictions
        
        # Save results
        if output_path:
            if output_path.endswith('.csv'):
                data.to_csv(output_path, index=False)
            elif output_path.endswith('.parquet'):
                data.to_parquet(output_path, index=False)
            logger.info(f"Predictions saved to {output_path}")
        
        return data


def main():
    """Main prediction function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Make predictions using deployed model')
    parser.add_argument(
        '--input',
        type=str,
        help='Input data file path (CSV or Parquet)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for predictions'
    )
    parser.add_argument(
        '--stage',
        type=str,
        default='Production',
        choices=['Staging', 'Production'],
        help='Model stage to use'
    )
    
    args = parser.parse_args()
    
    try:
        predictor = ModelPredictor(stage=args.stage)
        
        if args.input:
            # Batch prediction
            results = predictor.batch_predict(args.input, args.output)
            print(f"\n✓ Predictions completed for {len(results)} samples")
            print(f"\nSample predictions:")
            print(results[['predictions']].head())
        else:
            # Interactive mode - example
            print("\nModel loaded successfully!")
            print("Use predictor.predict(data) to make predictions")
    
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()

