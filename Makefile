.PHONY: help install setup train deploy-staging deploy-production predict clean test lint

help:
	@echo "GNU MLOps - Available Commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make setup            - Setup Databricks workspace"
	@echo "  make train            - Train ML model"
	@echo "  make deploy-staging   - Deploy to staging"
	@echo "  make deploy-production- Deploy to production"
	@echo "  make predict          - Run predictions"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run linters"
	@echo "  make clean            - Clean generated files"

install:
	pip install -r requirements.txt

setup:
	chmod +x scripts/setup_databricks.sh
	./scripts/setup_databricks.sh

train:
	python src/train_model.py

deploy-staging:
	python src/deploy_model.py --stage staging

deploy-production:
	python src/deploy_model.py --stage production

predict:
	python src/predict.py --stage Production

info:
	python src/deploy_model.py --stage info

rollback:
	python src/deploy_model.py --stage rollback

test:
	pytest tests/ -v

lint:
	flake8 src/
	black --check src/

format:
	black src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ mlruns/ mlartifacts/

