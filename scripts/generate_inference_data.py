#!/usr/bin/env python3
"""
Generate Multiple Inference Data Files
Author: Narsimha Betini
Purpose: Create multiple test data files for running inferences

This script generates various inference data files with different:
- File sizes (small, medium, large)
- Data distributions
- File formats (CSV)
- Use cases (daily batch, ad-hoc testing, production samples)
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import yaml

def load_config(config_path='config.yaml'):
    """Load configuration file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def generate_inference_data(num_records, seed=None, distribution='normal'):
    """
    Generate synthetic inference data matching training data format
    
    Args:
        num_records: Number of records to generate
        seed: Random seed for reproducibility
        distribution: Data distribution type ('normal', 'uniform', 'mixed')
    
    Returns:
        pandas.DataFrame: Generated inference data
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate features matching training data format
    if distribution == 'normal':
        # Normal distribution (most common)
        feature1 = np.random.randn(num_records)
        feature2 = np.random.randn(num_records)
        feature3 = np.random.randn(num_records)
    elif distribution == 'uniform':
        # Uniform distribution
        feature1 = np.random.uniform(-3, 3, num_records)
        feature2 = np.random.uniform(-3, 3, num_records)
        feature3 = np.random.uniform(-3, 3, num_records)
    elif distribution == 'mixed':
        # Mixed distribution (realistic scenario)
        feature1 = np.random.randn(num_records) * 0.8 + np.random.uniform(-1, 1, num_records) * 0.2
        feature2 = np.random.randn(num_records) * 0.7 + np.random.uniform(-2, 2, num_records) * 0.3
        feature3 = np.random.randn(num_records) * 0.9 + np.random.uniform(-1.5, 1.5, num_records) * 0.1
    else:
        # Default to normal
        feature1 = np.random.randn(num_records)
        feature2 = np.random.randn(num_records)
        feature3 = np.random.randn(num_records)
    
    # Create DataFrame with same feature names as training data
    df = pd.DataFrame({
        'feature1': feature1,
        'feature2': feature2,
        'feature3': feature3
    })
    
    return df

def generate_daily_batch_files(output_dir, num_files=7, records_per_file=1000):
    """Generate daily batch inference files (one per day)"""
    output_path = Path(output_dir) / 'daily_batch'
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📅 Generating {num_files} daily batch files...")
    
    for i in range(num_files):
        date = datetime.now() - timedelta(days=num_files - i - 1)
        filename = f"daily_batch_{date.strftime('%Y%m%d')}.csv"
        filepath = output_path / filename
        
        # Generate data with slight variation per day
        data = generate_inference_data(
            num_records=records_per_file,
            seed=42 + i,  # Different seed per day
            distribution='normal'
        )
        
        data.to_csv(filepath, index=False)
        print(f"  ✓ Created: {filename} ({len(data):,} records)")
    
    return output_path

def generate_test_files(output_dir):
    """Generate various test files for different scenarios"""
    output_path = Path(output_dir) / 'test'
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🧪 Generating test files...")
    
    test_files = [
        {
            'name': 'test_small.csv',
            'records': 100,
            'seed': 100,
            'distribution': 'normal',
            'description': 'Small test file (100 records)'
        },
        {
            'name': 'test_medium.csv',
            'records': 1000,
            'seed': 200,
            'distribution': 'normal',
            'description': 'Medium test file (1,000 records)'
        },
        {
            'name': 'test_large.csv',
            'records': 10000,
            'seed': 300,
            'distribution': 'normal',
            'description': 'Large test file (10,000 records)'
        },
        {
            'name': 'test_uniform.csv',
            'records': 1000,
            'seed': 400,
            'distribution': 'uniform',
            'description': 'Uniform distribution test (1,000 records)'
        },
        {
            'name': 'test_mixed.csv',
            'records': 1000,
            'seed': 500,
            'distribution': 'mixed',
            'description': 'Mixed distribution test (1,000 records)'
        },
        {
            'name': 'test_single.csv',
            'records': 1,
            'seed': 600,
            'distribution': 'normal',
            'description': 'Single record test'
        },
        {
            'name': 'test_edge_cases.csv',
            'records': 50,
            'seed': 700,
            'distribution': 'normal',
            'description': 'Edge cases test (50 records)'
        }
    ]
    
    for test_file in test_files:
        filepath = output_path / test_file['name']
        data = generate_inference_data(
            num_records=test_file['records'],
            seed=test_file['seed'],
            distribution=test_file['distribution']
        )
        
        # Add some edge cases for the edge cases file
        if 'edge_cases' in test_file['name']:
            # Add extreme values
            extreme_data = pd.DataFrame({
                'feature1': [5.0, -5.0, 0.0, np.nan, 10.0],
                'feature2': [5.0, -5.0, 0.0, 0.0, -10.0],
                'feature3': [5.0, -5.0, 0.0, 0.0, 10.0]
            })
            data = pd.concat([data, extreme_data], ignore_index=True)
            data = data.fillna(0)  # Fill NaN with 0
        
        data.to_csv(filepath, index=False)
        print(f"  ✓ Created: {test_file['name']} ({len(data):,} records) - {test_file['description']}")
    
    return output_path

def generate_production_samples(output_dir, num_files=3, records_per_file=5000):
    """Generate production-like sample files"""
    output_path = Path(output_dir) / 'production_samples'
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🏭 Generating {num_files} production sample files...")
    
    for i in range(num_files):
        filename = f"production_sample_{i+1}.csv"
        filepath = output_path / filename
        
        # Generate realistic production-like data
        data = generate_inference_data(
            num_records=records_per_file,
            seed=1000 + i,
            distribution='mixed'  # More realistic distribution
        )
        
        data.to_csv(filepath, index=False)
        print(f"  ✓ Created: {filename} ({len(data):,} records)")
    
    return output_path

def generate_batch_input_files(output_dir, num_files=5, records_per_file=2000):
    """Generate files for batch inference input directory"""
    output_path = Path(output_dir) / 'batch_input'
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📦 Generating {num_files} batch input files...")
    
    for i in range(num_files):
        timestamp = datetime.now() - timedelta(hours=i*2)
        filename = f"batch_input_{timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = output_path / filename
        
        data = generate_inference_data(
            num_records=records_per_file,
            seed=2000 + i,
            distribution='normal'
        )
        
        data.to_csv(filepath, index=False)
        print(f"  ✓ Created: {filename} ({len(data):,} records)")
    
    return output_path

def main():
    """Main function to generate all inference data files"""
    parser = argparse.ArgumentParser(
        description='Generate multiple inference data files for testing'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory for generated files (default: data)'
    )
    parser.add_argument(
        '--skip-daily',
        action='store_true',
        help='Skip generating daily batch files'
    )
    parser.add_argument(
        '--skip-test',
        action='store_true',
        help='Skip generating test files'
    )
    parser.add_argument(
        '--skip-production',
        action='store_true',
        help='Skip generating production sample files'
    )
    parser.add_argument(
        '--skip-batch',
        action='store_true',
        help='Skip generating batch input files'
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("GENERATING INFERENCE DATA FILES")
    print("=" * 70)
    print(f"Output directory: {output_dir.absolute()}")
    print()
    
    generated_paths = []
    
    # Generate daily batch files
    if not args.skip_daily:
        daily_path = generate_daily_batch_files(output_dir, num_files=7, records_per_file=1000)
        generated_paths.append(daily_path)
    
    # Generate test files
    if not args.skip_test:
        test_path = generate_test_files(output_dir)
        generated_paths.append(test_path)
    
    # Generate production samples
    if not args.skip_production:
        prod_path = generate_production_samples(output_dir, num_files=3, records_per_file=5000)
        generated_paths.append(prod_path)
    
    # Generate batch input files
    if not args.skip_batch:
        batch_path = generate_batch_input_files(output_dir, num_files=5, records_per_file=2000)
        generated_paths.append(batch_path)
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ GENERATION COMPLETE!")
    print("=" * 70)
    print(f"\nGenerated files in:")
    for path in generated_paths:
        file_count = len(list(path.glob('*.csv')))
        print(f"  📁 {path.relative_to(output_dir)} ({file_count} files)")
    
    print(f"\n📊 Total files generated: {sum(len(list(p.glob('*.csv'))) for p in generated_paths)}")
    print(f"📂 Base directory: {output_dir.absolute()}")
    print("\n💡 Usage examples:")
    print(f"  python src/predict.py --input {output_dir}/test/test_small.csv --output predictions.csv")
    print(f"  python src/batch_inference.py --input {output_dir}/batch_input/")
    print("=" * 70)

if __name__ == "__main__":
    main()

