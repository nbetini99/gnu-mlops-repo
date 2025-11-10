#!/bin/bash
# Quick Setup Validation Script
# Tests that everything is configured correctly

set -e

echo "========================================="
echo "GNU MLOps - Setup Validation"
echo "========================================="
echo ""

ERRORS=0

# Test 1: Check Python
echo "Test 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION found"
else
    echo "✗ Python 3 not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Test 2: Check required files
echo "Test 2: Checking project files..."
FILES=("config.yaml" "requirements.txt" "src/train_model.py" "src/deploy_model.py" "src/predict.py")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file missing"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Test 3: Check configuration
echo "Test 3: Validating configuration file..."
python3 << EOF
try:
    import yaml
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print("✓ config.yaml is valid YAML")
    print(f"  Model: {config['model']['algorithm']}")
    print(f"  Experiment: {config['mlflow']['experiment_name']}")
except Exception as e:
    print(f"✗ Configuration error: {e}")
    exit(1)
EOF
echo ""

# Test 4: Check Python dependencies
echo "Test 4: Checking Python dependencies..."
python3 << EOF
required_packages = [
    'numpy',
    'pandas', 
    'sklearn',
    'mlflow',
    'yaml'
]

missing = []
for package in required_packages:
    try:
        __import__(package)
        print(f"✓ {package}")
    except ImportError:
        print(f"✗ {package} not installed")
        missing.append(package)

if missing:
    print(f"\nTo install missing packages: pip install {' '.join(missing)}")
    exit(1)
EOF
echo ""

# Test 5: Check environment variables
echo "Test 5: Checking environment configuration..."
if [ -f ".env" ]; then
    echo "✓ .env file exists"
    if grep -q "DATABRICKS_HOST" .env 2>/dev/null; then
        echo "✓ DATABRICKS_HOST configured"
    else
        echo "⚠ DATABRICKS_HOST not set in .env"
    fi
    if grep -q "DATABRICKS_TOKEN" .env 2>/dev/null; then
        echo "✓ DATABRICKS_TOKEN configured"
    else
        echo "⚠ DATABRICKS_TOKEN not set in .env"
    fi
else
    echo "⚠ .env file not found (optional for local testing)"
fi
echo ""

# Test 6: Test import modules
echo "Test 6: Testing module imports..."
python3 << EOF
try:
    from src.train_model import MLModelTrainer
    print("✓ Can import MLModelTrainer")
    
    from src.deploy_model import ModelDeployment
    print("✓ Can import ModelDeployment")
    
    from src.predict import ModelPredictor
    print("✓ Can import ModelPredictor")
except Exception as e:
    print(f"✗ Import error: {e}")
    exit(1)
EOF
echo ""

# Test 7: Test sample data generation
echo "Test 7: Testing data generation..."
python3 << EOF
try:
    from src.train_model import MLModelTrainer
    trainer = MLModelTrainer()
    df = trainer._generate_sample_data(n_samples=10)
    print(f"✓ Generated sample data: {df.shape[0]} rows, {df.shape[1]} columns")
except Exception as e:
    print(f"✗ Data generation failed: {e}")
    exit(1)
EOF
echo ""

# Summary
echo "========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ All validation tests passed!"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Set your Databricks credentials in .env"
    echo "  2. Run: python3 src/train_model.py"
    echo "  3. Or use: make train"
    echo ""
else
    echo "✗ $ERRORS test(s) failed"
    echo "========================================="
    echo "Please fix the issues above before continuing"
    exit 1
fi

