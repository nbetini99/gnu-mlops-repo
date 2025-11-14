#!/bin/bash
# Complete GitHub Secrets Setup - Automated
# This script creates a GitHub Personal Access Token and sets up all secrets

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

REPO_OWNER="nbetini99"
REPO_NAME="gnu-mlops-repo"
GITHUB_USERNAME="nbetini99"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Complete GitHub Secrets Setup - Automated              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Please create it first: python3 -m venv venv"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing requests..."
    pip install requests --quiet
fi

if ! python3 -c "from nacl import encoding, public" 2>/dev/null; then
    echo "Installing pynacl..."
    pip install pynacl --quiet
fi

echo -e "${GREEN}✓ Dependencies ready${NC}"
echo ""

# Step 1: Create Personal Access Token
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 1: Create GitHub Personal Access Token${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "⚠️  GitHub no longer accepts passwords for API access."
echo "   You need to create a Personal Access Token."
echo ""
echo "📋 Instructions:"
echo ""
echo "1. Open this link:"
echo -e "   ${GREEN}https://github.com/settings/tokens/new${NC}"
echo ""
echo "2. Fill in:"
echo "   - Note: ${GREEN}GNU MLOps Secrets Setup${NC}"
echo "   - Expiration: ${GREEN}90 days${NC} (or your preference)"
echo "   - Select scope: ${GREEN}✅ repo${NC} (Full control)"
echo ""
echo "3. Click: ${GREEN}Generate token${NC}"
echo ""
echo "4. ${YELLOW}Copy the token immediately${NC} (you won't see it again!)"
echo ""

# Open token creation page
echo "Opening token creation page..."
open "https://github.com/settings/tokens/new" 2>/dev/null || echo "Please open: https://github.com/settings/tokens/new"

echo ""
read -p "Press Enter after you've created and copied the token..."

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 2: Enter Your Personal Access Token${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
read -sp "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ Token cannot be empty${NC}"
    exit 1
fi

export GITHUB_TOKEN

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 3: Setting Up Secrets via GitHub API${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Run Python script to set up secrets
python3 setup_secrets_with_auth.py --token "$GITHUB_TOKEN" --username "$GITHUB_USERNAME"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✅ ALL SECRETS SET UP SUCCESSFULLY! ✅            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Go to: https://github.com/${REPO_OWNER}/${REPO_NAME}/actions"
    echo "  2. Trigger a workflow"
    echo "  3. Check logs for: '✓ Databricks credentials found in GitHub Secrets'"
    echo ""
    echo "Verify secrets at:"
    echo "  https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/secrets/actions"
    echo ""
else
    echo ""
    echo -e "${YELLOW}⚠️  Some secrets may have failed to set${NC}"
    echo "   Please check the errors above"
    echo "   You can also set them manually using the link above"
fi

