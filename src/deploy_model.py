"""
Model Deployment Automation System
Author: Narsimha Betini
Purpose: Automated model lifecycle management with staged deployments

This module handles the complete model deployment workflow:
- Model validation against performance thresholds
- Staged deployments (None → Staging → GNU_Production)
- Version management and rollback capabilities
- Production model information and monitoring

The deployment follows a gated approach:
- Staging requires 70% accuracy minimum
- GNU_Production requires 80% accuracy minimum
- Automatic archiving of previous versions
- Quick rollback to previous versions if needed
"""

import os
import yaml
import mlflow
from mlflow.tracking import MlflowClient
import logging
from datetime import datetime

# Configure logging with consistent format
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelDeployment:
    """
    Automated model deployment system with stage management
    
    This class provides a complete deployment workflow for ML models with:
    - Performance-based validation gates
    - Multi-stage deployment (Staging → GNU_Production)
    - Version control and rollback capabilities
    - Model metadata management
    
    Attributes:
        config (dict): Loaded configuration from YAML file
        client (MlflowClient): MLflow client for model operations
        model_name (str): Name of the model in Model Registry
        
    Stage Flow:
        None (newly registered)
          ↓ (70% accuracy threshold)
        Staging (testing environment)
          ↓ (80% accuracy threshold)
        GNU_Production (live serving)
          ↓ (if issues detected)
        Rollback available
    """
    
    def __init__(self, config_path='config.yaml'):
        """
        Initialize deployment system with configuration
        
        Sets up MLflow connection and prepares deployment infrastructure.
        Uses environment variables for flexibility and security.
        
        Args:
            config_path (str): Path to YAML configuration file
                             Defaults to 'config.yaml'
                             
        Raises:
            FileNotFoundError: If config file doesn't exist
            KeyError: If required config keys are missing
        """
        # Load configuration from YAML
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set up MLflow tracking connection
        # Priority: Environment variable > config file value
        # This allows overriding config for different environments
        tracking_uri = os.getenv('MLFLOW_TRACKING_URI', self.config['mlflow']['tracking_uri'])
        mlflow.set_tracking_uri(tracking_uri)
        
        # Initialize MLflow client for model registry operations
        self.client = MlflowClient()
        
        # Store model name for all deployment operations
        self.model_name = self.config['mlflow']['model_name']
        
        logger.info(f"Initialized deployment for model: {self.model_name}")
        logger.info(f"MLflow tracking URI: {tracking_uri}")
    
    def get_latest_model_version(self):
        """
        Retrieve the most recent registered model version
        
        Queries MLflow Model Registry for the latest version in "None" stage.
        Models in "None" stage are newly registered and haven't been promoted yet.
        
        Returns:
            str: Version number of the latest model (e.g., "3")
            
        Raises:
            ValueError: If no model versions exist
            Exception: If MLflow query fails
            
        Note:
            Only looks at models in "None" stage - models already in
            Staging or GNU_Production are not considered.
        """
        try:
            # Query MLflow for latest versions in "None" stage
            # "None" stage means newly registered, not yet promoted
            latest_versions = self.client.get_latest_versions(
                self.model_name,
                stages=["None"]
            )
            
            # Validate that at least one version exists
            if not latest_versions:
                raise ValueError(f"No model versions found for {self.model_name}")
            
            # Extract version number from the result
            latest_version = latest_versions[0].version
            logger.info(f"Latest model version: {latest_version}")
            
            return latest_version
            
        except Exception as e:
            logger.error(f"Error getting latest model version: {str(e)}")
            raise
    
    def get_model_metrics(self, run_id):
        """
        Retrieve performance metrics for a specific training run
        
        Fetches all logged metrics from MLflow for the specified run.
        These metrics are used to validate model performance before deployment.
        
        Args:
            run_id (str): Unique identifier for the MLflow run
            
        Returns:
            dict: Dictionary of metric names and values
                  e.g., {'accuracy': 0.85, 'f1_score': 0.83, ...}
                  Returns empty dict if retrieval fails
                  
        Example:
            >>> metrics = deployer.get_model_metrics('abc123def456')
            >>> print(f"Accuracy: {metrics['accuracy']:.4f}")
        """
        try:
            # Fetch the complete run data from MLflow
            run = self.client.get_run(run_id)
            
            # Extract just the metrics portion
            metrics = run.data.metrics
            
            logger.info(f"Model metrics: {metrics}")
            return metrics
            
        except Exception as e:
            # Log error but don't crash - return empty dict for graceful handling
            logger.error(f"Error retrieving metrics: {str(e)}")
            return {}
    
    def validate_model_performance(self, metrics, threshold=0.8):
        """
        Validate that model meets minimum performance requirements
        
        This is a quality gate that prevents underperforming models from
        being deployed to production environments. Different thresholds
        are used for different stages:
        - Staging: 70% accuracy (lower bar for testing)
        - GNU_Production: 80% accuracy (higher bar for live serving)
        
        Args:
            metrics (dict): Dictionary of model performance metrics
            threshold (float): Minimum accuracy required (0.0 to 1.0)
                             Default is 0.8 (80%)
                             
        Returns:
            bool: True if model passes validation, False otherwise
            
        Example:
            >>> metrics = {'accuracy': 0.85, 'f1_score': 0.83}
            >>> is_valid = deployer.validate_model_performance(metrics, 0.8)
            >>> # Returns: True (0.85 >= 0.8)
        """
        # Extract accuracy from metrics, default to 0 if not found
        accuracy = metrics.get('accuracy', 0)
        
        # Compare against threshold
        if accuracy >= threshold:
            logger.info(f"Model validation passed. Accuracy: {accuracy:.4f} >= {threshold}")
            return True
        else:
            logger.warning(f"Model validation failed. Accuracy: {accuracy:.4f} < {threshold}")
            return False
    
    def transition_model_stage(self, version, stage="GNU_Production"):
        """
        Move a model version to a different deployment stage
        
        Transitions a specific model version to the requested stage in the
        Model Registry. Automatically archives any existing models in that stage.
        
        Args:
            version (str/int): Model version number to transition
            stage (str): Target stage name. Options:
                        - "Staging": For testing and validation
                        - "GNU_Production": For live production serving
                        Default is "GNU_Production"
                        
        Returns:
            bool: True if transition successful
            
        Raises:
            Exception: If transition fails (permissions, invalid stage, etc.)
            
        Note:
            archive_existing_versions=True means if version 3 is in GNU_Production
            and you promote version 4, version 3 automatically moves to Archived.
            This ensures only one model is in each stage at a time.
            
        Example:
            >>> deployer.transition_model_stage(version=3, stage="Staging")
            >>> # Version 3 is now in Staging, ready for testing
        """
        try:
            logger.info(f"Transitioning model version {version} to {stage}...")
            
            # Perform the stage transition in MLflow Model Registry
            # archive_existing_versions=True automatically archives previous versions
            self.client.transition_model_version_stage(
                name=self.model_name,
                version=version,
                stage=stage,
                archive_existing_versions=True  # Archive previous versions in this stage
            )
            
            logger.info(f"Successfully transitioned model to {stage} stage")
            return True
            
        except Exception as e:
            logger.error(f"Error transitioning model stage: {str(e)}")
            raise
    
    def add_model_description(self, version, description=None):
        """
        Add or update descriptive metadata for a model version
        
        Attaches human-readable description to a model version for documentation.
        Useful for tracking deployment history, performance notes, and decisions.
        
        Args:
            version (str/int): Model version number
            description (str, optional): Description text to add
                                        If None, generates timestamp-based description
                                        
        Example descriptions:
            - "Deployed to Staging - Accuracy: 0.87"
            - "Deployed to GNU_Production - Accuracy: 0.92 - 2025-11-12"
            - "Rollback from v4 due to performance issues"
            
        Returns:
            None
            
        Note:
            Failures are logged but don't crash the deployment process.
            Description is metadata only, doesn't affect model functionality.
        """
        # Generate default description if none provided
        if description is None:
            description = f"Model deployed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            # Update the model version metadata in MLflow
            self.client.update_model_version(
                name=self.model_name,
                version=version,
                description=description
            )
            logger.info(f"Added description to model version {version}")
            
        except Exception as e:
            # Log warning but don't fail deployment if description update fails
            logger.warning(f"Could not add description: {str(e)}")
    
    def deploy_to_staging(self):
        """
        Deploy latest model to Staging environment with validation
        
        Staging deployment workflow:
        1. Get the most recent model version from Model Registry
        2. Retrieve performance metrics from the training run
        3. Validate model meets 70% accuracy threshold
        4. If valid, promote to Staging stage
        5. Add deployment metadata for tracking
        
        Staging is the testing environment where models are validated
        before being promoted to GNU_Production.
        
        Returns:
            int/str: Version number if deployment successful
            bool: False if validation fails
            
        Validation Threshold:
            - Minimum accuracy: 70%
            - Purpose: Basic quality gate for testing
            - Lower than production (80%) to allow experimentation
            
        Example:
            >>> deployer = ModelDeployment()
            >>> version = deployer.deploy_to_staging()
            >>> print(f"Deployed version {version} to Staging")
        """
        logger.info("Deploying model to Staging...")
        
        # ===== STEP 1: Get Latest Model Version =====
        # Find the most recent model in "None" stage (newly trained)
        version = self.get_latest_model_version()
        
        # ===== STEP 2: Retrieve Model Metrics =====
        # Get the MLflow run ID associated with this model version
        model_version = self.client.get_model_version(self.model_name, version)
        run_id = model_version.run_id
        
        # Fetch all metrics from the training run
        metrics = self.get_model_metrics(run_id)
        
        # ===== STEP 3: Validate Performance =====
        # Check if model meets minimum 70% accuracy for Staging
        # This prevents completely broken models from being deployed
        if not self.validate_model_performance(metrics, threshold=0.7):
            logger.warning("Model did not meet staging threshold. Deployment aborted.")
            return False
        
        # ===== STEP 4: Transition to Staging Stage =====
        # Promote model to Staging environment
        self.transition_model_stage(version, "Staging")
        
        # ===== STEP 5: Add Deployment Metadata =====
        # Record deployment information for audit trail
        self.add_model_description(
            version, 
            f"Deployed to Staging - Accuracy: {metrics.get('accuracy', 0):.4f}"
        )
        
        logger.info(f"Model version {version} deployed to Staging")
        return version
    
    def deploy_to_production(self, version=None):
        """
        Deploy model to GNU_Production environment with strict validation
        
        Production deployment workflow:
        1. Get model from Staging (or specific version if provided)
        2. Retrieve and validate performance metrics
        3. Validate model meets 80% accuracy threshold (stricter than Staging)
        4. If valid, promote to GNU_Production stage
        5. Archive previous production version
        6. Add deployment metadata with timestamp
        
        GNU_Production is the live serving environment. Only high-quality
        models that have been tested in Staging should be promoted here.
        
        Args:
            version (str/int, optional): Specific version to deploy
                                        If None, uses latest Staging model
                                        
        Returns:
            int/str: Version number if deployment successful
            bool: False if validation fails or no Staging model exists
            
        Validation Threshold:
            - Minimum accuracy: 80%
            - Purpose: Ensure high quality for production serving
            - Higher than Staging (70%) for additional safety
            
        Best Practice:
            Always test in Staging first, then promote the same version
            to GNU_Production. Don't skip Staging!
            
        Example:
            >>> # Deploy latest Staging model to production
            >>> version = deployer.deploy_to_production()
            >>> 
            >>> # Or deploy specific version
            >>> version = deployer.deploy_to_production(version=5)
        """
        logger.info("Deploying model to GNU_Production...")
        
        # ===== STEP 1: Determine Which Version to Deploy =====
        if version is None:
            # No version specified - get the current Staging model
            # This is the recommended path: Staging → Production
            staging_versions = self.client.get_latest_versions(
                self.model_name,
                stages=["Staging"]
            )
            
            # Ensure a model exists in Staging
            if not staging_versions:
                logger.error("No model in Staging. Deploy to Staging first.")
                return False
                
            # Use the Staging model version
            version = staging_versions[0].version
        
        # ===== STEP 2: Retrieve Model Metrics =====
        # Get the training run information for this version
        model_version = self.client.get_model_version(self.model_name, version)
        run_id = model_version.run_id
        metrics = self.get_model_metrics(run_id)
        
        # ===== STEP 3: Validate for Production =====
        # Stricter threshold (80%) for production vs staging (70%)
        # This ensures only high-quality models make it to production
        if not self.validate_model_performance(metrics, threshold=0.8):
            logger.error("Model did not meet production threshold. Deployment aborted.")
            return False
        
        # ===== STEP 4: Transition to GNU_Production =====
        # Promote model to production stage
        # Previous production version is automatically archived
        self.transition_model_stage(version, "GNU_Production")
        
        # ===== STEP 5: Add Deployment Metadata =====
        # Record deployment details including timestamp and performance
        self.add_model_description(
            version,
            f"Deployed to GNU_Production - Accuracy: {metrics.get('accuracy', 0):.4f} - {datetime.now()}"
        )
        
        logger.info(f"Model version {version} deployed to GNU_Production")
        return version
    
    def rollback_production(self, target_version=None):
        """
        Rollback GNU_Production to a previous model version
        
        Emergency rollback functionality for quickly reverting to a previous
        known-good model version if issues are detected in production.
        
        Two rollback modes:
        1. Automatic: Rolls back to the previous production version
        2. Manual: Rolls back to a specific version number
        
        Args:
            target_version (str/int, optional): Specific version to rollback to
                                               If None, automatically finds previous version
                                               
        Returns:
            bool: True if rollback successful, False if failed or no previous version
            
        Raises:
            Exception: If rollback operation fails
            
        Use Cases:
            - Production model has bugs or errors
            - Performance degradation detected
            - User complaints after deployment
            - Need to quickly revert while fixing issues
            
        Example:
            >>> # Automatic rollback to previous version
            >>> deployer.rollback_production()
            >>> 
            >>> # Rollback to specific version
            >>> deployer.rollback_production(target_version=5)
        """
        logger.info("Rolling back production model...")
        
        try:
            if target_version:
                # ===== MODE 1: Rollback to Specific Version =====
                # User specified exactly which version to rollback to
                self.transition_model_stage(target_version, "GNU_Production")
                logger.info(f"Rolled back to version {target_version}")
                
            else:
                # ===== MODE 2: Automatic Rollback to Previous =====
                # Find all versions that have been in GNU_Production
                prod_versions = self.client.search_model_versions(
                    f"name='{self.model_name}'"
                )
                
                # Filter to only versions currently in GNU_Production
                prod_versions = [v for v in prod_versions if v.current_stage == "GNU_Production"]
                
                # Check if we have a previous version to rollback to
                if len(prod_versions) < 2:
                    logger.warning("No previous version available for rollback")
                    return False
                
                # Sort versions by number (highest first) and get second one
                # Example: [v7, v6, v5] → choose v6 (previous production)
                prod_versions.sort(key=lambda x: int(x.version), reverse=True)
                previous_version = prod_versions[1].version
                
                # Transition previous version back to GNU_Production
                self.transition_model_stage(previous_version, "GNU_Production")
                logger.info(f"Rolled back to version {previous_version}")
            
            return True
            
        except Exception as e:
            # Log error but return False instead of crashing
            logger.error(f"Rollback failed: {str(e)}")
            return False
    
    def get_production_model_info(self):
        """
        Retrieve detailed information about the current production model
        
        Fetches comprehensive details about the model currently serving
        in GNU_Production stage, including version, performance metrics,
        and deployment metadata.
        
        Returns:
            dict: Model information dictionary with keys:
                - version: Model version number
                - run_id: MLflow run identifier
                - status: Model status (READY, PENDING_REGISTRATION, etc.)
                - description: Deployment notes and metadata
                - metrics: Performance metrics from training
                
            None: If no model is in GNU_Production stage
            
        Use Cases:
            - Check which model is currently in production
            - Verify production model performance
            - Monitor deployment status
            - Audit trail and compliance
            
        Example:
            >>> info = deployer.get_production_model_info()
            >>> if info:
            >>>     print(f"Production: Version {info['version']}")
            >>>     print(f"Accuracy: {info['metrics']['accuracy']:.4f}")
        """
        try:
            # Query MLflow for models in GNU_Production stage
            prod_versions = self.client.get_latest_versions(
                self.model_name,
                stages=["GNU_Production"]
            )
            
            # Check if any model is deployed to production
            if not prod_versions:
                logger.info("No model currently in GNU_Production")
                return None
            
            # Get the production model details
            prod_model = prod_versions[0]
            
            # Build information dictionary
            info = {
                'version': prod_model.version,
                'run_id': prod_model.run_id,
                'status': prod_model.status,
                'description': prod_model.description
            }
            
            # Fetch and add performance metrics from the training run
            # This shows how well the production model performed during training
            metrics = self.get_model_metrics(prod_model.run_id)
            info['metrics'] = metrics
            
            logger.info(f"GNU_Production Model Info: {info}")
            return info
            
        except Exception as e:
            # Log error and return None for graceful handling
            logger.error(f"Error getting production model info: {str(e)}")
            return None


