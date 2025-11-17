"""
Unit tests for deployment automation
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.deploy_model import ModelDeployment


class TestModelDeployment:
    """Test cases for ModelDeployment class"""
    
    @pytest.fixture(autouse=True)
    def setup_mlflow(self, monkeypatch):
        """Set up MLflow tracking URI for testing"""
        monkeypatch.setenv('MLFLOW_TRACKING_URI', 'sqlite:///test_mlflow.db')
    
    @patch('src.deploy_model.MlflowClient')
    @patch('src.deploy_model.mlflow.set_tracking_uri')
    def test_validate_model_performance(self, mock_set_tracking, mock_client_class):
        """Test model performance validation"""
        # Mock the client instance
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        deployer = ModelDeployment()
        
        # Test passing threshold
        metrics = {'accuracy': 0.85, 'f1_score': 0.82}
        assert deployer.validate_model_performance(metrics, threshold=0.8) is True
        
        # Test failing threshold
        metrics = {'accuracy': 0.75, 'f1_score': 0.72}
        assert deployer.validate_model_performance(metrics, threshold=0.8) is False
    
    @patch('src.deploy_model.MlflowClient')
    @patch('src.deploy_model.mlflow.set_tracking_uri')
    def test_get_model_metrics(self, mock_set_tracking, mock_client_class):
        """Test retrieving model metrics"""
        # Mock the client instance
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the run object
        mock_run = Mock()
        mock_run.data.metrics = {'accuracy': 0.85, 'f1_score': 0.82}
        mock_client.get_run.return_value = mock_run
        
        deployer = ModelDeployment()
        metrics = deployer.get_model_metrics('test_run_id')
        
        assert 'accuracy' in metrics
        assert 'f1_score' in metrics
        assert metrics['accuracy'] == 0.85


if __name__ == '__main__':
    pytest.main([__file__])

