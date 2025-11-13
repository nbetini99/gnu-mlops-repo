"""
Model Deployment Script for Databricks
Automates model deployment to production
"""

import os
import yaml
import mlflow
from mlflow.tracking import MlflowClient
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelDeployment:
    """Automate model deployment to Databricks"""
    
    def __init__(self, config_path='config.yaml'):
        """Initialize deployment with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set up MLflow - Use environment variable if set, otherwise use config
        tracking_uri = os.getenv('MLFLOW_TRACKING_URI', self.config['mlflow']['tracking_uri'])
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()
        self.model_name = self.config['mlflow']['model_name']
        
        logger.info(f"Initialized deployment for model: {self.model_name}")
        logger.info(f"MLflow tracking URI: {tracking_uri}")
    
    def get_latest_model_version(self):
        """Get the latest version of the registered model"""
        try:
            latest_versions = self.client.get_latest_versions(
                self.model_name,
                stages=["None"]
            )
            if not latest_versions:
                raise ValueError(f"No model versions found for {self.model_name}")
            
            latest_version = latest_versions[0].version
            logger.info(f"Latest model version: {latest_version}")
            return latest_version
        except Exception as e:
            logger.error(f"Error getting latest model version: {str(e)}")
            raise
    
    def get_model_metrics(self, run_id):
        """Retrieve metrics for a specific model run"""
        try:
            run = self.client.get_run(run_id)
            metrics = run.data.metrics
            logger.info(f"Model metrics: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"Error retrieving metrics: {str(e)}")
            return {}
    
    def validate_model_performance(self, metrics, threshold=0.8):
        """Validate model meets performance thresholds"""
        accuracy = metrics.get('accuracy', 0)
        
        if accuracy >= threshold:
            logger.info(f"Model validation passed. Accuracy: {accuracy:.4f} >= {threshold}")
            return True
        else:
            logger.warning(f"Model validation failed. Accuracy: {accuracy:.4f} < {threshold}")
            return False
    
    def transition_model_stage(self, version, stage="GNU_Production"):
        """Transition model to a specific stage"""
        try:
            logger.info(f"Transitioning model version {version} to {stage}...")
            
            self.client.transition_model_version_stage(
                name=self.model_name,
                version=version,
                stage=stage,
                archive_existing_versions=True
            )
            
            logger.info(f"Successfully transitioned model to {stage} stage")
            return True
        except Exception as e:
            logger.error(f"Error transitioning model stage: {str(e)}")
            raise
    
    def add_model_description(self, version, description=None):
        """Add description to model version"""
        if description is None:
            description = f"Model deployed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            self.client.update_model_version(
                name=self.model_name,
                version=version,
                description=description
            )
            logger.info(f"Added description to model version {version}")
        except Exception as e:
            logger.warning(f"Could not add description: {str(e)}")
    
    def deploy_to_staging(self):
        """Deploy model to staging environment"""
        logger.info("Deploying model to Staging...")
        
        # Get latest model version
        version = self.get_latest_model_version()
        
        # Get model metrics
        model_version = self.client.get_model_version(self.model_name, version)
        run_id = model_version.run_id
        metrics = self.get_model_metrics(run_id)
        
        # Validate model
        if not self.validate_model_performance(metrics, threshold=0.7):
            logger.warning("Model did not meet staging threshold. Deployment aborted.")
            return False
        
        # Transition to staging
        self.transition_model_stage(version, "Staging")
        self.add_model_description(version, f"Deployed to Staging - Accuracy: {metrics.get('accuracy', 0):.4f}")
        
        logger.info(f"Model version {version} deployed to Staging")
        return version
    
    def deploy_to_production(self, version=None):
        """Deploy model to production environment"""
        logger.info("Deploying model to GNU_Production...")
        
        if version is None:
            # Get latest staging model
            staging_versions = self.client.get_latest_versions(
                self.model_name,
                stages=["Staging"]
            )
            if not staging_versions:
                logger.error("No model in Staging. Deploy to Staging first.")
                return False
            version = staging_versions[0].version
        
        # Get model metrics
        model_version = self.client.get_model_version(self.model_name, version)
        run_id = model_version.run_id
        metrics = self.get_model_metrics(run_id)
        
        # Validate model for production
        if not self.validate_model_performance(metrics, threshold=0.8):
            logger.error("Model did not meet production threshold. Deployment aborted.")
            return False
        
        # Transition to production
        self.transition_model_stage(version, "GNU_Production")
        self.add_model_description(
            version,
            f"Deployed to GNU_Production - Accuracy: {metrics.get('accuracy', 0):.4f} - {datetime.now()}"
        )
        
        logger.info(f"Model version {version} deployed to GNU_Production")
        return version
    
    def rollback_production(self, target_version=None):
        """Rollback production to a previous version"""
        logger.info("Rolling back production model...")
        
        try:
            if target_version:
                # Rollback to specific version
                self.transition_model_stage(target_version, "GNU_Production")
                logger.info(f"Rolled back to version {target_version}")
            else:
                # Get all production versions
                prod_versions = self.client.search_model_versions(
                    f"name='{self.model_name}'"
                )
                prod_versions = [v for v in prod_versions if v.current_stage == "GNU_Production"]
                
                if len(prod_versions) < 2:
                    logger.warning("No previous version available for rollback")
                    return False
                
                # Sort by version number and get second latest
                prod_versions.sort(key=lambda x: int(x.version), reverse=True)
                previous_version = prod_versions[1].version
                
                self.transition_model_stage(previous_version, "GNU_Production")
                logger.info(f"Rolled back to version {previous_version}")
            
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False
    
    def get_production_model_info(self):
        """Get information about current production model"""
        try:
            prod_versions = self.client.get_latest_versions(
                self.model_name,
                stages=["GNU_Production"]
            )
            
            if not prod_versions:
                logger.info("No model currently in GNU_Production")
                return None
            
            prod_model = prod_versions[0]
            info = {
                'version': prod_model.version,
                'run_id': prod_model.run_id,
                'status': prod_model.status,
                'description': prod_model.description
            }
            
            # Get metrics
            metrics = self.get_model_metrics(prod_model.run_id)
            info['metrics'] = metrics
            
            logger.info(f"Production Model Info: {info}")
            return info
        except Exception as e:
            logger.error(f"Error getting production model info: {str(e)}")
            return None


def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy ML Model to Databricks')
    parser.add_argument(
        '--stage',
        type=str,
        choices=['staging', 'production', 'info', 'rollback'],
        required=True,
        help='Deployment stage or action'
    )
    parser.add_argument(
        '--version',
        type=str,
        help='Specific model version to deploy (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        deployer = ModelDeployment()
        
        if args.stage == 'staging':
            version = deployer.deploy_to_staging()
            print(f"\n✓ Model version {version} deployed to Staging")
        
        elif args.stage == 'production':
            version = deployer.deploy_to_production(args.version)
            if version:
                print(f"\n✓ Model version {version} deployed to GNU_Production")
            else:
                print("\n✗ GNU_Production deployment failed")
        
        elif args.stage == 'info':
            info = deployer.get_production_model_info()
            if info:
                print("\n" + "="*50)
                print("GNU_Production Model Information")
                print("="*50)
                for key, value in info.items():
                    print(f"{key}: {value}")
                print("="*50)
        
        elif args.stage == 'rollback':
            success = deployer.rollback_production(args.version)
            if success:
                print("\n✓ GNU_Production model rolled back successfully")
            else:
                print("\n✗ Rollback failed")
    
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()

