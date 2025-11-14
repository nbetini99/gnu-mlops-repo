#!/bin/bash
# Quick Start: Automated GitHub Secrets Setup
# Run this script to complete the entire setup process

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Quick Start: GitHub Secrets Setup                       ║${NC}"
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
echo -e "${BLUE}Preparing environment...${NC}"
if ! python3 -c "import requests; from nacl import encoding, public" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install requests pynacl --quiet
fi
echo -e "${GREEN}✓ Environment ready${NC}"
echo ""

# Step 1: Guide user to create token
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 1: Create GitHub Personal Access Token${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "📋 Quick Instructions:"
echo ""
echo "1. Token creation page will open in your browser"
echo "2. Fill in:"
echo "   • Note: ${GREEN}GNU MLOps Secrets Setup${NC}"
echo "   • Expiration: ${GREEN}90 days${NC}"
echo "   • Scope: ${GREEN}✅ repo${NC} (Full control)"
echo "3. Click: ${GREEN}Generate token${NC}"
echo "4. ${YELLOW}Copy the token${NC} (you won't see it again!)"
echo ""

# Open token creation page
echo "Opening token creation page..."
open "https://github.com/settings/tokens/new" 2>/dev/null || echo "Please open: https://github.com/settings/tokens/new"

echo ""
read -p "Press Enter after you've created and copied the token..."

# Step 2: Get token
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 2: Enter Your Token${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
read -sp "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ Token cannot be empty${NC}"
    exit 1
fi

export GITHUB_TOKEN

# Step 3: Set up secrets
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 3: Setting Up Secrets${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

python3 setup_secrets_with_auth.py --token "$GITHUB_TOKEN" --username "nbetini99"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ SETUP COMPLETE! ✅                          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "✅ All secrets have been set up successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Verify secrets: https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions"
    echo "  2. Test workflow: https://github.com/nbetini99/gnu-mlops-repo/actions"
    echo "  3. Check logs for: '✓ Databricks credentials found in GitHub Secrets'"
    echo ""
    echo -e "${GREEN}🎉 Your GitHub Actions workflow is now ready to use Databricks!${NC}"
else
    echo -e "${YELLOW}⚠️  Setup encountered issues${NC}"
    echo "   Please check the errors above"
    echo "   You can set secrets manually at:"
    echo "   https://github.com/nbetini99/gnu-mlops-repo/settings/secrets/actions"
fi

echo ""