def main():
    """
    Main deployment function for command-line usage
    
    Provides CLI interface for model deployment operations:
    - staging: Deploy latest model to Staging environment
    - production: Deploy Staging model to GNU_Production
    - info: Display current production model information
    - rollback: Revert production to previous version
    
    Command-line Arguments:
        --stage: Required. One of [staging, production, info, rollback]
        --version: Optional. Specific model version number
        
    Usage Examples:
        python src/deploy_model.py --stage staging
        python src/deploy_model.py --stage production
        python src/deploy_model.py --stage production --version 5
        python src/deploy_model.py --stage info
        python src/deploy_model.py --stage rollback
        python src/deploy_model.py --stage rollback --version 3
        
    Raises:
        Exception: If deployment operation fails
    """
    import argparse
    
    # ===== Parse Command Line Arguments =====
    parser = argparse.ArgumentParser(
        description='Deploy ML Model to Databricks with stage management'
    )
    
    # Required: deployment action/stage
    parser.add_argument(
        '--stage',
        type=str,
        choices=['staging', 'production', 'info', 'rollback'],
        required=True,
        help='Deployment stage or action to perform'
    )
    
    # Optional: specific version number
    parser.add_argument(
        '--version',
        type=str,
        help='Specific model version to deploy (optional, uses latest if not specified)'
    )
    
    args = parser.parse_args()
    
    try:
        # ===== Initialize Deployment System =====
        deployer = ModelDeployment()
        
        # ===== Execute Requested Action =====
        
        if args.stage == 'staging':
            # Deploy latest model to Staging environment
            # Validates model meets 70% accuracy threshold
            version = deployer.deploy_to_staging()
            print(f"\n✓ Model version {version} deployed to Staging")
        
        elif args.stage == 'production':
            # Deploy to GNU_Production (from Staging or specific version)
            # Validates model meets 80% accuracy threshold
            version = deployer.deploy_to_production(args.version)
            
            if version:
                print(f"\n✓ Model version {version} deployed to GNU_Production")
            else:
                print("\n✗ GNU_Production deployment failed")
                print("   Possible reasons:")
                print("   - Model accuracy < 80%")
                print("   - No model in Staging")
                print("   - Specified version doesn't exist")
        
        elif args.stage == 'info':
            # Display current production model information
            # Shows version, metrics, status, and metadata
            info = deployer.get_production_model_info()
            
            if info:
                print("\n" + "="*50)
                print("GNU_Production Model Information")
                print("="*50)
                for key, value in info.items():
                    print(f"{key}: {value}")
                print("="*50)
            else:
                print("\n⚠ No model currently in GNU_Production")
                print("  Deploy a model first with: --stage production")
        
        elif args.stage == 'rollback':
            # Rollback production to previous version
            # Can specify version or auto-rollback to previous
            success = deployer.rollback_production(args.version)
            
            if success:
                print("\n✓ GNU_Production model rolled back successfully")
            else:
                print("\n✗ Rollback failed")
                print("   Possible reasons:")
                print("   - No previous version available")
                print("   - Specified version doesn't exist")
    
    except Exception as e:
        # Log error and re-raise for visibility
        logger.error(f"Deployment failed: {str(e)}")
        raise


# Script entry point - only executes if run directly
if __name__ == "__main__":
    main()

