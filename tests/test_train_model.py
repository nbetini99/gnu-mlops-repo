"""
Unit tests for training pipeline
"""

import pytest
import pandas as pd
import numpy as np
import os
from src.train_model import MLModelTrainer


class TestMLModelTrainer:
    """Test cases for MLModelTrainer class"""
    
    @pytest.fixture(autouse=True)
    def setup_mlflow(self, monkeypatch):
        """Set up MLflow tracking URI for testing"""
        monkeypatch.setenv('MLFLOW_TRACKING_URI', 'sqlite:///test_mlflow.db')
    
    def test_create_synthetic_dataset(self):
        """Test synthetic data generation"""
        trainer = MLModelTrainer()
        df = trainer._create_synthetic_dataset(num_records=100)
        
        assert len(df) == 100
        assert 'target_column' in df.columns
        assert 'feature1' in df.columns
        assert 'feature2' in df.columns
        assert 'feature3' in df.columns
    
    def test_preprocess_data(self):
        """Test data preprocessing"""
        trainer = MLModelTrainer()
        df = trainer._create_synthetic_dataset(num_records=100)
        
        X_train, X_test, y_train, y_test, feature_scaler = trainer.preprocess_data(df)
        
        assert X_train.shape[0] > 0
        assert X_test.shape[0] > 0
        assert len(y_train) > 0
        assert len(y_test) > 0
        assert feature_scaler is not None
    
    def test_train_model(self):
        """Test model training"""
        trainer = MLModelTrainer()
        df = trainer._create_synthetic_dataset(num_records=100)
        X_train, X_test, y_train, y_test, feature_scaler = trainer.preprocess_data(df)
        
        model, cv_scores = trainer.train_model(X_train, y_train)
        
        assert model is not None
        assert len(cv_scores) > 0
        assert all(0 <= score <= 1 for score in cv_scores)
    
    def test_evaluate_model(self):
        """Test model evaluation"""
        trainer = MLModelTrainer()
        df = trainer._create_synthetic_dataset(num_records=100)
        X_train, X_test, y_train, y_test, feature_scaler = trainer.preprocess_data(df)
        model, _ = trainer.train_model(X_train, y_train)
        
        metrics = trainer.evaluate_model(model, X_test, y_test)
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert all(0 <= v <= 1 for v in metrics.values())


if __name__ == '__main__':
    pytest.main([__file__])
