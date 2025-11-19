"""
Generate Titanic Inference Data Files
Author: Narsimha Betini
Purpose: Create multiple inference data files for testing predictions

This script creates 5 CSV files, each with 10 records, ready for inference.
"""

import csv
import random
from pathlib import Path
from datetime import datetime

def generate_inference_data(num_files=5, records_per_file=10):
    """
    Generate inference data files with realistic Titanic passenger data
    
    Args:
        num_files: Number of files to create
        records_per_file: Number of records per file
    """
    base_dir = Path(__file__).parent.parent
    inference_dir = base_dir / "data" / "inference_input"
    inference_dir.mkdir(parents=True, exist_ok=True)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    print(f"Generating {num_files} inference files with {records_per_file} records each...")
    
    # Feature names (8 features as per config)
    feature_names = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5', 'feature6', 'feature7', 'feature8']
    
    for file_num in range(1, num_files + 1):
        # Generate realistic Titanic passenger data
        data = []
        
        for i in range(records_per_file):
            # Generate realistic features
            pclass = random.choice([1, 2, 3])  # Passenger class
            age = max(0.5, min(80, random.gauss(30, 15)))  # Age (clamped)
            sibsp = min(3, random.randint(0, 3))  # Siblings/spouse
            parch = min(3, random.randint(0, 3))  # Parents/children
            
            # Fare based on class
            if pclass == 1:
                fare = max(0, random.gauss(80, 30))
            elif pclass == 2:
                fare = max(0, random.gauss(20, 10))
            else:
                fare = max(0, random.gauss(10, 5))
            
            has_cabin = random.choice([0, 1])  # Has cabin or not
            sex_male = random.choice([0, 1])  # 1 if male, 0 if female
            embarked_q = random.choice([0, 1])  # 1 if embarked from Q, 0 otherwise
            
            # Create feature row (8 features)
            # feature1: Pclass
            # feature2: Age
            # feature3: SibSp
            # feature4: Parch
            # feature5: Fare
            # feature6: HasCabin
            # feature7: Sex_male
            # feature8: Embarked_Q
            row = [
                round(pclass, 1),
                round(age, 2),
                sibsp,
                parch,
                round(fare, 2),
                has_cabin,
                sex_male,
                embarked_q
            ]
            
            data.append(row)
        
        # Save to CSV file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"titanic_inference_batch_{file_num:02d}_{timestamp}.csv"
        filepath = inference_dir / filename
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(feature_names)  # Header
            writer.writerows(data)  # Data rows
        
        print(f"  ✓ Created: {filename} ({len(data)} records)")
    
    print(f"\n{'='*70}")
    print(f"SUCCESS: Created {num_files} inference files in {inference_dir}")
    print(f"{'='*70}")
    print("\nFiles created:")
    for file_num in range(1, num_files + 1):
        files = list(inference_dir.glob(f"titanic_inference_batch_{file_num:02d}_*.csv"))
        if files:
            print(f"  - {files[0].name}")

if __name__ == "__main__":
    generate_inference_data(num_files=5, records_per_file=10)
