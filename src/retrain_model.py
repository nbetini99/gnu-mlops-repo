"""
Automatic Model Retraining System
Author: Narsimha Betini
Purpose: Scheduled retraining every 30 days with automatic deployment

This module provides automated retraining capabilities:
- Checks if retraining is needed (30 days since last training)
- Trains new model with latest data
- Compares performance with current production model
- Auto-deploys if new model is better
- Sends notifications on completion
- Logs all retraining activities

The retraining workflow:
1. Check if 30 days have passed since last training
2. Load latest data from configured source
3. Train new model
4. Compare with current production model
5. Deploy to Staging if meets threshold
6. Deploy to Production if better than current production
7. Send notification email (if configured)
"""

import os
import sys
import yaml
import mlflow
from mlflow.tracking import MlflowClient
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json

# Import existing modules
from train_model import MLModelTrainer
from deploy_model import ModelDeployment

# Setup logging with file output for scheduled runs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"retraining_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AutomaticRetrainer:
    """
    Automated model retraining system with scheduling and safety checks
    
    This class manages the complete retraining lifecycle:
    - Checks if retraining is needed based on schedule
    - Trains new models with latest data
    - Compares performance with production
    - Auto-deploys better models
    - Maintains retraining history
    
    Attributes:
        config (dict): Loaded configuration from YAML file
        client (MlflowClient): MLflow client for model operations
        model_name (str): Name of the model in Model Registry
        retrain_interval_days (int): Days between retraining (default: 30)
        auto_deploy (bool): Whether to auto-deploy better models
        
    Typical Usage:
        retrainer = AutomaticRetrainer()
        if retrainer.should_retrain():
            retrainer.retrain_and_deploy()
    """
    
    def __init__(self, config_path='config.yaml'):
        """
        Initialize retraining system with configuration
        
        Loads configuration and sets up MLflow connection for
        checking model versions and training history.
        
        Args:
            config_path (str): Path to YAML configuration file
                             Defaults to 'config.yaml'
                             
        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        # Load configuration
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set up MLflow connection
        tracking_uri = os.getenv('MLFLOW_TRACKING_URI') or self.config.get('mlflow', {}).get('tracking_uri', 'sqlite:///mlflow.db')
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()
        
        # Get model name
        self.model_name = self.config['mlflow']['model_name']
        
        # Get retraining configuration
        retrain_config = self.config.get('retraining', {})
        self.retrain_interval_days = retrain_config.get('interval_days', 30)
        self.auto_deploy = retrain_config.get('auto_deploy', True)
        self.min_improvement = retrain_config.get('min_improvement', 0.0)  # Minimum improvement to deploy
        self.notification_email = retrain_config.get('notification_email', None)
        
        logger.info(f"Retraining system initialized")
        logger.info(f"→ Model: {self.model_name}")
        logger.info(f"→ Interval: {self.retrain_interval_days} days")
        logger.info(f"→ Auto-deploy: {self.auto_deploy}")
    
    def get_last_training_date(self):
        """
        Get the date of the last successful training run
        
        Queries MLflow to find the most recent model version and
        extracts the training timestamp from the run metadata.
        
        Returns:
            datetime: Date of last training, or None if no models exist
            
        Note:
            Returns None if this is the first training (no models exist yet)
        """
        try:
            # Get all model versions
            model_versions = self.client.search_model_versions(f"name='{self.model_name}'")
            
            if not model_versions:
                logger.info("No previous models found - first training")
                return None
            
            # Find the most recent version by version number
            latest_version = max(model_versions, key=lambda v: int(v.version))
            
            # Get the run associated with this version
            run = self.client.get_run(latest_version.run_id)
            
            # Extract timestamp (MLflow stores as milliseconds)
            timestamp_ms = run.info.start_time
            last_training_date = datetime.fromtimestamp(timestamp_ms / 1000.0)
            
            logger.info(f"Last training date: {last_training_date.strftime('%Y-%m-%d %H:%M:%S')}")
            return last_training_date
            
        except Exception as e:
            logger.warning(f"Could not determine last training date: {str(e)}")
            return None
    
    def should_retrain(self):
        """
        Check if retraining is needed based on schedule
        
        Compares the last training date with the current date and
        the configured retraining interval.
        
        Returns:
            bool: True if retraining is needed, False otherwise
            
        Logic:
            - If no previous training exists → retrain
            - If last training was >= interval_days ago → retrain
            - Otherwise → don't retrain yet
        """
        last_training = self.get_last_training_date()
        
        if last_training is None:
            logger.info("✓ Retraining needed: No previous training found")
            return True
        
        # Calculate days since last training
        days_since_training = (datetime.now() - last_training).days
        
        logger.info(f"Days since last training: {days_since_training}")
        logger.info(f"Retraining interval: {self.retrain_interval_days} days")
        
        if days_since_training >= self.retrain_interval_days:
            logger.info(f"✓ Retraining needed: {days_since_training} days >= {self.retrain_interval_days} days")
            return True
        else:
            days_remaining = self.retrain_interval_days - days_since_training
            logger.info(f"✗ Retraining not needed: {days_remaining} days remaining")
            return False
    
    def get_production_metrics(self):
        """
        Get performance metrics of current production model
        
        Retrieves the model currently in GNU_Production stage and
        fetches its training metrics for comparison.
        
        Returns:
            dict: Production model metrics, or None if no production model
            
        Example:
            {'accuracy': 0.85, 'f1_score': 0.83, 'precision': 0.82, ...}
        """
        try:
            # Get production model
            prod_versions = self.client.get_latest_versions(
                self.model_name,
                stages=["GNU_Production"]
            )
            
            if not prod_versions:
                logger.info("No model in GNU_Production - will deploy first model")
                return None
            
            # Get metrics from the production model's training run
            prod_model = prod_versions[0]
            run = self.client.get_run(prod_model.run_id)
            metrics = run.data.metrics
            
            logger.info(f"Production model metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.warning(f"Could not get production metrics: {str(e)}")
            return None
    
    def compare_models(self, new_metrics, production_metrics):
        """
        Compare new model performance with production model
        
        Determines if the new model is better than production based on
        accuracy and minimum improvement threshold.
        
        Args:
            new_metrics (dict): Metrics from newly trained model
            production_metrics (dict): Metrics from current production model
            
        Returns:
            tuple: (is_better (bool), improvement (float))
                   - is_better: True if new model should replace production
                   - improvement: Accuracy improvement percentage
                   
        Comparison Logic:
            - If no production model exists → new model is better
            - If new accuracy > production accuracy + min_improvement → better
            - Otherwise → keep production model
        """
        if production_metrics is None:
            logger.info("No production model exists - new model will be deployed")
            return True, 0.0
        
        new_accuracy = new_metrics.get('accuracy', 0.0)
        prod_accuracy = production_metrics.get('accuracy', 0.0)
        
        improvement = new_accuracy - prod_accuracy
        required_improvement = self.min_improvement
        
        logger.info(f"Model Comparison:")
        logger.info(f"  Production accuracy: {prod_accuracy:.4f}")
        logger.info(f"  New model accuracy: {new_accuracy:.4f}")
        logger.info(f"  Improvement: {improvement:+.4f}")
        logger.info(f"  Required improvement: {required_improvement:.4f}")
        
        if improvement >= required_improvement:
            logger.info(f"✓ New model is better (improvement: {improvement:.4f} >= {required_improvement:.4f})")
            return True, improvement
        else:
            logger.warning(f"✗ New model is not better (improvement: {improvement:.4f} < {required_improvement:.4f})")
            logger.warning(f"  Keeping production model")
            return False, improvement
    
    def send_notification(self, subject, message):
        """
        Send notification email about retraining status
        
        Sends email notification if email is configured in config.
        Uses system's mail command (works on macOS/Linux).
        
        Args:
            subject (str): Email subject line
            message (str): Email body content
            
        Note:
            Requires email to be configured in retraining.notification_email
            Uses system mail command - may need mail server configuration
        """
        if not self.notification_email:
            logger.info("No notification email configured - skipping email")
            return
        
        try:
            import subprocess
            
            # Create email content
            email_content = f"""Subject: {subject}

