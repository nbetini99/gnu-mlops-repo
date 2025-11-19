"""
Preprocess Diabetes Data for ML Training
Author: Narsimha Betini
Purpose: Convert diabetes monitoring data into ML-ready format

This script:
- Reads diabetes data files from TrainData/Diabetes-Data/
- Extracts features (blood glucose, insulin doses, time features)
- Creates target variable (blood glucose prediction)
- Splits into training and testing sets
- Saves as CSV files
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import os

def load_diabetes_data(data_dir):
    """
    Load all diabetes data files and combine into single dataframe
    
    Args:
        data_dir: Path to Diabetes-Data directory
        
    Returns:
        pd.DataFrame: Combined diabetes data
    """
    data_dir = Path(data_dir)
    all_data = []
    
    # Load all data files (data-01 through data-70)
    for i in range(1, 71):
        file_path = data_dir / f"data-{i:02d}"
        if file_path.exists():
            try:
                df = pd.read_csv(
                    file_path,
                    sep='\t',
                    header=None,
                    names=['date', 'time', 'code', 'value'],
                    parse_dates={'datetime': ['date', 'time']},
                    date_format='%m-%d-%Y %H:%M',
                    on_bad_lines='skip'
                )
                df['patient_id'] = i
                all_data.append(df)
            except Exception as e:
                print(f"Warning: Could not load {file_path}: {e}")
    
    if not all_data:
        raise ValueError("No diabetes data files found!")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df

def create_features(df):
    """
    Create ML features from diabetes data
    
    Args:
        df: Raw diabetes dataframe
        
    Returns:
        pd.DataFrame: Feature dataframe
    """
    # Sort by patient and datetime
    df = df.sort_values(['patient_id', 'datetime']).reset_index(drop=True)
    
    # Extract time features
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df['day_of_month'] = df['datetime'].dt.day
    
    # Create features for each patient
    features_list = []
    
    for patient_id in df['patient_id'].unique():
        patient_df = df[df['patient_id'] == patient_id].copy()
        
        # Get blood glucose measurements (codes 48, 57, 58, 59, 60, 61, 62)
        bg_codes = [48, 57, 58, 59, 60, 61, 62]
        bg_measurements = patient_df[patient_df['code'].isin(bg_codes)].copy()
        
        # Get insulin doses (codes 33, 34, 35)
        insulin_codes = [33, 34, 35]
        insulin_doses = patient_df[patient_df['code'].isin(insulin_codes)].copy()
        
        # For each blood glucose measurement, create features
        for idx, row in bg_measurements.iterrows():
            # Current blood glucose value
            current_bg = row['value']
            
            # Find previous measurements within last 24 hours
            time_window = pd.Timedelta(hours=24)
            past_data = patient_df[
                (patient_df['datetime'] < row['datetime']) &
                (patient_df['datetime'] >= row['datetime'] - time_window)
            ]
            
            # Feature: Previous blood glucose (if available)
            prev_bg = past_data[past_data['code'].isin(bg_codes)]['value']
            prev_bg_mean = prev_bg.mean() if len(prev_bg) > 0 else current_bg
            prev_bg_max = prev_bg.max() if len(prev_bg) > 0 else current_bg
            prev_bg_min = prev_bg.min() if len(prev_bg) > 0 else current_bg
            
            # Feature: Insulin doses in last 24 hours
            insulin_past = past_data[past_data['code'].isin(insulin_codes)]['value']
            total_insulin = insulin_past.sum() if len(insulin_past) > 0 else 0
            insulin_count = len(insulin_past)
            
            # Feature: Time since last insulin
            last_insulin = past_data[past_data['code'].isin(insulin_codes)]['datetime']
            hours_since_insulin = (row['datetime'] - last_insulin.max()).total_seconds() / 3600 if len(last_insulin) > 0 else 24
            
            # Feature: Number of measurements in last 24 hours
            measurement_count = len(past_data)
            
            # Create feature row
            feature_row = {
                'patient_id': patient_id,
                'datetime': row['datetime'],
                'hour': row['hour'],
                'day_of_week': row['day_of_week'],
                'day_of_month': row['day_of_month'],
                'feature1': prev_bg_mean,  # Mean previous BG
                'feature2': prev_bg_max,   # Max previous BG
                'feature3': prev_bg_min,   # Min previous BG
                'feature4': total_insulin,  # Total insulin in 24h
                'feature5': insulin_count,   # Number of insulin doses
                'feature6': hours_since_insulin,  # Hours since last insulin
                'feature7': measurement_count,  # Number of measurements
                'target': current_bg  # Target: current blood glucose
            }
            
            features_list.append(feature_row)
    
    features_df = pd.DataFrame(features_list)
    
    # Handle missing values
    features_df = features_df.fillna(features_df.mean())
    
    return features_df

def main():
    """Main preprocessing function"""
    # Paths
    base_dir = Path(__file__).parent.parent
    diabetes_dir = base_dir / "data" / "TrainData" / "Diabetes-Data"
    output_dir = base_dir / "data"
    
    # Create output directories
    (output_dir / "training").mkdir(exist_ok=True)
    (output_dir / "testing").mkdir(exist_ok=True)
    (output_dir / "inference_input").mkdir(exist_ok=True)
    
    print("Loading diabetes data...")
    raw_df = load_diabetes_data(diabetes_dir)
    print(f"Loaded {len(raw_df):,} records from {raw_df['patient_id'].nunique()} patients")
    
    print("Creating features...")
    features_df = create_features(raw_df)
    print(f"Created {len(features_df):,} feature rows")
    
    # Split into train/test (80/20)
    np.random.seed(42)
    train_size = int(0.8 * len(features_df))
    indices = np.random.permutation(len(features_df))
    train_indices = indices[:train_size]
    test_indices = indices[train_size:]
    
    train_df = features_df.iloc[train_indices].copy()
    test_df = features_df.iloc[test_indices].copy()
    
    # Save training data
    train_path = output_dir / "training" / "diabetes_training_data.csv"
    train_df.to_csv(train_path, index=False)
    print(f"Saved training data: {train_path} ({len(train_df):,} rows)")
    
    # Save testing data
    test_path = output_dir / "testing" / "diabetes_test_data.csv"
    test_df.to_csv(test_path, index=False)
    print(f"Saved testing data: {test_path} ({len(test_df):,} rows)")
    
    # Create inference input (sample from test data without target)
    inference_df = test_df.drop(columns=['target']).head(100).copy()
    inference_path = output_dir / "inference_input" / "diabetes_inference_sample.csv"
    inference_df.to_csv(inference_path, index=False)
    print(f"Saved inference sample: {inference_path} ({len(inference_df):,} rows)")
    
    print("\n" + "="*70)
    print("PREPROCESSING COMPLETE!")
    print("="*70)
    print(f"Training data: {train_path}")
    print(f"Testing data: {test_path}")
    print(f"Inference sample: {inference_path}")
    print("="*70)

if __name__ == "__main__":
    main()

