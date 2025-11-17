# Deployment Guide

This guide provides detailed instructions for deploying your ML models using the GNU MLOps framework.

## Overview

The deployment process follows a staged approach:
1. **Development**: Model training and experimentation
2. **Staging**: Testing and validation
3. **Production**: Live serving

## Prerequisites

- Trained model registered in MLflow
- Databricks workspace access
- Required permissions for model deployment

## Deployment Workflow

### 1. Train and Register Model

```bash
python src/train_model.py
```

This will:
- Train your model
- Log metrics to MLflow
- Register model in MLflow Model Registry

### 2. Deploy to Staging

```bash
python src/deploy_model.py --stage staging
```

**Staging Deployment Checklist:**
- ✓ Model meets 70% accuracy threshold
- ✓ Model version is registered
- ✓ Staging environment is available

### 3. Validate in Staging

```bash
# Run predictions
python src/predict.py --input test_data.csv --stage Staging --output staging_results.csv

# Check metrics
python src/deploy_model.py --stage info
```

### 4. Deploy to Production

```bash
python src/deploy_model.py --stage production
```

**Production Deployment Checklist:**
- ✓ Model meets 80% accuracy threshold
- ✓ Staging validation completed
- ✓ Performance benchmarks met
- ✓ Stakeholder approval obtained

## Rollback Procedures

### Quick Rollback

If issues are detected in production:

```bash
# Rollback to previous version
python src/deploy_model.py --stage rollback
```

### Rollback to Specific Version

```bash
python src/deploy_model.py --stage rollback --version 5
```

## Monitoring

### Check Current Production Model

```bash
python src/deploy_model.py --stage info
```

### View Deployment History

Access MLflow UI:
```
https://diba-5e288a33-e706.cloud.databricks.com/#mlflow/models/gnu-mlops-model
```

## Automated Deployment (CI/CD)

### GitHub Actions

The repository includes automated deployment via GitHub Actions:

**Automatic Staging Deployment:**
- Triggers on push to `main` branch
- Runs training automatically
- Deploys to staging if successful

**Manual Production Deployment:**
```bash
# Commit with special flag
git commit -m "Deploy new model [deploy-prod]"
git push origin main
```

Or use GitHub Actions UI:
1. Go to Actions tab
2. Select "MLOps Training and Deployment Pipeline"
3. Click "Run workflow"
4. Set "deploy_to_production" to true

## Best Practices

### Pre-Deployment

1. **Model Validation**
   - Verify accuracy meets thresholds
   - Test with representative data
   - Check feature dependencies

2. **Documentation**
   - Document model changes
   - Update version notes
   - Log deployment decisions

3. **Communication**
   - Notify stakeholders
   - Schedule deployment window
   - Prepare rollback plan

### During Deployment

1. **Monitor Closely**
   - Watch for errors
   - Track latency metrics
   - Verify predictions

2. **Gradual Rollout** (Advanced)
   - Start with small traffic percentage
   - Gradually increase exposure
   - Monitor A/B test results

### Post-Deployment

1. **Validation**
   - Run smoke tests
   - Verify endpoint health
   - Check prediction quality

2. **Monitoring**
   - Set up alerts
   - Track performance metrics
   - Monitor data drift

3. **Documentation**
   - Update deployment logs
   - Document issues encountered
   - Record lessons learned

## Troubleshooting

### Common Deployment Issues

**Issue: Model fails validation threshold**
```
Solution: 
- Retrain with better hyperparameters
- Add more training data
- Review feature engineering
```

**Issue: Deployment hangs**
```
Solution:
- Check Databricks cluster status
- Verify network connectivity
- Review logs for errors
```

**Issue: Rollback needed**
```
Solution:
python src/deploy_model.py --stage rollback
```

## Emergency Procedures

### Critical Production Issue

1. **Immediate Rollback**
   ```bash
   python src/deploy_model.py --stage rollback
   ```

2. **Notify Team**
   - Alert stakeholders
   - Document issue
   - Create incident report

3. **Investigation**
   - Review MLflow logs
   - Check Databricks jobs
   - Analyze error patterns

4. **Resolution**
   - Fix underlying issue
   - Retrain if necessary
   - Redeploy with fixes

## Deployment Checklist

- [ ] Model trained and validated
- [ ] MLflow experiment tracked
- [ ] Model registered in registry
- [ ] Staging deployment successful
- [ ] Staging validation completed
- [ ] Performance thresholds met
- [ ] Documentation updated
- [ ] Stakeholders notified
- [ ] Rollback plan prepared
- [ ] Production deployment executed
- [ ] Post-deployment validation done
- [ ] Monitoring alerts configured

## Contact

For deployment support: nbetini@gmail.com

