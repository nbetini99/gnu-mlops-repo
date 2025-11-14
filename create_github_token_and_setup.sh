#!/bin/bash
# Complete GitHub Secrets Setup Script
# This script helps create a GitHub Personal Access Token and sets up secrets

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

REPO_OWNER="nbetini99"
REPO_NAME="gnu-mlops-repo"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Complete GitHub Secrets Setup                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Create Personal Access Token
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 1: Create GitHub Personal Access Token${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "GitHub requires a Personal Access Token (not password) for API access."
echo ""
echo "Please follow these steps:"
echo ""
echo "1. Open this link in your browser:"
echo -e "   ${GREEN}https://github.com/settings/tokens/new${NC}"
echo ""
echo "2. Fill in the form:"
echo "   - Note: ${GREEN}GNU MLOps Secrets Setup${NC}"
echo "   - Expiration: ${GREEN}90 days${NC} (or your preference)"
echo "   - Select scope: ${GREEN}✅ repo${NC} (Full control of private repositories)"
echo ""
echo "3. Click: ${GREEN}Generate token${NC}"
echo ""
echo "4. ${YELLOW}IMPORTANT: Copy the token immediately${NC} (you won't see it again!)"
echo ""

read -p "Have you created the token? (y/n): " token_created

if [[ ! "$token_created" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Opening token creation page..."
    open "https://github.com/settings/tokens/new" 2>/dev/null || echo "Please open: https://github.com/settings/tokens/new"
    echo ""
    echo "After creating the token, run this script again."
    exit 0
fi

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
echo -e "${BLUE}STEP 3: Setting Up Secrets${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Use Python script to set up secrets
if [ -f "setup_secrets_with_auth.py" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python3 setup_secrets_with_auth.py --token "$GITHUB_TOKEN" --username "nbetini99"
else
    echo -e "${RED}❌ setup_secrets_with_auth.py not found${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ Setup Complete! ✅                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

