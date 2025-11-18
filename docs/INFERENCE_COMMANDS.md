# Inference Commands Reference

This document provides all available commands for running inference with your MLOps pipeline.

---

## 📊 Single/Batch Prediction (`predict.py`)

The `predict.py` script allows you to make predictions using deployed models from MLflow.

### Basic Usage

```bash
# Production model inference
python src/predict.py --input data/test_data.csv --output predictions.csv

# Staging model inference
python src/predict.py --input data/test_data.csv --output predictions.csv --stage Staging

# Just load model (interactive mode - no predictions)
python src/predict.py --stage GNU_Production
```

### Command Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--input` | Input data file path (CSV or Parquet format) | No | None (interactive mode) |
| `--output` | Output file path for predictions | No | Auto-generated |
| `--stage` | Model stage to use | No | `GNU_Production` |

### Stage Options

- `Staging`: Use the model in staging environment
- `GNU_Production`: Use the production model (default)

### Examples

```bash
# Basic prediction with production model
python src/predict.py --input test.csv --output predictions.csv

# Test with staging model
python src/predict.py --input test.csv --output test_predictions.csv --stage Staging

# Load model for programmatic use
python src/predict.py --stage GNU_Production
```

### Input File Format

The input file should be a CSV or Parquet file with the same features used during training:
- Feature columns matching training data
- No target column needed (predictions will be generated)

### Output Format

The output file will contain:
- All original columns from input
- New `predictions` column with model predictions

---

## 🔄 Batch Inference (`batch_inference.py`)

The `batch_inference.py` script processes multiple files automatically, typically used for scheduled batch predictions.

### Basic Usage

```bash
# Use configured paths from config.yaml
python src/batch_inference.py

# Process specific file
python src/batch_inference.py --input data/new_data.csv

# Override both input and output
python src/batch_inference.py --input data/input.csv --output results/predictions.csv

# Use different config file
python src/batch_inference.py --config config.local.yaml
```

### Command Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--input` | Override input file or directory path | No | From config |
| `--output` | Override output directory path | No | From config |
| `--config` | Path to configuration file | No | `config.yaml` |

### Configuration

Batch inference uses the `batch_inference` section in `config.yaml`:

```yaml
batch_inference:
  input_path: data/batch_input/
  output_path: data/batch_output/
  archive_path: data/batch_archive/
  model_stage: GNU_Production
  batch_size: 10000
  archive_input: true
  notification_email: null
```

### Examples

```bash
# Process all files in configured input directory
python src/batch_inference.py

# Process single file
python src/batch_inference.py --input data/daily_data_2025-11-17.csv

# Custom output location
python src/batch_inference.py --input data/new_data.csv --output results/november/

# Use local config
python src/batch_inference.py --config config.local.yaml
```

### Features

- **Automatic file discovery**: Finds CSV/Parquet files in input directory
- **Batch processing**: Processes large files in chunks
- **File archiving**: Moves processed files to archive directory
- **Logging**: Detailed logs saved to `logs/batch_inference_*.log`
- **Error handling**: Continues processing even if one file fails

---

## 🔄 Complete Workflow Example

Here's a typical workflow from training to inference:

```bash
# 1. Train a new model
python src/train_model.py

# 2. Deploy to staging for testing
python src/deploy_model.py --stage staging

# 3. Test predictions with staging model
python src/predict.py --input test_data.csv --output test_predictions.csv --stage Staging

# 4. If satisfied, deploy to production
python src/deploy_model.py --stage GNU_Production

# 5. Run production inference
python src/predict.py --input production_data.csv --output production_predictions.csv

# 6. Or run scheduled batch inference
python src/batch_inference.py
```

---

## 📝 Notes

### Model Stages

- **Staging**: Use for testing new models before production
- **GNU_Production**: Live production model serving real predictions

### File Formats

- **Input**: CSV or Parquet files
- **Output**: CSV files with predictions column added

### Environment Variables

The scripts respect these environment variables:
- `MLFLOW_TRACKING_URI`: Override MLflow tracking URI
- `DATABRICKS_HOST`: Databricks host (if using Databricks)
- `DATABRICKS_TOKEN`: Databricks token (if using Databricks)

### Error Handling

- If model not found, scripts will provide clear error messages
- Batch inference continues processing even if individual files fail
- All errors are logged to appropriate log files

---

## 🔍 Troubleshooting

### Model Not Found

If you see "Model not found" error:
1. Make sure you've trained a model: `python src/train_model.py`
2. Check the model stage: `python src/deploy_model.py --stage info`
3. Verify MLflow tracking URI is correct

### Input File Format Issues

- Ensure input file has same features as training data
- Check file format (CSV or Parquet)
- Verify file path is correct

### Permission Errors

- Check file/directory permissions
- Ensure output directory exists or can be created
- Verify MLflow database file permissions

---

**Last Updated**: November 2025  
**Author**: Narsimha Betini

