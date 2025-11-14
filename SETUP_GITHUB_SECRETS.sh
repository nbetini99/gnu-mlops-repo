#!/bin/bash
# GitHub Secrets Setup Helper Script
# This script helps you verify GitHub Secrets setup and provides instructions

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        GitHub Secrets Setup for Databricks Integration      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Repository information
REPO_OWNER="nbetini99"
REPO_NAME="gnu-mlops-repo"
REPO_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}"

echo -e "${GREEN}Repository:${NC} ${REPO_URL}"
echo ""

# Required secrets
REQUIRED_SECRETS=(
    "DATABRICKS_HOST:https://dbc-5e289a33-a706.cloud.databricks.com"
    "DATABRICKS_TOKEN:dapicb7282387c50cc9aa3e8e3d18378b5fd"
)

# Optional secrets
OPTIONAL_SECRETS=(
    "DATABRICKS_WORKSPACE_PATH:/Users/nbatink@gmail.com/gnu-mlops/liveprod"
    "DATABRICKS_EXPERIMENT_PATH:/Users/nbatink@gmail.com/gnu-mlops/experiments"
)

echo -e "${YELLOW}⚠ IMPORTANT: This script provides instructions only.${NC}"
echo -e "${YELLOW}   GitHub Secrets must be set up through the GitHub web interface.${NC}"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 1: Navigate to GitHub Repository Settings${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "1. Open your browser and go to:"
echo -e "   ${GREEN}${REPO_URL}${NC}"
echo ""
echo "2. Click on 'Settings' (top menu bar)"
echo ""
echo "3. In the left sidebar, click on:"
echo "   ${GREEN}Secrets and variables → Actions${NC}"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 2: Add Required Secrets${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

for secret in "${REQUIRED_SECRETS[@]}"; do
    SECRET_NAME="${secret%%:*}"
    SECRET_VALUE="${secret#*:}"
    
    echo -e "${YELLOW}Secret: ${SECRET_NAME}${NC}"
    echo "  1. Click '${GREEN}New repository secret${NC}'"
    echo "  2. Name: ${GREEN}${SECRET_NAME}${NC}"
    echo "  3. Value: ${GREEN}${SECRET_VALUE}${NC}"
    echo "  4. Click '${GREEN}Add secret${NC}'"
    echo ""
done

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 3: Add Optional Secrets (Recommended)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

for secret in "${OPTIONAL_SECRETS[@]}"; do
    SECRET_NAME="${secret%%:*}"
    SECRET_VALUE="${secret#*:}"
    
    echo -e "${YELLOW}Secret: ${SECRET_NAME}${NC}"
    echo "  1. Click '${GREEN}New repository secret${NC}'"
    echo "  2. Name: ${GREEN}${SECRET_NAME}${NC}"
    echo "  3. Value: ${GREEN}${SECRET_VALUE}${NC}"
    echo "  4. Click '${GREEN}Add secret${NC}'"
    echo ""
done

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 4: Verify Secrets Are Set${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "After adding all secrets, you should see:"
echo ""
for secret in "${REQUIRED_SECRETS[@]}" "${OPTIONAL_SECRETS[@]}"; do
    SECRET_NAME="${secret%%:*}"
    echo -e "  ${GREEN}✓${NC} ${SECRET_NAME}"
done
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 5: Test GitHub Actions Workflow${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "1. Go to the 'Actions' tab in your repository"
echo "2. Trigger a workflow by:"
echo "   - Pushing a commit, OR"
echo "   - Clicking 'Run workflow' manually"
echo ""
echo "3. Check the workflow logs for:"
echo -e "   ${GREEN}✓ Databricks credentials found in GitHub Secrets${NC}"
echo -e "   ${GREEN}✓ Environment configured for Databricks${NC}"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Quick Reference: Secret Values${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Copy and paste these values when setting up secrets:"
echo ""
for secret in "${REQUIRED_SECRETS[@]}" "${OPTIONAL_SECRETS[@]}"; do
    SECRET_NAME="${secret%%:*}"
    SECRET_VALUE="${secret#*:}"
    echo -e "${YELLOW}${SECRET_NAME}:${NC}"
    echo "  ${SECRET_VALUE}"
    echo ""
done

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Direct Link to Secrets Page${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/secrets/actions${NC}"
echo ""
echo "Click the link above to go directly to the secrets page."
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Verification${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "After setting up secrets, you can verify by:"
echo "1. Checking the secrets page (should show all secrets listed)"
echo "2. Running a GitHub Actions workflow"
echo "3. Checking workflow logs for successful credential loading"
echo ""

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ Setup Instructions Complete! ✅              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

