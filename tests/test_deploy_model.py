"""
Unit tests for deployment automation
"""

import pytest
from unittest.mock import Mock, patch
from src.deploy_model import ModelDeployment


class TestModelDeployment:
    """Test cases for ModelDeployment class"""
    
    @patch('src.deploy_model.MlflowClient')
    def test_validate_model_performance(self, mock_client):
        """Test model performance validation"""
        deployer = ModelDeployment()
        
        # Test passing threshold
        metrics = {'accuracy': 0.85, 'f1_score': 0.82}
        assert deployer.validate_model_performance(metrics, threshold=0.8) is True
        
        # Test failing threshold
        metrics = {'accuracy': 0.75, 'f1_score': 0.72}
        assert deployer.validate_model_performance(metrics, threshold=0.8) is False
    
    @patch('src.deploy_model.MlflowClient')
    def test_get_model_metrics(self, mock_client):
        """Test retrieving model metrics"""
        deployer = ModelDeployment()
        
        # Mock MLflow client
        mock_run = Mock()
        mock_run.data.metrics = {'accuracy': 0.85, 'f1_score': 0.82}
        mock_client.return_value.get_run.return_value = mock_run
        
        metrics = deployer.get_model_metrics('test_run_id')
        assert 'accuracy' in metrics
        assert 'f1_score' in metrics


if __name__ == '__main__':
    pytest.main([__file__])

