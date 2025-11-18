# Inference Data Files

This document describes the inference data files generated for testing and running predictions.

---

## 📁 File Structure

All inference data files are stored in the `data/` directory, organized into subdirectories:

```
data/
├── daily_batch/          # Daily batch inference files
├── test/                 # Test files for various scenarios
├── production_samples/   # Production-like sample files
└── batch_input/          # Batch inference input files
```

---

## 📊 File Categories

### 1. Daily Batch Files (`data/daily_batch/`)

**Purpose**: Simulate daily batch inference runs

**Files**: 7 files (one per day for the past week)
- `daily_batch_YYYYMMDD.csv` format
- Each file: **1,000 records**
- Normal distribution
- Different seed per day for variation

**Usage**:
```bash
# Process all daily batch files
python src/batch_inference.py --input data/daily_batch/

# Process specific day
python src/predict.py --input data/daily_batch/daily_batch_20251117.csv --output daily_predictions.csv
```

---

### 2. Test Files (`data/test/`)

**Purpose**: Various test scenarios for validation

**Files**: 7 files with different characteristics

| File | Records | Description |
|------|---------|-------------|
| `test_small.csv` | 100 | Small test file for quick validation |
| `test_medium.csv` | 1,000 | Medium-sized test file |
| `test_large.csv` | 10,000 | Large test file for performance testing |
| `test_uniform.csv` | 1,000 | Uniform distribution test |
| `test_mixed.csv` | 1,000 | Mixed distribution test |
| `test_single.csv` | 1 | Single record test |
| `test_edge_cases.csv` | 55 | Edge cases with extreme values |

**Usage**:
```bash
# Quick test
python src/predict.py --input data/test/test_small.csv --output test_predictions.csv

# Performance test
python src/predict.py --input data/test/test_large.csv --output large_predictions.csv

# Edge case testing
python src/predict.py --input data/test/test_edge_cases.csv --output edge_predictions.csv
```

---

### 3. Production Samples (`data/production_samples/`)

**Purpose**: Production-like data for realistic testing

**Files**: 3 files
- `production_sample_1.csv` (5,000 records)
- `production_sample_2.csv` (5,000 records)
- `production_sample_3.csv` (5,000 records)

**Characteristics**:
- Mixed distribution (more realistic)
- Larger file sizes (5,000 records each)
- Suitable for production testing

**Usage**:
```bash
# Production inference
python src/predict.py --input data/production_samples/production_sample_1.csv --output prod_predictions.csv
```

---

### 4. Batch Input Files (`data/batch_input/`)

**Purpose**: Files ready for batch inference processing

**Files**: 5 files
- `batch_input_YYYYMMDD_HHMMSS.csv` format
- Each file: **2,000 records**
- Timestamped for chronological processing

**Usage**:
```bash
# Process all batch input files
python src/batch_inference.py --input data/batch_input/

# Process specific file
python src/predict.py --input data/batch_input/batch_input_20251117_134116.csv --output batch_predictions.csv
```

---

## 📋 Data Format

All inference data files follow the same format:

### Columns

- `feature1`: First feature (numeric)
- `feature2`: Second feature (numeric)
- `feature3`: Third feature (numeric)

**Note**: No target column (predictions will be generated)

### Example

```csv
feature1,feature2,feature3
-1.7497654730546974,-1.7046512057609624,0.6044235385892025
0.34268040332750216,-1.1362610068273629,-0.9070304174806991
1.153035802563644,-2.9733154740508856,0.5920232693603779
```

---

## 🔄 Regenerating Files

To regenerate inference data files:

```bash
# Generate all files
python scripts/generate_inference_data.py

# Generate specific categories only
python scripts/generate_inference_data.py --skip-daily  # Skip daily batch
python scripts/generate_inference_data.py --skip-test    # Skip test files
python scripts/generate_inference_data.py --skip-production  # Skip production samples
python scripts/generate_inference_data.py --skip-batch    # Skip batch input

# Custom output directory
python scripts/generate_inference_data.py --output-dir custom_data/
```

---

## 🚀 Quick Start Examples

### Example 1: Quick Test
```bash
python src/predict.py --input data/test/test_small.csv --output predictions.csv
```

### Example 2: Production Inference
```bash
python src/predict.py --input data/production_samples/production_sample_1.csv --output prod_predictions.csv
```

### Example 3: Batch Processing
```bash
python src/batch_inference.py --input data/batch_input/
```

### Example 4: Daily Batch Processing
```bash
python src/batch_inference.py --input data/daily_batch/
```

### Example 5: Test with Staging Model
```bash
python src/predict.py --input data/test/test_medium.csv --output staging_predictions.csv --stage Staging
```

---

## 📊 File Statistics

| Category | Files | Total Records | Avg Records/File |
|----------|-------|---------------|------------------|
| Daily Batch | 7 | 7,000 | 1,000 |
| Test | 7 | 14,256 | ~2,037 |
| Production Samples | 3 | 15,000 | 5,000 |
| Batch Input | 5 | 10,000 | 2,000 |
| **Total** | **22** | **46,256** | **~2,103** |

---

## 🔍 Validation

All generated files:
- ✅ Match training data format (feature1, feature2, feature3)
- ✅ Have no missing values (except edge cases file which tests NaN handling)
- ✅ Use reproducible seeds for consistency
- ✅ Are in CSV format for easy processing
- ✅ Are ready for immediate use with inference scripts

---

## 📝 Notes

1. **File Sizes**: Files range from 1 record (test_single.csv) to 10,000 records (test_large.csv)

2. **Distributions**: 
   - Normal: Most common, matches training data
   - Uniform: Tests model on different distribution
   - Mixed: More realistic production-like data

3. **Edge Cases**: The `test_edge_cases.csv` includes extreme values and NaN to test model robustness

4. **Reproducibility**: All files use fixed seeds, so regenerating will produce identical data

---

**Last Updated**: November 2025  
**Author**: Narsimha Betini  
**Total Files**: 22  
**Total Records**: 46,256