{message}

---
GNU MLOps Retraining System
Automated retraining completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # Send email using system mail command
            process = subprocess.Popen(
                ['mail', '-s', subject, self.notification_email],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            process.communicate(input=email_content.encode())
            
            logger.info(f"Notification email sent to {self.notification_email}")
            
        except Exception as e:
            logger.warning(f"Could not send notification email: {str(e)}")
            logger.warning("Email notification requires mail server configuration")
    
    def retrain_and_deploy(self, force=False):
        """
        Execute complete retraining and deployment workflow
        
        Main orchestration method that:
        1. Checks if retraining is needed (unless forced)
        2. Trains new model with latest data
        3. Compares with production model
        4. Deploys if better (if auto_deploy enabled)
        5. Sends notifications
        
        Args:
            force (bool): Force retraining even if not scheduled
                         Default: False
                         
        Returns:
            dict: Retraining results with status, metrics, and deployment info
            
        Raises:
            Exception: If any step in the workflow fails
            
        Example:
            >>> retrainer = AutomaticRetrainer()
            >>> results = retrainer.retrain_and_deploy()
            >>> print(f"New model accuracy: {results['new_metrics']['accuracy']:.4f}")
        """
        logger.info("="*70)
        logger.info("STARTING AUTOMATIC RETRAINING WORKFLOW")
        logger.info("="*70)
        
        # ===== STEP 1: Check if Retraining is Needed =====
        if not force and not self.should_retrain():
            logger.info("Retraining not needed at this time")
            return {
                'status': 'skipped',
                'reason': 'Not yet time for retraining',
                'timestamp': datetime.now().isoformat()
            }
        
        # ===== STEP 2: Get Current Production Metrics =====
        # Store for comparison later
        production_metrics = self.get_production_metrics()
        
        # ===== STEP 3: Train New Model =====
        logger.info("Training new model with latest data...")
        try:
            trainer = MLModelTrainer(config_path=self.config.get('config_path', 'config.yaml'))
            run_id, new_metrics = trainer.run_training_pipeline()
            
            logger.info(f"✓ New model trained successfully")
            logger.info(f"  Run ID: {run_id}")
            logger.info(f"  Accuracy: {new_metrics['accuracy']:.4f}")
            
        except Exception as e:
            error_msg = f"Training failed: {str(e)}"
            logger.error(error_msg)
            
            # Send failure notification
            self.send_notification(
                subject="GNU MLOps: Retraining Failed",
                message=f"Automatic retraining failed:\n\n{error_msg}\n\nPlease check logs for details."
            )
            
            raise
        
        # ===== STEP 4: Compare with Production =====
        is_better, improvement = self.compare_models(new_metrics, production_metrics)
        
        # ===== STEP 5: Deploy if Better (and auto_deploy enabled) =====
        deployment_info = {}
        
        if self.auto_deploy and is_better:
            logger.info("Auto-deploying new model...")
            
            try:
                deployer = ModelDeployment(config_path=self.config.get('config_path', 'config.yaml'))
                
                # Deploy to Staging first
                staging_version = deployer.deploy_to_staging()
                
                if staging_version:
                    logger.info(f"✓ Deployed to Staging: Version {staging_version}")
                    deployment_info['staging_version'] = staging_version
                    
                    # Deploy to Production
                    prod_version = deployer.deploy_to_production()
                    
                    if prod_version:
                        logger.info(f"✓ Deployed to GNU_Production: Version {prod_version}")
                        deployment_info['production_version'] = prod_version
                        deployment_info['deployed'] = True
                    else:
                        logger.warning("Model deployed to Staging but not to Production")
                        logger.warning("  Possible reasons: accuracy < 80% or deployment failed")
                        deployment_info['deployed'] = False
                else:
                    logger.warning("Model did not meet Staging threshold (35%)")
                    deployment_info['deployed'] = False
                    
            except Exception as e:
                error_msg = f"Deployment failed: {str(e)}"
                logger.error(error_msg)
                deployment_info['deployment_error'] = error_msg
                deployment_info['deployed'] = False
        
        elif not self.auto_deploy:
            logger.info("Auto-deploy is disabled - model trained but not deployed")
            logger.info("  Deploy manually with: python src/deploy_model.py --stage production")
            deployment_info['deployed'] = False
            deployment_info['reason'] = 'auto_deploy disabled'
        
        elif not is_better:
            logger.info("New model is not better than production - keeping production model")
            deployment_info['deployed'] = False
            deployment_info['reason'] = 'new model not better'
        
        # ===== STEP 6: Prepare Results Summary =====
        results = {
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'run_id': run_id,
            'new_metrics': new_metrics,
            'production_metrics': production_metrics,
            'improvement': improvement,
            'is_better': is_better,
            'deployment': deployment_info
        }
        
        # ===== STEP 7: Send Notification =====
        if deployment_info.get('deployed'):
            notification_subject = "GNU MLOps: Model Retrained and Deployed"
            notification_message = f"""Model retraining completed successfully!

New Model Performance:
  Accuracy: {new_metrics['accuracy']:.4f}
  F1 Score: {new_metrics['f1_score']:.4f}
  Precision: {new_metrics.get('precision', 'N/A')}
  Recall: {new_metrics.get('recall', 'N/A')}

Improvement: {improvement:+.4f}

Deployment:
  Staging Version: {deployment_info.get('staging_version', 'N/A')}
  Production Version: {deployment_info.get('production_version', 'N/A')}

The new model has been deployed to GNU_Production.
"""
        else:
            notification_subject = "GNU MLOps: Model Retrained (Not Deployed)"
            notification_message = f"""Model retraining completed, but new model was not deployed.

New Model Performance:
  Accuracy: {new_metrics['accuracy']:.4f}
  F1 Score: {new_metrics['f1_score']:.4f}

Production Model Performance:
  Accuracy: {production_metrics.get('accuracy', 'N/A') if production_metrics else 'N/A'}

Improvement: {improvement:+.4f}

Reason: {deployment_info.get('reason', 'Unknown')}

The new model is available in MLflow but not deployed to production.
You can review and deploy manually if needed.
"""
        
        self.send_notification(notification_subject, notification_message)
        
        # ===== STEP 8: Log Summary =====
        logger.info("="*70)
        logger.info("RETRAINING WORKFLOW COMPLETED")
        logger.info("="*70)
        logger.info(f"Status: {results['status']}")
        logger.info(f"New Model Accuracy: {new_metrics['accuracy']:.4f}")
        logger.info(f"Improvement: {improvement:+.4f}")
        logger.info(f"Deployed: {deployment_info.get('deployed', False)}")
        logger.info(f"Log file: {log_file}")
        
        return results


def main():
    """
    Main execution function for command-line usage
    
    Provides CLI interface for automatic retraining:
    - Normal mode: Checks schedule and retrains if needed
    - Force mode: Retrains immediately regardless of schedule
    
    Command-line Arguments:
        --force: Optional. Force retraining even if not scheduled
        --config: Optional. Path to config file (default: config.yaml)
        
    Usage Examples:
        # Normal scheduled retraining
        python src/retrain_model.py
        
        # Force immediate retraining
        python src/retrain_model.py --force
        
        # Use different config file
        python src/retrain_model.py --config config.local.yaml
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automatic model retraining with 30-day schedule'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force retraining even if not scheduled'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize retrainer
        retrainer = AutomaticRetrainer(config_path=args.config)
        
        # Execute retraining workflow
        results = retrainer.retrain_and_deploy(force=args.force)
        
        # Print summary
        print("\n" + "="*70)
        print("RETRAINING SUMMARY")
        print("="*70)
        print(f"Status: {results['status']}")
        
        if results['status'] == 'completed':
            print(f"New Model Accuracy: {results['new_metrics']['accuracy']:.4f}")
            print(f"Improvement: {results['improvement']:+.4f}")
            print(f"Deployed: {results['deployment'].get('deployed', False)}")
            if results['deployment'].get('production_version'):
                print(f"Production Version: {results['deployment']['production_version']}")
        
        print("="*70)
        print(f"Log file: logs/retraining_*.log")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Retraining failed: {str(e)}")
        sys.exit(1)


# Script entry point
if __name__ == "__main__":
    main()

