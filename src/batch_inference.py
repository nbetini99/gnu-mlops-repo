"""
Daily Batch Inference System
Author: Narsimha Betini
Purpose: Scheduled batch predictions on daily data files

This module provides automated batch inference capabilities:
- Loads input data from configured source (local file, S3, Databricks)
- Generates predictions using production model
- Saves results to configured output location
- Handles errors gracefully with logging
- Sends notifications on completion
- Archives processed files

The batch inference workflow:
1. Check for new input data files
2. Load production model from MLflow
3. Process data in batches (if large)
4. Generate predictions
5. Save results with timestamp
6. Archive input file (optional)
7. Send completion notification
"""

import os
import sys
import yaml
import mlflow
from datetime import datetime, timedelta
import logging
from pathlib import Path
import pandas as pd
import json

# Import existing prediction module
from predict import ModelPredictor

# Setup logging with file output for scheduled runs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"batch_inference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BatchInference:
    """
    Automated batch inference system for scheduled predictions
    
    This class manages the complete batch inference workflow:
    - Monitors input data directories
    - Processes data files automatically
    - Generates predictions using production model
    - Saves results with timestamps
    - Handles errors and retries
    - Sends notifications
    
    Attributes:
        config (dict): Loaded configuration from YAML file
        predictor (ModelPredictor): Loaded prediction service
        input_path (str): Path to input data file or directory
        output_path (str): Path to save predictions
        archive_path (str): Path to archive processed files
        
    Typical Usage:
        batch = BatchInference()
        results = batch.run_batch_inference()
    """
    
    def __init__(self, config_path='config.yaml'):
        """
        Initialize batch inference system with configuration
        
        Loads configuration and sets up prediction service with
        production model for batch processing.
        
        Args:
            config_path (str): Path to YAML configuration file
                             Defaults to 'config.yaml'
                             
        Raises:
            FileNotFoundError: If config file doesn't exist
            Exception: If model loading fails
        """
        # Load configuration
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Get batch inference configuration
        batch_config = self.config.get('batch_inference', {})
        
        # Input/output paths
        self.input_path = batch_config.get('input_path', 'data/batch_input/')
        self.output_path = batch_config.get('output_path', 'data/batch_output/')
        self.archive_path = batch_config.get('archive_path', 'data/batch_archive/')
        
        # Processing options
        self.model_stage = batch_config.get('model_stage', 'GNU_Production')
        self.batch_size = batch_config.get('batch_size', 10000)  # Process in chunks if large
        self.archive_input = batch_config.get('archive_input', True)
        self.notification_email = batch_config.get('notification_email', None)
        
        # Create directories if they don't exist
        Path(self.output_path).mkdir(parents=True, exist_ok=True)
        if self.archive_input:
            Path(self.archive_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize predictor with production model
        logger.info("Loading production model for batch inference...")
        self.predictor = ModelPredictor(config_path=config_path, stage=self.model_stage)
        
        logger.info(f"Batch inference system initialized")
        logger.info(f"→ Input path: {self.input_path}")
        logger.info(f"→ Output path: {self.output_path}")
        logger.info(f"→ Model stage: {self.model_stage}")
        logger.info(f"→ Batch size: {self.batch_size:,} rows")
    
    def find_input_files(self):
        """
        Find input data files to process
        
        Searches the input path for data files (CSV, Parquet) that
        haven't been processed yet. Supports both single files and
        directories with multiple files.
        
        Returns:
            list: List of file paths to process
            
        Supported Formats:
            - CSV (.csv)
            - Parquet (.parquet)
            
        Note:
            Files are sorted by modification time (oldest first)
            to ensure consistent processing order
        """
        input_path = Path(self.input_path)
        
        if not input_path.exists():
            logger.warning(f"Input path does not exist: {self.input_path}")
            return []
        
        # Find all data files
        data_files = []
        
        if input_path.is_file():
            # Single file specified
            if input_path.suffix in ['.csv', '.parquet']:
                data_files.append(str(input_path))
        else:
            # Directory - find all data files
            for ext in ['*.csv', '*.parquet']:
                data_files.extend([str(f) for f in input_path.glob(ext)])
        
        # Sort by modification time (oldest first)
        data_files.sort(key=lambda f: os.path.getmtime(f))
        
        logger.info(f"Found {len(data_files)} input file(s) to process")
        for f in data_files:
            logger.info(f"  → {f}")
        
        return data_files
    
    def process_file(self, input_file):
        """
        Process a single input file and generate predictions
        
        Loads data, generates predictions, and saves results.
        Handles large files by processing in batches if needed.
        
        Args:
            input_file (str): Path to input data file
            
        Returns:
            dict: Processing results with statistics
            
        Raises:
            Exception: If processing fails
        """
        logger.info(f"Processing file: {input_file}")
        
        try:
            # ===== STEP 1: Load Input Data =====
            input_path = Path(input_file)
            
            if input_path.suffix == '.csv':
                data = pd.read_csv(input_file)
            elif input_path.suffix == '.parquet':
                data = pd.read_parquet(input_file)
            else:
                raise ValueError(f"Unsupported file format: {input_path.suffix}")
            
            logger.info(f"Loaded {len(data):,} rows from {input_file}")
            
            # ===== STEP 2: Generate Predictions =====
            # Process in batches if file is large
            if len(data) > self.batch_size:
                logger.info(f"Large file detected ({len(data):,} rows). Processing in batches of {self.batch_size:,}...")
                
                predictions_list = []
                num_batches = (len(data) + self.batch_size - 1) // self.batch_size
                
                for i in range(0, len(data), self.batch_size):
                    batch = data.iloc[i:i + self.batch_size]
                    batch_num = (i // self.batch_size) + 1
                    
                    logger.info(f"Processing batch {batch_num}/{num_batches} ({len(batch):,} rows)...")
                    batch_predictions = self.predictor.predict(batch)
                    predictions_list.extend(batch_predictions)
                
                predictions = pd.Series(predictions_list)
            else:
                # Small file - process all at once
                predictions = self.predictor.predict(data)
            
            # ===== STEP 3: Add Predictions to DataFrame =====
            data['predictions'] = predictions
            data['prediction_timestamp'] = datetime.now().isoformat()
            
            # ===== STEP 4: Save Results =====
            # Generate output filename with timestamp
            input_filename = input_path.stem
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"{input_filename}_predictions_{timestamp}.csv"
            output_file = Path(self.output_path) / output_filename
            
            # Save results
            data.to_csv(output_file, index=False)
            logger.info(f"✓ Predictions saved to: {output_file}")
            
            # ===== STEP 5: Calculate Statistics =====
            stats = {
                'input_file': input_file,
                'output_file': str(output_file),
                'rows_processed': len(data),
                'predictions_0': int((predictions == 0).sum()),
                'predictions_1': int((predictions == 1).sum()),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Processing statistics:")
            logger.info(f"  Rows processed: {stats['rows_processed']:,}")
            logger.info(f"  Predictions (class 0): {stats['predictions_0']:,}")
            logger.info(f"  Predictions (class 1): {stats['predictions_1']:,}")
            
            # ===== STEP 6: Archive Input File =====
            if self.archive_input:
                archive_filename = f"{input_filename}_{timestamp}{input_path.suffix}"
                archive_file = Path(self.archive_path) / archive_filename
                
                # Copy file to archive
                import shutil
                shutil.copy2(input_file, archive_file)
                logger.info(f"✓ Input file archived to: {archive_file}")
                
                # Optionally remove original (uncomment if desired)
                # input_path.unlink()
                # logger.info(f"✓ Original input file removed")
            
            return stats
            
        except Exception as e:
            error_msg = f"Error processing file {input_file}: {str(e)}"
            logger.error(error_msg)
            raise
    
    def send_notification(self, subject, message):
        """
        Send notification email about batch inference status
        
        Sends email notification if email is configured in config.
        Uses system's mail command (works on macOS/Linux).
        
        Args:
            subject (str): Email subject line
            message (str): Email body content
            
        Note:
            Requires email to be configured in batch_inference.notification_email
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
GNU MLOps Batch Inference System
Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
    
    def run_batch_inference(self):
        """
        Execute complete batch inference workflow
        
        Main orchestration method that:
        1. Finds input data files
        2. Processes each file
        3. Generates predictions
        4. Saves results
        5. Archives input files
        6. Sends notifications
        
        Returns:
            dict: Summary of batch inference run with statistics
            
        Raises:
            Exception: If any step in the workflow fails
            
        Example:
            >>> batch = BatchInference()
            >>> results = batch.run_batch_inference()
            >>> print(f"Processed {results['total_rows']:,} rows")
        """
        logger.info("="*70)
        logger.info("STARTING BATCH INFERENCE WORKFLOW")
        logger.info("="*70)
        
        start_time = datetime.now()
        
        # ===== STEP 1: Find Input Files =====
        input_files = self.find_input_files()
        
        if not input_files:
            logger.warning("No input files found to process")
            return {
                'status': 'no_files',
                'timestamp': datetime.now().isoformat(),
                'files_processed': 0
            }
        
        # ===== STEP 2: Process Each File =====
        results = {
            'status': 'completed',
            'start_time': start_time.isoformat(),
            'files_processed': 0,
            'total_rows': 0,
            'file_results': []
        }
        
        for input_file in input_files:
            try:
                file_stats = self.process_file(input_file)
                results['file_results'].append(file_stats)
                results['files_processed'] += 1
                results['total_rows'] += file_stats['rows_processed']
                
            except Exception as e:
                logger.error(f"Failed to process {input_file}: {str(e)}")
                results['file_results'].append({
                    'input_file': input_file,
                    'status': 'failed',
                    'error': str(e)
                })
                # Continue with next file instead of failing completely
        
        # ===== STEP 3: Calculate Summary =====
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        results['end_time'] = end_time.isoformat()
        results['duration_seconds'] = duration
        
        # ===== STEP 4: Send Notification =====
        if results['files_processed'] > 0:
            notification_subject = f"GNU MLOps: Batch Inference Completed - {results['files_processed']} file(s)"
            notification_message = f"""Batch inference completed successfully!

Summary:
  Files processed: {results['files_processed']}
  Total rows: {results['total_rows']:,}
  Duration: {duration:.1f} seconds
  Output path: {self.output_path}

File Details:
"""
            for file_result in results['file_results']:
                if 'rows_processed' in file_result:
                    notification_message += f"""
  • {Path(file_result['input_file']).name}:
    - Rows: {file_result['rows_processed']:,}
    - Output: {Path(file_result['output_file']).name}
"""
            
            self.send_notification(notification_subject, notification_message)
        else:
            notification_subject = "GNU MLOps: Batch Inference - No Files Processed"
            notification_message = f"""Batch inference completed but no files were processed.

Input path: {self.input_path}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check if input files exist in the configured input path.
"""
            self.send_notification(notification_subject, notification_message)
        
        # ===== STEP 5: Log Summary =====
        logger.info("="*70)
        logger.info("BATCH INFERENCE WORKFLOW COMPLETED")
        logger.info("="*70)
        logger.info(f"Files processed: {results['files_processed']}")
        logger.info(f"Total rows: {results['total_rows']:,}")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Log file: {log_file}")
        
        return results


def main():
    """
    Main execution function for command-line usage
    
    Provides CLI interface for batch inference:
    - Normal mode: Processes files from configured input path
    - Custom mode: Process specific file or directory
    
    Command-line Arguments:
        --input: Optional. Override input path from config
        --output: Optional. Override output path from config
        --config: Optional. Path to config file (default: config.yaml)
        
    Usage Examples:
        # Use configured paths
        python src/batch_inference.py
        
        # Process specific file
        python src/batch_inference.py --input data/new_data.csv
        
        # Use different config
        python src/batch_inference.py --config config.local.yaml
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Daily batch inference at 1 PM PST'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='Override input file or directory path (default: from config)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Override output directory path (default: from config)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize batch inference system
        batch = BatchInference(config_path=args.config)
        
        # Override paths if provided
        if args.input:
            batch.input_path = args.input
        if args.output:
            batch.output_path = args.output
            Path(batch.output_path).mkdir(parents=True, exist_ok=True)
        
        # Execute batch inference
        results = batch.run_batch_inference()
        
        # Print summary
        print("\n" + "="*70)
        print("BATCH INFERENCE SUMMARY")
        print("="*70)
        print(f"Status: {results['status']}")
        print(f"Files processed: {results['files_processed']}")
        print(f"Total rows: {results.get('total_rows', 0):,}")
        if 'duration_seconds' in results:
            print(f"Duration: {results['duration_seconds']:.1f} seconds")
        print("="*70)
        print(f"Log file: logs/batch_inference_*.log")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Batch inference failed: {str(e)}")
        sys.exit(1)


# Script entry point
if __name__ == "__main__":
    main()

