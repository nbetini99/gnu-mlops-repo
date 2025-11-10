"""
Unit tests for training pipeline
"""

import pytest
import pandas as pd
import numpy as np
from src.train_model import MLModelTrainer


class TestMLModelTrainer:
    """Test cases for MLModelTrainer class"""
    
    def test_generate_sample_data(self):
        """Test sample data generation"""
        trainer = MLModelTrainer()
        df = trainer._generate_sample_data(n_samples=100)
        
        assert len(df) == 100
        assert 'feature1' in df.columns
        assert 'feature2' in df.columns
        assert 'feature3' in df.columns
        assert 'target_column' in df.columns
    
    def test_preprocess_data(self):
        """Test data preprocessing"""
        trainer = MLModelTrainer()
        df = trainer._generate_sample_data(n_samples=100)
        
        X_train, X_test, y_train, y_test, scaler = trainer.preprocess_data(df)
        
        assert X_train.shape[0] > 0
        assert X_test.shape[0] > 0
        assert len(y_train) > 0
        assert len(y_test) > 0
        assert scaler is not None
    
    def test_train_model(self):
        """Test model training"""
        trainer = MLModelTrainer()
        df = trainer._generate_sample_data(n_samples=100)
        X_train, X_test, y_train, y_test, scaler = trainer.preprocess_data(df)
        
        model, cv_scores = trainer.train_model(X_train, y_train)
        
        assert model is not None
        assert len(cv_scores) > 0
        assert all(0 <= score <= 1 for score in cv_scores)
    
    def test_evaluate_model(self):
        """Test model evaluation"""
        trainer = MLModelTrainer()
        df = trainer._generate_sample_data(n_samples=100)
        X_train, X_test, y_train, y_test, scaler = trainer.preprocess_data(df)
        model, _ = trainer.train_model(X_train, y_train)
        
        metrics = trainer.evaluate_model(model, X_test, y_test)
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert all(0 <= v <= 1 for v in metrics.values())


if __name__ == '__main__':
    pytest.main([__file__])

