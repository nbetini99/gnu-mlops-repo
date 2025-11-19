"""
Preprocess Titanic Data for ML Training
Author: Narsimha Betini
Purpose: Prepare Titanic dataset for classification with RandomForestClassifier

This script:
- Loads Titanic training and test data
- Handles missing values
- Creates features from categorical variables
- Saves processed data for training and inference
"""

import pandas as pd
import numpy as np
from pathlib import Path

def preprocess_titanic_data(df):
    """
    Preprocess Titanic data for ML
    
    Args:
        df: Raw Titanic dataframe
        
    Returns:
        pd.DataFrame: Preprocessed dataframe
    """
    df = df.copy()
    
    # Handle missing values
    # Age: Fill with median
    df['Age'].fillna(df['Age'].median(), inplace=True)
    
    # Embarked: Fill with most common
    df['Embarked'].fillna(df['Embarked'].mode()[0], inplace=True)
    
    # Fare: Fill with median
    df['Fare'].fillna(df['Fare'].median(), inplace=True)
    
    # Cabin: Create binary feature (has cabin or not)
    df['HasCabin'] = df['Cabin'].notna().astype(int)
    
    # Create feature columns
    # Select relevant features for classification
    features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked', 'HasCabin']
    
    # One-hot encode categorical variables
    df_processed = pd.get_dummies(df[features], columns=['Sex', 'Embarked'], drop_first=True)
    
    # Store target before renaming (if it exists)
    target_values = None
    if 'Survived' in df.columns:
        target_values = df['Survived'].copy()
    
    # Store PassengerId before renaming (if it exists)
    passenger_ids = None
    if 'PassengerId' in df.columns:
        passenger_ids = df['PassengerId'].copy()
    
    # Rename columns to feature1, feature2, etc. for consistency
    df_processed.columns = [f'feature{i+1}' for i in range(len(df_processed.columns))]
    
    # Add target if it exists (Survived column)
    if target_values is not None:
        df_processed['target'] = target_values
    
    # Add PassengerId for reference
    if passenger_ids is not None:
        df_processed['PassengerId'] = passenger_ids
    
    return df_processed

def main():
    """Main preprocessing function"""
    base_dir = Path(__file__).parent.parent
    titanic_dir = base_dir / "data" / "titanic"
    output_dir = base_dir / "data"
    
    # Create output directories
    (output_dir / "training").mkdir(exist_ok=True)
    (output_dir / "testing").mkdir(exist_ok=True)
    (output_dir / "inference_input").mkdir(exist_ok=True)
    
    print("Loading Titanic data...")
    
    # Load training data
    train_path = titanic_dir / "train.csv"
    train_df = pd.read_csv(train_path)
    print(f"Loaded training data: {len(train_df):,} rows")
    
    # Load test data
    test_path = titanic_dir / "test.csv"
    test_df = pd.read_csv(test_path)
    print(f"Loaded test data: {len(test_df):,} rows")
    
    # Preprocess training data
    print("Preprocessing training data...")
    train_processed = preprocess_titanic_data(train_df)
    print(f"Training features: {list(train_processed.columns)}")
    
    # Preprocess test data
    print("Preprocessing test data...")
    test_processed = preprocess_titanic_data(test_df)
    
    # Save training data
    train_output = output_dir / "training" / "titanic_training_data.csv"
    train_processed.to_csv(train_output, index=False)
    print(f"Saved training data: {train_output} ({len(train_processed):,} rows)")
    
    # Save test data (for validation)
    test_output = output_dir / "testing" / "titanic_test_data.csv"
    test_processed.to_csv(test_output, index=False)
    print(f"Saved test data: {test_output} ({len(test_processed):,} rows)")
    
    # Create inference input (test data without target)
    inference_df = test_processed.drop(columns=['target'], errors='ignore').copy()
    inference_output = output_dir / "inference_input" / "titanic_inference_data.csv"
    inference_df.to_csv(inference_output, index=False)
    print(f"Saved inference data: {inference_output} ({len(inference_df):,} rows)")
    
    print("\n" + "="*70)
    print("PREPROCESSING COMPLETE!")
    print("="*70)
    print(f"Training data: {train_output}")
    print(f"  - Rows: {len(train_processed):,}")
    print(f"  - Features: {len(train_processed.columns) - 2}")  # Exclude target and PassengerId
    print(f"  - Target: Survived (0 or 1)")
    print(f"Test data: {test_output}")
    print(f"Inference data: {inference_output}")
    print("="*70)

if __name__ == "__main__":
    main()

